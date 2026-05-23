import copy
import math
import os
import time
import numpy as np
import torch
import torch.nn as nn

from physics import initial_car, step_car as real_step_car
from observations import generate_observation
from policy import Policy as RealPolicy
from attack import AttackModel as RealAttack

CAR_LENGTH = 2.5
MAX_SPEED = 30.0
ACCEL_FORCE = 10.0
BRAKE_FORCE = 14.0
DRAG = 0.3
MAX_STEER_ANGLE = 28.0
STEER_SPEED = 70.0

OBS_DIM = 8
ATTACK_HIDDEN = 16
BOUND = 0.5
MAX_WEIGHT = 10.0
GOAL_RADIUS = 2.0

LEGIT_GOAL = torch.tensor([-20.0, -20.0])
CTF_GOAL = torch.tensor([18.5, -24.5])

INIT_X = 7.0
INIT_Z = 23.7
INIT_HEADING = -3 * math.pi / 4

T_TRAIN = 1800
DT = 1.0 / 60.0

HERE = os.path.dirname(os.path.abspath(__file__))
_data = np.load(os.path.join(HERE, "weights.npz"))
_W = [torch.from_numpy(_data[f"W{i}"]).float() for i in range(3)]
_B = [torch.from_numpy(_data[f"b{i}"]).float() for i in range(3)]
for w in _W + _B:
    w.requires_grad_(False)


def policy(obs):
    x = obs
    for i in range(len(_W) - 1):
        x = torch.tanh(x @ _W[i].T + _B[i])
    return torch.tanh(x @ _W[-1].T + _B[-1])


def make_obs(x, z, heading, speed, steer_angle, goal):
    dx = goal[0] - x
    dz = goal[1] - z
    ch = torch.cos(heading)
    sh = torch.sin(heading)
    return torch.stack([
        speed / 10.0,
        steer_angle / 28.0,
        ch,
        sh,
        (dx * ch + dz * sh) / 30.0,
        (-dx * sh + dz * ch) / 30.0,
        torch.log(torch.sqrt(dx * dx + dz * dz + 1e-8) + 1.0) / 5.0,
        torch.ones_like(speed),
    ])


def step_car(x, z, heading, speed, steer_angle, throttle, brake, steer, dt):
    steer_target = steer * MAX_STEER_ANGLE
    change = torch.clamp(steer_target - steer_angle, -STEER_SPEED * dt, STEER_SPEED * dt)
    steer_angle = steer_angle + change

    sign_speed = torch.tanh(100.0 * speed)
    accel = throttle * ACCEL_FORCE - brake * BRAKE_FORCE * sign_speed - DRAG * speed
    speed = torch.clamp(speed + accel * dt, -MAX_SPEED * 0.3, MAX_SPEED)

    speed_factor = 1.0 / (1.0 + 0.006 * speed * speed)
    steer_rad = torch.clamp(steer_angle * speed_factor * (math.pi / 180.0), -0.6, 0.6)
    angular_vel = speed * torch.tan(steer_rad) / CAR_LENGTH
    heading = heading + angular_vel * dt
    x = x + torch.cos(heading) * speed * dt
    z = z + torch.sin(heading) * speed * dt
    return x, z, heading, speed, steer_angle


class AttackNet(nn.Module):
    def __init__(self, bound):
        super().__init__()
        self.fc0 = nn.Linear(OBS_DIM, ATTACK_HIDDEN)
        self.fc1 = nn.Linear(ATTACK_HIDDEN, OBS_DIM)
        self.bound = bound

    def forward(self, obs):
        h = torch.tanh(self.fc0(obs))
        y = torch.tanh(self.fc1(h))
        norm = torch.norm(y, p=2) + 1e-8
        scale = torch.clamp(self.bound / norm, max=1.0)
        return y * scale


def rollout(attack, T=T_TRAIN, dt=DT):
    x = torch.tensor(INIT_X)
    z = torch.tensor(INIT_Z)
    heading = torch.tensor(INIT_HEADING)
    speed = torch.tensor(0.0)
    steer_angle = torch.tensor(0.0)
    positions = []
    for _ in range(T):
        obs = make_obs(x, z, heading, speed, steer_angle, LEGIT_GOAL)
        action = policy(obs + attack(obs))
        tmb, steer = action[0], action[1]
        throttle = torch.clamp(tmb, min=0.0)
        brake = torch.clamp(-tmb, min=0.0)
        x, z, heading, speed, steer_angle = step_car(
            x, z, heading, speed, steer_angle, throttle, brake, steer, dt
        )
        positions.append(torch.stack([x, z]))
    return torch.stack(positions)


def loss_fn(pos):
    d = torch.norm(pos - CTF_GOAL, dim=1)
    tau = 2.0
    softmin = -tau * torch.logsumexp(-d / tau, dim=0)
    topk = -torch.topk(-d, k=50).values
    return softmin + 0.2 * topk.mean(), d


def rollout_real(attack_state, T=T_TRAIN, dt=DT):
    arrays = {
        "W0": attack_state["fc0.weight"].detach().numpy(),
        "b0": attack_state["fc0.bias"].detach().numpy(),
        "W1": attack_state["fc1.weight"].detach().numpy(),
        "b1": attack_state["fc1.bias"].detach().numpy(),
    }
    real_attack = RealAttack(arrays)
    real_policy = RealPolicy(os.path.join(HERE, "weights.npz"))

    car = initial_car()
    car.x, car.z, car.heading = INIT_X, INIT_Z, INIT_HEADING
    car.speed = 0.0
    car.steer_angle = 0.0

    best_d = float("inf")
    for _ in range(T):
        obs = generate_observation(car, (-20.0, -20.0))
        delta = real_attack(obs)
        perturbed = obs + delta
        tmb, steer = real_policy(perturbed)
        throttle = max(0.0, min(1.0, tmb))
        brake = max(0.0, min(1.0, -tmb))
        real_step_car(car, dt, throttle, brake, steer)
        d = math.hypot(car.x - CTF_GOAL[0].item(), car.z - CTF_GOAL[1].item())
        if d < best_d:
            best_d = d
    return best_d


def bptt(seed, steps=400, lr=5e-3, verify_below=3.0):
    torch.manual_seed(seed)
    attack = AttackNet(bound=BOUND)
    for p in attack.parameters():
        nn.init.normal_(p, std=0.2)

    opt = torch.optim.Adam(attack.parameters(), lr=lr)
    best_diff = float("inf")
    best_diff_state = None
    best_real = float("inf")
    best_real_state = None

    for step in range(steps):
        opt.zero_grad()
        try:
            pos = rollout(attack)
            l, d = loss_fn(pos)
            if not torch.isfinite(l):
                continue
            l.backward()
            bad = any((p.grad is None or not torch.isfinite(p.grad).all())
                      for p in attack.parameters())
            if bad:
                opt.zero_grad(); continue
            torch.nn.utils.clip_grad_norm_(attack.parameters(), 1.0)
            opt.step()
            with torch.no_grad():
                for p in attack.parameters():
                    p.clamp_(-MAX_WEIGHT, MAX_WEIGHT)
            md = d.min().item()
        except RuntimeError:
            opt.zero_grad(); continue

        new_best = md < best_diff
        if new_best:
            best_diff = md
            best_diff_state = copy.deepcopy(attack.state_dict())

        verified = ""
        if new_best and md < verify_below:
            real_md = rollout_real(best_diff_state)
            if real_md < best_real:
                best_real = real_md
                best_real_state = copy.deepcopy(best_diff_state)
            verified = f"  real={real_md:.3f} (best_real={best_real:.3f})"

        if step % 20 == 0 or verified:
            print(f"  seed={seed} step={step:4d} md={md:6.2f} best_diff={best_diff:6.2f}{verified}")

        if best_real < GOAL_RADIUS:
            break

    return best_diff, best_real, best_real_state


def main():
    t0 = time.perf_counter()
    best_real = float("inf")
    best_state = None

    for seed in range(12):
        print(f"[seed {seed}]")
        diff_md, real_md, real_state = bptt(seed=seed, steps=400, lr=5e-3, verify_below=3.0)
        print(f"  -> diff_md={diff_md:.3f}  real_md={real_md:.3f}")
        if real_state is not None and real_md < best_real:
            best_real, best_state = real_md, real_state
        if best_real < GOAL_RADIUS:
            break

    if best_state is None:
        print("no verified solve")
        return

    attack = AttackNet(bound=BOUND)
    attack.load_state_dict(best_state)

    out = os.path.join(HERE, "solve_attack.npz")
    np.savez(out,
        W0=attack.fc0.weight.detach().numpy(),
        b0=attack.fc0.bias.detach().numpy(),
        W1=attack.fc1.weight.detach().numpy(),
        b1=attack.fc1.bias.detach().numpy(),
    )
    print(f"\nsaved {out}  real_min_d={best_real:.3f}  ({time.perf_counter()-t0:.1f}s)")


if __name__ == "__main__":
    main()

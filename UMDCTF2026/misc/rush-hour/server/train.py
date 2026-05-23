import math
import os
import time
import numpy as np
import torch
import torch.nn as nn

from physics import initial_car, step_car
from observations import generate_observation, OBS_DIM
from expert import expert_action

LEGIT_GOAL = (-20.0, -20.0)

EPISODES = 500
STEPS_PER_EP = 120
DT = 1.0 / 30.0

EPOCHS = 400
BATCH_SIZE = 512
LR = 1e-3
LOSS_TARGET = 3e-3
HIDDEN = 32

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(OBS_DIM, HIDDEN), nn.Tanh(),
            nn.Linear(HIDDEN, HIDDEN), nn.Tanh(),
            nn.Linear(HIDDEN, 2), nn.Tanh(),
        )

    def forward(self, x):
        return self.net(x)


def rollout_dataset(rng: np.random.Generator):
    N = EPISODES * STEPS_PER_EP
    X = np.empty((N, OBS_DIM), dtype=np.float32)
    Y = np.empty((N, 2), dtype=np.float32)
    k = 0
    for _ in range(EPISODES):
        car = initial_car()
        car.x = float(rng.uniform(-30, 30))
        car.z = float(rng.uniform(-30, 30))
        car.heading = float(rng.uniform(-math.pi, math.pi))
        car.speed = float(rng.uniform(0, 10))

        for _ in range(STEPS_PER_EP):
            obs = generate_observation(car, LEGIT_GOAL)
            act = expert_action(obs)
            X[k] = obs
            Y[k] = act
            k += 1

            tmb = float(act[0])
            step_car(car, DT, max(0.0, tmb), max(0.0, -tmb), float(act[1]))
    return X, Y


def main():
    torch.set_num_threads(max(1, os.cpu_count() // 2 or 1))

    rng = np.random.default_rng(42)
    torch.manual_seed(0)

    print(f"Device: {DEVICE}")
    t0 = time.perf_counter()
    X, Y = rollout_dataset(rng)
    print(f"Dataset: {X.shape[0]} samples  ({time.perf_counter()-t0:.1f}s)")

    X_t = torch.from_numpy(X).to(DEVICE)
    Y_t = torch.from_numpy(Y).to(DEVICE)

    model = Net().to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.MSELoss()

    N = X_t.shape[0]
    for epoch in range(EPOCHS):
        t0 = time.perf_counter()
        perm = torch.randperm(N, device=DEVICE)
        total = 0.0
        for i in range(0, N, BATCH_SIZE):
            idx = perm[i : i + BATCH_SIZE]
            pred = model(X_t[idx])
            loss = loss_fn(pred, Y_t[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * idx.shape[0]
        avg = total / N
        print(f"epoch {epoch+1:3d}  loss={avg:.5f}  ({time.perf_counter()-t0:.2f}s)")
        if avg < LOSS_TARGET:
            break

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "weights.npz")
    state: dict = {}
    layers = [m for m in model.net if isinstance(m, nn.Linear)]
    for i, lin in enumerate(layers):
        state[f"W{i}"] = lin.weight.detach().cpu().numpy()
        state[f"b{i}"] = lin.bias.detach().cpu().numpy()
    np.savez(out, **state)
    print(f"Saved {out}  params={sum(v.size for v in state.values())}")


if __name__ == "__main__":
    main()

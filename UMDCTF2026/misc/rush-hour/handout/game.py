import numpy as np
from physics import CarState, initial_car, step_car
from observations import OBS_DIM, generate_observation
from policy import Policy
from attack import AttackModel

LEGIT_GOAL = (-20.0, -20.0)
CTF_GOAL = (18.5, -24.5)
CTF_RADIUS = 2.0
EPISODE_TIMEOUT = 60.0

FLAG = "UMDCTF{fake_flag}"


class GameState:
    def __init__(self, policy: Policy):
        self.policy = policy
        self.attack: AttackModel | None = None
        self.attack_error: str | None = None
        self.car: CarState = initial_car()
        self.time = 0.0
        self.last_obs = np.zeros(OBS_DIM, dtype=np.float32)
        self.last_delta = np.zeros(8, dtype=np.float32)
        self.goal_reached = False
        self.timed_out = False
        self.flag: str | None = None

    def reset(self) -> None:
        self.car = initial_car()
        self.time = 0.0
        self.goal_reached = False
        self.timed_out = False
        self.flag = None
        self.last_delta = np.zeros(8, dtype=np.float32)

    def install_attack(self, model: AttackModel | None) -> None:
        self.attack = model
        self.attack_error = None
        self.reset()

    def set_attack_error(self, err: str) -> None:
        self.attack = None
        self.attack_error = err

    def step(self, dt: float) -> None:
        if self.goal_reached or self.timed_out:
            return

        obs = generate_observation(self.car, LEGIT_GOAL)
        self.last_obs = obs

        if self.attack is not None:
            delta = self.attack(obs)
            self.last_delta = delta
            policy_input = obs + delta
        else:
            self.last_delta = np.zeros(8, dtype=np.float32)
            policy_input = obs

        raw_t, steer = self.policy(policy_input)
        action = np.clip(np.array([raw_t, steer], dtype=np.float32), -1.0, 1.0)

        throttle = float(max(0.0, action[0]))
        brake = float(max(0.0, -action[0]))
        step_car(self.car, dt, throttle, brake, float(action[1]))
        self.time += dt

        dx = self.car.x - CTF_GOAL[0]
        dz = self.car.z - CTF_GOAL[1]
        if dx * dx + dz * dz < CTF_RADIUS * CTF_RADIUS:
            self.goal_reached = True
            self.flag = FLAG
        elif self.time > EPISODE_TIMEOUT:
            self.timed_out = True

    def to_state_dict(self) -> dict:
        if self.attack is not None:
            attack_status = "active"
        elif self.attack_error is not None:
            attack_status = "error"
        else:
            attack_status = "none"

        return {
            "type": "state",
            "t": self.time,
            "x": self.car.x,
            "z": self.car.z,
            "heading": self.car.heading,
            "speed": self.car.speed,
            "obs": self.last_obs.tolist(),
            "obsDelta": self.last_delta.tolist(),
            "attack": attack_status,
            "attackError": self.attack_error,
            "goalReached": self.goal_reached,
            "timedOut": self.timed_out,
            "flag": self.flag,
        }

import math
import numpy as np
from physics import CarState

OBS_DIM = 8


def generate_observation(car: CarState, goal: tuple[float, float]) -> np.ndarray:
    dx = goal[0] - car.x
    dz = goal[1] - car.z
    ch = math.cos(car.heading)
    sh = math.sin(car.heading)

    goal_fwd = dx * ch + dz * sh
    goal_right = -dx * sh + dz * ch
    goal_dist = math.hypot(dx, dz)

    return np.array([
        car.speed / 10.0,
        car.steer_angle / 28.0,
        ch,
        sh,
        goal_fwd / 30.0,
        goal_right / 30.0,
        math.log(goal_dist + 1.0) / 5.0,
        1.0,
    ], dtype=np.float32)

import math
import numpy as np


def expert_action(obs: np.ndarray) -> np.ndarray:
    goal_fwd = obs[4] * 30.0
    goal_right = obs[5] * 30.0
    goal_dist = math.exp(obs[6] * 5.0) - 1.0
    speed = obs[0] * 10.0

    angle_to_goal = math.atan2(goal_right, goal_fwd)
    steer = max(-1.0, min(1.0, angle_to_goal * 1.5))

    aligned = math.cos(angle_to_goal)
    if aligned > 0.5:
        target_speed = min(15.0, 3.0 + goal_dist)
    elif aligned > 0:
        target_speed = 6.0
    else:
        target_speed = 3.0

    if goal_dist < 5.0:
        target_speed = min(target_speed, goal_dist)

    speed_err = target_speed - speed
    throttle_minus_brake = max(-1.0, min(1.0, speed_err * 0.5))

    return np.array([throttle_minus_brake, steer], dtype=np.float32)

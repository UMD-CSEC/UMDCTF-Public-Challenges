from dataclasses import dataclass
import math

CAR_LENGTH = 2.5
MAX_SPEED = 30.0
ACCEL_FORCE = 10.0
BRAKE_FORCE = 14.0
HANDBRAKE_FORCE = 25.0
DRAG = 0.3
MAX_STEER_ANGLE = 28.0
STEER_SPEED = 70.0
STEER_RETURN = 120.0


@dataclass
class CarState:
    x: float = 7.0
    z: float = 23.7
    heading: float = -3 * math.pi / 4
    speed: float = 0.0
    steer_angle: float = 0.0


def initial_car() -> CarState:
    return CarState()


def step_car(car: CarState, dt: float, throttle: float, brake: float, steer: float, handbrake: bool = False) -> None:
    throttle = max(0.0, min(1.0, throttle))
    brake = max(0.0, min(1.0, brake))
    steer = max(-1.0, min(1.0, steer))

    steer_target = steer * MAX_STEER_ANGLE
    if abs(steer_target) > 0.1:
        diff = steer_target - car.steer_angle
        step = STEER_SPEED * dt
        if abs(diff) < step:
            car.steer_angle = steer_target
        else:
            car.steer_angle += math.copysign(step, diff)
    else:
        step = STEER_RETURN * dt
        if abs(car.steer_angle) < step:
            car.steer_angle = 0.0
        else:
            car.steer_angle -= math.copysign(step, car.steer_angle)

    accel = 0.0
    if handbrake:
        accel = -math.copysign(HANDBRAKE_FORCE, car.speed) if car.speed != 0 else 0.0
    else:
        accel += throttle * ACCEL_FORCE
        accel -= brake * BRAKE_FORCE * (math.copysign(1.0, car.speed) if car.speed != 0 else 1.0)
    accel -= DRAG * car.speed

    car.speed += accel * dt
    car.speed = max(-MAX_SPEED * 0.3, min(MAX_SPEED, car.speed))
    if abs(car.speed) < 0.05 and throttle == 0:
        car.speed = 0.0

    speed_factor = 1.0 / (1.0 + 0.006 * car.speed * car.speed)
    steer_rad = car.steer_angle * speed_factor * (math.pi / 180.0)
    if abs(steer_rad) > 0.001 and abs(car.speed) > 0.01:
        angular_vel = car.speed * math.tan(steer_rad) / CAR_LENGTH
        car.heading += angular_vel * dt

    car.x += math.cos(car.heading) * car.speed * dt
    car.z += math.sin(car.heading) * car.speed * dt

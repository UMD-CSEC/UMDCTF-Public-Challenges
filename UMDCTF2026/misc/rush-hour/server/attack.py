import base64
import io
import numpy as np

ATTACK_HIDDEN = 16
ATTACK_OUTPUT = 8
MAX_WEIGHT = 10.0
MAX_DELTA_L2 = 0.5
MAX_FILE_SIZE = 100_000


class InvalidAttack(Exception):
    pass


class AttackModel:
    def __init__(self, arrays):
        try:
            W0 = np.asarray(arrays["W0"], dtype=np.float32)
            b0 = np.asarray(arrays["b0"], dtype=np.float32)
            W1 = np.asarray(arrays["W1"], dtype=np.float32)
            b1 = np.asarray(arrays["b1"], dtype=np.float32)
        except KeyError as e:
            raise InvalidAttack(f"missing key: {e}")

        if W0.shape != (ATTACK_HIDDEN, 8):
            raise InvalidAttack(f"W0 shape {W0.shape} != ({ATTACK_HIDDEN}, 8)")
        if b0.shape != (ATTACK_HIDDEN,):
            raise InvalidAttack(f"b0 shape {b0.shape} != ({ATTACK_HIDDEN},)")
        if W1.shape != (ATTACK_OUTPUT, ATTACK_HIDDEN):
            raise InvalidAttack(f"W1 shape {W1.shape} != ({ATTACK_OUTPUT}, {ATTACK_HIDDEN})")
        if b1.shape != (ATTACK_OUTPUT,):
            raise InvalidAttack(f"b1 shape {b1.shape} != ({ATTACK_OUTPUT},)")

        for name, arr in [("W0", W0), ("b0", b0), ("W1", W1), ("b1", b1)]:
            if not np.all(np.isfinite(arr)):
                raise InvalidAttack(f"{name} contains non-finite values")
            if np.any(np.abs(arr) > MAX_WEIGHT):
                raise InvalidAttack(f"{name} exceeds max weight magnitude {MAX_WEIGHT}")

        self.W0, self.b0, self.W1, self.b1 = W0, b0, W1, b1

    def __call__(self, obs: np.ndarray) -> np.ndarray:
        h = np.tanh(self.W0 @ obs + self.b0)
        y = np.tanh(self.W1 @ h + self.b1)
        norm = float(np.linalg.norm(y))
        if norm > MAX_DELTA_L2:
            y = y * (MAX_DELTA_L2 / norm)
        return y.astype(np.float32)


def load_from_base64(b64_str: str) -> AttackModel:
    if not isinstance(b64_str, str):
        raise InvalidAttack("npz_b64 must be a string")
    if len(b64_str) > MAX_FILE_SIZE * 2:
        raise InvalidAttack(f"file too large (> {MAX_FILE_SIZE} bytes)")
    try:
        data = base64.b64decode(b64_str, validate=True)
    except Exception as e:
        raise InvalidAttack(f"bad base64: {e}")
    if len(data) > MAX_FILE_SIZE:
        raise InvalidAttack(f"file too large (> {MAX_FILE_SIZE} bytes)")
    try:
        arrays = np.load(io.BytesIO(data), allow_pickle=False)
    except Exception as e:
        raise InvalidAttack(f"bad npz file: {e}")
    return AttackModel(arrays)

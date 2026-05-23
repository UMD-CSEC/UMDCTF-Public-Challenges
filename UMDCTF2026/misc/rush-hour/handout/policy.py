import os
import numpy as np

ARCH = [8, 32, 32, 2]


class Policy:
    def __init__(self, weights_path: str):
        data = np.load(weights_path)
        self.W = [data[f"W{i}"].astype(np.float32) for i in range(len(ARCH) - 1)]
        self.b = [data[f"b{i}"].astype(np.float32) for i in range(len(ARCH) - 1)]

    def __call__(self, obs: np.ndarray) -> tuple[float, float]:
        x = obs
        for i in range(len(self.W) - 1):
            x = np.tanh(self.W[i] @ x + self.b[i])
        y = np.tanh(self.W[-1] @ x + self.b[-1])
        return float(y[0]), float(y[1])


def load_default_policy() -> Policy:
    here = os.path.dirname(os.path.abspath(__file__))
    return Policy(os.path.join(here, "weights.npz"))

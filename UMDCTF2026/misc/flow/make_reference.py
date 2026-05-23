from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from data import make_dataset
from predictor import Predictor

HERE = Path(__file__).parent

def main():
    torch.manual_seed(8)
    X, _ = make_dataset(500, seed=888)
    model = Predictor()
    model.load_state_dict(torch.load(HERE / "dist" / "predictor.pt"))
    model.eval()
    with torch.no_grad():
        probs = F.softmax(model(torch.from_numpy(X)), dim=1).numpy()
    idx = int(np.where(probs[:, 0] > 0.95)[0][0])
    np.save(HERE / "dist" / "reference_window.npy", X[idx])
    print(f"picked idx={idx}  p(class=0)={probs[idx, 0]:.4f}")

if __name__ == "__main__":
    main()

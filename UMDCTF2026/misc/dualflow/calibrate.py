from pathlib import Path

import numpy as np
import torch

from data import make_dataset
from flow import RealNVP
from challenge import log_prob_parts

HERE = Path(__file__).parent

def load_flow(name):
    d = torch.load(HERE / "dist" / name)
    flow = RealNVP(channels=d["channels"], window=d["window"], n_layers=d["n_layers"], hidden=d["hidden"])
    flow.load_state_dict(d["state_dict"]); flow.eval()
    return flow

def main():
    torch.manual_seed(5)
    f0 = load_flow("flow_0.pt"); f1 = load_flow("flow_1.pt")

    X, y = make_dataset(5000, seed=55)
    X0 = torch.from_numpy(X[y == 0]); X1 = torch.from_numpy(X[y == 1])

    with torch.no_grad():
        lp0_all = f0.log_prob(torch.from_numpy(X)).numpy()
        lp1_all = f1.log_prob(torch.from_numpy(X)).numpy()
    print(f"generative classifier accuracy: {((lp1_all > lp0_all).astype(np.int64) == y).mean():.3f}")

    with torch.no_grad():
        _, ld0_c0, lp0_c0 = log_prob_parts(f0, X0)
        _, ld1_c1, lp1_c1 = log_prob_parts(f1, X1)
    band0 = (float(np.quantile(ld0_c0.numpy(), 0.01)), float(np.quantile(ld0_c0.numpy(), 0.99)))
    band1 = (float(np.quantile(ld1_c1.numpy(), 0.01)), float(np.quantile(ld1_c1.numpy(), 0.99)))
    lp_thresh0 = float(np.quantile(lp0_c0.numpy(), 0.05))
    lp_thresh1 = float(np.quantile(lp1_c1.numpy(), 0.05))
    print(f"flow_0 on class-0: lp 5%={lp_thresh0:.2f}  |det J| band={band0}")
    print(f"flow_1 on class-1: lp 5%={lp_thresh1:.2f}  |det J| band={band1}")

    Xref_pool, yref_pool = make_dataset(2000, seed=77)
    Xref0 = Xref_pool[yref_pool == 0]
    with torch.no_grad():
        margins = (f0.log_prob(torch.from_numpy(Xref0)) - f1.log_prob(torch.from_numpy(Xref0))).numpy()
    pos = np.where(margins > 0)[0]
    order = pos[np.argsort(margins[pos])]
    idx = int(order[len(order) // 20])
    x_ref = Xref0[idx]
    print(f"reference margin log q0 - log q1 = {margins[idx]:.2f}")
    np.save(HERE / "dist" / "reference_window.npy", x_ref)

    np.savez(HERE / "dist" / "calibration.npz",
             band0_lo=band0[0], band0_hi=band0[1],
             band1_lo=band1[0], band1_hi=band1[1],
             lp_thresh0=lp_thresh0, lp_thresh1=lp_thresh1,
             target_margin=30.0)

if __name__ == "__main__":
    main()

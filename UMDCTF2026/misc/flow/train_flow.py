from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from data import make_dataset
from flow import RealNVP

HERE = Path(__file__).parent

def main(n_train=20000, n_cal=4000, epochs=20):
    torch.manual_seed(2)
    Xtr, _ = make_dataset(n_train, seed=21)
    Xca, _ = make_dataset(n_cal, seed=22)

    flow = RealNVP(channels=5, window=64, n_layers=6, hidden=128)
    flat = torch.from_numpy(Xtr).reshape(n_train, -1)
    flow.mu.copy_(flat.mean(0))
    flow.sigma.copy_(flat.std(0).clamp_min(1e-6))

    dl = DataLoader(TensorDataset(torch.from_numpy(Xtr)), batch_size=256, shuffle=True)
    opt = torch.optim.Adam(flow.parameters(), lr=5e-4)
    for ep in range(epochs):
        flow.train(); tot = n = 0
        for (xb,) in dl:
            nll = -flow.log_prob(xb).mean()
            opt.zero_grad(); nll.backward()
            torch.nn.utils.clip_grad_norm_(flow.parameters(), 5.0)
            opt.step()
            tot += nll.item() * xb.size(0); n += xb.size(0)
        if (ep + 1) % 3 == 0 or ep == 0:
            print(f"ep {ep+1}/{epochs}  nll/dim={tot/n/flow.dim:.4f}")

    flow.eval()
    with torch.no_grad():
        lp_clean = flow.log_prob(torch.from_numpy(Xca)).numpy()
    threshold = float(np.quantile(lp_clean, 0.05))
    print(f"clean log_prob: 5%={threshold:.2f}  50%={np.median(lp_clean):.2f}")

    out = HERE / "dist" / "flow.pt"
    torch.save({"state_dict": flow.state_dict(), "threshold": threshold,
                "channels": 5, "window": 64, "n_layers": 6, "hidden": 128}, out)
    print("saved", out)


if __name__ == "__main__":
    main()

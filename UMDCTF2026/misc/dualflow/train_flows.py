from pathlib import Path

import torch
from torch.utils.data import DataLoader, TensorDataset

from data import make_dataset
from flow import RealNVP

HERE = Path(__file__).parent

def train_one(Xc, name, epochs=25):
    flow = RealNVP(channels=5, window=64, n_layers=6, hidden=128)
    flat = torch.from_numpy(Xc).reshape(Xc.shape[0], -1)
    flow.mu.copy_(flat.mean(0))
    flow.sigma.copy_(flat.std(0).clamp_min(1e-6))

    dl = DataLoader(TensorDataset(torch.from_numpy(Xc)), batch_size=256, shuffle=True)
    opt = torch.optim.Adam(flow.parameters(), lr=5e-4)
    for ep in range(epochs):
        flow.train(); tot = n = 0
        for (xb,) in dl:
            nll = -flow.log_prob(xb).mean()
            opt.zero_grad(); nll.backward()
            torch.nn.utils.clip_grad_norm_(flow.parameters(), 5.0)
            opt.step()
            tot += nll.item() * xb.size(0); n += xb.size(0)
        if (ep + 1) % 5 == 0 or ep == 0:
            print(f"  [{name}] ep {ep+1}/{epochs}  nll/dim={tot/n/flow.dim:.4f}")
    return flow

def main(n_total=40000, epochs=25):
    torch.manual_seed(3)
    X, y = make_dataset(n_total, seed=31)
    X0 = X[y == 0]; X1 = X[y == 1]
    print(f"class0 {len(X0)}  class1 {len(X1)}")

    print("training flow_0...")
    f0 = train_one(X0, "flow_0", epochs=epochs)
    print("training flow_1...")
    f1 = train_one(X1, "flow_1", epochs=epochs)

    for flow, name in [(f0, "flow_0.pt"), (f1, "flow_1.pt")]:
        torch.save({"state_dict": flow.state_dict(),
                    "channels": 5, "window": 64, "n_layers": 6, "hidden": 128}, HERE / "dist" / name)
        print("saved", HERE / "dist" / name)

if __name__ == "__main__":
    main()

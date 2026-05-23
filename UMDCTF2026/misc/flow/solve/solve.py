import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from predictor import Predictor
from flow import RealNVP

EPS = 0.05
STEPS = 400
LR = 5e-2
PURIFY_STEPS = 3
PURIFY_ALPHA = 0.55

HERE = Path(__file__).resolve().parent.parent
HANDOUT = HERE / "dist"

class BPDAIdentity(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, purified_value):
        return purified_value

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output, None

def purify_no_grad(x, flow, n_steps=PURIFY_STEPS, alpha=PURIFY_ALPHA):
    with torch.no_grad():
        for _ in range(n_steps):
            z, _ = flow.forward(x)
            x = flow.inverse(alpha * z)
    return x

def main():
    x_ref = np.load(HANDOUT / "reference_window.npy")
    predictor = Predictor(); predictor.load_state_dict(torch.load(HANDOUT / "predictor.pt")); predictor.eval()
    for p in predictor.parameters(): p.requires_grad_(False)
    d = torch.load(HANDOUT / "flow.pt")
    flow = RealNVP(channels=d["channels"], window=d["window"], n_layers=d["n_layers"], hidden=d["hidden"])
    flow.load_state_dict(d["state_dict"]); flow.eval()
    for p in flow.parameters(): p.requires_grad_(False)
    lp_thresh = float(d["threshold"])

    x0 = torch.from_numpy(x_ref).unsqueeze(0)
    with torch.no_grad():
        z0, _ = flow.forward(x0)
    dz = torch.zeros_like(z0, requires_grad=True)
    target = torch.tensor([1])
    opt = torch.optim.Adam([dz], lr=LR)

    best_p1, best_x, best_step = -1.0, None, -1
    for step in range(STEPS):
        x_decoded = flow.inverse(z0 + dz)
        x_sub = x0 + torch.clamp(x_decoded - x0, -EPS, EPS)
        x_pure = BPDAIdentity.apply(x_sub, purify_no_grad(x_sub, flow))
        logits = predictor(x_pure)
        loss = F.cross_entropy(logits, target)
        opt.zero_grad(); loss.backward(); opt.step()

        with torch.no_grad():
            p1 = F.softmax(logits, dim=1)[0, 1].item()
            lp = flow.log_prob(x_sub).item()
            if lp > lp_thresh and p1 > best_p1:
                best_p1, best_x, best_step = p1, x_sub.clone(), step

        if step % 20 == 0 or step == STEPS - 1:
            print(f"step {step:3d}  p1(purified)={p1:.3f}  log_prob={lp:.1f}  linf={(x_sub - x0).abs().max().item():.5f}")
        if best_p1 > 0.95 and lp < lp_thresh + 50:
            print(f"early stop at step {step}: best at step {best_step} p1={best_p1:.3f}")
            break

    if best_x is None:
        raise RuntimeError("no feasible attack found")
    out = HERE / "solve" / "submission.npy"
    np.save(out, best_x.detach().squeeze(0).numpy().astype(np.float32))
    print(f"saved {out}")

if __name__ == "__main__":
    main()

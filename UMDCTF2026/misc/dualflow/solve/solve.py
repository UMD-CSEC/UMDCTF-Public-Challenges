import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pathlib import Path

import numpy as np
import torch

from challenge import load_flow, log_prob_parts

EPS = 0.08
OUTER_STEPS = 200
STEP_L2 = 0.002

HERE = Path(__file__).resolve().parent.parent
HANDOUT = HERE / "dist"

def flat_grad(scalar, x):
    g, = torch.autograd.grad(scalar, x, retain_graph=True)
    return g.reshape(-1)

def orthogonalize(target, against_list):
    out = target.clone()
    for u in against_list:
        u_hat = u / (u.norm() + 1e-12)
        out = out - (out @ u_hat) * u_hat
    return out

def main():
    x_ref_np = np.load(HANDOUT / "reference_window.npy")
    f0 = load_flow("flow_0.pt"); f1 = load_flow("flow_1.pt")
    for p in f0.parameters(): p.requires_grad_(False)
    for p in f1.parameters(): p.requires_grad_(False)
    cal = np.load(HANDOUT / "calibration.npz")
    lp_thresh1 = float(cal["lp_thresh1"])
    band1 = (float(cal["band1_lo"]), float(cal["band1_hi"]))
    target_margin = float(cal["target_margin"])

    shape = (1,) + x_ref_np.shape
    N = int(np.prod(x_ref_np.shape))
    x_ref = torch.from_numpy(x_ref_np).unsqueeze(0)
    delta_flat = torch.zeros(N)

    best = None
    for step in range(OUTER_STEPS):
        x = (x_ref + delta_flat.reshape(shape)).detach().requires_grad_(True)
        _, _, lp0 = log_prob_parts(f0, x)
        _, ld1, lp1 = log_prob_parts(f1, x)
        m = (lp1 - lp0).squeeze()

        gm = flat_grad(m, x)
        gr = flat_grad(lp1.squeeze(), x)
        gj = flat_grad(ld1.squeeze(), x)

        g_perp = orthogonalize(gm, [gr, gj])
        if g_perp.norm() < 1e-8:
            print("g_perp ~ 0; aborting")
            break

        delta_flat = delta_flat + STEP_L2 * (g_perp / (g_perp.norm() + 1e-12))
        delta_flat = delta_flat.clamp_(-EPS, EPS)

        with torch.no_grad():
            x_new = x_ref + delta_flat.reshape(shape)
            _, _, lp0_v = log_prob_parts(f0, x_new)
            _, ld1_v, lp1_v = log_prob_parts(f1, x_new)
            margin_v = (lp1_v - lp0_v).item()
            lp1_val = lp1_v.item()
            ld1_val = ld1_v.item()
            linf = delta_flat.abs().max().item()
            feasible = (margin_v >= target_margin
                        and lp1_val >= lp_thresh1
                        and band1[0] <= ld1_val <= band1[1]
                        and linf <= EPS + 1e-6)
            if feasible:
                slack = min(margin_v - target_margin,
                            lp1_val - lp_thresh1,
                            ld1_val - band1[0],
                            band1[1] - ld1_val)
                if best is None or slack > best[0]:
                    best = (slack, x_new.detach().clone(), step)

        if step % 10 == 0 or step == OUTER_STEPS - 1:
            status = "★" if feasible else " "
            print(f"step {step:3d} {status}  margin={margin_v:+7.2f}  "
                  f"log_q1={lp1_val:8.2f}  log_det1={ld1_val:7.2f}  linf={linf:.4f}")
        if best is not None and step >= best[2] + 20:
            print(f"early stop: best feasible at step {best[2]} slack={best[0]:.2f}")
            break

    if best is None:
        raise RuntimeError("no feasible attack found")
    out = HERE / "solve" / "submission.npy"
    np.save(out, best[1].squeeze(0).numpy().astype(np.float32))
    print(f"saved {out}")

if __name__ == "__main__":
    main()

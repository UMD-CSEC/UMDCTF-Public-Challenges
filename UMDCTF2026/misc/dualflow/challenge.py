#!/usr/local/bin/python
import base64
import io
import os
import sys
from pathlib import Path

import numpy as np
import torch

from flow import RealNVP

HERE = Path(__file__).parent
HANDOUT = HERE / "dist"

EPS = 0.08
FLAG = open("./flag.txt", "r").read()

def load_flow(name):
    d = torch.load(HANDOUT / name)
    flow = RealNVP(channels=d["channels"], window=d["window"], n_layers=d["n_layers"], hidden=d["hidden"])
    flow.load_state_dict(d["state_dict"]); flow.eval()
    return flow

def log_prob_parts(flow, x):
    z, log_det = flow.forward(x)
    log_prior = -0.5 * (z ** 2).sum(dim=1) - 0.5 * flow.dim * np.log(2.0 * np.pi)
    return log_prior, log_det, log_prior + log_det

def check(sub, x_ref, f0, f1, cal):
    if sub.shape != x_ref.shape:
        return False, f"shape mismatch {sub.shape} vs {x_ref.shape}", None
    if sub.dtype != np.float32:
        sub = sub.astype(np.float32)

    linf = float(np.max(np.abs(sub - x_ref)))
    if linf > EPS + 1e-6:
        return False, f"L-inf budget exceeded: {linf:.6f} > {EPS}", None

    t = torch.from_numpy(sub[None])
    with torch.no_grad():
        _, _, lp0 = log_prob_parts(f0, t)
        _, ld1, lp1 = log_prob_parts(f1, t)
    lp0, lp1, ld1 = float(lp0.item()), float(lp1.item()), float(ld1.item())
    margin = lp1 - lp0

    target_margin = float(cal["target_margin"])
    lp_thresh1 = float(cal["lp_thresh1"])
    band1 = (float(cal["band1_lo"]), float(cal["band1_hi"]))

    if margin < target_margin:
        return False, f"margin too low: log q_1 - log q_0 = {margin:.2f} < {target_margin}", None
    if lp1 < lp_thresh1:
        return False, f"flow_1 rejects realism: log q_1 = {lp1:.2f} < {lp_thresh1:.2f}", None
    if not (band1[0] <= ld1 <= band1[1]):
        return False, f"flow_1 Jacobian out of band: log|det J_f1| = {ld1:.2f} not in {band1}", None
    return True, f"OK  linf={linf:.5f}  margin={margin:.2f}  log_q1={lp1:.2f}  log_det1={ld1:.2f}", FLAG

def read_submission():
    sys.stdout.write("submit base64(numpy float32 array, shape (5, 64)):\n> ")
    sys.stdout.flush()
    line = sys.stdin.readline().strip()
    if not line:
        print("empty input"); sys.exit(2)
    try:
        raw = base64.b64decode(line, validate=False)
        return np.load(io.BytesIO(raw))
    except Exception as e:
        print(f"could not decode submission: {e}"); sys.exit(2)

def main():
    x_ref = np.load(HANDOUT / "reference_window.npy")
    f0 = load_flow("flow_0.pt"); f1 = load_flow("flow_1.pt")
    cal = np.load(HANDOUT / "calibration.npz")
    print(f"EPS={EPS}  target_margin={float(cal['target_margin'])}  "
          f"lp_thresh1={float(cal['lp_thresh1']):.2f}  "
          f"band1=({float(cal['band1_lo']):.2f}, {float(cal['band1_hi']):.2f})")
    sub = read_submission()
    ok, msg, flag = check(sub, x_ref, f0, f1, cal)
    print(f"{msg}")
    if ok:
        print(f"FLAG: {flag}")
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    main()

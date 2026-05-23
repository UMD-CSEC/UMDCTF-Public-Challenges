#!/usr/local/bin/python
import base64
import io
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from predictor import Predictor
from flow import RealNVP

HERE = Path(__file__).parent
HANDOUT = HERE / "dist"

EPS = 0.05
CONF_FLIP = 0.80
PURIFY_STEPS = 3
PURIFY_ALPHA = 0.55
FLAG = open("./flag.txt", "r").read()

def load_all():
    x_ref = np.load(HANDOUT / "reference_window.npy")
    predictor = Predictor()
    predictor.load_state_dict(torch.load(HANDOUT / "predictor.pt"))
    predictor.eval()
    d = torch.load(HANDOUT / "flow.pt")
    flow = RealNVP(channels=d["channels"], window=d["window"], n_layers=d["n_layers"], hidden=d["hidden"])
    flow.load_state_dict(d["state_dict"])
    flow.eval()
    return x_ref, predictor, flow, float(d["threshold"])


def purify(x, flow, n_steps=PURIFY_STEPS, alpha=PURIFY_ALPHA):
    for _ in range(n_steps):
        z, _ = flow.forward(x)
        x = flow.inverse(alpha * z)
    return x

def check(sub, x_ref, predictor, flow, lp_thresh):
    if sub.shape != x_ref.shape:
        return False, f"shape mismatch {sub.shape} vs {x_ref.shape}", None
    if sub.dtype != np.float32:
        sub = sub.astype(np.float32)

    linf = float(np.max(np.abs(sub - x_ref)))
    if linf > EPS + 1e-6:
        return False, f"L-inf budget exceeded: {linf:.6f} > {EPS}", None

    t = torch.from_numpy(sub[None])
    with torch.no_grad():
        lp = float(flow.log_prob(t).item())
    if lp < lp_thresh:
        return False, f"sanity log_prob too low: {lp:.2f} < {lp_thresh:.2f}", None

    with torch.no_grad():
        probs = F.softmax(predictor(purify(t, flow)), dim=1).numpy()[0]
    if probs[1] < CONF_FLIP:
        return False, f"post-purification prediction not flipped: p(class=1)={probs[1]:.4f} < {CONF_FLIP}", None
    return True, f"OK  linf={linf:.5f}  log_prob={lp:.2f}  p1(purified)={probs[1]:.4f}", FLAG


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
    x_ref, predictor, flow, lp_thresh = load_all()
    print(f"EPS={EPS}  CONF_FLIP={CONF_FLIP}  PURIFY_STEPS={PURIFY_STEPS}  ALPHA={PURIFY_ALPHA}  LP_THRESH={lp_thresh:.2f}")
    sub = read_submission()
    ok, msg, flag = check(sub, x_ref, predictor, flow, lp_thresh)
    print(f"{msg}")
    if ok:
        print(f"FLAG: {flag}")
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    main()

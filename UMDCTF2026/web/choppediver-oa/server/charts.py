import io
import random
import secrets
from enum import Enum

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class Direction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


def _generate_series(direction: Direction, n: int = 120) -> list[tuple[float, float, float, float]]:
    mu = 100.0
    price = mu
    candles = []
    for _ in range(n):
        o = price
        if direction == Direction.BUY:
            # Modest drift + heavy noise so ~1/3 of candles are red, but the
            # overall trajectory is unmistakably up.
            move = random.gauss(0.45, 1.15)
            # Occasional big swing for realism
            if random.random() < 0.05:
                move += random.choice([-2.5, 3.0])
        elif direction == Direction.SELL:
            move = random.gauss(-0.45, 1.15)
            if random.random() < 0.05:
                move += random.choice([-3.0, 2.5])
        else:
            # Mean-reverting around mu so the line stays visibly flat.
            move = -0.25 * (o - mu) + random.gauss(0, 0.35)
        c = o + move
        wick_scale = 0.45 if direction == Direction.HOLD else 0.8
        wick_up = abs(random.gauss(0, wick_scale))
        wick_down = abs(random.gauss(0, wick_scale))
        h = max(o, c) + wick_up
        l = min(o, c) - wick_down
        candles.append((o, h, l, c))
        price = c
    return candles


def render_chart(direction: Direction, seed: int | None = None) -> bytes:
    if seed is not None:
        random.seed(seed)
    candles = _generate_series(direction)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=130, facecolor="#0b0d12")
    ax.set_facecolor("#0b0d12")

    up_color = "#26a269"
    down_color = "#c01c28"
    wick_color = "#9aa0a6"

    for i, (o, h, l, c) in enumerate(candles):
        color = up_color if c >= o else down_color
        ax.vlines(i, l, h, color=wick_color, linewidth=0.9, alpha=0.85)
        body_low = min(o, c)
        body_h = max(abs(c - o), 0.08)
        rect = Rectangle((i - 0.35, body_low), 0.7, body_h,
                         facecolor=color, edgecolor=color, linewidth=0.5, alpha=0.95)
        ax.add_patch(rect)

    ax.set_xlim(-1, len(candles))
    prices = [p for o, h, l, c in candles for p in (h, l)]
    lo, hi = min(prices), max(prices)
    pad = (hi - lo) * 0.08
    ax.set_ylim(lo - pad, hi + pad)

    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
    ax.tick_params(colors="#9aa0a6", labelsize=9)
    ax.grid(True, color="#1a1f2a", linewidth=0.5, alpha=0.6)
    ax.set_xticks([])
    ax.set_ylabel("Price ($)", color="#9aa0a6", fontsize=10)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(),
                bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    return _pad(buf.getvalue())


_PAD_TARGET = 32_768


def _pad(png: bytes) -> bytes:
    if len(png) >= _PAD_TARGET:
        return png
    return png + b"\x00" * (_PAD_TARGET - len(png))


def random_round(seed: int | None = None) -> tuple[Direction, bytes]:
    if seed is not None:
        random.seed(seed)
    direction = secrets.choice([Direction.BUY, Direction.SELL, Direction.HOLD])
    return direction, render_chart(direction)


if __name__ == "__main__":
    for d in Direction:
        png = render_chart(d, seed=42)
        path = f"/tmp/choppediver_chart_{d.value}.png"
        with open(path, "wb") as f:
            f.write(png)
        print(f"{d.value}: {len(png)} bytes -> {path}")

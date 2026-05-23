"""Choppediver OA — server.

Classify each stock-price chart as BUY / SELL / HOLD before the round's
answer window elapses. React fast.
"""
from __future__ import annotations

import json
import os
import ssl
import time
from pathlib import Path

from websockets.sync.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosed

from charts import random_round, Direction
from keepalive import heartbeat_ack
from rounds import ROUND_BUDGETS_MS, TOTAL_ROUNDS


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "4443"))
CERT_PATH = Path(os.environ.get("CERT_PATH", "/app/cert.pem"))
KEY_PATH = Path(os.environ.get("KEY_PATH", "/app/key.pem"))
FLAG = os.environ["FLAG"]


def _send_json(ws: ServerConnection, obj: dict) -> None:
    ws.send(json.dumps(obj))


def _reject(ws: ServerConnection, reason: str) -> None:
    try:
        _send_json(ws, {"type": "reject", "reason": reason})
    except ConnectionClosed:
        pass


def _play_round(ws: ServerConnection, round_idx: int, budget_ms: int) -> bool:
    direction, chart_png = random_round()
    _send_json(ws, {
        "type": "round",
        "round": round_idx + 1,
        "total": TOTAL_ROUNDS,
        "time_ms": budget_ms,
    })
    ws.send(chart_png)

    deadline = time.monotonic() + budget_ms / 1000.0
    poll_interval = 0.001
    while True:
        try:
            msg = ws.recv(timeout=poll_interval)
        except TimeoutError:
            if time.monotonic() > deadline:
                _reject(ws, "timeout")
                return False
            continue

        if isinstance(msg, bytes):
            _reject(ws, "binary not allowed here")
            return False

        try:
            payload = json.loads(msg)
        except json.JSONDecodeError:
            _reject(ws, "bad message")
            return False

        kind = payload.get("type")
        if kind == "heartbeat":
            _send_json(ws, heartbeat_ack())
        elif kind == "answer":
            value = str(payload.get("value", "")).strip().lower()
            if value == direction.value:
                _send_json(ws, {"type": "correct"})
                return True
            _reject(ws, f"wrong: was {direction.value}")
            return False
        else:
            _reject(ws, f"unknown type: {kind}")
            return False


def handler(ws: ServerConnection) -> None:
    try:
        _send_json(ws, {"type": "hello", "total": TOTAL_ROUNDS})
        while True:
            msg = ws.recv()
            if isinstance(msg, bytes):
                _reject(ws, "unexpected binary")
                return
            try:
                payload = json.loads(msg)
            except json.JSONDecodeError:
                _reject(ws, "bad message")
                return
            kind = payload.get("type")
            if kind == "ready":
                break
            if kind == "heartbeat":
                _send_json(ws, heartbeat_ack())
                continue
            _reject(ws, "expected ready")
            return
        for i, budget in enumerate(ROUND_BUDGETS_MS):
            if not _play_round(ws, i, budget):
                return
        _send_json(ws, {"type": "pass", "flag": FLAG})
    except ConnectionClosed:
        pass


def _make_ssl_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(CERT_PATH), str(KEY_PATH))
    return ctx


def main() -> None:
    ssl_ctx = _make_ssl_context()
    with serve(handler, HOST, PORT, ssl=ssl_ctx) as server:
        print(f"choppediver oa listening on wss://{HOST}:{PORT}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()

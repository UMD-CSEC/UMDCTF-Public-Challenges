import asyncio
import json
import logging
import os
import time

import websockets

from attack import InvalidAttack, load_from_base64
from game import GameState
from policy import load_default_policy

HOST = os.environ.get("HOST", "localhost")
PORT = int(os.environ.get("PORT", "3000"))
TICK_HZ = 60
TICK_S = 1.0 / TICK_HZ

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ctf")

policy = load_default_policy()
games: dict = {}


async def send_json(ws, payload: dict) -> None:
    try:
        await ws.send(json.dumps(payload))
    except Exception:
        pass


async def handler(ws):
    path = getattr(getattr(ws, "request", None), "path", None) or getattr(ws, "path", "/ws")
    if path != "/ws":
        return
    game = GameState(policy)
    games[ws] = game
    log.info("client connected (%d total)", len(games))
    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            t = msg.get("type")
            if t == "submit":
                b64 = msg.get("npz_b64")
                if not isinstance(b64, str):
                    await send_json(ws, {"type": "submit_ack", "ok": False, "error": "missing npz_b64"})
                    continue
                try:
                    model = load_from_base64(b64)
                except InvalidAttack as e:
                    game.set_attack_error(str(e))
                    await send_json(ws, {"type": "submit_ack", "ok": False, "error": str(e)})
                    continue
                game.install_attack(model)
                await send_json(ws, {"type": "submit_ack", "ok": True})
            elif t == "reset":
                game.reset()
            elif t == "clear_attack":
                game.install_attack(None)
                await send_json(ws, {"type": "submit_ack", "ok": True, "cleared": True})
    except websockets.ConnectionClosed:
        pass
    finally:
        games.pop(ws, None)
        log.info("client disconnected (%d left)", len(games))


async def tick_loop():
    last = time.perf_counter()
    while True:
        await asyncio.sleep(TICK_S)
        now = time.perf_counter()
        dt = min(now - last, 0.1)
        last = now

        dead = []
        for ws, game in list(games.items()):
            game.step(dt)
            try:
                await ws.send(json.dumps(game.to_state_dict()))
            except Exception:
                dead.append(ws)
        for ws in dead:
            games.pop(ws, None)


async def main():
    log.info("listening on ws://%s:%d/ws", HOST, PORT)
    async with websockets.serve(handler, HOST, PORT):
        await tick_loop()


if __name__ == "__main__":
    asyncio.run(main())

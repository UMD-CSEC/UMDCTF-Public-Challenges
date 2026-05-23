import hashlib
import hmac
import json
import os
import secrets

from flask import Flask, jsonify, make_response, render_template, request
from flask_sock import ConnectionClosed, Sock

import rainbet

app = Flask(__name__)
sock = Sock(app)

FLAG = "UMDCTF{one_might_argue_that_gambling_is_the_best_vice_but_they_would_be_wrong}"
TARGET_STREAK = 25

# sid -> {"streak": int, "progress": dict, "secret": bytes}
SESSIONS: dict[str, dict] = {}


def _new_session() -> str:
    sid = secrets.token_hex(8)
    SESSIONS[sid] = {
        "streak": 0,
        "progress": {"revealed": [], "crossed": 0},
        "secret": secrets.token_bytes(32),
    }
    return sid


# Canonical "what the client is looking at right now" string.
# Must match between client and server byte-for-byte.
def canon_view(sid: str) -> str:
    state = SESSIONS[sid]
    streak = state["streak"]
    if streak >= TARGET_STREAK:
        return f"complete:{streak}"
    game = rainbet.generate_game(sid, streak)
    progress = state["progress"]
    if game["type"] == "mines":
        rev = ",".join(str(x) for x in sorted(progress["revealed"]))
        return f"mines:{streak}:{game['grid_size']}:{game['num_mines']}:{rev}"
    return f"chicken:{streak}:{game['steps']}:{progress['crossed']}"


def sign(sid: str, view: str) -> str:
    return hmac.new(SESSIONS[sid]["secret"], view.encode(), hashlib.sha256).hexdigest()


def _reveal_dict(game: dict) -> dict:
    if game["type"] == "mines":
        return {"type": "mines", "mines": game["mines"]}
    return {
        "type": "chicken",
        "cars": game["cars"],
        "max_safe": rainbet.max_safe_steps(game["cars"]),
    }


def _game_payload(sid: str) -> dict:
    state = SESSIONS[sid]
    streak = state["streak"]
    payload = {
        "session_id": sid,
        "round_idx": streak,
        "streak": streak,
        "target": TARGET_STREAK,
    }
    if streak >= TARGET_STREAK:
        payload["complete"] = True
        return payload
    game = rainbet.generate_game(sid, streak)
    progress = state["progress"]
    gv = {"type": game["type"]}
    if game["type"] == "mines":
        gv["grid_size"] = game["grid_size"]
        gv["num_mines"] = game["num_mines"]
        gv["max_reveals"] = game["max_reveals"]
        gv["revealed"] = list(progress["revealed"])
    else:
        gv["steps"] = game["steps"]
        gv["multipliers"] = game["multipliers"]
        gv["risk"] = game["risk"]
        gv["crossed"] = progress["crossed"]
    payload["game"] = gv
    return payload


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/sessioninfo", methods=["GET"])
def api_sessioninfo():
    sid = request.cookies.get("sid")
    if not sid or sid not in SESSIONS:
        sid = _new_session()
    body = {
        "session_id": sid,
        "secret": SESSIONS[sid]["secret"].hex(),
    }
    resp = make_response(jsonify(body))
    resp.set_cookie("sid", sid, samesite="Lax", httponly=False, path="/")
    return resp


@app.route("/api/reset", methods=["POST"])
def api_reset():
    old = request.cookies.get("sid")
    if old and old in SESSIONS:
        del SESSIONS[old]
    sid = _new_session()
    body = {
        "session_id": sid,
        "secret": SESSIONS[sid]["secret"].hex(),
    }
    resp = make_response(jsonify(body))
    resp.set_cookie("sid", sid, samesite="Lax", httponly=False, path="/")
    return resp


def _send(ws, obj):
    ws.send(json.dumps(obj, separators=(",", ":")))


def _kill_session(sid: str) -> str:
    if sid in SESSIONS:
        del SESSIONS[sid]
    return _new_session()


@sock.route("/ws")
def ws_route(ws):
    sid = request.cookies.get("sid")
    if not sid or sid not in SESSIONS:
        _send(ws, {"kind": "error", "error": "no session; GET /api/sessioninfo first", "fatal": True})
        return

    # Initial state
    hello = {"kind": "hello"}
    hello.update(_game_payload(sid))
    _send(ws, hello)

    try:
        while True:
            raw = ws.receive()
            if raw is None:
                break
            try:
                msg = json.loads(raw)
            except Exception:
                _send(ws, {"kind": "error", "error": "bad json"})
                continue

            state = SESSIONS.get(sid)
            if state is None:
                _send(ws, {"kind": "error", "error": "session gone", "fatal": True})
                return

            if state["streak"] >= TARGET_STREAK:
                _send(ws, {"kind": "result", "result": "complete", "flag": FLAG, "streak": state["streak"]})
                continue

            # Frame-token check: the client's asserted "view" must match the
            # server's current canonical view, and sig must be HMAC over it.
            claimed_view = msg.get("view")
            sig = msg.get("sig", "")
            expected_view = canon_view(sid)
            if claimed_view != expected_view:
                _send(ws, {
                    "kind": "error",
                    "error": "frame desync",
                    "expected_view": expected_view,
                })
                continue
            if not isinstance(sig, str) or not hmac.compare_digest(sig, sign(sid, expected_view)):
                _send(ws, {"kind": "error", "error": "bad sig"})
                continue

            game = rainbet.generate_game(sid, state["streak"])
            progress = state["progress"]
            action = msg.get("action")
            won = lost = False
            err = None

            if game["type"] == "mines":
                mine_set = set(game["mines"])
                total = game["grid_size"] ** 2
                max_reveals = game["max_reveals"]
                if action == "reveal":
                    tile = msg.get("tile")
                    if not isinstance(tile, int) or not 0 <= tile < total:
                        err = "bad tile"
                    elif tile in progress["revealed"]:
                        err = "already revealed"
                    elif tile in mine_set:
                        lost = True
                    else:
                        progress["revealed"].append(tile)
                        if len(progress["revealed"]) == max_reveals:
                            won = True
                elif action == "cashout":
                    if len(progress["revealed"]) == max_reveals:
                        won = True
                    else:
                        lost = True
                else:
                    err = "bad action (reveal|cashout)"
            else:
                car_set = set(game["cars"])
                max_safe = rainbet.max_safe_steps(game["cars"])
                if action == "cross":
                    idx = progress["crossed"]
                    if idx >= rainbet.CHICKEN_STEPS:
                        err = "already at last step"
                    elif idx in car_set:
                        lost = True
                    else:
                        progress["crossed"] += 1
                        if progress["crossed"] == rainbet.CHICKEN_STEPS:
                            won = progress["crossed"] == max_safe
                            if not won:
                                lost = True
                elif action == "cashout":
                    won = progress["crossed"] == max_safe
                    if not won:
                        lost = True
                else:
                    err = "bad action (cross|cashout)"

            if err:
                _send(ws, {"kind": "error", "error": err})
                continue

            if won:
                state["streak"] += 1
                state["progress"] = {"revealed": [], "crossed": 0}
                out = {
                    "kind": "result",
                    "result": "win",
                    "reveal": _reveal_dict(game),
                    "streak": state["streak"],
                    "target": TARGET_STREAK,
                }
                if state["streak"] >= TARGET_STREAK:
                    out["complete"] = True
                    out["flag"] = FLAG
                else:
                    out["next_game"] = _game_payload(sid)
                _send(ws, out)
                continue

            if lost:
                reveal = _reveal_dict(game)
                new_sid = _kill_session(sid)
                sid = new_sid
                out = {
                    "kind": "result",
                    "result": "lose",
                    "reveal": reveal,
                    "streak": 0,
                    "target": TARGET_STREAK,
                    "next_game": _game_payload(sid),
                    "session_id": sid,
                    "secret": SESSIONS[sid]["secret"].hex(),
                }
                _send(ws, out)
                continue

            # still in round
            upd = {"kind": "state", "streak": state["streak"]}
            if game["type"] == "mines":
                upd["revealed"] = list(progress["revealed"])
            else:
                upd["crossed"] = progress["crossed"]
            _send(ws, upd)
    except ConnectionClosed:
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

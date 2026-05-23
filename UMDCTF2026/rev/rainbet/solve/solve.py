"""
Solve script for Rainbet.

Independent Python reimplementation of the algorithm in `rainbet_gen.wasm`
(no `wasmtime` import — this is the "I reversed the wasm" reference impl).

Also drives the WebSocket move protocol with frame tokens.

Requires: requests, websocket-client
"""

import argparse
import hashlib
import hmac as hmac_mod
import json

import requests
import websocket

# -------------------------------------------------------------------------
# Algorithm (mirror of rust-gen/src/lib.rs)
# -------------------------------------------------------------------------

SECRET = bytes([
    0x7e, 0x15, 0xca, 0xfe, 0xd0, 0x0d, 0xfe, 0xed,
    0xb0, 0x0b, 0xfa, 0xce, 0x5b, 0xad, 0xa5, 0x50,
    0xc0, 0xff, 0xee, 0x11, 0x11, 0xde, 0xad, 0xbe,
    0xef, 0xab, 0xad, 0xca, 0xfe, 0x13, 0x37, 0xaa,
])

IV = (
    0x37a5b2d94e6c8f71,
    0x8c1e3f5a7b0d2c4f,
    0x91d6b8e2a4f7c0d3,
    0xf4e7c0a3b6d9e2c5,
    0x13824a69cfd0b5e7,
    0x6fa09c43d527e8b1,
    0xbc58e1df0a6c3793,
    0x2ed47b9061a8c5f3,
)

RC = (
    0xa0761d6478bd642f,
    0xe7037ed1a0b428db,
    0x8ebc6af09c88c6e3,
    0x589965cc75374cc3,
    0x1d8e4e27c39bc93a,
    0xeb44accab455d165,
    0x3b9dff8c52ef5f43,
    0x6b91fa824d69dfae,
    0x9d28a6d6c5a4c39f,
    0x4f6cdd1d45f12853,
    0x2d9cf5b73a6e8147,
    0xc831076b94a2ef5d,
    0x71e583ac4f09d6b2,
    0x58b0c7f9a3e1652d,
    0xfa203e857c91b46f,
    0x9e4d21fb60c83a75,
)

SBOX = bytes([
    0xec, 0xca, 0x0e, 0xf3, 0x08, 0xf0, 0x2a, 0xa2, 0x3b, 0x18, 0x2b, 0x5c, 0x37, 0xbd, 0x12, 0xa8,
    0x05, 0xd3, 0xa1, 0x57, 0x4f, 0x96, 0xfc, 0xf5, 0xa7, 0x14, 0x19, 0x66, 0x58, 0x9b, 0xbf, 0xb4,
    0x39, 0xd5, 0x1e, 0x1a, 0x30, 0xbc, 0x6c, 0x80, 0xb7, 0xed, 0x41, 0x06, 0xd9, 0x17, 0x67, 0xcd,
    0x1d, 0x2c, 0xae, 0x24, 0x03, 0x13, 0xc6, 0x53, 0x83, 0x11, 0x0a, 0xf7, 0xc0, 0x4d, 0xc4, 0x9e,
    0x8d, 0x00, 0x1f, 0xc3, 0x3f, 0x35, 0x9f, 0xcb, 0x72, 0x9d, 0x16, 0x6f, 0xac, 0xce, 0x3c, 0x5e,
    0xa6, 0xe1, 0x7b, 0x34, 0x36, 0x32, 0xb8, 0x95, 0x91, 0x89, 0x52, 0xc1, 0xe7, 0xa3, 0x33, 0x48,
    0x04, 0xcf, 0x10, 0xeb, 0x25, 0xbb, 0x8e, 0x0f, 0x81, 0x6e, 0xb3, 0x43, 0x45, 0x8f, 0x49, 0xf8,
    0x4b, 0x59, 0x07, 0x4a, 0xde, 0xfd, 0xc8, 0xd0, 0x84, 0x8b, 0xfb, 0xda, 0xdb, 0x28, 0xd4, 0x3e,
    0xa4, 0x2f, 0x56, 0xbe, 0xef, 0x86, 0xc7, 0x62, 0xea, 0x76, 0xe9, 0xd6, 0x74, 0xa5, 0x6b, 0xf9,
    0x98, 0x7d, 0x3a, 0x26, 0x5a, 0xaf, 0x87, 0x0d, 0x1b, 0x2e, 0xb2, 0xe3, 0x6a, 0xcc, 0xf1, 0xff,
    0xd7, 0xf6, 0x1c, 0xc9, 0xe8, 0x70, 0x20, 0x4e, 0x23, 0x3d, 0xc2, 0xaa, 0xdc, 0x0b, 0xf2, 0x5f,
    0x7a, 0xfa, 0x88, 0x97, 0x47, 0xd1, 0x0c, 0x02, 0x31, 0x7f, 0xf4, 0x75, 0x15, 0x93, 0x38, 0x8a,
    0x42, 0x90, 0x71, 0xdd, 0x73, 0x55, 0x7e, 0xb5, 0x5b, 0x29, 0x4c, 0x9a, 0xe0, 0x8c, 0xb0, 0xe5,
    0x64, 0x27, 0x01, 0xdf, 0xad, 0x21, 0x79, 0x94, 0x92, 0x51, 0x69, 0x7c, 0x22, 0x63, 0x50, 0x85,
    0x2d, 0xe2, 0x40, 0x46, 0x44, 0xa9, 0x82, 0xb6, 0x61, 0xd8, 0xd2, 0xb9, 0x68, 0xab, 0xb1, 0x5d,
    0x65, 0x54, 0x77, 0xa0, 0xc5, 0xba, 0x60, 0x9c, 0xe4, 0xfe, 0xee, 0x99, 0xe6, 0x78, 0x6d, 0x09,
])

SEP_SECRET = 0x17a3e9b5c2d60481
SEP_SID    = 0x2e91c47d3f80a562
SEP_ROUND  = 0x4c6f2d85b913e7a0

MASK64 = (1 << 64) - 1
GRID_SIZES = (5, 6, 7, 8)
MIN_MINES = 3
CHICKEN_STEPS = 24
CAR_THRESHOLD = 7378697629483820646
NUM_RISK = 4


def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK64


def _sub_bytes(s: list) -> None:
    for i in range(8):
        b = s[i].to_bytes(8, "little")
        s[i] = int.from_bytes(bytes(SBOX[x] for x in b), "little")


def _mix_lanes(s: list) -> None:
    t = [0] * 8
    t[0] = s[0] ^ _rotl(s[3], 13) ^ s[5]
    t[1] = s[1] ^ _rotl(s[4], 17) ^ s[6]
    t[2] = s[2] ^ _rotl(s[5], 19) ^ s[7]
    t[3] = s[3] ^ _rotl(s[6], 23) ^ s[0]
    t[4] = s[4] ^ _rotl(s[7], 29) ^ s[1]
    t[5] = s[5] ^ _rotl(s[0], 31) ^ s[2]
    t[6] = s[6] ^ _rotl(s[1], 37) ^ s[3]
    t[7] = s[7] ^ _rotl(s[2], 41) ^ s[4]
    for i in range(8):
        s[i] = t[i]


def _lane_perm(s: list) -> None:
    # [0,1,2,3,4,5,6,7] -> [3,5,7,1,2,4,6,0]
    a, b, c, d, e, f, g, h = s
    s[0] = d; s[1] = f; s[2] = h; s[3] = b
    s[4] = c; s[5] = e; s[6] = g; s[7] = a


def permute(s: list) -> None:
    for r in range(16):
        # ARX on disjoint pairs
        for p in range(4):
            a = p * 2
            b = a + 1
            s[a] = (s[a] + s[b]) & MASK64
            s[b] = _rotl(s[b], 13) ^ s[a]
            s[a] = _rotl(s[a], 29)
        _sub_bytes(s)
        _mix_lanes(s)
        _lane_perm(s)
        s[0] ^= RC[r]


def init_state(sid: bytes, round_idx: int) -> list:
    s = list(IV)
    # Phase 1: SECRET (32 bytes → 4 lanes)
    for i in range(4):
        s[i] ^= int.from_bytes(SECRET[i * 8:(i + 1) * 8], "little")
    s[7] ^= SEP_SECRET
    permute(s)
    # Phase 2: sid (8 bytes per lane, permute every 8 lanes)
    idx = 0
    off = 0
    while off < len(sid):
        b = sid[off:off + 8].ljust(8, b"\x00")
        s[idx & 7] ^= int.from_bytes(b, "little")
        idx += 1
        off += 8
        if idx & 7 == 0:
            permute(s)
    s[7] ^= SEP_SID
    permute(s)
    # Phase 3: round_idx
    s[0] ^= round_idx & MASK64
    s[7] ^= SEP_ROUND
    permute(s)
    return s


class Rng:
    def __init__(self, s):
        self.s = s
        self.pos = 8  # force permute on first next

    def next_u64(self) -> int:
        if self.pos >= 8:
            permute(self.s)
            self.pos = 0
        v = self.s[self.pos]
        self.pos += 1
        return v

    def range(self, n: int) -> int:
        return self.next_u64() % n


def predict(sid: str, round_idx: int) -> dict:
    state = init_state(sid.encode("ascii"), round_idx)
    rng = Rng(state)

    gtype = rng.next_u64() & 1
    if gtype == 0:
        grid_size = GRID_SIZES[rng.range(len(GRID_SIZES))]
        total = grid_size * grid_size
        num_mines = MIN_MINES + rng.range(1 + total // 4)
        positions = list(range(total))
        for i in range(num_mines):
            j = i + rng.range(total - i)
            positions[i], positions[j] = positions[j], positions[i]
        return {
            "type": "mines",
            "grid_size": grid_size,
            "num_mines": num_mines,
            "mines": sorted(positions[:num_mines]),
        }
    _risk_idx = rng.range(NUM_RISK)
    cars = [i for i in range(CHICKEN_STEPS) if rng.next_u64() < CAR_THRESHOLD]
    return {"type": "chicken", "cars": cars}


def max_safe_chicken(cars) -> int:
    car_set = set(cars)
    for i in range(CHICKEN_STEPS):
        if i in car_set:
            return i
    return CHICKEN_STEPS


# -------------------------------------------------------------------------
# Protocol helpers
# -------------------------------------------------------------------------


def canon_view(game, progress, streak):
    if game["type"] == "mines":
        rev = ",".join(str(x) for x in sorted(progress["revealed"]))
        return f"mines:{streak}:{game['grid_size']}:{game['num_mines']}:{rev}"
    return f"chicken:{streak}:{game['steps']}:{progress['crossed']}"


def sign(secret_bytes, view):
    return hmac_mod.new(secret_bytes, view.encode(), hashlib.sha256).hexdigest()


class Client:
    def __init__(self, base, url):
        self.base = base.rstrip("/")
        self.ws_url = url
        self.http = requests.Session()
        info = self.http.get(f"{self.base}/api/sessioninfo").json()
        self.sid = info["session_id"]
        self.secret = bytes.fromhex(info["secret"])
        cookie_header = "; ".join(f"{k}={v}" for k, v in self.http.cookies.get_dict().items())
        self.ws = websocket.create_connection(self.ws_url, header=[f"Cookie: {cookie_header}"])

    def recv(self):
        return json.loads(self.ws.recv())

    def send_move(self, game, progress, streak, action, **extra):
        view = canon_view(game, progress, streak)
        sig = sign(self.secret, view)
        self.ws.send(json.dumps({"action": action, "view": view, "sig": sig, **extra}))
        return self.recv()


def game_from_hello(hello):
    g = hello["game"]
    return g, {
        "revealed": list(g.get("revealed", [])),
        "crossed": g.get("crossed", 0),
    }, hello["streak"]


def play(base_http, ws_url):
    c = Client(base_http, ws_url)
    hello = c.recv()
    assert hello["kind"] == "hello"
    game, progress, streak = game_from_hello(hello)
    sid = hello["session_id"]

    while True:
        pred = predict(sid, streak)
        if pred["type"] != game["type"]:
            raise RuntimeError(f"type mismatch @ streak {streak}: {game['type']} vs {pred['type']}")

        if pred["type"] == "mines":
            if pred["grid_size"] != game["grid_size"] or pred["num_mines"] != game["num_mines"]:
                raise RuntimeError(
                    f"mines param mismatch @ streak {streak}: "
                    f"server {game['grid_size']}x/{game['num_mines']} vs "
                    f"predicted {pred['grid_size']}x/{pred['num_mines']}"
                )
            mines = set(pred["mines"])
            total = pred["grid_size"] * pred["grid_size"]
            safe = [t for t in range(total) if t not in mines]
            msg = None
            for tile in safe:
                msg = c.send_move(game, progress, streak, "reveal", tile=tile)
                if msg["kind"] == "state":
                    progress["revealed"] = msg["revealed"]
                    streak = msg["streak"]
                elif msg["kind"] == "result":
                    break
                elif msg["kind"] == "error":
                    raise RuntimeError(f"error: {msg}")
        else:
            safe_n = max_safe_chicken(pred["cars"])
            msg = None
            for _ in range(safe_n):
                msg = c.send_move(game, progress, streak, "cross")
                if msg["kind"] == "state":
                    progress["crossed"] = msg["crossed"]
                    streak = msg["streak"]
                elif msg["kind"] == "result":
                    break
                elif msg["kind"] == "error":
                    raise RuntimeError(f"error: {msg}")
            if msg is None or msg["kind"] == "state":
                msg = c.send_move(game, progress, streak, "cashout")

        if msg["kind"] != "result":
            raise RuntimeError(f"unexpected: {msg}")
        if msg["result"] == "lose":
            raise RuntimeError(f"lost round {streak}: {msg}")
        if msg["result"] != "win":
            raise RuntimeError(f"weird result: {msg}")

        streak = msg["streak"]
        shape = pred["type"]
        if shape == "mines":
            shape += f" {pred['grid_size']}x{pred['grid_size']}/{pred['num_mines']}"
        else:
            shape += f" safe={max_safe_chicken(pred['cars'])}"
        print(f"[+] round {streak - 1} won ({shape})  streak={streak}/{msg['target']}")

        if msg.get("complete"):
            return msg["flag"]
        ng = msg["next_game"]
        sid = ng["session_id"]
        game, progress, streak = game_from_hello(ng)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    args = ap.parse_args()
    base = args.url.rstrip("/")
    ws_url = base.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
    flag = play(base, ws_url)
    print(f"[flag] {flag}")


if __name__ == "__main__":
    main()

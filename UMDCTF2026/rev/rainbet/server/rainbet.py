import os
from typing import Sequence

import wasmtime

CHICKEN_STEPS = 24
RISK_NAMES = ("Easy", "Medium", "Hard", "Daredevil")

CHICKEN_MULT_TABLES = (
    (1.03, 1.08, 1.14, 1.21, 1.30, 1.40, 1.52, 1.66, 1.82, 2.01,
     2.24, 2.52, 2.86, 3.27, 3.77, 4.40, 5.21, 6.26, 7.65, 9.52,
     12.12, 15.75, 20.93, 28.52),
    (1.14, 1.38, 1.67, 2.01, 2.43, 2.93, 3.54, 4.28, 5.17, 6.24,
     7.54, 9.10, 10.99, 13.28, 16.04, 19.37, 23.40, 28.25, 34.11, 41.19,
     49.75, 60.08, 72.55, 87.61),
    (1.60, 2.74, 4.85, 8.90, 16.98, 33.97, 70.23, 150.50, 333.87, 768.41,
     1835.50, 4558.50, 11815.00, 31929.00, 91101.00, 275088.00, 882501.00, 3014100.00, 11047000.00, 43692000.00,
     189060000.00, 903960000.00, 4855700000.00, 30242000000.00),
    (2.50, 6.85, 18.96, 52.65, 146.5, 408.0, 1139.0, 3187.0, 8932.0, 25072.0,
     70450.0, 198158.0, 557930.0, 1571000.0, 4427000.0, 12482000.0, 35223000.0, 99455000.0, 281096000.0, 794796000.0,
     2248571000.0, 6362800000.0, 18000000000.0, 50930000000.0),
)

_WASM_PATH = os.path.join(os.path.dirname(__file__), "rainbet_gen.wasm")
_engine = wasmtime.Engine()
_module = wasmtime.Module.from_file(_engine, _WASM_PATH)


def _instance():
    store = wasmtime.Store(_engine)
    inst = wasmtime.Instance(store, _module, [])
    exports = inst.exports(store)
    return store, exports


def _call_generate(session_id: str, round_idx: int) -> bytes:
    store, exports = _instance()
    memory = exports["memory"]
    sid_bytes = session_id.encode("ascii")
    if len(sid_bytes) > 64:
        raise ValueError("session_id too long")

    sid_ptr = exports["sid_buf_ptr"](store)
    out_ptr = exports["out_buf_ptr"](store)
    memory.write(store, sid_bytes, sid_ptr)

    n = exports["generate"](store, len(sid_bytes), round_idx)
    return bytes(memory.read(store, out_ptr, out_ptr + n))


def generate_game(session_id: str, round_idx: int) -> dict:
    raw = _call_generate(session_id, round_idx)
    gtype = raw[0]
    if gtype == 0:
        grid_size = raw[1]
        num_mines = raw[2]
        mines = list(raw[3:3 + num_mines])
        return {
            "type": "mines",
            "grid_size": grid_size,
            "num_mines": num_mines,
            "mines": mines,
            "max_reveals": grid_size * grid_size - num_mines,
        }
    if gtype == 1:
        risk_idx = raw[1]
        num_cars = raw[2]
        cars = list(raw[3:3 + num_cars])
        return {
            "type": "chicken",
            "steps": CHICKEN_STEPS,
            "risk_idx": risk_idx,
            "risk": RISK_NAMES[risk_idx],
            "multipliers": list(CHICKEN_MULT_TABLES[risk_idx]),
            "cars": cars,
        }
    raise RuntimeError(f"unknown game type {gtype}")


def max_safe_steps(cars: Sequence[int]) -> int:
    car_set = set(cars)
    for i in range(CHICKEN_STEPS):
        if i in car_set:
            return i
    return CHICKEN_STEPS


def is_mines_max_win(game: dict, moves) -> bool:
    if game["type"] != "mines" or not isinstance(moves, list):
        return False
    total = game["grid_size"] ** 2
    max_reveals = total - game["num_mines"]
    if len(moves) != max_reveals:
        return False
    mines = set(game["mines"])
    seen = set()
    for m in moves:
        if not isinstance(m, int) or m < 0 or m >= total:
            return False
        if m in mines or m in seen:
            return False
        seen.add(m)
    return True


def is_chicken_max_win(game: dict, cash_out_at) -> bool:
    if game["type"] != "chicken" or not isinstance(cash_out_at, int):
        return False
    if cash_out_at < 0 or cash_out_at > CHICKEN_STEPS:
        return False
    return cash_out_at == max_safe_steps(game["cars"])

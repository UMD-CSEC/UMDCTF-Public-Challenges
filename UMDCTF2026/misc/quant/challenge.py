#!/usr/local/bin/python3
import math
import os
import pathlib
import re
import secrets
import sys
from collections import Counter

import numpy as np


N_BITS = 16
N_QUBITS = N_BITS + 1
ANCILLA = N_BITS
MAX_BYTES = 200_000
MAX_ORACLE_CALLS = 250
SHOTS = 512
SUCCESS_PROBABILITY = 0.55

LINE_RE = re.compile(
    r"^(?P<op>h|x|z|mcx|oracle|diffuse|measure)\s+(?P<args>[^;]+);$",
    re.IGNORECASE,
)
QUBIT_RE = re.compile(r"q\[(\d+)\]$")
MEASURE_RE = re.compile(r"^q\[(\d+)\]\s*->\s*c\[(\d+)\]$")


class QisketError(Exception):
    pass


def load_flag():
    if "FLAG" in os.environ:
        return os.environ["FLAG"].strip()
    flag_path = pathlib.Path(__file__).resolve().with_name("flag.txt")
    try:
        with open(flag_path, "r", encoding="utf-8") as flag_file:
            return flag_file.read().strip()
    except FileNotFoundError:
        raise RuntimeError("missing flag: set FLAG or provide flag.txt") from None


FLAG = load_flag()
FLAG_PAYLOAD = FLAG.removeprefix("UMDCTF{").removesuffix("}")
PAYLOAD_BITS = (
    FLAG_PAYLOAD
    if len(FLAG_PAYLOAD) == N_BITS and all(ch in "01" for ch in FLAG_PAYLOAD)
    else "".join(f"{byte:08b}" for byte in FLAG_PAYLOAD.encode())
)
MARKED_BITS = os.getenv("QISKET_MARKED_BITS", PAYLOAD_BITS)
MCX_PAIRS = {}


def check_secret():
    if len(MARKED_BITS) != N_BITS or any(ch not in "01" for ch in MARKED_BITS):
        raise QisketError("server is misconfigured")


def parse_qubit(token):
    match = QUBIT_RE.match(token.strip())
    if not match:
        raise QisketError(f"bad qubit operand: {token!r}")
    qubit = int(match.group(1))
    if not 0 <= qubit < N_QUBITS:
        raise QisketError(f"qubit index out of range: q[{qubit}]")
    return qubit


def parse_qubits(args):
    return [parse_qubit(token) for token in args.split(",")]


def parse_program(source):
    operations = []
    oracle_calls = 0
    measured = []

    for raw_line in source.splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue
        if line in {
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            f"qreg q[{N_QUBITS}];",
            f"creg c[{N_BITS}];",
        }:
            continue

        match = LINE_RE.match(line)
        if not match:
            raise QisketError(f"unsupported instruction: {line!r}")

        op = match.group("op").lower()
        args = match.group("args")
        if op == "measure":
            measure_match = MEASURE_RE.match(args.strip())
            if not measure_match:
                raise QisketError(f"bad measurement: {line!r}")
            q = int(measure_match.group(1))
            c = int(measure_match.group(2))
            if not 0 <= q < N_BITS or not 0 <= c < N_BITS:
                raise QisketError(f"measure only the input register into c[0..{N_BITS - 1}]")
            measured.append((q, c))
            operations.append((op, q, c))
            continue

        qubits = parse_qubits(args)
        if op in {"h", "x", "z"}:
            if len(qubits) != 1:
                raise QisketError(f"{op} takes exactly one qubit")
        elif op == "oracle":
            if qubits != list(range(N_QUBITS)):
                raise QisketError(f"call oracle as: oracle q[0],...,q[{N_QUBITS - 1}];")
            oracle_calls += 1
            if oracle_calls > MAX_ORACLE_CALLS:
                raise QisketError("too many oracle calls")
        elif op == "mcx":
            if len(qubits) < 2:
                raise QisketError("mcx needs at least one control and one target")
            if len(set(qubits)) != len(qubits):
                raise QisketError("mcx qubits must be distinct")
        elif op == "diffuse":
            if qubits != list(range(N_BITS)):
                raise QisketError(f"call diffuse as: diffuse q[0],...,q[{N_BITS - 1}];")
        operations.append((op, *qubits))

    expected_measurements = {(q, q) for q in range(N_BITS)}
    if set(measured) != expected_measurements:
        raise QisketError("measure q[i] -> c[i] for every input qubit")

    return operations


def apply_x(state, qubit):
    bit = 1 << qubit
    view = state.reshape(-1, bit << 1)
    left = view[:, :bit].copy()
    view[:, :bit] = view[:, bit:]
    view[:, bit:] = left


def apply_z(state, qubit):
    bit = 1 << qubit
    state.reshape(-1, bit << 1)[:, bit:] *= -1


def apply_h(state, qubit):
    bit = 1 << qubit
    inv_sqrt2 = 1 / math.sqrt(2)
    view = state.reshape(-1, bit << 1)
    a = view[:, :bit].copy()
    b = view[:, bit:].copy()
    view[:, :bit] = (a + b) * inv_sqrt2
    view[:, bit:] = (a - b) * inv_sqrt2


def marked_input_value():
    return int(MARKED_BITS[::-1], 2)


def apply_oracle(state):
    marked = marked_input_value()
    control_mask = (1 << N_BITS) - 1
    target = 1 << ANCILLA
    for ancilla in (0, target):
        i = ancilla | marked
        j = i ^ target
        if i < j:
            state[i], state[j] = state[j], state[i]


def apply_mcx(state, controls, target):
    key = (tuple(controls), target)
    if key in MCX_PAIRS:
        left, right = MCX_PAIRS[key]
    else:
        target_bit = 1 << target
        control_mask = sum(1 << q for q in controls)
        if control_mask & target_bit:
            raise QisketError("mcx target cannot also be a control")

        floating = [
            qubit
            for qubit in range(N_QUBITS)
            if qubit != target and not ((control_mask >> qubit) & 1)
        ]
        left_indices = []
        for value in range(1 << len(floating)):
            index = control_mask
            for offset, qubit in enumerate(floating):
                if (value >> offset) & 1:
                    index |= 1 << qubit
            left_indices.append(index)
        left = np.array(left_indices, dtype=np.int64)
        right = left | target_bit
        MCX_PAIRS[key] = (left, right)

    if np.intersect1d(left, right).size:
        raise QisketError("mcx target cannot also be a control")
    tmp = state[left].copy()
    state[left] = state[right]
    state[right] = tmp


def apply_diffuse(state):
    block = 1 << N_BITS
    for ancilla_base in (0, block):
        view = state[ancilla_base : ancilla_base + block]
        mean = np.mean(view)
        view[:] = (2 * mean) - view


def simulate(operations):
    state = np.zeros(1 << N_QUBITS, dtype=np.complex128)
    state[0] = 1

    for operation in operations:
        op = operation[0]
        if op == "x":
            apply_x(state, operation[1])
        elif op == "z":
            apply_z(state, operation[1])
        elif op == "h":
            apply_h(state, operation[1])
        elif op == "oracle":
            apply_oracle(state)
        elif op == "mcx":
            apply_mcx(state, operation[1:-1], operation[-1])
        elif op == "diffuse":
            apply_diffuse(state)
        elif op == "measure":
            pass
        else:
            raise QisketError(f"unsupported op {op!r}")

    probabilities = np.zeros(1 << N_BITS)
    control_mask = (1 << N_BITS) - 1
    for index, amplitude in enumerate(state):
        probabilities[index & control_mask] += abs(amplitude) ** 2

    total = probabilities.sum()
    if not np.isclose(total, 1.0, atol=1e-6):
        raise QisketError("state did not remain normalized")
    probabilities /= total
    return probabilities


def sample_counts(probabilities):
    samples = np.random.default_rng(secrets.randbits(64)).choice(
        probabilities.size,
        size=SHOTS,
        p=probabilities,
    )
    counts = Counter(format(sample, f"0{N_BITS}b")[::-1] for sample in samples)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:12])


def banner():
    print("qisket oracle service")
    print(f"input qubits: q[0]..q[{N_BITS - 1}], ancilla: q[{ANCILLA}]")
    print(f"max oracle calls: {MAX_ORACLE_CALLS}, shots: {SHOTS}")
    print("send an OpenQASM-like program, then a line containing only END")
    print("supported: h, x, z, mcx, oracle, diffuse, measure")
    print(f"oracle call: oracle {','.join(f'q[{i}]' for i in range(N_QUBITS))};")
    print(f"diffuser helper: diffuse {','.join(f'q[{i}]' for i in range(N_BITS))};")
    print("measure every input qubit as q[i] -> c[i]")
    print()
    sys.stdout.flush()


def read_program():
    chunks = []
    total = 0
    for line in sys.stdin:
        if line.strip() == "END":
            break
        total += len(line.encode())
        if total > MAX_BYTES:
            raise QisketError("program too large")
        chunks.append(line)
    return "".join(chunks)


def main():
    try:
        check_secret()
        banner()
        program = read_program()
        operations = parse_program(program)
        probabilities = simulate(operations)
        counts = sample_counts(probabilities)
        print("counts:")
        for bitstring, count in counts.items():
            print(f"{bitstring}: {count}")

        target_probability = probabilities[marked_input_value()]
        if target_probability >= SUCCESS_PROBABILITY:
            print(FLAG)
        else:
            print("no flag for that distribution")
    except QisketError as exc:
        print(f"error: {exc}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
CHALLENGE = ROOT / "challenge.py"
N_BITS = 16
ANCILLA = N_BITS


def qargs(start, stop):
    return ",".join(f"q[{i}]" for i in range(start, stop))


def grover_program():
    iterations = round((math.pi / 4) * math.sqrt(1 << N_BITS))
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{N_BITS + 1}];",
        f"creg c[{N_BITS}];",
        f"x q[{ANCILLA}];",
    ]

    for i in range(N_BITS + 1):
        lines.append(f"h q[{i}];")

    oracle_args = qargs(0, N_BITS + 1)
    diffuse_args = qargs(0, N_BITS)
    for _ in range(iterations):
        lines.append(f"oracle {oracle_args};")
        lines.append(f"diffuse {diffuse_args};")

    for i in range(N_BITS):
        lines.append(f"measure q[{i}] -> c[{i}];")

    lines.append("END")
    return "\n".join(lines) + "\n"


def main():
    program = grover_program()
    proc = subprocess.run(
        [sys.executable, str(CHALLENGE)],
        cwd=ROOT,
        input=program,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()

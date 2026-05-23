#!/usr/bin/env python3
"""
Generate challenge_data.h for crt-rev-2.

Usage:
  python3 gen_data.py "UMDCTF{example_flag}" > challenge_data.h
"""

from __future__ import annotations

import random
import sys

MASK32 = 0xFFFFFFFF


def rotl32(x: int, r: int) -> int:
    r &= 31
    return ((x << r) | (x >> (32 - r))) & MASK32


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def crt_u32(r1: int, m1: int, r2: int, m2: int) -> int:
    m = m1 * m2
    m1_big = m // m1
    m2_big = m // m2
    inv1 = pow(m1_big % m1, -1, m1)
    inv2 = pow(m2_big % m2, -1, m2)
    x = (r1 * m1_big * inv1 + r2 * m2_big * inv2) % m
    return x & MASK32


def vm_mask(k: int, s: int, idx: int) -> int:
    r0 = k & MASK32
    r1 = s & MASK32
    r2 = idx & MASK32
    r3 = rotl32((r0 ^ ((r1 + 0x6C8E9CF5) & MASK32)) & MASK32, r2 & 31)
    r3 = (r3 * 0x7FEB352D + 0x846CA68B) & MASK32
    r4 = ((r1 ^ rotl32(r0, 7)) + (r2 * 0x9E3779B9)) & MASK32
    r4 ^= (r4 >> 16)
    r4 = (r4 * 0x85EBCA6B) & MASK32
    r5 = (rotl32(r4 ^ r3, 11) + 0xC2B2AE35) & MASK32
    r6 = (r5 ^ (r5 >> 13)) & MASK32
    r6 = (r6 * 0x27D4EB2F) & MASK32
    r7 = (r6 ^ rotl32(r3, 3) ^ 0xA5A5A5A5) & MASK32
    return r7


def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not is_prime(n):
        n += 2
    return n


def choose_moduli(rng: random.Random, chunks: int):
    m1 = []
    m2 = []
    base1 = 70001 + rng.randrange(0, 4000, 2)
    base2 = 76001 + rng.randrange(0, 4000, 2)
    for i in range(chunks):
        a = next_prime(base1 + i * 18 + 1)
        b = next_prime(base2 + i * 22 + 1)
        while a == b or a * b <= 0xFFFFFFFF:
            b = next_prime(b + 2)
        m1.append(a)
        m2.append(b)
    return m1, m2


def to_chunks(data: bytes):
    out = []
    for i in range(0, len(data), 4):
        out.append(int.from_bytes(data[i : i + 4].ljust(4, b"\0"), "little"))
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 1

    flag = sys.argv[1].encode()
    chunks = to_chunks(flag)
    chunk_count = len(chunks)

    rng = random.Random(0xC0DEC0DE)
    seed = rng.getrandbits(32)
    m1, m2 = choose_moduli(rng, chunk_count)

    k = [rng.getrandbits(32) for _ in range(chunk_count)]
    r1 = [k[i] % m1[i] for i in range(chunk_count)]
    r2 = [k[i] % m2[i] for i in range(chunk_count)]

    s = seed
    enc = []
    r1_obf = []
    r2_obf = []
    for i, x in enumerate(chunks):
        fold1 = rotl32(seed ^ ((i * 0x45D9F3B) & MASK32), (i % 13) + 3)
        fold2 = rotl32((seed + 0x9E3779B9) & MASK32 ^ ((i * 0x7F4A7C15) & MASK32), (i % 11) + 5)
        r1_obf.append(r1[i] ^ (fold1 % m1[i]))
        r2_obf.append(r2[i] ^ (fold2 % m2[i]))

        k_i = crt_u32(r1[i], m1[i], r2[i], m2[i])
        mask = vm_mask(k_i, s, i)
        enc.append(x ^ mask)
        s = (rotl32((s ^ x ^ ((k_i * 0x45D9F3B) & MASK32)) & MASK32, (i % 5) + 7) + 0x9E3779B9 + ((i * 0x7F4A7C15) & MASK32)) & MASK32

    final_check = s ^ 0xA5A5A5A5

    def arr(name: str, vals: list[int], suffix: str) -> str:
        items = ", ".join(f"0x{v:08X}{suffix}" for v in vals)
        return f"static const uint32_t {name}[CHUNK_COUNT] = {{ {items} }};"

    print("#ifndef CRT_REV_2_CHALLENGE_DATA_H")
    print("#define CRT_REV_2_CHALLENGE_DATA_H")
    print()
    print(f"#define FLAG_LEN {len(flag)}u")
    print(f"#define CHUNK_COUNT {chunk_count}u")
    print(f"static const uint32_t SEED = 0x{seed:08X}u;")
    print(arr("M1", m1, "u"))
    print(arr("M2", m2, "u"))
    print(arr("R1_OBF", r1_obf, "u"))
    print(arr("R2_OBF", r2_obf, "u"))
    print(arr("ENC", enc, "u"))
    print(f"static const uint32_t FINAL_CHECK = 0x{final_check:08X}u;")
    print()
    print("#endif")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

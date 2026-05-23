#!/usr/bin/env python3
import argparse
import os
import re
import struct
import sys
from pathlib import Path


MOD = 257
CAL_LEN = 256
CRYPTO_SEED_BITS = 24
QUOTE_SEED = 0x9A7E_B00C
CRYPTO_MAGIC = b"CBELL-ELF-V2\x00"
PLAINTEXT_PRELUDE = b"CBELL24/ELF2\n"

VENUES = [
    "AMM", "CLOB", "DARK", "RFQ", "YESX", "NOX", "EDGE",
    "BASIS", "TWAP", "VWAP", "POOL", "OTC", "MOC",
]

LINE_RE = re.compile(
    r"LOT=([0-9A-F]{4}).*?VENUE=([A-Z]+).*?"
    r"YES=(\d{2})\.(\d{3}).*?DEPTH=(\d{4}).*?"
    r"SPREAD=(\d{2}).*?IMB=([+-]\d{3})"
)


def u32(x: int) -> int:
    return x & 0xFFFFFFFF


def rol32(x: int, r: int) -> int:
    r &= 31
    return u32((x << r) | (x >> (32 - r)))


def stream_bytes(seed: int):
    s = u32(seed ^ 0x6A09E667)
    ctr = 0
    while True:
        s = u32(s + 0x9E3779B9 + ctr * 0x45D9F3B)
        s ^= s >> 15
        s = u32(s * 0x85EBCA6B)
        s ^= s >> 13
        s = u32(s * 0xC2B2AE35)
        s ^= s >> 16
        z = u32(rol32(s ^ (ctr * 0x27D4EB2D), (ctr & 7) + 5) + 0xA5A5A5A5)
        for shift in (3, 11, 19, 27):
            yield (z >> shift) & 0xFF
        ctr += 1


def decrypt_with_seed(data: bytes, seed: int, n: int | None = None) -> bytes:
    ks = stream_bytes(seed)
    src = data if n is None else data[:n]
    return bytes(b ^ next(ks) for b in src)


def checksum32(data: bytes) -> int:
    h = 0x811C9DC5
    for b in data:
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def decrypt_payload(data: bytes, start: int = 0, stop: int = 1 << CRYPTO_SEED_BITS) -> tuple[int, bytes]:
    if not data.startswith(PLAINTEXT_PRELUDE):
        raise ValueError("missing plaintext wrapper prelude")
    data = data[len(PLAINTEXT_PRELUDE):]
    header_len = len(CRYPTO_MAGIC) + 8
    for seed in range(start, stop):
        header = decrypt_with_seed(data, seed, header_len)
        if not header.startswith(CRYPTO_MAGIC):
            continue
        size, want = struct.unpack("<II", header[len(CRYPTO_MAGIC):header_len])
        if size <= 0 or size > len(data) - header_len:
            continue
        plain = decrypt_with_seed(data, seed, header_len + size)
        artifact = plain[header_len:header_len + size]
        if artifact.startswith(b"\x7fELF") and checksum32(artifact) == want:
            return seed, artifact
    raise ValueError("crypto seed not found")


def calibration_byte(i: int) -> int:
    return (i * 73 + 41) & 0xFF


def tiny_noise(i: int, venue: int, field: int) -> int:
    x = u32(QUOTE_SEED ^ (i * 0x45D9F3B) ^ (venue * 0x9E3779B9) ^ (field * 0x27D4EB2D))
    x ^= x >> 16
    x = u32(x * 0x7FEB352D)
    return [-2, -1, 0, 0, 0, 1, 2][x % 7]


def circ_dist(a: int, b: int, mod: int) -> int:
    d = abs(a - b) % mod
    return min(d, mod - d)


def lot_for(i: int) -> str:
    return f"{((i * 73) ^ 0x5151) & 0xFFFF:04X}"


def parse(text: str) -> dict[int, list[tuple[int, tuple[int, int, int, int]]]]:
    raw: dict[str, list[tuple[int, tuple[int, int, int, int]]]] = {}
    groups: dict[int, list[tuple[int, tuple[int, int, int, int]]]] = {}
    venue_idx = {name: i for i, name in enumerate(VENUES)}
    for line in text.splitlines():
        m = LINE_RE.search(line)
        if not m:
            continue
        lot_s, venue_s, yes_w, yes_f, depth_s, spread_s, imb_s = m.groups()
        if venue_s not in venue_idx:
            continue
        yes = int(yes_w) * 1000 + int(yes_f)
        fields = (yes, int(depth_s), int(spread_s), int(imb_s))
        raw.setdefault(lot_s, []).append((venue_idx[venue_s], fields))

    for i in range(1 << 20):
        rows = raw.get(lot_for(i))
        if rows:
            # decoys can collide with real lots. Keep all rows here; later
            # scoring will reject inconsistent duplicates.
            groups[i] = rows
        else:
            if i > CAL_LEN:
                break
    return groups


def predicted_fields(y: int, i: int, venue: int) -> tuple[int, int, int, int]:
    drift = (i * 17 + venue * 29 + QUOTE_SEED) % 1000
    yes = 17000 + ((37 * y + drift) % 10000) + tiny_noise(i, venue, 0)
    depth = 1000 + ((83 * y + 19 * i + 41 * venue + QUOTE_SEED) % 9000) + tiny_noise(i, venue, 1)
    spread = 3 + ((5 * y + 7 * i + 3 * venue + QUOTE_SEED) % 95) + tiny_noise(i, venue, 2)
    imb = ((7 * y + 11 * i + 13 * venue + QUOTE_SEED) % 401) - 200 + tiny_noise(i, venue, 3)
    return yes, depth, spread, imb


def residue_from_yes(yes: int, i: int, venue: int) -> int:
    drift = (i * 17 + venue * 29 + QUOTE_SEED) % 1000
    inv = pow(37, -1, 10000)
    best = None
    for eps in range(-14, 15):
        shown = (yes - 17000 - tiny_noise(i, venue, 0) - eps - drift) % 10000
        y = (shown * inv) % 10000
        if y < MOD:
            pred = 17000 + ((37 * y + drift) % 10000) + tiny_noise(i, venue, 0)
            score = circ_dist(pred, yes, 10000)
            if best is None or score < best[0]:
                best = (score, y)
    if best is None:
        raise ValueError("bad ticker residue")
    return best[1]


def field_score(pred: tuple[int, int, int, int], got: tuple[int, int, int, int]) -> int:
    yes_p, depth_p, spread_p, imb_p = pred
    yes_g, depth_g, spread_g, imb_g = got
    return (
        circ_dist(yes_p, yes_g, 10000)
        + circ_dist(depth_p, depth_g, 9000)
        + 12 * circ_dist(spread_p, spread_g, 97)
        + 3 * circ_dist(imb_p + 200, imb_g + 200, 401)
    )


def fit_channels(groups: dict[int, list[tuple[int, tuple[int, int, int, int]]]]) -> list[tuple[int, int]]:
    by_venue: list[list[tuple[int, int, tuple[int, int, int, int]]]] = [[] for _ in VENUES]
    for i in range(CAL_LEN):
        for venue, fields in groups.get(i, []):
            by_venue[venue].append((i, calibration_byte(i), fields))

    channels: list[tuple[int, int]] = []
    for venue, samples in enumerate(by_venue):
        if len(samples) < 40:
            raise ValueError(f"not enough calibration samples for {VENUES[venue]}")
        residues = []
        for i, x, fields in samples:
            try:
                residues.append((x, residue_from_yes(fields[0], i, venue)))
            except ValueError:
                continue
        best = None
        subset = residues[:48]
        for a in range(1, MOD):
            for b in range(MOD):
                # Trim a few outliers caused by decoy LOT collisions.
                ds = sorted(circ_dist((a * x + b) % MOD, y, MOD) for x, y in subset)
                score = sum(ds[: max(12, len(ds) - 4)])
                if best is None or score < best[0]:
                    best = (score, a, b)
        assert best is not None
        channels.append((best[1], best[2]))
    return channels


def recover_payload(groups: dict[int, list[tuple[int, tuple[int, int, int, int]]]]) -> bytes:
    channels = fit_channels(groups)
    inv_channels = [(pow(a, -1, MOD), b) for a, b in channels]
    max_idx = max(groups)
    recovered = bytearray()
    for i in range(CAL_LEN, max_idx + 1):
        rows = groups.get(i, [])
        if len(rows) < 2:
            raise ValueError(f"too many dropped lines around IDX={i:04x}")
        votes: dict[int, int] = {}
        scored_votes: dict[int, int] = {}
        for venue, fields in rows:
            inv_a, b = inv_channels[venue]
            try:
                y = residue_from_yes(fields[0], i, venue)
            except ValueError:
                continue
            x = ((y - b) * inv_a) % MOD
            if x < 256:
                pred_y = (channels[venue][0] * x + channels[venue][1]) % MOD
                err = field_score(predicted_fields(pred_y, i, venue), fields)
                if err < 80:
                    votes[x] = votes.get(x, 0) + 1
                    scored_votes[x] = scored_votes.get(x, 0) + err
        if votes:
            winner, count = max(votes.items(), key=lambda kv: (kv[1], -scored_votes[kv[0]]))
            if count >= 2 or len(rows) <= 3:
                recovered.append(winner)
                continue

        best = None
        for x in range(256):
            score = 0
            for venue, fields in rows:
                a, b = channels[venue]
                y = (a * x + b) % MOD
                score += field_score(predicted_fields(y, i, venue), fields)
            if best is None or score < best[0]:
                best = (score, x)
        assert best is not None
        recovered.append(best[1])
    return bytes(recovered)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript", nargs="?", help="saved nc transcript; stdin if omitted")
    ap.add_argument("-o", "--output", default="recovered-closing-bell.bin")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--start", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--stop", type=lambda s: int(s, 0), default=1 << CRYPTO_SEED_BITS)
    args = ap.parse_args()

    text = Path(args.transcript).read_text("latin-1") if args.transcript else sys.stdin.read()
    groups = parse(text)
    data = recover_payload(groups)
    seed, data = decrypt_payload(data, args.start, args.stop)
    print(f"[+] crypto seed = 0x{seed:06x}", file=sys.stderr)

    if args.stdout:
        os.write(1, data)
    else:
        out = Path(args.output)
        out.write_bytes(data)
        out.chmod(0o755)
        print(f"wrote {out} ({len(data)} bytes)")


if __name__ == "__main__":
    main()

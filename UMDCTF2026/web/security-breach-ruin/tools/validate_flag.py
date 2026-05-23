"""
Build-time flag validator.

The challenge relies on a 1-sample BREACH oracle against the dashboard response.
For this to produce a clean solver experience, the chosen flag must be one
whose byte pattern doesn't create LZ77/Huffman ties. This script runs the full
attack against a candidate flag locally (no server needed) and reports whether
it solves cleanly.

Usage:
    python tools/validate_flag.py 'UMDCTF{your_candidate_flag_here}'
    # or
    FLAG='UMDCTF{...}' python tools/validate_flag.py

Run this before committing the final FLAG env var into the Dockerfile / compose.
"""
import gzip
import sys
import os

FLAG_PREFIX = "UMDCTF{"
FLAG_SUFFIX = "}"
FLAG_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789_"
PROBE_ALPHABET = FLAG_ALPHABET + FLAG_SUFFIX

# Must match src/server.py DASHBOARD_TEMPLATE.
DASHBOARD_TEMPLATE = '{{"filter":"{filter}","flag":"{flag}"}}'


def gz(body: str) -> int:
    return len(gzip.compress(body.encode(), compresslevel=6, mtime=0))


def validate(flag: str) -> tuple[bool, list[str]]:
    errors = []
    if not (flag.startswith(FLAG_PREFIX) and flag.endswith(FLAG_SUFFIX)):
        errors.append(f"flag must be {FLAG_PREFIX}...{FLAG_SUFFIX}")
        return False, errors
    body = flag[len(FLAG_PREFIX):-len(FLAG_SUFFIX)]
    bad = sorted(set(c for c in body if c not in FLAG_ALPHABET))
    if bad:
        errors.append(f"out-of-alphabet chars: {bad} (allowed: {FLAG_ALPHABET!r})")
        return False, errors

    tail = flag[len(FLAG_PREFIX):]  # e.g. "body_of_flag}"
    for pl in range(len(tail)):
        extracted = tail[:pl]
        correct = tail[pl]
        scores = {}
        for ch in PROBE_ALPHABET:
            probe = FLAG_PREFIX + extracted + ch
            scores[ch] = gz(DASHBOARD_TEMPLATE.format(filter=probe, flag=flag))
        min_v = min(scores.values())
        winners = [c for c, v in scores.items() if v == min_v]
        if winners != [correct]:
            errors.append(
                f"position {pl} (expected {correct!r}): min={min_v} winners={winners}"
            )
    return not errors, errors


def main():
    flag = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FLAG")
    if not flag:
        print("usage: validate_flag.py <flag>  or  FLAG=<flag> validate_flag.py", file=sys.stderr)
        sys.exit(2)
    ok, errors = validate(flag)
    if ok:
        print(f"OK: {flag!r} is 1-sample BREACH-solvable")
        sys.exit(0)
    print(f"FAIL: {flag!r}")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)


if __name__ == "__main__":
    main()

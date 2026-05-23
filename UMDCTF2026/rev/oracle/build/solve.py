#!/usr/bin/env python3
"""Reference solver.

Pipeline:
    feed.bin  →  2× AES decrypt  →  archive-body MWC undo  →  custom TLV
    pull `b` (BC3B class) → MWC-decrypt body → read const pool
    → RK[16] (round keys), TARGET[8], SALT
    invert the 8-round register permutation starting from TARGET
    → recover the unique 32-byte ticket
    flag_km = hash_x(ticket || SALT) → AES-CBC decrypt `g` → flag.

Emits dist/ticket.txt so the oracle binary reproduces the same result.
"""
import os, sys, struct, base64, random
from Crypto.Cipher import AES

sys.path.insert(0, os.path.dirname(__file__))
from hashx import hash_x
from gen_validate import inverse, ODD_MUL, ODD_MUL_INV, SALT, N_REGS, N_ROUNDS

KEY_TABLE_SIZE = 32
BLOB_BLOCK_SIZE = 64

# Shares the build seed; a real solver would dump the XOR-masked table
# out of the oracle binary's .rodata instead.
rng = random.Random(0xBADCAFE)
key_table = [bytes(rng.getrandbits(8) for _ in range(16)) for _ in range(KEY_TABLE_SIZE)]

def decrypt_layer(blob: bytes) -> bytes:
    hdr, body = blob[:BLOB_BLOCK_SIZE], blob[BLOB_BLOCK_SIZE:]
    out = bytearray(len(body))
    off = 0
    idx = 0
    while off < len(body):
        chunk = body[off:off + BLOB_BLOCK_SIZE]
        i1 = hdr[(idx + 11) & 63] % KEY_TABLE_SIZE
        i2 = hdr[(idx + 17) & 63] % KEY_TABLE_SIZE
        i3 = hdr[idx & 63]        % KEY_TABLE_SIZE
        dk = AES.new(key_table[i3], AES.MODE_ECB).decrypt(key_table[i1])
        pt = AES.new(dk, AES.MODE_CBC, key_table[i2]).decrypt(chunk)
        out[off:off + len(chunk)] = pt
        off += len(chunk)
        idx += 1
    return bytes(out)

def mwc_decrypt(buf: bytearray, seed: int):
    s1 = (0x7FFF7FFF - seed) & 0xFFFFFFFF
    s2 = seed & 0xFFFFFFFF
    for i in range(len(buf)):
        s1 = (((s1 & 0xFFFF) * 36969) + (s1 >> 16)) & 0xFFFFFFFF
        s2 = ((s2 >> 16) + (s2 & 0xFFFF) * 18000) & 0xFFFFFFFF
        buf[i] ^= (s2 & 0xFF)

def parse_archive(buf: bytes) -> dict[str, bytes]:
    assert buf[:4] == b'ARC\x01', f'not our archive: magic = {buf[:4]!r}'
    seed = int.from_bytes(buf[4:8], 'little')
    body = bytearray(buf[8:])
    mwc_decrypt(body, seed)
    pos = 0
    n = body[pos]; pos += 1
    out = {}
    for _ in range(n):
        name_len = body[pos]; pos += 1
        name = bytes(body[pos:pos + name_len]).decode(); pos += name_len
        data_len = int.from_bytes(bytes(body[pos:pos+4]), 'little'); pos += 4
        out[name] = bytes(body[pos:pos + data_len]); pos += data_len
    return out

def parse_class(vmc: bytes) -> dict:
    assert len(vmc) >= 10
    magic = vmc[:4]
    body = bytearray(vmc[4:])
    if magic[:2] == b'\xca\xfe':
        pass
    elif magic[:2] == b'\xbc\x3b':
        magic_xor = int.from_bytes(magic, 'little') ^ 0xBEBAFECA
        mwc_decrypt(body, magic_xor)
    else:
        raise ValueError(f'unknown class magic: {magic.hex()}')
    const_count = int.from_bytes(body[0:2], 'little')
    code_len    = int.from_bytes(body[2:6], 'little')
    pos = 6
    consts = []
    for _ in range(const_count):
        cl = int.from_bytes(body[pos:pos+2], 'little'); pos += 2
        consts.append(bytes(body[pos:pos+cl])); pos += cl
    code = bytes(body[pos:pos+code_len])
    return {'consts': consts, 'code': code}

feed = open('dist/feed.bin', 'rb').read()
arc = parse_archive(decrypt_layer(decrypt_layer(feed)))
validate_cls = parse_class(arc['b'])
flag_ct = arc['g']

RK_bytes     = validate_cls['consts'][0]
TARGET_bytes = validate_cls['consts'][1]
salt_bytes   = validate_cls['consts'][2]
assert len(RK_bytes) == 64 and len(TARGET_bytes) == 32
RK     = list(struct.unpack('<16I', RK_bytes))
TARGET = list(struct.unpack('<8I',  TARGET_bytes))
print(f'[*] RK (first 4 u32s): {RK[:4]}')
print(f'[*] TARGET:            {[hex(x) for x in TARGET]}')
print(f'[*] SALT:              {salt_bytes!r}')

TICKET = inverse(TARGET, RK)
print(f'[*] recovered ticket = {TICKET.hex()}')

from gen_validate import forward
regs_check = forward(TICKET, RK)
assert regs_check == TARGET, f'inverse check failed: {regs_check} != {TARGET}'

fkm = hash_x(TICKET + salt_bytes)
pt = AES.new(fkm[:16], AES.MODE_CBC, fkm[16:32]).decrypt(flag_ct)
pad = pt[-1]
if 1 <= pad <= 16 and all(b == pad for b in pt[-pad:]):
    print(f'[*] flag (locally decrypted): {pt[:-pad].decode()}')

tlv = b'TKT\x01'
tlv += struct.pack('<I', len(TICKET))
tlv += TICKET
b64 = base64.b64encode(tlv).decode()
pem = '-----BEGIN MARKET TICKET-----\n'
for i in range(0, len(b64), 64):
    pem += b64[i:i+64] + '\n'
pem += '-----END MARKET TICKET-----\n'
with open('dist/ticket.txt', 'w') as f:
    f.write(pem)
print(f'[*] wrote dist/ticket.txt ({len(pem)} bytes)')
print('[*] now run:  cd dist && ./oracle')

#!/usr/bin/env python3
"""Post-link: hash the `chk` section, pre-XOR it into KXK_M so main()'s
runtime XOR reassembles the real TEA key only if chk is unmodified, then
TEA-CFB-encrypt the .xtext section in place."""
import sys, struct, os
from elftools.elf.elffile import ELFFile

# Must stay in sync with src/main.c
REAL_TEA_KEY = (0x1a2b3c4d, 0x5e6f7081, 0x92a3b4c5, 0xd6e7f809)
KXK_MASK     = (0x12345678, 0x9abcdef0, 0xfedcba98, 0x87654321)
KXV          = bytes([0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77])
PLACEHOLDER  = struct.pack('<IIII', 0xAA550001, 0xAA550002, 0xAA550003, 0xAA550004)

TEA_DELTA = 0x9e3779b9
MASK = 0xffffffff

def fnv_like(buf: bytes) -> int:
    h = 0xC0DEF1AB
    for b in buf:
        h = (h ^ b) & MASK
        h = (h * 0x5BD1E995) & MASK
        h ^= (h >> 15)
        h &= MASK
    return h

def tea_encrypt_block(k, v0, v1, rounds=32):
    s = 0
    for _ in range(rounds):
        s = (s + TEA_DELTA) & MASK
        v0 = (v0 + (((v1 << 4) & MASK) + k[0] ^ (v1 + s) & MASK ^ ((v1 >> 5) + k[1]))) & MASK
        v1 = (v1 + (((v0 << 4) & MASK) + k[2] ^ (v0 + s) & MASK ^ ((v0 >> 5) + k[3]))) & MASK
    return v0, v1

def tea_cfb_encrypt(key, iv, pt):
    out = bytearray(len(pt))
    fb0, fb1 = struct.unpack('<II', iv)
    pos = 0
    while pos + 8 <= len(pt):
        ks0, ks1 = tea_encrypt_block(key, fb0, fb1)
        ks = struct.pack('<II', ks0, ks1)
        ct = bytes(a ^ b for a, b in zip(pt[pos:pos+8], ks))
        out[pos:pos+8] = ct
        fb0, fb1 = struct.unpack('<II', ct)
        pos += 8
    if pos < len(pt):
        ks0, ks1 = tea_encrypt_block(key, fb0, fb1)
        ks = struct.pack('<II', ks0, ks1)
        tail = bytes(a ^ b for a, b in zip(pt[pos:], ks[:len(pt)-pos]))
        out[pos:len(pt)] = tail
    return bytes(out)

def main():
    path = sys.argv[1]
    with open(path, 'rb') as f:
        data = bytearray(f.read())

    with open(path, 'rb') as f:
        elf = ELFFile(f)
        xtext = elf.get_section_by_name('.xtext')
        chk   = elf.get_section_by_name('chk')
        if xtext is None:
            print('ERROR: no .xtext section', file=sys.stderr); sys.exit(1)
        if chk is None:
            print('ERROR: no chk section',    file=sys.stderr); sys.exit(1)
        x_off, x_sz = xtext['sh_offset'], xtext['sh_size']
        c_off, c_sz = chk  ['sh_offset'], chk  ['sh_size']

    chk_bytes = bytes(data[c_off:c_off + c_sz])
    h = fnv_like(chk_bytes)
    print(f'chk @ 0x{c_off:x}+0x{c_sz:x}, hash=0x{h:08x}')

    # Patch KXK_M placeholder so runtime XOR assembles REAL_TEA_KEY
    idx = data.find(PLACEHOLDER)
    if idx < 0:
        print('ERROR: KXK_M placeholder not found', file=sys.stderr); sys.exit(2)
    patched = bytes()
    for i in range(4):
        patched += struct.pack('<I', (REAL_TEA_KEY[i] ^ KXK_MASK[i] ^ h) & 0xFFFFFFFF)
    data[idx:idx + 16] = patched
    print(f'patched KXK_M at 0x{idx:x}')

    # Encrypt .xtext using the real key
    ct = tea_cfb_encrypt(REAL_TEA_KEY, KXV, bytes(data[x_off:x_off + x_sz]))
    data[x_off:x_off + x_sz] = ct
    print(f'encrypted {x_sz} bytes of .xtext at 0x{x_off:x}')

    with open(path, 'wb') as f:
        f.write(bytes(data))

if __name__ == '__main__':
    main()

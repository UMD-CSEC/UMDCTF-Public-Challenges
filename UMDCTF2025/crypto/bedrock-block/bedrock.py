#!/usr/local/bin/python
from Crypto.Util.number import bytes_to_long
from Crypto.Util.Padding import pad
import os

def rot(n, r):
    return (n >> r) | ((n << (256 - r) & (2**256 - 1)))

round_constants1 = [3, 141, 59, 26, 53,  58]
round_constants2 = [2, 7,   18, 28, 182, 8 ]

M = 2**256

def encrypt(key, block):
    for i in range(6):
        block = (block + key) & (M-1)
        block = block ^ rot(block, round_constants1[i]) ^ rot(block, round_constants2[i])
    return block

key = bytes_to_long(os.urandom(32)) 

for _ in range(2**14):
    i = input("Plaintext (hex): ")
    if i[0] == 'q':
        break
    pt = bytes.fromhex(i)
    pt = pad(pt, block_size=32)
    blocks = [pt[i:i+32] for i in range(0, len(pt), 32)]
    if len(blocks) > 300:
        break

    ct = [hex(encrypt(key, bytes_to_long(b)))[2:].zfill(64) for b in blocks]
    print("Ciphertext: " + ''.join(ct))


flag = open("./flag.txt", 'rb').read()
assert len(flag) <= 32

print("Flag: ", hex(encrypt(key, bytes_to_long(flag)))[2:].zfill(64))


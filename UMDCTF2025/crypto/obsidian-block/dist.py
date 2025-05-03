from Crypto.Util.number import bytes_to_long
import os

def rot(n, r):
    return (n >> r) | ((n << (256 - r) & (2**256 - 1)))

round_constants = [3, 141, 59, 26, 53, 58, 97, 93, 23, 84, 62, 64, 33, 83, 27, 9, 50, 28, 84, 197, 169, 39, 93, 75]

M = 2**256

def encrypt(key, block):
    for i in range(24):
        block = (block + key) % M
        block = rot(block, round_constants[i])
    return block

key = os.urandom(32)
key = bytes_to_long(key)

p1 = b'please like and subscribe!!!!!!!'
p2 = b'UMDCTF{REDACTED}'
assert(len(p1) <= 32)
assert(len(p2) <= 32)

c1 = encrypt(key, bytes_to_long(p1))
c2 = encrypt(key, bytes_to_long(p2))

print(c1)
print(c2)

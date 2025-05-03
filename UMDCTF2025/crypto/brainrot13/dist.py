from Crypto.Util.number import bytes_to_long, getPrime
import codecs
import re

p = getPrime(512)
q = getPrime(512)
n = p * q
e = 3

flag = 'UMDCTF{redacted}'
assert re.fullmatch("UMDCTF\\{[a-z]+\\}", flag)
assert len(flag) == 28
rotflag = codecs.encode(flag, 'rot13')

def encrypt(b):
    while (len(b) < 120):
        # Optimal Asymmetric Encryption Padding
        b += b'OAEP'
    pt = bytes_to_long(b)
    return pow(pt, e, n)

print(f"n = {n}")
print(f"ct1 = {encrypt(flag.encode())}")
print(f"ct2 = {encrypt(rotflag.encode())}")

from Crypto.Util.number import bytes_to_long, long_to_bytes
import os
from tqdm import tqdm
import itertools

c1 = 19970192951896076587357270489167937916618022198129516743091736664525698125224
c2 = 78876026922201259108741049564691635166471597880603787944801336451046144103203

N = 24


def rotr(n, r):
    return (n >> r) | ((n << (256 - r) & (2**256 - 1)))

def rotl(n, r):
    return rotr(n, (256 - r))

round_constants = [3, 141, 59, 26, 53, 58, 97, 93, 23, 84, 62, 64, 33, 83, 27, 9, 50, 28, 84, 197, 169, 39, 93, 75]
M = 2**256

def encrypt(key, block):
    for i in range(N):
        block = (block + key) % M
        block = rotr(block, round_constants[i])
    return block

def decrypt(key, block):
    for i in range(N):
        block = rotl(block, round_constants[N-i-1])
        block = (block - key) % M
    return block

#R.<k> = PolynomialRing(Zmod(2**256 - 1))
p1 = bytes_to_long(b'please like and subscribe!!!!!!!')


rs = [2**(256 - i) for i in round_constants]
r_coefficients = [product(rs[i:]) % (2**256 - 1) for i in range(N)]
k_coefficient = sum(r_coefficients) % (2**256 - 1)
common_factor = gcd(k_coefficient, M-1)

print(common_factor)

k_coefficient_inv = Zmod((M-1) // common_factor)(k_coefficient // common_factor)^(-1)
starting_c = (-r_coefficients[0] * p1 + c1) % (M-1) 

for r in tqdm(itertools.product((0,1), repeat=N), total=int(2**N)):
    c = starting_c
    for i in range(N):
        c += r_coefficients[i] * r[i]
    if c % common_factor != 0:
        continue
    k = k_coefficient_inv * (c // common_factor)
    ks = [ZZ(k) + i*((M-1)//common_factor) for i in range(common_factor)]
    for x in ks:
        key = ZZ(x)
        if c1 == encrypt(key, p1):
            print(r)
            print(long_to_bytes(decrypt(key, c2)))
            print(key)

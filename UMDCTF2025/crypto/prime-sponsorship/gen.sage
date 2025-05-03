import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sage.arith.misc import crt

p1 = 211
p2 = 223
q = 1511

# strip UMDCTF{}\n
flag = open('flag.txt', 'rb').read()[7:-2]

def encode(msg):
    m = bin(bytes_to_long(msg))[2:].zfill(p1)
    return [0 if c == '0' else 1 for c in m]


Fq = GF(q)
F3 = GF(3)
Rq = PolynomialRing(Fq, 'x').quotient(x^p1 - x - 1)
R3 = PolynomialRing(F3, 'x').quotient(x^p1 - x - 1)

Rq_2 = PolynomialRing(Fq, 'x').quotient(x^p2 - x - 1)
R3_2 = PolynomialRing(F3, 'x').quotient(x^p2 - x - 1)

Rx.<x> = PolynomialRing(ZZ, 'x')
Qx = PolynomialRing(QQ, 'x')

# keygen
h1, h2 = None, None
g_inv, f = None, None
while True:
    g = Rx([random.choice([-1,0,1]) for _ in range(p1)])
    g3 = R3(g)
    g3_2 = R3_2(g)
    if g3.is_unit() and g3_2.is_unit():
        g_inv = g3.inverse()
        f = Rx([random.choice([-1,0,1]) for _ in range(p1)])
        h1 = Rq(g) / Rq(3 * f)
        h2 = Rq_2(g) / Rq_2(3 * f)
        break

def round3(poly):
    new_poly = []
    for c in poly.list():
        c = ZZ(c)
        if c % 3 == 1:
            new_poly.append(c - 1)
        elif c % 3 == 0:
            new_poly.append(c)
        else:
            new_poly.append(c+1)
    return Rq(new_poly)


def encrypt(r):
    return round3(h1 * Rq(r))

def decrypt(ct, f, g_inv):
    e = Rq(3 * f) * ct
    e = [c.lift_centered() for c in e]
    print("e = ", e)
    return list(g_inv * R3(e))


print("With our new PRIME sponsorship, we bundled an extra public key for you*!")
print()

print("pk1 =", h1.list())
print("pk2 =", h2.list())

msg = encode(flag)
ct1 = encrypt(msg)

print("ct =", ct1.list())

print("*ciphertext not included")

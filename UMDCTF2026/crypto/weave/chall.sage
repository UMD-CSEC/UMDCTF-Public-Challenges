#!/usr/bin/env sage
import json, os
from hashlib import sha256
from Crypto.Cipher import AES

Q       = 2
M       = 43
N       = 40
K       = 8
FRAYS   = 5
FIBER_D = 3

R.<x> = PolynomialRing(GF(Q))
MODPOLY = x**43 + x**21 + x**3 + x + 1
assert MODPOLY.is_irreducible()

Fq      = GF(Q)
Fqm.<a> = GF(Q**M, modulus=MODPOLY)

set_random_seed(int.from_bytes(os.urandom(32), 'big'))

def qpow(e, j):
    return e ** (Q ** j)

def pick_independent(count):
    while True:
        vs = [Fqm.random_element() for _ in range(count)]
        rows = []
        for v in vs:
            cs = list(v.polynomial()) if v else []
            cs = [Fq(c) for c in cs] + [Fq(0)] * (M - len(cs))
            rows.append(cs)
        if Matrix(Fq, rows).rank() == count:
            return vs

def pick_invertible_Fqm(sz):
    while True:
        M_ = Matrix(Fqm, sz, sz, [Fqm.random_element() for _ in range(sz * sz)])
        if M_.is_invertible():
            return M_

def pick_shuttle(sz, fibers):
    while True:
        entries = []
        for _ in range(sz * sz):
            cs = [Fq.random_element() for _ in range(FIBER_D)]
            entries.append(sum(c * v for c, v in zip(cs, fibers)))
        M_ = Matrix(Fqm, sz, sz, entries)
        if M_.is_invertible():
            return M_

pegs    = pick_independent(N)
loom    = Matrix(Fqm, K, N, lambda j, i: qpow(pegs[i], j))
knot    = pick_invertible_Fqm(K)
fibers  = pick_independent(FIBER_D)
shuttle = pick_shuttle(N, fibers)
warp    = knot * loom * shuttle.inverse()

secret = vector(Fqm, [Fqm.random_element() for _ in range(K)])

def pack(v):
    out = []
    for e in v:
        cs = list(e.polynomial()) if e else []
        cs = [int(c) for c in cs] + [0] * (M - len(cs))
        val = 0
        for i, c in enumerate(cs):
            val |= c << i
        out.append(int(val))
    return out

def pack_mat(M_):
    return [pack(row) for row in M_.rows()]

secret_bytes = b''.join(int(v).to_bytes((M + 7) // 8, 'big') for v in pack(secret))
wrap_key = sha256(secret_bytes).digest()[:16]

try:
    flag = open('flag.txt', 'rb').read().strip()
except FileNotFoundError:
    flag = b'UMDCTF{test_flag}'

iv = os.urandom(12)
body, tag = AES.new(wrap_key, AES.MODE_GCM, nonce=iv).encrypt_and_digest(flag)

def pick_frays():
    while True:
        B = Matrix(Fq, FRAYS, N, [Fq.random_element() for _ in range(FRAYS * N)])
        if B.rank() == FRAYS:
            break
    u = vector(Fqm, [Fqm.random_element() for _ in range(FRAYS)])
    return u * B.change_ring(Fqm)

frays = pick_frays()
bolt  = secret * warp + frays

handout = {
    'spec': {
        'q': int(Q),
        'm': int(M),
        'n': int(N),
        'k': int(K),
        'frays': int(FRAYS),
        'modulus': [int(c) for c in MODPOLY.list()],
    },
    'warp': pack_mat(warp),
    'bolt': pack(bolt),
    'loom': {
        'pegs':    pack(vector(Fqm, pegs)),
        'knot':    pack_mat(knot),
        'shuttle': pack_mat(shuttle),
        'fibers':  pack(vector(Fqm, fibers)),
    },
    'vault': {
        'iv':   iv.hex(),
        'body': body.hex(),
        'tag':  tag.hex(),
    },
}

with open('output.json', 'w') as fh:
    json.dump(handout, fh)

print('Output.json is created!')

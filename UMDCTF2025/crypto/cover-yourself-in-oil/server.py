#!/usr/local/bin/python
import random
from public_key import pk

n = 48
v = 120

# compression factor
l = 6

def expand_column(vec):
    M = []
    for k in range(l):
        M.append([(x * 2**k) % 127 for x in vec])
    return M

def dot_product(a, b):
    return sum([x * y for x,y in zip(a,b)]) % 127

def mat_vec_product(M, v):
    return [dot_product(r, v) for r in M]



# rebuild public key matrices
Ps = []
for p in pk:
    MT = []
    for c in p:
        cs = expand_column(c)
        MT += cs

    M = [[None for _ in range(n+v)] for _ in range(n+v)]
    for i in range(n+v):
        for j in range(n+v):
            M[i][j] = MT[j][i]

    Ps.append(M)

target = [random.randint(0, 126) for _ in range(n)]

print(f"The message to sign is {target}")

sig = input("Input your signature in the form x1, x2, ..., x168\n")
sig = sig.strip().split(', ')
assert len(sig) == 168
sig = [int(s) for s in sig]


t = []
for P in Ps:
    t.append(dot_product(sig, mat_vec_product(P, sig)))

if t == target:
    print(open('flag.txt', 'r').read())
else:
    print("Nope!")

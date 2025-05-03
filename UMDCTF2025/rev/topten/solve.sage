import struct
from numpy import float32
from z3 import *


flag = []

# part 1

R.<x> = GF(2)[]

p1 = [144, 228, 20, 182, 26, 221, 1, 168, 123, 208, 186, 15, 205, 132, 14, 14]
p = sum(sum(x^(i*8 + j) for j in range(8) if p1[i] & (1 << j)) for i in range(len(p1)))

def poly_to_bytes(f, nbits=64):
	bits = f.list()
	bits += [0] * (nbits - len(bits))
	return bytes([sum(Integer(bits[i+j]) << j for j in range(8)) for i in range(0, nbits, 8)])

def is_valid_factor(f, nbits=64):
	if f.degree() >= nbits: return False
	return all(33 <= i <= 126 for i in poly_to_bytes(f, nbits=nbits))

def find_valid_factor_pairs(factors, cur=1, other=1):
	if len(factors) == 0:
		if is_valid_factor(cur) and is_valid_factor(other):
			yield (cur, other)
		return
	(f, c), *rest = factors
	for i in range(c + 1):
		next_cur = cur * f^i
		next_other = other * f^(c - i)
		if next_cur.degree() >= 64 or next_other.degree() >= 64: continue
		yield from find_valid_factor_pairs(rest, cur=next_cur, other=next_other)

def pext(n, mask):
	i = 0
	result = 0
	while mask:
		if mask & 1:
			result += (n & 1) << i
			i += 1
		mask >>= 1
		n >>= 1
	return result
	
# pclmulqdq
for xx,yy in find_valid_factor_pairs(list(factor(p))[::-1]):
	xxx = sum(2^i for i,b in enumerate(xx.list()) if b)
	yyy = sum(2^i for i,b in enumerate(yy.list()) if b)
	if pext(xxx, yyy) == 562026407: # pext
		flag.extend(poly_to_bytes(xx))
		flag.extend(poly_to_bytes(yy))
		break

print(bytes(flag))

# part 2

# from addsubps: f0-f2, f1+f0, f2-f1, f3+f3
r0, r1, r2, r3 = map(float32, (1.7268289610614863e+28, 1.7269343608586483e+28, 1.0539650845336378e+24, 3.6204573916620575e-07))
dp = float32(5953314400000.0) # from dpps: 2 * f1 * f3
f3 = r3 / 2
f1 = dp / 2 / f3
f2 = r2 + f1
f0 = r1 - f1

flag.extend(struct.pack("<ffff", f0, f1, f2, f3))

print(bytes(flag))

# part 3

s = Solver()

w0 = [flag[i] + flag[i+1]*256 for i in range(0, len(flag), 2)]

f = [BitVec(f"a{i}", 32) for i in range(16)]
for i in f:
	s.add(i <= 126)
	s.add(i >= 13)
w1 = [f[i] + f[i+1] * 256 for i in range(0, 16, 2)]
expect = (16235, 17697, 20742, 16142, 14700, 13192, 46209, 16050)
lows = expect[::2]
highs = expect[1::2]
for i,(lo,hi) in enumerate(zip(lows, highs)):
	s.add((w0[2*i] * w1[2*i] + w0[2*i+1] * w1[2*i+1]) == (lo + hi * 65536)) # pmaddwd

search = [0xef, 0xbe, 0xad, 0xde, 0xde, 0xc0, 0x37, 0x13]
e2 = [14,2,67,2,76,2,25,2,2,1,167,1,170,1,151,1]
e2[8] = 228
e3 = [136,1,95,1,90,1,89,1,46,1,30,1,97,1,71,1]
# mpsadbw
for i in range(8):
	diff = sum([If(f[i+j] > search[j], f[i+j] - search[j], search[j] - f[i+j]) for j in range(4)])
	s.add((e2[2*i] + e2[2*i+1] * 256) == diff)

for i in range(8):
	diff = sum([If(f[i+j+4] > search[j+4], f[i+j+4] - search[j+4], search[j+4] - f[i+j+4]) for j in range(4)])
	s.add((e3[2*i] + e3[2*i+1] * 256) == diff)

assert s.check() == sat
m = s.model()
result = [m[i].as_long() for i in f]
flag.extend(result)

s.add(Or(*[f[i] != result[i] for i in range(16)]))
assert s.check() == unsat

print(bytes(flag))

# part 4

p2 = (109, 247, 219, 94, 35, 204, 117, 41, 211, 17, 186, 227, 73, 87, 36, 16)
p = sum(sum(x^(i*8 + j) for j in range(8) if p2[i] & (1 << j)) for i in range(len(p2)))

# pclmulqdq
for xx,yy in find_valid_factor_pairs(list(factor(p))[::-1]):
	xxx = sum(2^i for i,b in enumerate(xx.list()) if b)
	yyy = sum(2^i for i,b in enumerate(yy.list()) if b)
	f = poly_to_bytes(xx) + poly_to_bytes(yy)
	if f[5*2] + f[5*2+1]*256 == 13156: # phminposuw
		flag.extend(f)
		break
print(bytes(flag))
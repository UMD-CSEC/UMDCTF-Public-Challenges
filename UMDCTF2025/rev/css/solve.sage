from tqdm import tqdm
import random, string, itertools, time
from lc2 import lc2
F = GF(2^127-1)
A = 62406
A24 = (A+2)//4
P = 3
Q = 74991407119409573653134810242842117674
E = EllipticCurve(F, [0, A, 0, 1, 0])

startfrfr = time.time()

def mmul(x, n):
	# montgomery ladder
	x0, z0 = F(1), F(0)
	x1, z1 = F(x), F(1)
	bits = n.bits()[::-1]
	for i in bits[:-1]:
		if i == 0:
			d0 = x0 - z0
			s0 = x0 + z0
			d1s0 = (x1 - z1) * s0
			s1d0 = (x1 + z1) * d0
			x1 = (d1s0 + s1d0)^2
			z1 = x*(d1s0 - s1d0)^2
			d02 = d0*d0
			s02 = s0*s0
			xz4 = s02 - d02
			x0 = d02 * s02
			z0 = xz4 * (d02 + A24 * xz4)
		else:
			d1 = x1 - z1
			s1 = x1 + z1
			d1s0 = d1 * (x0 + z0)
			s1d0 = s1 * (x0 - z0)
			x0 = (d1s0 + s1d0)^2
			z0 = x*(d1s0 - s1d0)^2
			d12 = d1*d1
			s12 = s1*s1
			xz4 = s12 - d12
			x1 = d12 * s12
			z1 = xz4 * (d12 + A24 * xz4)
	if bits[-1] == 0:
		d02 = (x0 - z0)^2
		s02 = (x0 + z0)^2
		xz4 = s02 - d02
		x0 = d02 * s02
		z0 = xz4 * (d02 + A24 * xz4)
	else:
		d1 = x1 - z1
		s1 = x1 + z1
		d1s0 = d1 * (x0 + z0)
		s1d0 = s1 * (x0 - z0)
		x0 = (d1s0 + s1d0)^2
		z0 = x*(d1s0 - s1d0)^2
	return Integer(x0 / z0)
print(Q)

def dll(a, base, bounds):
	fa = F(A)
	random.seed(int(1248))
	def add(p1, p2):
		x1, y1 = p1
		x2, y2 = p2
		s = (y2 - y1)/(x2 - x1)
		x3 = s*s - x1 - x2 - fa
		return (x3, (x1 - x3)*s - y1)
	def mul(p, n): return list(E(*p) * n)[:2]
	lb, ub = bounds
	width = ub-lb
	theta = 1.39307 # (Van Oorschot and Wiener, 1999)
	m = (width * (1 + exp(-theta)) / (2 * theta * (2 - exp(-theta)))).sqrt()
	N = (theta * m).round()
	m = m.round()
	for _ in range(10):
		M = []
		k = 0
		start = time.time()
		while 2**k < N:
			r = random.randrange(1, 2*m)
			M.append((r, mul(base, r)))
			k += 1
		print(time.time() - start)
		H = mul(base, ub)
		c = ub
		start = time.time()
		for i in range(N):
			r, e = M[(H[0].lift() & 0xffffffff) % k]
			H = add(H, e)
			c += r
		print(time.time() - start)
		mem = H[0]
		H = a
		start = time.time()
		while c >= lb:
			if ub > c and H[0] == mem:
				print(time.time() - start)
				return c
			r, e = M[(H[0].lift() & 0xffffffff) % k]
			H = add(H, e)
			c -= r
		print(time.time() - start)
	raise ValueError("failed")


spine1 = [12, 2, 4, 12, 5, 13, 15, 12, 12, 8, 2, 8, 11, 4, 14, 2, 2, 4, 5, 6, 13, 12, 2, 3, 12, 11, 7, 14, 7, 4, 1, 5, 8, 1, 14, 13, 11, 9, 7, 13, 2, 7, 11, 8, 13, 9, 14, 8, 9, 2, 4, 10, 12, 10, 11, 13, 14, 8, 2, 5, 2, 9, 12, 15, 4, 13, 11, 3, 5, 1, 8, 9, 3, 4, 7, 6, 9, 4, 8, 6, 5, 13, 13, 9, 15, 8, 15, 5, 2, 11, 8, 8, 15, 8, 9, 3, 1, 6, 1, 7, 6, 15, 12, 2, 3, 13, 9, 10, 2, 3, 13, 4, 13, 2, 15, 2]
spine2 = [0, 11, 3, 7, 5, 10, 5, 9, 2, 10, 3, 4, 13, 13, 0, 15, 15, 14, 6, 10, 10, 15, 1, 5, 3, 7, 12, 4, 4, 14, 14, 13, 6, 13, 5, 10, 13, 14, 2, 11, 8, 6, 1, 14, 11, 4, 9, 13, 6, 3, 8, 10, 10, 7, 0, 5, 7, 13, 9, 5, 15, 5, 12, 15, 3, 1, 8, 4, 0, 10, 4, 13, 9, 2, 4, 2, 11, 0, 5, 7, 12, 15, 11, 14, 15, 15, 1, 4, 15, 2, 13, 6, 10, 10, 8, 13, 2, 13, 3, 2, 11, 4, 6, 10, 15, 2, 14, 7, 10, 7, 9, 0, 4, 5, 1, 10]
prng_table = [57, 173, 27, 125, 32, 64, 63, 175, 253, 84, 111, 109, 85, 212, 235, 250, 2, 18, 69, 131, 93, 195, 110, 38, 29, 223, 178, 164, 237, 211, 149, 176, 24, 194, 141, 240, 94, 43, 25, 234, 68, 163, 170, 112, 75, 136, 148, 65, 14, 249, 48, 135, 248, 28, 31, 26, 153, 186, 91, 233, 182, 40, 154, 196, 61, 132, 115, 1, 52, 150, 99, 10, 66, 41, 208, 245, 7, 172, 113, 201, 122, 247, 242, 155, 36, 30, 255, 119, 180, 202, 218, 67, 105, 50, 89, 225, 12, 137, 181, 189, 133, 79, 71, 59, 4, 215, 197, 217, 210, 252, 145, 142, 78, 160, 158, 118, 34, 81, 161, 168, 117, 179, 62, 232, 226, 98, 9, 86, 147, 165, 33, 254, 95, 156, 76, 166, 102, 127, 44, 114, 39, 22, 162, 70, 80, 207, 100, 15, 87, 231, 236, 228, 35, 188, 203, 37, 152, 174, 126, 192, 124, 199, 230, 19, 219, 222, 47, 229, 246, 224, 58, 220, 45, 55, 96, 56, 134, 60, 13, 49, 216, 139, 23, 21, 97, 239, 54, 184, 169, 209, 51, 107, 227, 11, 183, 90, 213, 244, 46, 116, 243, 88, 16, 198, 72, 185, 200, 129, 74, 108, 187, 0, 123, 138, 128, 82, 204, 42, 53, 101, 104, 157, 177, 103, 73, 6, 191, 146, 206, 143, 241, 214, 167, 221, 17, 151, 120, 106, 130, 3, 121, 92, 83, 205, 5, 251, 140, 193, 190, 159, 144, 20, 8, 77, 171, 238]

puncturing = []

start = time.time()
P1 = E.lift_x(P) * 42535295865117307934050092614044414781
Q1 = E.lift_x(Q) * 42535295865117307934050092614044414781
for b in range(4):
	if Q1 * b == P1: break
else: raise Exception("this shouldnt happen")
result = dll(list(E.lift_x(P) - E.lift_x(Q) * b)[:2], list(E.lift_x(Q) * 4)[:2], (0, 2^57 // 4))
result = result * 4 + b
end = time.time()
print(end - start)
print(hex(result))

q = Integer(result)
for i in range(58):
	puncturing.append(q & 1)
	q >>= 1

lc2inv = Matrix(GF(2), [Integer(i).digits(base=2, padto=len(lc2)) for i in lc2])^(-1)

def hash1(seed, r1, r2):
	new_seed = 0
	for j in range(32):
		out = prng_table[((seed >> (j*4)) & 0xf) + (r1 << 4)]
		new_seed += (out & 0xf) << (j*4)
		r1 = (out >> 4) ^^ r2
	return new_seed
def cost(seed, i):
	t2 = mmul(Q, seed)
	s1 = (t2 & 0xf) ^^ ((t2 >> 4) & 0xf)
	s2 = ((t2 >> 8) & 0xf) ^^ ((t2 >> 12) & 0xf)
	return bin(s1 ^^ spine1[i]).count('1') + bin(s2 ^^ spine2[i]).count('1')

seed = 0x7331
beam = [(0, tuple(), seed)]
candids = []
for i in range(116):
	nextbeam = []
	start = time.time()
	for curcost, path, s in beam:
		print(i, curcost, ''.join(f'{j:x}' for j in path))
		for r1 in range(16):
			for r2 in range(16):
				if i % 2 == 1 and r2 % 2 != puncturing[i//2]: continue
				ns = hash1(s, r1, r2)
				c1 = cost(ns, i)
				if curcost + c1 > 1: continue
				ns = mmul(P, ns)
				if i == 115:
					candids.append((curcost + c1, path + (r1, r2)))
					continue
				mincost = curcost + c1 + 8
				for r3 in range(16):
					for r4 in range(16):
						if i % 2 == 0 and r4 % 2 != puncturing[i//2]: continue
						ns2 = hash1(ns, r3, r4)
						c2 = cost(ns2, i+1)
						if curcost + c1 + c2 > 1: continue
						mincost = min(mincost, curcost + c1 + c2)
						if c2 == 0: break
					else: continue
					break
				else:
					continue
				nextbeam.append((mincost, path + (r1, r2), ns))
	beam = sorted(nextbeam)
	print(time.time() - start)
print(len(candids))

alpha = list(string.printable.strip().encode())

random.seed(int(0x62dcb0ee8ca15d83de82c8e895509c23))
charbits = []
for i in range(132):
	bits = list(range(128))
	random.shuffle(bits)
	charbits.append(bits[:len(alpha)])

for cost, path in candids:
	print(''.join(f'{j:x}' for j in path))
	bits = []
	for i in path: bits.extend((i >> j) & 1 for j in range(4))
	bits = bits[:len(lc2)]
	cbits = lc2inv * vector(GF(2), bits)
	flag = []
	for i in range(0, len(cbits), 7):
		c = sum(Integer(cbits[i+j]) << j for j in range(7))
		if c not in charbits[i//7]: break
		flag.append(alpha[charbits[i//7].index(c)])
	else:
		print(bytes(flag))
		continue
	print(f"invalid: ", bytes(flag))
print(time.time() - startfrfr)
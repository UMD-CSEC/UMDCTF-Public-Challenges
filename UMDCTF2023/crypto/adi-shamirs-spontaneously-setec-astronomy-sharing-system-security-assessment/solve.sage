from PIL import Image
import itertools
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

p = next_prime(2^128)
k = 64
n = 128

with Image.open("out.png") as im, Image.open("mask.png") as mask:
	px = im.load()
	mpx = mask.load()
	
	data = []
	obscured = []
	for y in range(n):
		r = [0] * n
		val = 0
		for x in range(n):
			val <<= 1
			for i,j in itertools.product(range(4), repeat=2):
				if mpx[4*x+i,4*y+j][3] == 0:
					val |= px[4*x+i,4*y+j][0] & 1
					break
			else: r[x] = 1
		data.append(val)
		obscured.append(r)

print("loaded images")

all_segments = []
n_segments = 0
max_size = 0
for i in range(1, n+1):
	segments = []
	obscured_rev = obscured[i-1][::-1] + [0]
	offset = 0
	size = 0
	for j,c in enumerate(obscured_rev):
		if c == 1:
			if size == 0:
				size = 1
				offset = j
			else:
				size += 1
		else:
			if size != 0:
				segments.append((size, offset))
				max_size = max(max_size, size)
				data[i-1] += 2^(offset + size - 1)
				size = 0
	all_segments.append(segments)
	n_segments += len(segments)

print(n_segments)
print(sum([sum([s for (s,o) in i]) for i in all_segments]))

def nearzero(i): return ((int(i)%p)+(p//2))%p - p//2
def print_matrix(m):
	t = {int(p): "p", int(0): "_"}
	for i in m: print("[",*["%4s" % str(t.get(int(j), (-1 if j<0 else 1) * int(j).bit_length())) for j in i],"]")

m = matrix(ZZ, [[i^j for j in range(k)] for i in range(1,k+1)])
inv = ~m
d = lcm(sum([[i.denominator() for i in r] for r in inv],[]))
ad = inv * d
m_outs = vector(ZZ, data[:k])

relsize = 1 + n_segments + (n-k)
rels = []
for i in range(k, n):
	c = [0] * relsize
	diff = vector(ZZ, [(i+1)^j for j in range(k)]) * ad
	const = d * data[i] - diff * m_outs
	c[0] = nearzero(const)
	seg_index = 1
	for j in range(i+1):
		for (s,o) in all_segments[j]:
			if j < k:
				c[seg_index] = -diff[j] * 2^o
			elif j == i:
				c[seg_index] = d * 2^o
			seg_index += 1
	c[1 + n_segments + (i-k)] = p
	rels.append(c)

out_weight = 2^(n + max_size)
weights = []
weights.append([out_weight] + [0] * (relsize-1))

K = 2^(max_size)
seg_index = 1
segweights = []
for seglist in all_segments:
	for (s,o) in seglist:
		c = [0] * relsize
		weight = K // 2^s
		segweights.append(weight)
		c[seg_index] = weight
		seg_index += 1
		weights.append(c)

M = Matrix(ZZ, weights + rels).T
print(M.dimensions())
print("LLL")
reduced = M.LLL()
print("LLL done")
for r in reduced:
	out_coef = r[0] / out_weight
	if out_coef and all(i%p == 0 for i in r[1+n_segments:]):
		segvals = [i/(j * out_coef) for i,j in zip(r[1:1+n_segments],segweights)]
		break
else:
	print("sad")
	exit()

seg_index = 0
for i, seglist in enumerate(all_segments):
	for (s,o) in seglist:
		data[i] += segvals[seg_index] * 2^o
		seg_index += 1

R = PolynomialRing(GF(p), 'x')
f = R.lagrange_polynomial([*zip(range(1,n+1), data)])
val = int(f(0))
print(val)

k = val.to_bytes(16, 'big')
with open("flag.png.enc", "rb") as f: ivc = f.read()
iv, c = ivc[:16], ivc[16:]
cipher = AES.new(k, AES.MODE_CBC, iv=iv)
with open("solved.png", "wb") as f: f.write(unpad(cipher.decrypt(c), 16))
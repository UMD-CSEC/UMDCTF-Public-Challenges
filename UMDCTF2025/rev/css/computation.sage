from tqdm import tqdm
import random, string
F = GF(2^127-1)
A = 62406
E = EllipticCurve(F, [0, A, 0, 1, 0])
o = E.order()
R = Zmod(o)
P = E.lift_x(3)

with open("flag.txt") as f:
	flag = f.read().strip()

flag_inner = flag[7:-1]
inner_bits = len(flag_inner) * 7
'''
random.seed(int(0x62dcb0ee8ca15d83de82c8e895509c23))

lc = []
for i in tqdm(range(inner_bits)):
	while 1:
		row = [int(random.random() < 0.05) for i in range(inner_bits)]
		if Matrix(GF(2), lc + [row]).rank() == len(lc) + 1:
			lc.append(row)
			break
lcl = []
for i in lc:
	lcl.append(sum(i[idx] << idx for idx in range(inner_bits)))
print(',\n'.join(map(hex, lcl)))
'''
expect4_2 = [1, 14, 8, 3, 9, 4, 0, 15, 2, 7, 1, 6, 10, 10, 5, 13, 6, 9, 5, 15, 0, 10, 8, 5, 1, 15, 12, 3, 0, 1, 5, 3, 3, 6, 15, 1, 15, 2, 1, 10, 11, 0, 14, 6, 0, 14, 6, 13, 13, 4, 9, 11, 8, 8, 3, 5, 4, 10, 4, 9, 10, 11, 0, 9, 11, 6, 13, 4, 9, 13, 13, 14, 6, 13, 6, 5, 7, 13, 4, 11, 14, 6, 2, 4, 14, 13, 6, 2, 11, 10, 2, 15, 5, 13, 6, 6, 2, 12, 4, 11, 0, 12, 13, 14, 5, 4, 2, 4, 13, 6, 6, 5, 6, 5, 4, 8, 10, 3, 2, 12, 0, 7, 9, 6, 15, 8, 5, 9, 3, 9, 7, 6, 5, 0, 5, 5, 12, 8, 5, 8, 2, 4, 14, 4, 14, 4, 14, 5, 8, 11, 8, 5, 15, 2, 12, 11, 0, 10, 4, 6, 13, 13, 3, 14, 9, 4, 2, 1, 4, 10, 13, 7, 6, 13, 13, 4, 9, 14, 11, 4, 5, 6, 3, 0, 4, 3, 14, 3, 4, 5, 8, 11, 5, 12, 7, 15, 13, 2, 10, 2, 2, 1, 14, 1, 12, 3, 6, 5, 13, 2, 13, 9, 4, 9, 8, 15, 9, 0, 9, 5, 11, 13, 8, 10, 0, 10, 0, 15, 0, 10, 8]
if len(expect4_2) % 2 == 1: expect4_2.append(0)

Qvalues = [i & 1 for i in expect4_2[3::4]]
q = sum(v * 2^i for i, v in enumerate(Qvalues))
print(q)
Q = R(q)^(-1) * P # P = q * Q

print(Q)

seed = 0x7331

prng_table = list(range(256))
random.seed(int(110495220192904012260259857295472515749))
while 1:
	random.shuffle(prng_table)
	if all(i!=prng_table[i] for i in range(256)): break

spine1 = []
spine2 = []
for i in range(0, len(expect4_2), 2):
	r1 = expect4_2[i]
	r2 = expect4_2[i+1]
	new_seed = 0
	for j in range(32):
		out = prng_table[((seed >> (j*4)) & 0xf) + (r1 << 4)]
		new_seed += (out & 0xf) << (j*4)
		r1 = (out >> 4) ^^ r2
	print(i, hex(new_seed))
	t2 = Integer((new_seed * Q)[0])
	s1 = (t2 & 0xf) ^^ ((t2 >> 4) & 0xf)
	s2 = ((t2 >> 8) & 0xf) ^^ ((t2 >> 12) & 0xf)
	spine1.append(s1)
	spine2.append(s2)
	print(s1, s2, hex(t2))
	seed = Integer((new_seed * P)[0])

print(spine1)
print(spine2)
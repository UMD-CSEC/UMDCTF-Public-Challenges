import struct
from numpy import float32

with open("flag.txt", "rb") as f: flag = f.read()
assert flag.startswith(b"UMDCTF{")
assert flag.endswith(b"}")
flag = flag[7:-1]
assert len(flag) == 64

inps = [int.from_bytes(flag[i:i+16], 'little') for i in range(0, 64, 16)]
R.<x> = GF(2)[]


i1 = inps[0]
r1 = sum(x^i for i in range(64) if inps[0] >> i & 1)
r2 = sum(x^i for i in range(64) if inps[0] >> (i+64) & 1)
check1 = int(''.join(map(str, (r1 * r2).list()))[::-1], 2).to_bytes(16, 'little')
print(list(check1))

f1 = [float32(i) for i in struct.unpack("<ffff", flag[16:32])]
print(f1)
res = (f1[0] - f1[2], f1[1] + f1[0], f1[2] - f1[1], f1[3] + f1[3])
print(res)
solve = ((res[0]+res[2]+res[1])/2, (res[1]-(res[0]+res[2]))/2, res[2] + (res[1]-(res[0]+res[2]))/2, res[3]/2)
print(struct.pack("<ffff", *solve))

print(f1[3] * f1[1] + f1[1] * f1[3])

words = struct.unpack("<HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH", flag)

dp = [words[i*2]*words[16+i*2] + words[i*2+1]*words[16+i*2+1] for i in range(8)]
print(sum([[i & 0xffff, i >> 16] for i in dp], []))

search = [0xef, 0xbe, 0xad, 0xde]
for i in range(8):
	diff = sum([abs(flag[32+i+j] - search[j]) for j in range(4)])
	print(diff & 0xff, diff >> 8)
print("...")	
search = [0xde, 0xc0, 0x37, 0x13]
for i in range(8):
	diff = sum([abs(flag[32+4+i+j] - search[j]) for j in range(4)])
	print(diff & 0xff, diff >> 8, sep=',', end=',')
print()

i1 = inps[3]
r1 = sum(x^i for i in range(64) if inps[3] >> i & 1)
r2 = sum(x^i for i in range(64) if inps[3] >> (i+64) & 1)
check2 = int(''.join(map(str, (r1 * r2).list()))[::-1], 2).to_bytes(16, 'little')
print(list(check2))
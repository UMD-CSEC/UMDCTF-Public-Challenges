from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
from os import urandom

with open("flag.txt", "rb") as f:
	flag = f.read()
	m = bytes_to_long(flag)

p = q = 0
while p % 4 != 3: p = getPrime(384)
while q % 4 != 3: q = getPrime(384)

N = p * q
print(f"{N = }")
def encrypt(m):
	lp = (pow(m, (p-1)//2, p) + 1) % p - 1
	lq = (pow(m, (q-1)//2, q) + 1) % q - 1
	return m * m % N, lp, lq

def decrypt(c, lp, lq):
	yq = pow(q, -1, p)
	yp = (1 - yq * q) // p

	mp = pow(c, (p+1)//4, p)
	mq = pow(c, (q+1)//4, q)
	
	if (pow(mp, (p-1)//2, p) - lp) % p != 0: mp = p - mp
	if (pow(mq, (q-1)//2, q) - lq) % q != 0: mq = q - mp

	return (yp * p * mq + yq * q * mp) % N
	

c, lp, lq = encrypt(m)
print(f"{(c, lp, lq) = }")
print(f"{long_to_bytes(decrypt(c, lp, lq)) = }")
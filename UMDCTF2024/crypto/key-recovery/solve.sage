from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.number import long_to_bytes, bytes_to_long
import base64

with open("modified.pem", "r") as f:
	lines = f.read().splitlines()[1:-1]

lines_0 = []
lines_1 = []

for line in lines:
	lines_0.append(line.ljust(64, 'A'))
	lines_1.append(line.ljust(64, '/'))
known_0 = base64.b64decode(''.join(lines_0))
known_1 = base64.b64decode(''.join(lines_1))

def get_region(start, size):
	value = bytes_to_long(known_0[start:start+size])
	mask = value ^^ bytes_to_long(known_1[start:start+size])
	regions = []
	while mask:
		start = (mask & -mask).bit_length() - 1
		mask >>= start
		length = ((mask + 1) & -mask).bit_length() - 1
		mask -= (1 << length) - 1
		mask <<= start
		regions.append([start, length])
	return value, regions

def extract(v, start, length):
	return ((v >> start) & ((1 << length) - 1)) << start

n, n_missing = get_region(38,256)
e, e_missing = get_region(296,3)
d, d_missing = get_region(303,256)
p, p_missing = get_region(563,128)
q, q_missing = get_region(695,128)
dp, dp_missing = get_region(827,128)
dq, dq_missing = get_region(959,128)

gcd_pm1_qm1 = 10 # you can get this from observing that e*d/phi is very very close to 3341.1
lambda_approx = (n - n//q - q + 1) // gcd_pm1_qm1

k = int(round(e*d/lambda_approx))

# Use the fact that k * (n - p - q + 1) / 10 = e*d + 1 to recover the upper half of n and d
# (we can't recover the lower half yet because of the errors in p and q)

d_approx = (lambda_approx * k - 1) // e
d ^^= extract(d_approx, *d_missing.pop())

n_approx = (gcd_pm1_qm1 * (e*d - 1)) // k - 1 + q + n//q
n ^^= extract(n_approx, *n_missing.pop())

lambda_approx = (n - n//q - q + 1) // gcd_pm1_qm1
d_approx = (lambda_approx * k - 1) // e
d ^^= extract(d_approx, *d_missing.pop())

n_approx = (gcd_pm1_qm1 * (e*d - 1)) // k - 1 + q + n//q
n ^^= extract(n_approx, *n_missing.pop())

lambda_approx = (n - n//q - q + 1) // gcd_pm1_qm1
d_approx = (lambda_approx * k - 1) // e
d ^^= extract(d_approx, *d_missing.pop())

# Use 10 * (e*d - 1) = k * (n - p - q + 1) mod MOD
# and          p * q = n                   mod MOD
# to recover more lower bits of n and q

MOD = 2^(p_missing[0][0]) # We know p, e, d mod MOD; n, q are unknown
phi_mod = 10 * (e*d - 1) * pow(k, -1, MOD) % MOD # this equals n - p - q + 1 mod MOD
x = (phi_mod + p - 1) % MOD
# pq = n and n-q = x, so pq = q+x => q = x / (p-1).
# unfortunately p-1 is even so it can't be inverted mod MOD
# so we need to go down to a modulus where p-1 is invertible
gcd_pm1_mod = gcd(p-1, MOD)
MOD //= gcd_pm1_mod
q_mod = (x // gcd_pm1_mod) * pow((p-1) // gcd_pm1_mod, -1, MOD) % MOD
n_mod = (q_mod + x) % MOD

n = n - (n % MOD) + n_mod
q = q - (q % MOD) + q_mod
added_bits = MOD.bit_length() - 1 - q_missing[0][0]
n_missing.pop(0)
q_missing[0][0] += added_bits
q_missing[0][1] -= added_bits

# Same thing as the last step, but now n, e, d are known and p, q are unknown
MOD = 2^(d_missing[0][0])
phi_mod = 10 * (e*d - 1) * pow(k, -1, MOD) % MOD
x = (n - phi_mod + 1) % MOD
# x = p + q and pq = n, so p(x-p) = n => p^2 - px + n = 0. This is a quadratic with roots p,q
# The quadratic formula has a division by 2, but 2 is not invertible so we'll need to change the modulus.
MOD //= 2
F = Integers(MOD)
sqroot = int(F((x//2)^2 - n).sqrt())
# Squares actually have four square roots mod 2^n (\pm x, \pm x + 2^(n-1)), so we need to change the modulus again.
MOD //= 2
root1 = (x//2 + sqroot) % MOD
root2 = (x//2 - sqroot) % MOD
if (root1 - q) % (2^q_missing[0][0]) == 0: root1, root2 = root2, root1
assert (root1 - p) % (2^p_missing[0][0]) == 0
p = p - (p % MOD) + root1
q = q - (q % MOD) + root2
added_bits = MOD.bit_length() - 1 - p_missing[0][0]
p_missing[0][0] += added_bits
p_missing[0][1] -= added_bits
added_bits = MOD.bit_length() - 1 - q_missing[0][0]
q_missing[0][0] += added_bits
q_missing[0][1] -= added_bits

# We know e * dp - 1 = kp * (p-1) for some kp < e
# We can recover kp ~ (e * dp - 1) / (p-1)
kp = int(round((e * dp - 1) / (n//q - 1)))
# Recover lower bits of dp
MOD = 2^(p_missing[0][0])
dp_mod = (kp * (p-1) + 1) * pow(e, -1, MOD) % MOD
dp = dp - (dp % MOD) + dp_mod
dp_missing.pop(0)

# Recover lower bits of p
MOD = 2^(dp_missing[0][0])
# kp is divisible by 2 so we need to divide by gcd again
gcd_kp_mod = gcd(kp, MOD)
MOD //= gcd_kp_mod
p_mod = (((e * dp - 1) // gcd_kp_mod) * pow(kp // gcd_kp_mod, -1, MOD) + 1) % MOD
p = p - (p % MOD) + p_mod
p_missing.pop(0)

# p * q = n mod MOD
MOD = 2^(n_missing[0][0])
q_mod = n * pow(p, -1, MOD) % MOD
q = q - (q % MOD) + q_mod
q_missing.pop(0)

MOD = 2^(q_missing[0][0])
n_mod = p * q % MOD
n = n - (n % MOD) + n_mod % MOD
added_bits = MOD.bit_length() - 1 - n_missing[0][0]
n_missing[0][0] += added_bits
n_missing[0][1] -= added_bits

# Recover lower bits of d
# 10 * (e*d - 1) = k * (n - p - q + 1) mod MOD
MOD = 2^(n_missing[0][0])
kphi_mod = (k * (n - p - q + 1)) % MOD
MOD //= 2 # 10 is even
d_mod = (kphi_mod // 2 * pow(5, -1, MOD) + 1) * pow(e, -1, MOD) % MOD
d = d - (d % MOD) + d_mod
d_missing.pop(0)

# Recover lower bits of n, q. We've been here before
MOD = 2^(p_missing[0][0]) # We know p, e, d mod MOD; n, q are unknown
phi_mod = 10 * (e*d - 1) * pow(k, -1, MOD) % MOD # this equals n - p - q + 1 mod MOD
x = (phi_mod + p - 1) % MOD
# pq = n and n-q = x, so pq = q+x => q = x / (p-1).
gcd_pm1_mod = gcd(p-1, MOD) # p-1 is even
MOD //= gcd_pm1_mod
q_mod = (x // gcd_pm1_mod) * pow((p-1) // gcd_pm1_mod, -1, MOD) % MOD
n_mod = (q_mod + x) % MOD
n = n - (n % MOD) + n_mod
q = q - (q % MOD) + q_mod
n_missing.pop(0)
added_bits = MOD.bit_length() - 1 - q_missing[0][0]
q_missing[0][0] += added_bits
q_missing[0][1] -= added_bits

# Lattice time!
MOD = 2^n_missing[0][0]
start = 2^q_missing[0][0]
# we know one more bit of p, but we won't use it to make things easier
p &= ~int(start)
M = MOD / start
# (p + eps_p * start)(q + eps_q * start) = n mod MOD
# q * eps_p * start + p * eps_q * start = n - pq mod MOD
# eps_p + p/q * eps_q = (n - pq) / (q*start) mod M
Wp = 2^q_missing[0][1]
Wq = 2^p_missing[0][1]
S = 10^100 # something big
L = matrix(ZZ, [
	[0, Wp, 0, S], # eps_p
	[0, 0, Wq, p * pow(q, -1, M) % M * S], # eps_q
	[S, 0, 0, (p*q-n) // start * pow(q, -1, M) % M * S],
	[0, 0, 0, M * S],
])
for (x, Wpp, Wqq, diff) in L.LLL():
	if x != 0 and diff == 0:
		coef = x / S
		eps_p = Wpp / (Wp * coef)
		eps_q = Wqq / (Wq * coef)
		break
eps_p, eps_q = int(eps_p), int(eps_q) # fixes sage complaining about xor
p ^^= eps_p * start
q ^^= eps_q * start
p_missing.pop(0)
q_missing.pop(0)

# recover d from p, q, n mod MOD
# 10 * (e*d - 1) = k * (n - p - q + 1) mod MOD
MOD = 2^n_missing[0][0]
kphi_mod = (k * (n - p - q + 1)) % MOD
MOD //= 2 # 10 is even
d_mod = (kphi_mod // 2 * pow(5, -1, MOD) + 1) * pow(e, -1, MOD) % MOD
d = d - (d % MOD) + d_mod
d_missing.pop(0)

lambda_ = (e*d - 1) // k
phi = lambda_ * gcd_pm1_qm1

# phi = pq - p - q + 1 mod MOD
MOD = 2^q_missing[0][0]
n_mod = (phi + p + q - 1) % MOD
n = n - (n % MOD) + n_mod
added_bits = MOD.bit_length() - 1 - n_missing[0][0]
n_missing[0][0] += added_bits
n_missing[0][1] -= added_bits

# phi = pq - p - q + 1 mod MOD
# phi + p - 1 = (p-1)*q mod MOD
MOD = 2^p_missing[0][0]
gcd_pm1_mod = gcd(p-1, MOD)
MOD //= gcd_pm1_mod
q_mod = (phi + p - 1) // gcd_pm1_mod * pow((p-1) // gcd_pm1_mod, -1, MOD) % MOD
q = q - (q % MOD) + q_mod
added_bits = MOD.bit_length() - 1 - q_missing[0][0]
q_missing[0][0] += added_bits
q_missing[0][1] -= added_bits

# n = pq mod MOD
MOD = 2^q_missing[0][0]
n_mod = p * q % MOD
n = n - (n % MOD) + n_mod
n_missing.pop(0)

with open("out.txt", "rb") as f:
	ct = f.read()
key = RSA.construct((int(n), int(e), int(d)))
cipher = PKCS1_OAEP.new(key)
pt = cipher.decrypt(ct)
print(pt)

# Eeeveelutions

Problem:

```python
from Crypto.Util.number import getPrime, inverse, bytes_to_long
from math import gcd
import re
import string
import random


while True:
    p = getPrime(1024)
    q = getPrime(1024)

    n = p * q
    e = 3
    phi = (p-1)*(q-1)

    if gcd(phi, e) == 1:
        d = inverse(e, phi)
        break


with open('flag.txt', 'r') as f:
    flag = f.read().strip()

pad1 = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12))
pad2 = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12))

evolutions = ['umbreon', 'sylveon', 'jolteon', 'flareon', 'glaceon', 'leafeon']
e1 = random.choice(evolutions)
while True:
    e2 = random.choice(evolutions)
    if e2 != e1:
        break

flag1 = re.sub("eevee", e1, flag) + pad1
flag2 = re.sub("eevee", e2, flag) + pad2

f1 = bytes_to_long(flag1.encode())
f2 = bytes_to_long(flag2.encode())

ct1 = pow(f1, e, n)
ct2 = pow(f2, e, n)

print(f"n = {n}")
print(f"e = {e}")
print(f"ct1 = {ct1}")
print(f"ct2 = {ct2}")

```


This is a classic application of Coppersmith's short pad attack. The public exponent `e` is small, and the padding appended to the ciphertext is too short to provide adequate randomness.
But first, let's investigate a simpler problem.

## The Franklin-Reiter attack
Let's consider the case where there is no padding. c1 and c2 have a known linear relationship to each other: we can obtain the plaintext of c2 by adding a certain value to c1.
What is this value? We know the two ciphertexts differ by exactly four letters. We don't know which four letters they are, or which characters are specifically used, but we have a finite number of
possible differences. That means we can use the [Franklin-Reiter attack](https://en.wikipedia.org/wiki/Coppersmith%27s_attack#Franklin%E2%80%93Reiter_related-message_attack) to recover the ciphertexts.

In essence, `x^e - c1 mod n` and `(x + diff)^e - c2 mod n` have a common root of flag1. Thus, the gcd of the two polynomials is the polynomial `x - flag1`. We can compute the gcd of the two polynomials using the Euclidean algorithm
in this case (this works well because `e = 3`). Once we do that, we have the original plaintext message. 

To summarize, if we know the difference between the two plaintext messages, we can decrypt them quickly. Because we have a small number of possible differences, we can just try the Franklin-Reiter attack on all possible
differences between f1 and f2.

## Dealing with padding

Unfortunately, there's randomized padding, which drastically increases the number of possible differences we'd have to test. So we need to use another technique to figure out the randomized part of the padding.
This difference is relatively small: in particular, it's less than `2^96`, which in turn is less than `(k / e^2)` where k is the number of bits of n. 
This means we can use [Coppersmith's short pad attack](https://en.wikipedia.org/wiki/Coppersmith%27s_attack#Coppersmith%E2%80%99s_short-pad_attack)
to recover the difference from the padding.

We construct two polynomials `g1(x,y) = x^e - c1` and `g2(x,y) = (x+y+diff)^e - c2` where `diff` is one of the candidate differences from the find/replace. `y` here represents the diffence from the padding.
We want to find a `y` such that both polynomials have the same zero in x. We can use a specifically constructed polynomial called the [resultant](https://en.wikipedia.org/wiki/Resultant) for this. The resultant,
h(y) not only has a root y that will allow us to find the exact difference between f1 and f2, but we know this root is small. We can use the `small_roots()` function in sage to recover y.

Once we know the root of `h(y)`, we can use the Franklin Reiter attack to recover the original encrypted flag.

Here's it all in Sage:

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long
import math


n = (put n here) 
e = 3
ct1 = (put ct1 here)
ct2 = (put ct2 here)

evolutions = [b'umbr', b'sylv', b'jolt', b'flar', b'glac', b'leaf']
all_diffs = [ bytes_to_long(a) - bytes_to_long(b) for b in evolutions for a in evolutions if a != b]


# adapted from https://github.com/yud121212/Coppersmith-s-Short-Pad-Attack-Franklin-Reiter-Related-Message-Attack/blob/master/coppersmiths_short_pad_attack.sage
def short_pad_attack(i, known_diff):
    PRxy.<x,y> = PolynomialRing(Zmod(n))
    PRx.<xn> = PolynomialRing(Zmod(n))
    PRZZ.<xz,yz> = PolynomialRing(Zmod(n))

    g1 = x^e - ct1
    g2 = (x+y+2^i * known_diff)^e - ct2

    q1 = g1.change_ring(PRZZ)
    q2 = g2.change_ring(PRZZ)


    h = q2.resultant(q1)
    h = h.univariate_polynomial()
    h = h.change_ring(PRx).subs(y=xn)
    h = h.monic()

    kbits = n.nbits()//(2*e*e)
    roots = h.small_roots(X=2^kbits, beta=0.5) 

    if roots == []:
        return -1
    else:
        return roots[0]

def fr(diff):
    R.<X> = Zmod(n)[]
    f1 = X^e - ct1
    f2 = (X + diff)^e - ct2
    g = polygcd(f1,f2).coefficients()[0]
    if g > 1:
        print(long_to_bytes(int(n-g)))


def polygcd(a, b):
    if(b == 0):
        return a.monic()
    else:
        return polygcd(b, a % b)

# We know the difference is aligned to byte boundaries
for i in range(8*14, 200*8, 8):
    print(i)
    for known_diff in all_diffs:
        diff = short_pad_attack(i, known_diff)
        if (diff != -1):
            print("found diff")
            fr(diff + 2^i * known_diff)
```


The script takes about 90 seconds to find the flag on my computer, since it does do a lot of computation. It outputs 
`Congratulations, you did it! Anyways, here's your flag: UMDCTF{y0Ur_-__flareon_h4s_eeV0Lv3d_1nt0_CRypT30N}zoWs6lqnbZpp`

So the flag is `UMDCTF{y0Ur_-__eevee_h4s_eeV0Lv3d_1nt0_CRypT30N}`


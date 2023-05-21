# LWE

Both Ekans and Caterpie were based off of LWE cryptography, which is a form of public-key cryptography designed on the hardness of solving the following matrix equation for `s`, given `A` and `b`:

```
As + e = b mod q
```

Here A is matrix, and s, e, and b are vectors. `e` and `s` both have relatively small entries.

In this implementation of an LWE cryptosystem, the pair `(A, B = As + e)` is the public key, and `s` is the secret key.

## Encryption and Decryption 

To encrypt a message, one first generates small error matrices S' and E', and a small error vector e'.

One computes `B' = S'A' + E' mod q`, and `V = S' B + e' + encode(msg)`. Encode is a function that maps a four-bit "nibble" to evenly spaced numbers between 0 and q.

To decrypt, the receiver computes `V - B'*s`. Let's expand it all out to see what happens:

```
V - B' * s = 
S'B + e' + msg - B's = 
S'(As + e) + e' + msg - (S'A' + E')s = 
S'As + e + e' + msg - S'A's + E's = 
e + e' + msg + E's
```

Since all the error terms are small, we get approximately our message. To decode it, we look at the closest number that the encode function maps to, and reverse that to get a nibble.

That's a brief description of how LWE crypto works. If we are able to recover s from (A, As + e), we can decrypt the ciphertexts given to us.

# Ekans

Instead of randomly generating e for the secret key, this problem just reverses s. This means we can write the equation `b = As + e mod q` as `b = (A + F)s mod q`, where F is the permutation matrix that reverses a vector (consisting
of 1s along the top-right to bottom-left diagonal, and 0s elsewhere). 

Once we have this equation, we can easily solve for `s` by Gaussian elimination. Once we have `s`, we can decrypt the ciphertext.

Flag: `UMDCTF{w3ll_m@ybE_1_5h0uLdnt_h4v3_tRi3d_t0_s@ve_0N_thE_raNdomn3ss._Le55on_l34rn3d}`


```python
# take output.txt and wrap the values in matrix() before running this script
load("output.sage")

q = 15901
n = 256

flip = [[0 for _ in range(n)] for _ in range(n)]
for i in range(n):
    flip[i][n-i-1] = 1

flip = matrix(flip)

R = IntegerModRing(q)
AF = (A + flip).change_ring(R)

s = AF.solve_right(B)

# Decryption functions 
def decode_msg(msg):
    hex_vals = ""
    for entry in msg:
        val = entry[0]
        val = round(int(val) * (2**4 / q) ) % (2**4)
        hex_vals += '0123456789abcdef'[val] # lazy way to convert to a single hex digit
    return hex_vals


def decrypt():
    msg = (V - B_prime*s) % q
    return decode_msg(msg)

print(decrypt())

```


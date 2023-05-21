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

# Caterpie

We need to find s and we're done. The parameters of this cryptosystem are too small, meaning we can recover `s` from `As+e` using lattice reduction.

There are several different ways of doing this, but the one I opted to use was viewing LWE as a "Bounded Distance Decoding (BDD)" problem, then converting the BDD instance into a uSVP instance
using a technique called "Kannan's embedding". This uSVP instance is small enough that we can run lattice reduction in a reasonable amount of time.

## What does that mean?

Starting off with lattices: a lattice is the set of integer combinations of a set of basis vectors. 

Bounded Distance Decoding is a problem in which one is given a point in space and a lattice vector, and they need to find the closest point in the lattice.

uSVP (unique shortest vector problem) is the problem in which, given a lattice, one needs to find a vector that is much shorter than the others with respect to some norm. uSVP can be solved using lattice reduction.

Lattice reduction is a very powerful technique that allows for one to find short vectors in a lattice. Lattice reduction is actually used under the hood the `small_roots()` algorithm from Eeveelutions, and it's part of the solve
for the ASSSASSSA challenge as well. For small enough lattices, it can solve uSVP. 

## So how do we do it?

Great, we have a technique to solve this: lattice reduction. But first we need to construct an instance of uSVP such that the secret vector is what we want. Luckily, the secret vector is already small.
We also need the error vector `e` to be small as well in the equation `B = As + e`. So let's construct a lattice with `s||e` as a small vector (here `||` denotes concatenation)!

First, we convert LWE into BDD. We have a natural choice for the target vector: `B`. We want a lattice such that `s||e` is the closest vector to `b`. Luckily, we have an equation that relates `s||e` to `b`:
`b = As + e mod q` or equivalently, `b = As + e - cq` where c is some vector.

To make this lattice, we write the block matrix:
```
[   I  -A^T   ] 
[   0   qI    ]
```
(we take the transpose since it's easier to work with row vectors)

All the points in the lattice are of the form `As + e - cq`, so the closest vector to `b` in our lattice will be `(s||e)` (

This means we have a BDD problem now!

Now we convert to uSVP using Kannan's embedding. We add an extra dimension to our lattice, giving
```
[   I   -A^T  0    ]
[   0   qI    0    ]
[   0   B^T   1    ]
```
This has `(s||e||1)` as a short vector (can you see why). It turns out that this will be a uniquely short vector.

Once we do that, we can run a lattice reduction algorithm to find `s||e||1`. The two main algorithms are LLL, which runs in polynomial time but is not as powerful, and BKZ, which doesn't run in polynomial time and is more powerful.
Either one works for our lattice (I opted for BKZ since I knew it was more likely to succeed, and the parameters are small enough that it runs quickly. I suspect most people used LLL though).

In Sage code:

```python
# Before running this solve script, make a file called output.sage that wraps the matrices in the output with matrix( )
load("output.sage")

q = 2**16
n = 64

AT = A.transpose()

kannan_embedding = block_matrix([[identity_matrix(ZZ, n), -AT,                        zero_matrix(n,1)],
                                 [zero_matrix(n, n),      q*identity_matrix(ZZ, n),   zero_matrix(n,1)],
                                 [zero_matrix(1, n),      B.transpose(),              identity_matrix(1)]])                              


solution = kannan_embedding.BKZ(block_size=20)

se = list(solution[0])

s = matrix(se[:n]).transpose()

# Decryption functions 
def decode_msg(msg):
    hex_vals = ""
    for entry in msg:
        val = entry[0]
        val = round(val * (2**4 / q) ) % (2**4)
        hex_vals += '0123456789abcdef'[val] # lazy way to convert to a single hex digit
    return hex_vals


def decrypt():
    msg = (V - B_prime*s) % q
    return decode_msg(msg)

print(decrypt()) # prints flag in hex
```

Once we have s, it's just a matter of decrypting the same way as described above.

Flag: `UMDCTF{c@teRp15_U53d_BKZ!}`


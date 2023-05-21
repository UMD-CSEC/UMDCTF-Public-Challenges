# Noisy Bits:

We're given a Python script that looks like this: 

```python
import random

POLY = 0xC75
FLAG_BIN_LENGTH = 360

def encode(cw):
    cw = (cw & 0xfff)
    c = cw
    for i in range(1, 12+1):
        if cw & 1 != 0:
            cw = cw ^ POLY
        cw = cw >> 1

    return (cw << 12) | c


flag = open('flag.txt', 'rb').read()

binary_str = bin(int.from_bytes(flag))[2:].zfill(FLAG_BIN_LENGTH)

blocks = [ ''.join([binary_str[12*i+j] for j in range(12)]) for i in range(FLAG_BIN_LENGTH // 12) ]
block_nos = [ int(s, 2) for s in blocks ]

encoded = [ encode(cw) for cw in block_nos ]

# flip some bits for fun
for i in range(len(encoded)):
    encoded[i] = encoded[i] ^ (1 << random.randint(0,22))
    encoded[i] = encoded[i] ^ (1 << random.randint(0,22))
    encoded[i] = encoded[i] ^ (1 << random.randint(0,22))

encoded_bin = [ bin(e)[2:].zfill(23) for e in encoded ]

print(' '.join(encoded_bin))
```

There are two points of interest here: the `encode()` function and the bit flipping near the end.
There's also a hint in the challenge description: "I think I'm gonna Go lay down."

Between the noise added after the encoding and the words "Go lay", you could possibly deduce that the encode function is a [Golay code](https://en.wikipedia.org/wiki/Binary_Golay_code) - a type of error-correcting code. 
Specifically, it's a perfect Golay code, which you can tell from the fact that the encoded blocks are 23 bits long, rather than 24 (for an extended Golay code).

The key property of a Golay code is that it's capable of correcting up to 3 bit flip errors. Since there are at most three bit flips in every codeword, we have enough information to recover the flag!

So how do we decode it? The original 12-bit block is stored in the lowest 12 bytes of the codeword, but some of those bits may be flipped.
There are clever ways to quickly reverse the encoding with even noise: you can read about how to do it [here](http://aqdi.com/articles/using-the-golay-error-detection-and-correction-code-3/)

However, what I ultimately did for my solve script was simply brute-force each codeword. Each codeword is at most 3 bit flips (ie. Hamming distance of 3) away from a valid codeword. So we can just generate 
all 2^12 codewords, then for each block in the output find the unique codeword that is 3 or less bitflips away from the actual block. Here's my script to do this:

```python

POLY = 0xC75


codewords = [0b01011100111010101110100,0b10111111010110100001100,0b00011010110011000110100,0b10000000111010101100110,0b10111011111000110110110,0b00001000110111100110000,0b10000010101001110010011,0b11001001000010101110001,0b10011100110010111010010,0b11100110111011101101010,0b01111111110001101001110,0b00000001011111001101100,0b10101101111000110110110,0b11011001100010000011101,0b10011100111011111010010,0b11001011100010101110010,0b11110001101000100110001,0b01111010100111110101100,0b00101001110001000000111,0b11101100000000001111111,0b11000010011010000000101,0b10101110001111100110000,0b10111111110011100000011,0b01101010101000001100010,0b01101011100000011000110,0b00101010010000101001101,0b11111011011010011110011,0b11100100100110001011110,0b10110111101011101010111,0b11010010000110100001010]

def golay(cw):
    cw = (cw & 0xfff)
    c = cw
    for i in range(1, 12+1):
        if cw & 1 != 0:
            cw = cw ^ POLY
        cw = cw >> 1

    return (cw << 12) | c

def hamming_dist(x, y):
    s1 = bin(x)[2:].zfill(23)
    s2 = bin(y)[2:].zfill(23)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

valid_words = {}

for i in range(0, 2**12):
    valid_words[golay(i)] = i

# This is highly inefficient, but it works.
for cw in codewords:
    for k in valid_words.keys():
        if hamming_dist(cw, k) <= 3:
            print(bin(valid_words[k])[2:].zfill(12))


```

Not the most elegant solution, but it still runs quick enough.

This outputs the original blocks in binary, which can then be popped into a decoder of your choice to get the flag: `UMDCTF{n0i5y_ch4nn3l5_ar3_n0t_@_pr0bleM_4_u}`


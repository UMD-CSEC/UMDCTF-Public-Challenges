from Crypto.Util import number
import gmpy

def nth_root(x, n):
    gs = gmpy.mpz(x)
    g3 = gmpy.mpz(n)
    mask = gmpy.mpz(0x8080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808080808000)
    test = 0
    while True:
      if test == 0:
       gs = gs
      root,exact = gs.root(g3)
      if (root & mask).bit_length() < 8:
        break
    return int(root)

ciphertext = int(open('ciphertext', 'r').read())
public_key = open('public_key', 'r').read().split(":")
n = int(public_key[0])
e = int(public_key[1])
plaintext = nth_root(ciphertext, e)
plaintext_string = number.long_to_bytes(plaintext)[0:-1]
print(plaintext_string)

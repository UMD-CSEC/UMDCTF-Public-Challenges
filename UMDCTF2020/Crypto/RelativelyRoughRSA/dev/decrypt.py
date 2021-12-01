import numpy as np
from Crypto.Util import number

def isqrt(n):
  x = n
  y = (x + n // x) // 2
  while y < x:
    x = y
    y = (x + n // x) // 2
  return x

def fermat(n):
    a = isqrt(n)
    b2 = a*a - n
    b = isqrt(n)
    count = 0
    while b*b != b2:
        a = a + 1
        b2 = a*a - n
        b = isqrt(b2)
        count += 1
    p=a+b
    q=a-b
    return p, q

def egcd(a, b):
    x, lastX = 0, 1
    y, lastY = 1, 0
    while (b != 0):
        q = a // b
        a, b = b, a % b
        x, lastX = lastX - q * x, x
        y, lastY = lastY - q * y, y
    return (lastX, lastY)

def find_primes(ciphertext, n, e):
    p, q = fermat(n)
    decrypt(ciphertext, p, q, e)

def decrypt(ciphertext, p, q, e):
  e //= 2
  n = p * q
  phi = (p - 1) * (q - 1)
  d, _ = egcd(e, phi)
  d %= phi
  rabin_ciphertext = pow(ciphertext, d, n)
  mp = pow(rabin_ciphertext, (p + 1) // 4, p)
  mq = pow(rabin_ciphertext, (q + 1) // 4, q)
  yp, yq = egcd(p, q)

  plaintexts = []
  r1 = (yp * p * mq + yq * q * mp) % n
  r2 = n - r1
  r3 = (yp * p * mq - yq * q * mp) % n
  r4 = n - r3
  plaintexts.append(r1)
  plaintexts.append(r2)
  plaintexts.append(r3)
  plaintexts.append(r4)

  for plaintext in plaintexts:
      plaintext_string = number.long_to_bytes(plaintext)
      if plaintext_string[:6] == b'UMDCTF':
          zero_index = plaintext_string.index(b'\x00')
          print(plaintext_string[:zero_index].decode('utf-8'))
          return True
  print("Not found")
  return False

ciphertext = int(open('ciphertext', 'r').read())
public_key = open('public_key', 'r').read().split(":")
n = int(public_key[0])
e = int(public_key[1])
find_primes(ciphertext, n, 0xcbfe)

#!/usr/bin/env python3

from Crypto.Util.number import *
import math

plaintext = "UMDCTF-{Sh4r1ng_I5_d3f1n1t3ly_n0t_c4r!ng}"
p = getPrime(2048)
q = getPrime(2058)
n = p*q
e1 = 65537
e2 = 65541
phi = (p-1)*(q-1)

print(plaintext)
plaintext = bytes_to_long(plaintext.encode())
print(plaintext)

c1 = pow(plaintext, e1, n)
c2 = pow(plaintext, e2, n)
print("n = {}\ne1 = {}\ne2 = {}\nc1 = {}\nc2 = {}\n".format(n, e1, e2, c1, c2))


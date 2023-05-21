from pwn import *
from Crypto.Util.number import long_to_bytes as l2b, bytes_to_long as b2l, isPrime, inverse
import random

r = remote('127.0.0.1', 60003)

# get params
n = int(r.recvuntil(b'\n').strip().split(b':')[1].strip().decode(), 16)
e = int(r.recvuntil(b'\n').strip().split(b':')[1].strip().decode(), 16)
flag_ct = int(r.recvuntil(b'\n').strip().split(b':')[1].strip().decode(), 16)
print(f'n: {hex(n)}\ne: {hex(e)}\nflag_ct: {hex(flag_ct)}')
r.recvuntil(b'(hex): ')

# pick a random message that results in prime ct
while True:
    m_rand = random.randrange(0,n)
    ct = pow(m_rand, e, n)
    ct_prime = (flag_ct * ct) % n
    if isPrime(ct_prime):
        # send to oracle and exit loop
        print(f'm\' = {m_rand}')
        r.send(f'{hex(ct_prime)}\n'.encode())
        break

r.recvuntil(b'result: ')
res = r.recvuntil(b'\n').strip().decode()
if res in ['invalid', 'null']:
    print(f'rip: {res}')
else:
    res = int(res, 16)
    inv = inverse(m_rand, n)
    flag = l2b((inv * res) % n)
    if b'UMDCTF' in flag:
        print(flag.decode()) 
    else:
        print(f'hmmm: {flag}')


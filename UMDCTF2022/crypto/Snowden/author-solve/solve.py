from pwn import *
import gmpy
import gmpy2
from Crypto.Util.number import long_to_bytes, bytes_to_long

r = remote('127.0.0.1', 60001)

n_arr = []
c_arr = []
e = 21

print(r.recv().decode())
while len(n_arr) < e:
    r.send('y\n'.encode())
    stuff = r.recv().decode().split('\n')[0]
    n = int(stuff.split("'n': ")[1].split(',')[0])
    e = int(stuff.split("'e': ")[1].split(',')[0])
    c = int(stuff.split("'c': ")[1].split('}')[0])
    if e == 21:
        n_arr.append(n)
        c_arr.append(c)
        print("appended")
    else:
        print(f'e = {e}')

#print(f'n_arr = {n_arr}')
#print(f'c_arr = {c_arr}')

N = 1
for n in n_arr:
    N *= n

print(f'N = {N}')

N_arr = []
for i in range(e):
    N_curr = 1
    for n_i in range(len(n_arr)):
        if n_i != i:
            N_curr *= n_arr[n_i]
    N_arr.append(N_curr)

#print(f'N_arr = {N_arr}')

u_arr = []
for i in range(len(n_arr)):
    u_arr.append(gmpy.invert(N_arr[i], n_arr[i]))

#print(f'u_arr = {u_arr}')

p = 0
for i in range(len(n_arr)):
    p += c_arr[i]*u_arr[i]*N_arr[i]

#print(f'p = {p}')

p = p % N
print(p)
m = gmpy.root(p,e)[0]
print(m)
pt = long_to_bytes(m)
print(pt)

# creds: https://bitsdeep.com/posts/attacking-rsa-for-fun-and-ctf-points-part-2/

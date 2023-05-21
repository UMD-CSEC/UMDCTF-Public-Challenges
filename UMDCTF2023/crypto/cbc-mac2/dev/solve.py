from pwn import *
from binascii import hexlify, unhexlify
from Crypto.Util.strxor import strxor
from Crypto.Util.number import long_to_bytes as l2b

def mac_query(msg, i):
    r.recvuntil(b'Choice: ')
    r.send(b'1\n')
    r.recvuntil(b'(hex): ')
    r.send(msg + b'\n')
    t = r.recvuntil(b'\n').split(b':')[1].strip()
    print(f'm{i} = {msg.decode()}\nt{i} = {t.decode()}')
    return t

BS = 16 # Block Size
addr = '127.0.0.1'
port = 60002

r = remote(addr, port)

# Query Messages
m1 = hexlify(b'\x00'*BS + b'\xff'*BS + l2b(2, BS) + b'\x00'*BS + b'\xff'*BS)
t1 = mac_query(m1, 1)

m2 = hexlify(b'\x00'*BS + b'\xff'*BS)
t2 = mac_query(m2, 2)

m3 = hexlify(b'\x00'*BS*2)
t3 = mac_query(m3, 3)


# FORGERY
m_prime = hexlify(b'\x00'*BS*2 + l2b(2, BS) + strxor(unhexlify(t2), unhexlify(t3)) + b'\xff'*BS)
#m_prime = hexlify(b'\x00'*BS*2 + l2b(2, BS) + unhexlify(t2) + b'\xff'*BS)
#print(f'strxor = {strxor(t2, t3)}')
r.recvuntil(b'Choice: ')
r.send(b'2\n')
r.recvuntil(b'(hex): ') # msg
r.send(m_prime + b'\n')
r.recvuntil(b'(hex): ') # tag
r.send(t1 + b'\n') # same tag
print(r.recv(1024).decode())
r.close()



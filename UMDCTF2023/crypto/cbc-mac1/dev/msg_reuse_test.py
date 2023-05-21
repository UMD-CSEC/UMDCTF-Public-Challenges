from pwn import *
from binascii import hexlify, unhexlify

BS = 16 # Block Size
addr = '127.0.0.1'
port = 60001

r = remote(addr, port)

# CBC-MAC query
msg = hexlify(b'\x00'*BS)
r.recvuntil(b'Choice: ')
r.send(b'1\n')
r.recvuntil(b'(hex): ')
r.send(msg + b'\n')
tag = r.recvuntil(b'\n').split(b':')[1].strip()
print(f'msg = {msg.decode()}\ntag = {tag.decode()}')

# FORGERY
msg_prime = msg
r.recvuntil(b'Choice: ')
r.send(b'2\n')
r.recvuntil(b'(hex): ') # msg
r.send(msg_prime + b'\n')
r.recvuntil(b'(hex): ') # tag
r.send(tag + b'\n') # same tag
print(r.recvuntil(b'\n').decode())
r.close()



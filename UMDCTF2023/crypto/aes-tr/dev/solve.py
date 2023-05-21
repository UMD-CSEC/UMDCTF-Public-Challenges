from pwn import *
from binascii import hexlify, unhexlify

BS = 16 # Block Size
addr = '127.0.0.1'
port = 60000

r = remote(addr, port)

m0 = b''
for i in range(1,7):
    m0 += bytes([0]*15 + [i])
m0 = hexlify(m0)
m1 = hexlify(b'\x00'*16*6)
times = 128 + 1

for i in range(1, times):
    #print(f'Bit {i}')
    
    # Encryption Query
    r.recvuntil(b'Choice: ') 
    r.send(b'1\n')
    r.recvuntil(b'(hex): ')
    r.send(m0 + b'\n')
    r.recvuntil(b'(hex): ')
    r.send(m1 + b'\n')
    ct = unhexlify(r.recvuntil(b'\n').split(b': ')[1].strip())
    ct_blocks = [ct[i:i+BS] for i in range(0, len(ct), BS)]

    b = 1
    if len(list(set(ct_blocks[1:]))) < len(ct_blocks[1:]):
        b = 0
    
    # Send bit guess
    r.recvuntil(b'Choice: ')
    r.send(b'2\n')
    r.recvuntil(b'guess: ')
    r.send(f'{b}\n'.encode())
    print(r.recvuntil(b'\n').decode() + '\n')

print(r.recvuntil(b'\n').decode())


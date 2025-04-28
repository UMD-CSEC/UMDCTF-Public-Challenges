from pwn import *
#context.log_level = 'debug'
with process("./tripledes.py") as r:
	r.readuntil(b": ")
	enc_flag = bytes.fromhex(r.readline(False).decode())

	from string import printable
	pairs = [enc_flag[i:i+32] for i in range(0,len(enc_flag)-32,8)]
	def xor(a,b): return bytearray([i^j for i,j in zip(a,b)])
	def test(s):
		r.sendlineafter(b"valid!\n", s.hex().encode())
		return r.readline(False) == b"yes"
	for p in pairs:
		iv = bytearray(p[:24])
		want = bytearray(24)
		have = bytearray(24)
		ct = bytearray(p[24:])
		for i in range(8):
			for t in printable.encode():
				for j in range(i+1): want[7-j] = i+1
				have[7-i] = t
				if test(xor(xor(iv, want), have) + ct):
					break
			else:
				print("oh no")
		print(have[:8])
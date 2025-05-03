class NumericRand:
	def __init__(self, state):
		self.rng = self._numeric_random()
		self.state = [int(''.join(map(str, state[i*32:i*32+32])), 2) for i in range(624)]
	
	def _numeric_random(self):
		N = 624
		M = 397
		index = 0
		while 1:
			if index >= N:
				for kk in range(N):
					y = (self.state[kk]&0x80000000) | (self.state[(kk+1)%N]&0x7fffffff)
					self.state[kk] = (self.state[(kk+M)%N] ^^ (y >> 1) ^^ ((y & 1) * 0x9908b0df)) & 0xffffffff
				index = 0
			y = self.state[index]
			index += 1
			y ^^= (y >> 11) & 0xffffffff
			y ^^= (y << 7) & 0x9d2c5680
			y ^^= (y << 15) & 0xefc60000
			y ^^= (y >> 18) & 0xffffffff
			yield y & 0xffffffff
	
	def set_state(state):
		self.state = state[:624]
	
	def predictrand_uint32(self):
		return next(self.rng)

class SymbolicRand:
	def __init__(self):
		self.rng = self._symbolic_random()
	
	def _ZERO(self): return zero_vector(GF(2), 32*624)
	def _AND(self, a, b): return [a[s] if ((b<<s) & 0x80000000) else self._ZERO() for s in range(32)]
	def _LSH(self, a, b): return a[b:] + [self._ZERO() for i in range(b)]
	def _RSH(self, a, b): return [self._ZERO() for i in range(b)] + a[:-b]
	def _XOR(self, *args): return [sum(i, self._ZERO()) for i in zip(*args)]
	def _XOR_in_place(self, a, b):
		for i in range(32): a[i] += b[i]
	def _MAGIC(self, a, b): return [a[31] if ((b<<s) & 0x80000000) else zero_vector(GF(2), 32*624) for s in range(32)]
	
	def _symbolic_random(self):
		N = 624
		M = 397
		mt = list(identity_matrix(GF(2), 32*N))
		index = 0
		while 1:
			if index >= N:
				for kk in range(N):
					y = mt[kk*32:][:1] + mt[(kk+1)%N*32:][1:32]
					mt[kk*32:(kk+1)*32] = self._XOR(mt[(kk+M)%N*32:][:32], self._RSH(y, 1), self._MAGIC(y, 0x9908b0df))
				index = 0
			y = mt[index*32:][:32]
			index += 1
			self._XOR_in_place(y, self._RSH(y, 11))
			self._XOR_in_place(y, self._AND(self._LSH(y, 7), 0x9d2c5680))
			self._XOR_in_place(y, self._AND(self._LSH(y, 15), 0xefc60000))
			self._XOR_in_place(y, self._RSH(y, 18))
			yield y
	
	def genrand_uint32(self):
		return next(self.rng)


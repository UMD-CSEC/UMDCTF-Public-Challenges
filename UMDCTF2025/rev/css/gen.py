import string, random, functools, json

CELL_SIZE = 4

with open("code.asm") as f:
	instructions = f.read().strip().splitlines()

with open("flag.txt") as f:
	flag = f.read().strip()


tapemap = {}
random.seed(0x678ad215ab47761db34f844fc5801dca)
with open("cache.json") as f:
	oldcache = json.load(f)
cache = {}
seen = set()
hit = set()
def random_name(n = None):
	if n is not None and n in cache:
		hit.add(n)
		return cache[n]
	while 1:
		prefix = ["subway-", "surfer-"][random.randint(0, 1)]
		name = prefix + hex(random.getrandbits(24))[2:]
		if name not in seen:
			seen.add(name)
			if n is not None:
				cache[n] = name
				if oldcache[n] != cache[n]: print("mismatch", n)
			return name
tape_template = f"""<div class="{random_name('tape')}" id="%s"%s>%s%s</div>"""

class Tape:
	def __init__(self, name, size, read_only=False):
		self.name = random_name(name)
		self.link = random_name(self.name)
		random_name(name)
		random_name(self.name)
		self.size = size
		n_shifts = (self.size - 1).bit_length()
		self.shifts = n_shifts
		self.ro = read_only
		tapemap[name] = self
		
	def html(self):
		total_shift = 2**self.shifts - 1
		shifts = []
		for i in range(self.shifts):
			shifts.append(f'<div class="{random_name("rshift")}" h="{CELL_SIZE<<i}"></div>')
		tshift = ''
		if total_shift:
			tshift = f' style="margin-top:calc({total_shift * CELL_SIZE} * var(--nsize))"'
		cell_html = f'<div class="{random_name("t-cell")}"><div class="{random_name("w0")}"></div><div class="{random_name("w1")}"></div><div class="{random_name("cover")}"></div></div>'
		if self.ro:
			cell_html = f'<div class="{random_name("t-cell")}"><div class="{random_name("covr")}"></div></div>'
		return tape_template % (self.name, tshift, "".join(shifts), cell_html * (self.size * CELL_SIZE))

rom = Tape("rom", 300, read_only=True)

mem = Tape("mem", 128)

flags = Tape("flags", 1)

modps = [
	Tape("t0", 32),
	Tape("t2", 32),
	Tape("t4", 32),
	Tape("t6", 32),
	Tape("t8", 32),
	Tape("t10", 32),
	Tape("t12", 32),
	Tape("t14", 32)
]

tapes = [
	Tape("p1", 1),
	Tape("p2", 1),
	Tape("p3", 1),
	Tape("r1", 1),
	Tape("r2", 1),
	Tape("r3", 1),
	Tape("r4", 1),
	Tape("r5", 1),
	Tape("r6", 1),
	Tape("r7", 1),
	Tape("r8", 1),
	Tape("r9", 1),
	Tape("r10", 1),
	Tape("r11", 1),
	Tape("r12", 1),
	Tape("r13", 1),
	Tape("r14", 1),
	Tape("r15", 1),
	Tape("acc", 32),
	*modps,
	rom,
	mem,
	flags,
]

opmap = {}

class Op:
	def __init__(self, name, gen=None, flags=None, jump=False, offset=None, block=False, unblock=False, has_dst=True, jumps=None):
		self.name = random_name(name)
		self.link = random_name(self.name)
		random_name(name)
		random_name(self.name)
		self.gen = gen
		self.flags = flags
		self.jump = jump
		self.offset = offset
		self.block = block
		self.unblock = unblock
		self.has_dst = has_dst
		self.no_table = gen is None
		opmap[name] = self
	def html(self):
		if self.no_table: return ''
		table = []
		for i in range(1 << CELL_SIZE):
			for j in range(1 << CELL_SIZE):
				res = self.gen(i, j)
				attrs = "".join(" " + random_name("res" + str(1 << k)) for k in range(CELL_SIZE) if res & (1 << k))
				if self.jump:
					attrs = f' class="{random_name("ajump")}"' if res else ''
				if self.offset:
					offset, shift = self.offset
					if offset is modps:
						attrs = "".join(f" {random_name(f'{offset[res >> 5].link}-{shift + k}')}" for k in range(5) if res & (1 << k))
					else:
						attrs = "".join(f" {random_name(f'{offset.link}-{shift + k}')}" for k in range(offset.shifts) if res & (1 << k))
				if self.flags:
					res = self.flags(i, j)
					attrs += "".join(f" {random_name(f'{flags.link}-{k}')}" if res & (1 << k) else f" {random_name(f'{flags.link}-n{k}')}" for k in range(CELL_SIZE))
				table.append(f'<div{attrs}></div>')
		return f'<div class="{random_name("optable")}" id="{self.name}">{"".join(table)}</div>'

prng_table = list(range(256))
random.seed(110495220192904012260259857295472515749)
while 1:
	random.shuffle(prng_table)
	if all(i!=prng_table[i] for i in range(256)): break

spine1 = [12, 2, 4, 12, 5, 13, 15, 12, 12, 8, 2, 8, 11, 4, 14, 2, 2, 4, 5, 6, 13, 12, 3, 3, 12, 11, 7, 14, 7, 4, 1, 5, 8, 1, 14, 13, 11, 9, 7, 13, 2, 7, 11, 8, 13, 9, 14, 8, 9, 2, 4, 10, 12, 10, 11, 13, 14, 8, 2, 5, 2, 9, 12, 15, 4, 13, 11, 3, 5, 1, 8, 9, 3, 4, 7, 6, 9, 4, 8, 6, 5, 13, 13, 9, 15, 8, 15, 5, 2, 11, 8, 8, 15, 8, 9, 3, 1, 6, 1, 7, 6, 15, 12, 2, 3, 13, 9, 10, 2, 3, 13, 4, 13, 2, 15, 2]
spine2 = [0, 11, 3, 7, 5, 10, 5, 9, 2, 10, 3, 4, 13, 13, 0, 15, 15, 14, 6, 10, 10, 15, 1, 5, 3, 7, 12, 4, 4, 14, 14, 13, 6, 13, 5, 10, 13, 14, 2, 11, 8, 6, 1, 14, 11, 4, 9, 13, 6, 3, 8, 10, 10, 7, 0, 5, 7, 13, 9, 5, 15, 5, 12, 15, 3, 1, 8, 4, 0, 10, 4, 13, 9, 2, 4, 2, 11, 0, 5, 7, 12, 15, 11, 14, 15, 15, 1, 4, 15, 2, 13, 6, 10, 10, 8, 13, 2, 13, 3, 2, 11, 4, 6, 10, 15, 2, 14, 7, 10, 7, 9, 0, 4, 5, 1, 10]
spine1[22] ^= 1
operations = [
	Op("rld1", lambda x,y: x + (y << CELL_SIZE), offset=(rom, 0), block=True, has_dst=False),
	Op("rld2", lambda x,y: x, offset=(rom, CELL_SIZE*2), block=True, has_dst=False),
	Op("mld1", lambda x,y: x + (y << CELL_SIZE), offset=(mem, 0), block=True, has_dst=False),
	Op("mpld", lambda x,y: x + (y << CELL_SIZE), offset=(modps, 0), block=True, has_dst=False),
	Op("pset", lambda x,y: ({0: 1, 32: 0, 64: 3, 96: 1, 68: 10, 85: 11, 204: 4, 221: 12, **{48+i: int(bin(i)[2:].zfill(4)[::-1],2) for i in range(16)}}).get((x<<CELL_SIZE) + y, random.getrandbits(CELL_SIZE))),
	Op("prng", lambda x,y: prng_table[x + (y << CELL_SIZE)] & 0xf, flags = lambda x,y: prng_table[x + (y << CELL_SIZE)] >> CELL_SIZE),
	Op("ublk", unblock=True),
	Op("and", lambda x,y: x & y, flags = lambda x,y: int(x > y)),
	Op("add", lambda x,y: x + y, flags = lambda x,y: int(x + y >= 16)),
	Op("sub", lambda x,y: x - y),
	Op("addnf", lambda x,y: x + y),
	Op("xor", lambda x,y: x ^ y),
	Op("add1", lambda x,y: x + 1, flags = lambda x,y: int(x + 1 >= 16)),
	Op("add2", lambda x,y: x + 2),
	Op("add10", lambda x,y: x + 10),
	Op("sub1", lambda x,y: (x - 1) % (1 << CELL_SIZE)),
	Op("shl1", lambda x,y: (x << 1) | y, flags = lambda x,y: int(x >= 8)),
	Op("mov", lambda x,y: x),
	Op("ham", lambda x,y: bin(x).count('1') + bin(y).count('1')),
	Op("ext6", lambda x,y: ((x >> y) & 1) * 6),
	Op("jl", lambda x,y: x < y, jump=True),
	Op("jg", lambda x,y: x > y, jump=True),
	Op("jge", lambda x,y: x >= y, jump=True),
	Op("jle", lambda x,y: x <= y, jump=True),
	Op("je", lambda x,y: x == y, jump=True),
	Op("jne", lambda x,y: x != y, jump=True),
	Op("jsl", lambda x,y: x == 7 and y == 14 or x >= 8 and random.random() < 0.06, jump=True),
	Op("jmp"),
	Op("cff", lambda x,y: y < len(expect4) and x != expect4[y], jump=True),
	Op("lsc", lambda x,y: spine1[(x + (y<<CELL_SIZE))//2] if (x + (y<<CELL_SIZE)) <= len(expect4_2) and x % 2 == 1 else random.getrandbits(CELL_SIZE), flags = lambda x,y: spine2[(x + (y<<CELL_SIZE))//2] if (x + (y<<CELL_SIZE)) <= len(expect4_2) and x % 2 == 1 else random.getrandbits(CELL_SIZE)),
	Op("halt"),
]

class Instruction:
	def __init__(self, addr, op, args):
		self.addr = addr
		self.op = op
		self.args = args
	def __repr__(self): return f"{self.addr}: {self.op}, {self.args}"
	def html(self):
		if self.op == "halt":
			return f'<div class="{random_name("instruction")}"><div class="{random_name("halt")}" show="{self.args[0]}"></div></div>'
		
		oplink = opmap[self.op].link
		attrs = ''
		if not opmap[self.op].no_table: attrs += f' {random_name("op")}="{oplink}"'
		if opmap[self.op].block: attrs += f" {random_name('block')}"
		if opmap[self.op].unblock: attrs += f" {random_name('unblock')}"
		jump = None
		op_elements = []
				
		for i in range(len(self.args)):
			arg = self.args[(i + 1) % len(self.args)] # leave dst for last
			if not opmap[self.op].has_dst and i == len(self.args) - 1:
				break
			if "+" in arg:
				arg, off = arg.split("+")
				offset = int(off)
				tape = tapemap[arg]
				attrs += "".join(f" {random_name(f'{tape.link}-{i}')}" for i in range(tape.shifts) if offset & (1 << i))
			if arg in tapemap:
				attrs += f' {random_name(f"p{i+1}")}="{tapemap[arg].link}"'
				op_elements.append(f'<div class="{random_name("setup")}"{attrs}></div>')
				attrs = ''
			elif arg in labels:
				jump = labels[arg]
			elif arg == "~~":
				op_elements.append(f'<div class="{random_name("setup")}"{attrs}></div>')
			else:
				print("unknown arg", arg)
			
			if opmap[self.op].no_table:
				# output a single jump
				op_elements = []
				if self.op == "jmp":
					self.addr, jump = jump - 1, None
				break
		offsets = "".join(f" {random_name(f'jmp{i}')}" if (p[self.addr+1]) & (1 << i) else f" {random_name(f'njmp{i}')}" for i in range(code_n_shifts))
		jump_element = f'<div class="{random_name("jump")}"{offsets}{attrs}></div>'
		jump_element2 = ''
		if jump is not None:
			offsets = "".join(f" {random_name(f'jmp{i}')}" if p[jump] & (1 << i) else f" {random_name(f'njmp{i}')}" for i in range(code_n_shifts))
			jump_element2 = f'<div class="{random_name("jump")} {random_name("alt")}"{offsets}></div>'
		return f'<div class="{random_name("instruction")}">{"".join(op_elements)}{jump_element}{jump_element2}</div>'

labels = {}
code = []
rom_1bits = []
for i in instructions:
	if ';' in i: i = i[:i.index(';')]
	if not i.strip(): continue
	if i.strip().startswith('.rom'):
		_, offset, value = i.split()
		offset = int(offset)
		value = int(value)
		for j in range(4):
			if value & (1 << j):
				rom_1bits.append(offset * 4 + j)
		continue
	op, *rest = i.strip().split(maxsplit=1)
	if op.endswith(":"):
		labels[op[:-1]] = len(code)
	else:
		if rest:
			args = rest[0]
			args = [i.strip() for i in args.strip().split(",")]
		else: args = []
		code.append(Instruction(len(code), op, args))

p = list(range(len(code)))
random.shuffle(p)
pz = p.index(0)
p[0], p[pz] = p[pz], p[0]
newcode = [None] * len(code)
for i,instruction in enumerate(code):
	newcode[p[i]] = instruction
code = newcode

qrom = 74991407119409573653134810242842117674 ^ 3
idx = 32*4
while qrom:
	if qrom & 1:
		rom_1bits.append(idx)
	qrom >>= 1
	idx += 1

row = []
col = []
shifts = []
results = []
for i in range(CELL_SIZE):
	shifts.append(f'<div class="{random_name("rshift")}" h="{1<<i}"></div>')
for i in range(CELL_SIZE):
	row.append(f'<div class="{random_name("opb")}" id="{random_name(f"row{1<<i}")}"></div>')
	col.append(f'<div class="{random_name("opb")}" id="{random_name(f"col{1<<i}")}"></div>')
	shifts.append(f'<div class="{random_name("shift")}" w="{1<<i}"></div>')
	results.append(f'<div class="{random_name("res")}" r="{i+1}"></div>')

codeshifts = []
code_n_shifts = (len(code) - 1).bit_length()
total_shift = 2**code_n_shifts - 1
for i in range(code_n_shifts):
	codeshifts.append(f'<div class="{random_name("cshift")}" h="{1<<i}"></div>')

flag_inner = flag[7:-1]
format_idxs = list(range(7)) + [len(flag) - 1]
inputs = []

styles = []
rootstyles = []
charstyles = []

alpha = list(string.printable.strip().encode())

random.seed(0x62dcb0ee8ca15d83de82c8e895509c23)
charbits = []
for i in range(len(flag_inner)):
	bits = list(range(128))
	random.shuffle(bits)
	charbits.append(bits[:len(alpha)])

for i in range(len(flag)):	
	options = []
	for idx,j in enumerate(alpha):
		attrs = ''
		value = j
		if i not in format_idxs:
			value = charbits[i-7][idx]
		for bit in range(7):
			if value & (1 << bit): attrs += " " + random_name(f"b{i}-{bit}")
		if i < 7 and j == ord(flag[i]): attrs += " selected"
		options.append(f"<option value='{idx:x}'{attrs}>&#x{j:02x};</option>")
	inputs.append(f"<select>{''.join(options)}</select>")
	for bit in range(7):
		rootstyles.append(" --" + random_name(f"--b{i}-{bit}") + ": 0;")
		charstyles.append("body:has(option[" + random_name(f"b{i}-{bit}") + "]:checked) { --" + random_name(f"--b{i}-{bit}") + ": 1; }")

styles.append(":root{" + "".join(rootstyles) + "}")
styles.extend(charstyles)

# 56 linearly independent 56-bit vectors
lc = [0xdc2ae386cd353b,0x21cf1a25c08c08,0xae5f9777ba539,0x1f482113cb550,0xe7547b52d7fd38,0x966f8e4bc7aca4,0xeb196d46283048,0x548604625aa9f8,0x51c48c02436e9f,0xc9b66a1afeb917,0xc00ffbffff004b,0x3afa70151cb1cc,0xcec04ccb7a6f8d,0xf7eea45f784265,0x3f244404fd4c01,0x92c447cb3d1923,0x3457a6a66e278b,0x58cf10dbcea990,0x944b0271171864,0xad8ea74066f7e,0x30f24f8606362d,0x5d1b4cab70e235,0xd7c93868cacfe2,0x8d441ca4d42141,0x972dca3abd5e2e,0xa79b6425dee2ce,0xe3306a990168fd,0xb1b01180b99548,0x5ae8790f9140d,0x8b90757181d82b,0x58f404635ed639,0x899eb0483a308,0xa3c839f68e7680,0x3c6b499174f094,0x61fcebfc99d697,0x12fc190f8df125,0x53e63483fcdd47,0xfedf794026e80f,0x2a73937fbc605f,0x65cc53c92d19e1,0x8944e7e7efc34,0x752e0cca1e3464,0xe298cbd8685b35,0xe5af4ceffe1a8e,0x505b2802dcff01,0x882ebd0e4e1522,0x6f16c32d30d3b9,0x1cd21ce99445c3,0xcfba3e3b7dc7b0,0xcbdbf7ea8cde79,0x188e003a65433d,0x648497efdee6b0,0xb01496eb0e58f8,0xa98f164a1a6165,0x1b6fe2cadc181,0x92ea9c82aeba1e]

romstyles = []
expected = []

for i in range(len(lc)):
	n = lc[i]
	s = []
	expect = 0
	for j in range(len(format_idxs)):
		c = ord(flag[format_idxs[j]])
		for k in range(7):
			if n & (1 << (j*7 + k)):
				s.append(f"var(--{random_name(f'--b{format_idxs[j]}-{k}')})")
				expect ^= (c >> k) & 1
	expected.append(expect)
	random.shuffle(s)
	romstyles.append(f"#{random_name('rom')} > .{random_name('t-cell')}:nth-child({i+1+rom.shifts}) > .{random_name('covr')} " + "{ translate: calc(mod(" + " + ".join(s) + ", 2) * var(--nsize)); }")
random.shuffle(romstyles)
styles.extend(romstyles)

from lc2 import lc2
romstyles2 = []
expected2 = []
for i in range(len(lc2)):
	n = lc2[i]
	s = []
	expect = 0
	for j in range(len(flag_inner)):
		c = charbits[j][alpha.index(ord(flag_inner[j]))]
		for k in range(7):
			if n & (1 << (j*7 + k)):
				s.append(f"var(--{random_name(f'--b{j+7}-{k}')})")
				expect ^= (c >> k) & 1
	expected2.append(expect)
	random.shuffle(s)
	romstyles2.append(f"#{random_name('rom')} > .{random_name('t-cell')}:nth-child({i+64*CELL_SIZE+1+rom.shifts}) > .{random_name('covr')} " + "{ translate: calc(mod(" + " + ".join(s) + ", 2) * var(--nsize)); }")
random.shuffle(romstyles2)
styles.extend(romstyles2)

random.shuffle(rom_1bits)
styles.append(f"#{random_name('rom')} > .{random_name('t-cell')}:is(" + ",".join(f":nth-child({i+1+rom.shifts})" for i in rom_1bits) + f") > .{random_name('covr')} " + "{ translate: var(--nsize); } ")

expect4 = [sum(expected[i+j] << j for j in range(4)) for i in range(0, len(expected), 4)]
expect4_2 = [sum(expected2[i+j] << j for j in range(min(4, len(expected2) - i))) for i in range(0, len(expected2), 4)]

cell_html = f"""<div class="{random_name('t-cell')}"><div class="{random_name('w0')}"></div><div class="{random_name('w1')}"></div><div class="{random_name('cover')}"></div></div>"""

template = f"""<!DOCTYPE html>
<html>
<head>
<style>
%s
</style>
</head>
<body>
<div id="{random_name('message')}">keep your cursor in the box</div><div id="{random_name('mouse-here')}"></div><div id="{random_name('program')}"><div id="{random_name('reset1')}" class="{random_name('reset')} {random_name('treset')} {random_name('sreset')}"></div><div id="{random_name('reset2')}" class="{random_name('treset')} {random_name('sreset')}"></div><div id="{random_name('reset3')}" class="{random_name('reset')} {random_name('treset')}"></div><div id="{random_name('reset4')}" class="{random_name('treset')}"></div><div id="{random_name('code')}" style="margin-top: calc({total_shift} * var(--nsize))">{"".join(codeshifts)}%s</div><div id="{random_name('operation')}"><div id="{random_name('oprow')}">{"".join(row)}</div><div id="{random_name('opcol')}">{"".join(col)}</div>{"".join(shifts)}<div id="{random_name('tables')}">%s</div></div>%s<div id="{random_name('result')}">{"".join(results)}</div></div>
<div class="{random_name('catch')}" id="{random_name('catch1')}"></div>
<div class="{random_name('catch')}" id="{random_name('catch2')}"></div>
<div class="{random_name('catch')}" id="{random_name('catch3')}"></div>
<div class="{random_name('catch')}" id="{random_name('catch4')}"></div>
<div class="{random_name('overlay')}" id="{random_name('start')}">
<div class="{random_name('text')}">
<p delay=0>put your cursor in the box.</p>
<p class="{random_name('right')}" delay=1>what's in the box?</p>
<p delay=2>pain.</p>
<div id="{random_name('inp')}">%s</div>
</div>
<button id="{random_name('ok')}" delay=2.5>click here<br><span style="font-size: 9px;">(you may need to hold for a bit if it's laggy)</span></button>
</div>
<div class="{random_name('overlay')}" id="{random_name('success')}">
<div class="{random_name('msg')}">
<p>you win</p>
</div>
</div>
<div class="{random_name('overlay')}" id="{random_name('fail')}">
<div class="{random_name('msg')}">
<p>you fell off</p>
</div>
</div>
<div class="{random_name('overlay')}" id="{random_name('fail2')}">
<div class="{random_name('msg')}">
<p>the gom jabbar plunges into your neck</p>
</div>
</div>
<div class="{random_name('overlay')}" id="{random_name('firefox')}">
<div class="{random_name('msg')}">
<p>firefox is <a href="https://caniuse.com/css3-attr">not supported</a></p>
</div>
</div>
</body>
</html>
"""


LOOP = [
	(0, 0), # reset
	(0, 1), # setup1
	(1, 7), # read src1 bit 1
	(2, 7), # read src1 bit 2
	(3, 7), # read src1 bit 3
	(4, 7), # read src1 bit 4
	(1, 0), # soft reset
	(0, 2), # setup2
	(1, 11), # read src2 bit 1
	(2, 11), # read src2 bit 2
	(3, 11), # read src2 bit 3
	(4, 11), # read src2 bit 4
	(1, 0), # soft reset
	(23, 15), # go to lookup table
	(0, 3), # setup3 (or jump)
	(1, 12), # write 0 to dst bit 1
	(2, 12), # write 0 to dst bit 2
	(3, 12), # write 0 to dst bit 3
	(4, 12), # write 0 to dst bit 4
	(1, 13), # write 1 to dst bit 1
	(2, 13), # write 1 to dst bit 2
	(3, 13), # write 1 to dst bit 3
	(4, 13), # write 1 to dst bit 4
	(0, 4), # jump
]

keyframes = ["@keyframes " + random_name('loop') + " {"]
prevrow, prevcol = None, None
skip = 100 // len(LOOP)
pct = 0
for row, col in LOOP:
	line = str(pct) + "% { "
	if row != prevrow:
		if row == 0:
			line += "top: 0px; "
		elif row == 1:
			line += "top: var(--nsize); "
		else:
			line += f"top: calc({row} * var(--nsize)); "
	if col != prevcol:
		if col == 0:
			line += "left: 0px; "
		elif col == 1:
			line += "left: var(--nsize); "
		else:
			line += f"left: calc({col} * var(--nsize)); "
	line += "}"
	prevrow, prevcol = row, col
	pct += skip
	keyframes.append(line)
keyframes.append("}")

cstyles = [
	",".join([f"""#{random_name('code')}:has(div[{random_name('p1')}="%s"]:hover) ~ #%s""" % (t.link, t.name) for t in tapes]) + " { animation-play-state: running, paused, paused; }",
	",".join([f"""#{random_name('code')}:has(div[{random_name('p2')}="%s"]:hover) ~ #%s""" % (t.link, t.name) for t in tapes]) + " { animation-play-state: paused, running, paused; }",
	",".join([f"""#{random_name('code')}:has(div[{random_name('p3')}="%s"]:hover) ~ #%s""" % (t.link, t.name) for t in tapes]) + " { animation-play-state: paused, paused, running; }",
	",".join([f"""#{random_name('code')}:has(div[{random_name('op')}="%s"]:hover) ~ #{random_name('operation')} #%s""" % (t.link, t.name) for t in operations]) + " { animation-play-state: running; }",
	",".join(sum(([f""":is(#{random_name('code')},#{random_name('operation')}):has(div[{random_name(f'{t.link}-{i}')}]:hover) ~ #{t.name} .{random_name('rshift')}[h="{CELL_SIZE<<i}"]""" for i in range(t.shifts)] for t in tapes if t.name != "flags"), [])) + " { animation-play-state: running; }",
	",".join([f"""#{random_name('operation')}:has(div[{random_name(f'{flags.link}-{i}')}]:hover) ~ #{flags.name} > .{random_name('t-cell')}:nth-child({i+1}) > .{random_name('cover')}""" for i in range(CELL_SIZE)]) + " { animation-play-state: running; }",
	",".join([f"""#{random_name('operation')}:has(div[{random_name(f'{flags.link}-n{i}')}]:hover) ~ #{flags.name} > .{random_name('t-cell')}:nth-child({i+1}) > .{random_name('cover')}""" for i in range(CELL_SIZE)]) + " { animation: none; }",
	",".join([f"""#{random_name('code')}:has(div[{random_name(f'jmp{i}')}]:hover) > .{random_name('cshift')}[h="{1<<i}"]""" for i in range(code_n_shifts)]) + " { animation-play-state: running; }",
	",".join([f"""#{random_name('code')}:has(div[{random_name(f'njmp{i}')}]:hover) > .{random_name('cshift')}[h="{1<<i}"]""" for i in range(code_n_shifts)]) + " { animation: none; }",
	",".join([f"""#{random_name('opcol')}:has(#{random_name(f'col{1<<i}')}:hover) ~ .{random_name('shift')}[w="{1<<i}"],#{random_name('oprow')}:has(#{random_name(f'row{1<<i}')}:hover) ~ .{random_name('rshift')}[h="{1<<i}"]""" for i in range(CELL_SIZE)]) + " { animation-play-state: running; }",
	",".join([f"""#{random_name('operation')}:has(div[{random_name(f'res{1<<i}')}]:hover) ~ #{random_name('result')} .{random_name('res')}[r="{i+1}"]""" for i in range(CELL_SIZE)]) + " { animation-play-state: running; }",
	" ".join(keyframes),
]

random.shuffle(cstyles)

styles.extend([
	*cstyles,
	f"\n#{random_name('program')}" + " { animation: " + random_name('loop') + " 15s forwards steps(1) infinite; } /* yes, you can overclock CSS. do so at your own risk. you have been warned */",
])
with open("style.css") as f: prestyles = f.read()
import re
prestyles = re.sub(r'#[a-zA-Z0-9-]+', lambda x: '#'+random_name(x.group(0)[1:]), prestyles)
prestyles = re.sub(r'\.[a-zA-z][a-zA-Z0-9-]*', lambda x: '.'+random_name(x.group(0)[1:]), prestyles)
prestyles = prestyles.replace("[block]", f"[{random_name('block')}]")
prestyles = prestyles.replace("[unblock]", f"[{random_name('unblock')}]")
with open("css.html", "w") as f:
	f.write(template % (prestyles + '\n' + " ".join(styles), "\n".join([i.html() for i in code]), "\n".join([i.html() for i in operations]), "\n".join([i.html() for i in tapes]), "".join(inputs)))
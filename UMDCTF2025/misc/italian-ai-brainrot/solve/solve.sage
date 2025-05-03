load("randcrack.sage")

try: from tqdm import tqdm
except ImportError: tqdm = lambda it: it

with open("./rands.txt", "r") as f:
    rands = [int(line.strip()) for line in f.readlines()]

sym_rand = SymbolicRand()
M = zero_matrix(GF(2), len(rands)*24, 624*32)
x = []
for i in tqdm(range(len(rands))):
    a = sym_rand.genrand_uint32()
    for j, rel in enumerate(a[-24:]):
        for k in rel.nonzero_positions():
            M[24*i + j, k] = 1
    output = rands[i]
    x.extend(map(int, bin(output)[2:].zfill(24)))

state = M.solve_right(vector(GF(2), x))
state_uints = [int("".join(map(str, state[i*32:i*32+32])), 2) for i in range(624)]
torch_state_bytes = [
    # the_initial_seed
    0, 0, 0, 0, 0, 0, 0, 0,
    # left
    112, 2, 0, 0,
    # seeded
    1, 0, 0, 0,
    # next
    0, 0, 0, 0, 0, 0, 0, 0,
]
for n in state_uints:
    torch_state_bytes.extend(n.to_bytes(8, byteorder="little"))
torch_state_bytes += [
    # normal_x
    0, 0, 0, 0, 0, 0, 0, 0,
    # normal_y
    0, 0, 0, 0, 0, 0, 0, 0,
    # normal_rho
    0, 0, 0, 0, 0, 0, 0, 0,
    # normal_is_valid
    0, 0, 0, 0,
    # pad
    0, 0, 0, 0,
]
with open("state.txt", "w") as f:
    f.write(" ".join(map(str, torch_state_bytes)))
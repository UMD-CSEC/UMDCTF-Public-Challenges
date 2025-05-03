from Crypto.Util.number import bytes_to_long, long_to_bytes
from pwn import *
import itertools
from tqdm import tqdm

# This script works around 25% of the time.

def rot(n, r):
    return (n >> r) | ((n << (256 - r) & (2**256 - 1)))

                  # 1  2    3    4   5   6
round_constants1 = [3, 141, 59,  26, 53, 58]
round_constants2 = [2, 7,   18,  28, 182, 8]

M = 2**256
N = 6

def encrypt(key, block):
    for i in range(6):
        block = (block + key) & (M-1)
        block = block ^ rot(block, round_constants1[i]) ^ rot(block, round_constants2[i])
    return block

# function that tries to quantify how many carries propagated in the difference
def get_weight(key_index, diff):
    return (diff[(172 - key_index) % 256]) * 2**6 + \
           (diff[(173 - key_index) % 256]) * 2**4 + \
           (diff[(174 - key_index) % 256]) * 2**3 + \
           (diff[(175 - key_index) % 256]) * 2**2 + \
           (diff[(176 - key_index) % 256]) * 2**1 


# undoes the block ^ rot(block) ^ rot(block) operation
# https://marc-b-reynolds.github.io/math/2017/10/13/XorRotate.html
def undo_rotations(block, a, b):
    for _ in range(8):
        block = block ^ rot(block, a) ^ rot(block, b)
        a = (a + a) & 0xff
        b = (b + b) & 0xff
    return block

def decrypt(key, block):
    for i in range(N-1, -1, -1):
        a, b = round_constants1[i], round_constants2[i]
        block = undo_rotations(block, a, b)
        block = (block - key) % M
    return block

def l2n(v):
    s = 0
    for i in range(256):
        s <<= 1
        s += int(v[i])
    return s

def n2l(n):
    return list(map(int, list(bin(n)[2:].zfill(256))))

guessed_key = []

#key = bytes_to_long(os.urandom(32))
#key_list = list(map(int, bin(key)[2:].zfill(256)))

#io = process(["python", "arx.py"])
io = remote("localhost", 1447)
#io.recvuntil("Key:  ")
#key_list = list(map(int, io.recvline(keepends=False).decode()))

samples = 256
attempts = 25

print("Collecting samples...")
guessed_key = [0 for _ in range(256)]
for key_index in tqdm(range(250)):
    carry_weights = {}
    for k in range(samples):
        carry_weights[k] = 0

    for j in range(attempts):
        base = 2**246 * j
        if key_index > 200:
            base = 2**100 * j
        # batch plaintexts
        plaintexts = []
        for k in range(samples):
            pt = base + k
            pt = rot(pt, 256 - key_index)
            plaintexts.append(hex(pt)[2:].zfill(64))
        # encrypt plaintext
        #print(''.join(plaintexts))
        io.sendlineafter(b'(hex): ', ''.join(plaintexts).encode())
        io.recvuntil(b'Ciphertext: ')
        line = io.recvline(keepends=False)
        #print(line)
        cts = bytes.fromhex(line.decode())
        cts = [bytes_to_long(cts[i:i+32]) for i in range(0, len(cts), 32)]
        ucts = [ undo_rotations(ct, round_constants1[N-1], round_constants2[N-1]) for ct in cts ]
        
        for k in range(samples):
            uct1 = ucts[k]
            uct2 = ucts[(k+1) % samples]
            uct1 = list(map(int, bin(uct1)[2:].zfill(256)))
            uct2 = list(map(int, bin(uct2)[2:].zfill(256)))
            diff = [ a ^ b for a, b in zip(uct1, uct2) ]
            weight = get_weight(key_index, diff)
            carry_weights[k] += weight
            
    weights = filter(lambda kv: kv[1] >= 600, carry_weights.items()) # cutoff experimentally determined
    weights = list(weights)
    parity_0, parity_1 = 0, 0
    for k, _ in weights:
        if k & 1 == 0:
            parity_0 += 1
        else:
            parity_1 += 1
    guess = 1 if parity_0 > parity_1 else 0
    #print("Guess: ", guess, "Index: ", key_index, "Actual: ", key_list[255-key_index], "Correct: ", key_list[255-key_index] == guess)
    guessed_key[255 - key_index] = guess
    #print(guessed_key)

io.sendline(b"q")
io.recvuntil(b"Flag: ")
flag_ct = bytes_to_long(bytes.fromhex(io.recvline(keepends=False).decode()))
#print(long_to_bytes(decrypt(l2n(key_list), flag_ct)))

print("Guess: " + str(guessed_key))
if b'UMDCTF' in long_to_bytes(decrypt(l2n(guessed_key), flag_ct)):
    print(long_to_bytes(decrypt(l2n(guessed_key), flag_ct)))
    exit()

new_key = guessed_key[6:]
for start in itertools.product([0, 1], repeat=6):
    k = list(start) + new_key
    pt = long_to_bytes(decrypt(l2n(k), flag_ct))
    #print(pt)
    if b'UMDCTF' in pt:
        print(pt)
        exit()

# try up to 2 errors in key, plus upper 6 bits wrong
for (a,) in tqdm(itertools.combinations(range(0, 250), 1)):
    new_key = guessed_key[6:]
    new_key[a] = new_key[a] ^ 1
    for start in itertools.product([0, 1], repeat=6):
        k = list(start) + new_key
        pt = long_to_bytes(decrypt(l2n(k), flag_ct))
        #print(pt)
        if b'UMDCTF' in pt:
            print(pt)
            exit()
    
print("Trying two errors...")
for (a,b) in tqdm(itertools.combinations(range(0, 250), 2)):
    new_key = guessed_key[6:]
    new_key[a] = new_key[a] ^ 1
    new_key[b] = new_key[b] ^ 1
    for start in itertools.product([0, 1], repeat=6):
        k = list(start) + new_key
        pt = (long_to_bytes(decrypt(l2n(k), flag_ct)))
        if b'UMDCTF' in pt:
            print(a, b)
            print(pt)
            exit()

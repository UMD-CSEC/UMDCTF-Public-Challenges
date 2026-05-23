from pwn import *
from Crypto.Util.number import long_to_bytes
from random import randint

n = 89496838321330017124211425752928111009238414395285545597372895783391482460166014550795440784240669454038164776392492949832230406030665778241454645944939829559549747525412818621247626093163657213524408194055221128159991890855776297338418179985226639927931716465641085590302394062423554511419578835789906477703 
e = 65537

flag_ct = 32496535957677891364589326421449417430729377837780608458415668409871165453269633749883484199105646010680426199991025988748836571723214666842053828395112864735589891145867964037266998630313719088346918877805294912906323776019864911411987496228755959020426960261019729414210431339734682774719446674290001297813

io = process(["python", "server.py"])

sixteen_pow = pow(16, e, n)

calls = 0
def oracle(i):
    global calls
    io.sendlineafter(b"message: ", str(i).encode())
    resp = io.recvuntil(b"Your")
    calls += 1
    # need to worry about 2**1012, 2**1008, etc.
    if b"ERROR" in resp:
        new_i = (sixteen_pow * i) % n
        io.sendlineafter(b"message: ", str(new_i).encode())
        resp = io.recvuntil(b"Your")
        calls += 1
        return b"ERROR" not in resp 
    else:
        return False

lower_bound = 0x67 * 2**1016
upper_bound = 0x68 * 2**1016 - 1



s_0 = randint(100, n)
while not oracle((flag_ct * pow(s_0, e, n)) % n):
    s_0 = randint(100, n)

c0 = (flag_ct * pow(s_0, e, n)) % n
M = [(lower_bound, upper_bound)] # lb <= ct <= ub
i = 1

def merge_intervals(intervals):
    if not intervals:
        return []

    # Sort by start
    intervals.sort()

    merged = [intervals[0]]

    for current in intervals[1:]:
        prev = merged[-1]

        # Overlap or adjacent
        if current[0] <= prev[1] + 1:
            merged[-1] = (prev[0], max(prev[1], current[1]))
        else:
            merged.append(current)

    return merged

s = []
while True: 
    print("Finding s_i...")
    if i == 1:
        s_1 = (n // upper_bound) + 1
        while not oracle((c0 * pow(s_1, e, n)) % n):
            s_1 += 1
        s.append(s_1)
    elif len(M) > 1:
        s_i = s[-1] + 1
        while not oracle((c0 * pow(s_i, e, n)) % n):
            s_i += 1
        s.append(s_i)
    else:
        a, b = M[0]
        # choose an r
        r_i = (2 * (b*s[-1] - lower_bound) // n) + 1
        found = False
        while True:
            # choose an s
            s_min = (lower_bound + r_i * n) // b 
            s_max = (upper_bound + r_i * n) // a
            #print(f"{r_i = }, {s_min = }, {s_max = }")
            for s_i in range(s_min, s_max+1):
                if oracle((c0 * pow(s_i, e, n)) % n):
                    found = True
                    s.append(s_i)
                    break
            if found:
                break
            r_i += 1

    print("narrowing intervals...")
    # narrow intervals
    s_i = s[-1]
    intervals = []
    for a, b in M:
        for r in range((a*s_i - upper_bound + 1)//n, (b*s_i - lower_bound)//n + 1):
            new_a = max(a, (lower_bound + r*n + s_i - 1)//s_i)
            new_b = min(b, (upper_bound - 1 + r*n)//s_i)
            if new_a <= new_b:
                intervals.append((new_a, new_b))
    M = merge_intervals(intervals)
    print(f"{len(M) = }")

    if len(M) == 1:
        print(f"size = {M[0][1] - M[0][0]}")
        if M[0][0] == M[0][1]:
            pt = (M[0][0] * pow(s_0, -1, n)) % n
            break
    i += 1

print(long_to_bytes(pt))

print(f"{calls = }")

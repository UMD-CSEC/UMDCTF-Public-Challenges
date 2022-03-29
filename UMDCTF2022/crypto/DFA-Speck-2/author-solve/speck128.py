from binascii import hexlify, unhexlify

ROUNDS = 32
HB = 64

# HELPERS
def ror(text, n):
    return (2**HB - 1) & ((text >> n) | (text << (HB - n)))

def rol(text, n):
    return (2**HB - 1) & ((text << n) | (text >> (HB - n)))

def R(x,y,k):
    new_x = ror(x, 8)
    #print(f'\nx_before = {unhexlify(hex(x)[2:])}\nx_after  = {unhexlify(hex(new_x)[2:])}\n')
    new_x = (new_x + y) % (1 << HB)
    new_x ^= k
    new_y = rol(y, 3)
    new_y ^= new_x
    return new_x, new_y

def RI(x,y,k):
    new_y = y ^ x
    new_y = ror(new_y, 3)
    new_x = x ^ k
    new_x = (new_x - new_y) % (1 << HB)
    new_x = rol(new_x, 8)
    return new_x, new_y

key_schedule = []

def gen_key_schedule(K): 
    a = K[1] 
    b = K[0]

    key_schedule.append(b)
    for i in range(ROUNDS - 1):
        a, b = R(a, b, i)
        key_schedule.append(b)
        #print(f'{i}:{hex(a)} {hex(b)}')
    
def encrypt(pt):
    x = pt[1]
    y = pt[0]

    #print('\nencrypting...')
    for i in range(ROUNDS):
        x, y = R(x, y, key_schedule[i])
        #print(f'key {i:02x} used --- {key_schedule[i]}')

    return [y,x]

def decrypt(ct):
    # a,b = key schedule, x,y = plaintext
    x = ct[1] 
    y = ct[0]
    
    #print('\ndecrypting...')
    for i in range(ROUNDS - 1, -1, -1):
        #print(f'key {i} used --- {key_schedule[i]}')
        x, y = RI(x, y, key_schedule[i])
    
    return [y,x]

def encrypt_fault(pt, fault_pos, fault_round):
    x = pt[1]
    y = pt[0]

    # Regular Speck until the last round
    for i in range(ROUNDS - fault_round):
        x, y = R(x, y, key_schedule[i])
    
    if (fault_pos < 64):
        y = y ^ (1 << fault_pos)
    elif (fault_pos < 128):
        x = x ^ (1 << (fault_pos - 64))
    else:
        print("WARNNIG: bit fault out of bounds")
        exit()
   
    for i in range(ROUNDS - fault_round, ROUNDS):
        x, y = R(x,y,key_schedule[i])

    return [y,x]

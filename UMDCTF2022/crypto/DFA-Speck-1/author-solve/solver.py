#!/usr/bin/env python3

import struct
import speck128
from binascii import unhexlify, hexlify

# SPECK 128/128

BS = 128
HB = 64
BB = 16
b = 3 # beta 
a = 8 # alpha

ROUNDS = 32

def process_file(filename):
    ciphers = {}
    unpack = lambda x: int(x,16)
    with open(filename, 'r') as file:
        for line in file:
            pos, cipher = [x.strip() for x in line.split(':')]
    
            if pos == 'ct' or pos == 'pt' or pos == 'ke':
                pass
            elif pos == 'k32':
                kt = cipher
                ciphers[pos] = unpack(kt)
                continue
            else:
                pos = int(pos,16)
        
            low,high = cipher[:BB],cipher[BB:] # div2
            ciphers[pos] = (unpack(low), unpack(high))
    
    return ciphers 
    
def get_hex(text):
    return ''.join(hex(x)[2:].zfill(2) for x in struct.pack('>Q', text))

def get_bin(hx):
    b = bin(hx)[2:]
    b = '0'*(HB-len(b)) + b
    return b

def ror(text, n):
    return (2**HB - 1) & ((text >> n) | text << (HB - n))

def rol(text, n):
    return (2**HB - 1) & ((text << n) | text >> (HB - n))

def bit(text,pos):
    return (text >> pos) & 1

# speck128.py
def RI(x,y,k):
    new_y = y ^ x
    new_y = ror(new_y, 3)
    new_x = x ^ k
    new_x = (new_x - new_y) % (1 << HB)
    new_x = rol(new_x, 8)
    return new_x, new_y

def reverse_last_round(ciphers, k32):
    ciphers['ct_original'] = [ciphers['ct'][1], ciphers['ct'][0]]
    yt, xt = ciphers['ct']

    xt, yt = RI(xt, yt, k32)
    ciphers['ct'] = (yt, xt)

    for i in range(64):
        yt, xt = ciphers[i]
        xt, yt = RI(xt, yt, k32)
        ciphers[i] = (yt, xt)
    
    return ciphers

def reverse_key_schedule(j32, k32):
    a = j32
    b = k32
    
    #print(f'31 - {get_hex(a)} {get_hex(b)}')
    for i in range(ROUNDS - 2, -1, -1):
        a, b = RI(a, b, i)
        #print(f'{i} - {get_hex(a)} {get_hex(b)}')

    return a, b

def solve_k(ciphers):
    yt, xt = ciphers['ct']
   
    #print(f'xt = {get_bin(xt)}\nyt = {get_bin(yt)}')

    kt = 0
    ci = 0
    for i in range(64):
        yti, xti = ciphers[i]
        
        e = ror(xt ^ yt ^ xti ^ yti, b)
        ee = xt ^ xti
        count = 0
        for c in [bit(ee,pos) for pos in range(64)]:
            if c == 1:
                count += 1
        
        ci_ = ci 
        if count == 1: # no ripple in add
            xt_a = ci
            ci = 0
        else: # ripple in add
            xt_a = ci ^ 1
            ci = 1

        ktp = xt_a ^ bit(xt ^ yt, (i+b) % HB) ^ bit(xt, i) ^ ci_
        kt = kt | (ktp << i)

        #print(f'\n      e   = {get_hex(e)}')
        #print(f'xt ^ xt\'  = {get_hex(xt ^ xti)}')
        #print(f'      eq  = ({xt_a} ^ {bit(xt ^ yt, (i+b) % HB)} ^ {ci_}) ^ {bit(xt, i)}')
        #print(f'       kt = {get_hex(kt)}')

    return kt

def process(options):
    ciphers = process_file(options.file)
    
    k32 = solve_k(ciphers)
    k32 ^= (1 << 63)
    #k32 = 0x306e675f336e7566 # this makes k32 = 0ng_3nuf
    print(f'k32: {get_hex(k32)} expect: 306e675f336e7566')
    
    # expected k31: 488bcae68d876541
    # expected k32: 306e675f336e7566

    #WIP 
    if options.part2:
        ciphers = process_file(options.file2)

        ciphers = reverse_last_round(ciphers, k32)
        
        k31 = solve_k(ciphers) 

        for i in range(2):
            k31 ^= (i << 63)
            print(f'\nk31: {get_hex(k31)} expect: 488bcae68d876541')
        
            j32 = rol(k31,b) ^ k32
            #j32 = 0x7430306b5f555f6c # this makes j32 = t00k_U_l 
            print(f'j32: {get_hex(j32)} expect: 7430306b5f555f6c')
        
            key = reverse_key_schedule(j32, k32)
            print(f'key: {get_hex(key[0])} - {get_hex(key[1])}')
            
            speck128.gen_key_schedule([key[1], key[0]])
            print(hex(ciphers['ct_original'][0])[2:])
            print(hex(ciphers['ct_original'][1])[2:])
            pty, ptx = speck128.decrypt(ciphers['ct_original'][::-1])
            print(f'pt = {(unhexlify(hex(ptx)[2:]) + unhexlify(hex(pty)[2:]))}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',
                        help='in file with all the faulted ciphers',
                        default='r-1_faults.out')
    parser.add_argument('-2', '--part2',
                        help='solve part2 items',
                        action='store_true')
    parser.add_argument('-F', '--file2',
                        help='in file with all the faulted ciphers for part 2',
                        default='r-2_faults.out')
    options = parser.parse_args()
    process(options)

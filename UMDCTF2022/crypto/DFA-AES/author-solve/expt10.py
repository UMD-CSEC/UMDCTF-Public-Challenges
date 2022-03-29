#!/usr/bin/env python3

import binascii as ba
#import IPython as ipy

### HELPERS
def tointarray(line):
    return [ x for x in line ]

def tohexarray(line):
    return [ f'0x{i:02x}' for i in line ]

def xor(a,b):
    return [ x ^ y for x , y in zip(a,b) ]

def flatten(l):
    return [x for y in l for x in y]

### PROCESSING
SBOX = [ \
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, 
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, 
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, 
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16 ]
SBOX_INV = [0] * 256

RCON = [[1,0,0,0],
        [2,0,0,0],
        [4,0,0,0],
        [8,0,0,0],
        [16,0,0,0],
        [32,0,0,0],
        [64,0,0,0],
        [128,0,0,0],
        [27,0,0,0],
        [54,0,0,0]]

def generate_sbox_inv():
    global SBOX_INV
    for i,x in enumerate(SBOX):
        SBOX_INV[x] = i

def RotWord(word):
    return [word[1],word[2],word[3],word[0]]

def SubWord(word):
    return [SBOX[i] for i in word]

# Inverses the key schedule from the last round key
# reference: https://camo.githubusercontent.com/77e8022c3c0518d1849d94611dccf3d0c9d3a2694b34ef99a2189f12153686c7/68747470733a2f2f692e696d6775722e636f6d2f5a4a3375576b492e6a7067
def aes_key_expand128_inv(k_10):
    w = [[0,0,0,0]]*44 #44 word output
    w[40], w[41], w[42], w[43] = [[k_10[i], k_10[i+1], k_10[i+2], k_10[i+3]] \
                                    for i in range(0,16,4)]

    def rcon_g():
        for i in RCON[::-1]:
            yield i
    rcon = rcon_g()

    #start
    w[39] = xor(w[42], w[43])
    w[38] = xor(w[41], w[42])
    w[37] = xor(w[40], w[41])
    
    for i in range(36,0,-4):
        w[i-1] = xor(w[i+2], w[i+3])
        w[i-2] = xor(w[i+1], w[i+2])
        x = RotWord(w[i+3])
        y = SubWord(x)
        z = xor(y, next(rcon))
        w[i] = xor(w[i+4],z)
        w[i-3] = xor(w[i], w[i+1])

    x = RotWord(w[3])
    y = SubWord(x)
    z = xor(y, next(rcon))
    w[0] = xor(w[4], z)
    return w

# find the byte that is affected by the fault
def get_diff_group(line):
    for i,x in enumerate(line):
        if x != 0:
            return i

# compare upper nibble, if in the same row
def compare_upper(collect):
    return (collect[0] & 0xf0) == (collect[1] & 0xf0) \
           and (collect[1] & 0xf0) == (collect[2] & 0xf0) \
           and (collect[2] & 0xf0) == (collect[3] & 0xf0) \

# compare lower nibble, if in the same col
def compare_lower(collect):
    return (collect[4] & 0x0f) == (collect[5] & 0x0f) \
           and (collect[5] & 0x0f) == (collect[6] & 0x0f) \
           and (collect[5] & 0x0f) == (collect[7] & 0x0f) \

# finds the byte of the last round key for the group defined by low/high
def process_group(low, high, faults):
    diff = xor(faults[low], faults['base'])
    grp_num = get_diff_group(diff)
    print(f'BYTE {grp_num}: ', end='')
    
    for guess in range(256):
        collect = []
        for i in range(low,high):
            m_i = faults[i][grp_num] ^ guess
            collect.append(SBOX_INV[m_i])
        
        #check if this looks good!          
        if compare_upper(collect) and compare_lower(collect):    
            print(f'{guess} -- ',end='')
            for m_i in collect:
                print(f'{m_i:02x}, ', end='')
            print()
            return grp_num, guess

# find all the bytes of last round key
def process(faults):
    key_j = [0] * 16
    for i in range(0,128,8):
        grp_num, key = process_group(i, i+8, faults)
        key_j[grp_num] = key
    
    print('K_10: ',end='')
    print(' '.join([f'{i:02x}' for i in key_j]))
    return key_j

### MAIN
if __name__ == '__main__':
    generate_sbox_inv()
    
    #process the data file
    faults = {}
    with open('faults.txt', 'r') as file:
        for line in file: 
            if line[0:2] == 'ct':
                faults['base'] = ba.unhexlify(line[4:-1])
                continue
            bit_fault = ba.unhexlify(line[0:2])
            out = ba.unhexlify(line[4:-1])
            faults[ord(bit_fault)] = out 
            print(f"{ord(bit_fault)} - {len(out)} - {out}")
    print('cipher: ')
    [print(f'{i:02x} ',end='') for i in faults['base']]

    k_10 = process(faults) # get k10
    key_schedule = aes_key_expand128_inv(k_10) # reverse k10
    
    print('key_schedule:')
    for i in range(0,44,4): #this is stupid ik, ignore this
        for j in range(4):
            print(f'{key_schedule[i][j]:02x} ',end='')
        for j in range(4):
            print(f'{key_schedule[i+1][j]:02x} ',end='')
        for j in range(4):
            print(f'{key_schedule[i+2][j]:02x} ',end='')
        for j in range(4):
            print(f'{key_schedule[i+3][j]:02x} ',end='')
        print()
    print('---')
    
    # pull the original key from schedule
    key = flatten(key_schedule[0:4])
    [print(f'{i:02X}',end='') for i in key]
    print()

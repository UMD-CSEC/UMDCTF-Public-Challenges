flag = open('flag.txt', 'r').read()
enc_flag = ''
for c in flag:
    bit = f'{ord(c):08b}'
    new_bit = bit[2] + bit[3] + bit[1] + bit[5] + bit[4] + bit[6] + bit[7] + bit[0]
    enc_flag += hex(int(new_bit, 2))[2:]

print(f'put this in the rom: {enc_flag}')

from Crypto.Util.number import long_to_bytes as l2b

parts = open('output.txt', 'r').read().split('\n')
chars = parts[1:-1]
p = int(parts[0].split(': ')[1])
m = p-1

flag_bits = ''
for line in chars:
    a = int(line.split(', ')[0])
    b = int(line.split(', ')[1])
    bit = '0'
    if ((a*b) % p == 1):
        bit = '1'
    flag_bits += bit

print(flag_bits)
print(l2b(int(flag_bits, 2)).decode())
    

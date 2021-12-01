ctext = ""

with open("flag.txt", 'r') as f:
    ctext = f.read()[0:-1]
alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"]

def sub_bit_array(b, s, e):
    return (b >> (8 - e)) % (2**(e - s))

def basenencode(data, n):
    buf = ""
    current_val = 0
    current_offset = 0
    end_offset = n
    left_over_bits = 0
    for i in data:
        while current_offset < 8 and end_offset < 8:
            current_bits = sub_bit_array(ord(i), current_offset, end_offset)
            current_bits += left_over_bits << end_offset            
            buf += alphabet[current_bits]
            current_offset = end_offset
            end_offset += n
            left_over_bits = 0       
        if current_offset < 8:
            left_over_bits = sub_bit_array(ord(i), current_offset, 8)       
        end_offset = end_offset % 8
        current_offset = 0
    current_bits = left_over_bits << end_offset
    buf += alphabet[current_bits]
    return buf

for n in range(6, 0, -1):
    print(ctext)
    ctext = basenencode(ctext, n)
with open('ctext.txt', 'w') as f:
    f.write(ctext)
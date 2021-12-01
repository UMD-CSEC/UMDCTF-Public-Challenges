with open("ctext.txt", 'r') as f:
    ctext = f.read()[0:-1]
alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"]

def from_sub_bit_array(b, s, e):
    return (b >> (8 - e)) % (2**(e - s))

# def basendecode(data, n):
#     buf = ""
#     left_over_bits = 0
#     current_offset = 0
#     end_offset = n
#     multiplier = 8 - n
#     for i in data:
#         element = alphabet.index(i)
#         print(i)
#         print(element)
#         print(current_offset)
#         print(end_offset)
#         print(bin(left_over_bits))
#         real_end_offset = min(end_offset, 8)
#         first_element = element
#         if end_offset > 8:
#             first_element = element >> (end_offset - 8)
#         current_val = first_element << multiplier
#         print(current_val)
#         current_val += left_over_bits 
#         print(current_val)
#         if end_offset >= 8:
#             buf += chr(current_val)
#             print("ADDING")
#             print(current_val)
#             current_offset = 0
#             end_offset %= 8
#             left_over_bits = (element % 2**(end_offset % 8)) << end_offset % 8
#         else:
#             current_offset = end_offset
#             end_offset += n 
#             left_over_bits = current_val
#             multiplier -= n
#             multiplier = max(multiplier, 0)
#     return buf
def basendecode(data, n):
    buf = ""
    current_offset = 0
    leftover_bits = 0
    for i in data:
        element = alphabet.index(i)
        needed_bits = (8 - current_offset)
        if needed_bits > n:
            leftover_bits += element << (needed_bits - n)
            current_offset += n
            continue
        first_element = element >> (n - needed_bits)
        leftover_bits += first_element
        buf += chr(leftover_bits)
        leftover_bits = (element % 2**(n - needed_bits)) << (needed_bits + 8 - n)
        current_offset = (n - needed_bits)
    if leftover_bits != 0:
        buf += chr(leftover_bits)
    return buf
for n in range(1, 7):
    ctext = basendecode(ctext, n)
    print(ctext)
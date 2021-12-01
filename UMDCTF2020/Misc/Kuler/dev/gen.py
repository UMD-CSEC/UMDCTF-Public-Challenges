import textwrap


def bitstring_to_bytes(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])



f = open('qr','r')
lines = f.readlines()
f.close()


for line in lines:
    line += '000000'
    blocks = (textwrap.wrap(line, 12))

    byte_blocks = []
    for block in blocks:
        # print(block)
        a = int(block, 2)
        hex_s = format(a, '#08x')
        print(hex_s)
        # byte_blocks.append(bitstring_to_bytes(block))
    
    # print('-----')
    print('')
    # input()

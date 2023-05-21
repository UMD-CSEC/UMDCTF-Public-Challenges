load("output.sage")

q = 15901
n = 256

flip = [[0 for _ in range(n)] for _ in range(n)]
for i in range(n):
    flip[i][n-i-1] = 1

flip = matrix(flip)

R = IntegerModRing(q)
AF = (A + flip).change_ring(R)

s = AF.solve_right(B)

# Decryption functions 
def decode_msg(msg):
    hex_vals = ""
    for entry in msg:
        val = entry[0]
        val = round(int(val) * (2**4 / q) ) % (2**4)
        hex_vals += '0123456789abcdef'[val] # lazy way to convert to a single hex digit
    return hex_vals


def decrypt():
    msg = (V - B_prime*s) % q
    return decode_msg(msg)

print(decrypt())

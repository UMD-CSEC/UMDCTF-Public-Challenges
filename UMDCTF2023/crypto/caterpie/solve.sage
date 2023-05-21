# Before running this solve script, make a file called output.sage that wraps the matrices in the output with matrix( )
load("output.sage")

q = 2**16
n = 64

AT = A.transpose()

kannan_embedding = block_matrix([[identity_matrix(ZZ, n), -AT,                        zero_matrix(n,1)],
                                 [zero_matrix(n, n),      q*identity_matrix(ZZ, n),   zero_matrix(n,1)],
                                 [zero_matrix(1, n),      B.transpose(),              identity_matrix(1)]])                              


solution = kannan_embedding.BKZ(block_size=20)

se = list(solution[0])

s = matrix(se[:n]).transpose()

# Decryption functions 
def decode_msg(msg):
    hex_vals = ""
    for entry in msg:
        val = entry[0]
        val = round(val * (2**4 / q) ) % (2**4)
        hex_vals += '0123456789abcdef'[val] # lazy way to convert to a single hex digit
    return hex_vals


def decrypt():
    msg = (V - B_prime*s) % q
    return decode_msg(msg)

print(decrypt()) # prints flag in hex

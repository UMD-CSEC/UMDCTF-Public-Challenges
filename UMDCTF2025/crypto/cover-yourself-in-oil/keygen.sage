import random

F = GF(127)

n = 48
v = 120

# compression factor
l = 6

def expand_matrix(vec):
    M = []
    for x in vec:
        M.append([F(x * 2**k) for k in range(l)])
    return matrix(M)

def sample_vector():
    return [random.randint(0, 126) for _ in range(l)]

def sample_block():
    return expand_matrix(sample_vector())

def compress_matrix(M):
    return M.columns()[::l]

# generate private key
Ms = []
for _ in range(n):
    # choose oil matrix
    O1 = block_matrix([[sample_block() for i in range(v // l)] for j in range(n // l)])
    O2 = block_matrix([[sample_block() for i in range(n // l)] for j in range(v // l)])
    O3 = block_matrix([[sample_block() for i in range(v // l)] for j in range(v // l)])

    # symmetric matrix? never heard of 'em
    M = block_matrix([[zero_matrix(n), O1], [O2, O3]])

    Ms.append(M)

# add identity to make T invertible
T = block_matrix([[sample_block() for i in range((n+v)//l)] for j in range((n+v)//l)]) + identity_matrix(n+v)
sk = (Ms, T)

# generate public key
pk = [compress_matrix(T.T * M * T) for M in Ms]

with open("public_key.txt", 'w') as f:
    f.write(str(pk))


import random

F = GF(127)

n = 48
v = 120

# compression factor
l = 6

def expand_column(vec):
    M = []
    for x in vec:
        M.append([F(x * 2**k) for k in range(l)])
    return matrix(M)


def sample_vector():
    return [random.randint(0, 126) for _ in range(l)]

def sample_block():
    return expand_matrix(sample_vector())


# rebuild public key matrices
f = open("public_key.txt", 'r')
pk = eval(f.read())

Ps = []
for p in pk:
    M = matrix([[]] * (n + v))
    for c in p:
        M = M.augment(expand_column(c))
    M.change_ring(F)
    Ps.append(M)


# rows 1-5 are kernel vectors of all P matrices
Q_block = matrix(F, [[1, 0, 0, 0, 0, 0],
                     [1, 0, 0, 0, 0, F(-1)/32],
                     [1, 0, 0, 0, F(-1)/16, 0],
                     [1, 0, 0, F(-1)/8 , 0, 0],
                     [1, 0, F(-1)/4 , 0, 0, 0],
                     [1, F(-1)/2 , 0, 0, 0, 0],
                    ]).T

# permutation to compress matrix
selection = [i for i in range(0, n+v, 6)] + [j for j in range(0, n+v) if j % 6 != 0]
permutation = [[1 if selection[j] == i else 0 for j in range(n+v)] for i in range(n+v)]
permutation = matrix(permutation)


Q = block_diagonal_matrix(*([Q_block] * ((n+v)//l)))
Q = Q * permutation

print(Q.rank())


'''
new_Ps = []
for P in Ps:
    new_P = (Q.T * P * Q).submatrix(0,0,n+v,28)
    new_Ps.append(new_P)
    #print(new_P)
    #print()
'''

O_dim = n+v - 28
O_img = block_matrix(F, [[zero_matrix(O_dim, 28), identity_matrix(O_dim)]])

'''
for oi in O_img:
    oiQ = oi * Q
    Qoi = Q * oi
    for new_P in new_Ps:
        assert oi * new_P * oi == 0
    for P in Ps:
        assert oiQ * P * Qoi == 0
'''

O = O_img * Q.T

# rows of O are zero on every P
'''
for o in O:
    for P in Ps:
        assert o * P * o == 0
'''

rand_v = random_vector(F, n+v)
system = matrix(F, [O * (P + P.T) * rand_v for P in Ps])
t = eval(input("Paste target: "))
target = vector(F, [ti - rand_v * P * rand_v for ti, P in zip(t, Ps)])
sig = system.solve_right(target)*O + rand_v

print(sig)
#for P in Ps:
    #print(sig * P * sig)



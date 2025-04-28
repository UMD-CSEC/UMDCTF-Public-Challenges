from enum import Enum
from ctypes import *
import numpy as np

SIZE = 15

def chall_gen():

    size = SIZE

    A = np.random.randn(size, size)

    for i in range(size):
        for j in range(size):
            A[i, j] = np.float32(A[i, j])


    Q, R = np.linalg.qr(A)
    # print(np.matmul(Q, Q.T))

    print(A)

    print()

    print(Q)

    print() 
    print(R)

    np.savez("solve.npz", a=A, q=Q, r=R)

    orthogonality_check = f"""
NOP {size}.0f 0.0f
MOV r-1 2.0f
JMP labSTART 0.0f
labFAIL
HLT 5.0f 5.0f
labSTART
labSUM
labOI
labOJ
labOII
labOJJ

labLoopSum
labOK
labOKK

NOP -{size}.0f 0.0f
MUL labOI r-1
NOP -1.3f 0.0f
ADD r-1 r-3
SUB labOK r-4

MOV r-5 r1
MOV 0.0f r1
NOP 0.0f 0.0f
NOP 0.0f 0.0f
MOV r-1 r-3

NOP -{size}.0f 0.0f
MUL labOJ r-1
NOP -1.3f 0.0f
ADD r-1 r-3
SUB labOK r-4

MOV r-5 r1
MOV 0.0f r1
NOP 0.0f 0.0f
NOP 0.0f 0.0f
MOV r-1 r-3

MUL r-3 r-13
ADD r-14 labLoopSum
//PH labLoopSum r-12
NOP 0.0f 0.0f

NOP -{size}.0f -{size}.0f
MOV r-1 r-14

NOP -{size}.0f -{size}.0f
MOV r-1 r-26

NOP 1.0f 0.0f
ADD r-1 labOK

#LOOP(2.0f, labOK, labOKK)
NOP 0.0f 0.0f
MOV r-1 labOK

#CMP(labOI, labOJ, labIEJ, labINJ)

labIEJ
NOP 1.0f 0.0f
SUB r-1 labLoopSum
NOP 0.00001f 0.0f
#CMP_LT(labLoopSum, r-1, labCONT, labFAIL)

labINJ
NOP 0.00001f 0.0f
#CMP_LT(labLoopSum, r-1, labCONT, labFAIL)

labCONT
NOP 0.0f 0.0f
MOV r-1 labLoopSum

NOP 1.0f 0.0f
ADD r-1 labOJ
#LOOP(2.0f, labOJ, labOJJ)
NOP 0.0f 0.0f
MOV r-1 labOJ

NOP 1.0f 0.0f
ADD r-1 labOI
#LOOP(2.0f, labOI, labOII)

    """

    upper_triangular_check = f"""
NOP {size}.0f 0.0f
MOV r-1 2.0f
JMP labUSTART 0.0f
labUFAIL
HLT 5.0f 5.0f
labUSTART
labUI
labUJ
labUII
labUJJ

//PH labUI labUJ
NOP 0.0f 0.0f

NOP -{size}.0f 0.0f
MUL labUI r-1
NOP -{size * size + 1.3}f 0.0f
ADD r-1 r-3
SUB labUJ r-4

MOV r-5 r1
MOV 0.0f r1
labULTSTODAT
NOP 0.0f 0.0f
MOV r-1 r-3

// PH r-10 labULTSTODAT
NOP 0.0f 0.0f

NOP -{size}.0f -{size}.0f
MOV r-1 r-12

#CMP_LT(labUJ, labUI, labULT, labUGEQ)

labULT
NOP 0.0f 0.0f
#CMP(labULTSTODAT, r-1, labUEQ, labUFAIL)
labUEQ
labUGEQ

NOP 1.0f 0.0f
ADD r-1 labUJ
#LOOP(2.0f, labUJ, labUJJ)
NOP 0.0f 0.0f
MOV r-1 labUJ

NOP 1.0f 0.0f
ADD r-1 labUI
#LOOP(2.0f, labUI, labUII)

labUEND
"""

    product_check = f"""

NOP {size}.0f 0.0f
MOV r-1 2.0f
JMP labPSTART 0.0f
labPFAIL
HLT 7.0f 7.0f
labPSTART
labPI
labPJ
labPII
labPJJ

labPLoopSum
labPK
labPKK

NOP -{size}.0f 0.0f
MUL labPI r-1
NOP -1.3f 0.0f
ADD r-1 r-3
SUB labPK r-4

MOV r-5 r1
MOV 0.0f r1
NOP 0.0f 0.0f
NOP 0.0f 0.0f
MOV r-1 r-3

NOP -{size}.0f 0.0f
MUL labPK r-1
NOP -{size * size + 1.3}f 0.0f
ADD r-1 r-3
SUB labPJ r-4

MOV r-5 r1
MOV 0.0f r1
NOP 0.0f 0.0f
NOP 0.0f 0.0f
MOV r-1 r-3

MUL r-3 r-13
ADD r-14 labPLoopSum
//PH r-12 r-22
NOP 0.0f 0.0f

NOP -{size}.0f -{size}.0f
MOV r-1 r-14

NOP -{size}.0f -{size}.0f
MOV r-1 r-26

NOP 1.0f 0.0f
ADD r-1 labPK

#LOOP(2.0f, labPK, labPKK)
NOP 0.0f 0.0f
MOV r-1 labPK

//PH labPLoopSum 0.0f

NOP {size}.0f 0.0f
MUL labPI r-1
NOP 4.1f 0.0f
ADD r-1 r-3
ADD labPJ r-4

MOV r-5 r1
MOV 0.0f r1
NOP 0.0f 0.0f
NOP 0.0f 0.0f
MOV r-1 r-3

// PH r-10 0.0f
NOP 0.0f 0.0f

NOP {size}.0f {size}.0f
MOV r-1 r-12

//PH r-5 0.0f
NOP 0.0f 0.0f

SUB r-7 labPLoopSum
NOP 0.00001f 0.0f
#CMP_LT(labPLoopSum, r-1, labPCONT, labPFAIL)

labPCONT
NOP 0.0f 0.0f
MOV r-1 labPLoopSum

NOP 1.0f 0.0f
ADD r-1 labPJ
#LOOP(2.0f, labPJ, labPJJ)
NOP 0.0f 0.0f
MOV r-1 labPJ

NOP 1.0f 0.0f
ADD r-1 labPI
#LOOP(2.0f, labPI, labPII)

"""

    B = np.random.randn(size, size)

    for i in range(size):
        for j in range(size):
            B[i, j] = np.float32(B[i, j])

    B = np.matmul(B, B.T)
    B = np.matmul(B, B)

    # Computing diagonalization
    evalues, evectors = np.linalg.eig(B)
    # Ensuring square root matrix exists
    assert (evalues >= 0).all()
    S = evectors * np.sqrt(evalues) @ np.linalg.inv(evectors)

    A = [j for i in A.tolist() for j in i]
    B = [j for i in B.tolist() for j in i]

    t = 0
    constants = ""
    for i in range(len(A)):
        t += 1
        constants += f"""
NOP {A[i]}f 0.0f
MOV r-1 {4 + i}.1f
"""

    for i in range(len(B)):
        constants += f"""
NOP {B[i]}f 0.0f
MOV r-1 {4 + t + i}.1f
"""
    # return (A, B, Q, R, S);
    return orthogonality_check, constants, upper_triangular_check, product_check;


def input_string(num_inps):
    yep = ""

    for i in range(num_inps):
        yep += f"INP -{i + 1}.3f 0.00f\n"

    return yep

ortho, const, ut, prod = chall_gen()

so_file = "./map.so"

funcs = CDLL(so_file)

funcs.map.argtypes = [c_float]
funcs.map.restype = c_float

with open("rev1.c", "r") as f:
    code = f.read().strip()

OP = {
    "HLT" : "-3.141f",
    "NOP" : "0.00f",
    "MOV" : "10.103f",
    "ADD" : "23.221891f",
    "SUB" : "21.8917f",
    "MUL" : "22.3313f",
    "SGN" : "20.32f",
    "ROT" : "28.393f",
    "CAS" : "8329.113f",
    "JMP" : "22.190f",
    "INP" : "4554.1337f",
    "PH" : "666.666f",
}


def macro_pass(string): 
    out1 = [i.strip() for i in string.split("\n") if i != '']
    ret = []

    for i in out1:
        if i.startswith("#"):
            x = i[1:]
            name = x.split("(")[0]
            args = [i.strip() for i in x.split("(")[1].split(")")[0].split(",")]
            if name == "CMP":
                ret.append(cmp(*args))
            if name == "CMP_LT":
                ret.append(cmp_lt(*args))
            if name == "LOOP":
                ret.append(loop(*args))
        else:
            ret.append(i)
    return "\n".join(ret)

def cmp(a, b, eq, neq):
    return f"""
MOV {b} r7
MOV {a} r4
SUB r5 r3
CAS r2 JMP
ROT r1 0.0f
NOP 0.0f r6
JMP r2 0.0f
NOP 0.0f 0.0f
ROT r-3 0.0f
ROT r-4 0.0f
JMP {eq} 0.0f
ROT r-6 0.0f
ROT r-7 0.0f
JMP {neq} 0.0f
    """

def loop(a, b, loopback):
    return f"""
MOV {b} r7
MOV {a} r4
SUB r5 r3
CAS r2 JMP
ROT r1 0.0f
NOP 0.0f r3
JMP r5 0.0f
NOP 0.0f 0.0f
ROT r-3 0.0f
ROT r-4 0.0f
JMP {loopback} 0.0f
ROT r-6 0.0f
ROT r-7 0.0f
    """

def cmp_lt(a, b, lt, geq):
    return f"""
NOP 4.0f 0.0f
NOP 3.0f 0.0f
MOV {b} r10
MOV {a} r7
SUB r8 r6
SGN r5 r5
SUB r1 r4
NOP -1.0f 0.0f
CAS r2 JMP
ROT r1 0.0f
NOP 0.0f r6
JMP r2 0.0f
NOP 0.0f 0.0f
ROT r-3 0.0f
ROT r-4 0.0f
JMP {lt} 0.0f
ROT r-6 0.0f
ROT r-7 0.0f
JMP {geq} 0.0f
    """

def compile_from_string(string):
    out1 = [i.strip() for i in string.split("\n") if i != '']
    out1 = [i for i in out1 if not i.startswith("//")]
    out1 = [i for i in out1 if i != '']
    labels = {}
    assembled = []
    for i in out1:
        keywords = [i for i in i.split(' ') if i != '' ]
        if len(keywords) == 1 and keywords[0].startswith("lab"):
            labels[keywords[0]] = len(assembled)
            assembled.append([OP["NOP"], "0.00f", "0.00f"])
        else:
            genned = []
            for j in range(len(keywords)):
                if keywords[j].startswith("r"):
                    genned.append((int(keywords[j][1:]), 'rel'))
                elif keywords[j].startswith("a"):
                    genned.append((int(keywords[j][1:]), 'abs'))

                elif keywords[j].startswith("lab"):
                    genned.append((keywords[j], 'lab'))

                elif keywords[j] in OP.keys():
                    genned.append(OP[keywords[j]])

                else:
                    genned.append(keywords[j])
            assert len(genned) == 3
            assembled.append(genned)

    for j in range(len(assembled)):
        for k in range(len(assembled[j])):
            if type(assembled[j][k]) == tuple:
                if assembled[j][k][1] == "lab":
                    assembled[j][k] = (labels[assembled[j][k][0]], 'abs')

    return assembled

prog = input_string(2) + """
labV
NOP 1.0f 0.0f
ADD r-1 labV
#LOOP(-1.3f, labV, labV)
MOV labV r1
HLT 40.0f 40.0f
"""

prog = const + input_string(2 * SIZE * SIZE) + ortho + ut + prod + "\nHLT 40.0f 40.0f";

out = macro_pass(prog)

out = compile_from_string(out)

length = len(out);

for i in range(length):
    for j in range(3):
        if type(out[i][j]) == tuple:
            if out[i][j][1] == "rel":
                out[i][j] = i + out[i][j][0]
            elif out[i][j][1] == "abs":
                out[i][j] = out[i][j][0]


mapped_tuples = [(0, -1.0)]
for i in range(length - 1):
    mapped_tuples.append((i + 1, funcs.map(c_float(i + 1))))
mapped_tuples.sort(key=lambda x: x[1])

n_out = [0] * length
for i in range(length):
    z = out[i]
    for j in range(3):
        if type(z[j]) == int:
            z[j] = str(mapped_tuples[z[j]][1])
    n_out[mapped_tuples[i][0]] = z

prog = "float prog[] = {" + ",".join([i[0] for i in n_out]) + "};"
d1 = "float d1[] = {" + ",".join([i[1] for i in n_out]) + "};"
d2 = "float d2[] = {" + ",".join([i[2] for i in n_out]) + "};"

code = code.replace("// { prog }", prog)
code = code.replace("// { d1 }", d1)
code = code.replace("// { d2 }", d2)
code = code.replace("// { size }", "int size = " + str(length) + ";");

with open("reality.c", "w") as f:
    f.write(code)


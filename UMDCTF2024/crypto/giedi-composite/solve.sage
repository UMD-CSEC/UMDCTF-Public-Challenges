from Crypto.Util.number import bytes_to_long, long_to_bytes

N = 210
q = 2003
p = 3


pub = [713, 927, 1979, 1300, 1756, 751, 512, 192, 1404, 340, 192, 1324, 1026, 1988, 1262, 1082, 255, 44, 1472, 705, 494, 256, 1799, 374, 371, 865, 1973, 1867, 1084, 951, 1725, 1561, 1669, 347, 689, 1682, 320, 1014, 1173, 1582, 1251, 745, 681, 1873, 1673, 481, 148, 243, 617, 277, 1962, 814, 479, 968, 1472, 642, 353, 409, 1603, 803, 323, 1691, 1364, 1809, 1824, 358, 1273, 246, 1507, 114, 1931, 1103, 17, 121, 1883, 1969, 74, 366, 231, 1167, 1393, 173, 454, 1083, 452, 817, 1623, 223, 1779, 1209, 1518, 1100, 968, 264, 1980, 1883, 1342, 1554, 1783, 1505, 852, 642, 1268, 759, 1723, 1543, 1999, 1019, 1999, 321, 449, 657, 1837, 1427, 313, 282, 1502, 1144, 1615, 1251, 1311, 236, 340, 253, 239, 1081, 1089, 848, 1988, 1365, 121, 1672, 629, 1499, 783, 1466, 1347, 936, 1165, 1740, 630, 701, 888, 554, 1465, 928, 21, 306, 1777, 62, 1744, 1712, 1105, 1940, 1660, 551, 1590, 1520, 1756, 899, 133, 378, 1215, 884, 812, 655, 660, 916, 1541, 1087, 1198, 1900, 1025, 430, 386, 1040, 1459, 1709, 224, 960, 575, 738, 695, 1421, 502, 688, 381, 235, 1171, 401, 110, 143, 332, 1589, 1611, 1424, 734, 1039, 692, 1380, 45, 1657, 82, 1676, 1918, 688, 772, 1719, 1287, 1346]
ct = [953, 681, 1154, 1558, 970, 1086, 1955, 1810, 797, 290, 816, 474, 98, 1288, 1668, 74, 1063, 253, 1782, 1479, 650, 1313, 854, 588, 485, 1054, 1833, 1418, 807, 1184, 545, 205, 1463, 495, 1426, 847, 1564, 1705, 1549, 1697, 1291, 1034, 1487, 766, 1299, 781, 1569, 803, 794, 347, 1998, 1003, 897, 714, 1285, 1400, 1703, 1726, 1372, 564, 656, 721, 1286, 1162, 879, 929, 922, 1668, 1922, 430, 685, 1843, 343, 1132, 1937, 1469, 1057, 53, 882, 555, 1121, 330, 1599, 1973, 574, 712, 649, 1704, 1621, 651, 961, 446, 1235, 316, 896, 1528, 54, 1862, 114, 1157, 310, 13, 1044, 1955, 1481, 1813, 439, 1018, 359, 1323, 1530, 205, 341, 154, 726, 1695, 691, 182, 1967, 378, 92, 392, 1644, 212, 1746, 1700, 1072, 795, 798, 1209, 965, 1362, 1023, 1731, 1902, 1763, 950, 1903, 627, 446, 1122, 1630, 1159, 955, 0, 1968, 1974, 72, 1590, 1614, 1669, 1772, 578, 1534, 1967, 1006, 80, 1664, 786, 94, 1825, 1335, 1496, 134, 4, 663, 742, 1856, 1182, 488, 407, 1719, 1757, 757, 1521, 1969, 298, 1478, 850, 274, 455, 304, 1215, 1745, 1038, 944, 1255, 670, 1310, 246, 876, 10, 1776, 455, 1450, 1388, 1908, 697, 1092, 1675, 439, 160, 1131, 1047, 21, 1114, 670, 228, 481, 173]

def encode_msg(msg):
    m = bin(bytes_to_long(msg))[2:].zfill(N)
    return [0 if c == '0' else 1 for c in m]


def decode_msg(m):
    n = 0
    for b in m:
        n *= 2
        n += b
    return long_to_bytes(n)

Fq = Zmod(q)
Fp = Zmod(p)
Rq = PolynomialRing(Fq, 'x').quotient(x^N - 1)
Rp = PolynomialRing(Fp, 'x').quotient(x^N - 1)
Rx.<x> = PolynomialRing(ZZ, 'x')
Qx = PolynomialRing(QQ, 'x')



def poly_CRT(residues, moduli):
    P.<x> = PolynomialRing(QQ, 'x')
    total = 0
    N = 1
    for n in moduli:
        N *= P(n)
    for i in range(len(residues)):
        Ni = N // moduli[i]
        a = Ni.inverse_mod(moduli[i])
        total += P(residues[i]) * P(a) * P(Ni)
    return total

# Solve script
# lattice attack
# we know that pub * f = p*g


reduced_lattices = []
p1 = Rx(x^70 - x^35 + 1) 
p2 = Rx(x^70 + x^35 + 1) 
p3 = Rx(x^70 - 1)

print (p1 * p2 * p3)

crt_basis = [1/6*x^175 - 1/6*x^140 - 1/3*x^105 - 1/6*x^70 + 1/6*x^35 + 1/3, -1/6*x^175 - 1/6*x^140 + 1/3*x^105 - 1/6*x^70 - 1/6*x^35 + 1/3, 1/3*x^140 + 1/3*x^70 + 1/3]

print(crt_basis)
def p1p2p3_CRT(residues):
    return sum([r * m for r, m in zip(residues, crt_basis)])


rings = []

for c in [p1,p2,p3]:
    print(c)
    R = Rx.quotient(c)
    rings.append(R)


    deg = c.degree()

    conv_matrix = matrix(ZZ, deg, deg, [list(map(ZZ, (R(pub) * x^i).list())) for i in range(0,deg)])

    NTRU_lattice = block_matrix([[identity_matrix(ZZ, deg), conv_matrix], [zero_matrix(ZZ,deg,deg), q * identity_matrix(ZZ,deg)]])

    print("Running BKZ...")
    L = NTRU_lattice.BKZ(delta=0.99, block_size=35)
    print("Finished BKZ...")

    #print("Combinations: " , L.solve_left(vector(target)))

    print("Lattice: ")
    for row in L:
        print(row)

    reduced_lattices.append(L)


# take third row for answer, hopefully this works
f1 = rings[0](list(reduced_lattices[0].rows()[2][:70]))
f2 = rings[1](list(reduced_lattices[1].rows()[2][:70]))
f3 = rings[2](list(reduced_lattices[2].rows()[2][:70]))

print("VALUES")
print(list(f1))
print(list(f2))
print(list(f3))


def find_key(f1, f2, f3):
    for i in range(210):
        for j in range(210):
            f123 = crt_basis[0] * f1.lift() + crt_basis[1] * f2.lift() * x^i + crt_basis[2] * f3.lift() * x^j
            f123 = f123 % (x^210 - 1)
            if len(set(list(f123))) <= 5:
                return f123

fk = find_key(f1, f2, f3)


for i in range(210):
    f_ = (fk * x^i) % (x^210 - 1)
    try:
        print("Found key!")
        v = Rq(f_) * Rq(ct)
        v = ([c.lift_centered() for c in v.list()])

        vp = Rp(v) * Rp(f_).inverse()
        plaintext = [c.lift_centered() for c in vp.list()]
        print(plaintext)
        if all(map(lambda x: x in [0,1], plaintext)):
            print(decode_msg(plaintext))
        if all(map(lambda x: x in [0,-1], plaintext)):
            print(decode_msg([-1 * p for p in plaintext]))
    except:
        pass


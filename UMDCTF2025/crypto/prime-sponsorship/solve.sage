import sage.matrix.matrix_integer_dense_hnf as matrix_integer_dense_hnf


# This might not be the most efficient way to do this. There's probably an algebraic attack 
# that solves x h1 = y (mod X^p1 - x - 1)
#             x h2 = y (mod X^p2 - x - 1)
# for x and y and uses those as a secret key, but I can't figure out a way to get short enough solutions
# from directly solving. If you solved it this way, please let me know!

# Instead we take the intersection of the NTRU lattices defined by the two public keys
# and run BKZ there.

# Taking the intersection is the same as taking the union of the duals, which we can do 
# somewhat quickly

# The BKZ actually is super quick because of the high lattice volume and uniquely short vector.
# The longest part here is the Hermite Normal Form computation. It runs in ~4 minutes on my machine.

p1 = 211
p2 = 223
q = 1511

h1 = [1475, 724, 857, 322, 1405, 898, 1406, 1299, 41, 745, 500, 1382, 196, 77, 882, 25, 774, 293, 135, 961, 1431, 675, 1246, 940, 106, 1286, 1065, 586, 1497, 702, 1213, 900, 246, 282, 1080, 916, 532, 369, 708, 257, 1345, 469, 395, 250, 691, 1216, 819, 566, 56, 1500, 25, 1428, 1104, 262, 537, 253, 1163, 202, 358, 620, 1304, 321, 369, 97, 451, 1122, 624, 441, 1489, 499, 590, 524, 446, 85, 435, 1493, 912, 56, 987, 1076, 439, 829, 66, 177, 113, 491, 644, 894, 732, 503, 112, 1365, 1359, 636, 28, 400, 207, 175, 861, 128, 1087, 945, 582, 14, 778, 1419, 1362, 53, 1208, 84, 1189, 680, 419, 297, 1414, 768, 1506, 1263, 948, 1055, 1007, 385, 837, 195, 1058, 1007, 678, 1007, 696, 1033, 373, 1240, 127, 806, 115, 322, 434, 651, 152, 1180, 911, 868, 1241, 1091, 1469, 440, 204, 719, 1251, 1090, 585, 998, 800, 1057, 1383, 1026, 1349, 51, 1405, 1378, 156, 1473, 413, 1402, 1481, 1488, 680, 31, 516, 87, 1066, 1142, 784, 968, 1120, 987, 676, 1315, 314, 1011, 462, 124, 435, 130, 1486, 331, 706, 509, 1119, 1475, 235, 600, 1143, 460, 874, 274, 351, 1184, 840, 974, 1094, 259, 1090, 1419, 872, 639, 1112, 1313, 263, 1134, 1156]
h2 = [1045, 277, 193, 978, 65, 1224, 1109, 513, 1351, 799, 454, 325, 163, 493, 392, 469, 549, 315, 1110, 759, 359, 85, 541, 744, 165, 1256, 1258, 1414, 31, 116, 230, 947, 1449, 1439, 400, 918, 838, 168, 47, 1325, 702, 610, 1391, 164, 602, 176, 309, 70, 965, 1159, 1016, 231, 1278, 143, 1271, 1383, 1014, 567, 290, 1263, 879, 701, 1310, 443, 713, 1456, 236, 317, 1056, 1159, 1181, 1218, 866, 87, 323, 435, 851, 1216, 1502, 376, 1127, 1454, 1281, 1158, 17, 320, 63, 1161, 1024, 877, 283, 399, 196, 659, 939, 307, 529, 176, 1458, 484, 372, 384, 103, 180, 955, 695, 502, 1456, 945, 914, 389, 249, 1013, 560, 1483, 769, 1089, 264, 753, 1047, 163, 1169, 567, 393, 924, 1473, 402, 519, 963, 1002, 1354, 1248, 91, 67, 1447, 320, 298, 791, 20, 889, 1266, 686, 139, 1417, 960, 963, 66, 26, 128, 591, 689, 1437, 450, 589, 485, 875, 1296, 1482, 350, 323, 1104, 322, 458, 1079, 719, 330, 578, 513, 128, 1322, 886, 1096, 1074, 300, 882, 428, 608, 1250, 1497, 30, 785, 1408, 846, 108, 1043, 619, 465, 1249, 942, 1264, 1219, 843, 459, 1486, 236, 1238, 442, 488, 111, 153, 120, 457, 4, 251, 445, 580, 1276, 581, 1188, 1180, 1345, 1045, 458, 430, 580, 119, 871, 766, 1164, 851, 1182, 53, 1183]
ct = [1017, 1506, 117, 123, 1458, 582, 1491, 1383, 1107, 438, 1263, 825, 1299, 387, 717, 21, 114, 1251, 177, 1338, 192, 102, 141, 9, 459, 669, 381, 369, 144, 459, 759, 1215, 1440, 612, 1305, 1152, 78, 321, 1227, 918, 540, 780, 873, 999, 876, 228, 1041, 852, 1188, 348, 1146, 1257, 975, 33, 1068, 195, 1227, 300, 36, 834, 1227, 540, 168, 690, 1107, 561, 492, 1107, 489, 915, 1191, 129, 144, 249, 186, 519, 1437, 1485, 1332, 852, 288, 123, 1092, 291, 57, 855, 810, 390, 273, 327, 60, 195, 489, 735, 1476, 549, 645, 642, 1434, 768, 789, 108, 1095, 66, 117, 1458, 1233, 846, 891, 594, 447, 117, 306, 339, 1179, 546, 1377, 237, 444, 1242, 1470, 1101, 1200, 345, 1449, 330, 663, 282, 24, 288, 354, 657, 447, 384, 1200, 66, 1332, 138, 1242, 915, 729, 1320, 702, 876, 519, 156, 1179, 993, 378, 1044, 816, 243, 1158, 630, 429, 1416, 516, 720, 852, 1098, 264, 855, 1434, 21, 1032, 822, 60, 669, 681, 465, 30, 972, 873, 837, 687, 1173, 516, 864, 906, 387, 981, 999, 1362, 393, 1347, 48, 528, 738, 1353, 630, 801, 144, 114, 1506, 405, 573, 1008, 246, 1020, 888, 1386, 1458, 1482, 195, 1437, 1164, 1464, 270, 1509, 1071, 987]

pari.allocatemem(2**33)


Fq = GF(q)
F3 = GF(3)
Rm1.<x1> = PolynomialRing(Fq, 'x').quotient(x^p1 - x - 1)
R3 = PolynomialRing(F3, 'x').quotient(x^p1 - x - 1)

Rm2.<x2> = PolynomialRing(Fq, 'x').quotient(x^p2 - x - 1)

Rx.<x> = PolynomialRing(ZZ, 'x')

# multiply by 3 so f is in the lattice instead of 3f 
h1 = 3 * Rx(h1)
h2 = 3 * Rx(h2)

conv_matrix1 = block_diagonal_matrix(matrix(ZZ, [list(map(ZZ, (Rm1(h1) * x1^i).list())) for i in range(0, p1)]), identity_matrix(p2 - p1))

print(conv_matrix1.dimensions())
B1 = block_matrix([[identity_matrix(ZZ, p2), conv_matrix1], [zero_matrix(ZZ,p2,p2), q * identity_matrix(ZZ,p2)]])
print(B1.dimensions())

conv_matrix2 = matrix(ZZ, [list(map(ZZ, (Rm2(h2) * x2^i).list())) for i in range(0, p2)])
B2 = block_matrix([[identity_matrix(ZZ, p2), conv_matrix2], [zero_matrix(ZZ,p2,p2), q * identity_matrix(ZZ,p2)]])
print(B2.dimensions())

print("Computing inverses...")
D1 = (B1.T)^(-1)
D2 = (B2.T)^(-1)
print("Done!")

print("Concatenating duals and calculating HNF...")
D = D1.stack(D2)
D *= q # multiply so it becomes integer lattice
D = D.change_ring(ZZ)
# compute HNF to remove linear dependencies
D = D.echelon_form(proof=False, include_zero_rows=False) # takes a bit
D = D / q # undo multiplication from earlier
print("Done!")

print("Going back to primal...")
G = D.T * D
print(G.dimensions())
Gi = G.inverse()
B = D * Gi
print(B.dimensions())
print("Done!")


print("Running BKZ...")
L = B.BKZ(block_size=5) # LLL might work too
print("Done!")
f = open("lattice_output.txt", 'w')
for row in L:
    f.write(str(row.list()))
    f.write('\n')

for ans in L[0:3]:
    #print(ans)

    f = list(ans[:p1])
    g = list(ans[p2:p2+p1])

    # decrypt ct
    try:
        e = Rm1(3) * Rm1(f) * Rm1(ct)
        e = [ c.lift_centered() for c in e ]
        g_inv = R3(g).inverse()

        print(list(g_inv * R3(e)))
        print()
    except e:
        print(e)
        pass

    #print(S)

import random
random.seed(999999999)
p = list(range(81))
random.shuffle(p)

board = '''
004003050
507100020
090000006
060001200
080000040
003806000
000090100
005417000
000000000
'''.strip().splitlines()

not_constraints = set()
is_constraints = set()

zero_value = 99999

for r in range(9):
	for c1 in range(9):
		if board[r][c1] != '0': is_constraints.add((p[r*9+c1], int(board[r][c1])))
		for c2 in range(c1 + 1, 9):
			not_constraints.add((p[r*9+c1], p[r*9+c2]))
			not_constraints.add((p[r+c1*9], p[r+c2*9]))
for r in range(0, 9, 3):
	for c in range(0, 9, 3):
		for c1 in range(9):
			for c2 in range(c1 + 1, 9):
				rr1 = r + c1 // 3
				cc1 = c + c1 % 3
				rr2 = r + c2 // 3
				cc2 = c + c2 % 3
				not_constraints.add((p[rr1*9+cc1], p[rr2*9+cc2]))
chains = []
chain = [p[0]]
while not_constraints:
	possible = [list(set(i) - {chain[-1]})[0] for i in not_constraints if chain[-1] in i]
	if possible:
		other = random.choice(possible)
		not_constraints -= {(other, chain[-1])}
		not_constraints -= {(chain[-1], other)}
		chain.append(other)
	else:
		chains.append(chain)
		chain = [random.choice(random.choice(list(not_constraints)))]
chains.append(chain)

q = list(range(81))
random.shuffle(q)
p0idx = q.index(p[0])
q[p0idx], q[-1] = q[-1], q[p0idx]
print(" != 0 != ".join(f"s[{j}]" for j in q))

for i in chains:
	print(" != ".join(f"s[{j}]" if j != zero_value else "0" for j in i))

for i in range(9, 0, -1):
	idxs = [j for j,k in is_constraints if k == i]
	random.shuffle(idxs)
	print(f" == ".join([f"s[{j}]" for j in idxs]) + " > ", end='')
print()
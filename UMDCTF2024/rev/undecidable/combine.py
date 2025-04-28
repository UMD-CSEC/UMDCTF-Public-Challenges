with open("original.txt") as f, open("checker.txt") as g, open("combined.txt", "w") as h:
	lines_f = f.read().splitlines()
	lines_g = g.read().splitlines()
	n_lines = len(lines_f) + len(lines_g) - 1
	for i in lines_g:
		state, w0, d0, n0, w1, d1, n1 = i.split()
		h.write(f"{state} {w0} {d0} {n0} {w1} {d1} {n1}\n")
	for i in lines_f:
		state, w0, d0, n0, w1, d1, n1 = i.split()
		h.write(f"{int(state)+len(lines_g)} {w0} {d0} {int(n0)+len(lines_g)} {w1} {d1} {int(n1)+len(lines_g)}\n")
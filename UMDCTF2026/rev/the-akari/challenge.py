import json, gzip
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

board = []
with open("board.txt.gz", "rb") as f:
	board_str = gzip.decompress(f.read()).decode()
	for line in board_str.splitlines():
		board.append(list(line))

soln = json.loads(input("solution: "))

for (r,c) in soln:
	if board[r][c] == " ":
		board[r][c] = "O"

for r in range(len(board)):
	for c in range(len(board[0])):
		if board[r][c] in "O ":
			neighbors = []
			rr, cc = r, c
			while 1:
				rr += 1
				if board[rr][cc] in "O ": neighbors.append(board[rr][cc] == "O")
				else: break
			rr, cc = r, c
			while 1:
				rr -= 1
				if board[rr][cc] in "O ": neighbors.append(board[rr][cc] == "O")
				else: break
			rr, cc = r, c
			while 1:
				cc += 1
				if board[rr][cc] in "O ": neighbors.append(board[rr][cc] == "O")
				else: break
			rr, cc = r, c
			while 1:
				cc -= 1
				if board[rr][cc] in "O ": neighbors.append(board[rr][cc] == "O")
				else: break
			neighbor_sum = sum(neighbors)
			if board[r][c] == "O":
				assert neighbor_sum == 0
			else:
				assert neighbor_sum > 0
		elif board[r][c] in "01234":
			neighbor_sum = 0
			for rr, cc in [(r,c+1),(r,c-1),(r+1,c),(r-1,c)]:
				neighbor_sum += board[rr][cc] == "O"
			assert neighbor_sum == int(board[r][c])

bits = []
for i in range(128):
	bits.append(int(board[2][22 + i*48] == "O"))
for i in range(128):
	bits.append(int(board[23 + i*40][1] == "O"))

key = bytes([int(''.join(map(str,bits[i:i+8]))[::-1], 2) for i in range(0, len(bits), 8)])

with open("flag_enc.bin", "rb") as f:
	ct = f.read()
iv, ct = ct[:16], ct[16:]

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
flag = unpad(cipher.decrypt(ct), 16)
print(f"{flag = }")
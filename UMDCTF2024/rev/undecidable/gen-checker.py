with open("flag.txt", "rb") as f:
	flag = f.read()
bits = list(map(int, ''.join(f'{x:08b}'[::-1] for x in flag)))

lines = []

state = 1

for i in range(len(bits) // 2):
	lines.append([state+0, 0, 'R', state+1, 1, 'R', state+1]) # 0
	lines.append([state+1, 0, 'R', state+2, 1, 'L', state+8]) # 1
	lines.append([state+2, 0, 'L', state+3, 1, 'L', state+4]) # 2
	lines.append([state+3, 0, 'L', state+5, 1, 'L', state+5]) # 1
	lines.append([state+4, 0, 'L', state+6, 1, 'L', state+6]) # 1
	lines.append([state+5, 0, 'R', state+7, 1, 'R', state+7]) # 0
	lines.append([state+6, 1, 'R', state+7, 0, 'R', state+7]) # 0
	lines.append([state+7, 0, 'R', state+0, 0, 'R', state+0]) # 1
	lines.append([state+8, 0, 'L', state+9, 1, 'L', state+9]) # 0
	lines.append([state+9, 1, 'L', state+10, 1, 'L', state+10]) # -1
	state += 10
	lines.append([state+0, 0, 'L', state+1, 1, 'L', state+1]) # 0
	lines.append([state+1, 0, 'L', state+2, 1, 'R', state+8]) # 1
	lines.append([state+2, 0, 'R', state+3, 1, 'R', state+4]) # 2
	lines.append([state+3, 0, 'R', state+5, 1, 'R', state+5]) # 1
	lines.append([state+4, 0, 'R', state+6, 1, 'R', state+6]) # 1
	lines.append([state+5, 0, 'L', state+7, 1, 'L', state+7]) # 0
	lines.append([state+6, 1, 'L', state+7, 0, 'L', state+7]) # 0
	lines.append([state+7, 0, 'L', state+0, 0, 'L', state+0]) # 0
	lines.append([state+8, 0, 'R', state+9, 1, 'R', state+9]) # 0
	lines.append([state+9, 1, 'R', state+10, 1, 'R', state+10]) # -1
	state += 10
lines.append([state+0, 0, 'L', state+1, 1, 'L', state+1])
lines.append([state+1, 0, 'R', state+2, 1, 'L', state+0])
lines.append([state+2, 0, 'R', state+3, 0, 'R', state+3])
lines.append([state+3, 0, 'R', state+4, 0, 'R', state+4])
state += 4

start = 0
end = len(bits) - 1
for i in range(len(bits) // 2):
	for j in range(start, end):
		bits[j] ^= bits[j+1]
	end -= 1
	for j in range(end, start, -1):
		bits[j] ^= bits[j-1]
	start += 1

last_state = state+2*len(bits) + 1

for i, bit in enumerate(bits):
	if bit == 0: lines.append([state+2*i, 0, 'R', state+2*i+1, 0, 'R', last_state])
	if bit == 1: lines.append([state+2*i, 0, 'R', last_state, 0, 'R', state+2*i+1])
	lines.append([state+2*i+1, 0, 'R', state+2*i+2, 0, 'R', state+2*i+2])
lines.append([state+2*i+2, 0, 'R', 0, 0, 'R', 0])

with open("checker.txt", "w") as f:
	for i in lines:
		f.write(" ".join(map(str, i)) + '\n')
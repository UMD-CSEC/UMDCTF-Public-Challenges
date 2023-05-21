f = open("pokecomms.txt", "r")
lines = f.readlines()
f.close()
res = ""

for line in lines:
	curr = line.split(" ")
	bits = ""
	for word in curr:
		if word.strip() == "CHU!":
			bits += "0"
		if word.strip() == "PIKA":
			bits += "1"
	res += str(chr(int(bits,2)))
print(res)
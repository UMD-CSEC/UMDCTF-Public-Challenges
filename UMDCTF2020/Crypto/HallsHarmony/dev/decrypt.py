f = open('ciphertext', 'r')
ctext = f.read()
f.close()

ptext = ""
i = 0
while i < len(ctext):
	p1 = (ord(ctext[i]) - 97) * 49
	p2 = (ord(ctext[i+1]) - 97) * 7
	p3 = (ord(ctext[i+2]) - 97)
	ptext += chr(p1 + p2 + p3)
	i += 3
print(ptext)

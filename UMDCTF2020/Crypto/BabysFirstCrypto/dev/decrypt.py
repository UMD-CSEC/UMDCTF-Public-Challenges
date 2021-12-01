def decrypt(ctext):
	ptext = ""
	for c in ctext:
		ptext += chr((ord(c) - 13) % 128)
	return ptext

f = open('../prod/ciphertext', 'r')
ctext = f.read()
f.close()
print(decrypt(ctext))

def encrypt(flag):
	ctext = ""
	for c in flag:
		ctext += chr((c + 13) % 128)
	return ctext

flag = "UMDCTF-{1_1uv_crypt0}".encode('utf-8')
ctext = encrypt(flag)
f = open('../prod/ciphertext', 'w')
f.write(ctext)
f.close()

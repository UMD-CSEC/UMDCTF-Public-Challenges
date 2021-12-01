flag = "UMDCTF-{cl@ss1c4l_crypt0}"

ctext = ""
i = 0
while i < len(flag):
	ctext += chr(97 + (ord(flag[i]) // 49) % 7)
	ctext += chr(97 + ((ord(flag[i]) // 7 ) % 7))
	ctext += chr(97 + (ord(flag[i]) % 7))
	i += 1
f = open('ciphertext', 'w')
f.write(ctext)

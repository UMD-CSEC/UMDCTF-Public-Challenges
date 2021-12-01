import base64

ctext = b'UMDCTF-{b@se64_15_my_f@v0r1t3_b@s3}'
i = 0
while i < 42:
	print(i)
	ctext = base64.b64encode(ctext)
	i += 1
f = open('../prod/ciphertext', 'wb')
f.write(ctext)
f.close()

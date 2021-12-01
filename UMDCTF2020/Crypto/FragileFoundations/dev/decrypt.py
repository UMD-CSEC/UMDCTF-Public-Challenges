import base64
import binascii

f = open('../prod/ciphertext', 'rb')
ctext = f.read()
i = 0
while True:
	try:
		ctext = base64.b64decode(ctext)
	except binascii.Error:
		break
print(ctext.decode('utf-8'))

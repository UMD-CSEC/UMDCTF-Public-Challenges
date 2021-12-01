import json

def convert_to_base_16(ptext):
	ctext = ''
	for c in ptext:
		ctext += chr(ord(c) // 16 + 97)
		ctext += chr(ord(c) % 16 + 97)
	return ctext

def encrypt(ptext):
	f = open('jsondata.json', 'r')
	text = f.read()
	pigpen = json.loads(text)
	ctext = ''
	for c in ptext:
		ctext += pigpen[c] + " "
	return ctext

flag = "UMDCTF-{1_l0v3_p1gp3n_c1ph3r1ng}"
b16 = convert_to_base_16(flag)
ctext = encrypt(b16)
f = open('../prod/ciphertext', 'w')
f.write(ctext)
f.close()

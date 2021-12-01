import socket
import sys
import base64

def recvall(c):
	plaintext = b''
	max_size = 1024
	while len(plaintext) < max_size:
		b = c.recv(1)
		if b == b'\n':
			return plaintext
		plaintext += b
	return None

def decrypt(ctext):
	s = socket.socket()
	host = '192.241.138.174'
	port = 1337
	s.connect((host, port))
	recvall(s)
	ciphertext = base64.b64encode(ctext)
	s.send(ciphertext + b'\n')
	result = recvall(s)
	s.close()
	return result == b'You are not allowed to decrypt!'

def set(s, i, v):
	return s[:i] + bytes([v]) + s[i + 1:]

def attack(ciphertext):
	length = 16
	for i in range(16, 32):
		ciphertext = set(ciphertext, i, ciphertext[i] + 1)
		if not decrypt(ciphertext):
			ciphertext = set(ciphertext, i, ciphertext[i] - 1)
			length = 32 - i
			break
		ciphertext = set(ciphertext, i, ciphertext[i] - 1)
	fblock = b'\x00' * 48
	ptext = b'\x00' * 32
	paddingStart = 48 - length;

	for i in range(paddingStart, 48):
		fblock = set(fblock, i, length ^ ciphertext[i-16])
	for i in range(paddingStart - 1, 31, -1):
		modifiable = ciphertext[:]
		for j in range(i + 1, 48):
			modifiable =  set(modifiable, j-16, (48 - i) ^ fblock[j])
		for j in range(0, 256):
			modifiable = set(modifiable, i - 16,  j)
			if decrypt(modifiable):
				fblock = set(fblock, i, j ^ (48 - i))
				break

		ptext = set(ptext, i - 16, ciphertext[i-16] ^ fblock[i])

	for i in range(31, 15, -1):
		modifiable = ciphertext[:]
		for j in range(i + 1, 32):
			modifiable =  set(modifiable, j-16, (32 - i) ^ fblock[j])
		for j in range(0, 256):
			modifiable = set(modifiable, i - 16,  j)
			if decrypt(modifiable[:32]):
				fblock = set(fblock, i, j ^ (32 - i))
				break
		ptext = set(ptext, i - 16, ciphertext[i-16] ^ fblock[i])
	print(ptext.decode('utf-8'))

f = open('ciphertext', 'rb')
ciphertext = f.read()
ciphertext = base64.b64decode(ciphertext)
f.close()
attack(ciphertext)

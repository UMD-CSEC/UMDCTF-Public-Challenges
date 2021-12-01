import base64

f = open('shrew.txt', 'r')
shrew = f.read()
f.close()
flag = b'UMDCTF-{shr3w_l3tt3r}'
b64flag = base64.b64encode(flag).decode('utf-8')
last_pos = 0
new_shrew = ""
for c in b64flag:
	if c not in shrew[last_pos:]:
		print("Letter not found :( " + c + ":" + str(last_pos))
		exit()
	pos = shrew.index(c, last_pos)
	new_shrew += shrew[last_pos:pos] + '~'
	last_pos = pos + 1
new_shrew += shrew[last_pos:]
f = open('../prod/shrew.txt', 'w')
f.write(new_shrew)
f.close()

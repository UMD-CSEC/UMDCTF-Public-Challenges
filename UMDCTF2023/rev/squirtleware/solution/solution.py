import requests
import base64

# Known "protocol" header (and end)
HDR = "squirtlenespanol"
# Padding between header/footer and content
PADDING = b'0' * 8

# app url
base_url = 'http://localhost:8080'

# junk, only thing that matters is node
login_params={"name": "wartortle", "node": 420}
resp = requests.post(url=base_url + "/squirtle/i-love-shakira", json=login_params)
token_json = resp.json()
token = token_json['token']
print(f'token: {token}')

bandera_enc = base64.b64encode(b'bandera')
flag_params={"type": "BANDERA_COMPLETA_POR_FAVOR", "data": bandera_enc.decode()}
resp = requests.post(url=base_url + "/connection", json=flag_params, cookies={'token': token})
content = resp.content
skip = len(HDR) + len(PADDING) + 1
print(f'status: {resp.reason}')
print(f'content length: {len(content)}')

content = content[skip:len(content)-skip:]

decrypted = []
for idx, x in enumerate(content):
	decrypted.append(x ^ ord(token[idx % len(token)]))

decrypted = bytes(decrypted)
print(f'decrypted_len: {len(decrypted)}')

# decode
decoded = base64.b64decode(decrypted.decode())
f = open('flag.png', 'wb')
f.write(decoded)
f.close()

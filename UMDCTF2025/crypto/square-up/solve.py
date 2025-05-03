from Crypto.Util.number import bytes_to_long, long_to_bytes
from math import gcd

def decrypt(c, lp, lq):
	yq = pow(q, -1, p)
	yp = (1 - yq * q) // p

	mp = pow(c, (p+1)//4, p)
	mq = pow(c, (q+1)//4, q)
	
	if (pow(mp, (p-1)//2, p) - lp) % p != 0: mp = p - mp
	if (pow(mq, (q-1)//2, q) - lq) % q != 0: mq = q - mq

	return (yp * p * mq + yq * q * mp) % N

N = 1298690852855676717877172430649235439701166577296380685015744142960768447038281361897617173145966407353660262643273693068083328108519398663073368426744653753236312330497119252304579628565448615356293308415969827357877088267274695333
(c, lp, lq) = (162345251908758036296170413099695514860545515965805244415511843227313118622229046299657295062100889503276740904118647336251473821440423216697485906153356736210597508871299190718706584361947325513349221296586217139380060755033205077, 1, -1)
p = gcd(bytes_to_long(b'\x1bR \xc4\xf0\x8f\xa7l\xa4\xdd\xbf\xf73\xf3\xe9(\xc8Q\xdd\xbd,\x08\xbd\x7f\xafm\x9b\xbf\xa0\xbe\xd4)t\xd4e\xc0,J\xb8H\x93i\xea\xbcy\x9a7AA\xeb]q\xae\x00\xebJ(Y\x8a\xa4B\xdc\t(\x8b\xcef&@b\x91\x06Y~\x88m\xaf\x9bl\\\x12\xf2\x9f\xe1\x1f\x18q\x16\xd8\xb4\x9f$\x88%8\x0f')**2 - c, N)
q = N//p
print(f"{long_to_bytes(decrypt(c, lp, lq)) = }")
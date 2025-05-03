import random
import time

seed = int(time.time())
random.seed(seed)

plaintext = b"UMDCTF{REDACTED}"
keystream = bytes([random.getrandbits(8) for _ in range(len(plaintext))])
ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])

with open("secret.bin", "wb") as f:
    f.write(ciphertext)

import random
import time
import datetime

with open("secret.bin", "rb") as f:
    cipher = f.read()

known_prefix = b"UMDCTF{"
prefix_len = len(known_prefix)

dt = datetime.datetime(2025,4,23,18,35,10)
seed = int(time.mktime(dt.timetuple()))
random.seed(seed)
guess_keystream = bytes([random.getrandbits(8) for _ in range(prefix_len)])
decrypted_prefix = bytes([c ^ k for c, k in zip(cipher[:prefix_len], guess_keystream)])

if decrypted_prefix == known_prefix:
    print(f"[+] Found seed: {seed}")
    # Decrypt full message
    random.seed(seed)
    full_keystream = bytes([random.getrandbits(8) for _ in range(len(cipher))])
    decrypted = bytes([c ^ k for c, k in zip(cipher, full_keystream)])
    print("Flag:", decrypted.decode())

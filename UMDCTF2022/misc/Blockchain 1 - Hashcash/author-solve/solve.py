import hashlib
import random
import os
import base64
import datetime
from pwn import *

conn = remote('127.0.0.1', 50001)
print(conn.recv().decode())
conn.send('y\n'.encode())
print(conn.recv().decode())

r = os.urandom(5)
d = datetime.date.today().strftime('%Y%m%d')[2:]
nonce = base64.b64encode(r).decode()
for counter in range(0, pow(2,30)):
    cnt = base64.b64encode(str(counter).encode()).decode()
    message = f"1:20:{d}:gary@hashcash.com::{nonce}:{cnt}"
    hashed = hashlib.sha1(message.encode()).hexdigest()
    #print(f'{message} --- {hashed[0]} {hashed[1]} {hashed[2]} {hashed[3]} {hashed[4]}')
    #print(f'{message} --- {hashed}')
    if hashed[0:5] == "00000": 
        print("found!!")
        print(f'{message} --- {hashed}')
        break

conn.send(f'{message}\n'.encode())
print(conn.recv().decode())

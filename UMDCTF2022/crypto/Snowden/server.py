import socket
import random
import threading
from _thread import *
import time
from Crypto.PublicKey import RSA
from Crypto.Util.number import long_to_bytes, bytes_to_long

def threading(conn):
    conn.sendall(initial.encode())

    while True:
        keys = gen_keys(FLAG, 2048)
        data = conn.recv(1024).decode()
        if data.lower() == "y\n":
            conn.sendall((str(keys)+"\n\n"+next_msg).encode())
        else:
            print('closing connection to', addr)
            break

    conn.close()

def gen_keys(p, bits):
    # message needs to be less than the smallest public modulus (N)
    # message needs to be bigger so that p^e > n 

    e = 0
    while e % 2 == 0:
        e = random.randint(20,31)
    p = bytes_to_long(p.encode())
    new_key = RSA.generate(bits, e=e).publickey()
    c = pow(p, new_key.e, new_key.n)
    return {'n': new_key.n, 'e': new_key.e, 'c': c}


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 60001        # Port to listen on (non-privileged ports are > 1023)
FLAG = "I'm just patiently waiting for someone to finally be able to decrypt this message. UMDCTF{y0u_r3ally_kn0w_y0ur_br04dc45t_4tt4ck!}"

initial = "Eddy Snowden setup a beacon constantly transmitting an encyrypted secret message, but he is always changing the public key for some reason. We've rigged up this intermediary to give you access to his encrypted transmissions. Would you like to capture a transmission? (y/n) "
next_msg = "Want another one? (y/n) "

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("\n")
        start_new_thread(threading, (conn, ))
    s.close()

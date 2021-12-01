import string
import random
import socket
import threading
from _thread import *
import time

FLAG = "REDACTED"
code = "REDACTED"
HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 12347        # Port to listen on (non-privileged ports are > 1023)

def threading(conn):
    conn.sendall(initial.encode())
    data = conn.recv(1024).decode()

    if data == "\n":
        values = give_values()
        print(values)
        print(('\n'.join(values)).encode())
        conn.sendall(('\n'.join(values)+'\n\nCode: ').encode())
        start_timer = time.perf_counter()
    else:
        conn.close()

    data = conn.recv(1024).decode().split('\n')[0]
    print(f'{data}\n{code}')
    end_timer = time.perf_counter()

    print("Start: {}\nFinish: {}\nExcecution Time: {}".format(start_timer, end_timer, int(end_timer - start_timer)))

    if data and data in code:
        if int(end_timer - start_timer) <= 5:
            conn.sendall("\nCongrats! You've successfully defused the bomb! Phew... Here is a flag for our appreciation:\n{}".format(FLAG).encode())
        else:
            conn.sendall("That took more than 5 seconds :(".encode())
    else:
        conn.sendall("That was wrong :(".encode())
    print('closing connection to', addr)
    conn.close()

def print_mode(mstring):
    print(max(set(mstring), key=mstring.count))

def generate_string():
    possible = string.ascii_lowercase + string.ascii_lowercase + string.digits + '_-{}'
    return [random.choice(possible) for i in range(1000)]

def give_values():
    total = []
    for i in range(len(code)):
        test = generate_string()
        c = code[i]
        for i in range(100):
            num = random.randint(0,999)
            test[num] = c
        total.append(''.join(test))
    return total

initial = "Hurry someone lost the code that stops the bomb! Find and decode it. Time is running out...\n\nPress Enter to begin"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("\n")
        start_new_thread(threading, (conn, ))
    s.close()

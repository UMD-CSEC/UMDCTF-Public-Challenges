import socket
import random
import threading
from _thread import *
import time

def threading(conn):
    arr = send_arr()
    summ, i, j = find_indices(arr)
    conn.sendall(initial.encode())
    data = conn.recv(1024).decode()

    if data == "\n":
        conn.sendall((str(arr)+"\n\n").encode())
        start_timer = time.perf_counter()
    else:
        conn.close()

    data = conn.recv(1024).decode()
    end_timer = time.perf_counter()

    print("Start: {}\nFinish: {}\nExcecution Time: {}".format(start_timer, end_timer, int(end_timer - start_timer)))

    if data:
        data2 = data.split(', ')
        if int(data2[0]) == summ and int(data2[1]) == i and int(data2[2]) == j and int(end_timer - start_timer) <= 5:
            conn.sendall("Oh YES! I'm free! Here, a token of my appreciation:\n{}".format(FLAG).encode())
        elif int(end_timer - start_timer) > 5:
            conn.sendall("That took more than 5 seconds :(".encode())
        else:
            conn.sendall("That was wrong :(".encode())
        print('closing connection to', addr)
    
    conn.close()


# Stolen from Wikipedia lol
def find_indices(numbers):
    """Find a contiguous subarray with the largest sum."""
    best_sum = 0  # or: float('-inf')
    best_start = best_end = 0  # or: None
    current_sum = 0
    for current_end, x in enumerate(numbers):
        if current_sum <= 0:
            # Start a new sequence at the current element
            current_start = current_end
            current_sum = x
        else:
            # Extend the existing sequence with the current element
            current_sum += x

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = current_end

    return best_sum, best_start, best_end

def send_arr():
    arr = []
    for i in range(20000):
        arr.append(random.randint(-100, 100))
    return arr

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
FLAG = "UMDCTF-{K4d4n35_41g0r1thm}"

initial = "\n" + \
"██   ██ ███████ ██      ██████  \n██   ██ ██      ██      ██   ██  \n███████ █████   ██      ██████   \n██   ██ ██      ██      ██       \n██   ██ ███████ ███████ ██       \n\n" + \
"I've been stuck in this room for some time now. They locked me in here and told\n" + \
"me the only way I can leave is if I solve their problem within five seconds. \n" + \
"I've tried so much, but my algorithm keeps going over the time. Can you help me?\n\n" + \
"What I have to do is find the maximum contiguous sub-array within this array of \n" + \
"numbers. They keep telling me my algorithm isn't efficient enough! If you can \n" + \
"send me the indices of this array, I might live to see another day.\n\n" + \
"Format: \"sum, i, j\" " + \
"Example: 103, 345, 455\n\n" + \
"sum = the maximum contiguous sum\ni = start index of sub-array\nj = end index of sub-array\n\n" + \
"Press Enter to get the arr\n\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("\n")
        start_new_thread(threading, (conn, ))
    s.close()

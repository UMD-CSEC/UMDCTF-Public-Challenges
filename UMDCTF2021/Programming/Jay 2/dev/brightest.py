import socket
import random
import threading
from _thread import *
import time

def threading(conn):
    arr = send_2d_arr()
    summ, row_start, row_end, col_start, col_end = find_indices(arr)
    print(f'Sum: {summ}\nrow_start = {row_start}\nrow_end = {row_end}\ncol_start = {col_start}\ncol_end = {col_end}')
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
        if int(data2[0]) == summ and int(data2[1]) == row_start and int(data2[2]) == row_end and int(data2[3]) == col_start and int(data2[4]) == col_end and int(end_timer - start_timer) <= 10:
            conn.sendall("Oh YES! I'm free! Here, a token of my appreciation:\n{}".format(FLAG).encode())
        elif int(end_timer - start_timer) > 10:
            conn.sendall("That took more than 5 seconds :(".encode())
        else:
            conn.sendall("That was wrong :(".encode())
        print('closing connection to', addr)
    
    conn.close()


def find_indices(arr):
    maxSum = 0
    for i in range(len(arr)):
        S = [0 for h in range(len(arr[i]))]
        for j in range(i,len(arr)):
            for k in range(len(S)):
                S[k] = S[k] + arr[j][k]
            M, max_start, max_end = kadanes(S)
            if (M > maxSum):
                maxSum = M
                max_sub_start_row = i
                max_sub_end_row = j
                max_sub_start_col = max_start
                max_sub_end_col = max_end

    return maxSum, max_sub_start_row, max_sub_end_row, max_sub_start_col, max_sub_end_col

# Stolen from Wikipedia lol
def kadanes(numbers):
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

        #print("{} > {}".format(current_sum, best_sum))
        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = current_end

    return best_sum, best_start, best_end

def send_2d_arr():
    arr = []
    for i in range(300):
        inner_arr = []
        for j in range(300):
            inner_arr.append(random.randint(-100, 100))
        arr.append(inner_arr)
    return arr

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65433        # Port to listen on (non-privileged ports are > 1023)
FLAG = "UMDCTF-{Pr0f3ss0r_Gr3n4nd3r}"

initial = "\n" + \
"███████ ████████ ██    ██  ██████ ██   ██ \n██         ██    ██    ██ ██      ██  ██  \n███████    ██    ██    ██ ██      █████   \n     ██    ██    ██    ██ ██      ██  ██  \n███████    ██     ██████   ██████ ██   ██ \n\n" + \
"Welp that didn't work. As soon as they took me out of this place, they dragged me\n" + \
"to another room and told me to solve another stupid puzzle. You think you could help\n" + \
"me with this one as well? This was all they gave me:\n\n" + \
"\"You are given a 2-dimensional array of values for an image. Find the\n" + \
"brightest subregion of the image (the bigger the number, the brighter). A " + \
"subregion (rectangular) can range from one pixel to the whole \n" + \
"image. You can assume the image has the same width and height.\"\n\n" + \
"They also gave me an example for clarification:\n" + \
"|-----|-----|-----|-----|-----|\n|     |     |     |     |     |\n|  6  | -5  | -7  |  4  | -4  |\n|     |     |     |     |     |\n|-----|-----|-----|-----|-----|\n|     |     |     |     |     |\n| -9  |  3  | -6  |  5  |  2  |\n|     |     |     |     |     |\n|-----|-----|-----|-----|-----|\n|     |     |     |     |     |\n| -10 |  4  |  7  | -6  |  3  |\n|     |     |     |     |     |\n|-----|-----|-----|-----|-----|\n|     |     |     |     |     |\n| -8  |  9  | -3  |  3  | -7  |\n|     |     |     |     |     |\n|-----|-----|-----|-----|-----|\n\n" + \
"Format: \"sum, row_start, row_end, col_start, col_end\" " + \
"Example: 17, 2, 3, 1, 2\n\n" + \
"sum = the maximum subregion sum\nrow_start = row index of top left\nrow_end = row index of bottom right\ncol_start = col index of top left\ncol_end = col index of bottom right\n\n" + \
"Press Enter to get the 2D array\n\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("\n")
        start_new_thread(threading, (conn, ))
    s.close()

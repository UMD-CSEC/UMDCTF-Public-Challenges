# import socket programming library
import socket
import json
import base64
import string
import numpy as np

# import thread module
from _thread import *
import threading
import random
import ctypes

host = "0.0.0.0"
port = 1337

#Stop peaking at the solution!!!
solution = [-1, 4, 2, 4, 2, 4, 2, 4, 2, 4, 1, 4, 2, 4, 2, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 2, 4, 1, 4, 2, 4, 2, 4, 2, 3, 1, 3, 1, 3, 2, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 3, 1, 3, 1, 3, 1, 3, 2, 3, 1, 3, 2, 3, 1, 4, 1, 3, 1, 4, 2, 4, 1, 4, 2, 3, 2, 4, 2, 4, 2, 3, 1, 3, 1, 3, 1, 3, 2, 3, 1, 4, 1, 4, 1, 3, 1, 4, 2, 4, 2, 4, 1, 4, 2, 3, 2, 4, 2, 4, 2, 3, 2, 4, 2, 3, 1, 3, 1, 3, 1, 4, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 1, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 3, 1, 3, 2, 3, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 1, 3, 1, 4, 2, 4, 2, 3, 2, 3, 2, 3, 2, 4, 1, 4, 2, 4, 2, 3, 1, 3, 1, 4, 1, 3, 2, 3, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 2, 4, 2, 3, 2, 4, 2, 4, 2, 3, 1, 3, 1, 3, 1, 3, 1, 3, 2, 3, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 1, 4, 1, 4, 1, 4, 2, 4, 2, 4, 2, 3, 1, 3, 1, 3, 1, 3, 1, 4, 1, 3, 1, 3, 1, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 3, 1, 3, 1, 3, 2, 3, 2, 3, 1, 3, 2, 3, 1, 3, 1, 4, 1, 3, 1, 3, 1]
solution_resp = [-1, 1, 5, 2, 8, 2, 4, 6, 2, 2, 2, 4, 2, 3, 1, 1, 1, 2, 2, 6, 4, 6, 4, 4, 8, 1, 1, 1, 1, 2, 6, 4, 4, 4, 2, 2, 6, 4, 4, 3, 1, 1, 3, 4, 2, 2, 4, 4, 2, 4, 2, 2, 8, 2, 6, 1, 1, 1, 1, 10, 4, 2, 2, 4, 6, 2, 6, 1, 1, 1, 5, 2, 2, 2, 2, 2, 2, 4, 4, 2, 2, 2, 6, 2, 4, 7, 1, 1, 9, 6, 4, 12, 2, 2, 6, 2, 6, 1, 1, 1, 1, 2, 2, 2, 2, 6, 2, 2, 10, 2, 2, 4, 4, 13, 1, 1, 5, 2, 2, 4, 2, 8, 2, 2, 2, 4, 2, 2, 4, 2, 4, 3, 1, 1, 5, 2, 2, 2, 2, 2, 2, 6, 2, 4, 2, 4, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 2, 6, 4, 4, 1, 1, 1, 7, 4, 4, 10, 4, 4, 12, 1, 1, 1, 3, 4, 2, 8, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 4, 2, 6, 5, 1, 1, 11, 2, 4, 2, 4, 8, 4, 2, 2, 6, 2, 3, 1, 1, 3, 2, 4, 8, 4, 2, 2, 2, 4, 6, 2, 3, 1, 1, 1, 2, 2, 4, 6, 2, 2, 2, 2, 2, 6, 2, 4, 5, 1, 1, 7, 2, 8, 6, 2, 2, 2, 2, 2, 2, 2, 4, 8, 1, 1, 1, 1, 4, 6, 2, 2, 8, 2, 2, 4, 6, 4, 1, 1, 1, 5, 2, 4, 6, 6, 4, 2, 4, 2, 3, 1, 1, 1, 2, 6, 4, 4, 2, 2, 4, 4, 2, 2, 2, 2, 2, 2, 2, 8, 2, 4, 1, 1]


def lsfr(seed):
    while True:
        seed = np.int32(seed ^ np.int32(seed >> 7))
        seed = np.int32(seed ^ np.int32(seed << 9))
        seed = np.int32(seed ^ np.int32(seed >> 13))
        yield seed

def knuth(seed:int):
    x = list(string.ascii_lowercase)
    gen = lsfr(seed)
    for i in range(len(x)-1, 0, -1):
        j = next(gen) % 26
        x[i], x[j] = x[j], x[i]
    return ''.join(x)

def i2t(x):
    d = {1:'up', 2:'down', 3:'left', 4:'right'}
    return d[x]

secret = 57346
test = 0
def gen_challenge():
    """Generate the challenge and answer for client"""
    chall = random.randrange(65535)
    answer = knuth(chall ^ secret)
    print(answer)
    return chall, answer

def process(data, state, answer):
    """Process client 'data', 'state' is internally maintained, 
       'answer' used to check chall_resp"""
       
    reply = {'flag':'','distance':0, 'challenge':0}
    msg = json.loads(base64.b64decode(data))
    print(msg)
    
    if msg['move'] == 'hello':
        challenge,answer = gen_challenge()
        reply['challenge'] = challenge
        reply['result'] = "SUCCESS"
        return reply, answer, True

    #handle general
    if msg['chall_resp'] == answer and msg['move'] == i2t(solution[state]):
        reply['result'] = 'SUCCESS'
        alive = True
        if state == len(solution)-1:
            reply['result'] = 'WINNER'
            reply['flag'] = 'RZT=gR7Nd(Luhq0XLWO5F>_x~axisdeE' #python uses ipv6 alphabet?
            alive = False 
        challenge,answer = gen_challenge()
        reply['challenge'] = challenge
        reply['distance'] = solution_resp[state]
        return reply, answer, alive
    
    else:
        reply['result'] = 'FAILURE'
        return reply, answer, False

def threaded(c):
    state = 0
    answer = None
    alive = True
    while True:
        data = c.recv(1024)
        if not data:
            break

        #Process data from client, answer gets updated each loop
        try:
            resp, answer, alive = process(data, state, answer)
        except Exception as e:
            print(e)
            resp = {'result': 'FAILURE', 'challenge':0, 'distance':0 }
            alive = False
       
        print('state:', state, 'resp:', resp)
        #increase state
        state += 1
        c.send(base64.b64encode(bytes(json.dumps(resp), encoding='utf-8'))+b'\n')
        if not alive:
            c.close()
            return

def Main():
    global port
    global host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)
    s.listen(5)
    print("socket is listening")

    while True:
        c, addr = s.accept()
        print('Connected to :', addr[0], ':', addr[1])
        start_new_thread(threaded, (c,))
    s.close()


if __name__ == '__main__':
    Main()


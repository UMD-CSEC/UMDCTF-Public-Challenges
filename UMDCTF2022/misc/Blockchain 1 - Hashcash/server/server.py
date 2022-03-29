import socket
import random
import threading
import hashlib
from _thread import *
import datetime
import base64

def threading(conn):
    conn.sendall(initial.encode()) # sends initial message

    # This is the main while loop for sending and receiving data to the client
    while True:
        data = conn.recv(1024).decode()
        if data.lower() == "y\n":
            conn.sendall(b"X-Hashcash: ")
            data = conn.recv(1024).decode()
            msg = ""
            msg, t = check_format(data)
            
            if t:
                msg, t = check_email(data)
                if t:
                    msg, t = check_proof(data)
                    if t:
                        conn.sendall((FLAG).encode())
                        break

            conn.sendall((msg + '\n\n'+ next_msg).encode())
        else:
            print('closing connection to', addr)
            break

    conn.close()

def check_format(sent_data):
    data = sent_data.strip().split(':') 
    t = datetime.datetime.today()
    msg = ""

    # version 1, correct number of parts, 20 leading zeros
    if int(data[0]) and len(data) == 7 and int(data[1]) == 20:
        d = data[2]

        # the date length is 6 (correct format), the year is correct
        if len(d) == 6:
            try:
                x = datetime.datetime(int(d[0:2])+2000, int(d[2:4]), int(d[4:6]))
                print(x)
                two_day_buffer = 60*60*24*2

                # date is lookin good
                print("here")
                print(round(x.timestamp()))
                print(round(t.timestamp()))
                if abs(round(x.timestamp()) - round(t.timestamp())) < two_day_buffer:
                    # test base64 format of last two parts
                    print("base64")
                    try:
                        base64.b64decode(data[5])
                        base64.b64decode(data[6])
                        return "", True
                    except:
                        msg = "X-Hashcash nonce or counter not in proper base64 format"
                else:
                    msg = "X-Hashcash date is not within two days of current date"
            except:
                msg = "X-Hashcash date values not valid"
        else:
            msg = "X-Hashcash date length is off"
    else:
        msg = "X-Hashcash header incorrect. Version number should be 1, leading zero" + \
              "bit length should be 20, and there should be 6 parts to the header"
        
    return msg, False

def check_email(sent_data):
    names = ["birch", "gary", "cheshirecatalytic", "dewy", "artemisi19", "triakontakai", "matlac", "wittsend2", 
             "jsfleming", "mykale", "amanthanvi", "ptrip9199", "ishaan514", "shricubed", "mmohades", "angcheng27", 
             "suryaviyyapu", "nickfroehl", "yieb", "cybercyber2", "sm00thcriminal96", "ai-ya-ya"]
    email = str(sent_data).strip().split(':')[3]
    name = email.strip().split('@')[0]
    if name in names:
        return "", True
    else:
        return f"No one by the name of \"{name}\" in these parts", False


def check_proof(sent_data):
    # Hash the sent data and check if there are 4 leading zeros
    #      - This could be changed up or down depending on how long it takes for the user to do the proof! 
    #        We don't want it to be too long, but we also don't wnat it to take less than a second or two
    hashed = hashlib.sha1(sent_data.strip().encode()).hexdigest()
    if hashed[0:5] == '00000':
        return "", True
    
    return "proof not correct", False
    

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 50001        # Port to listen on (non-privileged ports are > 1023)
FLAG = "Nice. You did the work. Good soup. \n\nHere is your flag: UMDCTF{H@sh_c4sH_1s_th3_F@th3r_0f_pr00f_0f_w0rk}\n"

initial = """
Welcome to Gary's email service. Gary has setup Hashcash because we've been getting a lot 
of emails lately. He said something about bitcoin and blockchain, but all that mumbo jumbo 
doesn't make sense to me. He said you should get a confirmation message after passing the 
Hashcash mechanism. 

ver = 1  
leading zero bits = 20
date format = YYMMDD

Here is a list of the emails on our network:
- gary@hashcash.com           - cheshirecatalytic@hashcash.com
- birch@hashcash.com          - dewy@hashcash.com
- shricubed@hashcash.com      - triakontakai@hashcash.com
- wittsend2@hashcash.com      - artemis19@hashcash.com
- jsfleming@hashcash.com      - mykale@hashcash.com
- amanthanvi@hashcash.com     - ptrip9199@hashcash.com
- ishaan514@hashcash.com      - mmohades@hashcash.com
- angcheng27@hashcash.com     - suryaviyyapu@hashcash.com
- nickfroehl@hashcash.com     - yieb@hashcash.com
- cybercyber2@hashcash.com    - sm00thcriminal96@hashcash.com
- ai-ya-ya@hashcash.com 

Would you like to send an email (y/n)? 
"""

next_msg = "Looks like the message didn't go through :(\nSend another (y/n)? "

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("\n")
        start_new_thread(threading, (conn, ))
    s.close()


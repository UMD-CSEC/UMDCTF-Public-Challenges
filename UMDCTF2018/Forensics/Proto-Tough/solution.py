#!/usr/bin/env python

import sys
import argparse
import socket
import time
import select
import random

import challenge_pb2


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('129.2.229.60', 12344))

request = challenge_pb2.get_flag()

socket.send("UMDCSEC" + request.SerializeToString())

# You can do this, the flag is sent in plaintext, but within another Protobuf message.
# As long as the user sends a valid get_flag protobuf message, they get the flag.
#print socket.recv(1024) 

#The preferred method:

data = socket.recv(1024)

flag = challenge_pb2.send_flag()
flag.ParseFromString(data)

print flag.flag

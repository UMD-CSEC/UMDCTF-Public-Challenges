#!/usr/bin/env python

import sys
import argparse
import socket
import challenge_pb2
from thread import start_new_thread
import time

#server runs on port 12344 and all interfaces
PORT = 12344
HOST = ''

def client_handler(connection):

	connection.settimeout(10)
	connection.setblocking(1)

	try:
		data = connection.recv(1024)
	except:
		connection.close()

	if not data:
		connection.close()

	try:
		if data[0] != "U":
				time.sleep(.1)
				if data[1] != "M":
					time.sleep(.1)
					if data[2] != "D":
						time.sleep(.1)
						if data[3] != "C":
							time.sleep(.1)
							if data[4] != "S":
								time.sleep(.1)
								if data[5] != "E":
									time.sleep(.1)
									if data[6] != "C":
										time.sleep(.1)
	except:
		connection.send("Invalid magic bytes! Try again!\n")

	try:
		get = challenge_pb2.get_flag()
		get.ParseFromString(data[7:])
		response = challenge_pb2.send_flag()
		response.flag = "UMDCSEC-{n0W_y0Ur_tH1nKInG_W1th_pR0toBufs!}\n"
		tosend = response.SerializeToString()
		connection.send(tosend)
	except:
		connection.send("That's not a valid Protobuf message! Try again!\n")
	if "hint" in data.lower():
		connection.send("HINT: Check out Google Protobufs: https://github.com/google/protobuf/\nUse the challenge.proto file we gave you!\n")
	else:
		connection.send("Welcome to the UMDCSEC Google Protobuf server!\nTo get your flag, send a valid get_flag Protobuf message!\n")

	connection.close()

def main():

	try:
	    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
	    print("Could not create socket.")
	    sys.exit(1)

	try:
	    sock.bind((HOST, PORT))
	    print("[-] Socket Bound to port " + str(PORT))
	except socket.error:
	    print("Bind Failed.")
	    sys.exit(2)

	sock.listen(64)

	while True:
		conn, addr = sock.accept()
		print "Connected to %s:%s" % (str(addr[0]), str(addr[1]))

		start_new_thread(client_handler, (conn,))


	sock.close()	


if __name__ == '__main__':
	main()
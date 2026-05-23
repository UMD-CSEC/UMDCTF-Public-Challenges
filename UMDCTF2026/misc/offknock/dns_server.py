#!/usr/local/bin/python -u

import sys, socket
from dnslib.server import DNSServer, DNSLogger, BaseResolver
from dnslib import RR, TXT, QTYPE, RCODE
from flag import flag

class Resolver(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()

        question = request.get_q()

        if question.qtype != QTYPE.TXT:
            reply.header.rcode = RCODE.reverse['NXDOMAIN']
            return reply

        if '\x04flag\x06market\x03polȳ'.encode('utf8') in handler.request[0][12:30]:
            reply.add_answer(RR("flag.market.polȳ", QTYPE.TXT, rdata=TXT(flag)))
        else:
            reply.header.rcode = RCODE.reverse['NXDOMAIN']

        return reply

server = DNSServer(Resolver(),
                   port=1337,
                   logger=DNSLogger(logf=DNSLogger.log_pass))
server.start_thread()

s = sys.stdin.buffer.read(2)
s = int.from_bytes(s)
q = sys.stdin.buffer.read(s)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.sendto(q, ("127.0.0.1", 1337))
    a = sock.recv(2**16)
    a = len(a).to_bytes(2) + a
    sys.stdout.buffer.write(a)

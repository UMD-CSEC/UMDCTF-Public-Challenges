#!/usr/local/bin/python -u

import time, sys, socket, random, string
from dnslib.server import DNSServer, DNSLogger, BaseResolver
from dnslib import RR, TXT, QTYPE, RCODE
from flag import flag

k = 819
secret = random.choices(string.ascii_letters, k=k)
subdomain = '.'.join([''.join(secret[i:i+63]) for i in range(0, k - 63 + 1, 63)])

class Resolver(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()

        for question in request.questions:
            qname = question.qname
            if question.qtype != QTYPE.TXT:
                reply.header.rcode = RCODE.reverse['NXDOMAIN']
                continue

            if qname == subdomain + ".inside.info":
                reply.questions = []
                reply.add_answer(RR("flag.inside.info", QTYPE.TXT, rdata=TXT(flag)))
            elif qname.matchWildcard("*.inside.info"):
                try:
                    index = int(qname.label[0])
                    reply.add_answer(RR(qname, QTYPE.TXT, rdata=TXT(secret[index])))
                except ValueError, IndexError:
                    reply.header.rcode = RCODE.reverse['NXDOMAIN']
                    reply.questions = []
            else:
                reply.header.rcode = RCODE.reverse['NXDOMAIN']

        return reply

server = DNSServer(Resolver(),
                   port=1337,
                   logger=DNSLogger(logf=DNSLogger.log_pass))
server.start_thread()

for _ in range(2):
    s = sys.stdin.buffer.read(2)
    s = int.from_bytes(s)
    q = sys.stdin.buffer.read(s)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(q, ("127.0.0.1", 1337))
        a = sock.recv(2**16)
        a = len(a).to_bytes(2) + a
        sys.stdout.buffer.write(a)

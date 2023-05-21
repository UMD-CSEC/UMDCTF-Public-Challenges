"""
A Seq solver

Spins up Geneva to handle the packet modifications and requests the file.

Usage: python3 solveit.py http://172.17.0.3
"""
import hashlib
import os
import sys

import requests

BASEPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASEPATH, "geneva/"))
# To do traffic modification, leverage geneva
import geneva.engine

if len(sys.argv) != 2:
    print("Usage: python3 %s <server>" % __file__)
    exit()

port = 80

adj = "[TCP:flags:*]-switch{}-| "\
      "\/"\
      "[TCP:flags:*]-switch{}-| " 

server = sys.argv[1]

with geneva.engine.Engine(port, adj, log_level="info", save_seen_packets=False) as eng:
    req1server = server + ":%d/gimmedafile.txt" % (port)
    print("requesting file from %s" % req1server)
    response = requests.get(req1server)
    print(response.text[-50:])

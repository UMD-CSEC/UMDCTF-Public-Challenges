#!/usr/local/bin/python -u

import subprocess
import sys
import socket

from flag import flag

dns_ip_addr = "127.0.0.1"
dns_port = 25565

subprocess.run(
        ['/app/dnsmasq',
         '-x', 'dnsmasq.pid',
         '-p', f'{dns_port}',
         '--txt-record', f'tiktok.com,{flag}'])

size = sys.stdin.buffer.read(4)
size = int.from_bytes(size)

req = sys.stdin.buffer.read(size)

if b'tiktok\x03com' in req:
    print("Sorry, TikTok isn't available right now. A law banning TikTok has been enacted in the U.S. Unfortunately, that means you can't use TikTok for now. We are fortunate that President Trump has indicated that he will work with us on a solution to reinstate TikTok once he takes office. Please stay tuned!")
else: 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(req, (dns_ip_addr, dns_port))
    resp = sock.recv(1024)
    print(resp)

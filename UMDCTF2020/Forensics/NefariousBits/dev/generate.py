from scapy.all import Ether, IP, TCP, sendp, FlagValue
import numpy
A = "41.137.13.37"
B = "128.8.0.0"
C = 6000
D = 5000
flag='UMDCTF-{3vil_b1ts_@r3_4lw4ys_3vi1}'

def send_evil_packet():
    evil_packet = Ether() / IP(src=A, dst=B, flags=4) / TCP(sport=C, dport=D, flags='S')
    sendp(evil_packet, iface='lo')

def send_good_packet():
    good_packet = Ether() / IP(src=A, dst=B) / TCP(sport=C, dport=D, flags='S')
    sendp(good_packet, iface='lo')

def to_bits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result

bits_array = to_bits(flag)
for bit in bits_array:
    if bit == 1:
        send_evil_packet()
    else:
        send_good_packet()
    C += 1

from scapy.all import rdpcap
import re
import requests

def from_bits(bits):
    chars = []
    for b in range(len(bits) // 8):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)

pcap = rdpcap("attack.pcap")
bits_array = []
for pkt in pcap:
    bits_array.append(1 if pkt.flags.evil else 0)
print(from_bits(bits_array))

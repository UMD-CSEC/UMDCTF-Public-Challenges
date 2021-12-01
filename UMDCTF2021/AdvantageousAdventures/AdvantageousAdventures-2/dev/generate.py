from scapy.all import Ether, IP, TCP, sendp, Raw, rdpcap
import time

packets = rdpcap('/root/test_data')

while True:
    for packet in packets:
        sendp(Ether() / packet, iface='wlo2')
    time.sleep(1)
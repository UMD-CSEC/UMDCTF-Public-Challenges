from scapy.all import rdpcap, RadioTap, wrpcap

# run this on the file you get during the second challenge
# you don't need to understand all of it

packets = rdpcap('in.pcap')
fixed_packets = []
for packet in packets:
    # I know eval is unsafe but stackoverflow is down when script was created
    packet_bytes = eval(str(packet))
    fixed_packet_bytes = packet_bytes[14:]
    fixed_packets.append(RadioTap(fixed_packet_bytes))
wrpcap("out.pcap", fixed_packets)

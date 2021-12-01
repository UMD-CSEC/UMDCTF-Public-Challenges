from scapy.all import *

for i in range(100):
    sendp(RadioTap(ChannelFrequency=2412) / Dot11(type=0, subtype=4,FCfield=0, addr1="ff:ff:ff:ff:ff:ff", addr2="7C:B2:7D:E1:44:CA") / Dot11ProbeReq() / Dot11Elt(ID='SSID', info='UMDCTF-{sp00ky_sh@rky}'), iface="wlx98ded0155fe3")
for i in range(100):
    send(Raw("UMDCTF-{wp@_!s_3z}"), iface='wlo1')
flag = "UMDCTF-{crypt0_1n_wp@?}"
for i, c in enumerate(flag):
    print(str(i) * ord(c))
    for _ in range(100):
        send(Raw(str(i) * ord(c)), iface='wlo1')
from scapy.all import rdpcap
import re
import requests

pcap = rdpcap("attack.pcap")

for pkt in pcap:
    if len(pkt) > 54:
        data = pkt.load[2:].decode('utf-16')
        r = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', data)
        ip = r.groups(1)[0]
        url = 'http://ipapi.co/' + ip + '/json'
        data = requests.get(url).json()
        print(data['country_name'])
        break

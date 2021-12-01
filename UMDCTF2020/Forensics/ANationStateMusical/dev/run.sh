sudo tcpdump -ni lo -s0 -v -c 5001 -nn -s0 -w attack.pcap tcp port 5000 &
sudo python3 generate.py

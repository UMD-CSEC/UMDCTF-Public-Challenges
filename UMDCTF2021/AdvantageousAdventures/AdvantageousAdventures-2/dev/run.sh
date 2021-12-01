ip link add wlo2 type dummy
ip link set wlo2 up
/usr/bin/python3 /root/generate.py &
/usr/sbin/sshd -D
FROM ubuntu:20.04
RUN echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections
RUN apt update && DEBIAN_FRONTEND="noninteractive" apt install -y openssh-server python3 python3-pip tshark iproute2 net-tools

#RUN apt update && DEBIAN_FRONTEND="noninteractive" apt install -y sudo

RUN pip3 install scapy

COPY generate.py /root
COPY test_data /root
COPY run.sh /root
RUN chmod +x /root/run.sh

RUN useradd -rm -d /home/ubuntu -s /bin/bash -u 1000 user

#RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 user || true

RUN echo 'user:w0w_th3s3_@dv3ntur3s_r3@lly_@r3_outr@g30u5' | chpasswd
RUN adduser user wireshark

#RUN adduser user sudo

RUN chmod +x /usr/bin/dumpcap
RUN service ssh start
EXPOSE 22
CMD /root/run.sh

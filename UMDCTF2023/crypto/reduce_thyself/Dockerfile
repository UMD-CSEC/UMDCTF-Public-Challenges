FROM ubuntu:20.04

RUN apt-get update && apt-get install python3 python3-pip -y
RUN pip3 install pycryptodome

RUN useradd -d /home/ctf -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY ./prod/* ./

EXPOSE 60003

CMD ["python3", "reduce_thyself.py"]

FROM ubuntu:18.04

RUN apt update && apt install -y gcc make cmake gdb vim

RUN apt install -y wget tmux

RUN apt install -y python3 python3-pip python3-venv

RUN python3 -m pip install keystone-engine unicorn capstone ropper

RUN python3 -m venv /venv --system-site-packages 

RUN /venv/bin/python -m pip install --upgrade pip

RUN /venv/bin/python -m pip install pwntools 

WORKDIR /root

RUN wget -O ~/.gdbinit-gef.py -q https://github.com/hugsy/gef/raw/master/gef.py 

RUN echo source ~/.gdbinit-gef.py >> ~/.gdbinit

COPY tcache2.c .

COPY tcache.py .

COPY .tmux.conf .

RUN echo "UMDCTF{TEST_FLAG}" > flag.txt

RUN gcc tcache2.c -o tcache2 -fno-pic -no-pie -lcrypt -static

RUN chmod +x tcache.py

ENV LC_CTYPE=C.UTF-8

CMD ["/bin/bash"]

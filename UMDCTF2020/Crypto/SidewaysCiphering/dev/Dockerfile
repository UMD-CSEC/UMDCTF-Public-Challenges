FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y dist-upgrade && \
    apt-get install -y python3 python3-pip

RUN pip3 install crypto

COPY ./oracle.py /run
COPY ./key /run
COPY ./ciphertext /ciphertext

WORKDIR /run

EXPOSE 1337

CMD ["python3", "oracle.py", "0.0.0.0", "1337", "key", "UMDCTF-{s1d3_ch@nn3l_0p3n}"]

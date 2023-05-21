FROM --platform=linux/amd64 amd64/ubuntu:22.04 AS builder
RUN apt update -y && apt install -y build-essential
WORKDIR /temp
COPY splash.c splash.c
RUN gcc splash.c



FROM --platform=linux/amd64 amd64/ubuntu:22.04

RUN apt update -y && apt install -y xinetd

RUN echo "You have been blocked by xinetd. Report this to the organizers if this persists." > /etc/banner_fail

WORKDIR /ctf
RUN useradd -d /ctf -m ctf
COPY --from=builder /temp/a.out a.out
COPY flag.txt ./flag.txt
COPY ctf.xinetd /etc/xinetd.d/ctf
COPY scripts/init.sh /init.sh
COPY scripts/run.sh /ctf/run.sh

RUN chmod +x /ctf/a.out /init.sh /ctf/run.sh

ENTRYPOINT ["/init.sh"]

EXPOSE 1449
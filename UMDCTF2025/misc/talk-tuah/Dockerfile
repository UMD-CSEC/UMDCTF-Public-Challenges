FROM ubuntu@sha256:f8b860e4f9036f2694571770da292642eebcc4c2ea0c70a1a9244c2a1d436cd9

RUN apt-get update && apt-get install -y socat sudo cgroup-tools daemontools hashcash

COPY talk-tuah /app/talk-tuah
COPY flag.txt /app/flag.txt
COPY entrypoint.sh /entrypoint.sh
COPY interactive-shell.sh /interactive-shell.sh

RUN useradd -M user && useradd -M flag

RUN chown flag:flag /app/flag.txt && chmod 400 /app/flag.txt
RUN chown flag:flag /app/talk-tuah && chmod u+s /app/talk-tuah
RUN chmod 550 /interactive-shell.sh

ENTRYPOINT /entrypoint.sh

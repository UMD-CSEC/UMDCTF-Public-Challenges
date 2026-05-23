FROM debian:bookworm-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc make libc6-dev binutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY artifact.c Makefile ./
RUN make

FROM python:3.12-slim AS app

FROM pwn.red/jail

COPY --from=app / /srv
COPY service.py /srv/app/run
COPY --from=builder /build/dist/closing-bell-template.bin /srv/app/closing-bell-template.bin
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1455 JAIL_MEM=64M JAIL_ENV_NUM=5 JAIL_PIDS=30 JAIL_TIME=3700

FROM ubuntu:21.10 AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY ./flag.txt /srv/app/flag.txt
COPY ./libc.so.6 /srv/app/
COPY ./ld-linux-x86-64.so.2 /srv/app/
COPY ./chisel /srv/app/run

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20

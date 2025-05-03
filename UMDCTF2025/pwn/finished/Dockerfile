FROM ubuntu:24.04 AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY ./finished /srv/app/run
COPY ./flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447 JAIL_MEM=128M JAIL_ENV_NUM=5 JAIL_PID=20 JAIL_TIME=1200

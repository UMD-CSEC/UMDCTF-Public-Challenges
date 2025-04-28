FROM ubuntu:23.10 AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY the_voice /srv/app/run
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20

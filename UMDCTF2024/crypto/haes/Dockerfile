FROM python:slim AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY haes.py /srv/app/run
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20

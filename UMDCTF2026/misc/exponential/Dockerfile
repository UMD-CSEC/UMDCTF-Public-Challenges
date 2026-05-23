FROM python:3.13-slim AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY chal.py /srv/app/run
COPY flag.txt /tmp/flag.txt

RUN mv /tmp/flag.txt /srv/app/flag_$(openssl rand -hex 8).txt
RUN chmod +x /srv/app/run

ENV JAIL_PORT=1449 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20

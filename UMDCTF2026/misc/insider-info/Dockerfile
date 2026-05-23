FROM python:slim AS app

RUN pip install --no-cache-dir dnslib

FROM pwn.red/jail

COPY --from=app / /srv
COPY dns_server.py /srv/app/run
COPY flag.py /srv/app/flag.py

RUN chmod +x /srv/app/run

ENV JAIL_PORT=32323 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20 JAIL_CONNS_PER_IP=5

FROM python:slim AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY filter.py /srv/app/run
COPY flag.py /srv/app/flag.py
COPY dnsmasq /srv/app/dnsmasq

RUN chmod +x /srv/app/run

ENV JAIL_PORT=32300 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20

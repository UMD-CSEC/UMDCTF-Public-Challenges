FROM python:3.11.1-slim-bullseye AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY server.py /srv/app/run
COPY public_key.py /srv/app/public_key.py
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

# yes 300M is necessary so there's a POW to compensate
ENV JAIL_PORT=1447 JAIL_MEM=300M JAIL_ENV_NUM=20 JAIL_TIME=60 JAIL_PIDS=10 JAIL_POW=15000

FROM python:3.12-slim AS app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM pwn.red/jail

COPY --from=app / /srv
COPY challenge.py /srv/app/run
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1458 JAIL_MEM=128M JAIL_ENV_NUM=5 JAIL_PIDS=30 JAIL_POW=7500

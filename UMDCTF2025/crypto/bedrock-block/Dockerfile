FROM python:3.11.1-slim-bullseye AS app
RUN pip install --no-cache pycryptodome

FROM pwn.red/jail

COPY --from=app / /srv
COPY bedrock.py /srv/app/run
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20 JAIL_TIME=1500


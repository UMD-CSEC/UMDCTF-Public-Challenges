FROM python:3.11.1-slim-bullseye AS app
RUN pip install --no-cache pycryptodome

FROM pwn.red/jail
COPY --from=app / /srv
COPY tripledes.py /srv/app/run
COPY key.txt /srv/app
COPY flag.txt /srv/app

RUN chmod +x /srv/app/run

ENV JAIL_MEM=20M JAIL_CPU=500 JAIL_TIME=300

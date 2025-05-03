FROM ubuntu:24.04 AS app

FROM pwn.red/jail

COPY --from=app / /srv
COPY ./flag.txt /srv/app/flag.txt
COPY ./aura /srv/app/run

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447

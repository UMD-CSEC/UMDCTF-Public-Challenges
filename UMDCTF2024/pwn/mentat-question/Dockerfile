FROM ubuntu@sha256:cb2af41f42b9c9bc9bcdc7cf1735e3c4b3d95b2137be86fd940373471a34c8b0 AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY mentat-question /srv/app/run
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run

ENV JAIL_PORT=32300 JAIL_MEM=20M JAIL_ENV_NUM=5 JAIL_PID=20

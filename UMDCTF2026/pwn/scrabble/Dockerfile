FROM ubuntu@sha256:cb2af41f42b9c9bc9bcdc7cf1735e3c4b3d95b2137be86fd940373471a34c8b0 AS app
FROM pwn.red/jail

COPY --from=app / /srv
COPY libc.so.6 /srv/app/libc.so.6
COPY ld-linux-x86-64.so.2 /srv/app/ld-linux-x86-64.so.2
COPY main /srv/app/run
COPY flag.txt /srv/app/flag.txt

RUN chmod +x /srv/app/run
RUN chmod +x /srv/app/libc.so.6
RUN chmod +x /srv/app/ld-linux-x86-64.so.2

ENV JAIL_PORT=1452 JAIL_MEM=64M JAIL_ENV_NUM=5 JAIL_PID=20

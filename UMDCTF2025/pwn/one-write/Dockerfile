FROM ubuntu:24.04@sha256:1e622c5f073b4f6bfad6632f2616c7f59ef256e96fe78bf6a595d1dc4376ac02 AS app

FROM pwn.red/jail

COPY --from=app / /srv
COPY ./flag.txt /srv/app/flag.txt
COPY ./one_write /srv/app/run

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447

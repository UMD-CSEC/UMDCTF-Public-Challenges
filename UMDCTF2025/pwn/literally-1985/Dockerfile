FROM ubuntu:24.04 AS app
RUN apt update && apt install -y bash tar adduser
FROM pwn.red/jail

COPY --from=app / /srv
COPY ./dist.tar.gz /srv/app/dist.tar.gz
RUN tar -xf /srv/app/dist.tar.gz -C /srv/app
COPY d8 /srv/app/d8
RUN cp /srv/app/wrapper.sh /srv/app/run
COPY ./flag.txt /srv/app/flag.txt
RUN mv /srv/app/flag.txt /srv/app/flag_$(tr -dc A-Za-z0-9 </dev/urandom | head -c 15).txt

RUN chmod +x /srv/app/run
RUN chmod +x /srv/app/d8

ENV JAIL_PORT=1447 JAIL_MEM=512M JAIL_ENV_NUM=5 JAIL_PIDS=50 JAIL_TIME=600 JAIL_TMP_SIZE=20000

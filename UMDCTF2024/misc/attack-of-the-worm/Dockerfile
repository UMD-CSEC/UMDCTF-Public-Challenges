FROM python:3.11.8-slim-bookworm as app
RUN pip install torch torchvision --no-cache --index-url https://download.pytorch.org/whl/cpu

FROM pwn.red/jail
COPY --from=app / /srv

COPY server.py /srv/app/run
COPY flag.txt /srv/app/flag.txt
COPY model.pt /srv/app/model.pt
COPY worm.png /srv/app/worm.png
RUN chmod 755 /srv/app/run

ENV JAIL_PORT=7274 JAIL_PIDS=20 JAIL_TIME=45 JAIL_MEM=1200M JAIL_POW=7500 JAIL_CPU=750
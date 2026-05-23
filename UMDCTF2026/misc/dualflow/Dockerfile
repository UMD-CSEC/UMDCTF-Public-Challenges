FROM python:3.14.4-slim-bookworm AS app
RUN pip install torch==2.11.0 --no-cache --index-url https://download.pytorch.org/whl/cpu
RUN pip install numpy==2.4.4 --no-cache

FROM pwn.red/jail
COPY --from=app / /srv

COPY challenge.py /srv/app/run
COPY flag.txt /srv/app/flag.txt
COPY flow.py /srv/app/flow.py
COPY dist /srv/app/dist

RUN chmod +x /srv/app/run

ENV JAIL_PORT=7276 JAIL_PIDS=48 JAIL_TIME=45 JAIL_MEM=1200M JAIL_CPU=750 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

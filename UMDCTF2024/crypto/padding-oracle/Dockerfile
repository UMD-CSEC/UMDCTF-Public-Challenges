# set base image (host OS)
FROM python:3.8-alpine as app
# install dependencies

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY padding_oracle.py run

FROM pwn.red/jail

# set the working directory in the container
COPY --from=app / /srv

RUN chmod +x /srv/app/run

ENV JAIL_PORT=1447 JAIL_MEM=20M JAIL_PID=20 JAIL_TIME=300

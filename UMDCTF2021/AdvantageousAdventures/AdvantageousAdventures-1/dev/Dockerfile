FROM ubuntu:20.04
COPY . /app
RUN apt update && apt -y install python3 python3-flask
CMD cd /app && flask run --host="0.0.0.0"

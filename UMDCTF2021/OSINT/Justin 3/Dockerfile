FROM ubuntu:20.04
COPY . /app
RUN apt update && apt -y install python3 python3-flask python3-pip
RUN pip3 install requests
CMD cd /app/dev && flask run --host="0.0.0.0"

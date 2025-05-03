FROM python:3.12
RUN apt update && apt install -y sudo

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get -y install cron

COPY main.py .
COPY static ./static
COPY templates ./templates
COPY flag.txt .
COPY basedict.brainrot .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN mkdir uploads
RUN useradd -u 1000 web
RUN chown 1000:1000 uploads
RUN chmod =r flag.txt
RUN chmod =r basedict.brainrot
COPY cron_clean /etc/cron.d/cron_clean
RUN crontab /etc/cron.d/cron_clean

EXPOSE 5000

CMD ./entrypoint.sh

FROM alpine
MAINTAINER Christian Gatzlaff <cgatzlaff@gmail.com>

# basic flask environment
RUN apk add --no-cache bash git nginx uwsgi uwsgi-python py2-pip \
    && pip2 install --upgrade pip \
    && pip2 install flask

RUN "mkdir /opt/app/"
COPY ./ /opt/app
RUN 'python /opt/app/hangman.py'
EXPOSE 80
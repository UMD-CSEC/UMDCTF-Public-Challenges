FROM alpine
MAINTAINER Christian Gatzlaff <cgatzlaff@gmail.com>

# basic flask environment
RUN apk add --no-cache bash git nginx uwsgi uwsgi-python py2-pip \
    && pip2 install --upgrade pip \
    && pip2 install flask

RUN "mkdir /opt/app/"
COPY ./app /opt/app
WORKDIR "/opt/app"
RUN "python -c 'from hangman import db; db.create_all()'"
RUN 'python /opt/app/app.py'
EXPOSE 80
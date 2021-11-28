FROM php:7.0-apache
RUN apt-get update
MAINTAINER michael@csec.umiacs.umd.edu

RUN echo "UMDCTF-{wh00ps_you_hacked_my_IOT}" >> /etc/passwd
EXPOSE 80 
COPY ./src /var/www/html

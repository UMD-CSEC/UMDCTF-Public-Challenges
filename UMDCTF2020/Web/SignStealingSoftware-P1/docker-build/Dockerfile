FROM php:7.4-apache
RUN apt update -y
RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli
COPY ./code /var/www/html

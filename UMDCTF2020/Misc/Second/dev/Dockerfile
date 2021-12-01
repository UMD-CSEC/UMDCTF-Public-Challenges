FROM ubuntu:latest

COPY ./second /run

WORKDIR /run

RUN chmod +x /run/second

EXPOSE 7799

CMD ["/run/second"]

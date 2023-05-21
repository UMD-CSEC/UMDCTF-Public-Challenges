FROM ubuntu:20.04

COPY youwantmetorunwhat /
COPY flag.txt /
WORKDIR /

EXPOSE 8080

RUN chmod +x /youwantmetorunwhat

CMD ["/youwantmetorunwhat"]

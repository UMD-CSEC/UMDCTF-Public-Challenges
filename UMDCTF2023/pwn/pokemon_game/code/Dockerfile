FROM --platform=linux/amd64 amd64/ubuntu:20.04 as build-env

MAINTAINER bfu "bella@localhost22.com"

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /pokemon_game_build
COPY *.c ./
COPY include ./include
COPY build ./build
COPY templates ./templates
COPY Makefile .
COPY build.sh .

RUN apt update
RUN apt install --yes automake gcc gcc-multilib python3-dev python3-pip
RUN ./build.sh

# https://github.com/SniperOJ/Jeopardy-Dockerfiles/blob/master/pwn/bof-x86-64/Dockerfile
FROM --platform=linux/amd64 amd64/ubuntu:20.04

RUN dpkg --add-architecture i386

RUN apt update --yes
RUN apt install --yes socat libc6:i386 libncurses5:i386 libstdc++6:i386

WORKDIR /ctf
RUN useradd -d /ctf -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd
COPY --from=build-env /pokemon_game_build/out/catch_them_all ./catch_them_all
COPY flag.txt ./flag.txt
RUN chmod 755 ./catch_them_all
RUN chown ctf:ctf ./catch_them_all
RUN chown ctf:ctf /ctf/flag.txt

USER ctf

ENTRYPOINT socat -d TCP-LISTEN:8080,reuseaddr,fork exec:"./catch_them_all",stderr,pty,echo=0

EXPOSE 8080

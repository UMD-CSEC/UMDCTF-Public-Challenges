FROM ubuntu:20.04

RUN apt update && apt install -y curl openssh-server bash

RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

RUN useradd -m user

COPY image /usr/lib/current_image

RUN echo 'user:umdctf' | chpasswd

RUN usermod -aG docker user

RUN echo "Please note, the container has not finished it's creation until further noted in this README (it will be automatically updated in less than a minute)." > /home/user/README.md

RUN service ssh start

CMD /usr/sbin/sshd -D & \
    service docker start && \
    sleep 1 && \
    docker build -t ubuntu:16.04 /usr/lib/current_image && \
    rm -rf /usr/lib/current_image && \
    docker run -d --name secret_image ubuntu:16.04 && \
    docker stop secret_image && \
    echo "\nCreation Finished!" >> /home/user/README.md && \
    sleep infinity
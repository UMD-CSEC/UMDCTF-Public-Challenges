FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y python3 python3-pip texlive-latex-base texlive-latex-extra

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 4433

RUN chmod +rwx ./startup.sh

CMD ["./startup.sh"]

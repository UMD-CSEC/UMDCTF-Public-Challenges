FROM php:7.4-apache
RUN apt update -y
RUN apt install git -y
COPY . /var/www/html
RUN useradd gitserver
RUN mkdir /home/gitserver
WORKDIR /home/gitserver
RUN git clone "https://github.com/drkmrin78/PiPlay"
WORKDIR /home/gitserver/PiPlay
RUN git config --global user.email "wittsend2@gmail.com"
RUN git config --global user.anme "WittsEnd2"
RUN git commit --amend -m "VU1EQ1RGLXtZbzBfS04wd19UaDNfTjNYdF9wMXRDSH0="
RUN rm /home/gitserver/PiPlay/.git/COMMIT_EDITMSG
RUN cp -r /home/gitserver/PiPlay/.git /home/gitserver
RUN rm -rf /home/gitserver/PiPlay
# RUN touch /home/gitserver/data.txt
# RUN echo "VU1EQ1RGLXtZbzBfS04wd19UaDNfTjNYdF9wMXRDSH0=" >> /home/gitserver/data.txt

EXPOSE 8080

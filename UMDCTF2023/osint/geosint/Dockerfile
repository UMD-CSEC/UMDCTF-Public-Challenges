FROM node:16

WORKDIR /usr/src/app

# Install app dependencies
# COPY package*.json ./
RUN npm install body-parser cookie-parser express jsdom node-fetch@2

COPY . .

RUN mkdir -p ./public/img/chall1 ./public/img/chall2 ./public/img/chall3 

RUN rm -f ./public/img/chall*/*

RUN node pull_challs_fast.js

EXPOSE 6958

CMD [ "node", "server.js" ]


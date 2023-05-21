FROM node:16

WORKDIR /usr/src/app

RUN npm install express

COPY . .

EXPOSE 6958

CMD [ "node", "server.js" ]
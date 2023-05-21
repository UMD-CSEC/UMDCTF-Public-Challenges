FROM node:16

WORKDIR /usr/src/app

# Install app dependencies
# COPY package*.json ./
RUN npm install express

COPY . .

EXPOSE 7000

CMD [ "node", "server.js" ]


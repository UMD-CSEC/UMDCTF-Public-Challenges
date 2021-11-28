FROM node:carbon
WORKDIR /src
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3200
CMD ["npm", "start"]

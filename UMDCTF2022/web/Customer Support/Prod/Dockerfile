# Dockerfile

# base image
FROM node:alpine

# create & set working directory
RUN mkdir -p /usr/src
WORKDIR /usr/src

# copy source files
COPY . /usr/src

# install dependencies
RUN npm i
RUN cd microservice && npm i && cd ..
RUN npm install -g concurrently

# start app
RUN npm run build
EXPOSE 3000
CMD npm run startall

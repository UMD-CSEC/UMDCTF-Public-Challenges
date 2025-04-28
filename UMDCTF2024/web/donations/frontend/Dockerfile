FROM node:lts as build

WORKDIR /usr/app

COPY . .

RUN npm install
RUN npm run build

FROM ubuntu

RUN apt-get update
RUN apt-get install nginx -y

COPY --from=build /usr/app/dist /var/www/html/

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
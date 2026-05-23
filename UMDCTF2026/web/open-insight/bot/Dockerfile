FROM node:22-alpine

RUN apk update && apk upgrade
RUN apk add chromium

WORKDIR /app

COPY package.json ./
RUN PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true npm install --omit=dev --no-package-lock

RUN adduser -D -u 1001 bot && \
    mkdir -p /home/bot && \
    chown -R bot:bot /home/bot

COPY index.js ./
COPY public ./public
USER bot

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

EXPOSE 3001

CMD ["node", "index.js"]

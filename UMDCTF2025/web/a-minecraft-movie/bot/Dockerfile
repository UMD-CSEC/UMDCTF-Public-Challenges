FROM node:22-alpine

RUN apk update && apk upgrade
RUN apk add chromium

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./
RUN PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true pnpm install

RUN adduser -D -u 1001 bot && \
    mkdir -p /home/bot && \
    chown -R bot:bot /home/bot

COPY . .
USER bot

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

EXPOSE 4000

CMD ["pnpm", "start"]

FROM node:22-slim

RUN apt-get update && apt-get install -y \
  python3 \
  python3-distutils \
  make \
  g++ \
  sqlite3 \
  libsqlite3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml database.db ./

ENV npm_config_build_from_source=true
RUN pnpm install

COPY . .

EXPOSE 3000

CMD ["pnpm", "start"]
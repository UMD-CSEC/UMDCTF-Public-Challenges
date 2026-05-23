#!/bin/sh
set -e

mkdir -p /app/data

echo "[entrypoint] syncing schema..."
node ./node_modules/prisma/build/index.js db push --accept-data-loss

echo "[entrypoint] seeding..."
node ./node_modules/tsx/dist/cli.mjs prisma/seed.ts

echo "[entrypoint] starting next..."
exec node server.js

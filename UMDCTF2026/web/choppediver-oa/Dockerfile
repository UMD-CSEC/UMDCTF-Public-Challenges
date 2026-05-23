# syntax=docker/dockerfile:1.7
# ---------------------------------------------------------------------------
# server — python WSS app
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS server
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 libpng16-16 \
 && rm -rf /var/lib/apt/lists/*
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ ./
COPY certs/cert.pem /app/cert.pem
COPY certs/key.pem /app/key.pem
EXPOSE 4443
CMD ["python3", "entrypoint.py"]

# ---------------------------------------------------------------------------
# frontend-build — Vite bundle
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend-build
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install
COPY frontend/ ./
ARG VITE_WS_URL=wss://localhost:4443/
ENV VITE_WS_URL=$VITE_WS_URL
RUN pnpm build

# ---------------------------------------------------------------------------
# frontend — nginx
# ---------------------------------------------------------------------------
FROM nginx:alpine AS frontend
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY certs/cert.pem /etc/nginx/certs/cert.pem
COPY certs/key.pem /etc/nginx/certs/key.pem
EXPOSE 80 443

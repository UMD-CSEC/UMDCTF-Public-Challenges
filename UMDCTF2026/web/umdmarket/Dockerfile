# syntax=docker/dockerfile:1.7
#
# Multi-stage build shared by the server and frontend images. Both images
# descend through the `certgen` stage, so the cert baked into the server and
# the hash baked into the frontend bundle are guaranteed to come from the
# same generation run.
#
# Build the server: `docker build --target server -t predictctf-server .`
# Build the frontend: `docker build --target frontend -t predictctf-frontend .`
# Or via compose: `docker compose build`

# ---------------------------------------------------------------------------
# Stage: certgen — run the Go cert generator once per build, emit /certs/*
# ---------------------------------------------------------------------------
FROM golang:1.25-alpine AS certgen
WORKDIR /src
COPY server/go.mod server/go.sum ./
RUN go mod download
COPY server/ ./
RUN CGO_ENABLED=0 go build -o /bin/certgen ./cmd/certgen
RUN mkdir -p /certs && /bin/certgen -out /certs


# ---------------------------------------------------------------------------
# Stage: server-build — compile the WebTransport server binary
# ---------------------------------------------------------------------------
FROM golang:1.25-alpine AS server-build
WORKDIR /src
COPY server/go.mod server/go.sum ./
RUN go mod download
COPY server/ ./
RUN CGO_ENABLED=0 go build -o /server ./cmd/server


# ---------------------------------------------------------------------------
# Stage: frontend-build — Vite build with the baked cert hash
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend-build
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
# Read the hash produced by the certgen stage and expose it to Vite.
COPY --from=certgen /certs/backend-cert.hash /tmp/backend-cert.hash
ARG VITE_SERVER_URL=https://localhost:4443/wt
ENV VITE_SERVER_URL=$VITE_SERVER_URL
RUN VITE_CERT_HASH="$(cat /tmp/backend-cert.hash)" pnpm build


# ---------------------------------------------------------------------------
# Stage: server — final runtime image for the WebTransport server
# ---------------------------------------------------------------------------
FROM alpine:3.21 AS server
WORKDIR /app
COPY --from=server-build /server /app/server
COPY --from=certgen /certs/backend-cert.pem /app/cert.pem
COPY --from=certgen /certs/backend-key.pem /app/key.pem
EXPOSE 4443/udp
ENTRYPOINT ["/app/server"]
CMD ["-addr", ":4443", "-cert", "/app/cert.pem", "-key", "/app/key.pem"]


# ---------------------------------------------------------------------------
# Stage: frontend — final runtime image serving the built SPA via nginx
# ---------------------------------------------------------------------------
FROM nginx:alpine AS frontend
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY certs/frontend-cert.pem /etc/nginx/certs/cert.pem
COPY certs/frontend-key.pem /etc/nginx/certs/key.pem
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]

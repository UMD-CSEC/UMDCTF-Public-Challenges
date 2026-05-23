FROM rust:1.83-slim AS wasm-builder

RUN rustup target add wasm32-unknown-unknown

WORKDIR /build
COPY rust-gen/Cargo.toml rust-gen/Cargo.lock* ./
COPY rust-gen/src ./src
RUN cargo build --target wasm32-unknown-unknown --release

FROM python:3.12-slim

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./
COPY --from=wasm-builder \
    /build/target/wasm32-unknown-unknown/release/rainbet_gen.wasm \
    ./rainbet_gen.wasm

ENV PORT=8000
EXPOSE 8000

CMD ["gunicorn", "-w", "1", "--worker-class", "gevent", "--worker-connections", "256", "-b", "0.0.0.0:8000", "app:app"]

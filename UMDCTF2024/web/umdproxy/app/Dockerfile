FROM rust:1.77.2

WORKDIR /usr/app

COPY . .

RUN cargo install --path .

CMD ["umdproxy"]

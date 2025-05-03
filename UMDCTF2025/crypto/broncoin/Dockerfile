FROM rust:1.86.0

WORKDIR /usr/app

COPY . .

RUN cargo build --release

EXPOSE 3000

CMD ["./target/release/bron-server"]

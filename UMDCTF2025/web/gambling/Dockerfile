FROM rust:1.86.0

WORKDIR /usr/app

COPY . .

RUN cargo install --path .

ENV FLAG=UMDCTF{d_D_d_dehH_@W_dANG_!7} HTTP_PORT=80 HTTPS_PORT=443

CMD ["umdctf-umd-gambling"]
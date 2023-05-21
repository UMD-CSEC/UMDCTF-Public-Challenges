#!/bin/sh

cargo build --release

rm -rf dist/
mkdir dist/

cp -r Dockerfile Cargo.lock Cargo.toml src/ scripts/ dist/
cp target/release/bbfmspmss dist/
cp target/release/bbfmspmss .
cp ctf.xinetd dist/

echo "UMDCTF{test_flag_dont_submit_bozo}" > dist/flag.txt

zip -FSr dist.zip dist/

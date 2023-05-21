#!/bin/bash

PORT="6969"

docker run --name pokemon-game -it --rm -p"${PORT}:8080" pwn-pokemon-game

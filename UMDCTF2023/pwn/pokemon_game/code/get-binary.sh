#!/bin/bash

CONTAINER="pokemon-game"

# Extract binary
docker cp "${CONTAINER}:/ctf/catch_them_all" ./catch_them_all

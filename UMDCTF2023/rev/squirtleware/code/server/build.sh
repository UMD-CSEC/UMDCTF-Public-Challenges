#!/bin/bash

# Location of the maven wrapper.
MVNW="./mvnw"

# Function to run commands through the maven wrapper.
function run_maven() {
    "${MVNW}" "$@"
}

# Run checkstyle! :).. Time crunch! Sorry
# run_maven "checkstyle:check"
# Build native
run_maven -Dcheckstyle.skip compile 
run_maven -Dcheckstyle.skip package 
docker build -f src/main/docker/Dockerfile.jvm -t quarkus/server-jvm .

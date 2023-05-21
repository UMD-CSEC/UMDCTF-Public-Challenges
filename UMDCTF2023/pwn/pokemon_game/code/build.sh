#!/bin/bash

# Clean generated files.
make clean

# Seriously, you need to make dependencies first.
make deps&& make target

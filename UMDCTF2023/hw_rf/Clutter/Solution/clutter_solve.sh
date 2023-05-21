#!/bin/bash

# Run with long trace and save to file
./gen_clutter.py > clutter.vspa; ./VESPa/VESP_1.0/VESPa.py -p clutter.vspa > clutter.vsp

# Run clutter.vsp with long trace and save to file
./VESP/vesp1_1 | tee log

# Extract data from memory writes to addresses between 0x100 and 0x2FF
cat log | grep -i "memory\[" | grep -E '0(1|2)[0-9A-F]{2}\] = [0-9A-F]{4}' | awk '{print $3}' | cut -c 3- | tr -d "\n" | xxd -r -p
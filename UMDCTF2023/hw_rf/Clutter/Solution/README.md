# Clutter - Solve

## Generate chall
1. Download [VeSPa](https://github.com/BusesCanFly/VESPa)
2. Generate vspa code

    `./gen_clutter.py > clutter.vspa`
3. Assemble vspa -> vsp
    `./VESPa/VESP_1.0/VESPa.py -p clutter.vspa > clutter.vsp`
    
## Solve 
1. Run `clutter.vsp` with long trace (important!) and save to file 
    `./VESP/vesp1_1 | tee log`
2. Extract data from memory writes to addresses between 0x100 and 0x2FF
    `cat log | grep -i "memory\[" | grep -E '0(1|2)[0-9A-F]{2}\] = [0-9A-F]{4}' | awk '{print $3}' | cut -c 3- | tr -d "\n" | xx
       │ d -r -p`
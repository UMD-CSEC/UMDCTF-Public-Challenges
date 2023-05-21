# notsogeo
Here is an early iteration of Geosint that is more similar to how GeoGuessr loads its Street View panorama. I wonder how we can find the location?

*HINT1:* The __original__ Geosint source can be found [here](https://github.com/JustHackingCo/geosint).

*HINT2:* I picked an impossible location to actually figure out where this is. If you find the location purely through geo OSINT, 
then you must be rainbolt's long-lost child.

## Build Instructions
TODO: generate cert and key on GCP server
```sh
docker build -t notsogeo .
docker run --name notsogeo-test -d -p EXTERNAL_PORT:6958 notsogeo
```

## Files for CTFd
none

## Flag
`UMDCTF{n0t_th3_b35t_1dea_exp0s!ng_th3_p4nor@ma_ID_3897334}`

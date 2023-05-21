# pop calc

Challenge Description for CTFd:

```txt
We have created a new calculator application to fit all your mathematical needs. Give it a try!
```

## Build Instructions

```sh
docker build -t pop-calc .

docker run -p EXTERNAL_PORT:5000 pop-calc
```

## Files for CTFd

N/A - Do __NOT__ provide the source for this challenge.

## Walkthrough

Flask/Jinja SSTI challenge. See `solve.py` script for solution. Requires user to recognize SSTI vulnerability in the calculator app. They can simply test `{{ 7*7 }}` to see 49 as the result instead of the string `"7*7"`. They then need leak the python environment variables to string together commands and get RCE to read the flag file.

One trick is that this web app actually HTML encodes everything, so to correctly read what environment variables they have access to, they will need to decode that to the correct ASCII when reading through the responses.

__Solve script made need to have Python index modified for Popen() for it to work.__


## Flag

`UMDCTF{wh3n_an_app_giv3s_u_ssti_p0p_calc}`
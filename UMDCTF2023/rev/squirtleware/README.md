# rev/squirtleware

hey, charmander found this weird program on his computer. he's convinced that squirtle stole something from him at a shakira concert, but he doesn't know how to ask for it back.

## Challenge Notes

This challenge is squirtle-themed malware. The player will get a copy of a "broken" client (golang) that interacts with the server (java).

They will have to reverse-engineer the client to figure out how to interact with the server in order to get the correct cookie and the encrypted flag. Then they must reverse-engineer the client to figure out how to decrypt the flag using their cookie.

The solution is to reimplement interacting with the server in order to get the encrypted bytes. 
Trim away the junk, decrypt, get image flag.

The client doesn't use the correct method to get the full flag. The correct method is 'BANDERA_COMPLETA_POR_FAVOR'.
The client hints at asking the server for the full flag.

Also, all of the client symbols are in Spanish.

## Building

### Server

```sh
./build.sh
```
After, in order to start the appropriate docker containers, you should be able to run

```sh
docker-compose up --build -d
```

There is an alternate way to do all of this:
```sh
make && make run
```

### Client

Should be like building a go binary, there will be a makefile.

```sh
make
```
## Solution
see `solution/solution.py`


## Flag
`UMDCTF{c4using_ch4o5_1n_my_5unni3s}`

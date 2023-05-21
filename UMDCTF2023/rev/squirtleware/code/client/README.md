# rev/squirtleware
client for interacting with the server.

## Solution
Reimplement interacting with the server in order to get the encrypted bytes. 
Trim away the junk, decrypt, get image flag.

The client doesn't use the correct method to get the full flag. The correct method is 'BANDERA_COMPLETA_POR_FAVOR'.
The client hints at asking the server for the full flag.

## Building
```bash
make
```

## Developer notes

This is the client. Disclaimer, all Spanish in here is Google Translate spanish.
Think: terrible malware dev or something...

Why? squirtle lore
# Solution

Reimplement interacting with the server in order to get the encrypted bytes. 
Trim away the junk, decrypt, get image flag.

The client doesn't use the correct method to get the full flag. The correct method is 'BANDERA_COMPLETA_POR_FAVOR'.
The user also must ask for the file name (base64 encoded). I suppose this gives the opportunity to explore the docker FS.
The client hints at asking the server for the full flag.

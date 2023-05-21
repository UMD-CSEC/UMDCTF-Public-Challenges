# But Like When 

Butlikewhen is a Golang reversing challenge. Under the hood, it gets the current date, adds a year to it, and then sums the digits. 
If the digits sum to a magic number, it prints out the flag. To make reverse engineering harder, the binary is built with 10,000 
plausible flags inside and the correct magic number is the index into the slice. 

## Solution

Magic number: 2031
Flag: UMDCTF{dictionary_time_travel_extremely_crazy}
# You Want Me To Run What??

This challenge is a reversing/pwn-y challenge. It is a Go binary that accepts a
string input, maps those bytes into memory, and will execute them. If the
program survives after executing them, it will give the user the flag.  The
kicker is that it will only execute the given bytes if the MD5 hash of the bytes
start and end with three 0s. 

## A solution: 
ÃIPGwZkdRIE

The gen.go will generate other solutions if you let it run long enough. It works 
by just generating random messages that follow an \xc3 until the MD5 collision occurs. 

## Flag
UMDCTF{cpus_love_collisions}
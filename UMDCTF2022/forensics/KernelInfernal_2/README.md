# Kernel Infernal 2

- `Author` -- drakemp

- `Points` -- 1000

- `Solves` -- 3


file: ubuntu20.04-5.4.0-99-generic-cloudimg-20220215.kdump

flag: fill-in UMDCTF{0x<ADDRESS>}

An import value for performing memory forensics is the CR3 contents, we so
happen have to the ability to get it from our crash dump in the previous
challenge. I dont want any CR3, I want the first CR3. 


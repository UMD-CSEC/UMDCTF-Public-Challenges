# DFA Speck 1

`Authors` -- drakemp, itsecgary

`Points` -- 1000

We managed to percisely inject bit faults on a piece of hardware running Speck 128/128. The faults
are injected right before the last round of the pt/ct side. Can you figure out what k32 (last round
key schedule) is from the faulted cipher texts? 

ex: if k32 was "aabbccddeeff0011" in hex, then
  flag format: "UMDCTF{aabbccddeeff0011}" 

provided in file:
- `ct`: original cipher text
- `XX`: i.e. `01`, `02`, ... this index corresponds to the bit fault position in the input to last round
   Example input to last round. 00 represents the least significant byte, ff most significant byte.
   if bit fault was in position `05:`
   ```
   7766554433221100 ffeeddccbbaa9988
                 || 
                /  \
       MSB  0000    0000  LSB
              ^ 
              faulted bit (aka flipped from original value) 
   ```
- faulted cipher texts fromat:
    ```
    XX: 7766554433221100ffeeddccbbaa9988  # provided format, 00 - LSB, ff - MSB
    
    7766554433221100 ffeeddccbbaa9988 # interpreted as uint64, uint64 in big-endian format
    ```

**Links:**
- https://en.wikipedia.org/wiki/Speck_%28cipher%29
- *hint*: https://eprint.iacr.org/2014/267.pdf 
    The paper provides fault injection attacks on both Simon and Speck. The Speck fault injection
    starts on page 9.

**Free Hints: **
- The MSB of k32 cannot be calculated with the formula in the paper.
- k32 is ASCII-readable if translated from hex to ASCII. 

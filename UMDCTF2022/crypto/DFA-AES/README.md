# DFA AES

`Author` -- drakemp

`Points` -- 990

We've managed to inject faults into a device executing AES. We arent sure what
its encrypting, but its only a single block. Here are all the faulted cipher
texts, can you get the original plain text block? Assume ECB.

The leading hex (`XX:`) are the bit fault positions. 

*UPDATE:* turns out the fault positions are slightly off, but those values are not needed and can be ignored as they do no affect the solve method. 

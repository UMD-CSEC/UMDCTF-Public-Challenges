# DFA Speck 2

`Authors` -- drakemp, itsecgary

`Points` -- 1000

`Solves` -- 3

Nice job on finding k32! The hard part is done. Eveything in part 1 is relevant here. Your task now
is to recover the original plaintexts. To help with this task, we've provide additional faulted
ciphers from injections to the second to last round inputs. 

The flag is the ASCII representation of the pt (like UMDCTF{16_char_flag_DFA}). The ASCII
representation of the plaintext should **make sense**. The plaintext is in order of "{pt_x}{pt_y}",
both uint64 values should be in Little endian for this, unlike the faulted cipher texts. 
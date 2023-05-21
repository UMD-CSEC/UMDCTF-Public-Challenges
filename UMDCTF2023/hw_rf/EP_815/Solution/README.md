# EP_815 - Solve

Note: I renamed `smuggled.vsp` to `program.vsp` for CTFd, to not give too much away

## Solve
1. Run `smuggled.vsp` with long trace (important!) and save to file 

    `./VESP/vesp1_1 | tee log`
2. Extract all smuggled bytes and decode

    `cat log | grep -B 3 -e ADD -e HLT | grep IR | awk '{print $6}' | cut -c 2- | tr -d "\n," | xxd -r -p`

## Files
 - smuggle.vspa 
 - smuggle.vsp
 - smuggle**d**.vsp (only file with flag!)

## Flag check
`diff smuggle.vsp smuggled.vsp | grep ">" | cut -c 4- | tr -d "\n" | xxd -r -p`

## Idea
In theory the code does:
```
LDA A 0
LDA B 0
LDA 0x10 0
LDA A 0
LDA B 1
LDA 0x10 0
ADD
SUB
ADD
SUB
ADD
SUB
ADD
SUB
LDA 0x10 10
LDA A 1
MOV B 0x10
ADD
HLT
```

and it runs that fine, but the ADD, CMP, and HLT instructions have their lower 3 bytes filled with flag data since the MSB (the opcode) is the only thing used for them.
(SUB is a pseudo-instruction that calls ADD and CMP)

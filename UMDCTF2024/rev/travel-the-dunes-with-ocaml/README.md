# Travel the Dunes with OCaml

`ocaml_executable` is a flag checker compiled and assembled from OCaml using `ocamlopt`. Can you rev it?

### Hints

Hint 1: The flag is `123` characters in length.

## Build Instructions

Install OCaml, then run `ocamlopt main.ml -o ocaml_executable`

## Files for CTFd

+`ocaml_executable`

## Flag

`UMDCTF{rvgxbvhm89tc83oc3t84mo90m83dt4m_____s3R10Us1Y_whO_@ctu@11y_usEs_0c@m1???_____al7of37d3otdxlsdt8nysfln8y43fsg7xuvnsf}`

## Writeup (Outdated - will fix later)


### Explaination

Ghidra pretty much fails on this challenge. We'll use **Binary Ninja** (Binja) to help us decypher what is going on in this ELF file: https://binary.ninja/free/

OCaml comes with a native-code compiler named `ocamlopt`, which is basically a way to turn OCaml programs into executable files for your system. `ocaml_executable` is one such instance.

Let's start by opening `ocaml_executable` in Binja:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/2e5e945d-cf51-4007-a394-d86f3e667b05)

Looking into `caml_main(...)`, we click through to `caml_start_program(...)`:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/667ae049-c1f6-4140-b8b2-8627157d8c05)

Going down the function chain, we finally find our entry point:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/8a866ae2-42ad-4bc0-80d4-73f2ec9cf629)

In `camlMain_entry(...)`, we observe the 5 segments of the flag checker:

```
1.) Display user prompt

2.) Get possible flag from user

3.) Check lengths of flag - if the lengths are different, we simply tell the user and quit instantly.
Recall from (Hint 2) that the flag is 123 characters long. OCaml compares the length doubled, hence the "if (<input> == 0xf6)" part, where "0xf6" is "246" or 123 times 2 in decimal.

4.) Call the character comparer function (camlMain__check_input_306) if we need to

5.) Display final messages and quit
```

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/72e7c08b-2581-475d-8d3c-6dc94cabe0a4)

Diving into the comparer function, things now make a little more sense - when an input equal in length to the flag is submitted, the program individually checks each character of the input to see if it matches the flag.

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/c7b0c946-e33d-4694-b893-17c1d59fefe1)

Done unsuccessfully, it will look something like this for all 123 characters:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/e3a5a440-1be7-4a48-a4b6-eca254dbfd78)

Done successfully, it will look like this instead:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/1a76f9d6-abe9-4dec-afb9-92000e4790ea)


### The Solution

Now... What if during each character comparison cycle, we patched the assembly code to simply print out a character from the flag instead?

We can infer that the flag is stored in `rax` by the use of `List__nth` here:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/fadcdcee-b880-402f-a300-12fa5258cebd)

Now switch to the disassembly. When the flag checker outputs `Checking: <char>` using `printf`, it grabs a user-submitted character off the stack. What if we patched the `printf` to show the other character on the stack instead?

**Before:**

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/b3fe81ee-e852-45dc-8274-fec3fa75e828)

**After:**

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/7561757f-ac78-43d0-aaea-5f752d06439f)

#### Result:

![image](https://github.com/UMD-CSEC/UMDCTF-2024-Challenges/assets/123607179/fd822679-d977-45e0-8183-386a40bb6486)

We now have our flag!


**P.S:** You could've also datamined or brute-forced the flag.













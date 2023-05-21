#!/usr/bin/env python3

from random import randint

flag = "554D444354467B557831332D7573332D6D336D3072792D77317033217D0A"
n = 2
flag_chars = [hex(int(flag[i:i+n], 16)) for i in range(0, len(flag), n)]
# print(flag_chars)

print("LDA A 0\nLDA B 0\n")
for char in flag_chars:
    offset = randint(0,9)
    data = hex(int(char, 16)-offset)
    address = hex(randint(256, 767)) # between 0x100 and 0x2FF
    code = f"LDA B {offset}\nLDA A {data}\nADD\nMOV {address} A"""
    print(code)
print("HLT")
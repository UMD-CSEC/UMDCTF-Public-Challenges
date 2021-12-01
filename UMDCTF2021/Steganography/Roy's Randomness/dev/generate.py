from scapy.all import *

MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

def send_letter(val):
    if val == ".":
        flags = "S"
    elif val == "-":
        flags = "R"
    else:
        flags = "P"
    send(IP(src="128.8.0.0", dst="128.8.0.1") / TCP(sport=1337, dport=31337, flags=flags), iface='wlo1')

flag = "UMDCTF-{r0y_f0und_m0r53}"

for c in flag:
    hex_val = hex(ord(c))[2:]
    if len(hex_val) == 1:
        hex_val = "0" + hex_val
    hex_val = hex_val.upper()
    morse_1 = MORSE_CODE_DICT[hex_val[0]]
    morse_2 = MORSE_CODE_DICT[hex_val[1]]
    for letter in morse_1:
        send_letter(letter)
    send_letter(None)
    for letter in morse_2:
        send_letter(letter)
    send_letter(None)
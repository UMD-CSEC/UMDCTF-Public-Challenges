#!/usr/local/bin/python
from collections import Counter

c = input("> ")[:100000] # sorry i'm poor i can't consume more tokens than that

def gen():
    s = 1
    while True:
        yield s
        s *= 2

assert all(i==j for i,j in zip(sorted(Counter(c).values()),gen()))
assert all("~">=i not in "#'\" \t\n\r\x0c\x0b" for i in c) # these tokens do not incite proper insider trading!!!

exec(c)

# Multiple Time Pad (MTP)

`Author` -- itsecgary

`Points` -- 149

One-time pad? More like multiple-time pad ;)

NOTE: You can assume that the plaintexts are grammatically-correct English sentences

FLAG FORMAT: Concatenate all 8 plaintext sentences together like so: `"[pt1][pt2][pt3][pt4][pt5][pt6][pt7][pt8]"` and
take the MD5 hash of this string. Wrap the MD5 hash in the flag format to submit.

```
import hashlib
plaintexts = [...]

pt_str = ''
for pt in plaintexts:
    pt_str += pt

print('UMDCTF{' + hashlib.md5(pt_str.encode()).hexdigest() + '}')
```


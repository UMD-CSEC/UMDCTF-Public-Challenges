from collections import Counter

base = 'quit.__class__.__eq__=input;q=quit==quit;quit.__class__.__eq__=exec;quit==q'

base += ";p"*29 + "=" + "n"*63 + "a"*126 + "c"*253 + "e"*508 + "p"*994 + "q"*2039 + "u"*4090 + "i"*8186 + "t"*16378 + "s"*32764

exec(base)
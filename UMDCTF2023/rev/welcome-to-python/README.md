
# Welcome to Python!

Jimmy has a Python program which compiled into something he's never seen. Can you fix it?

## Build Instructions

 1. Call `pyinstaller -F chal.py`on a Ubuntu instance running Python 3.10
 2. Head to `/dist`. A single-file executable named `chal` should now exist! This is what you're looking for.

## Files for CTFd

 - `chal` executable (compiled with Python 3.10 on Ubuntu 22.04.1 LTS, WSL)

## Flag

`UMDCTF{0_0+-+eXP-eLLiARm_us_!!!-12345}`

## Writeup
First, we need to decompile the executable. 

 1. Use pyinstxtractor (https://github.com/extremecoders-re/pyinstxtractor) to turn the executable into a set of .pyc files. 
 2. Find chal.pyc among the output. Then, use pycdc (https://github.com/zrax/pycdc) to extract the python binary into readable code! 

	(Decomplication with pycdc)
	
		# Source Generated with Decompyle++
		# File: chal.pyc (Python 3.10)

		from math import sqrt, sin, cos
		from ctypes import c_uint32, c_float
		from sys import exit as exit_
		source = [
		    672662614,
		    741343303,
		    495239261,
		    744259788,
		    722021046,
		    0xA70AA247L,
		    1053692,
		    0xA8050035L,
		    0xA982A820L,
		    624689,
		    0xA90D20BCL,
		    41134,
		    295340,
		    0xA0028102L,
		    622681,
		    576469,
		    671170814,
		    0x8041086EL,
		    765,
		    680595550,
		    0x80200166L,
		    698368102,
		    2437137,
		    0x8042C1EEL,
		    570966112,
		    4612341,
		    0x800008D4L,
		    0xA94D02CEL,
		    16484,
		    2103301,
		    136226,
		    9438506,
		    663820758,
		    0x8013523BL,
		    8405532,
		    0xA4000875L,
		    0x80030A78L,
		    136768]
		seed = 64

		def wandom(x):
		    return x * x * cos(x) * sin(x) / 1000


		def evil_bit_hack(y):
		    return int(c_uint32.from_buffer(c_float(y)).value)

		print('==========================================')
		print('Professional flag checker service (v 97.2)')
		print('==========================================')
		flag = input('Show me the flag: ')
		lf = len(flag)
		ls = len(source)
		l = lf if lf < ls else ls
		for i in range(seed, seed + l):
		    w = wandom(i)
		    c = ~(~ord(flag[i - seed]) ^ evil_bit_hack(wandom(wandom(w))) & evil_bit_hack(w)) + 1
		    if source[i - seed] != c:
		        print("Uh oh! We don't think your flag is correct... :(")
		        exit_(1)
		if lf == ls:
		    print('Your flag is correct!')
		    return None
		None('Some of your flag is correct...')

 3. Finally, we have something we can work with. Analyze the decomplication and reverse-engineer the flag with something like this:
 
		from math import sqrt, sin, cos
		from ctypes import c_uint32, c_float

		source = [672662614, 741343303, 495239261, 744259788, 722021046, 2802491975, 1053692, 2818900021, 2843912224, 624689, 2836209852, 41134, 295340, 2684518658, 622681, 576469, 671170814, 2151745646, 765, 680595550, 2149581158, 698368102, 2437137, 2151858670, 570966112, 4612341, 2147485908, 2840396494, 16484, 2103301, 136226, 9438506, 663820758, 2148749883, 8405532, 2751465589, 2147682936, 136768]
		seed = 64

		def wandom(x):
		    return (x * x * cos(x) * sin(x)) / 1000

		def evil_bit_hack(y):
		    return int(c_uint32.from_buffer(c_float(y)).value)

		output = ""
		for i in range(seed, seed + len(source)):
		    w = wandom(i)
		    output += chr(~(evil_bit_hack(w) & evil_bit_hack(wandom(wandom(w))) ^ (~source[i - seed] + 1)))

		print(output)
 

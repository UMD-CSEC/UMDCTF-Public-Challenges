#Don't post this to CTFd!

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




# Introduction to C

*"Welcome to CMSC216. Weeeeee have a lecture worksheet that the TAs will now hand out. You must write your name, student ID, and discussion session **CORRECTLY** at the top of the worksheet. I have 369 students, so any time I need to spend finding out who to grade will cause YOU to lose credit." (Larry Herman)*

## Build Instructions

 1. Run `builder.py` to create `intro_to_c.png` and `intro_to_c.txt`!

## Files for CTFd

 - `intro_to_c.txt`
 - `intro_to_c.png`

## Flag

`UMDCTF{pu61ic_st@t1c_v0ID_m81n_s7r1ng_@rgs[]!!!}`

## Writeup

 The given `.png` is a C source file encoded into pixels! By looking at `intro_to_c.txt`, we can see which characters are mapped to which RGB color values:
 ```Key: 0, Value: RGB(0, 0, 0)
Key: 1, Value: RGB(210, 126, 15)
Key: 2, Value: RGB(164, 252, 30)
Key: 3, Value: RGB(118, 122, 45)
(...etc...)
```
<small>*(The characters are in integer representation)*</small>


This knowledge allows us to reverse-engineer the original C source code with this simple python script:
```
from PIL import Image

#I've omitted the process of reading the .txt file and remapping RGB->characters. 
#This loop below, generates the mapping from scratch
color_to_ascii = {}
for i in range(128):
    r = (i*722) % 256
    g = (i*126) % 256
    b = (i*15) % 256
    color_to_ascii[(r, g, b)] = chr(i)

image = Image.open('intro_to_c.png')

image_width, image_height = image.size

decoded_text = ''

for y in range(image_height):
    for x in range(image_width):
        color = image.getpixel((x, y))
        char = color_to_ascii.get(color, '')

        decoded_text += char

print(decoded_text)
```



...which then compiles into an executable, printing us our flag!
```
user@DESKTOP:/mnt/c/Users/me/Downloads/Introduction to C$ gcc -o intro_to_c intro_to_c.c 
user@DESKTOP:/mnt/c/Users/me/Downloads/Introduction to C$ ./intro_to_c
UMDCTF{pu61ic_st@t1c_v0ID_m81n_s7r1ng_@rgs[]!!!}
```


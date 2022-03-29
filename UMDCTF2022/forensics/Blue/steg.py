from PIL import Image
import random

filename = 'blue.png'
orig_image = Image.open(filename)
pixels = orig_image.load()
width, height = orig_image.size

with open('flag.txt', 'r') as f:
    flag = f.read().strip()

for y in range(len(flag)):
    for a in range(ord(flag[y])):
        x = random.randrange(0,width-1)
        c = random.randrange(0,3)
        pixel = list(orig_image.getpixel((x, y)))
        pixel[c] += 1
        pixels[x, y] = (pixel[0], pixel[1], pixel[2])

orig_image.save('bluer.png')


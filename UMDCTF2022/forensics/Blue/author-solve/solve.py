from PIL import Image

filename = 'bluer.png'
im = Image.open(filename)
pixels = im.load()
width, height = im.size

flag = ''
base_pixel = list(pixels[width-1,height-1])
print(base_pixel)
y = 0
while 1:
    count = 0
    for x in range(width):
        rgb = list(pixels[x,y])
        #print(f'pixel at ({x}, {y}) is {rgb}')
        count += (rgb[0]-base_pixel[0]) + (rgb[1]-base_pixel[1]) + (rgb[2]-base_pixel[2])
        #print(count)
    
    #print(f'count = {count}')
    flag += chr(count)
    #print(f'count = {count}')
    if count == 0:
        break

    y += 1

print(f'flag = {flag}')

from PIL import Image

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

from PIL import Image

def generate_ascii__to_color_mappings():
    ascii_to_color = {}

    for i in range(128):
        r = (i*722) % 256
        g = (i*126) % 256
        b = (i*15) % 256
        ascii_to_color[chr(i)] = (r, g, b)

    return ascii_to_color

def generate_challenge(ascii_to_color):  
    with open('intro_to_c.c', 'r') as file:
        text = file.read()

    text_length = len(text)
    image_width = int(text_length ** 0.5) + 1
    image_height = int(text_length / image_width) + 1

    image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))

    for i, char in enumerate(text):
        color = ascii_to_color.get(char, (0, 0, 0))
        x = i % image_width
        y = int(i / image_width)
        image.putpixel((x, y), color)

    image.save('intro_to_c.png')

    

ascii_to_color = generate_ascii__to_color_mappings()

for key in ascii_to_color.keys():
    print("Key: {}, Value: RGB{}".format(ord(key), ascii_to_color[key]))
    
generate_challenge(ascii_to_color)


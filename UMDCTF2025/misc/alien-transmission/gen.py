import numpy as np
import random
from skimage.io import imread, imsave


filename = "./flag.png"
img = imread(filename, as_gray=True)

(width, height) = img.shape

random.seed(420)
kernel = [[float(random.randint(-10,10)) for _ in range(19)] for _ in range(19)]
print(kernel)
q = sum(sum(kernel, start=[]))
print(q)

kernel = [[a / q for a in r] for r in kernel]

output_data = []
for x in range(9, width-9):
    row = []
    for y in range(9, height-9):
        p = 0.0
        for i in range(-9, 10):
            for j in range(-9, 10):
                p += img[x+i, y+j] * kernel[i+9][j+9] 
        row.append((0, p, 0))
    output_data.append(row)

output_data = np.array(output_data)
output_data = np.interp(output_data, (-10, 10), (0, 256))
output_data = np.uint8(np.round(output_data))
imsave("output.png", output_data)

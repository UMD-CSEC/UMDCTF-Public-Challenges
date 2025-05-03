import numpy as np
import skimage.restoration as restoration
import random
from skimage.io import imread
from matplotlib import pyplot as plt

random.seed(420)
kernel = np.flip(np.array([[float(random.randint(-10,10)) for _ in range(19)] for _ in range(19)]))
kernel /= sum(sum(kernel))

img = np.double(imread("./output.png"))[:,:,1]

img = np.interp(img, (0, 256), (-10.0, 10.0))

deconvolved_img = restoration.unsupervised_wiener(img, kernel)[0]

plt.imshow(deconvolved_img, vmin=deconvolved_img.min(), vmax=deconvolved_img.max())
plt.show()

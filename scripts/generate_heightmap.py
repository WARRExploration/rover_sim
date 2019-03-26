#!/usr/bin/env python

from PIL import Image
import numpy as np
import os

dirname = os.path.dirname(__file__)

path = os.path.join(dirname, "../providedFiles/erc2018/DTM_ver2.csv")

data = np.loadtxt(open(path, "rb"), delimiter=",", skiprows=2)

w, h = data.shape
data -= np.min(data)
data /= np.max(data)
data *= 255
data = np.stack((data,)*3, axis=-1)

img = Image.fromarray(np.uint8(data), 'RGB')
img = img.resize((129, 129), resample=Image.BICUBIC)

path = os.path.join(dirname, "../worlds/terrain.png")
img.save(path)
img.show()

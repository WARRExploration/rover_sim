#!/usr/bin/env python

from PIL import Image
import numpy as np
import os
from argparse import ArgumentParser


parser = ArgumentParser(description = "Creates heightmap from .csv to .png")
parser.add_argument("-i", "--input", type=str, help = "Path to heightmap .csv file",
                    nargs="?", default="../providedFiles/erc2018/DTM_ver2.csv")
parser.add_argument("-o", "--output", type=str, help = "Path to generated .png heightmap",
                    nargs="?", default="../worlds/terrain.png")

args = parser.parse_args()

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, args.input)

data = np.loadtxt(open(path, "rb"), delimiter=",", skiprows=2)

w, h = data.shape
data -= np.min(data)
data /= np.max(data)
data *= 255
data = np.stack((data,)*3, axis=-1)

img = Image.fromarray(np.uint8(data), 'RGB')
img = img.resize((129, 129), resample=Image.BICUBIC)

path = os.path.join(dirname, args.output)
img.save(path)
img.show()

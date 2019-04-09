#!/usr/bin/env python
"""
This script generates terrain in the ERC provided format and writes it down into a csv file

Todo:
Replace hardcode of file paths and variables with an apropriate command line arguements

"""


from PIL import Image
import numpy as np
import os 
import random
import csv
from sys import maxsize
from noise import pnoise2 # if error: pip install noise
from argparse import ArgumentParser

#couldn't test the script because segfault, sry :)

parser = ArgumentParser(description = "Creates random heightmap as .csv")
parser.add_argument("-o", "--output", type=str, help = "Path to heightmap csv file",
                    nargs="?", default="../generated_maps/map.csv")

args = parser.parse_args()

map_height = 110
map_width = 60
rows_spacing = 0.5
columns_spacing = 0.5
noise_base = random.randint(0,100)

max_altitude = 2
min_altitude = -0.5
data = np.empty ([map_width, map_height])

iterator = np.nditer(data, flags=["multi_index"], op_flags=['writeonly'])

# Calculating noise
while not iterator.finished:
    iterator[0] = round(pnoise2 (iterator.multi_index[0]/ map_width, iterator.multi_index[1]/map_height, octaves = 4, base = noise_base), 5)
    iterator.iternext()

#Normalizing noise within range
data = min_altitude + (max_altitude - min_altitude) * (data - np.min(data))/(np.max(data) - np.min(data)) 


dirname = os.path.dirname(__file__)
path = os.path.join(dirname, args.output) 

with open(path, 'w+', newline='') as f:
    writer = csv.writer(f, delimiter="|" , quoting = csv.QUOTE_NONE)
    writer.writerow (["Number of Rows ",  " Number of Columns ", " Grid spacing rows ", " Grid spacing columns ", " Coordinates of the first point in the matrix (x,y)"])   
    writer = csv.writer(f, delimiter=" " , quoting = csv.QUOTE_NONE)
    writer.writerow ([str(map_height), str(map_width), str(rows_spacing), str(columns_spacing), str(0), str(map_height//2)])
    
    s1 = "Number of Rows | Number of Columns | Grid spacing rows | Grid spacing columns | Coordinates of the first point in the matrix (x,y)"
    s2 = str(map_height) + str(map_width) + str(rows_spacing) + str(columns_spacing) + str(0) + str(map_height//2)

    np.savetxt(f, data, fmt="%.5f", delimiter=",")


# Uncomment this if you want to get nice pictures as the output
"""
w, h = data.shape
data -= np.min(data)
data /= np.max(data)
data *= 255
data = np.stack((data,)*3, axis=-1)

img = Image.fromarray(np.uint8(data), 'RGB')

path = "../worlds/gterrain.png"
img.save(path)
img.show()
"""

#!/usr/bin/env python3

#TODO use python 2?

#TODO give a seed value, and save it somewhere, so we can recreate the exaxt same random world

#TODO specify size in arguments

"""
This script generates terrain in the ERC provided format and writes it down into a csv file

Todo:
Replace hardcode of file paths and variables with an apropriate command line arguements

"""


from PIL import Image
import numpy as np
import os, sys
import random
import csv
import io
from sys import maxsize
from noise import pnoise2 # if error: pip install noise (or pip3)
from argparse import ArgumentParser
from rospkg import RosPack # if error: pip3 install rospkg

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))


def create_random_heightmap(output_file):
    """Creates random heightmap as .csv
    
    Arguments:
        output_file {str} -- Path of generated heightmap csv file
    """

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


    with io.open(output_file, 'w+', newline='') as f:
        writer = csv.writer(f, delimiter="|" , quoting = csv.QUOTE_NONE)
        writer.writerow (["Number of Rows ",  " Number of Columns ", " Grid spacing rows ", " Grid spacing columns ", " Coordinates of the first point in the matrix (x,y)"])   
        writer = csv.writer(f, delimiter=" " , quoting = csv.QUOTE_NONE)
        writer.writerow ([str(map_height), str(map_width), str(rows_spacing), str(columns_spacing), str(0), str(map_height//2)])
    

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




if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


    # parse command line arguments
    parser = ArgumentParser(
        description="Creates random heightmap as .csv",
        formatter_class=ArgumentDefaultsHelpFormatter    
    )
    parser.add_argument("-o", "--output", type=str, help = "Path of generated heightmap csv file")
    args = parser.parse_args()

    # generate model
    create_random_heightmap(args.output)

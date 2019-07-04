#!/usr/bin/env python
"""
snap the landmarks to the terrain according to the heights provided in the heightmap
"""

import numpy as np
import os, sys
from rospkg import RosPack
import csv

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

def get_context_info_from_csv(csv_file_path):
    """This function extracts the context info from a csv file based on the provided files of the ERC

    Arguments:
        csv_file_path {str} -- path to the ERC csv file (ver2)

    Returns:
        () -- touple containing the spacing and the coordinates of the first point in the matrix
    """

    # read context informations from *.csv file
    with open(csv_file_path) as fp:
        for i, line in enumerate(fp):
            if i != 1:
                continue

            # we are only interested in the spacing and coords_0
            _, _, spacing_y, spacing_x, x_0, y_0 = np.fromstring(line, dtype=float, sep=' ')

            break

    return (spacing_y, spacing_x, x_0, y_0)


def get_heights_from_csv(csv_file_path):
    """This function extracts the heights from a csv file based on the provided files of the ERC

    Arguments:
        csv_file_path {str} -- path to the ERC csv file (ver2)

    Returns:
        [[]] -- array of heights
    """

    # load heights from *.csv file
    heights = np.loadtxt(open(csv_file_path), delimiter=',', skiprows=2)

    # transform the matrix so heights are accessible by intuitive indices
    heights = np.swapaxes(np.flip(heights, 0), 0, 1)

    # apply threshold (set invalid values to 0)
    heights[heights >= 2.8] = 0

    return heights

def get_landmark_coords_from_csv(csv_file_path):
    """This function extracts the landmarks' coordinates from a csv file based on the provided 
        files of the ERC
    
    Arguments:
        csv_file_path {str} -- path to the ERC csv file (Landmarks)

    Returns:
        [[]] -- array of coordinates
    """

    # load coords from *.csv file
    coords = np.loadtxt(open(csv_file_path), delimiter=',', skiprows=1, usecols=(1,2))

    return coords

def interpolate_heights(context_info, heights, coords, offset):
    """This function interpolates the correct heights at a coordinate based on the provided heightmap
    
    Arguments:
        context_info {()} -- spacing and coordinates of the first point in the matrix
        heigths {[[]]} -- array of heights provided by a heightmap
        coords {[[]]} -- array of landmarks' coordinates

    Returns:
        [] -- array of interpolated heights
    """

    # extract the context information
    spacing_y, spacing_x, x_0, y_0 = context_info
    number_of_cols, number_of_rows = heights.shape

    # convert y_0 to actual coordinate at ind_y=0
    y_0 -= (number_of_rows-1)*spacing_y

    # init the new heights
    landmark_heights = []

    # for each landmark, interpolate the correct height
    for (coord_x, coord_y) in coords:

        # index left of x-coord
        ind_x = (int) ((coord_x - x_0) / spacing_x)

        # absolute offset to x-coordinate at ind_x
        offset_x = (x_0 + coord_x) % spacing_x      # x_0 as it might not be a multiple of spacing_x

        # offset percentage
        offset_x /= spacing_x

        # same for the y-coord
        ind_y = (int) ((coord_y - y_0) / spacing_y)
        offset_y = (y_0 + coord_y) % spacing_y
        offset_y /= spacing_y

        #interpolate
        height = (offset_x * offset_y * heights[ind_x][ind_y] 
                    + offset_x * (1-offset_y) * heights[ind_x][ind_y+1]
                    + (1-offset_x) * offset_y * heights[ind_x+1][ind_y]
                    + (1-offset_x) * (1-offset_y) * heights[ind_x+1][ind_y+1])

        # add static offset
        height += offset

        # adapt values to precision of the given *.csv files
        height = round(height, 2)

        # save landmarks' heights in a list
        landmark_heights.append(height)

    return landmark_heights

def save_fixed_landmarks(output, landmarks, landmark_heights):
    """This function saves the newly interpolated heights to a proper output file
    
    Arguments:
        output {str} -- path to output file (fixed landmarks)
        landmarks {str} -- path to input file (original landmarks)
        landmark_heights {[]} -- array of landmarks' interpolated heights
    """

    # read original landmarks' information from file
    with open(landmarks, 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)

    readFile.close()

    # replace old heights by newly interpolated ones
    for i in range(len(lines)):
        if i == 0:
            continue

        lines[i][3] = landmark_heights[i-1]

    # write the new landmark file
    with open(output, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

    writeFile.close()

def fix_landmark_heights(heightmap, landmarks, output, offset):
    """snap the landmarks to the terrain according to the heights provided in the heightmap

    Arguments:
        heightmap {str} -- path to the ERC csv file (ver2)
        landmarks {str} -- path to input file (original landmarks)
        output {str} -- path to output file (fixed landmarks)
        offset {float} -- height offset added to all landmarks
    """

    # read context info
    context_info = get_context_info_from_csv(heightmap)

    # read heigths
    heights = get_heights_from_csv(heightmap)

    # read landmark coords
    coords = get_landmark_coords_from_csv(landmarks)

    # calculate the correct heights by interpolating
    landmark_heights = interpolate_heights(context_info, heights, coords, offset)

    # save new heights to a proper *.csv file
    save_fixed_landmarks(output, landmarks, landmark_heights)


if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    
    # default values
    heightmap_csv_path = os.path.join(rover_sim_dir, 'worlds/erc2018final/Heightmap.csv')
    landmarks_csv_path = os.path.join(rover_sim_dir, 'worlds/erc2018final/Landmarks.csv')
    fixed_landmarks_path = os.path.join(rover_sim_dir, 'worlds/erc2018final/Landmarks.csv')
    height_offset = 0

    # parse command line arguments
    parser = ArgumentParser(
        description="snap the landmarks to the terrain according to the heights provided in the heightmap",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-m", "--heightmap", type=str, help="path to an ERC csv file (ver2)", default=heightmap_csv_path)
    parser.add_argument("-l", "--landmarks", type=str, help="path to a heightmap csv file", default=landmarks_csv_path)
    parser.add_argument("-o", "--output", type=str, help="output path for fixed landmarks csv file", default=fixed_landmarks_path)
    parser.add_argument("-s", "--offset", type=float, help="height offset added to all landmarks", default=height_offset)
    args = parser.parse_args()

    # fix landmark heigths
    fix_landmark_heights(heightmap=args.heightmap, landmarks=args.landmarks, output=args.output, offset=args.offset)

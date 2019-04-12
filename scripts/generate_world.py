#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script calls all the necessary generation scripts and creates a world folder
from specified provided files. If the world already exists, it replaces 
landmarks and terrain but keeps manual changes to the .world file
"""
from lxml import etree
import os.path as op
import os, sys
import copy
from argparse import ArgumentParser
from shutil import copy2, copyfile
import subprocess

from rospkg import RosPack

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

from rover_sim.scripts.landmarks.generate_landmarks import create_landmarks
from rover_sim.scripts.generate_terrain import generate_terrain


def create_world(name,  landmarks, heightmap, random=False):
    """generates a full gazebo model for a ERC landmark
    
    Arguments:
        name {str} -- name of the generated world in rover_sim/worlds
        landmarks {str} -- path to landmarks csv file
        heightmap {str} -- path to heightmap csv file (ERC ver2)
    TODO is {bool} correct here?
        random {bool} -- create a random heightmap custom to world (default: {False})
    """


    dirname = op.dirname(__file__)
    base_path = op.join(dirname, op.pardir, "worlds", name)
    custom_models = op.join(base_path, "models")

    world_file = op.join(base_path, "world.world")
    landmarks_csv = op.join(base_path, "Landmarks.csv")
    heightmap_csv = op.join(base_path, "Heightmap.csv")

    terran_name = "terrain"
    all_landmarks = "all_landmarks"



    if not op.isdir(custom_models):
        os.makedirs(custom_models)

    if landmarks is not None:
        copyfile(landmarks, landmarks_csv)

    if heightmap is not None:
        copyfile(heightmap, heightmap_csv)


    # Terrain and Landmarks generation
    if random:
        subprocess.call(["python", op.join(dirname, "generate_random_heightmap.py"),
                    "--output", heightmap_csv])


    generate_terrain(name=terran_name, csv_file_path=heightmap_csv, output_folder=custom_models)

    #all_landmarks_model(landmarks_csv, op.join(rover_sim_dir, "models", "landmarks")) # ↓TODO
    create_landmarks(name=all_landmarks, input_csv_path=landmarks_csv, output_path=custom_models, landmark_models_path="/tmp/not_used_yet_TODO")


    # .world file creation, not modified if already present
    if not op.exists(world_file):    
        root = etree.Element('sdf')
        root.set("version", "1.3")
        tree = etree.ElementTree (root)
        world = etree.Element ('world')
        world.set("name", "default")
        root.append(world)

        scene = etree.Element("scene")
        grid = etree.SubElement(scene,"grid")
        grid.text = "false"
        world.append(scene)

        include_sun = etree.Element("include")
        uri = etree.SubElement(include_sun,"uri")
        uri.text = "model://sun"
        world.append(include_sun)


        include_terrain = etree.Element("include")
        uri = etree.SubElement(include_terrain,"uri")
        uri.text = "model://terrain"
        world.append(include_terrain)

        include_landmarks = etree.Element("include")
        uri = etree.SubElement(include_landmarks,"uri")
        uri.text = "model://all_landmarks"
        world.append(include_landmarks)


        #print(etree.tostring(worl_file, pretty_print=True, encoding='utf8', xml_declaration=True))
        tree.write(world_file, pretty_print=True, encoding='utf8', xml_declaration=True)


if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    # parse command line arguments
    parser = ArgumentParser(
        description="Creates world in worlds directory",
        formatter_class=ArgumentDefaultsHelpFormatter    
    )

    parser.add_argument("-w", "--world", type=str, help = "World name, updates world if already exists", nargs="?", default="Generated")
    parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file")
    parser.add_argument("-m", "--heightmap", type=str, help = "Path to heightmap csv file (ERC ver2)")
    parser.add_argument("-r", "--random", action="store_true", help = "Random heightmap and landmarks")
    args = parser.parse_args()

    # generate model
    create_world(name=args.world, landmarks=args.landmarks, heightmap=args.heightmap, random=args.random)
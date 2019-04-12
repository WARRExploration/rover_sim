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
import shutil
import subprocess

from rospkg import RosPack

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

from rover_sim.scripts.landmarks.generate_landmarks import create_landmarks
from rover_sim.scripts.generate_terrain import generate_terrain
from rover_sim.scripts.generate_random_heightmap import create_random_heightmap


def create_world(name, template_dir, landmarks, heightmap, random=False, force=False):
    """generates a full gazebo model for a ERC landmark
    
    Arguments:
        name {str} -- name of the generated world in rover_sim/worlds
        template_dir {str} -- template folder with correctly named resources for generation
        landmarks {str} -- path to landmarks csv file
        heightmap {str} -- path to heightmap csv file (ERC ver2)
        random {bool} -- create a random heightmap custom to world (default: {False})
        force {bool} -- delete old generated world files (default: {False})
    """


    dirname = op.dirname(__file__)
    base_path = op.join(dirname, op.pardir, "worlds", name)
    custom_models = op.join(base_path, "models")
    backup_models = custom_models + ".backup"

    world_name = "world"
    terran_name = "terrain"
    all_landmarks = "all_landmarks"
    landmarks_name = "Landmarks"
    heightmap_name = "Heightmap"

    world_file = op.join(base_path, world_name + ".world")
    landmarks_csv = op.join(base_path, landmarks_name + ".csv")
    heightmap_csv = op.join(base_path, heightmap_name + ".csv")


    if not op.isdir(base_path):
        os.makedirs(base_path)

    if force:
        if op.exists(world_file):
            print("Removing old world file at " + world_file)
            os.remove(world_file)
        if op.isdir(custom_models):
            print("Removing old models folder at " + custom_models)
            shutil.rmtree(custom_models)
        if op.isdir(backup_models):
            print("Removing old models backup folder at " + backup_models)
            shutil.rmtree(backup_models)
    

    ## Create or pull in Resources

    if random:
        # need the subprocess call because random_heightmap uses python3
        subprocess.call(["python3", op.join(dirname, "generate_random_heightmap.py"),
                "--output", heightmap_csv])
    
    #TODO add generate_random_landmarks.py once the script is ready


    if template_dir is not None:
        template_land = op.join(template_dir, landmarks_name + ".csv")
        if op.exists(template_land):
            shutil.copyfile(template_land, landmarks_csv)

        template_height = op.join(template_dir, heightmap_name + ".csv")
        if op.exists(template_height):
            shutil.copyfile(template_height, heightmap_csv)


    if landmarks is not None:
        shutil.copyfile(landmarks, landmarks_csv)

    if heightmap is not None:
        shutil.copyfile(heightmap, heightmap_csv)


    if not os.path.exists(heightmap_csv):
        raise ValueError(" heightmap file needed at " + heightmap_csv 
                        + "\nProvide one manually or run generate_world with 'random' flag")
    
    if not os.path.exists(landmarks_csv):
        raise ValueError("landmark file needed at " + landmarks_csv 
                        + "\nProvide one manually or run generate_world with 'random' flag")

        

    ## Generate the Models from the Resources

    if os.path.exists(custom_models):
        if not os.path.isdir(custom_models):
            raise ValueError("'models' has to be a directory, found file at " + custom_models)
        else:
            if os.path.exists(backup_models):
                print("Removing the old backup folder")
                shutil.rmtree(backup_models)
            print("Copying old 'models' folder to backup at " + backup_models + "\n")
            os.rename(custom_models, backup_models)
    
    os.mkdir(custom_models)


    generate_terrain(name=terran_name, csv_file_path=heightmap_csv, output_folder=custom_models)

                                                                                                                             # ↓TODO
    create_landmarks(name=all_landmarks, input_csv_path=landmarks_csv, output_path=custom_models, landmark_models_path="/tmp/not_used_yet_TODO")



    ## Create .world file

    if op.exists(world_file):
        print("World file found at " + world_file)
        print("Skipping creation, leaving old world file\n")
    else:
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

        include_names = etree.Element("include")
        uri = etree.SubElement(include_names,"uri")
        uri.text = "model://names/all_names"
        world.append(include_names)


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
    parser.add_argument("-t", "--template", type=str, help = "Template folder with correctly named Resources for generation.\n"
                                                            + "Overridden by individual resource arguments like '-l'. Use this to create world with same settings as an old one")
    parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file")
    parser.add_argument("-m", "--heightmap", type=str, help = "Path to heightmap csv file (ERC ver2)")
    parser.add_argument("-r", "--random", action="store_true", help = "Random heightmap and landmarks")
    parser.add_argument("-f", "--force", action="store_true", help = "Force overwrite of generated world")
    args = parser.parse_args()

    # generate model
    create_world(name=args.world, template_dir=args.template, landmarks=args.landmarks, heightmap=args.heightmap, random=args.random, force=args.force)
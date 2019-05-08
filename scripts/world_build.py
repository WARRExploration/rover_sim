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
from argparse import ArgumentParser
import shutil

from rospkg import RosPack

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

from rover_sim.scripts.landmarks.generate_landmarks import create_landmarks
from rover_sim.scripts.generate_terrain import generate_terrain


def world_build(world_path=None, force=False):
    """
    Builds the world from files in the specified folder. The following files should be present:
        'Heightmap.csv':  heightmap csv file (ERC ver2) 
        'Landmarks.csv':  position list of the landmarks
    
    Arguments:
        world_path {str} -- path to the directory where the world will be generated,
                            if empty: use current path of the shell (default: {None})
        force {bool} -- delete old .world file (default: {False})
    """

    if world_path is None:
        base_path = os.getcwd()
    else:
        base_path = op.abspath(world_path)

    custom_models = op.join(base_path, "models")
    backup_models = custom_models + ".backup"

    terran_name = "terrain"
    all_landmarks_name = "all_landmarks"

    world_file = op.join(base_path,"world.world")
    landmarks_csv = op.join(base_path, "Landmarks.csv")
    heightmap_csv = op.join(base_path, "Heightmap.csv")


    if not op.samefile(op.split(base_path)[0], op.join(rover_sim_dir, "worlds")):
        print("The world will be generated at " + base_path)
        if "y" != raw_input("This is not the standard location inside the 'worlds' directory.\n"
                + "Are you sure? Type y to continue\n").lower():
            raise KeyboardInterrupt("Cancelled by user")


    if not op.isdir(base_path):
        print("Creating base directory at " + base_path)
        os.makedirs(base_path)
    
    if os.path.exists(custom_models):
        if not os.path.isdir(custom_models):
            raise ValueError("'models' has to be a directory, found file at " + custom_models)
        else:
            if os.path.exists(backup_models):
                print("Removing old models backup folder at " + backup_models)
                shutil.rmtree(backup_models)
            print("Copying old 'models' folder to backup at " + backup_models)
            os.rename(custom_models, backup_models)
    
    print("Creating new models directory at " + custom_models + "\n")
    os.mkdir(custom_models)


    no_terrain = False
    no_landmarks = False

    if not os.path.exists(heightmap_csv):
        print("Heightmap file not found at " + heightmap_csv)
        print("Building world with default ground plane\n")
        no_terrain = True
    
    if not os.path.exists(landmarks_csv):
        print("Landmarks file not found at " + landmarks_csv)
        print("Building world without landmarks\n")
        no_landmarks = True


    ## Generate the Models from the Resources

    if not no_terrain:
        generate_terrain(name=terran_name, csv_file_path=heightmap_csv, output_folder=custom_models)
    
    if not no_landmarks:                                                                                                         # ↓TODO
        create_landmarks(name=all_landmarks_name, input_csv_path=landmarks_csv, output_path=custom_models, landmark_models_path="/tmp/not_used_yet_TODO")

    try:
        os.rmdir( custom_models )
        print("Removing empty models directory at " + custom_models + "\n")
    except OSError:
        pass
    

    ## Create .world file

    if force:
        if op.exists(world_file):
            print("Removing old world file at " + world_file)
            os.remove(world_file)

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
        if no_terrain:
            uri.text = "model://ground_plane"
        else:
            uri.text = "model://" + terran_name
        world.append(include_terrain)

        if not no_landmarks:
            include_landmarks = etree.Element("include")
            uri = etree.SubElement(include_landmarks,"uri")
            uri.text = "model://" + all_landmarks_name
            world.append(include_landmarks)

        include_names = etree.Element("include")
        uri = etree.SubElement(include_names,"uri")
        uri.text = "model://names/all_names"
        world.append(include_names)


        #print(etree.tostring(tree, pretty_print=True, encoding='utf8', xml_declaration=True))
        tree.write(world_file, pretty_print=True, encoding='utf8', xml_declaration=True)


if __name__ == '__main__':

    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    # parse command line arguments
    parser = ArgumentParser(
        description="Builds the world from files in the specified folder. The following files should be present:\n"
                + "  'Heightmap.csv':  heightmap csv file (ERC ver2)\n"
                + "  'Landmarks.csv':  position list of the landmarks""",
        formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument("world", type=str, help = "Path to the world directory, if empty: use shell working dir" , nargs="?", default=None)
    parser.add_argument("-f", "--force", action="store_true", help = "Force overwrite of old world file")
    args = parser.parse_args()

    # generate model
    world_build(world_path=args.world, force=args.force)
    
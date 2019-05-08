#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper script to pull in various resources required by world_build.py
You can also manually provide the files
"""
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

from rover_sim.scripts.world_build import world_build
from rover_sim.scripts.generate_random_heightmap import create_random_heightmap


def world_create(name, template_dir, landmarks, heightmap, random=False, build=True, force=False):
    """pulls in resources
    
    Arguments:
        name {str} -- name of the generated world in rover_sim/worlds
        template_dir {str} -- template folder with correctly named resources for generation, e.g. another world
        landmarks {str} -- path to landmarks csv file
        heightmap {str} -- path to heightmap csv file (ERC ver2)
        random {bool} -- create a random heightmap custom to world (default: {False})
        build {bool} -- call world_build.py afterwards (default: {True})
        force {bool} -- delete old world file (default: {False})
    """

    base_path = op.join(rover_sim_dir, "worlds", name)

    landmarks_name = "Landmarks.csv"
    heightmap_name = "Heightmap.csv"
    start_yaml_name = "start.yaml"

    landmarks_csv = op.join(base_path, landmarks_name)
    heightmap_csv = op.join(base_path, heightmap_name)
    start_yaml = op.join(base_path, start_yaml_name)


    if not op.isdir(base_path):
        os.makedirs(base_path)


    ## Create or pull in Resources

    if random:
        # need the subprocess call because random_heightmap uses python3
        subprocess.call(["python3", op.join(rover_sim_dir, "scripts", "generate_random_heightmap.py"),
                "--output", heightmap_csv])
    
    #TODO add generate_random_landmarks.py once the script is ready


    if template_dir is not None: 
        template_land = op.join(template_dir, landmarks_name)
        if op.exists(template_land):
            shutil.copyfile(template_land, landmarks_csv)

        template_height = op.join(template_dir, heightmap_name)
        if op.exists(template_height):
            shutil.copyfile(template_height, heightmap_csv)

        template_yaml = op.join(template_dir, start_yaml_name)
        if op.exists(template_yaml):
            shutil.copyfile(template_yaml, start_yaml)


    if landmarks is not None:
        shutil.copyfile(landmarks, landmarks_csv)

    if heightmap is not None:
        shutil.copyfile(heightmap, heightmap_csv)

    
    ## Build using the resources

    if build:
        world_build(base_path, force) 



if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    # parse command line arguments
    parser = ArgumentParser(
        description="Helper script to pull in various resources required by world_build. You can also manually provide the files",
        formatter_class=ArgumentDefaultsHelpFormatter    
    )

    parser.add_argument("-w", "--world", type=str, help = "World name, updates world if already exists", nargs="?", default="Generated")
    parser.add_argument("-t", "--template", type=str, help = "Template folder with correctly named Resources for generation.\n"
                                                            + "Overridden by individual resource arguments like '-l'. Use this to create world with same settings as an old one")
    parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file")
    parser.add_argument("-m", "--heightmap", type=str, help = "Path to heightmap csv file (ERC ver2)")
    parser.add_argument("-r", "--random", action="store_true", help = "Random heightmap and landmarks")
    parser.add_argument("-b", "--build", action="store_false", help = "Call world_build afterwards")
    parser.add_argument("-f", "--force", action="store_true", help = "Force overwrite of old world file")
    args = parser.parse_args()

    # pull in resources
    world_create(name=args.world, template_dir=args.template, landmarks=args.landmarks, 
            heightmap=args.heightmap, random=args.random, build=args.build, force=args.force)

    
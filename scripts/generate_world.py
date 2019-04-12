#!/usr/bin/env python
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

parser = ArgumentParser(description = "Creates world in worlds directory")
parser.add_argument("-w", "--world", type=str, help = "World name, updates world if already exists", nargs="?", default="Generated")
parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file")
parser.add_argument("-m", "--heightmap", type=str, help = "Path to heightmap csv file")
parser.add_argument("-r", "--random", action="store_true", help = "Random heightmap and landmarks")

args = parser.parse_args()
print(args)



dirname = op.dirname(__file__)
base_path = op.join(dirname, op.pardir, "worlds", args.world)
custom_models = op.join(base_path, "models")

world_file = op.join(base_path, "world.world")
landmarks_csv = op.join(base_path, "Landmarks.csv")
heightmap_csv = op.join(base_path, "Heightmap.csv")

terran_path = op.join(custom_models, "terrain")
all_landmarks_path = op.join(custom_models, "all_landmarks")



if not op.isdir(custom_models):
    os.makedirs(custom_models)

if args.landmarks is not None:
    copyfile(args.landmarks, landmarks_csv)

if args.heightmap is not None:
    copyfile(args.heightmap, heightmap_csv)


# Terrain and Landmarks generation
if args.random:
    subprocess.call(["python", op.join(dirname, "generate_random_heightmap.py"),
                "--output", heightmap_csv])


# subprocess.call(["python", op.join(dirname, "generate_terrain.py"),
#                 "--input", heightmap_csv,
#                 "--output", op.join(base_path, "terrain")])

#all_landmarks_model(landmarks_csv, op.join(rover_sim_dir, "models", "landmarks"))
create_landmarks("all_landmarks", landmarks_csv, custom_models, "/tmp/not_used_yet_TODO")


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


'''
# Terrain inclusion
# should probably be its own script
terran = etree.Element("model")
terran.set("name","terrain")
static = etree.SubElement(terran,"static")
static.text = "true"
link = etree.SubElement(terran,"link")
link.set("name","link")

coll = etree.SubElement(link,"collision")
coll.set("name","collision")
c_mesh = etree.SubElement(etree.SubElement(coll,"geometry"),"mesh") # :3
uri = etree.SubElement(c_mesh,"uri")
uri.text = terran_path

vis = etree.SubElement(link,"visual")
vis.set("name","visual")
v_mesh = etree.SubElement(etree.SubElement(vis,"geometry"),"mesh")
uri = etree.SubElement(v_mesh,"uri")
uri.text = terran_path

pose = etree.SubElement(terran,"pose")
pose.text = "0 0 0 0 0 0"
replace_elem("model[@name='terrain']", terran)
'''


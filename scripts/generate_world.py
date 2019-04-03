"""
This script calls all the necessary generation scripts and creates a world folder
from specified provided files. If the world already exists, it replaces 
landmarks and terrain but keeps manual changes to the .world file
"""
from lxml import etree
import os.path as op
import os
import copy
from argparse import ArgumentParser
from shutil import copy2, copyfile
import subprocess

import generate_landmarks


parser = ArgumentParser(description = "Creates world in worlds directory")
parser.add_argument("-w", "--world", type=str, help = "World name, updates world if already exists", nargs="?", default="Generated")
parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file")
parser.add_argument("-m", "--heightmap", type=str, help = "Path to heightmap csv file")
parser.add_argument("-r", "--random", action="store_true", help = "Random heightmap and landmarks")

args = parser.parse_args()
print(args)



dirname = op.dirname(__file__)
base_path = op.join(dirname, op.pardir, "worlds", args.world)
world_file = op.join(base_path, "world.world")
gen_files = op.join(base_path, "generationFiles")

landmarks_csv = op.join(gen_files, "Landmarks.csv")
heightmap_csv = op.join(gen_files, "Heightmap.csv")

# There is still no solution to the relative path issue:
terran_path = "model://rover_sim/worlds/" + args.world + "/terrain/terrain.dae"



if not op.isdir(gen_files):
    os.makedirs(gen_files)

if args.landmarks is not None:
    copyfile(args.landmarks, landmarks_csv)

if args.heightmap is not None:
    copyfile(args.heightmap, heightmap_csv)
    
# .world file
if op.exists(world_file):
    try:
        tree = etree.parse(world_file, etree.XMLParser(remove_blank_text=True))
        root = tree.getroot()
        world = root.find("world")

    except:
        backup_name = world_file + ".backup"
        os.rename(world_file, backup_name)
        print ("World structure corrupted, creating a new world. \nOld file was saved as: \n " + backup_name)
        
if not op.exists(world_file):    
    root = etree.Element('sdf')
    root.set("version", "1.3")
    tree = etree.ElementTree (root)
    world = etree.Element ('world')
    world.set("name", "default")
    root.append(world)


# Terrain generation
if args.random:
    subprocess.call(["python", op.join(dirname, "generate_random_heightmap.py"),
                "--output", heightmap_csv])

 
subprocess.call(["python", op.join(dirname, "generate_terrain.py"),
                "--input", heightmap_csv,
                "--output", op.join(base_path, "terrain")])


# World file

def replace_elem(name, elem):
    old_elem = world.find(name)
    if old_elem is None:
        world.append(elem)
    else:
        old_elem[:] = elem[:]

scene = etree.Element("scene")
grid = etree.SubElement(scene,"grid")
grid.text = "false"
replace_elem("scene", scene)

include_sun = etree.Element("include")
uri = etree.SubElement(include_sun,"uri")
uri.text = "model://sun"
replace_elem("include[1]",include_sun) # finds first <include>


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


# Landmarks
landmarks = generate_landmarks.all_landmarks_model(landmarks_csv)

replace_elem("model[@name='landmarks']", landmarks)







#print(etree.tostring(worl_file, pretty_print=True, encoding='utf8', xml_declaration=True))

tree.write(world_file, pretty_print=True, encoding='utf8', xml_declaration=True)

"""
This script takes locations of the landmarks on the field from a csv file and ads appropriate locations to some gazebo world  
(or creates a world with only landmarks, if a world does not exist)

Todo:
Replace simple boxes with textured collada models

"""
from lxml import etree
import csv
import copy
from argparse import ArgumentParser
from shutil import copyfile

parser = ArgumentParser(description = "Adds landmarks to worlds")
parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file")
parser.add_argument("-w", "--world", type=str, help = "Path to .word file to add landmarks")

args = parser.parse_args()
box_size = 1

# landmarks_path = "../erc2018/Landmarks.csv"
# world_path = "../worlds/erc2019.world"

try:
    tree = etree.parse(args.world)
    root = tree.getroot()
    world = root.find("world")

except:  
    
    new_name = args.world + ".backup"
    copyfile(args.world, new_name)
    print ("World structure corrupted, creating a new world. \nOld file was saved as: \n " + new_name)
    
    
    root = etree.Element('sdf')
    tree = etree.ElementTree (root)
    world = etree.Element ('world')
    root.append(world)
    

finally:
    with open (args.landmarks) as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            model = etree.Element("model")
            model.set("name", row[0])

            pose = etree.Element("pose")
            pose.text = " ".join(row[1:4]) + " 0 0 0"

            static = etree.Element("static")
            static.text = "true"

            link = etree.Element("link")
            link.set("name", "link")

            visual = etree.Element("visual")
            visual.set("name", "visual")
            collision = etree.Element("collision")
            collision.set("name", "collision")

            geometry = etree.Element("geometry")
            box = etree.Element("box")
            size = etree.Element("size")
            size.text = str(box_size) + " " + str(box_size) + " " + str(box_size)

            box.append(size)
            geometry.append(box)
        
            visual.append(geometry)
            collision.append(copy.deepcopy(geometry))

            link.append(visual)
            link.append(collision)
            
            model.append(link)
            
            model.append(pose)
            model.append(static)
            model.append(link)
            world.append(model)

tree.write(args.world, pretty_print=True)

#!/usr/bin/env python
"""
This script takes locations of the landmarks on the field from a csv file and adds textured models at the appropriate locations
to some gazebo sdf model to be <include>ed in a world file
"""
from lxml import etree
import csv
import copy
from argparse import ArgumentParser
from shutil import copyfile

import generate_single_landmark

parser = ArgumentParser(description = "Adds landmarks to worlds")
parser.add_argument("-l", "--landmarks", type=str, help = "Path to landmarks csv file", nargs="?",
        default="../../providedFiles/erc2018/Landmarks.csv")
parser.add_argument("-o", "--output", type=str, help = "Path to .sdf file where the landmarks are inserted", nargs="?",
        default="../../worlds/erc2018_landmarks/model.sdf")

args = parser.parse_args()

# landmarks_path = "../../providedFiles/erc2018/Landmarks.csv"
# output_path = "../../worlds/erc2018_landmarks/model.sdf"


with open (args.landmarks) as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)

    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')

    landmarks = etree.Element('model')
    landmarks.set('name', 'landmarks')
    
    for row in reader:
        i = row[0][1:]

        # (we define the pose in the <include>)
        generate_single_landmark.create_all(int(i), '0 0 0 0 0 0')

        model = etree.Element('model')
        model.set('name', 'L' + i)

        include = etree.Element('include')
        
        uri = etree.Element('uri')
        uri.text = 'model://rover_sim/models/landmarks/L' + row[0][1:]

        pose = etree.Element('pose')
        pose.text = ' '.join(row[1:4]) + ' 0 0 0'

        include.append(uri)
        include.append(pose)
        model.append(include)
        
        landmarks.append(model)


    sdf.append(landmarks)


    tree = etree.ElementTree(sdf)
    print(args.output)
    tree.write(args.output, pretty_print=True, encoding='utf8', xml_declaration=True)
    #print(etree.tostring(args.output, pretty_print=True, encoding='utf8', xml_declaration=True))
    

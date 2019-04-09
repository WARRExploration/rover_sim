#!/usr/bin/env python
from lxml import etree
import csv
import os, sys
from rospkg import RosPack
hash
# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

from rover_sim.scripts.landmarks.generate_single_landmark import create_single_landmark
from rover_sim.scripts.generate_gazebo_model import create_model_config


def create_landmarks_sdf(input_csv_path, output_path):
    """generate the sdf file for the landmarks gazebo model which includes all the models needed in the scene

    Arguments:
        input_csv_path {str} -- path to the csv file which contains the positions of the landmarks
        output_path {str} -- path to the folder where the sdf file should be placed
    """

    landmark_model_relative_path = "models"

    with open (input_csv_path) as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)

        sdf = etree.Element('sdf')
        sdf.set('version', '1.6')

        landmarks = etree.Element('model')
        landmarks.set('name', 'landmarks')
        
        # create landmark model and include it for each landmark in the file
        for row in reader:
            landmark_name = row[0]
            i = row[0][1:]

            # TODO: check if it there is already a model with this name
            # create a single landmark model
            # (we define the pose in the <include>)
            create_single_landmark(landmark_name, int(i), os.path.join(rover_sim_dir, landmark_model_relative_path))

            model = etree.Element('model')
            model.set('name', landmark_name)

            include = etree.Element('include')
            
            uri = etree.Element('uri')
            uri.text = 'model://rover_sim/models/landmarks/' + landmark_name

            pose = etree.Element('pose')
            pose.text = ' '.join(row[1:4]) + ' 0 0 0'

            include.append(uri)
            include.append(pose)
            model.append(include)
            
            landmarks.append(model)


        sdf.append(landmarks)

        tree = etree.ElementTree(sdf)
        tree.write(os.path.join(output_path, 'model.sdf'), pretty_print=True, encoding='utf8', xml_declaration=True)
    
def create_landmarks(name, input_csv_path, output_path):
    """create the landmarks gazebo model which includes all the landmarks specified in the csv file (it will automatically generate those landmarks)
    
    Arguments:
        name {str} -- name of the gazebo model
        input_csv_path {str} -- path to the csv file which contains the positions of the landmarks
        output_path {str} -- path to the folder where the model should be placed
    """


    model_path = os.path.join(output_path, name)

    # create folder
    # check if output folder exists (path to it)
    if os.path.exists(model_path):
        if not os.path.isdir(model_path):
            raise ValueError('There is already a file with this name')
        elif os.listdir(model_path):
            raise ValueError('The folder is not empty')

    # generate it if necessary
    else:
        os.makedirs(model_path)

    # generate config
    create_model_config(name, model_path)

    # generate sdf
    create_landmarks_sdf(input_csv_path, model_path)

if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(
        description = "\
        This script takes locations of the landmarks on the field from a csv file \
            and adds textured models at the appropriate locations to some gazebo sdf model to be <include>ed in a world file",
        formatter_class=ArgumentDefaultsHelpFormatter    
)
    parser.add_argument("input_csv_path", type=str, help = "path to landmarks csv file")
    parser.add_argument("output_path", type=str, help = "path where the gazebo model should be generated")
    parser.add_argument("-n", "--name", type=str, help = "name of the gazebo model", default="landmarks")
    args = parser.parse_args()

    create_landmarks(args.name, args.input_csv_path, args.output_path)
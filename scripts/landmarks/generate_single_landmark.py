#!/usr/bin/env python
import os, sys
from rospkg import RosPack

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

from rover_sim.scripts.landmarks.generate_landmark_texture import create_texture
from rover_sim.scripts.generate_gazebo_model import create_gazebo_model

def create_single_landmark(name, number, output_folder, pose=[0, 0, 0, 0, 0, 0]):
    """generates a full gazebo model for a ERC landmark
    
    Arguments:
        name {str} -- name of the generated model
        number {int} -- number on the landmark
        output_folder {str} -- path where the landmark model should be generated
    
    Keyword Arguments:
        pose {list} -- the pose of the model (default: {[0, 0, 0, 0, 0, 0]})
    """

    font_path = os.path.join(rover_sim_dir, 'resources/landmarks/Roboto-Bold.ttf')
    template_vis = os.path.join(rover_sim_dir, 'resources/landmarks/marker.dae')
    template_col = os.path.join(rover_sim_dir, 'resources/landmarks/marker_coll.dae')
    size = [0.210, 0.210, 0.297]

    temp_texture_path = '/tmp/landmark.png'

    # generate texture
    create_texture(number, temp_texture_path, font_path)

    # generate gazebo model
    #create_gazebo_model(name, os.path.join(output_folder, name), template_path, temp_texture_path, pose, description="Landmark for the ERC")
    create_gazebo_model(
        name=name, 
        output_folder=os.path.join(output_folder, name), 
        template_model_file_path=template_vis, 
        texture_path=temp_texture_path,
        pose=pose, size=size, 
        template_collision_model_file_path=template_col,
        description="Landmark for the ERC"
    )

    # remove temporary texture
    os.remove(temp_texture_path)


if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    # default values
    output_folder = os.path.join(rover_sim_dir, 'models')

    # parse command line arguments
    parser = ArgumentParser(
        description="generates a full gazebo model for a ERC landmark",
        formatter_class=ArgumentDefaultsHelpFormatter    
    )
    parser.add_argument("number", type=int, help="number of the landmark")
    parser.add_argument("-o", "--output", type=str, help="path to the output folder where the model should be generated", default=output_folder)
    parser.add_argument("-p", "--pose", type=float, help="position and rotation of the model", default=[0, 0, 0, 0, 0, 0], nargs=6)
    args = parser.parse_args()

    # generate model
    create_single_landmark('L' + str(args.number), args.number, args.output, args.pose)
#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageFont
import os, sys
from rospkg import RosPack

# import relative to rover_sim
rospack = RosPack()
rover_sim_dir = rospack.get_path('rover_sim')
sys.path.append(os.path.dirname(rover_sim_dir))

from rover_sim.scripts.generate_gazebo_model import create_gazebo_model

def create_name_texture(name, path):

    font_size = 80
    font_path =  os.path.join(rover_sim_dir, 'resources/names/DejaVuSans-Bold.ttf')
    size = (600, 300)

    # base image
    # Gazebo doesn't support transparent textures :(
    img = Image.new('RGBA', size, (255,255,255,255))

    # get a font
    fnt = ImageFont.truetype(font_path, font_size)
    # get a drawing context
    d = ImageDraw.Draw(img)

    # draw a blue frame
    # color from warr logo
    margin = 15
    width = 10
    d.rectangle((margin, margin, size[0]-margin, size[1]-margin), fill=(102,163,215,255))
    d.rectangle(((margin+width), (margin+width), size[0]-(margin+width), size[1]-(margin+width)), fill=(255,255,255,255))
    
    # draw the name
    ts = d.textsize(name, fnt)
    y_correction=0.875 # font not centered vertically
    d.text(( (img.size[0]-ts[0])/2, (img.size[1]-ts[1])/2 * y_correction), name, font=fnt, fill=(0,101,189,255))

    #img.show() 
    img.save(path)
    return



def create_name(name, output_folder, pose=[0, 0, 0, 0, 0, 0]):
    """generates a gazebo model for a name credit
    
    Arguments:
        name {str} -- name which will appear on the generated model
        output_folder {str} -- path to the output folder in which the model will be generated
    
    Keyword Arguments:
        pose {list} -- the pose of the model (default: {[0, 0, 0, 0, 0, 0]})
    """
    temp_texture_path = '/tmp/name.png'
    create_name_texture(name, temp_texture_path)

    create_gazebo_model(
        name=name, 
        output_folder=output_folder, 
        template_mesh_vis=os.path.join(rover_sim_dir, 'resources','names','name_default.dae'), 
        template_texture=temp_texture_path,
        pose=pose,
        template_mesh_col=None,
        description="Name credit",
        static=True, 
        ghost=True
    )

    os.remove(temp_texture_path)



def create_logo(name, output_folder, pose):

    create_gazebo_model(
        name=name, 
        output_folder=output_folder, 
        template_mesh_vis=os.path.join(rover_sim_dir,'resources','names','exp_logo.dae'), 
        template_texture=os.path.join(rover_sim_dir,'resources','names','Exploration_logo.png'),
        pose=pose,
        template_mesh_col=None,
        description="Name credit",
        static=True, 
        ghost=True
    )



if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    # default values
    output_folder = os.path.join(rover_sim_dir, 'models', 'names')

    # parse command line arguments
    parser = ArgumentParser(
        description="generates a full gazebo model for a name credit rectangle",
        formatter_class=ArgumentDefaultsHelpFormatter    
    )
    parser.add_argument("name", type=str, help="the name of the model and on the model texture")
    parser.add_argument("-o", "--output", type=str, help="path to the output folder in which the model will be generated", default=output_folder)
    parser.add_argument("-p", "--pose", type=float, help="position and rotation of the model", default=[0, 0, 0, 0, 0, 0], nargs=6)
    parser.add_argument("-l", "--logo", action="store_true", help = "use the wider than normal logo model and texture")
    args = parser.parse_args()

    # generate model
    if args.logo:
        create_logo(args.name, args.output, args.pose)
    else:
        create_name(args.name, args.output, args.pose)

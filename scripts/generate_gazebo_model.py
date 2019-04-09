#!/usr/bin/env python

from lxml import etree
import os
import numpy as np
from rospkg import RosPack
from shutil import copyfile

def replace_texture_path_on_template(template_file_path, output_file_path, new_texture_relative_path, template_texture_path='texture.png'):
    """replaces the texture path in a mesh file with a new one
    
    Arguments:
        template_file_path {str} -- path to the template mesh file (will be copied)
        output_file_path {str} -- path of the modified copy 
        new_texture_relative_path {str} -- new relative path of the texture relative to the new generated mesh file
    
    Keyword Arguments:
        template_texture_path {str} -- old texture path in the mesh file (default: {'texture.png'})
    """

    # replace texture path
    with open(template_file_path) as f:
        newText=f.read().replace('<init_from>' + template_texture_path + '</init_from>',
                                '<init_from>' + new_texture_relative_path + '</init_from>')

    # write new mesh file
    with open(output_file_path, "w") as f:
        f.write(newText)

def create_model_config(name, output_file_path, description=None):
    """ creates a config file for a gazebo model
    
    Arguments:
        name {str} -- name of the model
        output_file_path {str} -- path of the folder where the config file should be generated
    
    Keyword Arguments:
        description {str} -- optional description of the model (default: {None})
    """

    config = etree.Element('model')

    name_node = etree.Element('name')
    name_node.text = name
    config.append(name_node)

    version = etree.Element('version')
    version.text = '1.0'
    config.append(version)

    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')
    sdf.text = 'model.sdf'
    config.append(sdf)

    # if there is a description add it to the config file
    if description:
        description_node = etree.Element('description')
        description_node.text = description
        config.append(description_node)

    tree = etree.ElementTree(config)
    tree.write(os.path.join(output_file_path, 'model.config'), pretty_print=True, encoding='utf8', xml_declaration=True)


def create_model_sdf(name, model_file_path, output_file_path, pose=[0, 0, 0, 0, 0, 0], size=[1, 1, 1], collision_model_file_path=None):
    """generates the sdf file for a gazebo model (model will be static)
    
    Arguments:
        name {str} -- name of the model
        model_file_path {str} -- path to the model in sdf format (model://...)
        output_file_path {str} -- path of the folder where the sdf file should be generated
    
    Keyword Arguments:
        pose {list} -- static pose of the model (default: {[0, 0, 0, 0, 0, 0]})
        size {list} -- size of the model (default: {[1, 1, 1]})
        collision_model_file_path {str} -- optional path to the collision model in sdf format (default: {None}, the normal model will be used as collision model instead)
    """
    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')

    model = etree.Element('model')
    model.set('name', name)

    pose_node = etree.Element('pose')
    pose_node.text = ' '.join(map(str, pose))

    static = etree.Element('static')
    static.text = 'true'

    link = etree.Element('link')
    link.set('name', 'link')

    # visual
    visual = etree.Element('visual')
    visual.set('name', 'visual')
    visual_geometry = etree.Element('geometry')

    visual_mesh = etree.Element('mesh')
    visual_uri = etree.Element('uri')
    visual_uri.text = model_file_path
    
    visual_scale = etree.Element('scale')
    visual_scale.text = ' '.join(map(str, size))

    visual_mesh.append(visual_uri)
    visual_mesh.append(visual_scale)
    visual_geometry.append(visual_mesh)
    visual.append(visual_geometry)

    # collision
    collision = etree.Element('collision')
    collision.set('name', 'collision')
    collision_geometry = etree.Element('geometry')

    collision_mesh = etree.Element('mesh')
    collision_uri = etree.Element('uri')
    # use the same model for collision if there is no extra collision model
    collision_uri.text = collision_model_file_path if collision_model_file_path else model_file_path
    
    collision_scale = etree.Element('scale')
    collision_scale.text = ' '.join(map(str, size))

    collision_mesh.append(collision_uri)
    collision_mesh.append(collision_scale)
    collision_geometry.append(collision_mesh)
    collision.append(collision_geometry)

    link.append(visual)
    link.append(collision)
    
    model.append(link)
    
    model.append(pose_node)
    model.append(static)
    model.append(link)

    sdf.append(model)

    tree = etree.ElementTree(sdf)
    tree.write(os.path.join(output_file_path, 'model.sdf'), pretty_print=True, encoding='utf8', xml_declaration=True)


def create_gazebo_model(name, output_folder, template_model_file_path, texture_path, pose=[0, 0, 0, 0, 0, 0], size=[1, 1, 1], template_collision_model_file_path=None, description=None):
    """generates a whole static gazebo model for a given mesh with texture
    
    Arguments:
        name {str} -- name of the model
        output_file_path {str} -- path of the generated model (has to be inside the rover_sim package)
        template_model_file_path {str} -- path to the template mesh (will be copied)
        texture_path {str} -- path to the texture (will be copied)
    
    Keyword Arguments:
        pose {list} -- static pose of the model (default: {[0, 0, 0, 0, 0, 0]})
        size {list} -- size of the model (default: {[1, 1, 1]})
        template_collision_model_file_path {[type]} -- path to the template collision mesh (will be copied) (default: {None}, the normal model will be used as collision model insteat)
        description {str} -- optional description of the model (default: {None})
    """

    # check if output folder exists (path to it)
    if os.path.exists(output_folder):
        if not os.path.isdir(output_folder):
            raise ValueError('There is already a file with this name')
        elif os.listdir(output_folder):
            raise ValueError('The folder is not empty')

    # generate it if necessary
    else:
        os.makedirs(output_folder)

    # create subfolder
    os.makedirs(os.path.join(output_folder, 'textures'))
    os.makedirs(os.path.join(output_folder, 'meshes'))

    # copy texture
    _, texture_extension = os.path.splitext(texture_path)
    if not os.path.exists(texture_path):
        raise ValueError('The texture file is missing in the folder ' + texture_path)

    relative_texture_path = 'textures/texture' + texture_extension
    copyfile(texture_path, os.path.join(output_folder, relative_texture_path))


    # replace the texturepath in the template
    replace_texture_path_on_template(
        template_file_path= template_model_file_path,
        output_file_path= os.path.join(output_folder, 'meshes/mesh.dae'),
        new_texture_relative_path= os.path.join('..',relative_texture_path)
    )

    if template_collision_model_file_path:
        replace_texture_path_on_template(
            template_file_path= template_collision_model_file_path,
            output_file_path= os.path.join(output_folder, 'meshes/collision_mesh.dae'),
            new_texture_relative_path= os.path.join('..',relative_texture_path)
        )

    create_model_config(
        name,  
        output_file_path= output_folder,
        description=description
    )

    rospack = RosPack()
    rover_sim_dir = rospack.get_path('rover_sim')
    relative_path = os.path.relpath(output_folder, rover_sim_dir)

    model_file_path = 'model://rover_sim/' + relative_path + '/meshes/mesh.dae'
    collision_model_file_path = 'model://rover_sim/' + relative_path + '/meshes/collision_mesh.dae'

    create_model_sdf(
        name, 
        model_file_path= model_file_path,
        pose= pose,
        size= size,
        output_file_path=output_folder,
        collision_model_file_path=collision_model_file_path
    )

if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    rospack = RosPack()

    # get path of package
    rover_sim_dir = rospack.get_path('rover_sim')
    
    # default values
    output_folder = os.path.join(rover_sim_dir, 'models')

    # parse command line arguments
    parser = ArgumentParser(
        description="generates a whole static gazebo model for a given mesh with texture",
        formatter_class=ArgumentDefaultsHelpFormatter    
    )
    parser.add_argument("name", type=str, help="name of the gazebo model file")
    parser.add_argument("template", type=str, help="path to the mesh template")
    parser.add_argument("texture", type=str, help="path to the texture which should be mapped on the mesh (texture will be copied)")
    parser.add_argument("-c", "--collision", type=str, help="path to the collisin mesh template")
    parser.add_argument("-o", "--output", type=str, help="path to the folder where the model should be generated, the path will be created", default=output_folder)
    parser.add_argument("-p", "--pose", type=float, help="path to the folder where the model should be generated, the path will be created", default=[0, 0, 0, 0, 0, 0], nargs=6)
    parser.add_argument("-s", "--size", type=str, help="path to the folder where the model should be generated, the path will be created", default=[1, 1, 1], nargs=3)
    parser.add_argument("-d", "--description", type=str, help="small description of the model")
    args = parser.parse_args()

    # generate model
    create_gazebo_model(
        args.name, 
        os.path.join(args.output, args.name), 
        args.template,
        args.texture,
        args.pose,
        args.size,
        args.collision,
        args.description
    )
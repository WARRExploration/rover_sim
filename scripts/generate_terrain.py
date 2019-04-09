#!/usr/bin/env python

from collada import *
import numpy as np
import os
from rospkg import RosPack
from shutil import copyfile


def id(x, y, number_of_rows):
    """Used to index a 1d-array with 2 indices

    Arguments:
        x {int} -- x value
        y {int} -- y value
        number_of_rows {int} -- number of rows in the array

    Returns:
        int -- 1d index
    """

    return x * number_of_rows + y


def get_coordinates_from_csv(csv_file_path):
    """This function extracts the coordinates from a csv file based on the provided files of the ERC

    Arguments:
        csv_file_path {str} -- path to the ERC csv file (ver2)

    Returns:
        [[[]]] -- 2d array of 3d coordinates
    """

    # read context informations from *.csv file
    with open(csv_file_path) as fp:
        for i, line in enumerate(fp):
            if i != 1:
                continue

            # we are only interested in the spacing
            _, _, spacing_y, spacing_x, _, _ = np.fromstring(
                line, dtype=float, sep=' ')
            break

    # load heights from *.csv file
    data = np.loadtxt(open(csv_file_path), delimiter=',', skiprows=2)

    # flip the matrix around the x-axis to be able to index it the right way
    data = np.moveaxis(np.flip(data, 0), 0, -1)

    # get dimensions of the matrix
    number_of_cols, number_of_rows = data.shape

    # x-Axis
    # generate vector
    xs = np.mgrid[:number_of_cols] * spacing_x
    # generate grid from vector
    xs = np.stack((xs,) * number_of_rows, axis=-1)

    # y-Axis
    # generate vector
    ys = np.mgrid[:number_of_rows] * spacing_y
    # generate grid from vector
    ys = np.stack((ys,) * number_of_cols, axis=0)

    # coordinates
    coords = np.stack((xs, ys, data), axis=2)

    return coords


def generate_vertex_array(coords):
    """generate the vertex array out of the coordinates

    Arguments:
        coords {[[[]]]} -- 2d array of 3d coordinates

    Returns:
        [] -- linear array of vertecies
    """

    return coords.flatten()


def generate_normal_array(coords):
    """generate the normal array out of the coordinates

    Arguments:
        coords {[[[]]]} -- 2d array of 3d coordinates

    Returns:
        [] -- linear array of normals
    """

    number_of_cols, number_of_rows, _ = coords.shape

    normal_floats = []
    for x in range(number_of_cols):
        for y in range(number_of_rows):
            # edge cases (normal points up)
            if x == 0 or x == number_of_cols - 1 or y == 0 or y == number_of_rows - 1:
                normal_floats.append([0, 0, 1])
                continue

            # calculate normal to gradient
            current_normal = np.cross(coords[x+1, y]-coords[x-1, y],
                                      coords[x, y+1]-coords[x, y-1])

            # normalize normal
            current_normal /= np.linalg.norm(current_normal)
            normal_floats.append(current_normal)

    normal_floats = np.array(normal_floats)

    return normal_floats


def generate_uv_array(coords):
    """generate the uv coordinate array out of the coordinates

    Arguments:
        coords {[[[]]]} -- 2d array of 3d coordinates

    Returns:
        [] -- linear array of uv coordinates
    """

    # get width and height of the terrain of the last element
    width, height, _ = coords[-1, -1]

    # extract x and y from the coords
    x, y, _ = np.split(coords, 3, axis=2)
    x = np.squeeze(x)
    y = np.squeeze(y)

    # normalize all the values
    x /= width
    y /= height

    # recombine x and y
    uv_coords = np.stack((x, y), axis=2)

    return uv_coords.flatten()


def generate_index_array(coords):
    """generate the index array for a simple 2d mesh

    Arguments:
        coords {[[[]]]} -- 2d array of 3d coordinates

    Returns:
        [] -- linear array of uv indices
    """

    number_of_cols, number_of_rows, _ = coords.shape

    indices = []
    # iterate over grid (ignore last row and col)
    for x in range(number_of_cols-1):
        for y in range(number_of_rows-1):
            # 1. triangle
            indices.append([
                id(x, y, number_of_rows),
                id(x+1, y, number_of_rows),
                id(x, y+1, number_of_rows)
            ])
            # 2. triangle
            indices.append([
                id(x+1, y+1, number_of_rows),
                id(x, y+1, number_of_rows),
                id(x+1, y, number_of_rows)
            ])

    indices = np.array(indices)

    return indices


def generate_collada(coords, relative_texture_path):
    """generate the pycollada mesh out of the coordinates array

    Arguments:
        coords {[[[]]]} -- 2d array of 3d coordinates
        relative_texture_path {str} -- relative path to the texture, relative to the generated collada file

    Returns:
        Collada -- final collada mesh
    """

    # create the mesh
    mesh = Collada()

    # create source arrays
    vert_src = source.FloatSource(
        'verts-array', generate_vertex_array(coords), ('X', 'Y', 'Z'))
    normal_src = source.FloatSource(
        'normals-array', generate_normal_array(coords), ('X', 'Y', 'Z'))
    uv_src = source.FloatSource(
        'uv-array', generate_uv_array(coords), ('S', 'T'))

    # create geometry and add the sources
    geom = geometry.Geometry(mesh, 'geometry', 'terrain', [
        vert_src, normal_src, uv_src])

    # define inputs to triangle set
    input_list = source.InputList()
    input_list.addInput(0, 'VERTEX', '#verts-array')
    input_list.addInput(1, 'NORMAL', '#normals-array')
    input_list.addInput(2, 'TEXCOORD', '#uv-array', set='0')

    # create index array
    indices = generate_index_array(coords)
    # repeat each of the entries for vertex, normal, uv
    indices = np.repeat(indices, 3)

    # create triangle set, add it to list of geometries in the mesh
    triset = geom.createTriangleSet(indices, input_list, 'material')
    geom.primitives.append(triset)
    mesh.geometries.append(geom)

    # add a material
    image = material.CImage('material-image', relative_texture_path)
    surface = material.Surface('material-image-surface', image)
    sampler2d = material.Sampler2D('material-image-sampler', surface)
    material_map = material.Map(sampler2d, 'UVSET0')

    effect = material.Effect('material-effect', [surface, sampler2d], 'lambert', emission=(0.0, 0.0, 0.0, 1),
                             ambient=(0.0, 0.0, 0.0, 1),  diffuse=material_map, transparent=material_map, transparency=0.0, double_sided=True)

    mat = material.Material('materialID', 'material', effect)
    mesh.effects.append(effect)
    mesh.materials.append(mat)
    mesh.images.append(image)

    # instantiate geometry into a scene node
    matnode = scene.MaterialNode('material', mat, inputs=[])
    geomnode = scene.GeometryNode(geom, [matnode])
    node = scene.Node('model', children=[geomnode])

    # create scene
    myscene = scene.Scene('scene', [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    return mesh


def generate_terrain(csv_file_path, output_folder, terrain_name):
    """generate the texure and the mesh of a ERC terrain in a specified folder

    Arguments:
        csv_file_path {str} -- path to the ERC csv file (ver2)
        output_folder {str} -- path to the folder where the files should be generated, the path will be created, folder has to be empty
        terrain_name {str} -- name of the terrain collada file
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

    # read coordinates
    coords = get_coordinates_from_csv(csv_file_path)

    # TODO: generate texture (currently only copy of resources)
    rospack = RosPack()
    rover_sim_dir = rospack.get_path('rover_sim')
    texture_path = os.path.join(rover_sim_dir, 'resources/terrain/sand_texture.png')
    _, extension = os.path.splitext(texture_path)
    if not os.path.exists(texture_path):
        raise ValueError('The texture file is missing in the folder ' + texture_path)

    relative_texture_path = 'texture' + extension
    copyfile(texture_path, os.path.join(output_folder, relative_texture_path))

    # generate mesh
    mesh = generate_collada(coords, relative_texture_path)
    # save collada to file
    mesh.write(os.path.join(output_folder, terrain_name + '.dae'))


if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    rospack = RosPack()

    # get path of package
    rover_sim_dir = rospack.get_path('rover_sim')
    
    # default values
    output_folder = os.path.join(rover_sim_dir, 'models/terrain')
    terrain_name = 'terrain'

    # parse command line arguments
    parser = ArgumentParser(
        description="generate the texure and the mesh of a ERC terrain in a specified folder",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input", type=str, help="path to the ERC csv file (ver2)")
    parser.add_argument("-o", "--output", type=str, help="path to the folder where the files should be generated, the path will be created", default=output_folder)
    parser.add_argument("-n", "--name", type=str, help="name of the terrain collada file", default=terrain_name)
    args = parser.parse_args()

    # generate terrain
    generate_terrain(args.input, args.output, args.name)
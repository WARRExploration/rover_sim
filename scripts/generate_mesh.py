#!/usr/bin/env python

from collada import *
import numpy as np
import os

dirname = os.path.dirname(__file__)

# load heights from *.csv file
path = os.path.join(dirname, "../providedFiles/erc2018/DTM_ver2.csv")
data = np.loadtxt(open(path, "rb"), delimiter=",", skiprows=2)
data = np.moveaxis(np.flip(data, 0), 0, -1)
cols, rows = data.shape

# small helper function
def id(x, y):
    return x * rows + y

# read further information
with open(path) as fp:
   for i, line in enumerate(fp):
       if i == 1:
           _, _, sr, sc, _, _ = list(map(float,line.strip().split(" ")))
           break

# x-Axis
xs = np.mgrid[:cols] * sc
xs = np.stack((xs,)*rows, axis = -1)

# y-Axis
ys = np.mgrid[:rows] * sr
ys = np.stack((ys,)*cols, axis=0)

# coordinates
coords = np.stack((xs, ys, data), axis=2)

# create the mesh
mesh = Collada()

# add a material
path = "../textures/sand_texture.png"
image = material.CImage("material_1-image", path)
surface = material.Surface("material_1-image-surface", image)
sampler2d = material.Sampler2D("material_1-image-sampler", surface)
map1 = material.Map(sampler2d, "UVSET0")

# effect0 = material.Effect("material_0-effect", [], "lambert", emission=(0.0, 0.0, 0.0, 1),\
#                      ambient=(0.0, 0.0, 0.0, 1), diffuse=(0.890196, 0.882353, 0.870588, 1),\
#                      transparent=(1, 1, 1, 1), transparency=1.0, double_sided=True)
effect1 = material.Effect("material_1-effect", [surface, sampler2d], "lambert", emission=(0.0, 0.0, 0.0, 1),\
                     ambient=(0.0, 0.0, 0.0, 1),  diffuse=map1, transparent=map1, transparency=0.0, double_sided=True)

# mat0 = material.Material("material_0ID", "material_0", effect0)
mat1 = material.Material("material_1ID", "material_1", effect1)

# mesh.effects.append(effect0)
mesh.effects.append(effect1)

# mesh.materials.append(mat0)
mesh.materials.append(mat1)

mesh.images.append(image)

# create source arrays
vert_floats = coords.flatten()

normal_floats = []
for x in range(cols):
    for y in range(rows):
        if x == 0 or x == cols-1 or y == 0 or y == rows-1:
            normal_floats.append([0,0,1])
            continue
        tmp = np.cross(coords[x+1,y]-coords[x-1,y],coords[x,y+1]-coords[x,y-1])
        tmp = tmp / np.linalg.norm(tmp)
        normal_floats.append(tmp)

xs /= (cols-1) * sc
ys /= (rows-1) * sr
uv_coords = np.stack((xs, ys), axis=2)
uv_floats = uv_coords.flatten()

vert_src = source.FloatSource("cubeverts-array", np.array(vert_floats), ('X', 'Y', 'Z'))
normal_src = source.FloatSource("cubenormals-array", np.array(normal_floats), ('X', 'Y', 'Z'))
uv_src = source.FloatSource("cubeuv-array", np.array(uv_floats), ('S', 'T'))

# create geometry and add the sources
geom = geometry.Geometry(mesh, "geometry", "mycube", [vert_src, normal_src, uv_src])

# define inputs to triangle set
input_list = source.InputList()
input_list.addInput(0, 'VERTEX', "#cubeverts-array")
input_list.addInput(1, 'NORMAL', "#cubenormals-array")
input_list.addInput(2, 'TEXCOORD', "#cubeuv-array", set="0")

# create index array
indices = []
for x in range(cols-1):
    for y in range(rows-1):
        indices.append([id(x, y), id(x+1, y), id(x, y+1)])
        indices.append([id(x+1, y+1), id(x, y+1), id(x+1, y)])
indices = np.array(indices).flatten()
indices = np.stack((indices,indices,indices), axis=1).flatten()

# create triangle set, add it to list of geometries in the mesh
# triset0 = geom.createTriangleSet(indices, input_list, "material_0")
triset1 = geom.createTriangleSet(indices, input_list, "material_1")
# geom.primitives.append(triset0)
geom.primitives.append(triset1)
mesh.geometries.append(geom)

# instantiate geometry into a scene node
# matnode0 = scene.MaterialNode("material_0", mat0, inputs=[])
matnode1 = scene.MaterialNode("material_1", mat1, inputs=[])
# geomnode = scene.GeometryNode(geom, [matnode0, matnode1])
geomnode = scene.GeometryNode(geom, [matnode1])
node = scene.Node("Model", children=[geomnode])

# create scene
myscene = scene.Scene("myscene", [node])
mesh.scenes.append(myscene)
mesh.scene = myscene

#save document to file
path = os.path.join(dirname, "../models/terrain.dae")
mesh.write(path)
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

# add a material
mesh = Collada()
effect = material.Effect("effect0", [], "phong", emission=(0.2,0,0,1.0), diffuse=(0,1.0,0,1.0), specular=(1.0,1.0,1.0,1.0))
mat = material.Material("material0", "mymaterial", effect)
mesh.effects.append(effect)
mesh.materials.append(mat)

# create source arrays
'''
vert_floats = [-50,50,50,50,50,50,-50,-50,50,50,
    -50,50,-50,50,-50,50,50,-50,-50,-50,-50,50,-50,-50]
normal_floats = [0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,
    0,1,0,0,1,0,0,1,0,0,-1,0,0,-1,0,0,-1,0,0,-1,0,-1,0,0,
    -1,0,0,-1,0,0,-1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,-1,
    0,0,-1,0,0,-1,0,0,-1]
'''
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

vert_src = source.FloatSource("cubeverts-array", np.array(vert_floats), ('X', 'Y', 'Z'))
normal_src = source.FloatSource("cubenormals-array", np.array(normal_floats), ('X', 'Y', 'Z'))

# create geometry and add the sources
geom = geometry.Geometry(mesh, "geometry0", "mycube", [vert_src, normal_src])

# define inputs to triangle set
input_list = source.InputList()
input_list.addInput(0, 'VERTEX', "#cubeverts-array")
input_list.addInput(1, 'NORMAL', "#cubenormals-array")

# create index array
'''
indices = numpy.array([0,0,2,1,3,2,0,0,3,2,1,3,0,4,1,5,5,6,0,
    4,5,6,4,7,6,8,7,9,3,10,6,8,3,10,2,11,0,12,
    4,13,6,14,0,12,6,14,2,15,3,16,7,17,5,18,3,
    16,5,18,1,19,5,20,7,21,6,22,5,20,6,22,4,23])
'''
indices = []
for x in range(cols-1):
    for y in range(rows-1):
        indices.append([id(x, y), id(x+1, y), id(x, y+1)])
        indices.append([id(x+1, y+1), id(x, y+1), id(x+1, y)])
indices = np.array(indices).flatten()
indices = np.stack((indices,indices), axis=1).flatten()

# create triangle set, add it to list of geometries in the mesh
triset = geom.createTriangleSet(indices, input_list, "materialref")
geom.primitives.append(triset)
mesh.geometries.append(geom)

# instantiate geometry into a scene node
matnode = scene.MaterialNode("materialref", mat, inputs=[])
geomnode = scene.GeometryNode(geom, [matnode])
node = scene.Node("node0", children=[geomnode])

# create scene
myscene = scene.Scene("myscene", [node])
mesh.scenes.append(myscene)
mesh.scene = myscene

#save document to file
path = os.path.join(dirname, "../models/terrain.dae")
mesh.write(path)
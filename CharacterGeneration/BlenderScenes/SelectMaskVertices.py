import bpy

import os
import json

from deeva import DEEVA_DATA_DIR

mesh_obj = bpy.context.active_object
assert mesh_obj.type == 'MESH'


mesh = mesh_obj.data  # type: bpy.types.Mesh

with open(os.path.join(DEEVA_DATA_DIR, "face_mask_vertices.json"), "r") as vertex_list_file:
    vertices = json.load(vertex_list_file)

print("Loaded {} vertices".format(len(vertices)))

#
# (Un)select everything
for v in mesh.vertices:  # type: bpy.types.MeshVertex
    if v.index in vertices:
        v.select = True
    else:
        v.select = False


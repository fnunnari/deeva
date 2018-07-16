import bpy

mesh_obj = bpy.context.active_object
assert mesh_obj.type == 'MESH'

mesh = mesh_obj.data

selected_vertex_list = []

for v in mesh.vertices:
    if v.select:
        selected_vertex_list.append(v.index)

print("Indices of selected vertices ({}):".format(len(selected_vertex_list)))
print(selected_vertex_list)

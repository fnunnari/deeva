""" Bpy script to export the physical attributes from the ManuelBastioniLAB 

1. Initialiaze a 'Caucasian Female' (F_CA01) in ManuelBastioniLAB
2. Run this script, check console for progress and errors
3. A csv file called mbastauto.csv will be created in your home folder
"""

# extract all attributes
import bpy

import inspect
import csv
import os


def export_mblab_attributes(mesh_obj:bpy.types.Object, outfilepath: str) -> None:

    #
    # List attributes
    print("Start gathering attributes...")

    attributes = []

    # Filter for float only attributes
    for attr in inspect.getmembers(mesh_obj, lambda a: isinstance(a, float)):
        attribute_name = attr[0]  # type: str
        # filter for uppercase only attributes
        if attribute_name[0].isupper():
            # print(attr[0])
            if not attribute_name.startswith("Expressions_"):
                attributes.append({'name': attr[0], 'type': 'nc'})  # 'nc' stands for 'numerical continuous'

    print("Found {} attributes.".format(len(attributes)))

    print("Writing csv file '{}'...".format(outfilepath))

    #
    # Write attribute list to a file

    # Useful paths
    scene_path = bpy.data.filepath
    scene_dir, scene_file = os.path.split(scene_path)
    attributes_out_filename = os.path.join(scene_dir, outfilepath)

    print("Writing attributes to file '{}'...".format(attributes_out_filename))

    with open(attributes_out_filename, 'w') as csvfile:
        fieldnames = ['name', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for attribute in attributes:
            writer.writerow(attribute)

    print("Finished.")


#
# MAIN
#

if __name__ == "__main__":
    scene = bpy.context.scene

    mesh_obj = bpy.context.active_object  # type: bpy.types.Object
    assert isinstance(mesh_obj, bpy.types.Object)
    assert mesh_obj.type == 'MESH'

    arm_obj = mesh_obj.parent  # bpy.types.Object
    assert isinstance(arm_obj, bpy.types.Object)
    assert arm_obj.type == 'ARMATURE'

    export_mblab_attributes(mesh_obj=mesh_obj, outfilepath="mblab_attributes.csv")

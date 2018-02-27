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


#
# Get reference to character mesh
print("Taking reference to MBLab Mesh...")

MHHuman = bpy.data.objects['f_ca01']
assert MHHuman is not None
assert MHHuman.type == 'MESH'

#
# List attributes
print("Start gathering attributes...")

attributes = []

# Filter for float only attributes
for attr in inspect.getmembers(MHHuman, lambda a: isinstance(a, float)):
    # filter for uppercase only attributes
    if attr[0][0].isupper():
        # print(attr[0])
        attributes.append({'name': attr[0], 'type': 'nc'})  # 'nc' stands for 'numerical continuous'

print("Finished. Found {}!".format(len(attributes)))
print("Writing csv file...", end='')     
        

#
# Write attribute list to a file

# Useful paths
scene_path = bpy.data.filepath
scene_dir, scene_file = os.path.split(scene_path)
attributes_out_filename = os.path.join(scene_dir, 'mbast_attributes.csv')

print("Writing attributes to file '{}'...".format(attributes_out_filename))

with open(attributes_out_filename, 'w') as csvfile:
    fieldnames = ['name', 'type']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for attribute in attributes:
        writer.writerow(attribute)
        
        
print("Finished. File written to {} !".format(attributes_out_filename))

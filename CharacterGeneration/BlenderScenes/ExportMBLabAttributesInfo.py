""" Bpy script to export the physical attributes from the ManuelBastioniLAB 

1. initialiaze a 'human_female_base01' in ManuelBastioniLAB
2. run this script, check console for progress and errors
3. a csv file called mbastauto.csv will be created in your home folder
"""
print("Start gathering attributes...", end='')

#extract all attributes
import bpy, inspect

MHHuman = bpy.data.objects['human_female_base01']

attributes = [] 

#filter for float only attributesl
for attr in inspect.getmembers(MHHuman, lambda a:isinstance(a, float)):
    #filter for uppercase only attributes
    if attr[0][0].isupper():
        #print(attr[0])
        attributes.append({'name':attr[0], 'type':'nc'})

print("Finished. Found {}!".format(len(attributes)))
print("Writing csv file...", end='')     
        
#write attributes to a file    
import csv, os

abspath = os.path.expanduser('~/mbastauto.csv')

with open(abspath, 'w') as csvfile:
    fieldnames = ['name', 'type']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for attribute in attributes:
        writer.writerow(attribute)
        
        
print("Finished. File written to {} !".format(abspath))   
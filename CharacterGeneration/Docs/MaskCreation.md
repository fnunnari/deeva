
# How to create the face mask for the MBLab characters.

The mask is needed to cover the head except the face.
It is needed to run experiments where the hair, the shape of the head and
the ears do play a role in the perception of the personality of the character.

## Mask as polygon color

Strategy:
 * Select all the vertices of the mask
 * Export the vertex list as an array into a json file
   - Use script PrintSelectedVertices.py
 * Create an operator to apply the mask:
   - Create a new material as dull black
   - load back the list of vertices of the mask
   - For each polygon of the body
     - if all the vertices of the polygon are in the list of vertices,
     - then set the material of the polygon to black.



## Mask as Proxy

This is the procedure I used to create a mask as an object which can be applied as proxy to MBLab characters.
Unfortunately, this can not be used if we want to mask the face of characters before finalization.

Strategy: Create a mask starting from the original head model and use it as proxy
to cover the head of any shape.
Set it to a black material and use black background.

 * Start from a geometry of the standard body
 * Duplicate it
 * Remove all shape keys
 * Remove Armature modifier
 * Apply all other modifiers
 * Unparent from original armature
 * Keep only the head vertices
 * Delete eyes
 * Delete the tongue
 * Make a vertex group with the contour you want to Hide
 * hide the vertices and easily select all vertices of the face
 * make a group for all face vertices
 * Select all head vertices and put cursor to selection.
 * Scale a bit the mesh to increase size
 * Make a mask to hide the vertices that you want to see through (face)

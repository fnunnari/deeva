# Procedural authoring of Characters with ManuelbBastioniLab

[ManuelBastioniLAB](http://www.manuelbastioni.com/) is a great Blender addon, with full dedicated GUI, for the procedural generation of virtual characters.

However, in its original version, it is impossible to alter the character appearance via Python scripting.

This patch allows people to edit a ManualeBastioniLAB character using scripted code instead of direct GUI manipulation.


## Releases

The patch doesn't come as pre-packed zip. It is a _.diff_ file that you must apply using a _patch_ tool (it is a default command-line utility on Mac and Linux).

* `ManuelBastioniLab-1_4_0-FalseTimePatch-171006.diff` applies to versions 1.4, 1.4a, 1.5.
* `ManuelBastioniLab-1_6_1-FalseTimePatch-180227.diff` applies to version 1.6.1. (Untested on 1.6.0)


## How to patch a vanilla version of ManuelBastioniLAB

* Download and install the ManuelBastioniLAB add-on from its official website;
* Open a console/terminal
* CD to the directory `manuelbastionilab`, probably in your Blender's addons directory;
* Apply the patch with command `patch`. E.g.:

```
> cd path/to/BlenderScripts/addons/manuelbastionilab
> patch -p1 < path/to/ManuelBastioniLab-1_4_0-FalseTimePatch-171006.diff
```

Expected output looks like (sample from v1.5):

```
patching file __init__.py
Hunk #1 succeeded at 214 (offset -23 lines).
Hunk #2 succeeded at 1515 with fuzz 1 (offset -7 lines).
patching file humanoid.py
Hunk #1 succeeded at 795 (offset -5 lines).
```


## Usage

* Select the Mesh of the ManualBastioniLab character (the child of the armature);
* Update the attribute(s) you like;
* Invoke the `refresh.character` operator to apply the changes to the geometry.

For example, in the Blender interactive Python console:

```
>>> ao = bpy.context.active_object
>>> ao.type
'MESH'
>>> ao.Hands_Lenght = 1.0
>>> ao['Hands_Size'] = 0.0
>>> bpy.ops.refresh.character()
falsetime_update
{'FINISHED'}
```

... and you will see that your character mesh updates.


## How to create the patch

This section is for developers who want to fix/enhance the patch and release a new diff file.

We assume that the original MBLab addon stays in a dedicated folder and that your working/development version stays in a Blender `addons` directory. They both contain a directory named `manuelbastionilab`

* CD to your working `addons` folder;
* Compute the `diff`.

```
cd path/to/workingdir/BlenderScripts/addons/
diff -rup path/to/original_vanilla/manuelbastionilab/ manuelbastionilab/ > ManuelBastioniLab-FalseTimePatch-yymmdd.diff
```

Where diff options mean:

```
r: recursive
u: output 3 lines of unified context
p: show the name of the function containing the changes
```

# Deeva - Character Generator #

This project is part of the DeEvA project and consists of a set of packages
and scripts to procedurally generate pictures of virtual characters.

The generator is based of the [ManuelBastioniLAB](http://www.manuelbastioni.com/).


# Installation

## MBLab

Download and install the ManuelBastioniLab add-on.
E.g.: [MBLab v1.6.1a](http://www.manuelbastioni.com/download/manuelbastionilab_161a.zip)

```
cd BlenderScripts/addons
unzip .../manuelbastionilab_161a.zip
```

## PIP and Python packages

The Python installation embedded in Blender must be enhanced with additional libraries.
Install pip in the Python interpreter embedded in Blender.

From a Terminal:
```
cd path/to/BlenderScenes
../BlenderExe/blender.app/Contents/Resources/2.79/python/bin/python3.5m ../../Downloads/get-pip.py
```

(Do not even think of doing it from within the Blender console. It would just corrupt your Blender installation.)

Setup the required python packages using the list provided in the `BlenderScene/` directory
```
../BlenderExe/blender.app/Contents/Resources/2.79/python/bin/pip install -r python_packages.txt
```

## Enable add-ons

Start Blender with the script in `BlenderScenes`.

On Mac, from a Terminal
```
cd path/to/BlenderScenes
sh _LaunchBlenderMac.command
```

or on Windows, from a DOS prompt

```
cd path/to/BlenderScenes
_LaunchBlenderWin.bat
```

From `File -> User preferences ... -> Add-ons`
locate and activate:

* `Characters: ManuelbastioniLAB`
* `Characters: Deeva`
* `Save user Settings`

# With whom do I talk to? #

Fabrizio Nunnari
<fabrizio.nunnari@dfki.de>
<fab.nunnari@gmail.com>

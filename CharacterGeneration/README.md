# BlenderProjectSkeleton #

Scripts and guidelines to help in the development of multiple Blender scripts and add-ons.

## What is this repository for? ##

This is a template to organize the structure of projects aiming at the development of Blender code using an external code editor like PyCharm.
It helps developers working simultaneously on several projects using different add-ons (or different versions of the same add-on) and different versions of Blender.

Essentially, this project consists of a structured directory tree and a collection of scripts.
After setting up your new project, run Blender using the provided _LaunchBlender_ scripts and enjoy a non-interfering multiple-projects development.

This template accommodates developers' need, such as:

* Dealing with different versions of Blender on the same machine;
* Configuring different user settings for each project;
* Managing different (maybe incompatible) versions of the same add-on;
* Developing add-ons using external editors;
  - Support for Blender namespaces (`bpy`, `mathutils`, ...) in static code analysis;
  - Support debugging;
* Storing temporary files in a controlled directory.

Advantages:

* Flawlessly use a specific version of Blender for each project;
* The add-ons that you develop for a project will not collide with other installations;
* All your Blender user settings will be local to the project, including the list of enabled add-ons and the list of recently opened scenes.

Disadvantages:

* A different copy of the Blender executable for each project (Disk space consuming).


## How to get it / Download / Clone ##
Get the project from:

* [BlenderProjectSkeleton](https://bitbucket.org/fnunnari/blenderprojectskeleton/)  at BitButcket.


## Setup ##

* Create a new empty directory that will be the root of your new project.
* Copy all the 5 directories whose name starts with BlenderXXX in the new project directory:
  * BlenderProjectSkeleton/
    * BlenderConfig/
    * BlenderExe/
    * BlenderScenes/
      * \_LaunchBlenderMac.command
      * \_LaunchBlenderWin.bat
    * BlenderScripts/
      * add-ons/
    * BlenderTemp/
* Configure PyCharm:
  - Set the root of a new IDE to the root directory
  - If you want to develop an add-on, right click on directory `BlenderScripts/addons` and `Mark Directory as --> Sources Root`
* Configure Blender:
  - Make a copy of your Blender editor in the BlenderExe directory
    - For Mac, copy the Blender.app directory inside BlenderExe
    - For Windows, copy the whole content of the directory containing the blender.exe
  - Launch you local blender instance by double clicking on the provided _Launch_ scripts for your architecture. The scripts are in the `BlenderScenes`:
    - On Mac: \_LaunchBlenderMac.command
    - On Windows: \_LaunchBlenderWin.bat
* If you develop a Blender add-on:
  - Create the new add-on file (e.g. _myaddon.py_), or module,  in the `BlenderScripts/addons/` directory.
  - Launch Blender and load it:
    - File -> User Preferences... -> tab _Add-ons_ ->
    - Look for your _myaddon_ in the list and enable it.


## How to use it ##

* Put all the blender scenes (`.blend`) in the `BlenderScenes/` directory
* If you develop stand-alone scripts:
  - Place the scripts (`.py`) in the same BlenderScene directory
  - Load the scripts in the blender scenes
  - Edit the script with your favorite editor (e.g. PyCharm)
  - reload the script in the blender scene after modification
* If you work on an add-on:
  - Place the add-on file, or module in the `BlenderScripts/addons` directory
  - see the following section on how to reload the code the you modified externally.


## How to expose the Blender namespaces to PyCharm ##

This section explains how to see and used the Blander namespaces (bpy, mathutils) in the PyCharm editor.

This instructions are an adaptation of the [pycharm-blender](https://github.com/mutantbob/pycharm-blender) project documentation.

### Configure the python interpreter ###

Your PyCharm project must use the same python interpreter contained in your local Blender copy.

PyCharm Menu —> Preferences -> Project: … -> Project Interpreter -> “gear” icon -> Add local -> select the python executable in your blender editor (e.g.: `path/to/project/BlenderExe/blender.app/Contents/Resources/2.78/python/bin/python3.5m`)


### Generate Blender namespace stubs ###

This archive comes with some pre-computed stubs for several Blender versions.

If you need to create stubs for a new Blender version, go on with the following instructions.

1. Locate the executable of the Blender version for which you want to create the namespace, e.g.,

   `path/to/project/BlenderExe/blender.app/Contents/MacOS/blender`

2. Open a terminal and `cd` to the `PyCharm-Blender` directory, containing the `python_api` directory.

   `cd path/to/project/PyCharm-Blender/`

3. From the Terminal, launch the Blender exe with the option to execute the generation script:

   `path/to/project/BlenderExe/blender.app/Contents/MacOS/blender -b -P python_api/pypredef_gen.py`

4. This will create a directory named `python_api/pypredef/`

5. Rename the newly generated API, e.g.:

   `mv python_api/pypredef python_api/pypredef-2.79`

### Configure the PyCharm to use the Blender namespace stubs ###

You must include the newly generated stubs in the search path of your python interpreter.

PyCharm Menu -> Preferences... -> Project: ... -> Project Interpreter -> Project Interpreter x.y.z <path> Gear -> more... -> (bottom icon) Show paths for current interpreter -> (icon +) Add -> Select e.g. path/to/PyCharm-Blender/python_api/pypredef-2.79


## How to debug Blender code in PyCharm ##

It is possible to debug the execution of an add-on inside the PyCharm IDE. For it, you need a Professional version of PyCharm (you need the pycharm-debug-py3k.egg)

* Blender side:
  - Install the `Remote debugger` add-on.
    - There is a version in this archive under `BlenderScripts/addons/remote_debugger.py`.
    - If needed, replace it with a fresh version of the `remote_debugger.py` file from [here](https://code.blender.org/2015/10/debugging-python-code-with-pycharm/) or [here](https://github.com/sybrenstuvel/random-blender-addons/blob/master/remote_debugger.py)
  - Enable the add-on in Blender, open the preferences and set the path to the PyCharm egg file `pycharm-debug-py3k.egg` (i.e., `/Applications/PyCharm.app/Contents/debug-eggs/pycharm-debug-py3k.egg`)

* PyCharm side:
  - Create a debug configuration (Edit configurations):
  	- Add a “Python remote debug”
  	- name, e.g., “Remote Debug”
  	- local host name: localhost
  	- port: 1090
  	- NO redirect output to console
  	- YES suspend after connect
  	- It will fill the lines 2 and 3:
  		- Add the following import statement: import pydevd
  		- Add the following command to connect to the debug server: pydevd.settrace('localhost', port=1090)

* Run:
  - In PyCharm, start the debugger configuration.
  - In Blender, in the 3D view press space and search command: “Connect to remote PyCharm debugger”


## Reloading externally modified add-ons ##

https://stackoverflow.com/questions/15506971/recursive-version-of-reload/38243403#38243403

TODO

## With whom do I talk to? ##

Fabrizio Nunnari
<fabrizio.nunnari@dfki.de>
<fab.nunnari@gmail.com>

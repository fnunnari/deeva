# Deeva - Character Generation Platform
# Copyright (C) 2018 Fabrizio Nunnari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.path import abspath

from deeva.generation import create_random_individuals
from deeva.generation import AttributesTable
from deeva.generation import IndividualsTable
from deeva.generation import create_mblab_chars_dir


bl_info = {
    "name": "Deeva - Character Generation Tool",
    "description": "Deeva tools to manage attributes and generate random characters.",
    "author": "Fabrizio Nunnari",
    "version": (0, 10),
    "blender": (2, 79, 0),
    "location": "Toolbox > ManuelBastioniLAB > Generation",
    "category": "Characters",
    }


#
# GUI
#
class GenerationPanel(bpy.types.Panel):
    # bl_idname = "OBJECT_PT_GenerationPanel"
    bl_label = "Generation Tools (v" + (".".join([str(x) for x in bl_info["version"]])) + ")"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "Deeva"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.operator(ExportMBLabAttributes.bl_idname)

        row = layout.row()
        box = row.box()
        box.prop(context.scene, "deeva_generation_attributes_file")
        box.prop(context.scene, "deeva_generation_num_individuals")
        box.prop(context.scene, "deeva_generation_segments")
        box.operator(CreateRandomIndividuals.bl_idname)

        row = layout.row()
        box = row.box()
        box.prop(context.scene, "deeva_generation_attributes_file")
        box.prop(context.scene, "deeva_generation_individuals_file")
        box.prop(context.scene, "deeva_conversion_outdir")
        box.operator(ConvertIndividualsToMBLabJSon.bl_idname)


#
# INDIVIDUALS MANAGEMENT
#
class CreateRandomIndividuals(bpy.types.Operator, ExportHelper):
    """Generates a set of random individuals."""
    bl_idname = "deeva.create_random_individuals"
    bl_label = "Generate Individuals"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".csv"

    def execute(self, context):
        s = context.scene  # type: bpy.types.Scene

        attrib_table = AttributesTable(table_filename=abspath(s.deeva_generation_attributes_file))

        create_random_individuals(attributes_table=attrib_table,
                                  num_individuals=s.deeva_generation_num_individuals,
                                  out_filename=self.filepath,
                                  random_segments=s.deeva_generation_segments)

        return {'FINISHED'}


class ConvertIndividualsToMBLabJSon(bpy.types.Operator):
    """Generates a set of random individuals."""
    bl_idname = "deeva.convert_individuals"
    bl_label = "Convert Individuals to MBLAB/JSON dir"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ""
    use_filter_folder = True

    def execute(self, context):
        s = context.scene

        individuals_table = IndividualsTable(individuals_filename=abspath(s.deeva_generation_individuals_file))
        attrib_table = AttributesTable(table_filename=abspath(s.deeva_generation_attributes_file))

        create_mblab_chars_dir(individuals=individuals_table,
                               attributes=attrib_table,
                               dirpath=abspath(s.deeva_conversion_outdir))

        return {'FINISHED'}


#
# ATTRIBUTES EXPORT
#
class ExportMBLabAttributes(bpy.types.Operator, ExportHelper):
    """Export the attributes used by MBLab to control the shape of the characters.
    The exported csv can be used to populate the variables table in the web platform."""
    bl_idname = "deeva.export_attributes"
    bl_label = "Export MBLab Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".csv"

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if context.active_object.type == 'MESH':
                return True

        return False

    def execute(self, context):
        mesh_obj = context.active_object
        print("Saving to {}".format(self.filepath))

        export_mblab_attributes(mesh_obj=mesh_obj, outfilepath=self.filepath)

        return {'FINISHED'}


def export_mblab_attributes(mesh_obj: bpy.types.Object, outfilepath: str) -> None:
    import inspect
    import csv

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

    #
    # Write attribute list to a file
    print("Writing csv file '{}'...".format(outfilepath))
    with open(outfilepath, 'w') as csvfile:
        fieldnames = ['name', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for attribute in attributes:
            writer.writerow(attribute)

    print("Finished.")


#
# Register & Unregister ###
#

def register():
    bpy.types.Scene.deeva_generation_individuals_file = bpy.props.StringProperty(
        name="generation_individuals",
        default="",
        description="The CSV with the individuals table, as downloaded from the web platform.",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.deeva_generation_attributes_file = bpy.props.StringProperty(
        name="generation_attributes",
        default="",
        description="The CSV attributes table, as downloaded from the web platform.",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.deeva_generation_num_individuals = bpy.props.IntProperty(
        name="generation_num_individuals",
        default=100,
        description="Number of individuals to generate."
    )

    bpy.types.Scene.deeva_generation_segments = bpy.props.IntProperty(
        name="generation_segments",
        default=9,
        min=2,
        description="Number of segments to use for segmentation of randomization."
    )

    bpy.types.Scene.deeva_conversion_outdir = bpy.props.StringProperty(
        name="conversion_outdir",
        default="",
        description="The directory where to put the MBLab json files.",
        subtype='DIR_PATH'
    )

    bpy.utils.register_class(ExportMBLabAttributes)
    bpy.utils.register_class(GenerationPanel)
    bpy.utils.register_class(CreateRandomIndividuals)
    bpy.utils.register_class(ConvertIndividualsToMBLabJSon)


def unregister():
    bpy.utils.unregister_class(ExportMBLabAttributes)
    bpy.utils.unregister_class(GenerationPanel)
    bpy.utils.unregister_class(CreateRandomIndividuals)
    bpy.utils.unregister_class(ConvertIndividualsToMBLabJSon)

    del bpy.types.Scene.deeva_generation_attributes_file
    del bpy.types.Scene.deeva_generation_num_individuals
    del bpy.types.Scene.deeva_generation_segments
    del bpy.types.Scene.deeva_conversion_outdir


#
# Invoke register if started from editor
if __name__ == "__main__":
    register()

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
from bpy.path import abspath
from bpy_extras.io_utils import ExportHelper

from deeva.generation import AttributesTable
from deeva.generation import IndividualsTable
from deeva.generation_tools import export_mblab_attributes, create_mblab_chars_json_dir

bl_info = {
    "name": "Deeva - Character Generator",
    "description": "Deeva tools to manage attributes and generate random characters.",
    "author": "Fabrizio Nunnari",
    "version": (0, 10),
    "blender": (2, 79, 0),
    "location": "Toolbox > ManuelBastioniLAB > Generation",
    "category": "Characters",
    }


#
# GUIs
#
class ToolsPanel(bpy.types.Panel):
    # bl_idname = "OBJECT_PT_GenerationPanel"
    bl_label = bl_info["name"] + " Tools (v" + (".".join([str(x) for x in bl_info["version"]])) + ")"
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
        box.prop(context.scene, "deeva_generation_individuals_file")
        box.prop(context.scene, "deeva_conversion_outdir")
        box.operator(ConvertIndividualsToMBLabJSon.bl_idname)


class GenerationPanel(bpy.types.Panel):
    # bl_idname = "OBJECT_PT_GenerationPanel"
    bl_label = bl_info["name"] + " (v" + (".".join([str(x) for x in bl_info["version"]])) + ")"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "Deeva"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.prop(context.scene, "deeva_generation_attributes_file")
        box.prop(context.scene, "deeva_generation_individuals_file")
        box.label("TODO -- select file: the traits table")
        box.label("TODO -- select file: the votes results (coefficients and p values)")
        box.label("TODO -- grid: list the traits and select their values")
        box.label("TODO -- operator: reset/center traits")


#
# INDIVIDUALS MANAGEMENT
#
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

        create_mblab_chars_json_dir(individuals=individuals_table,
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

    bpy.types.Scene.deeva_conversion_outdir = bpy.props.StringProperty(
        name="conversion_outdir",
        default="",
        description="The directory where to put the MBLab json files.",
        subtype='DIR_PATH'
    )

    bpy.utils.register_class(ExportMBLabAttributes)
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(GenerationPanel)
    bpy.utils.register_class(ConvertIndividualsToMBLabJSon)


def unregister():
    bpy.utils.unregister_class(ExportMBLabAttributes)
    bpy.utils.unregister_class(ToolsPanel)
    bpy.utils.unregister_class(GenerationPanel)
    bpy.utils.unregister_class(ConvertIndividualsToMBLabJSon)

    del bpy.types.Scene.deeva_generation_attributes_file
    del bpy.types.Scene.deeva_conversion_outdir


#
# Invoke register if started from editor
if __name__ == "__main__":
    register()

bl_info = {
    "name": "Automation Tool for ManuelbastioniLAB",
    "description": "Automates import of scripts and genration of pictures from characters for the ManuelbastioniLAB.",
    "author": "Nicolas Erbach",
    "version": (0, 9),
    "blender": (2, 79, 0),
    "location": "Toolbox > ManuelBastioniLAB > Automation",
    "category": "Characters",
    }



import bpy
from mathutils import Vector

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )
                       
                       
pi = 3.14159265
                       
### Panel ###                     
                       
class AutomationPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_hello_world"
    bl_label = "Automation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "ManuelBastioniLAB"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        box = row.box()
        box.label(text="Load character files")
        box.prop(context.scene, "conf_path")
        box.operator(LoadScripts.bl_idname)
        
        row = layout.row()
        box = row.box()
        box.label(text="Preview characters")
        box.prop(context.scene, "character_file_list")

        '''
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.operator(LoadScripts.bl_idname, text="|<")
        row.operator(LoadScripts.bl_idname, text="<")
        row.operator(LoadScripts.bl_idname, text=">")
        row.operator(LoadScripts.bl_idname, text=">|")
        '''
        
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Camera")
        row.operator(ChangeCamera.bl_idname, text="Head").view = 'head'
        row.operator(ChangeCamera.bl_idname, text="Body").view = 'body'
        
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="head scale")
        row.prop(context.scene, "check_head_scale")
        row.prop(context.scene, "float_head_scale")
        
        row = box.row()
        row.alignment = 'EXPAND'
        row.label(text="Lights")
        row.operator(ReplaceLights.bl_idname, text="Replace Lights")
        
        row = layout.row()
        box = row.box()
        box.label(text="Generate pictures")
        box.prop(context.scene, "check_head_render")
        box.prop(context.scene, "check_body_render")
        box.prop(context.scene, "output_path")
        
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Render")
        row.operator(CreateOneRender.bl_idname, text="current").file_name = context.scene.character_file_list
        row.operator(CreateAllRender.bl_idname, text="all")
        
        
        
        row = layout.row()
        box = row.box()
        box.label(text="Version {}.{}".format(bl_info['version'][0], bl_info['version'][1]))
        



### Functions ###

class LoadScripts(bpy.types.Operator):
    """Iterates trough the folder and looks for json files."""
    bl_idname = "mbastauto.load_scripts"
    bl_label = "Load Scripts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        
        import glob, os
        
        #clear current list
        del context.scene.character_file_list_items[:]
        
        #print(" path" , context.scene.conf_path)
        os.chdir(context.scene.conf_path)
        
        #fill list with filenames
        for file in glob.glob("*.json"):
            #print(file)
            #print("enum m", context.scene.character_file_list_items)
            context.scene.character_file_list_items.append((file, file, file))
            
        print("enum s", context.scene.character_file_list)
        
            


        return {'FINISHED'}
    
class ChangeCamera(bpy.types.Operator):
    bl_idname = "mbastauto.change_camera"
    bl_label = "Change Camera"
    view = bpy.props.StringProperty()
 
    def execute(self, context):
        if self.view == 'head':
            #get correct skeleton
            skeleton = next( v for k,v in bpy.data.armatures.items() if k.find('skeleton'))
    
            #calculate head position and size
            bone_head_end = skeleton.bones['head'].tail_local
            bone_neck_start = skeleton.bones['neck'].head_local
            head_middle = (bone_head_end + bone_neck_start)/2
            head_length = (bone_head_end - bone_neck_start).length
            
            t = head_middle - Vector([0, 1, 0])
            r = [90, 0, 0]
            o = head_length * 1.1
            if context.scene.check_head_scale:
                o  = context.scene.float_head_scale
                
        elif self.view == 'body':
            t = [0, -5, 1.30]
            r = [90, 0, 0]
            o = 2.7
            
        #set camera position (translation)         
        bpy.context.scene.camera.location = t
        
        #set camera direction (rotation)
        r = [value * (pi/180.0) for value in r]
        bpy.context.scene.camera.rotation_mode = 'XYZ'
        bpy.context.scene.camera.rotation_euler = r
        
        #set camera to ortographic mode and set scale
        bpy.data.cameras['Camera'].type = 'ORTHO'
        bpy.data.cameras['Camera'].ortho_scale = o
        
        #set render size (to get correct preview)
        bpy.context.scene.render.resolution_x = 600
        bpy.context.scene.render.resolution_y = 600
        bpy.context.scene.render.resolution_percentage = 100
        
        #render settings
        bpy.data.scenes['Scene'].cycles.samples = 1000
        bpy.data.scenes['Scene'].cycles.sample_clamp_direct = 3
        bpy.data.scenes['Scene'].cycles.sample_clamp_indirect = 3
        
        
        
        
        return{'FINISHED'}  
    
    
class CreateOneRender(bpy.types.Operator):
    """Create render for currenttly selected chracter"""
    bl_idname = "mbastauto.create_one_render"
    bl_label = "Render current character"
    bl_options = {'REGISTER'}
    
    file_name = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        
        import glob, os
        
        
        if not context.scene.check_head_render and not context.scene.check_body_render:
            raise Exception("No picture type selected!")
        
        if not context.scene.output_path:
             raise Exception("No output path selected!")
        
        #script_name = context.scene.character_file_list
        script_name = self.file_name
        
        if not self.file_name:
            raise Exception("No character selected!")    
        name = script_name.replace(".json", "")
        
        #set background transparent
        bpy.context.scene.cycles.film_transparent = True
        bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
        
        if context.scene.check_head_render:
            bpy.ops.mbastauto.change_camera(view="head")
            bpy.data.scenes['Scene'].render.filepath = os.path.join(context.scene.output_path, "{}-head.png".format(name))
            bpy.ops.render.render( write_still=True ) 
            
        
        if context.scene.check_body_render:
            bpy.ops.mbastauto.change_camera(view="body")
            bpy.data.scenes['Scene'].render.filepath = os.path.join(context.scene.output_path, "{}-body.png".format(name))
            bpy.ops.render.render( write_still=True ) 


        return {'FINISHED'}
    
    
    
class CreateAllRender(bpy.types.Operator):
    """Create render for all chracters"""
    bl_idname = "mbastauto.create_all_render"
    bl_label = "Render current character"
    bl_options = {'REGISTER'}
    
    file_name = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        
        import glob, os
        
        
        if not context.scene.check_head_render and not context.scene.check_body_render:
            raise Exception("No picture type selected!")
        
        if not context.scene.output_path:
             raise Exception("No output path selected!")
        
        if not bpy.types.Scene.character_file_list_items :
            raise Exception("No characters loaded!") 
           
        print("here ") 
        for file_name in bpy.types.Scene.character_file_list_items:
            filepath = os.path.join(context.scene.conf_path, file_name[0])
            print(filepath)
            bpy.ops.mbast_import.character(filepath=filepath)
            print("rendering", file_name[0])
            bpy.ops.mbastauto.create_one_render(file_name=file_name[0])
            #bpy.ops.mbastauto.create_one_render().file_name=file_name[0]


        return {'FINISHED'}
    
'''
#camera settings
bpy.context.scene.render.resolution_x = 500
bpy.context.scene.render.resolution_y = 500
bpy.context.scene.render.resolution_percentage = 100

#set background transparent
bpy.context.scene.cycles.film_transparent = True
bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

#set render preset?
bpy.ops.script.execute_preset(filepath="C:\\Program Files\\Blender Foundation\\Blender\\2.78\\scripts\\presets\\cycles/sampling\\final.py", menu_idname="CYCLES_MT_sampling_presets")

#save image
home/t_image.png'
bpy.ops.render.render( write_still=True ) 


'''


class ReplaceLights(bpy.types.Operator):
    """Replace current lights with optimal lights"""
    bl_idname = "mbastauto.replace_lights"
    bl_label = "Replace Lights"
    bl_options = {'REGISTER'}
    
    
    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        
        #remove all lamps in current scene
        for c in bpy.data.lamps:
            print(c.name)
            bpy.data.lamps.remove(c, do_unlink=True)
            
        #add lamps
        
        # Create new lamp datablock
        bpy.ops.object.lamp_add(type='SUN')
        sun = bpy.data.lamps["Sun"]
        sun.shadow_soft_size=5
        sun.node_tree.nodes["Emission"].inputs[1].default_value = 15.0
        #sun.location = (-1.96, 1.59, 1.39)
        
        """
        lamp_data = bpy.data.lamps.new(name="Lamp Back", type='SUN')

        # Create new object with our lamp datablock
        lamp_object = bpy.data.objects.new(name="Lamp Back", object_data=lamp_data)

        # Link lamp object to the scene so it'll appear in this scene
        scene.objects.link(lamp_object)

        # Place lamp to a specified location
        lamp_object.location = (-1.96, 1.59, 1.39)
        lamp_data.energy=15
        
        r = [42, 37, 558]
        r = [value * (pi/180.0) for value in r]
        lamp_object.rotation_mode = 'XYZ'
        lamp_object.rotation_euler = r

        # And finally select it make active
        lamp_object.select = True
        scene.objects.active = lamp_object
        
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.worlds['World'].use_nodes = True
        """
        
        
        
        # Create new lamp datablock
        lamp_data = bpy.data.lamps.new(name="Lamp Front", type='HEMI')

        # Create new object with our lamp datablock
        lamp_object = bpy.data.objects.new(name="Lamp Front", object_data=lamp_data)

        # Link lamp object to the scene so it'll appear in this scene
        scene.objects.link(lamp_object)

        # Place lamp to a specified location
        lamp_object.location = (0.72, -1.6, 0.86)
        lamp_data.energy=15
        
        r = [108, 66, 38]
        r = [value * (pi/180.0) for value in r]
        lamp_object.rotation_mode = 'XYZ'
        lamp_object.rotation_euler = r

        # And finally select it make active
        lamp_object.select = True
        scene.objects.active = lamp_object

        return {'FINISHED'}



### Register & Unregister ###

def register():
    #panels
    bpy.utils.register_class(AutomationPanel)
    
    #operators
    bpy.utils.register_class(LoadScripts)
    bpy.utils.register_class(ChangeCamera)
    bpy.utils.register_class(CreateOneRender)
    bpy.utils.register_class(CreateAllRender)
    bpy.utils.register_class(ReplaceLights)
    
    
    #variables/props
    bpy.types.Scene.conf_path = bpy.props.StringProperty(
          name = "Scripts Path",
          default = "",
          description = "Define the path where the scripts are located",
          subtype = 'DIR_PATH'
      )
      
    bpy.types.Scene.character_file_list_items = []
    
    def fill_items(self, context):
        return bpy.types.Scene.character_file_list_items
    
    def change_preview(self, context):
        
        import os
        
        filepath = os.path.join(context.scene.conf_path ,context.scene.character_file_list)
        print(filepath)
        
        bpy.ops.mbast_import.character(filepath=filepath)
    
    bpy.types.Scene.character_file_list = bpy.props.EnumProperty(
            items = fill_items,
            name = "character",
            update = change_preview,
        )
        
    bpy.types.Scene.check_head_scale = bpy.props.BoolProperty(name = "manual")
    bpy.types.Scene.float_head_scale = bpy.props.FloatProperty(name = "number", default=0.5)
        
    bpy.types.Scene.check_head_render = bpy.props.BoolProperty(name = "head")
    bpy.types.Scene.check_body_render = bpy.props.BoolProperty(name = "body")

    bpy.types.Scene.output_path = bpy.props.StringProperty(
          name = "Images Path",
          default = "",
          description = "Define the path where the rendered imgaes should be written",
          subtype = 'DIR_PATH'
      )


def unregister():
    bpy.utils.unregister_class(AutomationPanel)
    bpy.utils.unregister_class(LoadScripts)
    bpy.utils.unregister_class(ChangeCamera)
    bpy.utils.unregister_class(CreateOneRender)
    bpy.utils.unregister_class(CreateAllRender)
    bpy.utils.unregister_class(ReplaceLights)
    del bpy.types.Scene.conf_path
    del bpy.types.Scene.character_file_list 
    del bpy.types.Scene.character_file_list_items
    del bpy.types.Scene.check_head_render 
    del bpy.types.Scene.check_body_render 
    del bpy.types.Scene.output_path 
    del bpy.types.Scene.check_head_scale
    del bpy.types.Scene.float_head_scale 

    
    
   


#invoke register if started from editor
if __name__ == "__main__":
    register()

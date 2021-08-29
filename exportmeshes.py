import os
import sys
import bpy
import math

from .util import *
from .addon.preferences import get_scexport_pref, set_scexport_pref

class ExportFBXFiles(bpy.types.Operator):
    bl_idname = "scexport.export_fbx_models"
    bl_label = "Export Objects as FBX"
    bl_description = "Exports meshes in the selected hierarchy as FBX files into the Export Path"
    
    def writeFBXFile(self, prefaceName, object):
        props = bpy.context.scene.StarCitizenExporterPreferences
        
        worldMatrix = list(object.matrix_world)
        object.matrix_world.identity()
        
        if (object.type != "MESH"):
            return
        
        object.select_set(True)
        object.hide_set(False)
        
        itemname = object.name
        if ("orig_name" in object):
            itemname = object["orig_name"]
        itemname = SanitizeName(itemname)
        prefaceName = SanitizeName(prefaceName)
        if (itemname == 'Merged' or itemname.startswith('Merged.')):
            itemname = prefaceName
        
        outputFolder = getOutputFolder(prefaceName)
        
        if (not os.path.exists(outputFolder)):
            os.makedirs(outputFolder)
        
        #if (prefaceName != ""):
        #    itemname = SanitizeName(prefaceName + '_' + itemname)
        FilePath = os.path.join(outputFolder, itemname + '.fbx')
        
        print("Writing FBX file: "+FilePath)
        bpy.ops.export_scene.fbx(filepath=FilePath, use_selection=True, object_types={'MESH'}, mesh_smooth_type='EDGE', use_tspace=True, use_mesh_modifiers=True)
        
        object.select_set(False)
        object.matrix_world = worldMatrix

    def ProcessChildren(self, prefaceName, object):
        self.writeFBXFile(prefaceName, object)
        children = getChildren(object)
        
        for child in children:
            self.ProcessChildren(prefaceName, child)

    def execute(self, context):
        print("Exporting FBX files...")
        props = bpy.context.scene.StarCitizenExporterPreferences
        
        TopObj = context.object
        TopName = TopObj.name
        if ("orig_name" in TopObj):
            TopName = TopObj["orig_name"]
            
        if ("source_file" in TopObj):
            props.asset_path = TopObj["source_file"].rsplit('/', maxsplit=1)[0]
            
        TopName = SanitizeName(TopName)
        self.writeFBXFile("", TopObj)
        children = getChildren(TopObj)
        
        for child in children:
            self.ProcessChildren(TopName, child)
        
        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class(ExportFBXFiles)

def unregister():
    bpy.utils.unregister_class(ExportFBXFiles)
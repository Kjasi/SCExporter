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
    
    MeshesToExport = []
    CollectionList = []
    
    def writeFBXFile(self, prefaceName, object):
        props = bpy.context.scene.StarCitizenExporterPreferences
        
        worldMatrix = list(object.matrix_world)
        object.matrix_world.identity()
        
        if (object.type != "MESH"):
            return
            
        oldSelection = bpy.context.selected_objects
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        
        object.select_set(True)
        object.hide_set(False)
        
        prefaceName = SanitizeName(prefaceName)
        itemname = SanitizeName(object.name)
        if ("orig_name" in object):
            itemname = SanitizeName(object["orig_name"])
        elif (itemname == 'Merged' or itemname.startswith('Merged.')):
            itemname = prefaceName
        elif (not itemname.startswith(prefaceName)):
            itemname = prefaceName + "_" + itemname
            
        if ("source_file" in object):
            print("SourceFile found: %s", object["source_file"])
            filepath = object["source_file"].rsplit('/', maxsplit=1)[0]
            filename = object["source_file"].rsplit('/', maxsplit=1)[1]
            filename = filename.rsplit('.', maxsplit=1)[0]
            props.asset_path = filepath
            itemname = ("%s_%s" % (filename, itemname))
        
        print("Itemname: %s, AssetPath: %s" %(itemname, props.asset_path))
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
        
        for obj in oldSelection:
            obj.select_set(True)

    def ProcessChildren(self, object):
        if (object.type == "MESH"):
            if object not in self.MeshesToExport:
                self.MeshesToExport.append(object)
        elif (object.type == "EMPTY" and object.instance_type == "COLLECTION"):
            print("Collection Found!")
            if object.instance_collection.name not in self.CollectionList:
                self.CollectionList.append(object.instance_collection.name)
        
        children = getChildren(object)
        
        for child in children:
            self.ProcessChildren(child)

    def execute(self, context):
        print("Exporting FBX files...")
        props = bpy.context.scene.StarCitizenExporterPreferences
        
        for TopObj in bpy.context.selected_objects:
            TopName = TopObj.name

            if ("orig_name" in TopObj):
                TopName = TopObj["orig_name"]
                
            if ("source_file" in TopObj):
                props.asset_path = TopObj["source_file"].rsplit('/', maxsplit=1)[0]

            TopName = SanitizeName(TopName)
            print("TopName: %s, assetPath: %s" % (TopName, props.asset_path))
            self.writeFBXFile("", TopObj)
            children = getChildren(TopObj)
            
            for child in children:
                self.ProcessChildren(child)
            
        if len(self.CollectionList) > 0:
            for collectionName in self.CollectionList:
                TopItem = bpy.data.collections[collectionName].objects[0]
                children = getChildren(TopItem)
            
                for child in children:
                    self.ProcessChildren(child)


        bpy.context.window.scene = bpy.data.scenes["StarFab"]
        if len(self.MeshesToExport) > 0:
            for meshObject in self.MeshesToExport:
                self.writeFBXFile(TopName, meshObject)
                
        bpy.context.window.scene = bpy.data.scenes["Scene"]
        self.CollectionList = []
        
        
        print("Finished Exporting FBX files.")
        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class(ExportFBXFiles)

def unregister():
    bpy.utils.unregister_class(ExportFBXFiles)
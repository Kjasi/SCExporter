import bpy
from bpy.types import Operator
from . import preferences

class SCExporterPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SCExporter"


class SCEXPORTER_PT_Main(SCExporterPanel, bpy.types.Panel):
    bl_idname = "SCEXPORTER_PT_UI_MAIN"
    bl_label = "Star Citizen Exporting"
    
    def draw(self, context):
        addon_prefs = bpy.context.scene.StarCitizenExporterPreferences
        layout = self.layout
        
        obj = context.object
        objName = "None"
        assetPath = ""
        if (obj):
            objName = obj.name
            if ("source_file" in obj):
                srcPath = obj["source_file"].rsplit('/', maxsplit=1)[0]
                assetPath = srcPath
                
        outFolder = addon_prefs.output_path + "/"+ assetPath + "/"
        outFolder = outFolder.replace("\\","/")
        while "//" in outFolder:
            outFolder = outFolder.replace("//","/")
        if (outFolder == "/"):
            outFolder = ""
            
        row = layout.row()
        row.label(text="Top level object is: " + objName)
        
        row = layout.row()
        row.label(text="Output Folder: " + outFolder)

class SCEXPORTER_PT_Prefs(SCExporterPanel, bpy.types.Panel):
    bl_parent_id  = "SCEXPORTER_PT_UI_MAIN"
    bl_label = "Preferences"
    
    def draw(self, context):
        addon_prefs = bpy.context.scene.StarCitizenExporterPreferences
        layout = self.layout
        
        row = layout.row()
        row.prop(addon_prefs, "output_path")
        
        row = layout.row()
        row.prop(addon_prefs, "asset_path")
        
        row = layout.row()
        row.prop(addon_prefs, "asset_subpath")
        
        row = layout.row()
        row.prop(addon_prefs, "exportBillboards")

class SCEXPORTER_PT_Cleanup(SCExporterPanel, bpy.types.Panel):
    bl_parent_id  = "SCEXPORTER_PT_UI_MAIN"
    bl_label = "Cleanup"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("scexport.cleanup_materials")

class SCEXPORTER_PT_Exporting(SCExporterPanel, bpy.types.Panel):
    bl_parent_id  = "SCEXPORTER_PT_UI_MAIN"
    bl_label = "Exporting"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("scexport.export_fbx_models")
        
        row = layout.row()
        row.operator("scexport.write_unreal_blueprint_file")
        
        
classes = (
    SCEXPORTER_PT_Main,
    SCEXPORTER_PT_Prefs,
    SCEXPORTER_PT_Cleanup,
    SCEXPORTER_PT_Exporting,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
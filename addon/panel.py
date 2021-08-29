import bpy
from bpy.types import Operator
from . import preferences


class SCExportPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_export_panel"
    bl_label = "Star Citizen Exporting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SCExport"

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
        row.label(text="Blueprint Creation", icon='MESH_GRID')

        row = layout.row()
        row.label(text="Top level object is: " + objName)
        
        row = layout.row()
        
        row.label(text="Output Folder: " + outFolder)
        
        row = layout.row()
        row.prop(addon_prefs, "output_path")
        
        row = layout.row()
        row.prop(addon_prefs, "asset_subpath")
        
        row = layout.row()
        row.operator("scexport.export_fbx_models")
        
        row = layout.row()
        row.operator("scexport.write_unreal_blueprint_file")

        row = layout.row()
        #row.operator("scene.export_fbx_models")
        
        
def register():
    bpy.utils.register_class(SCExportPanel)


def unregister():
    bpy.utils.unregister_class(SCExportPanel)
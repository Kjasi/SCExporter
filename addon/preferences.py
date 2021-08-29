import bpy
from bpy.props import StringProperty

class SCExportPreferences(bpy.types.PropertyGroup):

    output_path: StringProperty(
        name="Export Path",
        subtype='DIR_PATH',
        default="R:/StarCitizen/StarCitizenCinema/",
        description="Root folder to export all the files to"
    )
    
    asset_path: StringProperty(
        name="Asset Path",
        default="Objects/",
        description="Path to where the object should be stored, under the Export Path"
    )
    
    asset_subpath: StringProperty(
        name="UnrealEngine Asset Subpath",
        default="Meshes",
        description="Subdirectory used in Unreal Engine to store the meshes under"
    )


def register():
    bpy.utils.register_class(SCExportPreferences)    
    bpy.types.Scene.StarCitizenExporterPreferences = bpy.props.PointerProperty(type=SCExportPreferences)


def unregister():
    bpy.utils.unregister_class(SCExportPreferences)
    del bpy.types.Scene.StarCitizenExporterPreferences


def get_scexport_pref(prop):
    return getattr(bpy.context.preferences.addons['StarCitizenExporterPreferences'].preferences, prop)


def set_scexport_pref(prop, value):
    return setattr(bpy.context.preferences.addons['StarCitizenExporterPreferences'].preferences, prop, value)
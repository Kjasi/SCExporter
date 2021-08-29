import bpy

from .utils import reload_blender_modules
from . import preferences, panel
from .. import exportmeshes, unreal #, unity

modules = [
    exportmeshes,
    unreal
    #unity
]

def updateAssetPath(scene):
    obj = scene.objects.active
    srcPath = ""
    if (obj and "source_file" in obj):
        srcPath = obj["source_file"].rsplit('/', maxsplit=1)[0]
        scene.SCExportPreferences.asset_path = srcPath


def register():
    if not modules:
        return

    reload_blender_modules()

    for module in modules:
        module.register()

    preferences.register()
    panel.register()

def unregister():
    
    for module in modules:
        module.unregister()
        
    preferences.unregister()
    panel.unregister()
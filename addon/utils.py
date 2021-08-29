import sys
import importlib

def reload_blender_modules():
    # build up the list of modules first, otherwise sys.modules will change while you iterate through it
    loaded_modules = [m for n, m in sys.modules.items() if n.startswith('SCExport')]
    for module in loaded_modules:
        importlib.reload(module)

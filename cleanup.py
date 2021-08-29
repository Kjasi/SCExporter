import bpy

class MergeMaterials(bpy.types.Operator):
    bl_idname = "scexport.cleanup_materials"
    bl_label = "Merge Materials"
    bl_description = "Will merge all materials with the same name. IE: Merges matname.001 & matname.003 into matname"
    
    def execute(self, context):
        mats = bpy.data.materials

        for obj in bpy.data.objects:
            for slt in obj.material_slots:
                part = slt.name.rpartition('.')
                if part[2].isnumeric() and part[0] in mats:
                    slt.material = mats.get(part[0])
                    
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(MergeMaterials)

def unregister():
    bpy.utils.unregister_class(MergeMaterials)
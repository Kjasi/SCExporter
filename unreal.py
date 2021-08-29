import bpy
import os
import math

from .util import *
from .addon.preferences import get_scexport_pref, set_scexport_pref

# Converts Meters to Centimeters
EngineScale = 100.0

class exportBlueprint(bpy.types.Operator):
    bl_idname = "scexport.write_unreal_blueprint_file"
    bl_label = "Save Unreal Blueprint Data"
    bl_description = "Saves the current hierarchy information as a .txt file that can be copied and pasted into an Unreal Engine actor blueprint"
    
    def GetParentAttachmentText(self, obj):
        text = ""
        if (obj.parent):
            parentname = SanitizeName(obj.parent.name)
            if ("orig_name" in obj.parent):
                parentname = obj.parent["orig_name"]
            text = '''
    AttachParent='''
            if (obj.parent.type == "ARMATURE"):
                text += '''SkeletalMeshComponent'''
            elif (obj.parent.type == "MESH"):
                text += '''StaticMeshComponent'''
            else:
                text += '''SceneComponent'''
            text += ''''"'''+parentname+'_GEN_VARIABLE\"\''
        return text
    
    def GenerateSceneComponent(self, prefaceName, obj, skipbillboard = False):
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        itemname = obj.name
        if ("orig_name" in obj):
            itemname = obj["orig_name"]
        itemname = SanitizeName(itemname)
        text = 'Begin Object Class=/Script/Engine.SceneComponent Name="'+itemname+'_GEN_VARIABLE\"'
        if (pos[0] != 0.0 or pos[1] != 0.0 or pos[2] != 0.0):
            text += '''
    RelativeLocation=(X='''+str(pos[0] * EngineScale)+''',Y='''+str(-pos[1] * EngineScale)+''',Z='''+str(pos[2] * EngineScale)+''')'''
    
        if (rot[0] != 0.0 or rot[1] != 0.0 or rot[2] != 0.0):
            text += '''
    RelativeRotation=(Pitch='''+str(-math.degrees(rot[1]))+''',Yaw='''+str(-math.degrees(rot[2]))+''',Roll='''+str(math.degrees(rot[0]))+''')'''
        ''' Pitch = Y, Yaw = Z, Roll = X '''
        
        if (scale[0] != 1.0 or scale[1] != 1.0 or scale[2] != 1.0):
            text += '''
    RelativeScale3D=(X='''+str(scale[0])+''',Y='''+str(scale[1])+''',Z='''+str(scale[2])+''')'''
        
        text += self.GetParentAttachmentText(obj)
        text += '''
End Object'''
        if (itemname[0:8] != "$physics" and obj.parent and not skipbillboard):
            text += '''
Begin Object Class=/Script/Engine.BillboardComponent Name="Billboard_%s_GEN_VARIABLE"
    RelativeScale3D=(X=0.500000,Y=0.500000,Z=0.500000)
    AttachParent=SceneComponent'"%s_GEN_VARIABLE"'
End Object''' % (itemname, itemname)
        
        return text
    
    def GenerateLightComponent(self, prefaceName, obj):
        pos = obj.location
        obj.rotation_mode = 'XYZ'
        rot = obj.rotation_euler
        scale = obj.scale
        itemname = obj.name
        itemname = SanitizeName(itemname)
        lamp = bpy.data.objects[obj.name].data
        text = ""
        if (lamp.type == "SUN"):
            text = 'Begin Object Class=/Script/Engine.DirectionalLightComponent Name="'+itemname+'_GEN_VARIABLE\"'
            text += '''
    LightSourceAngle=%f''' % (degrees(lamp.angle))
        elif (lamp.type == "SPOT"):
            text = 'Begin Object Class=/Script/Engine.SpotLightComponent Name="'+itemname+'_GEN_VARIABLE\"'
            text += '''
    SourceRadius=%f
    SoftSourceRadius=%f
    SourceLength=%f''' % (lamp.shadow_soft_size * EngineScale, 0.0, 0.0)
        elif (lamp.type == "AREA"):
            text = 'Begin Object Class=/Script/Engine.RectLightComponent Name="'+itemname+'_GEN_VARIABLE\"'
            text += '''
    SourceWidth=%f
    SourceHeight=%f
    BarnDoorAngle=%f
    BarnDoorLength=%f''' % (lamp.size * EngineScale, lamp.size * EngineScale, 88.0, 20.0)
        elif (lamp.type == "POINT"):
            text = 'Begin Object Class=/Script/Engine.PointLightComponent Name="'+itemname+'_GEN_VARIABLE\"'
            text += '''
    SourceRadius=%f
    SoftSourceRadius=%f
    SourceLength=%f''' % (lamp.shadow_soft_size * EngineScale, 0.0, 0.0)
        else:
            print("Unsupported Light Type: %s" % lamp.type)
            return ""
        
        # Shared Values
        text += '''
    Intensity=%f
    AttenuationRadius=%f
    LightColor=(B=%i, G=%i, R=%i, A=%i)''' % (lamp.energy * 100000, lamp.cutoff_distance * 100 * EngineScale, lamp.color[2]*255,lamp.color[1]*255,lamp.color[0]*255,255)
        if (pos[0] != 0.0 or pos[1] != 0.0 or pos[2] != 0.0):
            text += '''
    RelativeLocation=(X='''+str(pos[0] * EngineScale)+''',Y='''+str(-pos[1] * EngineScale)+''',Z='''+str(pos[2] * EngineScale)+''')'''
    
        if (rot[0] != 0.0 or rot[1] != 0.0 or rot[2] != 0.0):
            text += '''
    RelativeRotation=(Pitch='''+str(-math.degrees(rot[1]))+''',Yaw='''+str(-math.degrees(rot[2]))+''',Roll='''+str(math.degrees(rot[0]))+''')'''
        ''' Pitch = Y, Yaw = Z, Roll = X '''
        
        if (scale[0] != 1.0 or scale[1] != 1.0 or scale[2] != 1.0):
            text += '''
    RelativeScale3D=(X='''+str(scale[0])+''',Y='''+str(scale[1])+''',Z='''+str(scale[2])+''')'''
        
        text += self.GetParentAttachmentText(obj)
        text += '''
End Object'''
        return text
        
    def GenerateStaticMeshComponent(self, prefaceName, obj):
        props = bpy.context.scene.StarCitizenExporterPreferences
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        itemname = obj.name
        if ("orig_name" in obj):
            itemname = obj["orig_name"]
        itemname = SanitizeName(itemname)
        text = 'Begin Object Class=/Script/Engine.StaticMeshComponent Name="'+itemname+'_GEN_VARIABLE"'
        
        assetPath = props.asset_path
        if (props.asset_subpath != ""):
            assetPath += '/' + props.asset_subpath
        assetPath = assetPath.strip("/")
        assetPath = assetPath.replace("\\", "/")
        assetPath = assetPath.replace("//", "/")
        
        text += '''
    StaticMesh=StaticMesh'"/Game/'''+assetPath+"/"+itemname+"."+itemname+'''"'
    StaticMeshImportVersion=1'''
        if (pos[0] != 0.0 or pos[1] != 0.0 or pos[2] != 0.0):
            text += '''
    RelativeLocation=(X='''+str(pos[0] * EngineScale)+''',Y='''+str(-pos[1] * EngineScale)+''',Z='''+str(pos[2] * EngineScale)+''')'''
    
        if (rot[0] != 0.0 or rot[1] != 0.0 or rot[2] != 0.0):
            text += '''
    RelativeRotation=(Pitch='''+str(-math.degrees(rot[1]))+''',Yaw='''+str(-math.degrees(rot[2]))+''',Roll='''+str(math.degrees(rot[0]))+''')'''
        ''' Pitch = Y, Yaw = Z, Roll = X '''
        
        if (scale[0] != 1.0 or scale[1] != 1.0 or scale[2] != 1.0):
            text += '''
    RelativeScale3D=(X='''+str(scale[0])+''',Y='''+str(scale[1])+''',Z='''+str(scale[2])+''')'''
        
        text += self.GetParentAttachmentText(obj)
        text += '''
End Object'''
        return text
        
    def GenerateSkeletalMeshComponent(self, prefaceName, obj):
        props = bpy.context.scene.StarCitizenExporterPreferences
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        itemname = SanitizeName(obj.parent.name)
        if ("orig_name" in obj):
            itemname = obj["orig_name"]
        itemname = SanitizeName(itemname)
        text = 'Begin Object Class=/Script/Engine.SkeletalMeshComponent Name="'+itemname+'_GEN_VARIABLE\"'
        
        objName = SanitizeName(itemname)
        assetPath = props.asset_path
        if (props.asset_subpath != ""):
            assetPath += '/' + props.asset_subpath
        assetPath = assetPath.strip("/")
        assetPath = assetPath.replace("\\", "/")
        assetPath = assetPath.replace("//", "/")
        
        text += '''
    SkeletalMesh=SkeletalMesh'"/Game/'''+assetPath+"/"+objName+"."+objName+'\'"'
        if (pos[0] != 0.0 or pos[1] != 0.0 or pos[2] != 0.0):
            text += '''
    RelativeLocation=(X='''+str(pos[0] * EngineScale)+''',Y='''+str(-pos[1] * EngineScale)+''',Z='''+str(pos[2] * EngineScale)+''')'''
    
        if (rot[0] != 0.0 or rot[1] != 0.0 or rot[2] != 0.0):
            text += '''
    RelativeRotation=(Pitch='''+str(-math.degrees(rot[1]))+''',Yaw='''+str(-math.degrees(rot[2]))+''',Roll='''+str(math.degrees(rot[0]))+''')'''
        ''' Pitch = Y, Yaw = Z, Roll = X '''
        
        if (scale[0] != 1.0 or scale[1] != 1.0 or scale[2] != 1.0):
            text += '''
    RelativeScale3D=(X='''+str(scale[0])+''',Y='''+str(scale[1])+''',Z='''+str(scale[2])+''')'''
        
        text += self.GetParentAttachmentText(obj)
        text += '''
End Object'''
        return text
    
    def GetChildrenText(self, prefaceName, child):
        children = getChildren(child)
        text = self.GenerateBlueprintText(prefaceName, child)

        for child in children:
            childText = self.GetChildrenText(prefaceName, child)
            if (childText != ""):
                text += '''
'''
                text += childText
            
        return text
    
    def GenerateBlueprintText(self, prefaceName, obj):
        text = ""
        
        if (obj.type == "EMPTY"):
            if (obj.instance_type != "NONE"):
                text += self.GenerateSceneComponent(prefaceName, obj, True)
            else:
                text += self.GenerateSceneComponent(prefaceName, obj)
        elif (obj.type == "ARMATURE"):
            # Get the next child mesh, and use that.
            children = getChildren(obj)
            if (len(children) > 0):
                if (children[0].type == "MESH"):
                    text += self.GenerateSkeletalMeshComponent(prefaceName, children[0])
            
        elif (obj.type == "LIGHT"):
            text += self.GenerateLightComponent(prefaceName, obj)
        elif (obj.type == "MESH"):
            if (obj.parent):
                if (obj.parent.type == "ARMATURE"):
                    return ""
            text += self.GenerateStaticMeshComponent(prefaceName, obj)
        else:
            print("Unsupported Object Type: %s" % obj.type)
            return ""
        
        if (text == ""):
            return ""

        return text

    def writeBlueprintFile(self, prefaceName, objparent):
        props = bpy.context.scene.StarCitizenExporterPreferences
        children = getChildren(objparent)
        
        alltext = self.GenerateBlueprintText(prefaceName, objparent)

        for child in children:
            text = self.GetChildrenText(prefaceName, child)
            if (text != ""):
                alltext += '''
''' + text
        
        objName = objparent.name
        if ("orig_name" in objparent):
            objName = objparent["orig_name"]
            
        outputFolder = getOutputFolder(objName)
            
        print("Final outputFolder: %s" % outputFolder)
        
        if (not os.path.exists(outputFolder)):
            os.makedirs(outputFolder)
            
        ObjFileName = SanitizeName(objName)
        while (ObjFileName[-1] == "_"):
            ObjFileName = ObjFileName[:-1]
            
        #print("ObjFileName: %s" % ObjFileName)
        
        filename = outputFolder + SanitizeName(ObjFileName) + ".txt"
        print("Writing Unreal Blueprint file: "+filename)
        
        # open a file to write to
        file = open(filename, "w")
        if (not file):
            return
        # write the data to file
        file.write(alltext)
        # close the file
        file.close()
        
    def execute(self, context):
        print("Saving Blueprint Data to a file...")
        props = bpy.context.scene.StarCitizenExporterPreferences
        object = context.object
        if (not object):
            print("\nNo Object selected. Unable to save file.")
            return {'FINISHED'}
            
        if ("source_file" in object):
            props.asset_path = object["source_file"].rsplit('/', maxsplit=1)[0]
            
        objName = object.name
        if ("orig_name" in object):
            objName = object["orig_name"]
            
        self.writeBlueprintFile(objName, object)
                
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(exportBlueprint)

def unregister():
    bpy.utils.unregister_class(exportBlueprint)
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
    
    CollectionsToExport = []
    NamesDB = {}
    
    def FixRepeatNames(self, itemname):
        if itemname in self.NamesDB:
            self.NamesDB[itemname] += 1
            itemname += str(self.NamesDB[itemname])
        else:
            self.NamesDB[itemname] = 0
            
        return itemname
    
    def GetTransformText(self, pos, rot, scale):
        text = ""
        if (pos and (pos[0] != 0.0 or pos[1] != 0.0 or pos[2] != 0.0)):
            text += '''
    RelativeLocation=(X=%s,Y=%s,Z=%s)''' % (str(pos[0] * EngineScale), str(-pos[1] * EngineScale), str(pos[2] * EngineScale))
    
        # Pitch = Y, Yaw = Z, Roll = X
        if (rot and (rot[0] != 0.0 or rot[1] != 0.0 or rot[2] != 0.0)):
            text += '''
    RelativeRotation=(Pitch=%s,Yaw=%s,Roll=%s)''' % (str(-math.degrees(rot[1])), str(-math.degrees(rot[2])), str(math.degrees(rot[0])))
        
        if (scale and (scale[0] != 1.0 or scale[1] != 1.0 or scale[2] != 1.0)):
            text += '''
    RelativeScale3D=(X=%s,Y=%s,Z=%s)''' % (str(scale[0]), str(scale[1]), str(scale[2]))
    
        return text
    
    def GetParentAttachmentText(self, prefaceName, obj):
        text = ""
        if (obj.parent):
            prefaceName = SanitizeName(prefaceName)
            
            parentname = obj.parent.name
            if ("filename" in obj.parent):
                parentname = getMeshName(obj.parent["filename"])
            if ("orig_name" in obj.parent):
                parentname = obj.parent["orig_name"]
            if ("BlueprintName" in obj.parent):
                parentname = obj["BlueprintName"]
            parentname = SanitizeName(parentname)
            
            text = '''
    AttachParent='''
            if (obj.parent.type == "ARMATURE"):
                text += 'SkeletalMeshComponent'+''''"'''+prefaceName+'_'
            elif (obj.parent.type == "MESH"):
                text += 'StaticMeshComponent'+''''"'''+prefaceName+'_'
            else:
                text += 'SceneComponent'+''''"'''
            text += parentname+'_GEN_VARIABLE\"\''
        return text
    
    def GenerateSceneComponent(self, prefaceName, obj, skipbillboard = False):
        props = bpy.context.scene.StarCitizenExporterPreferences
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        itemname = obj.name
        if ("filename" in obj):
            itemname = getMeshName(obj["filename"])
        if ("orig_name" in obj):
            itemname = SanitizeName(obj["orig_name"])
        itemname = SanitizeName(itemname)
        itemname = self.FixRepeatNames(itemname)
        obj["BlueprintName"] = itemname
        
        text = 'Begin Object Class=/Script/Engine.SceneComponent Name="'+itemname+'_GEN_VARIABLE\"'
        text += self.GetTransformText(pos, rot, scale)
        text += self.GetParentAttachmentText(prefaceName, obj)
        text += '''
End Object'''
        if (itemname[0:8] != "$physics" and obj.parent and not skipbillboard and props.exportBillboards):
            text += '''
Begin Object Class=/Script/Engine.BillboardComponent Name="Billboard_%s_GEN_VARIABLE"
    RelativeScale3D=(X=0.500000,Y=0.500000,Z=0.500000)
    AttachParent=SceneComponent'"%s_GEN_VARIABLE"'
End Object''' % (itemname, itemname)
        
        return text
    
    def GenerateChildActorComponent(self, prefaceName, obj):
        props = bpy.context.scene.StarCitizenExporterPreferences
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale

        prefaceName = SanitizeName(prefaceName)
        itemname = SanitizeName(obj.name)
        
        if ("orig_name" in obj):
            itemname = obj["orig_name"]
        elif (itemname == 'Merged' or itemname.startswith('Merged.')):
            itemname = prefaceName
        elif (not itemname.startswith(prefaceName)):
            itemname = prefaceName + "_" + itemname
            
        itemname = self.FixRepeatNames(itemname)
        obj["BlueprintName"] = itemname

        itempath = props.asset_path
        if ("filename" in obj):
            filepath = obj["filename"].rsplit('/', maxsplit=1)[0]
            filename = obj["filename"].rsplit('/', maxsplit=1)[1]
            itemname = filename.rsplit('.', maxsplit=1)[0]
            itempath = filepath
        
        itemname = SanitizeName(itemname)
        
        text = ('Begin Object Class=/Script/Engine.ChildActorComponent Name="%s_GEN_VARIABLE"'%(itemname))
        text += '''
    Begin Object Class=/Game/{path}/{itemname}.{itemname}_C Name="{itemname}_GEN_VARIABLE_{itemname}_C_CAT"
    End Object
    Begin Object Name="{itemname}_GEN_VARIABLE_{itemname}_C_CAT"
        ActorLabel="{itemname}-1"
    End Object
    ChildActorClass=BlueprintGeneratedClass'"/Game/{path}/{itemname}.{itemname}_C"\''''.format(
        path=itempath,
        itemname=itemname
        )
        
        text += self.GetTransformText(pos, rot, scale)
        text += self.GetParentAttachmentText(prefaceName, obj)
        text += '''
End Object'''
        
        return text
    
    def GenerateLightComponent(self, prefaceName, obj):
        pos = obj.location
        obj.rotation_mode = 'XYZ'
        rot = obj.rotation_euler
        scale = obj.scale
        itemname = obj.name
        itemname = SanitizeName(itemname)
        
        itemname = self.FixRepeatNames(itemname)
        obj["BlueprintName"] = itemname
        
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
    
        text += self.GetTransformText(pos, rot, scale)
        text += self.GetParentAttachmentText(prefaceName, obj)
        text += '''
End Object'''
        return text
        
    def GenerateStaticMeshComponent(self, prefaceName, obj):
        props = bpy.context.scene.StarCitizenExporterPreferences
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        
        prefaceName = SanitizeName(prefaceName)
        itemname = SanitizeName(obj.name)
        
        if ("filename" in obj):
            itemname = getMeshName(obj["filename"])
        elif ("orig_name" in obj):
            itemname = obj["orig_name"]
        elif (itemname == 'Merged' or itemname.startswith('Merged.')):
            itemname = prefaceName
        elif (not itemname.startswith(prefaceName)):
            itemname = prefaceName + "_" + itemname

        itemname = self.FixRepeatNames(itemname)
        obj["BlueprintName"] = itemname

        itempath = props.asset_path
        if ("source_file" in obj):
            filepath = obj["source_file"].rsplit('/', maxsplit=1)[0]
            filename = obj["source_file"].rsplit('/', maxsplit=1)[1]
            filename = filename.rsplit('.', maxsplit=1)[0]
            itempath = filepath
            itemname = ("%s_%s" % (filename, itemname))
        
        itemname = SanitizeName(itemname)
        text = 'Begin Object Class=/Script/Engine.StaticMeshComponent Name="'+itemname+'_GEN_VARIABLE"'
        
        assetPath = itempath
        if (props.asset_subpath != ""):
            assetPath += '/' + props.asset_subpath
        assetPath = assetPath.strip("/")
        assetPath = assetPath.replace("\\", "/")
        assetPath = assetPath.replace("//", "/")
        
        text += '''
    StaticMesh=StaticMesh'"/Game/'''+assetPath+"/"+itemname+"."+itemname+'''"'
    StaticMeshImportVersion=1'''
    
        text += self.GetTransformText(pos, rot, scale)
        text += self.GetParentAttachmentText(prefaceName, obj)
        text += '''
End Object'''
        return text
        
    def GenerateSkeletalMeshComponent(self, prefaceName, obj):
        props = bpy.context.scene.StarCitizenExporterPreferences
        pos = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        
        prefaceName = SanitizeName(prefaceName)
        itemname = SanitizeName(obj.name)
        if ("filename" in obj):
            itemname = SanitizeName(getMeshName(obj["filename"]))
        if ("orig_name" in obj):
            itemname = SanitizeName(obj["orig_name"])
        elif (itemname == 'Merged' or itemname.startswith('Merged.')):
            itemname = prefaceName
        elif (not itemname.startswith(prefaceName)):
            itemname = prefaceName + "_" + itemname

        itemname = self.FixRepeatNames(itemname)
        obj["BlueprintName"] = itemname
        
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
        
        text += self.GetTransformText(pos, rot, scale)
        text += self.GetParentAttachmentText(prefaceName, obj)
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
        
        if (obj.type == "MESH"):
            if (obj.parent):
                if (obj.parent.type == "ARMATURE"):
                    return ""
            text += self.GenerateStaticMeshComponent(prefaceName, obj)
        elif (obj.type == "EMPTY" and obj.instance_type == "COLLECTION"):
            text += self.GenerateChildActorComponent(prefaceName, obj)
            if obj.instance_collection.name not in self.CollectionsToExport:
                self.CollectionsToExport.append(obj.instance_collection.name)
        elif (obj.type == "EMPTY"):
            #print("Obj Instance Type: %s" %(obj.instance_type))
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
        else:
            print("Unsupported Object Type: %s" % obj.type)
            return ""
        
        if (text == ""):
            return ""

        return text

    def writeBlueprintFile(self, prefaceName, objparent):
        props = bpy.context.scene.StarCitizenExporterPreferences
        children = getChildren(objparent)
        self.NamesDB = {}
        
        alltext = self.GenerateBlueprintText(prefaceName, objparent)

        for child in children:
            text = self.GetChildrenText(prefaceName, child)
            if (text != ""):
                alltext += '''
''' + text
        
        objName = objparent.name
        if ("filename" in objparent):
            objName = getMeshName(objparent["filename"])
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
        print("\n\nSaving Blueprint Data to a file...")
        props = bpy.context.scene.StarCitizenExporterPreferences
        self.CollectionsToExport = []
        object = context.object
        if (not object):
            print("\nNo Object selected. Unable to save file.")
            return {'FINISHED'}
            
        if ("filename" in object):
            props.asset_path = object["filename"].rsplit('/', maxsplit=1)[0]
            
        orig_assetPath = props.asset_path            
        objName = object.name
        
        print("orig_assetPath: %s" % orig_assetPath)

        self.writeBlueprintFile(objName, object)
        
        if len(self.CollectionsToExport) > 0:
            print("We have Collections to Export!")
            for collectionName in self.CollectionsToExport:
                print("Attempting to Write BP file for %s" % (collectionName))
                topItem = bpy.data.collections[collectionName].objects[0]
                
                if "source_file" in topItem:
                    props.asset_path = topItem["source_file"].rsplit('/', maxsplit=1)[0]
                    
                objName = topItem.name
                if ("filename" in topItem):
                    objName = getMeshName(topItem["filename"])
                if ("orig_name" in topItem):
                    objName = SanitizeName(topItem["orig_name"])
                objName = SanitizeName(objName)
            
                self.writeBlueprintFile(objName, topItem)
                
            props.asset_path = orig_assetPath
            self.CollectionsToExport = []
                
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(exportBlueprint)

def unregister():
    bpy.utils.unregister_class(exportBlueprint)
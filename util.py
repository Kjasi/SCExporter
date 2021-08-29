import bpy
import re
import os

def SanitizeName(inputstring):
    newstring = inputstring
    
    # Remove .xxx from the end of the string
    match = re.search("(.+)\.[0-9]{3}$", inputstring)
    #print("String: %s VS Match: %s" % (inputstring, match))
    if (match != None):
        newstring = match[1];
        
    # Basic string cleaning for Unreal Engine
    if (newstring.find("\\") > -1):
        newstring = newstring.split("\\")[1]
    newstring = newstring.replace("(", "_")
    newstring = newstring.replace(")", "_")
    newstring = newstring.replace(":", "_")
    newstring = newstring.replace(".", "_")
    newstring = newstring.replace("__", "_")
    
    return newstring

def getChildren(myObject):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == myObject:
            children.append(ob)
    return children
    
    
def getOutputFolder(itemName):
    props = bpy.context.scene.StarCitizenExporterPreferences
    outputFolder = props.output_path
    print("outputFolder = Ouput_Path: %s" % outputFolder)
    if (outputFolder == ""):
        outputFolder = os.path.split(bpy.data.filepath)[0];

    if (outputFolder == ""):
        print("\nCouldn't get output path. Unable to save file.")
        return

    if (props.asset_path != ""):
        print("Adjust folder with Asset Path: %s" % props.asset_path)
        outputFolder = os.path.join(outputFolder, props.asset_path)
        
    ObjFileName = SanitizeName(itemName)
    while (ObjFileName[-1] == "_"):
        ObjFileName = ObjFileName[:-1]
        
    # Check for default asset path
    if outputFolder == os.path.join(props.output_path, "Objects/"):
        outputFolder = os.path.join(outputFolder, SanitizeName(ObjFileName))
        
    if outputFolder[-1] != "/":
        outputFolder += "/"
        
    outputFolder = outputFolder.replace("//", "/")

    return outputFolder
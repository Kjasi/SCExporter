
# Star Citizen Exporter

The Star Citizen Exporter (or SCExporter for short) is a set of tools designed to help export Star Citizen models from Blender into other 3D software, and even game engines, while trying to retain Star Citizen's folder structure, with only a few button presses.

# How to use it

Extensive guide coming later. Basically: install, open panel, set preferences, select the top-level object you want to export, press the buttons.

# Export Support

The program will exports the selected hierarchy's models as FBX files. (Version determined by Blender's FBX exporter.)

## Specific Support

### Unreal Engine

 * Exports a text file that you can copy & paste into an actor blueprint for a fully-built object tree.

# Software Notes

## Blender

While written for 2.93, most 2.8+ Blender versions should be supported. Blender 3.0 support is not yet tested.

## Star Citizen Data Viewer

This plugin is written to take advantage of models imported with the [SCDV](https://gitlab.com/scmodding/tools/scdv) program. While this greatly helps with retaining folder structure, models without this data will also be supported, but without the in-depth folder structure. (A future patch may change this.)

# Installation

Installation guide coming later, with installation support.

# F.A.Q.

> __Q__: Does this HAVE to work with Star Citizen?
> 
> __A__: No, it should work with any Blender hierarchy. However, it was built specifically for Star Citizen, so there might be some things that it does that's specific to Star Citizen.

> __Q__: Why did you make this?
> 
> __A__: To easily export Star Citizen models from Blender into Unreal Engine. Although other software support will be added later.

> __Q__: What other software will this export to?
> 
> __A__: At the moment, only Unity support is planned, but others may come too.

> __Q__: What about software X?
> 
> __A__: I'm not currently taking requests. Let me get out what I have planned, and then we'll see.

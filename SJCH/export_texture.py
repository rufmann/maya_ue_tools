import sys

import maya.standalone as ms

"""
Usage /path/to/mayapy -c "/path/to/export_texture.py /path/to/rig.ma" 
"""
scene_file_path = sys.argv[1]

ms.initialize()
import maya.cmds as cmds

print(f"*****Opening maya scene file {scene_file_path}*****")
maya_scene_file = cmds.file(scene_file_path, open=True)

import repath_texture
import tex_to_ue

repath_texture
tex_to_ue


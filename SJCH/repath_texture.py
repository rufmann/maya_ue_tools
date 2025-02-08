import os
import re

import maya.cmds as cmds

print("\n\n*****Repath texture files*****")
scene_path = cmds.file(query=True, sceneName=True)
root_path = '/'.join(scene_path.split('/')[:4])
pattern = r"^(.*?)(?=/Maps)"

tex_files = cmds.ls(type='file')
for tex in tex_files:
    tex_path = cmds.getAttr(f"{tex}.fileTextureName")
    match = re.match(pattern, tex_path)
    if match:
        new_path = re.sub(pattern, root_path, tex_path)
        if not os.path.exists(new_path):
            try:
                file_name, ext = os.path.splitext(os.path.basename(new_path))
                match_file = [f for f in os.listdir(os.path.dirname(new_path)) if file_name in f][0]
                new_path = os.path.join(os.path.dirname(new_path), match_file)
            except:
                print(f"Texture {new_path} not found. Need to relink texture manually")
        cmds.setAttr(f"{tex}.fileTextureName", new_path, type="string")
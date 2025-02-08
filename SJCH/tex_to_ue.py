import os
import re
import json
import maya.cmds as cmds

print("\n\n*****Preparing textures for FBX export*****")
if cmds.pluginInfo("fbxmaya", query=True, loaded=True):
    print("FBX plugin is already loaded")
else:
    cmds.loadPlugin("fbxmaya")
    print("FBX plugin loaded successfully")

tex_dict = dict()
texture_nodes = [tex for tex in cmds.ls(tex=True)]

scene_path = cmds.file(query=True, sceneName=True)
scene_name = os.path.basename(scene_path)
asset_root_path = os.path.dirname(os.path.dirname(scene_path.replace("/", os.sep)))
filename, ext = os.path.splitext(scene_name)
fbx_export_path = os.path.join(asset_root_path, "FBX_Export", ".".join([filename, "fbx"]))
if not os.path.exists(os.path.dirname(fbx_export_path)):
    os.makedirs(os.path.dirname(fbx_export_path))

# tex_path = os.path.dirname(scene_path).replace('Rig', 'Maps')
asset_name = re.match(r"^(.*?)(?=_Rig)", scene_name).group()

# write textures info
for node in texture_nodes:
    layered = False
    if 'layered' in node :
        texture_files = cmds.listConnections(node + ".inputs")
        texture_paths = [cmds.getAttr(tex + ".fileTextureName") for tex in texture_files]
        if len(texture_paths) > 1:
            layered= True
    else:
        if 'ramp' in node:
            continue
        texture_paths = [cmds.getAttr(node + ".fileTextureName")]
    materials = cmds.listConnections(node + ".outColor") or []  # point of reference for ue material
    if texture_paths:
        tex_dict[node] = {'texture_paths': texture_paths, 'layered': layered, 'materials': materials}

print("Writing texture paths to json file")
if os.path.exists(asset_root_path):
    tex_json_file = os.sep.join([asset_root_path, "FBX_Export", f"{asset_name}_textures.json"])
    json_obj = json.dumps(tex_dict, indent=4)
    if os.path.exists(tex_json_file):
        os.remove(tex_json_file)
    with open(tex_json_file, "w") as tex_json:
        tex_json.write(json_obj)

print("Converting any nurbs curves into mesh")
# convert any nurbs curves into mesh
root_geo = 'renderGeo_ITGP'
cmds.select(cl=True)
cmds.select(root_geo)
for nurbs_surface in cmds.listRelatives(allDescendents=True, type='nurbsSurface'):
    if 'Orig' not in nurbs_surface:
        print(f"{nurbs_surface} is a nurbsSurface. Converting to mesh")
        nurbs_surface_path = cmds.ls(nurbs_surface, long=True)[0]
        top_grp = cmds.listRelatives(cmds.listRelatives(nurbs_surface_path, parent=True, fullPath=True)[0], parent=True,
                                     fullPath=True)[0]
        cmds.select(cl=True)
        cmds.select(nurbs_surface)
        mesh = cmds.nurbsToPoly(nurbs_surface, ch=0, f=3, pt=1, mnd=1, mel=1, un=1, vn=1, ft=0.01, ut=0, vt=0, d=3,
                                n=nurbs_surface.replace('Shape', ''))
        cmds.polyClean(mesh)
        cmds.polySmooth(mesh, ch=0, dv=1, kb=0, peh=1)
        cmds.delete(mesh, constructionHistory=True)

        cmds.delete(cmds.listRelatives(nurbs_surface_path, parent=True, fullPath=True)[0])
        cmds.parent(mesh[0], top_grp)


# export fbx
print("Exporting FBX")
# ensure fbx plugin is loaded
if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
    cmds.loadPlugin('fbxmaya')

# fbx settings
cmds.FBXExportAxisConversionMethod('none')
cmds.FBXExportCameras('-v', False)
cmds.FBXExportLights('-v', False)
cmds.FBXExportSkins('-v', True)
cmds.FBXExportShapes('-v', True)
cmds.FBXExportInputConnections('-v', True)
cmds.FBXExportInstances('-v', False)
cmds.FBXExportReferencedAssetsContent('-v', True)
cmds.FBXExportSmoothingGroups('-v', True)
cmds.FBXExportSmoothMesh('-v', True)
cmds.FBXExportTangents('-v', True)
cmds.FBXExportSmoothingGroups('-v', True)
cmds.FBXExportHardEdges('-v', False)
cmds.FBXExportInAscii('-v', False)
cmds.FBXExportConstraints('-v', False)
cmds.FBXExportAnimationOnly('-v', False)
# cmds.FBXExportEmbeddedTextures('-v', True)
cmds.FBXExportFileVersion('-v', 'FBX202000')
cmds.FBXExportUpAxis('y')

# duplicate meshes before export
root_geo_obj = cmds.ls(root_geo)
meshes = [mesh for mesh in cmds.listRelatives(root_geo_obj, allDescendents=True, type='mesh') if 'Orig' not in mesh]
cmds.select(cl=True)
cmds.select(meshes)

# duplicate meshes
dupe_meshes = list()
for mesh in meshes:
    parent_obj = cmds.listRelatives(mesh, parent=True)[0]
    if cmds.getAttr(f"{parent_obj}.visibility"):
        dupe_mesh = cmds.duplicate(mesh, name=f"{mesh}_duplicate")[0]
        cmds.parent(dupe_mesh, world=True)
        dupe_mesh = cmds.rename(dupe_mesh, parent_obj)
        dupe_meshes.append(cmds.ls(dupe_mesh, long=True)[0])
cmds.select(cl=True)
cmds.select(dupe_meshes)
# cmds.file(fbx_export_path, force=True, options="v=0;", type="FBX Export", exportSelected=True)
cmds.FBXExport('-f', fbx_export_path, '-s')
print(f"\n\nSuccess! {asset_name} exported to {fbx_export_path}")

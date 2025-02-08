import os.path
import sys
import unreal
from pathlib import Path

src_path = sys.argv[1]
fbx_assets = list(Path(src_path).glob("*.fbx"))
game_path = f"/Game"
texture_path = f"{game_path}/Textures"
mesh_path = f"{game_path}/Meshes"
print(fbx_assets)

# import data settings
static_mesh_import_data = unreal.FbxStaticMeshImportData()
static_mesh_import_data.combine_meshes = True
static_mesh_import_data.remove_degenerates = True  # prevent importing objects that has issues with vertices/polygons

# FBX import options
options = unreal.FbxImportUI()
options.import_animations = False
options.import_as_skeletal = False
options.import_mesh = True
options.import_materials = True
options.import_textures = False
options.import_rigid_mesh = False
options.automated_import_should_detect_type = True
options.static_mesh_import_data = static_mesh_import_data

# for unreal we need to construct tasks and then pass the task to AssetTools
tasks: list[unreal.AssetImportTask] = []
unreal.Array.cast(unreal.AssetImportTask, tasks)  # casting list to unreal.Array data type, good for avoiding unwanted errors

for asset in fbx_assets:
    task = unreal.AssetImportTask()
    task.automated = True
    dst_path = f"{game_path}/{str(asset.stem)}"
    task.destination_path = dst_path
    task.destination_name = str(asset.stem)  # stem function returns the name
    task.filename = str(asset)  # unreal.AssetImportTask().filename resolves the file path
    task.replace_existing = True
    task.save = True  # this will save the meshes upon importing
    task.options = options

    tasks.append(task)

# pass tasks to AssetTools object
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.import_asset_tasks(tasks)

# for task in tasks:
#     for path in task.import_objects_paths:
#         print(f"[Import Task] Imported {path}")
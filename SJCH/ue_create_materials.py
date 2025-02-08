import os
import sys
import json
import unreal  # type:ignore

"""
TextureSampleA(RGB) > Blend_Screen(Blend(V3))
TextureSampleB(RGB) > Multiply(A)
ScalarParam(0, value=0.5) > Multiply(B)
Multiply(0) > Blend_Screen(Base(V3))
Blend_Screen(Result) > MaterialProperty.MP_BASE_COLOR
"""


# read json file
# if layered_material true
# create a material
# for each texture path, create texture sample
# assemble material graph according to template above

def connect_material_expression(from_expression, from_output_name, to_expression, to_input_name):
    unreal.MaterialEditingLibrary.connect_material_expression(from_expression=from_expression,
                                                              from_output_name=from_output_name,
                                                              to_expression=to_expression,
                                                              to_input_name=to_input_name)


def create_material_blueprint(json_file_path):
    with open(json_file_path) as json_file:
        material_data = json.load(json_file)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_name = os.path.basename(json_file_path).rstrip("_textures.json")
    for material_name, material_info in material_data.items():
        # Create material
        material_path = f"/Game/{asset_name}"
        material_asset = asset_tools.create_asset(material_name, material_path, unreal.Material,
                                                  unreal.MaterialFactoryNew())

        for path in material_info.get('texture_paths'):
            texture_path, ext = os.path.splitext(path)
            texture_name = os.path.basename(texture_path)
            # create TextureSample nodes
            texture_node = unreal.MaterialEditingLibrary.create_material_expression(material_asset, unreal.MaterialExpressionTextureSample)
            texture_asset = unreal.load_asset(f"/Game/{asset_name}_Rig/{texture_name}")
            print(texture_asset)
            texture_node.set_editor_property("Texture", texture_asset)
            print(texture_node)
            if material_info.get('layered'):
                # create Blend_Screen node
                blend_screen_node = unreal.MaterialEditingLibrary.create_material_expression(material_asset,
                                                                                             unreal.MaterialExpressionBlendScreen)
                # create Multiply node
                multiply_node = unreal.MaterialEditingLibrary.create_material_expression(material_asset,
                                                                                         unreal.MaterialEditingLibraryMultiply)
                # create ScalarParam node
                param_node = unreal.MaterialEditingLibrary.create_material_expression(material_asset,
                                                                                      unreal.MaterialEditingLibraryScalarParam)
                param_node.set_editor_property("value", 0.5)

                # connect nodes
                tex_sample_nodes = [node for node in unreal.MaterialEditingLibrary.get_material_expressions]  # ???

                connect_material_expression(tex_sample_nodes[0], "RBG", blend_screen_node, "Blend(V3)")
                connect_material_expression(tex_sample_nodes[1], "RGB", multiply_node, "A")
                connect_material_expression(param_node, "", multiply_node, "B")
                connect_material_expression(multiply_node, "", blend_screen_node, "Base(V3)")
                unreal.MaterialEditingLibrary.connect_material_property(from_expression=blend_screen_node, from_output_name="Result", property_=unreal.MaterialProperty.MP_BASE_COLOR)
            else:
                unreal.MaterialEditingLibrary.connect_material_property(from_expression=texture_node, from_ouput_name="RGB", property_=unreal.MaterialProperty.MP_BASE_COLOR)

        unreal.MaterialEditingLibrary.layout_material_expression(material_asset)
        unreal.MaterialEditingLibrary.recompile(material_asset)
        unreal.EditorAssetLibrary.save_asset(f"{material_path}/{material_name}")
        print(f"Material f{material_path}/{material_name} created successfully")


if __name__ == "__main__":
    # need to import all textures
    json_file_path = sys.argv[1]
    create_material_blueprint(json_file_path)
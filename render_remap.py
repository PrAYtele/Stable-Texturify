import bpy
import math
import numpy as np
from mathutils import Quaternion, Vector
import os
import cv2
import sys
import addon_utils
import bmesh
from PIL import Image,ImageDraw
from bpy_extras import mesh_utils
import yaml
# Convert Euler angles to Quaternion

with open("Render_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 从配置中提取参数
fbx_model_path = config["fbx_model_path"]
output_folder = config['output_folder']
# textures_paths = config["textures"]
resolution_width = config["resolution"]["width"]
resolution_height = config["resolution"]["height"]
offset_angle = config["camera"]["side_angle"]
camera_views = config["camera"]["view"]
camera_distance = config["camera"]["distance"]

random_color_flag = config["seg_node"]["random_color"]
textures_path = config["textures"]
project_order = config["project_order"]

# Delete all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

if fbx_model_path.endswith('vrm'):
    bpy.ops.import_scene.vrm(filepath=fbx_model_path)
if fbx_model_path.endswith('fbx'):
    bpy.ops.import_scene.fbx(filepath=fbx_model_path)
elif fbx_model_path.endswith('obj'):
    bpy.ops.import_scene.obj(filepath=fbx_model_path)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
    bpy.ops.object.location_clear()
    camera_distance *= 1.5

        # Load the exported binary UV layout and set it as the active image for the UV editor
        # binary_uv_layout = bpy.data.images.load(filepath=os.path.join(output_folder, "binary_uv_layout.png"))
        # for area in bpy.context.screen.areas:
        #     if area.type == 'IMAGE_EDITOR':
        #         for space in area.spaces:
        #             if space.type == 'IMAGE_EDITOR':
        #                 space.image = binary_uv_layout
        #                 break

material_name = "ModelMaterial"
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and 'face' not in obj.name.lower():
        bpy.context.view_layer.objects.active = obj

        obj.select_set(True)
        if len(obj.data.materials) > 2:
            obj.active_material_index = 2
        else:
            obj.active_material_index = 0
        material = obj.data.materials[obj.active_material_index]
        break

# Set up the material nodes
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create required nodes
image_node = nodes.new('ShaderNodeTexImage')
bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
output_node = nodes.new('ShaderNodeOutputMaterial')

# Set node positions
image_node.location = (-400, 300)
bsdf_node.location = (-200, 300)
output_node.location = (0, 300)

# Connect nodes
links.new(image_node.outputs['Color'], bsdf_node.inputs['Base Color'])
links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])




output_texture_path = os.path.join(output_folder, "Tex_sres_0.png")

saved_texture = bpy.data.images.load(filepath=output_texture_path)
image_node.image = saved_texture
output_fbx_path = os.path.join(output_folder, "model_with_texture_remap.fbx")
# Enable the FBX addon
# Enable the FBX add
# Export the scene as an FBX file
bpy.ops.export_scene.fbx(
    filepath=output_fbx_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    bake_space_transform=False,
    object_types={'MESH', 'ARMATURE'},
    use_mesh_modifiers=True,
    use_armature_deform_only=True,
    add_leaf_bones=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=1.0,
    path_mode='COPY',
    batch_mode='OFF',
    embed_textures = True,
    use_batch_own_dir=True,
    use_metadata=True
)
bpy.ops.wm.quit_blender()
sys.exit()

# Reset the 3D view mode
# area.ui_type = 'VIEW'
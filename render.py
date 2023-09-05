import bpy
import math
import numpy as np
import sys
from mathutils import Quaternion, Vector
import os
import cv2
import bmesh
from PIL import Image,ImageDraw
from bpy_extras import mesh_utils
import yaml
# Convert Euler angles to Quaternion
def get_model_dimensions():
    min_coords = [float('inf')] * 3
    max_coords = [float('-inf')] * 3

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for vertex in obj.data.vertices:
                world_vertex = obj.matrix_world @ vertex.co
                min_coords = [min(min_coords[i], world_vertex[i]) for i in range(3)]
                max_coords = [max(max_coords[i], world_vertex[i]) for i in range(3)]

    dimensions = [max_coords[i] - min_coords[i] for i in range(3)]
    return Vector(dimensions)
def euler_to_quaternion(angles):
    x, y, z = angles
    qx = Quaternion((math.cos(x / 2), math.sin(x / 2), 0, 0))
    qy = Quaternion((math.cos(y / 2), 0, math.sin(y / 2), 0))
    qz = Quaternion((math.cos(z / 2), 0, 0, math.sin(z / 2)))
    return qx * qy * qz

# Create and set active camera
def create_and_set_active_camera(view, model_center, camera_distance=3,offset=20):
    # Create a new camera data block
    camera_data = bpy.data.cameras.new("Camera")

    # Create a new camera object and link it to the scene's collection
    camera = bpy.data.objects.new("Camera", camera_data)
    bpy.context.scene.collection.objects.link(camera)

    # Set the new camera as the active camera
    bpy.context.scene.camera = camera

    angle = math.radians(20)  # 45-degree angle in radians


    if view == 'front':
        camera.location.x = model_center.x 
        camera.location.y = model_center.y - camera_distance
        camera.location.z = model_center.z
    elif view == 'back':
        camera.location.x = model_center.x
        camera.location.y = model_center.y + camera_distance
        camera.location.z = model_center.z
    elif view == 'left':
        angle = math.radians(-offset)
        camera.location.x = model_center.x + camera_distance * math.sin(angle)
        camera.location.y = model_center.y - camera_distance * math.cos(angle)
        camera.location.z = model_center.z
    elif view == 'right':
        angle = math.radians(offset)  # 20-degree angle in radians
        camera.location.x = model_center.x + camera_distance * math.sin(angle)
        camera.location.y = model_center.y - camera_distance * math.cos(angle)
        camera.location.z = model_center.z

    # Set the camera to face the model
    direction = model_center - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

    return camera

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
# Create a new binary image for the UV layout
binary_uv_image_name = "Binary_UV_Layout"
bpy.ops.image.new(name=binary_uv_image_name, width=4096, height=4096, color=(0.0, 0.0, 0.0, 1.0), alpha=True, generated_type='BLANK', float=True)
binary_uv_image = bpy.data.images[binary_uv_image_name]

# Export the UV layout as a binary image
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        # Create a bmesh object from the mesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Create a new UV layer if it doesn't exist
        if not bm.loops.layers.uv:
            bm.loops.layers.uv.new()

        # Get the active UV layer
        uv_layer = bm.loops.layers.uv.active

        # Create a new PIL image
        img = Image.new('RGB', (4096, 4096), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        img2 = Image.new('RGB', (4096, 4096), (0, 0, 0))
        draw2 = ImageDraw.Draw(img2)
        # Draw the UV layout
        for face in bm.faces:
            for loop in face.loops:
                uv = loop[uv_layer].uv
                if loop.link_loop_next is not None:
                    next_uv = loop.link_loop_next[uv_layer].uv
                    draw.line([(uv.x * 4096, (1 - uv.y) * 4096), (next_uv.x * 4096, (1 - next_uv.y) * 4096)], fill=(255, 255, 255), width=1)
        for face in bm.faces:
            uv_coordinates = []
            for loop in face.loops:
                uv = loop[uv_layer].uv
                uv_coordinates.append((uv.x * 4096, (1 - uv.y) * 4096))
            draw2.polygon(uv_coordinates, fill=(255, 255, 255), outline=(255, 255, 255))
        # Save the binary UV layout
        img.save(os.path.join(output_folder, "binary_uv.png"))
        img2.save(os.path.join(output_folder, "binary_uv_layout.png"))

        # Load the exported binary UV layout and set it as the active image for the UV editor
        # binary_uv_layout = bpy.data.images.load(filepath=os.path.join(output_folder, "binary_uv_layout.png"))
        # for area in bpy.context.screen.areas:
        #     if area.type == 'IMAGE_EDITOR':
        #         for space in area.spaces:
        #             if space.type == 'IMAGE_EDITOR':
        #                 space.image = binary_uv_layout
        #                 break
# 计算模型尺寸
model_dimensions = get_model_dimensions()
max_dimension = max(model_dimensions)

# 根据模型最大尺寸调整相机距离
adjusted_camera_distance = max_dimension * camera_distance

# 替换原有的相机距离
camera_distance = adjusted_camera_distance
# Load the textures
textures = {
    'back': bpy.data.images.load(filepath=textures_path["back"]),
    'front': bpy.data.images.load(filepath=textures_path["front"]),
    'left': None,
    'right': None
}
# textures = {key: textures[key] for key in project_order}
# Create a new material
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

# bpy.ops.object.light_add(type='SPOT', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
# light = bpy.context.active_object
# light.data.energy = 100
# Connect nodes
links.new(image_node.outputs['Color'], bsdf_node.inputs['Base Color'])
links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
bsdf_node.inputs['Specular'].default_value = 0
# Add material to the model
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        break
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
model_center = bpy.context.active_object.location
if material_name not in bpy.context.object.data.materials:
    bpy.context.object.data.materials.append(material)

# Create a new texture map
texture_name = "ProjectedTexture"
bpy.ops.image.new(name=texture_name, width=4096, height=4096, color=(0.0, 0.0, 0.0, 1.0), alpha=True, generated_type='BLANK', float=True)
projected_texture = bpy.data.images[texture_name]

# Set the texture map to the material node
image_node.image = projected_texture

# Enable texture painting mode in the 3D view
area_3d_view = None
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area_3d_view = area
        break

if area_3d_view is not None:
    old_type = area_3d_view.type
    area_3d_view.type = 'VIEW_3D'
    override = bpy.context.copy()
    override['area'] = area_3d_view
    bpy.ops.object.mode_set(override, mode='TEXTURE_PAINT')
    area_3d_view.type = old_type

# Create a new texture slot for the paintbrush
paint = bpy.context.tool_settings.image_paint
paint.detect_data()

# Load and project texture images
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.resolution_x = 4096
bpy.context.scene.render.resolution_y = 4096

bpy.context.scene.view_settings.view_transform = 'Standard'
bpy.context.scene.view_settings.look = 'None'
bpy.context.scene.view_settings.exposure = 5  # 增加曝光度以提高亮度
bpy.context.scene.view_settings.gamma = 1.0

for view, texture_image in textures.items():
    active_camera = create_and_set_active_camera(view, model_center, camera_distance=camera_distance,offset=offset_angle)
    # 设置光源位置
    # light.location = active_camera.location

    # # 设置光源对准模型
    # direction = model_center - light.location
    # rot_quat = direction.to_track_quat('-Z', 'Y')
    # light.rotation_euler = rot_quat.to_euler()

    # Set the view direction
    if view == 'front':
        angle = (0, math.pi / 2, 0)
    elif view == 'back':
        angle = (0, -math.pi / 2, 0)
    elif view == 'left':
        angle = (0, math.pi / 2 + math.radians(-offset_angle), 0)
    elif view == 'right':
        angle = (0, math.pi / 2 + math.radians(offset_angle), 0)

    # Set the 3D view's perspective
    area.spaces[0].region_3d.view_rotation = euler_to_quaternion(angle)
    area.spaces[0].region_3d.view_distance = 2

    # Update the scene
    bpy.context.view_layer.update()

    # Project the texture
    if view =='front' or view =='back':
        texture_image.name = f"Texture_{view}"

        # Set the paintbrush texture
        paint.brush.texture = bpy.data.textures.new(texture_image.name, 'IMAGE')
        paint.brush.texture.image = texture_image
        bpy.ops.paint.project_image(image=texture_image.name)
    else:
       
        bpy.context.scene.render.filepath = os.path.join(output_folder, f"inpaint_{view}.png")

    # 渲染并保存线稿图
        bpy.ops.render.render(write_still=True)
    
output_texture_path = os.path.join(output_folder, "projected_texture.png")
projected_texture.filepath_raw = output_texture_path
projected_texture.file_format = 'PNG'
projected_texture.save()
saved_texture = bpy.data.images.load(filepath=output_texture_path)
image_node.image = saved_texture
output_fbx_path = os.path.join(output_folder, "model_with_texture.fbx")
bpy.ops.export_scene.fbx(filepath=output_fbx_path, use_selection=True, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', bake_space_transform=False, object_types={'MESH', 'ARMATURE'}, use_mesh_modifiers=True, use_armature_deform_only=True, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=True, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
bpy.ops.wm.quit_blender()
sys.exit()

# Reset the 3D view mode
# area.ui_type = 'VIEW'
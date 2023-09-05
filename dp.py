import bpy
import math
import numpy as np
from mathutils import Quaternion, Vector
import os
import cv2
import bpy_extras.view3d_utils
import yaml
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
# 从config.yaml文件中读取参数
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
map_offset = config["depth_node"]["map_value_node_offset"]
map_size = config["depth_node"]["map_value_node_size"]

# 指定FBX模型文件路径

# 删除所有现有的物体
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 导入FBX模型
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
bpy.ops.object.select_all(action='SELECT')
# 设置相机距离与模型最大尺寸的比例


# 计算模型尺寸
model_dimensions = get_model_dimensions()
max_dimension = max(model_dimensions)

# 根据模型最大尺寸调整相机距离
adjusted_camera_distance = max_dimension * camera_distance

# 替换原有的相机距离
camera_distance = adjusted_camera_distance

# 断开所有模型的贴图
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        for slot in obj.material_slots:
            slot.material.use_nodes = True
            nodes = slot.material.node_tree.nodes
            links = slot.material.node_tree.links

            # 查找Image Texture节点并断开
            for link in links:
                if link.from_node.type == 'TEX_IMAGE':
                    links.remove(link)
            nodes.clear()

            # 创建Diffuse BSDF节点和Material Output节点
            diffuse_node = nodes.new(type='ShaderNodeBsdfDiffuse')
            output_node = nodes.new(type='ShaderNodeOutputMaterial')

            # 设置Diffuse BSDF节点的颜色为白色
            diffuse_node.inputs[0].default_value = (1, 1, 1, 1)

            # 连接Diffuse BSDF节点和Material Output节点
            links.new(diffuse_node.outputs[0], output_node.inputs[0])

# 计算模型边界框中心
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        break
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
model_center = bpy.context.active_object.location




for view in camera_views:
    
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

    if view == 'front':
        camera.location.x = model_center.x
        camera.location.y = model_center.y - camera_distance
        camera.location.z = model_center.z
    elif view == 'back':
        camera.location.x = model_center.x
        camera.location.y = model_center.y + camera_distance
        camera.location.z = model_center.z
    elif view == 'left':
        angle = math.radians(-offset_angle)
        camera.location.x = model_center.x + camera_distance * math.sin(angle)
        camera.location.y = model_center.y - camera_distance * math.cos(angle)
        camera.location.z = model_center.z
    elif view == 'right':
        angle = math.radians(offset_angle)  # 45-degree angle in radians
        camera.location.x = model_center.x + camera_distance * math.sin(angle)
        camera.location.y = model_center.y - camera_distance * math.cos(angle)
        camera.location.z = model_center.z

    # 设置相机对准模型
    direction = model_center - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

    # 设置相机裁剪距离
    camera.data.clip_start = 0.1
    camera.data.clip_end = 100

    # 设置渲染输出路径
    bpy.context.scene.render.filepath = os.path.join(output_folder, f"depth_{view}.png")

    # 设置渲染引擎为Eevee
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    # 设置渲染分辨率
    bpy.context.scene.render.resolution_x = resolution_width
    bpy.context.scene.render.resolution_y = resolution_height
     # 设置深度通道
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # 清除所有节点
    for n in tree.nodes:
        tree.nodes.remove(n)

    # 创建节点
    render_layers_node = tree.nodes.new('CompositorNodeRLayers')
    file_output_node = tree.nodes.new('CompositorNodeOutputFile')
    normalize_node = tree.nodes.new('CompositorNodeNormalize')
    invert_node = tree.nodes.new('CompositorNodeInvert')
    map_value_node = tree.nodes.new('CompositorNodeMapValue')

    # 设置节点位置
    render_layers_node.location = 0, 0
    normalize_node.location = 200, 0
    invert_node.location = 400, 0
    map_value_node.location = 600, 0
    file_output_node.location = 800, 0

    # 链接节点
    links.new(render_layers_node.outputs['Depth'], normalize_node.inputs[0])
    links.new(normalize_node.outputs[0], invert_node.inputs[1])
    links.new(invert_node.outputs[0], map_value_node.inputs[0])
    links.new(map_value_node.outputs[0], file_output_node.inputs[0])

    # 设置输出路径
    file_output_node.base_path = output_folder
    file_output_node.file_slots[0].path = f"depth_{view}_"

    # 调整深度图颜色范围
    map_value_node.offset = [map_offset]
    map_value_node.size = [map_size]

    # 渲染并保存深度图
    bpy.ops.render.render(write_still=True)

    # 启用Freestyle
    bpy.context.scene.render.use_freestyle = True
    # 创建新的LineSet
    lineset = bpy.context.scene.view_layers[0].freestyle_settings.linesets.new("LineSet")

    # 设置LineSet的可见性
    # 设置Freestyle线条设置
    lineset.select_by_visibility = True
    lineset.visibility = 'VISIBLE'

   # 创建新的LineStyle
    linestyle = bpy.data.linestyles.new("LineStyle")
    lineset.linestyle = linestyle

    # 设置Freestyle线条颜色为白色
    linestyle.color = (1, 1, 1)
    linestyle.thickness = 200

    # 设置背景颜色为黑色
    bpy.context.scene.world.color = (1, 1, 1)
    # 设置透明背景
    bpy.context.scene.render.film_transparent = True

    # 设置Composite节点
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # 删除所有节点
    for node in tree.nodes:
        tree.nodes.remove(node)

    # 创建新节点
    render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
    composite_node = tree.nodes.new(type='CompositorNodeComposite')
    alpha_over_node = tree.nodes.new(type='CompositorNodeAlphaOver')

    # 设置节点位置
    render_layers_node.location = (0, 0)
    composite_node.location = (400, 0)
    alpha_over_node.location = (200, 0)

    # 设置Alpha Over节点颜色为黑色
    alpha_over_node.inputs[1].default_value = (1, 1, 1, 1)

    # 连接节点
    links.new(render_layers_node.outputs['Image'], alpha_over_node.inputs[2])
    links.new(alpha_over_node.outputs['Image'], composite_node.inputs['Image'])

    # 设置输出路径
    bpy.context.scene.render.filepath = os.path.join(output_folder, f"lineart_{view}.png")

    # 渲染并保存线稿图
    bpy.ops.render.render(write_still=True)
    

    # 删除当前相机
    # bpy.ops.object.select_all(action='DESELECT')
    # camera.select_set(True)
    # bpy.ops.object.delete()
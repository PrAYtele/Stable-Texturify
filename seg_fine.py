import bpy
import os
import random
import math
from mathutils import Vector
import yaml
def random_color():
    return random.random(), random.random(), random.random()
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

def create_pure_color_image(color, width=16, height=16):
    image = bpy.data.images.new("PureColor", width=width, height=height)
    pixels = [color[0], color[1], color[2], 1] * (width * height)
    image.pixels = pixels
    return image

def set_pure_color_for_textures(obj):
    for slot in obj.material_slots:
        if slot.material:
            mat = slot.material
            if mat.use_nodes:
                nodes = mat.node_tree.nodes
                for node in nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        color_image = create_pure_color_image(random_color())
                        node.image = color_image

def set_camera_view(view, model_center, camera_distance,offset):
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
        angle = math.radians(-offset)
        camera.location.x = model_center.x + camera_distance * math.sin(angle)
        camera.location.y = model_center.y - camera_distance * math.cos(angle)
        camera.location.z = model_center.z
    elif view == 'right':
        angle = math.radians(offset)  # 20-degree angle in radians
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

random_color_flag = config["seg_node"]["random_color"]



# 删除所有现有的物体
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
# 计算模型尺寸
model_dimensions = get_model_dimensions()
max_dimension = max(model_dimensions)

# 根据模型最大尺寸调整相机距离
adjusted_camera_distance = max_dimension * camera_distance

# 替换原有的相机距离
camera_distance = adjusted_camera_distance
# 计算模型边界框中心
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        break
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
model_center = bpy.context.active_object.location
# 为模型的每个部分分配随机颜色

# Change materials to random colors
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        set_pure_color_for_textures(obj)

# 设置渲染引擎为Cycles
bpy.context.scene.render.engine = 'CYCLES'

# 关闭阴影、散射和反射效果
bpy.context.scene.cycles.use_animated_seed = False
bpy.context.scene.cycles.samples = 1
bpy.context.scene.cycles.use_square_samples = False
bpy.context.scene.cycles.caustics_reflective = False
bpy.context.scene.cycles.caustics_refractive = False
bpy.context.scene.cycles.blur_glossy = 0
bpy.context.scene.cycles.sample_clamp_direct = 0
bpy.context.scene.cycles.sample_clamp_indirect = 0

# 设置输出路径和文件格式
bpy.context.scene.render.image_settings.file_format = 'PNG'

# 渲染不同视图的图像
for view in camera_views:
    set_camera_view(view, model_center, camera_distance,offset_angle)
    bpy.context.scene.render.resolution_x = resolution_width
    bpy.context.scene.render.resolution_y = resolution_height
    bpy.context.scene.render.filepath = os.path.join(output_folder, f"seg_{view}.png")
    bpy.ops.render.render(write_still=True)
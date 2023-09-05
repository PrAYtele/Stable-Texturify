import base64
import io
import cv2
import json
import requests
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter as scipy_gaussian_filter
import yaml
def image_to_base64(image_path):
    with Image.open(image_path) as img:
        #img = img.resize((512, 512), Image.ANTIALIAS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

def base64_to_image(base64_data, output_path):
    img_data = base64.b64decode(base64_data)
    img = Image.open(io.BytesIO(img_data))
    img.save(output_path, format="PNG")
def cvmat_to_base64(image, file_format='.jpg'):

    # 将OpenCV图像（numpy数组）转换为PIL图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # 将PIL图像保存到内存中的字节缓冲区
    buffer = io.BytesIO()
    image_pil.save(buffer, format='JPEG')

    # 对缓冲区中的字节进行base64编码
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64
def find_contours(binary_img):
    # 查找轮廓
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours
def draw_circles(img, contours, radius,epsilon_factor=0.002):
    for cnt in contours:
        arc_length = cv2.arcLength(cnt, True)
        step_size = radius / 2

        # 计算在轮廓上绘制圆形的次数
        num_circles = int(arc_length / step_size)

        # 获取近似多边形
        epsilon = epsilon_factor * arc_length
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        for i in range(num_circles):
            # 计算当前点在近似多边形顶点上的索引
            index = (i * len(approx)) // num_circles
            point = approx[index][0]

            # 在原图上绘制圆形
            cv2.circle(img, tuple(point), radius, (255, 255, 255), -1)

def process_image(img):
    # Load the image

    # Create a mask for pixels with values (0, 0, 0) or (1, 1, 1)
    mask = np.logical_or(np.all(img == [0, 0, 0], axis=-1), np.all(img == [1, 1, 1], axis=-1))

    # Create a blank white image with the same dimensions as the input image
    output_image = np.ones_like(img) * 255

    # Set the corresponding pixels in the output image to (0, 0, 0) based on the mask
    output_image[mask] = [0, 0, 0]
    gray_output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY)
    gray_output_image = cv2.bitwise_not(gray_output_image)
    contours = find_contours(gray_output_image)

    # 用半径为R的圆形覆盖白色区域
    radius = 100
    draw_circles(gray_output_image, contours, radius)
    return gray_output_image
    #return cv2.cvtColor(output_image,cv2.COLOR_BGR2GRAY)
with open("Render_config.yaml", "r") as f:
    config = yaml.safe_load(f)
sd_model = config["sd_model_checkpoint"]
img_right = image_to_base64("inpaint_right.png")
img_left = image_to_base64("inpaint_left.png")

depth_right = image_to_base64('depth_right_0001.png')
depth_left = image_to_base64('depth_left_0001.png')

seg_left = image_to_base64('seg_left.png')
seg_right = image_to_base64('seg_right.png')

mask_right = process_image(cv2.imread("inpaint_right.png"))
mask_left = process_image(cv2.imread("inpaint_left.png"))
#cv2.namedWindow('sdf', cv2.WINDOW_NORMAL)
# mask_left = cv2.resize(mask_left,(512,512))
# mask_right = cv2.resize(mask_right,(512,512))
# mask_left = cv2.GaussianBlur(mask_left, (51, 51), 100)
# mask_left = cv2.GaussianBlur(mask_right, (51, 51), 100)

# cv2.imshow('sdf',mask_left)
# cv2.waitKey()
# cv2.imshow('sdf',mask_right)
# cv2.waitKey()

mask_right = cvmat_to_base64(mask_right)
mask_left = cvmat_to_base64(mask_left)
img_list = [img_right,img_left]
mask_list = [mask_right,mask_left]
depth_list = [depth_right,depth_left]
seg_list=[seg_right,seg_left]
url = "http://127.0.0.1:7860/sdapi/v1/img2img"
# model_list = requests.get("http://127.0.0.1:7860/sdapi/v1/sd-models")
# print(model_list.text)
for i,img in enumerate(img_list):
    data = {
        "init_images": [img],

        'prompt': 'fabric,texture',
        'negative_prompt': 'blur,motion blur,black,dark',
        'enable_hr': False,
        'resize_mode': 0,
        'mask':mask_list[i],
        'mask_blur':32,
        "inpainting_fill": 2,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 0,#used when only masked
        "inpainting_mask_invert": 0,
        'denoising_strength': 1,
        # 'hr_upscaler': 'Latent (bicubic)',
        # 'hr_scale': 1.0,
        'seed': -1,
        'sampler_name': 'Euler a',
        'batch_size': 1,
        'steps': 20,
        #'quick_steps': 20,
        'cfg_scale': 4,
        'width': 1920,
        'height': 1920,
        # 'override_settings': {'CLIP_stop_at_last_layers': 1},
        'override_settings': {'sd_model_checkpoint': sd_model},

        # 'override_settings_restore_afterwards': 'false',
        # 'hr_second_pass_steps': 20, 
    "alwayson_scripts": {
        "controlnet": {
        "args": [
            {
            "enabled":True,
            # "module":"tile_resample",
            "input_image": depth_list[i],
            "model": "control_v11f1p_sd15_depth",
            "resize_mode": 0,
            "processor_res":2048,
            "weight":1,
            # "threshold_a":1

            },
            {
            "enabled":True,
            "input_image": seg_list[i],
            # "module":'invert',
            "model": "control_v11p_sd15_seg",
                "resize_mode": 0,
                "processor_res":2048,
            "weight":0.6

            },
            {
            "enabled":False,
            "module":"tile_resample",
            "input_image": img,
            "model": "control_v11f1e_sd15_tile",
            "resize_mode": 0,
            "processor_res":2048,
            "weight":1,
            "threshold_a":1
            }
        ]
        }
    }
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print("Request was successful")
        response_data = response.json()
        output_image_path = "inpainted_{}.png"
        base64_to_image(response_data["images"][0], output_image_path.format(str(i)))
        print(f"Saved output image to {output_image_path.format(str(i))}")
    else:
        print(f"Request failed with status code {response.status_code}")
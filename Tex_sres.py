import base64
import io
import json
import requests
from PIL import Image

def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

def base64_to_image(base64_data, output_path):
    img_data = base64.b64decode(base64_data)
    img = Image.open(io.BytesIO(img_data))
    img.save(output_path, format="PNG")


img1 = image_to_base64("tex_tile_0.png")

img_list = [img1]
url = "http://127.0.0.1:7860/sdapi/v1/extra-single-image"
for i,img in enumerate(img_list):
    data = {
    "resize_mode": 1,
    "show_extras_results": False,
    "gfpgan_visibility": 0,
    "codeformer_visibility": 0,
    "codeformer_weight": 0,
    # "upscaling_resize": 0,#By how much to upscale the image, only used when resize_mode=0.
    "upscaling_resize_w": 4096,
    "upscaling_resize_h": 4096,
        "upscaling_crop": False,
        "upscaler_1": "4x-UltraSharp",
        # "upscaler_2": "4x-UltraSharp",
        # "extras_upscaler_2_visibility": 0.5,
        "upscale_first": False,
    "image": img
    }
    # data = {
    # "resize_mode": 0,
    # "show_extras_results": False,
    # "gfpgan_visibility": 0,
    # "codeformer_visibility": 0,
    # "codeformer_weight": 0,
    # "upscaling_resize": 1,
    # "upscaling_resize_w": 4096,
    # "upscaling_resize_h": 4096,
    # "upscaling_crop": False,
    # "upscaler_1": "SwinIR_4x",
    # "upscaler_2": "R-ESRGAN 4x+ Anime6B",
    # "extras_upscaler_2_visibility": 0.5,
    # "upscale_first": False,
    # "imageList": [
    # {
    #     "data": img1,
    #     "name": "C:\\Users\\y\\code\\ppainter\\restored_image_1.jpg"
    # }
    # ]
    # }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print("Request was successful")
        response_data = response.json()
        output_image_path = "Tex_sres_{}.png"
        base64_to_image(response_data["image"], output_image_path.format(str(i)))
        print(f"Saved output image to {output_image_path.format(str(i))}")
    else:
        print(f"Request failed with status code {response.status_code}")
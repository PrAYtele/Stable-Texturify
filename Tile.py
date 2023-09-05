import base64
import io
import json
import requests
from PIL import Image
import yaml
def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

def base64_to_image(base64_data, output_path):
    img_data = base64.b64decode(base64_data)
    img = Image.open(io.BytesIO(img_data))
    img.save(output_path, format="PNG")
with open("Render_config.yaml", "r") as f:
    config = yaml.safe_load(f)
sd_model = config["sd_model_checkpoint"]
img1 = image_to_base64("restored_image_1.jpg")
img2 = image_to_base64("restored_image_2.jpg")

img_list = [img1,img2]
url = "http://127.0.0.1:7860/sdapi/v1/img2img"
# model_list = requests.get("http://127.0.0.1:7860/sdapi/v1/sd-models")
# print(model_list.text)
for i,img in enumerate(img_list):
    data = {
        "init_images": [img],

        'prompt': 'masterpiece:1.2, best quality:1.4, (simple background, white background:1.3)',
        'negative_prompt': ' easynegative,((shadow)),((lighting)),blur,motion blur',
        'enable_hr': False,
        'denoising_strength': 0.3,
        # 'hr_upscaler': 'Latent (bicubic)',
        # 'hr_scale': 1.0,
        'seed': -1,
        'sampler_name': 'DPM++ 2M Karras',
        'batch_size': 1,
        'steps': 25,
        #'quick_steps': 20,
        'cfg_scale': 3,
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
            "module":"tile_resample",
            "input_image": img,
            "model": "control_v11f1e_sd15_tile",
            "resize_mode": 0,
            "processor_res":2048,
            "weight":1,
            "threshold_a":1

            },
            {
            "enabled":False,
            "input_image": img,
            "module":'invert',
            "model": "control_v11p_sd15s2_lineart_anime",
                "resize_mode": 0,
                "processor_res":4096,
            "weight":1.2

            },
            {
            "enabled":False,

            "input_image": None,
            "model": "none"
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
        output_image_path = "resample_{}.jpg"
        base64_to_image(response_data["images"][0], output_image_path.format(str(i)))
        print(f"Saved output image to {output_image_path.format(str(i))}")
    else:
        print(f"Request failed with status code {response.status_code}")
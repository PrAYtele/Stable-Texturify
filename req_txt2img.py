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

# 从配置中提取参数
dep_image_path = "concatenated_image.jpg"
lineart_image_path = "concatenated_lineart.jpg"
seg_image_path = "concatenated_seg.jpg"

encoded_image_depth = image_to_base64(dep_image_path)
encoded_image_lineart = image_to_base64(lineart_image_path)
encoded_image_seg = image_to_base64(seg_image_path)

url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
model_list = requests.get("http://127.0.0.1:7860/sdapi/v1/sd-models")
print(model_list.text)

data = {
    'prompt': '((highres)), (charturnerv2:0.7), (simple background:1.3), multiple views,((cloth)), <lora:charTurnBetaLora:0.1>',
    'negative_prompt': 'easynegative,(shadow:1.6),((lighting)),((naked)),((soft lighting)),fold',
    'enable_hr': False,
    #'denoising_strength': 1.0,
    # 'hr_upscaler': 'Latent (bicubic)',
    # 'hr_scale': 1.0,
    'seed': -1,
    'sampler_name': 'DPM++ 2M Karras',
    'batch_size': 1,
    'steps': 25,
    #'quick_steps': 20,
    'cfg_scale': 4,
    'width': 2016,
    'height': 896,
    # 'override_settings': {'CLIP_stop_at_last_layers': 1},
    'override_settings': {'sd_model_checkpoint': sd_model},

    # 'override_settings_restore_afterwards': 'false',
    # 'hr_second_pass_steps': 20, 
  "alwayson_scripts": {
    "controlnet": {
      "args": [
        {
        "enabled":True,

          "input_image": encoded_image_depth,
          "model": "control_v11f1p_sd15_depth",
          "resize_mode": 0,
          "processor_res":2048,
          "weight":0.8
        },
        {
        "enabled":True,
          "input_image": encoded_image_seg,
        #   "module":'invert',
          "model": "control_v11p_sd15_seg",
            "resize_mode": 0,
            "processor_res":2048,
        "weight":0.5
        },
        {
        "enabled":False,
          "input_image": encoded_image_lineart,
          "module":'invert',
          "model": "control_v11p_sd15_softedge",
            "resize_mode": 0,
            "processor_res":2048,
        "weight":0.1



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
    output_image_path = "output_image.png"
    base64_to_image(response_data["images"][0], output_image_path)
    print(f"Saved output image to {output_image_path}")
else:
    print(f"Request failed with status code {response.status_code}")
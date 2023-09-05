# Stable-Texturify
Create textures for 3d models using stable-diffusion  and blender

Certainly! Here's the README file in English using Markdown format:

# README

## Installation Requirements

To successfully use this project, you need to meet the following installation requirements:

1. **automatic1111 webui:** Ensure that you have installed automatic1111 webui. You can download it from the [official website](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and follow their installation instructions.

2. **controlnet:** Make sure you have controlnet installed. You can obtain it from the [GitHub repository](https://github.com/Mikubill/sd-webui-controlnet) and follow its installation documentation.

3. **Blender 2.93 with Python:** You need to install Blender version 2.93 and ensure it supports Python. You can download and install it from the [official Blender website](https://www.blender.org/download/).

## Usage

Using this project is straightforward; just follow these steps:

1. Pass the path to the model file you want to texture in the render config. It can be in .obj, .fbx, or .vrm format. For example:

   ```yaml
   render config:
     model_path: path/to/your/model
   ```

2. Configure Parameters: You can set parameters in the configuration file according to your requirements so that the project behaves as expected.
  
3. Make sure you have run sd-webui as ''--api'' mode.

4. Run run.sh: Execute the main script of the project, which will read your configuration and begin processing the model.

```bash
./run.sh
```

## Example

Here's an example configuration file that includes the model file path and some parameter settings:

```yaml
render config:
fbx_model_path: "./tmp.obj"
output_folder: './'
# textures:
#   back: "path/to/your/texture/back.png"
#   front: "path/to/your/texture/front.png"
#   left: "path/to/your/texture/left.png"
sd_model_checkpoint: 'darkSushi25D25D_v40.safetensors'
seg_node:
  random_color: True
depth_node:
  map_value_node_offset: 0.5
  map_value_node_size: 0.7
camera:
  view: ['back','front','left','right']
  distance: 1.5
  side_angle: 80
resolution:
  width: 1600
  height: 1600
textures: {
    back: "./Sres_0.png",
    front: "./Sres_1.png",
    left: "./Sres_2.png"
    # 'right': sides_image
}
inpaint_textures: {
    back: "./Sres_0_brinting.png",
    front: "./Sres_1_brinting.png",
    left: "./Sres_inpainted_1.png",
    right: "./Sres_inpainted_0.png"
}
project_order: ['back','front','left','right']
```
If you run it correctly, you will see the following intermediate files in the output directory

![concatenated_image](https://github.com/PrAYtele/Stable-Texturify/assets/49559621/c67b95d8-2b92-4eec-99c4-cb97c92169e6)
![output_image](https://github.com/PrAYtele/Stable-Texturify/assets/49559621/3529c533-e351-4568-8a56-038ce9bc1449)
Finally, you will get a model_with_texture_remap.fbx file

![QQ20230905-152311](https://github.com/PrAYtele/Stable-Texturify/assets/49559621/5537d452-6e08-4a9c-b10b-83e6e21ee6bb)
![QQ20230905-152331](https://github.com/PrAYtele/Stable-Texturify/assets/49559621/f99102a5-1fb4-4401-9fcf-db5bf6c2cb49)
## Help and Support

If you encounter any issues during installation or usage, please feel free to reach out to our support team at any time. You can also submit issues or request help on our [GitHub repository](https://github.com/PrAYtele/Stable-Texturify).

## License

This project is released under the [MIT License](LICENSE). Refer to the license file for more details.

Thank you for using our project! We hope you find it enjoyable to use!


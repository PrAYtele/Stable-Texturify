from PIL import Image, ImageEnhance

def enhance_brightness(image_path, factor):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(factor)
    return enhanced_image

inpaint_textures = {
    "back": "Sres_0.png",
    "front": "Sres_1.png"
}

brightness_factor = 1.2

for key, value in inpaint_textures.items():
    enhanced_image = enhance_brightness(value, brightness_factor)
    enhanced_image.save(value.replace(".png", "_brinting.png"))
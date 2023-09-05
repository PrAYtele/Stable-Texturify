from PIL import Image
import numpy as np

# 加载图像
image_a = Image.open("projected_texture_inpaint.png")
image_b = Image.open("projected_texture.png")

# 将图像转换为numpy数组

array_a = np.array(image_a)[..., :3]  # 仅保留RGB通道
array_b = np.array(image_b)[..., :3]  # 仅保留RGB通道
array_b = np.clip(array_b * 1.2, 0, 255).astype(np.uint8)

# 检查两个图像的形状是否相同
if array_a.shape != array_b.shape:
    raise ValueError("图像a和图像b的尺寸不相同")
# 计算图像a和图像b的像素总和
sum_a = np.sum(array_a, axis=-1)
sum_b = np.sum(array_b, axis=-1)

# 寻找满足条件的像素


# 计算图像a的RGB三个值的极差
range_a = np.max(array_a, axis=-1) - np.min(array_a, axis=-1)
pixels_to_replace = (sum_a >400) & (sum_b > 50) & (range_a <= 50)



# 将满足条件的像素替换为图像b中的对应像素
array_a[pixels_to_replace] = array_b[pixels_to_replace]

# 将替换后的数组转换回图像
result_image = Image.fromarray(array_a)

# 保存结果图像
result_image.save("tex_fusion.png")
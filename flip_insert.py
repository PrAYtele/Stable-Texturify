import cv2
import numpy as np

def process_images(a_path, b_path):
    a = cv2.imread(a_path, cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(b_path)

    if a.shape != b.shape[:2]:
        raise ValueError("两张图片的尺寸不一样")

    height, width = a.shape

    # 创建一个掩码，其中白色像素对应于a中的白色像素和b中的黑色像素
    mask = np.logical_and(a == 255, b.sum(axis=-1) == 0)

    # 计算中心点
    center_x = width // 2

    # 找到掩码中的所有白色像素坐标
    white_pixels_y, white_pixels_x = np.where(mask)

    # 计算对称像素的x坐标
    symm_pixels_x = center_x - (white_pixels_x - center_x)

    # 获取对称像素的颜色
    symm_pixels_colors = b[white_pixels_y, symm_pixels_x]

    # 检查对称像素是否为黑色
    black_symm_pixels = (symm_pixels_colors.sum(axis=-1) == 0)

    # 如果对称像素为黑色，则计算b中所有非黑色像素的均值
    if np.any(black_symm_pixels):
        b_non_black_pixels = b[b.sum(axis=-1) != 0]
        mean_color = b_non_black_pixels.mean(axis=0)

        # 将黑色对称像素设置为均值颜色
        symm_pixels_colors[black_symm_pixels] = mean_color

    # 将原始白色像素设置为对称像素的颜色
    b[white_pixels_y, white_pixels_x] = symm_pixels_colors

    return b
# 使用示例
result_img = process_images('binary_uv_layout.png', 'projected_texture.png')
cv2.imwrite('tex_fusion.png', result_img)
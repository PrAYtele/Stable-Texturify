import cv2
import numpy as np

def split_image(image, num_parts):
    width = image.shape[1]
    part_width = width // num_parts
    parts = []
    for i in range(num_parts):
        left = i * part_width
        right = (i + 1) * part_width if i < num_parts - 1 else width
        part = image[:, left:right]
        parts.append(part)
    return parts

def add_black_border(image, border_size=112):
    height, width = image.shape[:2]
    left_right = np.zeros((height, border_size, 3), dtype=np.uint8)
    image_with_border = cv2.hconcat([left_right, image, left_right])
    return image_with_border

if __name__ == "__main__":
    concatenated_image = cv2.imread('output_image.png')

    # 将拼接后的图片分割成三个部分
    split_images = split_image(concatenated_image, 3)

    # 为每个部分添加黑色边框
    restored_images = [add_black_border(img) for img in split_images]

    # 显示和保存恢复后的图片
    for i, img in enumerate(restored_images):
        #cv2.imshow(f'Restored Image {i + 1}', img)
        cv2.imwrite(f'restored_image_{i + 1}.jpg', img)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
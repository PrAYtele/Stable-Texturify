import cv2

def horizontal_concatenate(images):
    return cv2.hconcat(images)

def crop_image(image, border_size=200):
    height, width = image.shape[:2]
    cropped_image = image[0:height, border_size:width-border_size]
    return cropped_image

if __name__ == "__main__":
    # 读取四张图片
    image1 = cv2.imread('depth_back_0001.png')
    image2 = cv2.imread('depth_front_0001.png')
    image3 = cv2.imread('depth_left_0001.png')

    #裁剪每张图片的上下左右边框的200个像素
    cropped_image1 = crop_image(image1)
    cropped_image2 = crop_image(image2)
    cropped_image3 = crop_image(image3)
    # cropped_image4 = crop_image(image4)

    # 将四张图片水平拼接在一起
    concatenated_image = horizontal_concatenate([cropped_image1, cropped_image2,cropped_image3])

    # # 显示拼接后的图像
    # cv2.imshow('Concatenated Image', concatenated_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # # 保存拼接后的图像
    cv2.imwrite('concatenated_image.jpg', concatenated_image)
    image1 = cv2.imread('lineart_back.png')
    image2 = cv2.imread('lineart_front.png')
    image3 = cv2.imread('lineart_left.png')
    cropped_image1 = crop_image(image1)
    cropped_image2 = crop_image(image2)
    cropped_image3 = crop_image(image3)
    concatenated_image = horizontal_concatenate([cropped_image1, cropped_image2,cropped_image3])
    cv2.imwrite('concatenated_lineart.jpg', concatenated_image)
    image1 = cv2.imread('seg_back.png')
    image2 = cv2.imread('seg_front.png')
    image3 = cv2.imread('seg_left.png')
    cropped_image1 = crop_image(image1)
    cropped_image2 = crop_image(image2)
    cropped_image3 = crop_image(image3)
    concatenated_image = horizontal_concatenate([cropped_image1, cropped_image2,cropped_image3])
    cv2.imwrite('concatenated_seg.jpg', concatenated_image)

import os
import cv2
import numpy as np
from tqdm import tqdm


def calculate_image_statistics(image_folder):
    # 获取文件夹中所有图片文件的路径
    image_files = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.endswith(('.jpg', '.png', '.jpeg'))]

    if not image_files:
        print("文件夹中没有图片文件")
        return None

    # 初始化均值和标准差
    mean = np.zeros(3)
    std = np.zeros(3)
    total_images = len(image_files)

    for image_path in tqdm(image_files):
        # 读取图片
        img = cv2.imread(image_path)
        img = img

        # 计算均值和标准差
        mean += np.mean(img, axis=(0, 1))
        std += np.std(img, axis=(0, 1))

    # 计算平均值
    mean /= total_images
    std /= total_images

    return mean, std

if __name__ == "__main__":
    image_folder = "./images"  # 替换成你的图片文件夹路径
    mean, std = calculate_image_statistics(image_folder)

    if mean is not None:
        print("图片均值：", mean)
        print("图片标准差：", std)

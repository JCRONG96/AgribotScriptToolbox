import os, shutil, random
import numpy as np

postfix = 'jpg'  # 这里要注意下，文件夹里的图片格式要都是jpg，如果是PNG那就都得是PNG
base_path = './tomato'  # 转化完的图片和txt所在的文件夹
dataset_path = './coco'  # 新建一个文件夹
val_size, test_size = 0.2, 0.0  # 这里把test设置为0，也就是train：val = 9:1
# val_size = 0.1

os.makedirs(dataset_path, exist_ok=True)
os.makedirs(f'{dataset_path}/images', exist_ok=True)
os.makedirs(f'{dataset_path}/images/train', exist_ok=True)
os.makedirs(f'{dataset_path}/images/val', exist_ok=True)
os.makedirs(f'{dataset_path}/images/test', exist_ok=True)
os.makedirs(f'{dataset_path}/labels/train', exist_ok=True)
os.makedirs(f'{dataset_path}/labels/val', exist_ok=True)
os.makedirs(f'{dataset_path}/labels/test', exist_ok=True)

path_list = np.array([i.split('.')[0] for i in os.listdir(base_path) if 'txt' in i])
random.shuffle(path_list)
train_id = path_list[:int(len(path_list) * (1 - val_size - test_size))]
# train_id = path_list[:int(len(path_list) * (1 - val_size))]

# val_id = path_list[int(len(path_list) * (1 - val_size - test_size)):int(len(path_list) * (1 - test_size))]
val_id = path_list[int(len(path_list) * (1 - val_size - test_size)):int(len(path_list) * (1 - test_size))]
test_id = path_list[int(len(path_list) * (1 - test_size)):]

for i in train_id:
    shutil.copy(f'{base_path}/{i}.{postfix}', f'{dataset_path}/images/train/{i}.{postfix}')
    shutil.copy(f'{base_path}/{i}.txt', f'{dataset_path}/labels/train/{i}.txt')

for i in val_id:
    shutil.copy(f'{base_path}/{i}.{postfix}', f'{dataset_path}/images/val/{i}.{postfix}')
    shutil.copy(f'{base_path}/{i}.txt', f'{dataset_path}/labels/val/{i}.txt')

for i in test_id:
    shutil.copy(f'{base_path}/{i}.{postfix}', f'{dataset_path}/images/test/{i}.{postfix}')
    shutil.copy(f'{base_path}/{i}.txt', f'{dataset_path}/labels/test/{i}.txt')

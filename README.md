# 网络训练

## 1 训练YOLOv8-Seg 
### 1.1 数据集准备

[将labelme标注的json文件转化为txt文件](./data_convert_scripts/labelme2yolo.py)

[划分数据集](./data_convert_scripts/split_dataset.py)

### 1.2 训练
[可以参考这个文档](https://blog.csdn.net/m0_70140421/article/details/129052132)


# 硬件调试

## 1 睿尔曼机械臂调试

[问题梳理](./realman_robot_issues.md)

# 各类型相机使用教程

## 1 Intel RealSense

如果你使用 Intel RealSense 相机，你可以参考以下代码 

[代码和教程](./Image-Capture-With-RealSense/README_CN.md)

# ros

[ros主从机通讯](./ros_connect.md) 

[ros的IDE配置](./ros_vscode_config.md)

# 杂记
[git工具使用命令基础](./git_usage.md) 
[求解图片数据集中所有图片的颜色平均值和标准差](./calculate_mean_std_of_image/demo.py)

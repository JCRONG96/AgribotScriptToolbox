1.解决ros2中rclpy报错，不显示的问题

原因是使用了虚拟环境，IDE找不到部分环境：在vscode中打开设置，搜索**python.analysis.extra paths**；添加项选择添加'''/opt/ros/foxy/lib/python3.8/site-packages'''

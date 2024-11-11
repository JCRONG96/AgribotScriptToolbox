#! /home/rongjc/miniconda3/envs/robot/bin/python3
# -*- coding: utf-8 -*-

import pyrealsense2 as rs
import numpy as np
import os


class RealSense:
    
    def __init__(self, 
                 color_width: int = 1280,
                 color_height: int = 720,
                 color_fps: int = 30,
                 depth_width: int = 1024,
                 depth_height: int = 768,
                 depth_fps: int  =30,
                 preset: bool = True,  
                 n_serial: str = None,  
                 json_file: str = None,
                 conf_thresh: int = None,  # 1
                 noise_filtering: int = None,  # 4
                 auto_exposure: bool = False,
                 auto_white_balance: bool = False):
        
        self.color_width = color_width
        self.color_height = color_height
        self.color_fps = color_fps
        self.depth_width = depth_width
        self.depth_height = depth_height
        self.depth_fps = depth_fps
        self.preset = preset
        self.json_file = json_file
        self.n_serial = n_serial
        self.conf_thresh = conf_thresh
        self.noise_filtering = noise_filtering
        self.auto_exposure = auto_exposure
        self.auto_white_balance = auto_white_balance
        
        self._start_device()
        
    def _start_device(self):

        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # 打印设备信息
        ctx = rs.context()
        print("Devices found:")
        dev = None
        for d in ctx.query_devices():
            print(d.get_info(rs.camera_info.name), d.get_info(rs.camera_info.serial_number))
            a = rs.camera_info.serial_number
            if self.n_serial == d.get_info(rs.camera_info.serial_number):
                dev = d
                break
        if self.n_serial is not None:
            self.config.enable_device(self.n_serial)
        self.config.enable_stream(rs.stream.color, self.color_width, self.color_height, 
                                  rs.format.bgr8, self.color_fps)
        self.config.enable_stream(rs.stream.depth, self.depth_width, self.depth_height,
                                  rs.format.z16, self.depth_fps)
        profiel = self.config.resolve(self.pipeline)
        
        self.pipeline.start(self.config)
        
        # dev = self.find_device_that_supports_advanced_mode()
        if self.json_file is not None and dev is not None:
            ser_dev = rs.serializable_device(dev)
            with open(self.json_file, 'r') as f:
                json = f.read().strip()
                ser_dev.load_json(json)
        else:
            depth_sensor = profiel.get_device().first_depth_sensor()
            # rs.l500_visual_preset.short_range
            if self.preset:
                depth_sensor.set_option(rs.option.visual_preset, rs.l500_visual_preset.short_range) 
                # depth_sensor.set_option(rs.option.visual_preset, self.preset)       # 5 is short range, 3 is low ambient light
            if self.auto_exposure:
                depth_sensor.set_option(rs.option.enable_auto_exposure, 1)
            if self.auto_white_balance:
                depth_sensor.set_option(rs.option.enable_auto_white_balance, 1)
            if self.conf_thresh is not None:
                depth_sensor.set_option(rs.option.confidence_threshold, 1)          # 3 is max
            if self.noise_filtering is not None:
                depth_sensor.set_option(rs.option.noise_filtering, 4)               # 5 is max
        
        self.align = rs.align(rs.stream.color)
        
        self.pc = rs.pointcloud()
        
    def find_device_that_supports_advanced_mode(self) :
        ctx = rs.context()
        devices = ctx.query_devices()
        for dev in devices:
            if dev.supports(rs.camera_info.product_id):
                if dev.supports(rs.camera_info.name):
                    print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
                return dev
        raise Exception("No product line device that supports advanced mode was found")
    
    def get_frames(self):
        try:
            # get the color and depth frames
            frames = self.pipeline.wait_for_frames()
            # 创建一个空字典
            data = {}
            # align the color and depth frames
            aligned_frames = self.align.process(frames)
            # get the color and depth image
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            
            self.pc.map_to(color_frame)
            points = self.pc.calculate(depth_frame)
            
            if not color_frame or not depth_frame:
                return None
            # convert the color and depth images to numpy array
            color_image = np.asanyarray(color_frame.get_data())
            # depth_image = np.asanyarray(depth_frame.get_data())

            points = np.asanyarray(points.get_vertices()).view(np.float32).reshape(self.color_height, 
                                                                                   self.color_width,
                                                                                   3)
            data['color'] = color_image
            data['depth'] = points[:, :, 2]
            data['points'] = points
            
            return data
        except Exception as e:
            return None
    
    def stop(self):
        self.pipeline.stop()
    
    
if __name__ == "__main__":
    
    # rs = RealSense(depth_width=1280, depth_height=720, conf_thresh=None, preset=4)
    # 218622275888
    rs = RealSense(json_file="./src/robot_vision/robot_vision/cams/l515_config.json", n_serial='f1370188',conf_thresh=1, noise_filtering=4, preset=True)
    # rs = RealSense(conf_thresh=1, noise_filtering=4, preset=None)
    import cv2
    
    while True:
        data = rs.get_frames()
        if data is not None:
            print("color shape: ", data['color'].shape)
            
            print("depth shape: ", data['depth'].shape)
            print("points shape: ", data['points'].shape)
        
        cv2.imshow('color', data['color'])
        depth = data['depth']

        depth = cv2.convertScaleAbs(depth, alpha=round(255 / 1.2, 3))
        cv2.imshow('depth', depth)
        key = cv2.waitKey(1)
        if key == ord('s'):
            name = len(os.listdir(r'./calibrate_images/')) + 1
            cv2.imwrite("./calibrate_images/{}.jpg".format(name), data['color'])
        elif key == ord('q'):
            rs.stop()
            break
        
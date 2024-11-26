# -*- coding: utf-8 -*-

import os

import cv2
import numpy as np
import tensorrt as trt
from cuda import cudart

from src.common.tensorrt.preprocess import preprocess


class Calibrator(trt.IInt8EntropyCalibrator2):
    def __init__(self, calibration_data_path, n_calibration, input_shape, cache_file):
        super(Calibrator, self).__init__()
        self.image_list = []
        self.n_calibration = n_calibration
        self.shape = input_shape
        self.buffer_size = trt.volume(input_shape) * trt.float32.itemsize
        self.cache_file = cache_file
        _, self.d_in = cudart.cudaMalloc(self.buffer_size)
        self.one_batch = self.batch_generator()

        for per_image_name in os.listdir(calibration_data_path):
            per_image_path = os.path.join(calibration_data_path, per_image_name)
            if os.path.isfile(per_image_path):
                self.image_list.append(per_image_path)

        print(f"Using {len(self.image_list)} images for calibration.")
        print(f"Device memory allocated at: {int(self.d_in)}")

    def __del__(self):
        cudart.cudaFree(self.d_in)

    @staticmethod
    def image_preprocess(image_path: str, input_size: tuple):
        """
        预处理每一张图片，转换为模型的输入格式。
        """
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        data = preprocess(img, input_size[0], input_size[1])
        return data

    def batch_generator(self):
        """
        生成数据批次。确保每次生成的批次包含 n_calibration 张图片。
        """
        for i in range(self.n_calibration):
            print(f"> Calibration batch {i + 1}/{self.n_calibration}")
            sub_image_list = np.random.choice(self.image_list, self.shape[0], replace=False)
            yield np.ascontiguousarray(self.load_image_list(sub_image_list))

    def load_image_list(self, image_list):
        """
        将一组图片转换为模型输入所需的格式。
        """
        res = np.empty(self.shape, dtype=np.float32)
        for i in range(self.shape[0]):
            res[i] = self.image_preprocess(image_list[i], tuple(self.shape[2:]))
        return res

    def get_batch_size(self):
        return self.shape[0]

    def get_batch(self, name_list=None, input_node_name=None):
        """
        获取一个数据批次并将其拷贝到GPU。
        """
        try:
            data = next(self.one_batch)
            cudart.cudaMemcpy(self.d_in, data.ctypes.data, self.buffer_size,
                              cudart.cudaMemcpyKind.cudaMemcpyHostToDevice)
            return [int(self.d_in)]
        except StopIteration:
            return None

    def read_calibration_cache(self):
        """
        读取已保存的校准缓存文件。
        """
        if os.path.exists(self.cache_file):
            print(f"Cache file found: {self.cache_file}")
            with open(self.cache_file, "rb") as f:
                cache = f.read()
                return cache
        else:
            print("No cache file found!")
            return None

    def write_calibration_cache(self, cache):
        """
        将校准数据写入缓存文件。
        """
        with open(self.cache_file, "wb") as f:
            f.write(cache)
        print(f"Successfully saved calibration cache to {self.cache_file}")

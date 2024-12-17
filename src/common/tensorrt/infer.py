# -*- coding:utf-8 -*-

"""
    onnx 模型转 tensorrt 模型，并使用 tensorrt python api 推理
"""
import math
import os
import threading
import cv2
import time
import numpy as np
import tensorrt as trt
from tqdm import tqdm
from cuda import cudart
from src.common.tensorrt import calibrator
from src.common.tensorrt.config import *
from src.common.tensorrt.preprocess import preprocess
from src.common.tensorrt.postprocess import postprocess


class YoloTRT:
    def __init__(
            self,
            trt_plan=trt_file,
            gpu_id=kGpuId,
            num_classes=kNumClass,
            nms_thresh=kNmsThresh,
            conf_thresh=kConfThresh
    ):
        self.trt_file = trt_plan
        self.logger = trt.Logger(trt.Logger.ERROR)
        cudart.cudaSetDevice(gpu_id)

        self.num_classes = num_classes
        self.nms_thresh = nms_thresh
        self.conf_thresh = conf_thresh

        self.engine = self.load_or_build_engine()
        self.context = self.engine.create_execution_context()
        input_layer_name = self.engine.get_tensor_name(0)
        self.context.set_input_shape(input_layer_name, [1, 3, kInputH, kInputW])

        self.buffer_h, self.buffer_d = self.allocate_buffers()

    def load_or_build_engine(self):
        """加载或构建 TensorRT 引擎"""
        if os.path.exists(self.trt_file):
            with open(self.trt_file, "rb") as f:
                engine_data = f.read()
            if engine_data:
                print("成功加载序列化的引擎文件")
                return trt.Runtime(self.logger).deserialize_cuda_engine(engine_data)
            else:
                raise RuntimeError("序列化引擎文件为空")
        else:
            return self.build_engine()

    import time

    def build_engine(self):
        builder = trt.Builder(self.logger)
        network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
        config = builder.create_builder_config()
        config.set_flag(trt.BuilderFlag.STRICT_NANS)
        config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)

        if use_fp16_mode:
            config.set_flag(trt.BuilderFlag.FP16)
        if use_int8_mode:
            config.set_flag(trt.BuilderFlag.INT8)
            config.int8_calibrator = calibrator.Calibrator(
                calibration_data_dir, n_calibration, (8, 3, kInputH, kInputW), cache_file
            )

        parser = trt.OnnxParser(network, self.logger)
        if not os.path.exists(onnx_file):
            raise FileNotFoundError(f"未找到 ONNX 文件：'{onnx_file}'！")

        with open(onnx_file, "rb") as model, tqdm(total=100, desc="解析 ONNX 文件", unit="%", leave=False) as pbar:
            model_data = model.read()
            if not parser.parse(model_data):
                for error in range(parser.num_errors):
                    print(f"ONNX 解析错误：{parser.get_error(error)}")
                raise RuntimeError("解析 ONNX 文件失败")
            pbar.update(100)
            pbar.close()

        print("成功解析 ONNX 文件")
        input_tensor = network.get_input(0)
        profile = builder.create_optimization_profile()
        profile.set_shape(input_tensor.name, [1, 3, 640, 640], [1, 3, 1024, 1024],
                          [1, 3, 1280, 1280])
        config.add_optimization_profile(profile)

        start_time = time.time()
        max_time = 600
        total_progress = 100
        current_progress = 0

        def nonlinear_progress(x, total_steps):
            scale = 10
            return min(int((math.log(x + 1) / math.log(total_steps + 1)) * 100), total_progress)

        with tqdm(total=total_progress, desc="构建 TensorRT 引擎", unit="%", leave=True) as pbar:
            engine_build_started = False
            engine_data = None
            elapsed_time = 0
            last_progress = 0

            while current_progress < total_progress:
                elapsed_time = time.time() - start_time

                if not engine_build_started:
                    engine_build_started = True
                    build_thread = threading.Thread(target=lambda: builder.build_serialized_network(network, config))
                    build_thread.start()

                if engine_build_started and not build_thread.is_alive():
                    engine_data = builder.build_serialized_network(network, config)
                    if not engine_data:
                        raise RuntimeError("构建 TensorRT 引擎失败")

                    while current_progress < total_progress:
                        current_progress += 5
                        pbar.update(5)
                        time.sleep(0.2)
                    break

                current_progress = nonlinear_progress(elapsed_time, max_time)
                increment = current_progress - last_progress
                if increment > 0:
                    pbar.update(increment)
                    last_progress = current_progress

                time.sleep(0.5)

        pbar.close()
        total_time = time.time() - start_time
        print(f"成功构建 TensorRT 引擎，耗时 {total_time:.2f} 秒")

        with open(self.trt_file, "wb") as f:
            f.write(engine_data)

        return trt.Runtime(self.logger).deserialize_cuda_engine(engine_data)

    def allocate_buffers(self):
        """分配主机和设备缓冲区"""
        num_io_tensors, io_tensor_names, _ = self.get_io_tensors()
        buffer_h = []
        buffer_d = []

        for name in io_tensor_names:
            shape = self.context.get_tensor_shape(name)
            dtype = trt.nptype(self.engine.get_tensor_dtype(name))
            if dtype == np.float64:
                dtype = np.float32

            try:
                buffer_h.append(np.empty(shape, dtype=dtype))
                buffer_d.append(cudart.cudaMalloc(buffer_h[-1].nbytes)[1])
                self.context.set_tensor_address(name, int(buffer_d[-1]))
            except MemoryError as e:
                print(f"内存分配失败: {e}")
                raise

        return buffer_h, buffer_d

    def get_io_tensors(self):
        """获取 I/O 张量信息"""
        num_io_tensors = self.engine.num_io_tensors
        io_tensor_names = [self.engine.get_tensor_name(i) for i in range(num_io_tensors)]
        num_inputs = sum(1 for name in io_tensor_names if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT)
        return num_io_tensors, io_tensor_names, num_inputs

    def inference(self, image):
        """进行推理"""
        input_data = preprocess(image, kInputH, kInputW)
        input_data = np.expand_dims(input_data, axis=0)

        buffer_h, buffer_d = self.buffer_h, self.buffer_d
        buffer_h[0][:] = np.ascontiguousarray(input_data)
        cudart.cudaMemcpy(buffer_d[0], buffer_h[0].ctypes.data, buffer_h[0].nbytes,
                          cudart.cudaMemcpyKind.cudaMemcpyHostToDevice)

        self.context.execute_v2(buffer_d)

        cudart.cudaMemcpy(buffer_h[1].ctypes.data, buffer_d[1], buffer_h[1].nbytes,
                          cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost)
        outputs = buffer_h[-1].reshape((4 + self.num_classes, -1))

        return postprocess(image, outputs, self.conf_thresh, self.nms_thresh, kInputW, kInputH)

    def release(self):
        """释放设备内存"""
        for buf in self.buffer_d:
            cudart.cudaFree(buf)


YoloTRT = YoloTRT()

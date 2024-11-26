# -*- coding:utf-8 -*-

"""
    onnx 模型转 tensorrt 模型，并使用 tensorrt python api 推理
"""

import os

import cv2
import numpy as np
import tensorrt as trt
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

        self.nums_classes = num_classes
        self.nms_thresh = nms_thresh
        self.conf_thresh = conf_thresh

        self.engine = self.get_engine()
        self.context = self.engine.create_execution_context()
        input_layer_name = self.engine.get_tensor_name(0)
        self.context.set_input_shape(input_layer_name, [1, 3, kInputH, kInputW])

        self.buffer_h, self.buffer_d = self.allocate_buffers()

    def get_io_tensors(self, engine):
        num_io_tensors = engine.num_io_tensors
        io_tensor_names = [engine.get_tensor_name(i) for i in range(num_io_tensors)]
        num_input_io_tensors = [engine.get_tensor_mode(io_tensor_names[i]) for i in range(num_io_tensors)].count(
            trt.TensorIOMode.INPUT)
        return num_io_tensors, io_tensor_names, num_input_io_tensors

    def allocate_buffers(self):
        num_io_tensors, io_tensor_names, num_input_tensors = self.get_io_tensors(self.engine)
        buffer_h = []
        buffer_d = []

        for i in range(num_io_tensors):
            buffer_h.append(
                np.empty(
                    self.context.get_tensor_shape(io_tensor_names[i]),
                    dtype=trt.nptype(self.engine.get_tensor_dtype(io_tensor_names[i]))
                )
            )
            buffer_d.append(cudart.cudaMalloc(buffer_h[i].nbytes)[1])

        for i in range(num_io_tensors):
            self.context.set_tensor_address(io_tensor_names[i], int(buffer_d[i]))

        return buffer_h, buffer_d

    def release(self):
        for b in self.buffer_d:
            cudart.cudaFree(b)

    def get_engine(self):
        if os.path.exists(self.trt_file):
            with open(self.trt_file, "rb") as f:
                engine_string = f.read()
            if engine_string is None:
                print("Failed getting serialized engine!")
                return
            print("Succeeded getting serialized engine!")
        else:
            builder = trt.Builder(self.logger)
            network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
            profile = builder.create_optimization_profile()
            config = builder.create_builder_config()
            config.set_flag(trt.BuilderFlag.STRICT_NANS)
            config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)
            if use_fp16_mode:
                config.set_flag(trt.BuilderFlag.FP16)
            if use_int8_mode:
                config.set_flag(trt.BuilderFlag.INT8)
                config.int8_calibrator = calibrator.Calibrator(calibration_data_dir, n_calibration,
                                                               (8, 3, kInputW, kInputW), cache_file)

            parser = trt.OnnxParser(network, self.logger)
            if not os.path.exists(onnx_file):
                print("Failed finding ONNX file!")
                return
            print("Succeeded finding ONNX file!")
            with open(onnx_file, "rb") as model:
                if not parser.parse(model.read()):
                    print("Failed parsing .onnx file!")
                    for error in range(parser.num_errors):
                        print(parser.get_error(error))
                    return
                print("Succeeded parsing .onnx file!")

            input_tensor = network.get_input(0)
            profile.set_shape(input_tensor.name, [1, 3, kInputH, kInputW], [1, 3, kInputH, kInputW],
                              [1, 3, kInputH, kInputW])
            config.add_optimization_profile(profile)

            engine_string = builder.build_serialized_network(network, config)
            if engine_string is None:
                print("Failed building engine!")
                return
            print("Succeeded building engine!")
            with open(self.trt_file, "wb") as f:
                f.write(engine_string)

        engine = trt.Runtime(self.logger).deserialize_cuda_engine(engine_string)

        return engine

    def inference_one(self, data_input, context, buffer_h, buffer_d):
        buffer_h[0] = np.ascontiguousarray(data_input)
        cudart.cudaMemcpy(buffer_d[0], buffer_h[0].ctypes.data, buffer_h[0].nbytes,
                          cudart.cudaMemcpyKind.cudaMemcpyHostToDevice)

        context.execute_v2(buffer_d)

        cudart.cudaMemcpy(buffer_h[1].ctypes.data, buffer_d[1], buffer_h[1].nbytes,
                          cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost)

        outs = buffer_h[-1].reshape((4 + self.nums_classes, -1))

        return outs

    def inference(self, image):
        input_data = preprocess(image, kInputH, kInputW)
        input_data = np.expand_dims(input_data, axis=0)

        output = self.inference_one(input_data, self.context, self.buffer_h, self.buffer_d)

        detect_res = postprocess(image, output, self.conf_thresh, self.nms_thresh, kInputW, kInputW)

        return detect_res


YoloTRT = YoloTRT()

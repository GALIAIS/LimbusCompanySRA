# -*- coding:utf-8 -*-
import sys
from pathlib import Path

from src.app.utils.ConfigManager import cfgm

root_path = Path(sys.argv[0]).resolve().parents[0]

kGpuId = 0
kNumClass = 55
kInputH = 1280
kInputW = 1280
kNmsThresh = 0.45
kConfThresh = 0.25
kMaxNumOutputBbox = 1000
kNumBoxElement = 7
onnx_file = root_path / 'src' / 'common' / 'tensorrt' / 'onnx_model' / 'LBC.onnx'
trt_file = cfgm.get("BaseSetting.Model_path")

# for FP16 mode
use_fp16_mode = False
# for INT8 mode
use_int8_mode = False
n_calibration = 20
cache_file = "./int8.cache"
calibration_data_dir = "./calibrator"

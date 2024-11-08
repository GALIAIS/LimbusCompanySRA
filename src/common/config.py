# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
from attrs import asdict, define, make_class, Factory
from typing import Optional
import threading
from loguru import logger
from src.data.ui_text import UI_TEXT


@define
class Config:
    """配置类"""
    Game_exe_path: str = None
    window_name: str = "LimbusCompany"
    window_process_name: str = "LimbusCompany.exe"
    handle: int = 0
    pid: int = 0
    model_dir: str = os.path.dirname(__file__)
    model_path: str = '../model/LBC.pt'
    absolute_model_path: str = os.path.join(model_dir, model_path)

    # 窗口
    window_width: int = 0
    window_height: int = 0
    window_left: int = 0
    window_top: int = 0
    m_width: int = 0
    m_height: int = 0
    m_left: int = 0
    m_top: int = 0

    # 屏幕
    screen_width: int = 0
    screen_height: int = 0
    screen_left: int = 0
    screen_top: int = 0
    screen_size: tuple = None
    screen_center: tuple = None
    width_scale: float = None
    height_scale: float = None
    original_width: float = None
    original_height: float = None
    system_dpi: int = None
    last_update_time: float = 0
    latest_img_src: Optional[np.array] = None
    previous_img_src: Optional[np.array] = None

    # 鼠标
    mouse_pos: list[int] = Factory(lambda: [0, 0])
    mouse_acceleration: Optional[float] = None

    # OCR与YOLO
    conf: float = 0.7
    iou: float = 0.6
    half: bool = True
    device: str = 'cuda:0'
    max_det: int = 25
    vid_stride: int = 2
    agnostic_nms: bool = False
    classes: Optional[list] = None
    verbose: bool = False

    bboxes: Optional[list] = None
    latest_bboxes: Optional[list] = None
    ocr_result: Optional[str] = None
    img_src: Optional[np.array] = None
    img_yolo_src: Optional[np.array] = None
    img_ocr_src: Optional[np.array] = None

    # 事件流程
    mirror_loop_count: int = 3
    mirror_switch: bool = True
    mirror_dungeon_count: int = 0
    battle_count: int = 0

    #线程
    lock = threading.Lock()
    img_event = threading.Event()
    bboxes_event = threading.Event()
    ocr_event = threading.Event()

    def __post_init__(self):
        """初始化绝对模型路径"""
        self.absolute_model_path = os.path.join(self.model_dir, self.model_path)

    def update_window_position(self, left: int, top: int, width: int, height: int):
        """更新窗口位置信息"""
        self.window_left = left
        self.window_top = top
        self.window_width = width
        self.window_height = height

    def update_screen_size(self, left: int, top: int, width: int, height: int):
        """更新屏幕尺寸"""
        self.screen_left = left
        self.screen_top = top
        self.screen_width = width
        self.screen_height = height


# 配置实例
config = Config()


def get_ui_text(language, key):
    """获取用户界面文本"""
    return UI_TEXT.get(language, {}).get(key, "")
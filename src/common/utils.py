# -*- coding: utf-8 -*-
import base64
import ctypes
import json
import logging
import random
import re
import tempfile
import threading
import time
from pathlib import Path
from typing import Union, Optional, List, Tuple

import cv2
import mss
import numpy as np
import psutil
import pyautogui
import pydirectinput as pdi
import pywinctl as pwc
import win32gui
from PySide6.QtCore import QTimer, Qt
from attrs import define
from loguru import logger
from PySide6.QtWidgets import QApplication, QMainWindow, QInputDialog, QFileDialog, QMessageBox, QVBoxLayout, \
    QHBoxLayout, QPushButton, QLabel, QDialog, QListWidget, QLineEdit, QTreeWidgetItem, QTreeWidget, QCheckBox, \
    QStackedWidget, QGroupBox
from PySide6.QtGui import QGuiApplication

# from paddleocr import PaddleOCR
from src.app.utils.ConfigManager import cfgm
from src.common.config import config as cfg
from src.common.tensorrt.infer import YoloTRT
from src.common.paddleocr_json.PPOCR_api import GetOcrApi
from src.common.paddleocr_json.tbpu import GetParser
from src.data.Labels import Labels_ID, LABELS, COLORS

# model = YOLO(cfg.model_path)
root_path = Path(__file__).resolve().parents[2]
cfgm.set("BaseSetting.root_path", str(root_path))

img_lock = threading.Lock()
ocr_lock = threading.Lock()
bboxes_lock = threading.Lock()
logging.disable(logging.DEBUG)

# ocr = PaddleOCR(use_angle_cls=True, lang="ch")

ocr_engine = None

"""鼠标控制相关"""


# 鼠标移动
def move_mouse_to(start_x, start_y, end_x, end_y, duration=0.2):
    try:
        cfg.mouse_pos = (start_x, start_y)
        pdi.moveTo(end_x, end_y, duration)
    except Exception as e:
        logger.error(f"鼠标移动失败: {e}")


def leftclick(x, y):
    try:
        pdi.leftClick(x, y)
    except Exception as e:
        logger.error(f"鼠标单击失败: {e}")


def moveto(x, y):
    try:
        pdi.moveTo(x, y)
    except Exception as e:
        logger.error(f"鼠标移动失败: {e}")


# 鼠标拖拽到
def drag_to(start_x, start_y, end_x, end_y, duration=0.5):
    try:
        cfg.mouse_pos = (start_x, start_y)
        pdi.dragTo(end_x, end_y, duration, button="MOUSE_LEFT")
    except Exception as e:
        logger.error(f"鼠标拖拽失败: {e}")


# 鼠标单击
def mouse_click(x, y, click=1, interval=1, button="left"):
    try:
        pdi.click(x, y, click, interval, button)
    except Exception as e:
        logger.error(f"鼠标单击失败: {e}")


# 鼠标按下
def mouse_down(x, y, button="left"):
    try:
        pdi.mouseDown(x, y, button)
    except Exception as e:
        logger.error(f"鼠标按下失败: {e}")


# 鼠标释放
def mouse_up(x, y, button="left", duration=1):
    try:
        pdi.mouseUp(x, y, button, duration)
    except Exception as e:
        logger.error(f"鼠标释放失败: {e}")


# 添加随机偏移
def add_random_offset(x, y, max_offset=random.uniform(20, 40)):
    try:
        random_offset_x = x + random.uniform(-max_offset, max_offset)
        random_offset_y = y + random.uniform(-max_offset, max_offset)
        return random_offset_x, random_offset_y
    except Exception as e:
        logger.error(f"添加随机偏移失败: {e}")
        return x, y


# 随机移动鼠标
def move_mouse_random():
    try:
        get_mouse_pos()
        r_x, r_y = add_random_offset(cfg.mouse_pos[0] + random.uniform(50, 100),
                                     cfg.mouse_pos[1] + random.uniform(50, 100))
        move_mouse_to(cfg.mouse_pos[0], cfg.mouse_pos[1], r_x, r_y)
    except Exception as e:
        logger.error(f"随机移动鼠标失败: {e}")


# 获取鼠标位置
def get_mouse_pos():
    try:
        cfg.mouse_pos = pyautogui.position()
        return cfg.mouse_pos
    except Exception as e:
        logger.error(f"获取鼠标位置失败: {e}")
        return 0, 0


# 点击边界框的中心位置
# def click_center_of_bbox(bbox: list) -> None:
#     try:
#         if bbox and isinstance(bbox[0], list):
#             bbox = bbox[0]
#         if bbox:
#             x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
#             target_coords = (int((x0 + x1) / 2), int((y0 + y1) / 2))
#             current_mouse_pos = get_mouse_pos()
#             move_mouse_to(current_mouse_pos[0], current_mouse_pos[1], target_coords[0], target_coords[1])
#             mouse_click(target_coords[0], target_coords[1])
#     except Exception as e:
#         logger.error(f"点击边界框中心失败: {e}")
def click_center_of_bbox(bbox: list, click: int = 1) -> None:
    """点击指定边界框的中心位置"""
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        x0, y0, x1, y1 = map(int, bbox[:4])
        target_coords = ((x0 + x1) // 2, (y0 + y1) // 2)
        move_mouse_to(*get_mouse_pos(), *target_coords)
        mouse_click(*target_coords, click, interval=1, button="left")
    except IndexError:
        logger.error("边界框坐标不完整，无法执行点击操作")
    except Exception as e:
        logger.error(f"点击边界框中心失败: {e}")


# def click_center_of_bboxM(bbox: list, offset_ratio: tuple = (0.05, 0.1)) -> None:
#     try:
#         if bbox and isinstance(bbox[0], list):
#             bbox = bbox[0]
#         if bbox and len(bbox) != 0:
#             x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
#             width, height = x1 - x0, y1 - y0
#             x_offset = int(width * offset_ratio[0] + random.uniform(-20, 20))  # 加上随机微调
#             y_offset = int(height * offset_ratio[1] + random.uniform(-20, 20))
#             target_x = int((x0 + x1) / 2) + x_offset
#             target_y = int((y0 + y1) / 2) + y_offset
#             target_coords = (target_x, target_y)
#             current_mouse_pos = get_mouse_pos()
#             move_mouse_to(current_mouse_pos[0], current_mouse_pos[1], target_coords[0], target_coords[1])
#             mouse_click(target_coords[0], target_coords[1])
#         else:
#             logger.warning("无效的边界框格式，无法点击")
#     except Exception as e:
#         logger.error(f"点击边界框中心失败: {e}")
def click_center_of_bboxR(bbox: list, click: int = 1, offset_ratio: tuple = (0.05, 0.5)) -> None:
    """点击边界框中心位置，带有偏移和随机微调"""
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        if bbox and len(bbox) >= 4:
            x0, y0, x1, y1 = map(float, bbox[:4])
            width, height = x1 - x0, y1 - y0
            x_offset = int(width * offset_ratio[0] + random.uniform(-20, 20))
            y_offset = int(height * offset_ratio[1] + random.uniform(-20, 15))
            target_coords = (int((x0 + x1) / 2) + x_offset, int((y0 + y1) / 2) + y_offset)
            move_mouse_to(*get_mouse_pos(), *target_coords)
            mouse_click(*target_coords, click, interval=1, button="left")
        else:
            logger.warning("无效的边界框格式，无法点击")
    except IndexError:
        logger.error("边界框坐标不足，无法执行点击操作")
    except Exception as e:
        logger.error(f"点击边界框中心失败: {e}")


def click_center_of_text(coordinates: list, click: int = 1, interval: float = 0.1, button: str = "left") -> None:
    """
    点击指定文本区域的中心位置

    :param coordinates: 文本区域的四个角坐标，格式为[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    :param click: 鼠标点击次数，默认为1
    :param interval: 每次点击之间的间隔时间（秒），默认0.1秒
    :param button: 鼠标点击按钮，默认为 "left"（可选 "right" 或 "middle"）
    """
    try:
        if not isinstance(coordinates, list) or len(coordinates) != 4:
            raise ValueError("坐标列表必须是包含四个点的列表，格式为 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]")
        if not all(isinstance(point, list) and len(point) == 2 for point in coordinates):
            raise ValueError("每个坐标点必须是包含两个整数的列表，例如 [x, y]")

        x_coords = [point[0] for point in coordinates]
        y_coords = [point[1] for point in coordinates]

        center_x = sum(x_coords) // 4
        center_y = sum(y_coords) // 4
        target_coords = (center_x, center_y)

        # logger.debug(f"计算中心点坐标: {target_coords}, 点击次数: {click}, 间隔: {interval}s, 按钮: {button}")

        current_pos = get_mouse_pos()
        move_mouse_to(*current_pos, *target_coords)
        mouse_click(*target_coords, click=click, interval=interval, button=button)

        # logger.success(f"成功点击文本中心坐标: {target_coords}")
    except ValueError as ve:
        logger.error(f"坐标验证失败: {ve}")
    except Exception as e:
        logger.exception(f"点击文本中心失败: {e}")


def click_center_of_textR(coordinates: list, click: int = 1, offset_ratio: tuple = (0.05, 0.05)) -> None:
    """
    点击指定文本区域的中心位置，带有偏移和随机微调
    :param coordinates: 文本区域的四个坐标点 [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    :param click: 点击次数，默认为1次
    :param offset_ratio: 偏移比例 (x_ratio, y_ratio)，默认为 (5%, 5%)
    """
    try:
        if not coordinates or len(coordinates) != 4:
            raise ValueError("无效的坐标格式，必须为包含4个点的列表")

        if not all(len(point) == 2 for point in coordinates):
            raise ValueError("坐标点格式错误，每个点必须包含两个数值")

        x0, y0 = map(float, coordinates[0])
        x1, y1 = map(float, coordinates[2])

        if x1 <= x0 or y1 <= y0:
            raise ValueError("坐标范围错误，右下角点必须大于左上角点")

        width = x1 - x0
        height = y1 - y0

        x_offset = int(width * offset_ratio[0] + random.uniform(-0.1 * width, 0.1 * width))
        y_offset = int(height * offset_ratio[1] + random.uniform(-0.1 * height, 0.1 * height))

        target_coords = (int((x0 + x1) / 2) + x_offset, int((y0 + y1) / 2) + y_offset)

        move_mouse_to(*get_mouse_pos(), *target_coords)
        mouse_click(*target_coords, click, interval=1, button="left")

        # logger.info(f"点击文本区域中心成功: {target_coords}, 偏移比例: {offset_ratio}, 点击次数: {click}")

    except ValueError as ve:
        logger.error(f"参数验证失败: {ve}")
    except Exception as e:
        logger.error(f"点击文本区域中心失败: {e}")


# 将鼠标移动到边界框的中心位置
def move_to_center_of_bbox(bbox: list, offset_ratio: tuple = (0.05, 0.1)) -> None:
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        if bbox and len(bbox) == 4:
            x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            width, height = x1 - x0, y1 - y0
            x_offset = int(width * offset_ratio[0] + random.uniform(-2, 2))
            y_offset = int(height * offset_ratio[1] + random.uniform(-2, 2))
            target_x = int((x0 + x1) / 2) + x_offset
            target_y = int((y0 + y1) / 2) + y_offset
            target_coords = (target_x, target_y)
            current_mouse_pos = get_mouse_pos()
            move_mouse_to(current_mouse_pos[0], current_mouse_pos[1], target_coords[0], target_coords[1])
        else:
            logger.warning("无效的边界框格式，无法移动")
    except Exception as e:
        logger.error(f"移动到边界框中心失败: {e}")


# 移动鼠标至显示屏中心
def move_mouse_to_center():
    try:
        cfg.screen_size = pdi.virtual_size()
        cfg.screen_center = cfg.screen_size[0] / 2, cfg.screen_size[1] / 2
        get_mouse_pos()
        move_mouse_to(cfg.mouse_pos[0], cfg.mouse_pos[1], cfg.screen_center[0], cfg.screen_center[1])
    except Exception as e:
        logger.error(f"移动鼠标至显示屏中心失败: {e}")


# 鼠标滚动
def mouse_scroll(click=-10):
    try:
        pdi.scroll(click)
    except Exception as e:
        logger.error(f"鼠标滚动失败: {e}")


# 将鼠标移动到中心点并向下拖拽
def move_to_center_and_drag(bbox: list) -> None:
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        if bbox:
            x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            target_coords = (int((x0 + x1) / 2), int((y0 + y1) / 2))
            end_coords = (target_coords[0], target_coords[1] + 300)
            current_mouse_pos = get_mouse_pos()
            move_mouse_to(current_mouse_pos[0], current_mouse_pos[1], target_coords[0], target_coords[1])
            mouse_down(target_coords[0], target_coords[1])
            move_mouse_to(target_coords[0], target_coords[1], end_coords[0], end_coords[1])
            mouse_up(target_coords[0], target_coords[1])
    except Exception as e:
        logger.error(f"拖拽到边界框中心失败: {e}")


def move_to_center_and_dragR(bbox: list, direction: str = 'down', distance: int = 300) -> None:
    """将鼠标移动到中心点并拖拽"""
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        if bbox:
            x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            target_coords = (int((x0 + x1) / 2), int((y0 + y1) / 2))

            if direction == 'down':
                end_coords = (target_coords[0], target_coords[1] + distance)
            elif direction == 'up':
                end_coords = (target_coords[0], target_coords[1] - distance)
            elif direction == 'left':
                end_coords = (target_coords[0] - distance, target_coords[1])
            elif direction == 'right':
                end_coords = (target_coords[0] + distance, target_coords[1])
            else:
                raise ValueError(f"Invalid direction: {direction}")

            current_mouse_pos = get_mouse_pos()
            move_mouse_to(current_mouse_pos[0], current_mouse_pos[1], target_coords[0], target_coords[1])
            mouse_down(target_coords[0], target_coords[1])
            move_mouse_to(target_coords[0], target_coords[1], end_coords[0], end_coords[1])
            mouse_up(target_coords[0], target_coords[1])
    except Exception as e:
        logger.error(f"拖拽到边界框中心失败: {e}")


def calculate_center(coordinates: list) -> tuple:
    """
    计算边界框中心点坐标。

    Args:
        coordinates (list): OCR 结果中的坐标列表，包含四个点。

    Returns:
        tuple: 中心点坐标 (x, y)。
    """
    if len(coordinates) == 4:
        x0, y0 = coordinates[0]
        x1, y1 = coordinates[2]
        return int((x0 + x1) / 2), int((y0 + y1) / 2)
    else:
        raise ValueError("边界框的坐标数量不正确，应为 4 个点。")


def get_drag_offset(drag_offset: int, direction: str) -> tuple:
    """
    根据方向和偏移量计算拖拽的最终目标偏移值。

    Args:
        drag_offset (int): 拖拽偏移量。
        direction (str): 拖拽方向，支持 'down', 'up', 'left', 'right'。

    Returns:
        tuple: 偏移量 (offset_x, offset_y)。
    """
    directions = {
        "down": (0, drag_offset),
        "up": (0, -drag_offset),
        "left": (-drag_offset, 0),
        "right": (drag_offset, 0),
    }
    if direction in directions:
        return directions[direction]
    else:
        raise ValueError(f"无效的拖拽方向: {direction}，请使用 'down', 'up', 'left', 'right' 之一。")


def drag_to_target(start_coords: tuple, drag_offset: tuple) -> None:
    """
    执行鼠标拖拽操作。

    Args:
        start_coords (tuple): 起始坐标 (x, y)。
        drag_offset (tuple): 拖拽偏移量 (offset_x, offset_y)。

    Returns:
        None
    """
    try:
        end_coords = (start_coords[0] + drag_offset[0], start_coords[1] + drag_offset[1])
        current_mouse_pos = get_mouse_pos()

        move_mouse_to(current_mouse_pos[0], current_mouse_pos[1], start_coords[0], start_coords[1])
        mouse_down(start_coords[0], start_coords[1])
        move_mouse_to(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
        mouse_up(end_coords[0], end_coords[1])
        # logger.info(f"拖拽完成：从 {start_coords} 到 {end_coords}")
    except Exception as e:
        logger.error(f"鼠标拖拽操作失败: {e}")


def locate_and_drag(img_src: str, target_text: str, drag_offset: int = 300, direction: str = 'down') -> None:
    """
    根据图像和目标文本定位并拖拽。

    Args:
        img_src (str): 图像路径。
        target_text (str): 目标文本内容。
        drag_offset (int): 拖拽的偏移量（像素）。
        direction (str): 拖拽方向，支持 'down', 'up', 'left', 'right'。

    Returns:
        None
    """
    try:
        ocr_data = get_ocrx_data(img_src)
        ocr_results = ocrx_process(ocr_data)

        offset_x, offset_y = get_drag_offset(drag_offset, direction)

        for result in ocr_results:
            if result.get('text') == target_text and 'coordinates' in result:
                try:
                    target_coords = calculate_center(result['coordinates'])
                    # logger.info(f"找到目标文本 '{target_text}'，中心点坐标: {target_coords}")

                    drag_to_target(target_coords, (offset_x, offset_y))
                    return
                except ValueError as ve:
                    logger.warning(f"处理目标文本 '{target_text}' 的坐标失败: {ve}")

        logger.warning(f"未找到目标文本: {target_text}")
    except Exception as e:
        logger.error(f"定位和拖拽操作失败: {e}")


# 计算边界框的中心位置
def center_of_bbox(bbox: list):
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        if bbox:
            x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            return int((x0 + x1) / 2), int((y0 + y1) / 2)
        return None
    except Exception as e:
        logger.error(f"计算边界框中心失败: {e}")
        return None


"""鼠标控制相关"""

"""OCR检测相关"""


# def get_ocr_data(img_src: np.ndarray) -> list:
#     try:
#         if img_src is not None:
#             if img_src.size == 0:
#                 raise ValueError("输入图像数据为空")
#             ocr_result = ocr.ocr(img_src, cls=True)
#             if not ocr_result or not isinstance(ocr_result, list):
#                 raise ValueError("OCR 结果为空或格式不正确")
#             return ocr_result
#         return []
#     except IndexError as e:
#         logger.error(f"OCR 数据获取失败 - 索引错误: {e}")
#         return []
#     except Exception as e:
#         logger.error(f"OCR 数据获取失败: {e}")
#         return []

# def initOCRX(ocrx):
#     """
#     初始化 PaddleOCR-json OCR 引擎
#     """
#     exePath = root_path / "src" / "3rdparty" / "PaddleOCR-json" / "PaddleOCR-json.exe"
#     modelsPath = root_path / "src" / "3rdparty" / "PaddleOCR-json" / "models"
#     configPath = modelsPath / "config_chinese.txt"
#     argument = {"config_path": str(configPath)}
#
#     try:
#         ocrx = GetOcrApi(str(exePath))
#         return ocrx
#     except Exception as e:
#         logger.error(f"初始化 OCR 失败: {e}")
#         ocrx = None
#         raise

def initOCRX():
    """
    初始化 PaddleOCR-json OCR 引擎
    """
    global ocr_engine
    if ocr_engine is not None:
        return

    exePath = root_path / "src" / "3rdparty" / "PaddleOCR-json" / "PaddleOCR-json.exe"
    modelsPath = root_path / "src" / "3rdparty" / "PaddleOCR-json" / "models"
    configPath = modelsPath / "config_chinese.txt"
    argument = {"config_path": str(configPath)}

    try:
        ocr_engine = GetOcrApi(str(exePath))
    except Exception as e:
        logger.error(f"初始化 OCR 失败: {e}")
        ocr_engine = None
        raise


# PaddleOCR-json的获取数据函数
def get_ocrx_data(img_src, input_type="ndarray") -> dict:
    """
    使用 PaddleOCR-json 引擎获取 OCR 检测结果。

    :param img_src: 输入图像数据，可以是 ndarray、字节流、Base64 字符串或路径。
    :param input_type: 输入图像类型，可选值为 'ndarray', 'bytes', 'base64', 'path'。
    :return: 包含 OCR 检测结果的字典，格式正确则返回数据；未检测到文字时返回空字典。
    """
    global ocr_engine
    try:
        validate_input(img_src, input_type)

        if ocr_engine is None:
            initOCRX()
            if ocr_engine is None:
                raise RuntimeError("OCR 引擎初始化失败")

        # logger.debug(f"OCR 输入类型: {input_type}")

        if input_type == "ndarray":
            _, img_bytes = cv2.imencode('.png', img_src)
            ocr_result = ocr_engine.runBytes(img_bytes.tobytes())
        elif input_type == "bytes":
            ocr_result = ocr_engine.runBytes(img_src)
        elif input_type == "base64":
            ocr_result = ocr_engine.runBase64(img_src)
        elif input_type == "path":
            ocr_result = ocr_engine.run(img_src)
        else:
            raise ValueError(f"不支持的 input_type: {input_type}")

        if ocr_result.get("code") == 101:
            return {}

        return validate_ocr_result(ocr_result)

    except ValueError as e:
        logger.error(f"OCR 输入数据验证失败: {e}")
    except RuntimeError as e:
        logger.error(f"OCR 引擎运行失败: {e}")
    except Exception as e:
        logger.error(f"OCR 数据处理失败: {e}")


# 在程序结束时退出 OCR 引擎
def exitOCRX():
    """
    退出 PaddleOCR-json OCR 引擎
    """
    global ocr_engine
    if ocr_engine is not None:
        try:
            ocr_engine.exit()
        except Exception as cleanup_error:
            logger.warning(f"释放 OCR 引擎资源时出现问题: {cleanup_error}")


# PaddleOCR的获取数据函数
# def get_ocr_data(img_src: np.ndarray) -> list:
#     try:
#         if img_src is not None:
#             if not isinstance(img_src, np.ndarray):
#                 raise ValueError("输入图像数据不是 numpy.ndarray 类型")
#             if img_src.size == 0:
#                 raise ValueError("输入图像数据为空")
#             ocr_result = ocr.ocr(img_src, cls=True)
#             if not ocr_result or not isinstance(ocr_result, list):
#                 raise ValueError("OCR 结果为空或格式不正确")
#             return ocr_result
#         return []
#     except IndexError as e:
#         logger.error(f"OCR 数据获取失败 - 索引错误: {e}")
#         return []
#     except Exception as e:
#         logger.error(f"OCR 数据获取失败: {e}")
#         return []


# PaddleOCR-json的获取数据函数
# def get_ocrx_data(img_src, input_type="ndarray") -> dict:
#     """
#     使用 PaddleOCR-json 引擎获取 OCR 检测结果。
#
#     :param img_src: 输入图像数据，可以是 ndarray、字节流、Base64 字符串或路径。
#     :param input_type: 输入图像类型，可选值为 'ndarray', 'bytes', 'base64', 'path'。
#     :return: 包含 OCR 检测结果的字典，格式正确则返回数据；未检测到文字时返回空字典。
#     """
#     ocr_engine = None
#     try:
#         validate_input(img_src, input_type)
#
#         ocr_engine = initOCRX(ocr_engine)
#         if ocr_engine is None:
#             raise RuntimeError("OCR 引擎初始化失败")
#
#         # logger.debug(f"OCR 输入类型: {input_type}")
#
#         if input_type == "ndarray":
#             _, img_bytes = cv2.imencode('.png', img_src)
#             ocr_result = ocr_engine.runBytes(img_bytes.tobytes())
#         elif input_type == "bytes":
#             ocr_result = ocr_engine.runBytes(img_src)
#         elif input_type == "base64":
#             ocr_result = ocr_engine.runBase64(img_src)
#         elif input_type == "path":
#             ocr_result = ocr_engine.run(img_src)
#         else:
#             raise ValueError(f"不支持的 input_type: {input_type}")
#
#         if ocr_result.get("code") == 101:
#             return {}
#
#         return validate_ocr_result(ocr_result)
#
#     except ValueError as e:
#         logger.error(f"OCR 输入数据验证失败: {e}")
#     except RuntimeError as e:
#         logger.error(f"OCR 引擎运行失败: {e}")
#     except Exception as e:
#         logger.error(f"OCR 数据处理失败: {e}")
#     finally:
#         if ocr_engine is not None:
#             try:
#                 ocr_engine.exit()
#             except Exception as cleanup_error:
#                 logger.warning(f"释放 OCR 引擎资源时出现问题: {cleanup_error}")
#     return {}


def validate_input(img_src, input_type):
    """
    验证输入的图像数据和类型是否符合要求。

    :param img_src: 输入图像数据。
    :param input_type: 输入图像类型。
    :raises ValueError: 如果输入无效。
    """
    if input_type == "ndarray" and not isinstance(img_src, np.ndarray):
        raise ValueError("输入类型为 'ndarray' 时，img_src 必须是 numpy.ndarray")
    if input_type == "bytes" and not isinstance(img_src, (bytes, bytearray)):
        raise ValueError("输入类型为 'bytes' 时，img_src 必须是字节流对象")
    if input_type == "base64" and not isinstance(img_src, str):
        raise ValueError("输入类型为 'base64' 时，img_src 必须是 Base64 编码字符串")
    if input_type == "path" and not isinstance(img_src, str):
        raise ValueError("输入类型为 'path' 时，img_src 必须是字符串路径")


def validate_ocr_result(ocr_result):
    """
    验证 OCR 返回结果格式是否正确。

    :param ocr_result: OCR 返回的数据。
    :return: 验证通过的 OCR 结果。
    :raises ValueError: 如果结果格式不符合要求。
    """
    if not ocr_result or not isinstance(ocr_result, dict):
        raise ValueError("OCR 结果为空或格式不正确")
    if ocr_result.get("code") != 100:
        raise ValueError(f"OCR 执行失败，状态码: {ocr_result.get('code')}")
    if "data" not in ocr_result or not isinstance(ocr_result["data"], list):
        raise ValueError("OCR 返回的数据结构不完整")

    for item in ocr_result["data"]:
        if not isinstance(item, dict):
            raise ValueError(f"OCR 数据项格式错误: {item}")
        if not all(k in item for k in ["box", "text", "score"]):
            raise ValueError(f"OCR 数据项缺少必要字段: {item}")
        if not isinstance(item["box"], list) or len(item["box"]) != 4:
            raise ValueError(f"OCR 检测框格式错误: {item['box']}")
        if not isinstance(item["text"], str):
            raise ValueError(f"OCR 文本格式错误: {item['text']}")
        if not isinstance(item["score"], (float, int)):
            raise ValueError(f"OCR 置信度格式错误: {item['score']}")

    return ocr_result


# 单文本检测
def text_exists(
        img_src: np.ndarray,
        text: str,
        flag: bool = False,
        confidence_threshold: float = 0.5
) -> bool:
    """
    检查给定图像中是否存在符合条件的文本。

    Args:
        img_src (np.ndarray): 输入图像，作为 OCR 处理的源数据。
        text (str): 要匹配的目标文本（支持正则表达式）。
        flag (bool): 是否打印详细日志信息，默认开启。
        confidence_threshold (float): 匹配文本的置信度阈值，默认值为 0.8。

    Returns:
        bool: 如果存在符合条件的文本，返回 True；否则返回 False。
    """
    try:
        if img_src is None or not isinstance(img_src, np.ndarray):
            logger.warning("文本检测失败: img_src 为空或类型错误")
            return False

        if not isinstance(text, str) or not text.strip():
            logger.error(f"无效的文本输入: {text}")
            return False

        if not (0 <= confidence_threshold <= 1):
            logger.error(f"无效的置信度阈值: {confidence_threshold}，应在 0 到 1 之间")
            return False

        ocr_results = ocrx_process(get_ocrx_data(img_src))
        if flag:
            logger.info(f"OCR 结果: {ocr_results}")

        try:
            pattern = re.compile(text)
        except re.error as regex_error:
            logger.warning(f"无效的正则表达式: {text} | 错误: {regex_error}")
            pattern = re.compile(re.escape(text))

        for res in ocr_results:
            ocr_text = res.get('text', '')
            confidence = res.get('confidence', 0)
            if confidence >= confidence_threshold:
                if flag:
                    logger.info(f"当前 OCR 文本: {ocr_text} | 置信度: {confidence}")
                if pattern.search(ocr_text):
                    if flag:
                        logger.info(f"匹配成功: {ocr_text} | 置信度: {confidence}")
                    return True

        if flag:
            logger.info(f"匹配失败: 未找到符合条件的文本 | 输入: {text}")
        return False

    except Exception as e:
        logger.error(f"文本检测失败: {e} | 输入文本: {text}")
        return False


# 多文本列表检测
def text_list_exists(
        img_src: np.ndarray,
        patterns: list,
        flag: bool = False,
        confidence_threshold: float = 0.5,
        match_mode: str = "any",
        return_details: bool = False,
        ignore_case: bool = True
) -> Union[bool, list, dict]:
    """
    检查给定图像中是否存在符合条件的文本列表中任意一个，并支持返回详细匹配信息。

    Args:
        img_src (np.ndarray): 输入图像，作为 OCR 处理的源数据。
        patterns (list): 要匹配的目标文本列表（支持正则表达式）。
        flag (bool): 是否打印详细日志信息，默认关闭。
        confidence_threshold (float): 匹配文本的置信度阈值，默认值为 0.8。
        match_mode (str): 匹配模式，可选 "all"（所有模式必须匹配）或 "any"（任意一个模式即可匹配）或 "not"（反向匹配）。
        return_details (bool): 是否返回详细匹配信息，默认返回布尔值。
        ignore_case (bool): 是否忽略大小写匹配，默认为 True。

    Returns:
        Union[bool, list, dict]:
            - 如果 `return_details=False`，返回布尔值表示是否存在匹配。
            - 如果 `return_details=True`，返回匹配的详细信息列表或空列表。
    """
    try:
        if img_src is None or not isinstance(img_src, np.ndarray):
            logger.warning("文本检测失败: img_src 为空或类型错误")
            return False if not return_details else []

        if not isinstance(patterns, list) or not patterns:
            logger.error("无效的文本列表输入")
            return False if not return_details else []

        if not (0 <= confidence_threshold <= 1):
            logger.error(f"无效的置信度阈值: {confidence_threshold}，应在 0 到 1 之间")
            return False if not return_details else []

        ocr_results = ocrx_process(get_ocrx_data(img_src))
        if flag:
            logger.debug(f"OCR 结果: {ocr_results}")

        regex_flags = re.IGNORECASE if ignore_case else 0
        compiled_patterns = []
        for pattern in patterns:
            try:
                compiled_patterns.append(re.compile(pattern, flags=regex_flags))
            except re.error as regex_error:
                logger.warning(f"无效的正则表达式: {pattern} | 错误: {regex_error}")

        if not compiled_patterns:
            logger.error("未能解析任何有效的正则表达式")
            return False if not return_details else []

        matches = []
        for res in ocr_results:
            ocr_text = res.get('text', '')
            confidence = res.get('confidence', 0)
            if confidence < confidence_threshold:
                continue

            pattern_matches = []
            for pattern in compiled_patterns:
                match_found = False
                if match_mode == "all":
                    match_found = pattern.fullmatch(ocr_text) is not None
                elif match_mode == "any":
                    match_found = pattern.search(ocr_text) is not None
                elif match_mode == "not":
                    match_found = pattern.search(ocr_text) is None

                pattern_matches.append(match_found)

            if match_mode == "all" and all(pattern_matches):
                match_info = {
                    "text": ocr_text,
                    "pattern_matches": pattern_matches,
                    "confidence": confidence
                }
                matches.append(match_info)
                if flag:
                    logger.info(f"匹配成功: {match_info}")

            elif match_mode == "any" and any(pattern_matches):
                match_info = {
                    "text": ocr_text,
                    "pattern_matches": pattern_matches,
                    "confidence": confidence
                }
                matches.append(match_info)
                if flag:
                    logger.info(f"匹配成功: {match_info}")

            elif match_mode == "not" and any(pattern_matches):
                if flag:
                    logger.info(f"匹配失败: 模式 {patterns} 的反向匹配未找到")

        if flag:
            if matches:
                logger.info(f"总匹配结果: {matches}")
            else:
                logger.info(f"未找到符合条件的文本 | 输入模式: {patterns}")

        if return_details:
            return matches
        return bool(matches)

    except Exception as e:
        logger.error(f"文本检测失败: {e} | 输入文本列表: {patterns}")
        return False if not return_details else []


# 获取ocr_text的坐标
def get_text_coordinates(text: str,
                         img_src: Optional[np.ndarray] = None,
                         threshold: float = 0.5,
                         multiple: bool = False,
                         partial_match: bool = False) -> Union[List[List[int]], List[Tuple[List[int], float]]]:
    """
    获取文本在图像中的坐标。

    Args:
        text: 要查找的文本。
        img_src: 可选参数，提供图像源。如果未提供，则使用 getWindowShot() 获取屏幕截图。
        threshold: 可选参数，匹配的置信度阈值，默认为 0.8。
        multiple: 可选参数，是否返回多个匹配结果，默认为 False。
        partial_match: 可选参数，是否允许部分匹配，默认为 False。

    Returns:
        如果 multiple 为 False，则返回一个包含文本坐标的列表，格式为 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]。
        如果 multiple 为 True，则返回一个包含多个匹配结果的列表，每个元素是一个元组，
        格式为 ([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], confidence)，其中 confidence 是匹配的置信度。
        如果没有找到匹配的文本，则返回空列表。
    """
    try:
        img_src = img_src or getWindowShot()
        if img_src is None:
            logger.warning("无法获取图像源。")
            return []

        result = ocrx_process(get_ocrx_data(img_src))
        if partial_match:
            pattern = re.compile(f".*{text}.*")
        else:
            pattern = re.compile(text)

        coordinates = []
        for res in result:
            match = pattern.search(res['text'])
            if match and res['confidence'] >= threshold:
                if multiple:
                    coordinates.append((res['coordinates'], res['confidence']))
                else:
                    return res['coordinates']
        return coordinates
    except Exception as e:
        logger.error(f"获取文本坐标失败: {e}")
        return []


# PaddleOCR的数据处理
def ocr_process(ocr_result: list) -> list:
    """处理 OCR 结果"""
    result_list = []
    try:
        if ocr_result is not None and isinstance(ocr_result, list):
            for res in ocr_result:
                if isinstance(res, list):
                    for line in res:
                        coordinates = line[0]
                        text = line[1][0]
                        confidence = line[1][1]
                        result_list.append({
                            "coordinates": coordinates,
                            "text": text,
                            "confidence": confidence
                        })
        else:
            logger.warning("OCR 识别结果为空或格式不正确")
    except Exception as e:
        logger.error(f"OCR 处理失败: {e}")
    return result_list


# PaddleOCR-json的数据处理
def ocrx_process(ocr_result: dict) -> list:
    """
    处理 OCR 返回的结果，提取所需数据。

    :param ocr_result: OCR 返回的结果字典
    :return: 处理后的文本块列表，每项包含坐标、文本和置信度
    """
    result_list = []
    try:
        if not ocr_result:
            # logger.warning("OCR 返回结果为空")
            return result_list
        if not isinstance(ocr_result, dict):
            logger.warning(f"OCR 返回结果格式错误，类型为: {type(ocr_result)}")
            return result_list

        data = ocr_result.get("data", [])
        if not isinstance(data, list):
            logger.warning(f"OCR 数据格式错误，'data' 应为列表，但类型为: {type(data)}")
            return result_list

        for item in data:
            if not isinstance(item, dict):
                logger.warning(f"OCR 文本块格式错误，非字典类型，实际类型为: {type(item)}")
                continue

            box = item.get("box", [])
            text = item.get("text", "")
            score = item.get("score", 0.0)

            if not isinstance(box, list) or len(box) != 4:
                logger.warning(f"检测框格式错误: {box}")
                continue
            if not isinstance(text, str):
                logger.warning(f"文本格式错误: {text}")
                continue
            if not isinstance(score, (float, int)):
                logger.warning(f"置信度格式错误: {score}")
                continue

            result_list.append({
                "coordinates": box,
                "text": text,
                "confidence": score
            })

    except Exception as e:
        logger.error(f"OCR 处理失败: {e}")

    return result_list


def process_and_merge_ocr(ocr_result: dict, scheme: str = "multi_para") -> list:
    """
    对 OCR 结果进行后处理，包括使用 tbpu 调整文本块顺序并合并为完整语句。

    :param ocr_result: OCR 返回的结果字典，必须包含 'data' 键
    :param scheme: tbpu 的处理方案 ID，默认为 "multi_para"
    :return: 合并后的完整语句列表
    """
    try:
        if not ocr_result or not isinstance(ocr_result, dict):
            raise ValueError("OCR 结果为空或格式不正确")

        text_blocks = ocr_result.get("data", [])
        if not isinstance(text_blocks, list):
            raise ValueError("OCR 数据格式错误，'data' 应为列表")

        parser = GetParser(scheme)

        processed_blocks = parser.run(text_blocks)

        merged_sentences = []
        current_sentence = ""

        for block in processed_blocks:
            text = block.get("text", "")
            end = block.get("end", "")

            current_sentence += text

            if end == "\n":
                merged_sentences.append(current_sentence.strip())
                current_sentence = ""

        if current_sentence:
            merged_sentences.append(current_sentence.strip())

        return merged_sentences

    except ValueError as e:
        logger.error(f"OCR 输入数据验证失败: {e}")
    except Exception as e:
        logger.error(f"OCR 文本处理失败: {e}")
    return []


def check_text_and_click(text: str, click: int = 1):
    """匹配文本并点击对应的选项"""
    ocr_coordinates = get_text_coordinates(text)
    if ocr_coordinates:
        click_center_of_text(ocr_coordinates, click)


def check_text_and_clickR(text: str, click: int = 1):
    """匹配文本并点击对应的选项"""
    ocr_coordinates = get_text_coordinates(text)
    if ocr_coordinates:
        click_center_of_textR(ocr_coordinates, click)


def check_text_in_model_and_click(pattern: str, click: int = 1):
    """匹配文本并点击对应的选项"""
    result_check = check_text_in_model(cfg.bboxes, pattern)
    if result_check:
        click_center_of_bbox(result_check, click)


def check_text_in_model_and_clickR(pattern: str, click: int = 1):
    """匹配文本并点击对应的选项"""
    result_check = check_text_in_model(cfg.bboxes, pattern)
    if result_check:
        click_center_of_bboxR(result_check, click)


"""OCR检测相关"""

"""WindowManager相关"""


@define
class WindowManager:
    window_size: tuple = None
    screen_size: tuple = None
    result: bool = False
    hwnd: int = None
    window: str = None
    window_name: str = cfg.window_name
    window_process_name: str = cfg.window_process_name
    processes: str = None
    process: str = None
    process_info: str = None
    pid: str = None
    dpi_scale: float = None

    def window_info(self):
        try:
            windows = pwc.getWindowsWithTitle(self.window_name)
            if windows:
                window = windows[0]
                bbox = window.box
                cfg.m_top = bbox.top + 38
                cfg.m_left = bbox.left + 10
                cfg.m_width = bbox.width - 20
                cfg.m_height = bbox.height - 45

                self.screen_size = pdi.virtual_size()
                cfg.update_screen_size(*self.screen_size)

                self.window_size = bbox
                cfg.update_window_position(bbox[0], bbox[1], bbox[2], bbox[3])
                return self.window_size
            return None
        except Exception as e:
            logger.error(f"获取窗口信息失败: {e}")
            return None

    def init_window(self):
        try:
            windows = pwc.getWindowsWithTitle(self.window_name)
            if windows:
                window = windows[0]
                self.hwnd = window.getHandle()
                self.result = True
                cfg.handle = self.hwnd

                if window.isMinimized:
                    window.restore()
                window.raiseWindow()
                window.activate()
                window.maximize()
            return True
        except Exception as e:
            logger.error(f"初始化窗口失败: {e}")
            return False

    def get_dpi_scale(self):
        try:
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            hdc = win32gui.GetDC(None)

            logical_width = gdi32.GetDeviceCaps(hdc, 8)
            logical_height = gdi32.GetDeviceCaps(hdc, 10)

            physical_width = user32.GetSystemMetrics(0)
            physical_height = user32.GetSystemMetrics(1)

            width_scale = logical_width / physical_width
            height_scale = logical_height / physical_height

            cfg.system_dpi = user32.GetDpiForSystem()

            cfg.width_scale = width_scale
            cfg.height_scale = height_scale
            cfg.original_width = physical_width
            cfg.original_height = physical_height
        except Exception as e:
            logger.error(f"获取 DPI 缩放失败: {e}")

    def get_pid(self):
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] == self.window_process_name:
                    cfg.pid = process.info['pid']
                    return process.info['pid']
            return None
        except Exception as e:
            logger.error(f"获取 PID 失败: {e}")
            return None

    def get_hwnd(self):
        try:
            windows = pwc.getWindowsWithTitle(self.window_name)
            if windows:
                self.hwnd = windows[0].getHandle()
                cfg.handle = self.hwnd
                return self.hwnd
        except Exception as e:
            logger.error(f"获取窗口句柄失败: {e}")
            return None

    def is_window_open(self):
        try:
            return bool(pwc.getWindowsWithTitle(self.window_name))
        except Exception as e:
            logger.error(f"检查窗口是否打开失败: {e}")
            return False

    def show_window(self):
        try:
            if self.window:
                self.window[0].show()
        except Exception as e:
            logger.error(f"显示窗口失败: {e}")

    def hide_window(self):
        try:
            if self.window:
                self.window[0].hide()
        except Exception as e:
            logger.error(f"隐藏窗口失败: {e}")

    def is_minimized(self):
        try:
            return self.window[0].isMinimized if self.window else False
        except Exception as e:
            logger.error(f"检查窗口是否最小化失败: {e}")
            return False

    def is_active(self):
        try:
            return self.window[0].isActive if self.window else False
        except Exception as e:
            logger.error(f"检查窗口是否激活失败: {e}")
            return False

    def set_window_position(self, x, y):
        try:
            if self.window:
                self.window[0].moveTo(x, y)
        except Exception as e:
            logger.error(f"设置窗口位置失败: {e}")

    def set_window_size(self, width, height):
        try:
            if self.window:
                self.window[0].resizeTo(width, height)
        except Exception as e:
            logger.error(f"设置窗口大小失败: {e}")

    def close_window(self):
        try:
            if self.window:
                self.window[0].close()
        except Exception as e:
            logger.error(f"关闭窗口失败: {e}")


# 检查Label名称是否存在并移动鼠标点击按钮
def check_label_and_click(bboxes: list, label: str, click: int = 1) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]):
                    click_center_of_bbox(bbox, click)
                    break
    except Exception as e:
        logger.error(f"检查标签失败: {e}")


def check_label_and_clickR(bboxes: list, label: str, click: int = 1) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]):
                    click_center_of_bboxR(bbox, click)
                    break
    except Exception as e:
        logger.error(f"检查标签失败: {e}")


# 检查Label_ID是否存在并移动鼠标点击按钮
def check_label_id_and_click(bboxes: list, label_id: float, click: int = 1) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, label_id):
                    click_center_of_bbox(bbox, click)
                    break
    except Exception as e:
        logger.error(f"检查标签 ID 失败: {e}")


def check_label_id_and_clickR(bboxes: list, label_id: float, click: int) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, label_id):
                    click_center_of_bboxR(bbox, click)
                    break
    except Exception as e:
        logger.error(f"检查标签 ID 失败: {e}")


# 检查Label是否存在并移动鼠标拖拽
def check_label_and_drag(bboxes: list, label: str) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]):
                    move_to_center_and_drag(bbox)
                    break
    except Exception as e:
        logger.error(f"检查标签并拖拽失败: {e}")


# 检查Label和Text是否存在并移动鼠标拖拽
def check_label_text_and_drag(theme_pack: str, bboxes: list, label: str) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]) and text_is_within(bbox, theme_pack):
                    move_to_center_and_dragR(bbox, direction='down')
                    break
    except Exception as e:
        logger.error(f"检查标签和文本并拖拽失败: {e}")


# 获取yolo的bbox
def getBBOX(bboxes: list, label: str) -> list:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]):
                    return bbox
    except Exception as e:
        logger.error(f"获取 YOLO 的 bbox 失败: {e}")
    return []


# label检测
def label_exists(bbox: list, label: float) -> bool:
    try:
        if isinstance(bbox, list) and len(bbox) > 5:
            return bbox[5] == label
        else:
            logger.error(f"bbox 格式不符合预期: {bbox}")
            return False
    except Exception as e:
        logger.error(f"检查标签存在性失败: {e}，bbox: {bbox}, label: {label}")
        return False


def labels_exists(bboxes: list, label_id: float) -> bool:
    """检查标签是否存在"""
    if not isinstance(bboxes, (list, dict)):
        logger.error(f"bboxes 数据类型错误: {type(bboxes)}，值为: {bboxes}")
        return False
    if isinstance(bboxes, list):
        if all(isinstance(item, list) and len(item) >= 6 for item in bboxes):
            return any(label_id == item[5] for item in bboxes)
        else:
            logger.error("bboxes 列表内部结构不符合预期")
            return False
    if isinstance(bboxes, dict):
        return label_id in bboxes
    return False


def getWindowShot(
        target: str = "screen",
        window_name: str = None,
        convert: bool = False,
        output_format: str = "ndarray",
        file_format: str = "png",
        file_path: str = None,
        crop_area: tuple[int, int, int, int] = None,
        preprocess: list[str] = None,
        quality: int = 50,
        debug: bool = False,
        monitor_id: int = 0,
        base64_as_str: bool = True,
) -> str | np.ndarray | bytes | None:
    """
    获取屏幕或指定窗口截图，并支持多种处理与输出选项。

    :param target: 截图目标，"screen" 或 "window"
    :param window_name: 窗口标题，仅在 target 为 "window" 时有效
    :param convert: 是否对输出数据进行 JSON 兼容性转换
    :param output_format: 输出格式，可选 'ndarray', 'file_path', 'base64'
    :param file_format: 文件存储格式，默认 'png'，可选 'jpg', 'tiff'
    :param file_path: 指定保存路径，默认 None（自动生成临时文件）
    :param crop_area: 裁剪区域 (x, y, w, h)，默认 None
    :param preprocess: 图像预处理选项列表，可选 ['resize', 'grayscale', 'blur']
    :param quality: 图像质量参数，仅在 JPEG 格式中生效，默认 50
    :param debug: 是否显示截图内容，默认 False
    :param monitor_id: 多显示器支持，默认主显示器 (0)
    :param base64_as_str: 是否将 Base64 输出作为字符串，默认 True。否则返回字节流
    :return: 处理后的截图数据，格式根据 output_format 决定
    """
    try:
        if target == "screen":
            with mss.mss() as sct:
                monitors = sct.monitors
                if monitor_id < 0 or monitor_id >= len(monitors):
                    raise ValueError(f"无效的监视器 ID: {monitor_id}")
                monitor = monitors[monitor_id]
                sct_img = sct.grab(monitor)
                img_src = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)

        elif target == "window":
            # if not window_name:
            #     raise ValueError("请指定窗口标题 (window_name)")
            # window = pwc.getWindowsWithTitle(window_name)
            # if not window:
            #     raise ValueError(f"找不到标题为 '{window_name}' 的窗口")
            wm.window_info()

            monitor = {
                "top": cfg.m_top,
                "left": cfg.m_left,
                "width": cfg.m_width,
                "height": cfg.m_height
            }
            if any(value <= 0 for value in monitor.values()):
                logger.warning("窗口参数无效，无法截取截图")
                return None

            with mss.mss() as sct:
                screen = sct.monitors[0]
                monitor["top"] = max(0, monitor["top"])
                monitor["left"] = max(0, monitor["left"])
                monitor["width"] = min(screen["width"] - monitor["left"], monitor["width"])
                monitor["height"] = min(screen["height"] - monitor["top"], monitor["height"])

                sct_img = sct.grab(monitor)
                img_src = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
        else:
            raise ValueError(f"无效的截图目标: {target}")

        if crop_area:
            x, y, w, h = crop_area
            x, y = max(0, x), max(0, y)
            w, h = max(1, w), max(1, h)
            img_src = img_src[y:y + h, x:x + w]

        if preprocess:
            img_src = preprocess_image(img_src, preprocess)

        if debug:
            cv2.imshow("Debug Screenshot", img_src)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return process_image(
            img_src,
            output_format,
            convert,
            file_format,
            quality,
            file_path,
            base64_as_str
        )

    except Exception as e:
        # logger.error(f"获取截图失败: {e}")
        return None


def preprocess_image(img: np.ndarray, operations: list[str]) -> np.ndarray:
    """
    对图像进行预处理。

    :param img: 输入图像 (numpy.ndarray)
    :param operations: 预处理操作列表
    :return: 预处理后的图像
    """
    for operation in operations:
        if operation == "resize":
            img = cv2.resize(img, (640, 480))
        elif operation == "grayscale":
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif operation == "blur":
            img = cv2.GaussianBlur(img, (5, 5), 0)
    return img


def process_image(
        img_src: np.ndarray,
        output_format: str,
        convert: bool,
        file_format: str,
        quality: int,
        file_path: str,
        base64_as_str: bool,
) -> str | np.ndarray | bytes | None:
    """
    处理图像数据为指定格式。

    :param img_src: 输入图像
    :param output_format: 输出格式，可选 'ndarray', 'file_path', 'base64'
    :param convert: 是否对输出进行 JSON 兼容转换
    :param file_format: 文件存储格式
    :param quality: 图像质量参数，仅对 JPEG 生效
    :param file_path: 指定保存路径，默认 None（自动生成临时文件）
    :param base64_as_str: 是否将 Base64 输出作为字符串，默认 True
    :return: 指定格式的图像数据
    """
    if output_format == "ndarray":
        return img_src.tolist() if convert else img_src

    elif output_format == "file_path":
        if file_path is None:
            with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as temp_file:
                file_path = temp_file.name
        if file_format.lower() == "jpg":
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
            cv2.imwrite(file_path, img_src, encode_param)
        else:
            cv2.imwrite(file_path, img_src)
        return file_path

    elif output_format == "base64":
        _, buffer = cv2.imencode(f".{file_format}", img_src)
        base64_data = base64.b64encode(buffer.tobytes())
        return base64_data.decode("utf-8") if base64_as_str else base64_data

    else:
        # logger.warning(f"未知的输出格式: {output_format}")
        return None


def getWindowShot_test():
    try:
        wm.window_info()
        monitor = {
            "top": cfg.m_top,
            "left": cfg.m_left,
            "width": cfg.m_width,
            "height": cfg.m_height
        }
        if any(value <= 0 for value in monitor.values()):
            logger.warning("窗口参数无效，无法截取截图")
            return None

        with mss.mss() as sct:
            screen = sct.monitors[0]
            # logger.info(f"屏幕边界: {screen}")
            monitor["top"] = max(0, monitor["top"])
            monitor["left"] = max(0, monitor["left"])
            monitor["width"] = min(screen["width"] - monitor["left"], monitor["width"])
            monitor["height"] = min(screen["height"] - monitor["top"], monitor["height"])

            sct_img = sct.grab(monitor)
            img_src = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            # logger.info(f"截图成功，大小: {img_src.shape}")
            return img_src
    except Exception as e:
        logger.error(f"获取窗口截图失败: {e}")
        return None


# 判断坐标是否在某个区域
def text_is_within(bbox: list, text: str) -> bool:
    try:
        text_coordinates = get_text_coordinates(text)
        if bbox and text_coordinates:
            bbox_x0, bbox_y0, bbox_x1, bbox_y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            text_x0, text_y0, text_x1, text_y1 = float(text_coordinates[0][0]), float(text_coordinates[0][1]), float(
                text_coordinates[2][0]), float(
                text_coordinates[2][1])

            return bbox_x0 < text_x1 and bbox_x1 > text_x0 and bbox_y0 < text_y1 and bbox_y1 > text_y0
        return False
    except Exception as e:
        logger.error(f"判断坐标是否在区域内失败: {e}")
        return False


def model_is_within(bboxes: list, text: str, label: float):
    try:
        text_coordinates = get_text_coordinates(text)
        if not text_coordinates:
            logger.warning("未找到文本的坐标")
            return False

        text_x0, text_y0, text_x1, text_y1 = map(float, [text_coordinates[0][0], text_coordinates[0][1],
                                                         text_coordinates[2][0], text_coordinates[2][1]])
        text_center = ((text_x0 + text_x1) / 2, (text_y0 + text_y1) / 2)
        # logger.info(f"文本中心点: {text_center}")

        nearest_button = None
        min_distance = float('inf')

        for idx, button_coordinates in enumerate(bboxes):
            try:
                if not label_exists(button_coordinates, label):
                    continue

                btn_x0, btn_y0, btn_x1, btn_y1 = map(float, button_coordinates[:4])
                btn_center = ((btn_x0 + btn_x1) / 2, (btn_y0 + btn_y1) / 2)

                distance = ((text_center[0] - btn_center[0]) ** 2 + (text_center[1] - btn_center[1]) ** 2) ** 0.5

                # logger.debug(f"按钮 {idx}: {button_coordinates}, 距离: {distance:.2f}")

                if distance < min_distance:
                    min_distance = distance
                    nearest_button = button_coordinates

            except Exception as inner_e:
                logger.warning(f"解析按钮 {idx} 时发生错误: {inner_e}")
                continue

        if nearest_button:
            # logger.info(f"最近的按钮: {nearest_button}, 距离: {min_distance:.2f}")
            return list(nearest_button)
        else:
            logger.warning("未找到符合条件的按钮")
            return False

    except Exception as e:
        logger.error(f"处理按钮点击失败: {e}")
        return False


# 检查是否有坐标在 YOLO 模型坐标内
# 返回包含坐标的bbox: [[x0, y0, x1, y1, conf, label_id]]
def check_text_in_model(bboxes: list, text: str) -> list:
    try:
        if bboxes:
            contained_coords = []
            for bbox in bboxes:
                if text_is_within(bbox, text):
                    contained_coords.append(bbox)
            return contained_coords
    except Exception as e:
        logger.error(f"检查文本在模型内失败: {e}")
    return []


# 选择bbox内距文本最近的另一bbox
def check_model_click(bboxes: list, text: str, label: float) -> None:
    try:
        if bboxes:
            bbox = model_is_within(bboxes, text, label)
            click_center_of_bboxR(bbox)
    except Exception as e:
        logger.error(f"检查模型点击失败: {e}")


def check_model_clickR(bboxes: list, text: str, label: float) -> None:
    try:
        if bboxes:
            bbox = model_is_within(bboxes, text, label)
            click_center_of_bbox(bbox)
    except Exception as e:
        logger.error(f"检查模型点击失败: {e}")


def wait_for_text(text: str) -> bool:
    MAX_TEXT_WAIT_TIME = 10
    CHECK_INTERVAL = 0.5
    start_time = time.time()
    try:
        while time.time() - start_time < MAX_TEXT_WAIT_TIME:
            if text_exists(cfg.img_src, text):
                return True
            time.sleep(CHECK_INTERVAL)
        logger.warning(f"等待文本 '{text}' 超时")
        return False
    except Exception as e:
        logger.error(f"等待文本失败: {e}")
        return False


def wait_for_model_recognition(recognition_func) -> bool:
    CHECK_INTERVAL = 0.5
    MAX_MODEL_WAIT_TIME = 5
    start_time = time.time()
    try:
        while time.time() - start_time < MAX_MODEL_WAIT_TIME:
            if recognition_func():
                return True
            time.sleep(CHECK_INTERVAL)
        logger.warning("模型识别超时")
        return False
    except Exception as e:
        logger.error(f"等待模型识别失败: {e}")
        return False


def window_update_data():
    cfg.img_src = getWindowShot()
    cfg.bboxes = getDetectionTRT(cfg.img_src)


# 随机移动鼠标并更新数据
def window_update_dataX():
    move_mouse_random()
    window_update_data()


"""WindowManager相关"""

"""YOLO推理相关"""


def yolo_inference():
    cv2.namedWindow(f"{cfg.window_name} Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"{cfg.window_name} Detection", cfg.m_width, cfg.m_height)

    last_inference_img = None

    while True:
        with cfg.lock:
            img = cfg.latest_img_src.copy() if cfg.latest_img_src is not None else None

        if img is not None and not np.array_equal(img, last_inference_img):
            bboxes = getDetectionTRT(img)
            with cfg.lock:
                cfg.latest_bboxes = bboxes

            img = drawBBox(img, bboxes)
            cv2.imshow(f"{cfg.window_name} Detection", img)
            last_inference_img = img.copy()

        if cv2.waitKey(1) & 0xFF == ord('\x1b'):
            cv2.destroyAllWindows()
            break


# def getDetection(img_src: np.ndarray) -> list:
#     result = model.predict(img_src, conf=cfg.conf, iou=cfg.iou, half=cfg.half, device='cuda:0',
#                            max_det=cfg.max_det, vid_stride=cfg.vid_stride, agnostic_nms=cfg.agnostic_nms,
#                            classes=cfg.classes, verbose=cfg.verbose)
#     bbox = result[0].boxes
#     bboxes = bbox.data.tolist()
#     return bboxes


def getDetectionTRT(img_src: np.ndarray) -> list:
    """
    使用 YoloDetector 类进行目标检测

    Args:
        img_src: 输入图像，numpy 数组

    Returns:
        检测到的边界框列表，每个边界框格式为 [x1, y1, x2, y2, conf, class_id]
    """
    detect_res = YoloTRT.inference(img_src)

    if isinstance(detect_res, (np.ndarray, list)):
        return detect_res.tolist()
    else:
        logger.error(f"Detection result is not in a valid format: {type(detect_res)}")
        return []


def getMonitor():
    with mss.mss() as sct:
        while True:
            img_src = getWindowShot("window")
            if img_src is not None:
                with cfg.lock:
                    if cfg.previous_img_src is None or not np.array_equal(img_src, cfg.previous_img_src):
                        cfg.latest_img_src = img_src
                        cfg.previous_img_src = img_src.copy()
            else:
                logger.info("No window found")
                break


def getLargestBox(bboxes, type):
    largest = -1
    bbox_largest = np.array([])
    for bbox in bboxes:
        if LABELS[int(bbox[5])] in type:
            x0, y0, x1, y1 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            area = (x1 - x0) * (y1 - y0)
            if area > largest:
                largest = area
                bbox_largest = bbox
    return bbox_largest


def drawBBox(img_src: np.ndarray, bboxes: list) -> np.ndarray:
    for bbox in bboxes:
        conf = bbox[4]
        class_id = int(bbox[5])
        if conf > cfg.conf and class_id is not None:
            x0, y0, x1, y1 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            color = [int(color) for color in COLORS[class_id]]
            cv2.rectangle(img_src, (x0, y0), (x1, y1), color, 2)
            text = "{}: {:.2f}".format(LABELS[class_id], conf)
            cv2.putText(img_src, text, (max(0, x0), max(0, y0 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return img_src


"""YOLO推理相关"""

cfg_lock = threading.Lock()


def imgsrc_update_thread():
    """更新屏幕截图"""
    while True:
        try:
            new_img_src = getWindowShot("window")
            if new_img_src is not None:
                with cfg_lock:
                    if not (cfg.img_src == new_img_src).all():
                        cfg.img_src = new_img_src
                        cfg.img_event.set()
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"imgsrc_update_thread 中的错误: {e}")


def bboxes_update_thread():
    """更新目标检测的边界框数据"""
    while True:
        try:
            with cfg_lock:
                if cfg.img_src is not None and cfg.img_src.size > 0:
                    new_bboxes = getDetectionTRT(cfg.img_src)
                    if not np.array_equal(new_bboxes, cfg.bboxes):
                        cfg.bboxes = new_bboxes
                        cfg.bboxes_event.set()
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"bbox_update_thread 中的错误: {e}")


def ocr_update_thread():
    """更新 OCR 识别结果"""
    while True:
        try:
            with cfg_lock:
                if cfg.img_src is not None and cfg.img_src.any():
                    new_ocr_result = ocrx_process(get_ocrx_data(cfg.img_src))
                    if new_ocr_result != cfg.ocr_result:
                        cfg.ocr_result = new_ocr_result
                        cfg.ocr_event.set()
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"ocr_update_thread 中的错误: {e}")


"""进程相关"""


def show_message_box(title="提示", message="这是一个消息框", icon=QMessageBox.Information):
    """
    显示消息框
    :param title: 窗口标题
    :param message: 显示内容
    :param icon: 消息框图标类型（Information, Warning, Critical, Question）
    """
    app = QApplication.instance() or QApplication([])
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.addButton(QMessageBox.Ok)
    msg_box.exec()


def show_confirmation_dialog(title="确认", message="你确定要继续吗？"):
    """
    显示确认对话框，带有“是”和“否”按钮
    :param title: 窗口标题
    :param message: 提示信息
    :return: 用户选择的布尔值，True 表示选择了“是”，False 表示选择了“否”
    """
    app = QApplication.instance() or QApplication([])
    reply = QMessageBox.question(
        None, title, message,
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    return reply == QMessageBox.Yes


def select_file(title="选择文件", file_filter="所有文件 (*)"):
    """
    文件选择对话框
    :param title: 对话框标题
    :param file_filter: 文件过滤器（如 "图片文件 (*.png *.jpg)"）
    :return: 用户选择的文件路径，未选择返回 None
    """
    app = QApplication.instance() or QApplication([])
    file_path, _ = QFileDialog.getOpenFileName(None, title, "", file_filter)
    return file_path


def select_folder(title="选择文件夹"):
    """
    文件夹选择对话框
    :param title: 对话框标题
    :return: 用户选择的文件夹路径，未选择返回 None
    """
    app = QApplication.instance() or QApplication([])
    folder_path = QFileDialog.getExistingDirectory(None, title)
    return folder_path


def get_user_input(title="输入", message="请输入内容", default_value=""):
    """
    输入对话框，获取用户输入
    :param title: 对话框标题
    :param message: 提示信息
    :param default_value: 输入框的默认值
    :return: 用户输入的字符串，点击取消返回 None
    """
    app = QApplication.instance() or QApplication([])
    text, ok = QInputDialog.getText(None, title, message, text=default_value)
    return text if ok else None


def select_from_list(title="选择", message="请选择一项", items=None):
    """
    显示下拉选择框，让用户选择列表中的一项
    :param title: 对话框标题
    :param message: 提示信息
    :param items: 可供选择的列表项
    :return: 用户选择的项，点击取消返回 None
    """
    app = QApplication.instance() or QApplication([])
    if items is None:
        items = []
    item, ok = QInputDialog.getItem(None, title, message, items, 0, False)
    return item if ok else None


def show_critical_error(title="错误", message="发生了一个严重错误！"):
    """
    显示错误消息框
    :param title: 对话框标题
    :param message: 错误信息
    """
    show_message_box(title=title, message=message, icon=QMessageBox.Critical)


def show_warning(title="警告", message="这是一个警告消息"):
    """
    显示警告消息框
    :param title: 对话框标题
    :param message: 警告信息
    """
    show_message_box(title=title, message=message, icon=QMessageBox.Warning)


def show_countdown_dialog(title="倒计时确认", message="请确认操作", countdown_time=10, default_choice=True):
    """
    显示一个带倒计时的确认对话框。
    :param title: 窗口标题
    :param message: 提示信息
    :param countdown_time: 倒计时秒数
    :param default_choice: 倒计时结束后的默认选择，True 表示“确认”，False 表示“取消”
    :return: 用户选择的布尔值，True 表示选择了“确认”，False 表示选择了“取消”
    """

    class CountdownDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.countdown_time = countdown_time
            self.user_choice = default_choice

            self.message_label = QLabel(message)
            self.message_label.setAlignment(Qt.AlignCenter)

            self.countdown_label = QLabel(f"自动选择将在 {self.countdown_time} 秒后执行")
            self.countdown_label.setAlignment(Qt.AlignCenter)
            self.countdown_label.setStyleSheet("color: red; font-weight: bold;")

            self.confirm_button = QPushButton("确认")
            self.cancel_button = QPushButton("取消")
            self.confirm_button.clicked.connect(self.confirm)
            self.cancel_button.clicked.connect(self.cancel)

            button_layout = QHBoxLayout()
            button_layout.addWidget(self.confirm_button)
            button_layout.addWidget(self.cancel_button)

            layout = QVBoxLayout()
            layout.addWidget(self.message_label)
            layout.addWidget(self.countdown_label)
            layout.addLayout(button_layout)
            self.setLayout(layout)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_countdown)
            self.timer.start(1000)

        def update_countdown(self):
            self.countdown_time -= 1
            self.countdown_label.setText(f"自动选择将在 {self.countdown_time} 秒后执行")
            if self.countdown_time <= 0:
                self.timer.stop()
                self.accept()

        def confirm(self):
            self.user_choice = True
            self.accept()

        def cancel(self):
            self.user_choice = False
            self.accept()

    app = QApplication.instance() or QApplication([])
    dialog = CountdownDialog()
    dialog.exec()
    return dialog.user_choice


def show_multiselect_dialog(title="多选对话框", options=None):
    """
    简单的多选对话框。
    :param title: 对话框标题
    :param options: 可选项列表
    :return: 用户选择的列表
    """
    if options is None:
        options = []

    class MultiSelectDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.selected_items = []

            self.list_widget = QListWidget()
            self.list_widget.addItems(options)
            self.list_widget.setSelectionMode(QListWidget.MultiSelection)

            self.ok_button = QPushButton("确定")
            self.cancel_button = QPushButton("取消")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

            layout = QVBoxLayout()
            layout.addWidget(self.list_widget)
            layout.addWidget(self.ok_button)
            layout.addWidget(self.cancel_button)
            self.setLayout(layout)

        def accept(self):
            self.selected_items = [item.text() for item in self.list_widget.selectedItems()]
            super().accept()

    app = QApplication.instance() or QApplication([])
    dialog = MultiSelectDialog()
    if dialog.exec():
        return dialog.selected_items
    return []


def show_checkbox_multiselect_dialog(title="多选对话框", options=None):
    """
    使用复选框的多选对话框。
    :param title: 对话框标题
    :param options: 可选项列表
    :return: 用户选择的列表
    """
    if options is None:
        options = []

    class CheckBoxDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.selected_items = []

            self.layout = QVBoxLayout()
            self.checkboxes = []

            for option in options:
                checkbox = QCheckBox(option)
                self.layout.addWidget(checkbox)
                self.checkboxes.append(checkbox)

            self.ok_button = QPushButton("确定")
            self.cancel_button = QPushButton("取消")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
            self.layout.addWidget(self.ok_button)
            self.layout.addWidget(self.cancel_button)

            self.setLayout(self.layout)

        def accept(self):
            self.selected_items = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
            super().accept()

    app = QApplication.instance() or QApplication([])
    dialog = CheckBoxDialog()
    if dialog.exec():
        return dialog.selected_items
    return []


def show_tree_multiselect_dialog(title="多选对话框", options=None):
    """
    树状结构的多选对话框。
    :param title: 对话框标题
    :param options: 可选项字典，键是父项，值是子项列表
    :return: 用户选择的列表
    """
    if options is None:
        options = {}

    class TreeDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.selected_items = []

            self.tree_widget = QTreeWidget()
            self.tree_widget.setHeaderHidden(True)

            for parent, children in options.items():
                parent_item = QTreeWidgetItem(self.tree_widget, [parent])
                for child in children:
                    child_item = QTreeWidgetItem(parent_item, [child])
                    child_item.setCheckState(0, Qt.Unchecked)

            self.ok_button = QPushButton("确定")
            self.cancel_button = QPushButton("取消")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

            layout = QVBoxLayout()
            layout.addWidget(self.tree_widget)
            layout.addWidget(self.ok_button)
            layout.addWidget(self.cancel_button)
            self.setLayout(layout)

        def accept(self):
            for i in range(self.tree_widget.topLevelItemCount()):
                parent_item = self.tree_widget.topLevelItem(i)
                for j in range(parent_item.childCount()):
                    child_item = parent_item.child(j)
                    if child_item.checkState(0) == Qt.Checked:
                        self.selected_items.append(child_item.text(0))
            super().accept()

    app = QApplication.instance() or QApplication([])
    dialog = TreeDialog()
    if dialog.exec():
        return dialog.selected_items
    return []


def show_searchable_multiselect_dialog(title="多选对话框", options=None):
    """
    可搜索的多选对话框。
    :param title: 对话框标题
    :param options: 可选项列表
    :return: 用户选择的列表
    """
    if options is None:
        options = []

    class SearchableDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.selected_items = []
            self.all_options = options

            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("搜索...")
            self.search_box.textChanged.connect(self.filter_options)

            self.list_widget = QListWidget()
            self.list_widget.addItems(options)
            self.list_widget.setSelectionMode(QListWidget.MultiSelection)

            self.ok_button = QPushButton("确定")
            self.cancel_button = QPushButton("取消")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

            layout = QVBoxLayout()
            layout.addWidget(self.search_box)
            layout.addWidget(self.list_widget)
            layout.addWidget(self.ok_button)
            layout.addWidget(self.cancel_button)
            self.setLayout(layout)

        def filter_options(self, text):
            self.list_widget.clear()
            filtered_options = [opt for opt in self.all_options if text.lower() in opt.lower()]
            self.list_widget.addItems(filtered_options)

        def accept(self):
            self.selected_items = [item.text() for item in self.list_widget.selectedItems()]
            super().accept()

    app = QApplication.instance() or QApplication([])
    dialog = SearchableDialog()
    if dialog.exec():
        return dialog.selected_items
    return []


def show_grouped_checkbox_multiselect_dialog(title="分组多选对话框", options=None):
    """
    分组复选框多选对话框。
    :param title: 对话框标题
    :param options: 可选项字典，键为组名，值为该组的选项列表
    :return: 用户选择的列表
    """
    if options is None:
        options = {}

    class GroupedDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.selected_items = []

            self.layout = QVBoxLayout()
            self.checkboxes = []

            for group_name, group_options in options.items():
                group_box = QGroupBox(group_name)
                group_layout = QVBoxLayout()
                for option in group_options:
                    checkbox = QCheckBox(option)
                    group_layout.addWidget(checkbox)
                    self.checkboxes.append(checkbox)
                group_box.setLayout(group_layout)
                self.layout.addWidget(group_box)

            self.ok_button = QPushButton("确定")
            self.cancel_button = QPushButton("取消")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

            button_layout = QHBoxLayout()
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.cancel_button)
            self.layout.addLayout(button_layout)

            self.setLayout(self.layout)

        def accept(self):
            self.selected_items = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
            super().accept()

    app = QApplication.instance() or QApplication([])
    dialog = GroupedDialog()
    if dialog.exec():
        return dialog.selected_items
    return []


def show_paginated_multiselect_dialog(title="分页多选对话框", options=None, items_per_page=10):
    """
    带分页的多选对话框。
    :param title: 对话框标题
    :param options: 可选项列表
    :param items_per_page: 每页显示的选项数量
    :return: 用户选择的列表
    """
    if options is None:
        options = []

    class PaginatedDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.selected_items = []
            self.current_page = 0

            self.total_pages = (len(options) + items_per_page - 1) // items_per_page
            self.stacked_widget = QStackedWidget()

            for i in range(self.total_pages):
                page_list_widget = QListWidget()
                start_idx = i * items_per_page
                end_idx = min(start_idx + items_per_page, len(options))
                page_list_widget.addItems(options[start_idx:end_idx])
                page_list_widget.setSelectionMode(QListWidget.MultiSelection)
                self.stacked_widget.addWidget(page_list_widget)

            self.prev_button = QPushButton("上一页")
            self.next_button = QPushButton("下一页")
            self.ok_button = QPushButton("确定")
            self.cancel_button = QPushButton("取消")

            self.prev_button.clicked.connect(self.show_prev_page)
            self.next_button.clicked.connect(self.show_next_page)
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

            layout = QVBoxLayout()
            layout.addWidget(self.stacked_widget)

            button_layout = QHBoxLayout()
            button_layout.addWidget(self.prev_button)
            button_layout.addWidget(self.next_button)
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)

            self.setLayout(layout)
            self.update_buttons()

        def show_prev_page(self):
            if self.current_page > 0:
                self.current_page -= 1
                self.stacked_widget.setCurrentIndex(self.current_page)
                self.update_buttons()

        def show_next_page(self):
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self.stacked_widget.setCurrentIndex(self.current_page)
                self.update_buttons()

        def update_buttons(self):
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.total_pages - 1)

        def accept(self):
            for i in range(self.total_pages):
                page_widget = self.stacked_widget.widget(i)
                self.selected_items.extend([item.text() for item in page_widget.selectedItems()])
            super().accept()

    app = QApplication.instance() or QApplication([])
    dialog = PaginatedDialog()
    if dialog.exec():
        return dialog.selected_items
    return []


def kill_process(process_name: str):
    """
    杀死指定名称的进程。

    Args:
        process_name: 要杀死的进程名称。
    """
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == process_name:
                proc.kill()
                # print(f"进程 {process_name} (PID: {proc.info['pid']}) 已杀死")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def is_process_running(process_name: str) -> bool:
    """
  检测指定名称的进程是否存在。

  Args:
      process_name: 要检测的进程名称。

  Returns:
      如果进程存在则返回 True，否则返回 False。
  """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


wm = WindowManager()

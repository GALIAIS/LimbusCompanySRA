# -*- coding: utf-8 -*-
import ctypes
import json
import logging
import random
import re
import tempfile
import threading
import time
from pathlib import Path
import cv2
import mss
import numpy as np
import psutil
import pyautogui
import pydirectinput as pdi
import pywinctl as pwc
import win32gui
from attrs import define
from loguru import logger
# from paddleocr import PaddleOCR
from src.app.utils.ConfigManager import cfgm
from src.common.config import config as cfg
from src.data.Labels import Labels_ID, LABELS, COLORS
from src.common.tensorrt.infer import YoloTRT
from src.common.paddleocr_json.PPOCR_api import GetOcrApi
from src.common.paddleocr_json.tbpu import GetParser

# model = YOLO(cfg.model_path)
root_path = Path(__file__).resolve().parents[2]
cfgm.set("BaseSetting.root_path", str(root_path))

img_lock = threading.Lock()
ocr_lock = threading.Lock()
bboxes_lock = threading.Lock()
logging.disable(logging.DEBUG)
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
def mouse_click(x, y, clicks=1, interval=0.0, button="left"):
    try:
        pdi.click(x, y, clicks, interval, button)
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
def click_center_of_bbox(bbox: list, clicks: int = 1) -> None:
    """点击指定边界框的中心位置"""
    try:
        if bbox and isinstance(bbox[0], list):
            bbox = bbox[0]
        x0, y0, x1, y1 = map(int, bbox[:4])
        target_coords = ((x0 + x1) // 2, (y0 + y1) // 2)
        move_mouse_to(*get_mouse_pos(), *target_coords)
        mouse_click(*target_coords, clicks, interval=1, button="left")
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
def click_center_of_bboxR(bbox: list, clicks: int = 1, offset_ratio: tuple = (0.05, 0.5)) -> None:
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
            mouse_click(*target_coords, clicks, interval=1, button="left")
        else:
            logger.warning("无效的边界框格式，无法点击")
    except IndexError:
        logger.error("边界框坐标不足，无法执行点击操作")
    except Exception as e:
        logger.error(f"点击边界框中心失败: {e}")


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
def mouse_scroll(clicks=-10):
    try:
        pdi.scroll(clicks)
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
exePath = str(root_path / "src" / "3rdparty" / "PaddleOCR-json_v1.4.1" / "PaddleOCR-json.exe")
modelsPath = str(root_path / "src" / "3rdparty" / "PaddleOCR-json_v1.4.1" / "models")
configPath = str(root_path / "src" / "3rdparty" / "PaddleOCR-json_v1.4.1" / "models" / "config_chinese.txt")
argument = {"config_path": configPath}
# ocr = PaddleOCR(use_angle_cls=True, lang="ch")
ocrx = GetOcrApi(exePath, modelsPath)


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


def save_temp_image(img_src: np.ndarray) -> str:
    """
    将 numpy.ndarray 图像保存为临时文件，并返回文件路径。

    :param img_src: 输入的 numpy.ndarray 图像
    :return: 临时文件路径
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(temp_file.name, img_src)
    return temp_file.name


# PaddleOCR-json的获取数据函数
def get_ocrx_data(img_src: np.ndarray) -> dict:
    """
    从 OCR 模型中获取检测结果并验证数据格式。

    :param img_src: 输入图像的 numpy.ndarray 格式
    :return: 包含 OCR 检测结果的字典或空字典
    """
    try:
        if img_src is None:
            raise ValueError("输入图像数据为空")
        if not isinstance(img_src, np.ndarray):
            raise ValueError("输入图像数据不是 numpy.ndarray 类型")
        if img_src.size == 0:
            raise ValueError("输入图像数据为空")

        temp_file_path = save_temp_image(img_src)

        ocr_result = ocrx.run(temp_file_path)

        if not ocr_result or not isinstance(ocr_result, dict):
            raise ValueError("OCR 结果为空或格式不正确")
        if "code" not in ocr_result or "data" not in ocr_result:
            raise ValueError("OCR 返回的数据结构不完整")
        if ocr_result["code"] != 100:
            raise ValueError(f"OCR 执行失败，状态码: {ocr_result['code']}")

        data = ocr_result["data"]
        if not isinstance(data, list):
            raise ValueError("OCR 数据格式错误，data 应为列表类型")

        for item in data:
            if not isinstance(item, dict):
                raise ValueError("OCR 数据项格式错误，item 应为字典类型")
            if "box" not in item or "text" not in item or "score" not in item:
                raise ValueError("OCR 数据项缺少必要字段")
            if not isinstance(item["box"], list) or len(item["box"]) != 4:
                raise ValueError(f"OCR 检测框格式错误: {item['box']}")
            if not isinstance(item["text"], str):
                raise ValueError(f"OCR 文本格式错误: {item['text']}")
            if not isinstance(item["score"], (float, int)):
                raise ValueError(f"OCR 置信度格式错误: {item['score']}")

        return ocr_result

    except ValueError as e:
        logger.error(f"OCR 数据验证失败: {e}")
        return {}
    except Exception as e:
        logger.error(f"OCR 数据获取失败: {e}")
        return {}


def text_exists(
        img_src: np.ndarray,
        text: str,
        flag: bool = False,
        confidence_threshold: float = 0.8
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


# 获取ocr_text的坐标
def get_text_coordinates(text: str) -> list:
    try:
        img_src = getWindowShot()
        if img_src is not None:
            result = ocrx_process(get_ocrx_data(img_src))
            pattern = re.compile(text)
            for res in result:
                if pattern.search(res['text']):
                    return res['coordinates']
        return []
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
        if not ocr_result or not isinstance(ocr_result, dict):
            logger.warning("OCR 结果为空或格式不正确")
            return result_list

        data = ocr_result.get("data", [])
        if not isinstance(data, list):
            logger.warning("OCR 数据格式错误，'data' 应为列表")
            return result_list

        for item in data:
            if not isinstance(item, dict):
                logger.warning("OCR 文本块格式错误，非字典类型")
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


def check_text_and_click(pattern: str, clicks: int = 1):
    """匹配文本并点击对应的选项"""
    result_check = check_text_in_model(cfg.bboxes, pattern)
    if result_check:
        click_center_of_bbox(result_check, clicks)


def check_text_and_clickR(pattern: str, clicks: int = 1):
    """匹配文本并点击对应的选项"""
    result_check = check_text_in_model(cfg.bboxes, pattern)
    if result_check:
        click_center_of_bboxR(result_check, clicks)


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
            window = pwc.getWindowsWithTitle(cfg.window_name)[0]
            if window:
                bbox = window.box
                cfg.m_top = bbox.top + 38
                cfg.m_left = bbox.left + 10
                cfg.m_width = bbox.width - 20
                cfg.m_height = bbox.height - 45

                self.screen_size = pdi.virtual_size()
                cfg.update_screen_size(self.screen_size[2], self.screen_size[3], self.screen_size[0],
                                       self.screen_size[1])
                self.window = pwc.getWindowsWithTitle(self.window_name)

                if self.window:
                    self.window_size = self.window[0].box
                    cfg.update_window_position(self.window_size[0], self.window_size[1], self.window_size[2],
                                               self.window_size[3])
                    return self.window_size
            return None
        except Exception as e:
            logger.error(f"获取窗口信息失败: {e}")
            return None

    def init_window(self):
        try:
            self.window = pwc.getWindowsWithTitle(self.window_name)
            if self.window:
                self.hwnd = self.window[0].getHandle()
                self.result = True
                cfg.handle = self.hwnd
                if self.window[0].isMinimized:
                    self.window[0].restore()
                self.window[0].raiseWindow()
                self.window[0].activate()
                self.window[0].maximize()
            return True
        except Exception as e:
            logger.error(f"初始化窗口失败: {e}")
            return False

    def get_dpi_scale(self):
        try:
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            hdc = win32gui.GetDC(None)

            # 获取逻辑宽度和高度
            logical_width = gdi32.GetDeviceCaps(hdc, 8)
            logical_height = gdi32.GetDeviceCaps(hdc, 10)

            # 获取系统真实宽度和高度
            physical_width = user32.GetSystemMetrics(0)
            physical_height = user32.GetSystemMetrics(1)

            # 计算 DPI 缩放因子
            width_scale = logical_width / physical_width
            height_scale = logical_height / physical_height

            # 获取系统 DPI
            cfg.system_dpi = user32.GetDpiForSystem()

            # 更新到配置
            cfg.width_scale = width_scale
            cfg.height_scale = height_scale
            cfg.original_width = physical_width
            cfg.original_height = physical_height
        except Exception as e:
            logger.error(f"获取 DPI 缩放失败: {e}")

    def get_pid(self):
        try:
            self.pid = str(psutil.process_iter())
            for self.process in self.pid:
                if self.process.name() == cfg.window_process_name:
                    cfg.pid = self.process.pid
                    return self.process.pid
        except Exception as e:
            logger.error(f"获取 PID 失败: {e}")
            return None

    def get_hwnd(self):
        try:
            self.process = pwc.getWindowsWithTitle(self.window_name)
            if self.process:
                self.hwnd = self.process[0].getHandle()
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
            return self.window[0].isMinimized() if self.window else False
        except Exception as e:
            logger.error(f"检查窗口是否最小化失败: {e}")
            return False

    def is_active(self):
        try:
            return self.window[0].isActive() if self.window else False
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
def check_label_and_click(bboxes: list, label: str, clicks: int = 1) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]):
                    click_center_of_bbox(bbox, clicks)
                    break
    except Exception as e:
        logger.error(f"检查标签失败: {e}")


def check_label_and_clickR(bboxes: list, label: str, clicks: int = 1) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, Labels_ID[label]):
                    click_center_of_bboxR(bbox, clicks)
                    break
    except Exception as e:
        logger.error(f"检查标签失败: {e}")


# 检查Label_ID是否存在并移动鼠标点击按钮
def check_label_id_and_click(bboxes: list, label_id: float, clicks: int = 1) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, label_id):
                    click_center_of_bbox(bbox, clicks)
                    break
    except Exception as e:
        logger.error(f"检查标签 ID 失败: {e}")


def check_label_id_and_clickR(bboxes: list, label_id: float, clicks: int) -> None:
    try:
        if bboxes:
            for bbox in bboxes:
                if label_exists(bbox, label_id):
                    click_center_of_bboxR(bbox, clicks)
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


def getWindowShot():
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


# def window_update_data():
#     cfg.img_src = getWindowShot()
#     cfg.bboxes = getDetection(cfg.img_src)
def window_update_data():
    cfg.img_src = getWindowShot()
    cfg.bboxes = getDetectionTRT(cfg.img_src)


# 随机移动鼠标并更新数据
def window_update_dataX():
    move_mouse_random()
    window_update_data()


# IMGSRC数据更新
# def imgsrc_update_thread():
#     while True:
#         with cfg.lock:
#             cfg.img_src = getWindowShot()
#             img_update_event.set()
#             time.sleep(0.5)
# BBOXES数据更新
# def bbox_update_thread():
#     while True:
#         with cfg.lock:
#             cfg.bboxes = getDetection(cfg.img_src)
#             bboxes_update_event.set()
#             time.sleep(0.5)
# OCR数据更新
# def ocr_update_thread():
#     while True:
#         with cfg.lock:
#             cfg.ocr_result = ocr_process(get_ocr_data(cfg.img_src))
#             ocr_result_event.set()
#             time.sleep(0.5)


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
            img_src = getWindowShot()
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

"""线程"""


def imgsrc_update_thread():
    """更新屏幕截图"""
    while True:
        try:
            new_img_src = getWindowShot()
            if new_img_src is not None and not (cfg.img_src == new_img_src).all():
                cfg.img_src = new_img_src
                cfg.img_event.set()
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"imgsrc_update_thread 中的错误: {e}")


# def bboxes_update_thread():
#     """更新目标检测的边界框数据"""
#     while True:
#         try:
#             if cfg.img_src is not None and np.any(cfg.img_src):
#                 new_bboxes = getDetection(cfg.img_src)
#                 if new_bboxes != cfg.bboxes:
#                     cfg.bboxes = new_bboxes
#                     cfg.bboxes_event.set()
#             time.sleep(1)
#         except Exception as e:
#             logger.error(f"bbox_update_thread 中的错误: {e}")
#             break
def bboxes_update_thread():
    """更新目标检测的边界框数据"""
    while True:
        try:
            if cfg.img_src is not None and cfg.img_src.size > 0:
                new_bboxes = getDetectionTRT(cfg.img_src)
                if not np.array_equal(new_bboxes, cfg.bboxes):
                    cfg.bboxes = new_bboxes
                    cfg.bboxes_event.set()
            time.sleep(1)
        except Exception as e:
            logger.error(f"bbox_update_thread 中的错误: {e}")
            break


def ocr_update_thread():
    """更新 OCR 识别结果"""
    while True:
        try:
            if cfg.img_src is not None and cfg.img_src.any():
                new_ocr_result = ocrx_process(get_ocrx_data(cfg.img_src))
                if new_ocr_result != cfg.ocr_result:
                    cfg.ocr_result = new_ocr_result
                    cfg.ocr_event.set()
            time.sleep(2)
        except Exception as e:
            logger.error(f"ocr_update_thread 中的错误: {e}")
            break


def load_event_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


wm = WindowManager()

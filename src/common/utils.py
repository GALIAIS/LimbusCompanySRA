# -*- coding: utf-8 -*-
import sys
import logging
from attrs import asdict, define, make_class, Factory
import pydirectinput as pdi
from ultralytics import YOLO
import pyautogui
import random
import psutil
import ctypes
import pywinctl as pwc
import win32gui
import cv2
import threading
import time
import re
import mss
import numpy as np
from loguru import logger
from paddleocr import PaddleOCR, draw_ocr
from PySide6.QtWidgets import QApplication

logging.disable(logging.DEBUG)

from src.common.config import config as cfg
from src.data.Labels import Labels_ID, LABELS, COLORS

model = YOLO(cfg.absolute_model_path)

img_lock = threading.Lock()
ocr_lock = threading.Lock()
bboxes_lock = threading.Lock()

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
            y_offset = int(height * offset_ratio[1] + random.uniform(-20, 20))
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


# 计算边界框的中心位置
def center_of_bbox(bbox: list) -> tuple:
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
ocr = PaddleOCR(use_angle_cls=True, lang="ch")


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

def get_ocr_data(img_src: np.ndarray) -> list:
    try:
        if img_src is not None:
            if not isinstance(img_src, np.ndarray):
                raise ValueError("输入图像数据不是 numpy.ndarray 类型")
            if img_src.size == 0:
                raise ValueError("输入图像数据为空")
            ocr_result = ocr.ocr(img_src, cls=True)
            if not ocr_result or not isinstance(ocr_result, list):
                raise ValueError("OCR 结果为空或格式不正确")
            return ocr_result
        return []
    except IndexError as e:
        logger.error(f"OCR 数据获取失败 - 索引错误: {e}")
        return []
    except Exception as e:
        logger.error(f"OCR 数据获取失败: {e}")
        return []


def text_exists(img_src: np.ndarray, text: str, flag: bool = False) -> bool:
    try:
        if img_src is not None:
            result = ocr_process(get_ocr_data(img_src))
            if flag:
                print(result)
            pattern = re.compile(text)
            for res in result:
                if pattern.search(res['text']):
                    return True
            return False
        return False
    except Exception as e:
        logger.error(f"文本检测失败: {e}")
        return False


# 获取ocr_text的坐标
def get_text_coordinates(text: str) -> list:
    try:
        img_src = getWindowShot()
        if img_src is not None:
            result = ocr_process(get_ocr_data(img_src))
            pattern = re.compile(text)
            for res in result:
                if pattern.search(res['text']):
                    return res['coordinates']
        return []
    except Exception as e:
        logger.error(f"获取文本坐标失败: {e}")
        return []


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
            self.pid = psutil.process_iter()
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
        with mss.mss() as sct:
            wm.window_info()
            monitor = {
                "top": cfg.m_top,
                "left": cfg.m_left,
                "width": cfg.m_width,
                "height": cfg.m_height
            }
            if monitor["width"] > 0 and monitor["height"] > 0:
                sct_img = sct.grab(monitor)
                img_src = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
                return img_src
            return None
    except Exception as e:
        logger.error(f"获取窗口截图失败: {e}")
        return None


# def getWinShot():
#     try:
#         hwnd = wm.get_hwnd()
#         if hwnd is None:
#             logger.error("无法获取窗口句柄")
#             return None
#         img = screen.grabWindow(hwnd).toImage()
#         if img.isNull():
#             logger.error("截图失败，未获取到图像")
#             return None
#         bgra = img.constBits()
#         bgra.setsize(img.bytesPerLine() * img.height())
#         img_np = np.frombuffer(bgra, dtype=np.uint8).reshape((img.height(), img.width(), 4))
#
#         img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
#         return img_rgb
#     except AttributeError as e:
#         logger.error("获取窗口句柄时发生 AttributeError，可能窗口不存在或不可见。")
#         logger.exception(e)
#     except MemoryError:
#         logger.error("内存不足，截图失败。")
#     except Exception as e:
#         logger.error(f"未知错误: {e}")
#         logger.exception(e)
#     return None


# 判断坐标是否在某个区域
def is_within(bbox: list, text: str) -> bool:
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


# 检查是否有坐标在 YOLO 模型坐标内
# 返回包含坐标的bbox: [[x0, y0, x1, y1, conf, label_id]]
def check_text_in_model(bboxes: list, text: str) -> list:
    try:
        if bboxes:
            contained_coords = []
            for bbox in bboxes:
                if is_within(bbox, text):
                    contained_coords.append(bbox)
            return contained_coords
    except Exception as e:
        logger.error(f"检查文本在模型内失败: {e}")
    return []


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
    cfg.bboxes = getDetection(cfg.img_src)


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
            bboxes = getDetection(img)
            with cfg.lock:
                cfg.latest_bboxes = bboxes

            img = drawBBox(img, bboxes)
            cv2.imshow(f"{cfg.window_name} Detection", img)
            last_inference_img = img.copy()

        if cv2.waitKey(1) & 0xFF == ord('\x1b'):
            cv2.destroyAllWindows()
            break


def getDetection(img_src: np.ndarray) -> list:
    result = model.predict(img_src, conf=cfg.conf, iou=cfg.iou, half=cfg.half, device='cuda:0',
                           max_det=cfg.max_det, vid_stride=cfg.vid_stride, agnostic_nms=cfg.agnostic_nms,
                           classes=cfg.classes, verbose=cfg.verbose)
    bbox = result[0].boxes
    bboxes = bbox.data.tolist()
    return bboxes


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


def bboxes_update_thread():
    """更新目标检测的边界框数据"""
    while True:
        try:
            if cfg.img_src is not None and cfg.img_src.any():
                new_bboxes = getDetection(cfg.img_src)
                if new_bboxes != cfg.bboxes:
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
                new_ocr_result = ocr_process(get_ocr_data(cfg.img_src))
                if new_ocr_result != cfg.ocr_result:
                    cfg.ocr_result = new_ocr_result
                    cfg.ocr_event.set()
            time.sleep(2)
        except Exception as e:
            logger.error(f"ocr_update_thread 中的错误: {e}")
            break


wm = WindowManager()

# -*- coding: utf-8 -*-
import os
import sys
import torch
from ultralytics import YOLO
import threading
import cv2
from mss import mss
import mss
import pywinctl as pwc
import numpy as np
from time import time, sleep
from loguru import logger
from typing import Optional
from src.common.utils import *

model = YOLO(cfg.absolute_model_path)

COLORS = [
    (56, 158, 13), (92, 219, 211), (9, 109, 217), (173, 198, 255), (146, 84, 222), (247, 89, 171),
    (255, 163, 158), (212, 56, 13), (255, 192, 105), (173, 139, 0), (211, 242, 97), (56, 158, 13),
    (92, 219, 211), (173, 198, 255), (146, 84, 222), (247, 89, 171), (255, 163, 158), (212, 56, 13),
    (255, 192, 105), (173, 139, 0), (211, 242, 97), (56, 158, 13), (92, 219, 211), (9, 109, 217),
    (173, 198, 255), (146, 84, 222), (247, 89, 171), (255, 163, 158), (212, 56, 13), (173, 139, 0),
    (211, 242, 97), (56, 158, 13), (92, 219, 211), (9, 109, 217), (146, 84, 222), (247, 89, 171),
    (255, 163, 158), (212, 56, 13), (255, 192, 105), (173, 139, 0), (211, 242, 97), (212, 56, 13),
    (255, 163, 158), (212, 56, 13), (255, 163, 158), (212, 56, 13), (255, 192, 105),
    (0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0),
    (128, 0, 128), (255, 165, 0), (128, 128, 0), (192, 192, 192), (255, 20, 147), (210, 180, 140),
    (34, 139, 34), (255, 99, 71), (75, 0, 130), (255, 228, 225), (255, 228, 181), (153, 50, 204),
    (139, 69, 19), (255, 127, 80), (240, 230, 140), (245, 222, 179), (0, 100, 0), (205, 92, 92),
    (135, 206, 250), (255, 240, 245), (218, 112, 214), (240, 128, 128), (255, 239, 196), (0, 255, 127), (176, 84, 222)
]

LABELS = [
    "Active Node", "Advantage-High", "Advantage-Very High", "Available Node",
    "Back", "Battle Node", "Boss", "Cancel", "Character", "Clear Selection",
    "Confirm", "Continue", "Current Node", "Damage", "Dispense", "Drive",
    "E.G.O", "E.G.O Gift", "EXP", "Encounter Reward Card", "End Node",
    "Enemy", "Enkephalin", "Enter", "Event Node", "Event Option",
    "Explored Node", "Extract", "Give Up", "Halt Exploration", "Heal Sinner",
    "Inactive Button", "Leava", "Luxcavation", "Mailbox", "Mirror Dungeon",
    "Refresh", "Resume", "Safe Node", "Settings", "Sinner", "Skip", "Start",
    "Start Node", "Themes Pack", "Therter", "Thread", "Unavailable Node",
    "Win Rate", "Window", "Pause"
]

wm = WindowManager()


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


# def getWindowShot():
#     with mss.mss() as sct:
#         wm.window_info()
#         monitor = {
#             "top": cfg.m_top,
#             "left": cfg.m_left,
#             "width": cfg.m_width,
#             "height": cfg.m_height
#         }
#         if monitor["width"] > 0 and monitor["height"] > 0:
#             sct_img = sct.grab(monitor)
#             img_src = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
#             return img_src
#         return None


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


def window_update_data():
    cfg.img_src = getWindowShot()
    cfg.bboxes = getDetection(cfg.img_src)


# 随机移动鼠标并更新数据
def window_update_dataX():
    move_mouse_random()
    window_update_data()


# 仅更新数据
def window_update_thread():
    while True:
        window_update_data()  # 实时更新屏幕信息
        time.sleep(0.1)

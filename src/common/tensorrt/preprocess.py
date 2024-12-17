# -*- coding:utf-8 -*-

"""
    YOLO 图像预处理
"""

import cv2
import numpy as np


def letterbox(img, new_shape=(1024, 1024), color=(114, 114, 114)):
    """
    调整图像到指定的形状，保持原始比例并填充边界。

    参数:
        img: numpy.ndarray，输入图像。
        new_shape: tuple 或 int，目标形状（宽，高）。
        color: tuple，填充边界的颜色。

    返回:
        img: numpy.ndarray，经过调整和填充后的图像。
        ratio: tuple，调整的宽高比例。
        (dw, dh): tuple，填充的宽高边界。
    """
    shape = img.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # 计算缩放比例
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    ratio = (r, r)

    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))

    dw = (new_shape[1] - new_unpad[0]) / 2
    dh = (new_shape[0] - new_unpad[1]) / 2

    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(dh), int(dh + 0.5)
    left, right = int(dw), int(dw + 0.5)

    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return img, ratio, (dw, dh)


def preprocess(np_img, dst_height, dst_width):
    """
    对图像进行预处理，调整大小、归一化等。

    参数:
        np_img: numpy.ndarray，输入图像。
        dst_height: int，目标高度。
        dst_width: int，目标宽度。

    返回:
        img: numpy.ndarray，预处理后的图像，形状为 (3, dst_height, dst_width)。
    """
    img, _, _ = letterbox(np_img, (dst_height, dst_width))

    img = img[:, :, ::-1]
    img = np.transpose(img, (2, 0, 1))

    img = img / 255.0

    img = np.ascontiguousarray(img, dtype=np.float32)

    return img

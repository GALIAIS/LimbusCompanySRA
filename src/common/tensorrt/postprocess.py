# -*- coding:utf-8 -*-

"""
    YOLO11 图像预处理
"""

import numpy as np


def xywh2xyxy(bboxes):
    bboxes = bboxes.astype(np.float64)
    out = bboxes.copy()
    out[:, 0] = bboxes[:, 0] - bboxes[:, 2] / 2
    out[:, 1] = bboxes[:, 1] - bboxes[:, 3] / 2
    out[:, 2] = bboxes[:, 0] + bboxes[:, 2] / 2
    out[:, 3] = bboxes[:, 1] + bboxes[:, 3] / 2
    return out


def nms(bboxes, scores, threshold=0.5):
    bboxes = bboxes.astype(np.float64)
    scores = scores.astype(np.float64)
    x1 = bboxes[:, 0]
    y1 = bboxes[:, 1]
    x2 = bboxes[:, 2]
    y2 = bboxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h

        iou = inter / (areas[i] + areas[order[1:]] - inter)

        indexes = np.where(iou <= threshold)[0]
        order = order[indexes + 1]
    return np.array(keep, dtype=int)


def clip_coords(boxes, img_shape):
    boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, img_shape[1])
    boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, img_shape[0])


def scale_coords(img1_shape, coords, img0_shape):
    gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])
    pad = (
        max(0, (img1_shape[1] - img0_shape[1] * gain) / 2),
        max(0, (img1_shape[0] - img0_shape[0] * gain) / 2),
    )

    coords[:, [0, 2]] -= pad[0]
    coords[:, [1, 3]] -= pad[1]
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


def postprocess(img0, prediction, conf_thres, iou_thres, input_h, input_w):
    if not prediction.shape[0]:
        return np.empty((0, 6), dtype=np.float64)

    xc = prediction[4:].max(0) > conf_thres
    prediction = prediction.transpose((1, 0))
    x = prediction[xc]

    if not x.shape[0]:
        return np.empty((0, 6), dtype=np.float64)

    box = x[:, :4]
    cls = x[:, 4:]

    i, j = np.where(cls > conf_thres)
    x = np.concatenate((box[i], x[i, 4 + j, None], j[:, None]), 1)

    bboxes = xywh2xyxy(x)

    detected_objects = []
    for label in np.unique(bboxes[:, 5]):
        selected_bboxes = bboxes[bboxes[:, 5] == label]
        keep_indices = nms(selected_bboxes[:, :4], selected_bboxes[:, 4], iou_thres)
        detected_objects.append(selected_bboxes[keep_indices])

    if detected_objects:
        detected_objects = np.vstack(detected_objects)
    else:
        return np.empty((0, 6), dtype=np.float64)

    detected_objects[:, :4] = scale_coords((input_h, input_w), detected_objects[:, :4], img0.shape[:2])

    result = np.zeros_like(detected_objects, dtype=np.float64)
    result[:, :4] = np.around(detected_objects[:, :4], decimals=10)
    result[:, 4] = np.around(detected_objects[:, 4], decimals=10)
    result[:, 5] = detected_objects[:, 5] + 0.0

    return result

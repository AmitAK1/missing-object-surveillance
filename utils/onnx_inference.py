"""Lightweight ONNXRuntime-based inference helper for YOLOv8-exported ONNX models.

This module provides a small wrapper to run detection on Raspberry Pi using
`onnxruntime`. It implements preprocessing, running the model, simple postprocessing,
and non-maximum suppression. It is intentionally minimal — use this for smoke-tests
and Pi deployments where `torch` is not available.
"""
from typing import List, Tuple, Dict
import numpy as np
import cv2


def load_onnx_model(path: str):
    try:
        import onnxruntime as ort
    except Exception as e:
        raise ImportError(f"onnxruntime is required for ONNX inference: {e}")

    providers = None
    try:
        # Prefer CPUExecutionProvider by default; platform-specific providers may be available
        providers = ['CPUExecutionProvider']
        sess = ort.InferenceSession(path, providers=providers)
    except Exception:
        # fallback to default
        sess = ort.InferenceSession(path)
    return sess


def preprocess(frame: np.ndarray, imgsz: int = 640) -> Tuple[np.ndarray, float, float]:
    h, w = frame.shape[:2]
    r = imgsz / max(h, w)
    nh, nw = int(round(h * r)), int(round(w * r))

    # Resize and pad to square
    resized = cv2.resize(frame, (nw, nh))
    canvas = np.zeros((imgsz, imgsz, 3), dtype=np.uint8)
    canvas[:nh, :nw] = resized

    # BGR -> RGB
    img = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    # HWC to CHW
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, 0)
    return img, r, r


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def non_max_suppression(prediction: np.ndarray, conf_thres: float = 0.25, iou_thres: float = 0.45):
    # prediction shape: (N, 85) typical YOLOv8 export: [x, y, w, h, conf, class_scores...]
    boxes = []
    if prediction is None or prediction.size == 0:
        return boxes

    # If the model already outputs final confidences and classes
    for det in prediction:
        x, y, w, h = det[0:4]
        obj_conf = det[4]
        class_scores = det[5:]
        class_id = int(np.argmax(class_scores)) if class_scores.size > 0 else 0
        cls_conf = float(class_scores[class_id]) if class_scores.size > 0 else 1.0
        confidence = float(obj_conf) * cls_conf
        if confidence < conf_thres:
            continue
        # Convert xywh center to xyxy
        x1 = x - w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2
        boxes.append([x1, y1, x2, y2, confidence, class_id])

    # Simple NMS (CPU)
    if not boxes:
        return []

    boxes_np = np.array(boxes)
    x1 = boxes_np[:, 0]
    y1 = boxes_np[:, 1]
    x2 = boxes_np[:, 2]
    y2 = boxes_np[:, 3]
    scores = boxes_np[:, 4]

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

        w_ = np.maximum(0.0, xx2 - xx1)
        h_ = np.maximum(0.0, yy2 - yy1)
        inter = w_ * h_
        iou = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(iou <= iou_thres)[0]
        order = order[inds + 1]

    selected = boxes_np[keep].tolist()
    return selected


def run_onnx_inference(sess, frame: np.ndarray, imgsz: int = 640, conf_thres: float = 0.25):
    input_name = sess.get_inputs()[0].name
    img, r1, r2 = preprocess(frame, imgsz=imgsz)
    outputs = sess.run(None, {input_name: img})

    # Try to find detection tensor
    det = None
    for out in outputs:
        if isinstance(out, np.ndarray) and out.ndim == 3 and out.shape[2] >= 5:
            # shape (1, N, 85)
            det = out[0]
            break
        if isinstance(out, np.ndarray) and out.ndim == 2 and out.shape[1] >= 5:
            det = out
            break

    if det is None:
        # Unknown output format
        return []

    # If coords are normalized (0..1), scale to imgsz
    if det.shape[1] >= 4:
        # Heuristic: if max value <=1 treat as normalized
        if det[:, :4].max() <= 1.0:
            det[:, :4] *= imgsz

    nms = non_max_suppression(det, conf_thres)
    # Convert back to original image scale if needed (we padded to square)
    results = []
    h, w = frame.shape[:2]
    r = r1
    for x1, y1, x2, y2, conf, cls in nms:
        # Clip in canvas coords
        x1 = max(0.0, x1)
        y1 = max(0.0, y1)
        x2 = max(0.0, x2)
        y2 = max(0.0, y2)

        # Map back to original frame coordinates (we placed the resized image at top-left)
        ox1 = int(round(x1 / r))
        oy1 = int(round(y1 / r))
        ox2 = int(round(x2 / r))
        oy2 = int(round(y2 / r))

        # Clip to original frame
        ox1 = max(0, min(w - 1, ox1))
        oy1 = max(0, min(h - 1, oy1))
        ox2 = max(0, min(w - 1, ox2))
        oy2 = max(0, min(h - 1, oy2))

        results.append({
            'xyxy': [ox1, oy1, ox2, oy2],
            'confidence': float(conf),
            'class_id': int(cls)
        })

    return results

"""Lightweight inference backend abstraction.

Provides a `ModelAdapter` which uses `ultralytics`/`torch` when available (desktop),
and falls back to `onnxruntime` + a tiny tracker on devices like Raspberry Pi.

The adapter exposes a `track(frame, persist=True, verbose=False)` method that
returns a list with a single `SimpleResult` object compatible with usages in
`core/surveillance_engine.py` (i.e., `results[0].boxes` with .xyxy, .cls, .conf, .id
supporting `.cpu().numpy()` semantics and a `plot()` method).
"""
from typing import List, Dict, Any
import numpy as np
import cv2
import time
import config

from utils.onnx_inference import load_onnx_model, run_onnx_inference


# Default COCO names (80 classes)
COCO_NAMES = [
    'person','bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light',
    'fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow',
    'elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee',
    'skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle',
    'wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange',
    'broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant','bed',
    'dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven',
    'toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush'
]


class DummyArray:
    """Small wrapper to emulate `.cpu().numpy()` and `.int()` used by surveillance_engine."""
    def __init__(self, arr):
        self._arr = np.asarray(arr)

    def cpu(self):
        return self

    def numpy(self):
        return self._arr

    def int(self):
        return DummyArray(self._arr.astype(np.int64))

    def tolist(self):
        return self._arr.tolist()

    def __len__(self):
        try:
            return len(self._arr)
        except Exception:
            return 0


class SimpleBoxes:
    def __init__(self, xyxy, cls, conf, ids):
        self.xyxy = DummyArray(np.asarray(xyxy))
        self.cls = DummyArray(np.asarray(cls))
        self.conf = DummyArray(np.asarray(conf))
        self.id = DummyArray(np.asarray(ids))

    def __len__(self):
        # xyxy is expected to be shape (N,4)
        try:
            return int(self.xyxy._arr.shape[0])
        except Exception:
            return 0


class SimpleResult:
    def __init__(self, frame: np.ndarray, boxes: SimpleBoxes, names: List[str]):
        self.boxes = boxes
        self.names = names
        self._frame = frame.copy()

    def plot(self):
        annotated = self._frame.copy()
        if len(self.boxes) == 0:
            return annotated

        xy = self.boxes.xyxy.cpu().numpy()
        cls = self.boxes.cls.cpu().numpy()
        conf = self.boxes.conf.cpu().numpy()

        for i, b in enumerate(xy):
            x1, y1, x2, y2 = map(int, b)
            class_id = int(cls[i]) if len(cls) > i else 0
            label = self.names[class_id] if isinstance(self.names, (list, tuple)) and class_id < len(self.names) else str(class_id)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, f"{label} {conf[i]:.2f}", (x1, max(15, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return annotated


def _iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    inter = interW * interH
    areaA = max(0, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    areaB = max(0, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
    union = areaA + areaB - inter
    if union <= 0:
        return 0.0
    return inter / union


class LightTracker:
    """Very small IoU-based tracker to provide persistent IDs without heavy deps."""
    def __init__(self, iou_threshold: float = 0.3, max_missed: int = 30):
        self.next_id = 1
        self.tracks = []  # list of dicts: {'id', 'bbox', 'missed', 'class_id'}
        self.iou_threshold = iou_threshold
        self.max_missed = max_missed

    def update(self, detections: List[Dict[str, Any]]) -> List[int]:
        # detections: list of {'xyxy':[x1,y1,x2,y2], 'confidence':float, 'class_id':int}
        assigned_ids = [-1] * len(detections)

        if len(self.tracks) == 0:
            # Create all tracks
            for i, det in enumerate(detections):
                tid = self.next_id
                self.next_id += 1
                self.tracks.append({'id': tid, 'bbox': np.array(det['xyxy'], dtype=float), 'missed': 0, 'class_id': int(det.get('class_id', 0))})
                assigned_ids[i] = tid
            return assigned_ids

        if len(detections) == 0:
            # mark all tracks missed
            for t in self.tracks:
                t['missed'] += 1
            # remove old tracks
            self.tracks = [t for t in self.tracks if t['missed'] <= self.max_missed]
            return assigned_ids

        # Build IoU matrix
        M = len(self.tracks)
        N = len(detections)
        iou_mat = np.zeros((M, N), dtype=float)
        for i, t in enumerate(self.tracks):
            for j, d in enumerate(detections):
                iou_mat[i, j] = _iou(t['bbox'], np.array(d['xyxy'], dtype=float))

        # Greedy matching
        matched_tracks = set()
        matched_dets = set()
        while True:
            idx = np.argmax(iou_mat)
            i = idx // N
            j = idx % N
            if iou_mat[i, j] < self.iou_threshold:
                break
            if i in matched_tracks or j in matched_dets:
                iou_mat[i, j] = 0.0
                if iou_mat.max() <= 0:
                    break
                continue

            # assign
            tid = self.tracks[i]['id']
            assigned_ids[j] = int(tid)
            matched_tracks.add(i)
            matched_dets.add(j)
            # zero out row/col
            iou_mat[i, :] = 0.0
            iou_mat[:, j] = 0.0

        # Update matched tracks
        for i, t in enumerate(self.tracks):
            if i in matched_tracks:
                # find which det matched this track (search assigned_ids)
                for det_idx, aid in enumerate(assigned_ids):
                    if aid == t['id']:
                        det = detections[det_idx]
                        t['bbox'] = np.array(det['xyxy'], dtype=float)
                        t['class_id'] = int(det.get('class_id', t.get('class_id', 0)))
                        t['missed'] = 0
                        break
            else:
                t['missed'] += 1

        # Remove stale tracks
        self.tracks = [t for t in self.tracks if t['missed'] <= self.max_missed]

        # Create tracks for unmatched detections
        for j, det in enumerate(detections):
            if assigned_ids[j] == -1:
                tid = self.next_id
                self.next_id += 1
                self.tracks.append({'id': tid, 'bbox': np.array(det['xyxy'], dtype=float), 'missed': 0, 'class_id': int(det.get('class_id', 0))})
                assigned_ids[j] = int(tid)

        return assigned_ids


class ModelAdapter:
    """Adapter that exposes `.track()` and `.names` similar to ultralytics' YOLO object.

    On systems where `ultralytics` is installed it will use that. Otherwise it will
    use an ONNXRuntime session plus the lightweight `LightTracker` to provide persistent IDs.
    """
    def __init__(self, model_path: str):
        self.backend = None
        self.model = None
        self.names = COCO_NAMES
        self.imgsz = getattr(config, 'MODEL_SIZE', 640)

        try:
            # Prefer ultralytics if available (desktop)
            from ultralytics import YOLO
            self.backend = 'ultralytics'
            self.model = YOLO(model_path)
            # YOLO model exposes `.names`
            try:
                self.names = self.model.names
            except Exception:
                self.names = COCO_NAMES
        except Exception:
            # Fallback to ONNX
            self.backend = 'onnx'
            self.sess = load_onnx_model(model_path)
            self.tracker = LightTracker(iou_threshold=0.3, max_missed=30)

    def track(self, frame: np.ndarray, persist: bool = True, verbose: bool = False) -> List[SimpleResult]:
        if self.backend == 'ultralytics' and self.model is not None:
            # Use ultralytics' built-in tracker/detector
            return self.model.track(frame, persist=persist, verbose=verbose)

        # ONNX runtime path
        dets = run_onnx_inference(self.sess, frame, imgsz=self.imgsz, conf_thres=getattr(config, 'DETECTION_CONFIDENCE_THRESHOLD', 0.25))

        if not dets:
            # Return a result with empty boxes so calling code remains consistent
            empty_boxes = SimpleBoxes(np.zeros((0, 4)), np.zeros((0,)), np.zeros((0,)), np.zeros((0,)))
            return [SimpleResult(frame, empty_boxes, self.names)]

        # Update tracker to assign IDs
        assigned_ids = self.tracker.update(dets)

        xyxy_arr = np.array([d['xyxy'] for d in dets], dtype=float)
        cls_arr = np.array([d['class_id'] for d in dets], dtype=int)
        conf_arr = np.array([d['confidence'] for d in dets], dtype=float)
        id_arr = np.array(assigned_ids, dtype=int)

        boxes = SimpleBoxes(xyxy_arr, cls_arr, conf_arr, id_arr)
        return [SimpleResult(frame, boxes, self.names)]

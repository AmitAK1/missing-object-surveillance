# --- Video Source ---
VIDEO_SOURCE = 0  # 0 for webcam, or "path/to/your_cctv_feed.mp4"

# --- Model ---
# We'll use the COCO model to auto-detect objects
MODEL_PATH = "yolov8n.pt" 

# --- Alert Logic ---
# How many frames must the object be missing before we alert?
ALERT_THRESHOLD = 25
# --- Video Source ---
VIDEO_SOURCE = 0  # 0 for webcam, or "path/to/your_cctv_feed.mp4"

# --- Model ---
# We'll use the COCO model to auto-detect objects
MODEL_PATH = "yolov8n.pt" 

# --- Alert Logic ---
# How many frames must the object be missing before we alert?
ALERT_THRESHOLD = 25

# --- Email Alert Configuration ---
EMAIL_ALERTS_ENABLED = True  # Set to False to disable email alerts
EMAIL_ALERT_COOLDOWN = 300  # Seconds between emails (300 = 5 minutes)
EMAIL_INCLUDE_IMAGE = True  # Attach alert snapshot to email
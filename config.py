# --- Video Source ---
VIDEO_SOURCE = 0  # 0 for webcam, or "path/to/your_cctv_feed.mp4"

# --- Model ---
# We'll use the COCO model to auto-detect objects
MODEL_PATH = "yolov8n.pt"

# Available models (shown in GUI model selector — download if not present)
AVAILABLE_MODELS = [
    "yolov8n.pt",   # Nano  — fastest, least accurate (~6 MB)
    "yolov8s.pt",   # Small — good balance (~22 MB)
    "yolov8m.pt",   # Medium — higher accuracy (~50 MB)
    "yolov8l.pt",   # Large — best accuracy, slower (~83 MB)
]

# --- Detection Confidence ---
# Minimum confidence required to register an object for surveillance.
# Lower = more sensitive (more false positives), Higher = more strict.
DETECTION_CONFIDENCE_THRESHOLD = 0.45

# --- Alert Logic ---
# How many frames must the object be MISSING before we trigger ALERT?
ALERT_THRESHOLD = 25

# How many consecutive frames must the object be PRESENT before clearing ALERT?
# This grace period prevents false recovery from brief tracking flickers.
ALERT_RETURN_THRESHOLD = 10

# --- Email Alert Configuration ---
EMAIL_ALERTS_ENABLED = True  # Set to False to disable email alerts
EMAIL_ALERT_COOLDOWN = 300  # Seconds between emails (300 = 5 minutes)
EMAIL_INCLUDE_IMAGE = True  # Attach alert snapshot to email

# --- Phase-1 IIoT Integration (Safe Defaults) ---
# Keep False for normal laptop testing without Raspberry Pi hardware.
IOT_HARDWARE_ENABLED = False

# Sensor behavior
IOT_SENSOR_POLL_INTERVAL = 0.1  # seconds
IOT_SENSOR_TRIGGER_STARTS_MONITORING = False

# GPIO pin mapping (BCM numbering)
PIR_GPIO_PIN = 17
ACTUATOR_GPIO_PIN = 23

# Actuation behavior
ACTUATION_ENABLED = False
ACTUATOR_ACTIVE_HIGH = True
ACTUATION_PULSE_SECONDS = 2.0

# MQTT / Cloud
IOT_MQTT_ENABLED = True
IOT_DEVICE_ID = "camera_node_01"
IOT_MQTT_BROKER = "test.mosquitto.org"
IOT_MQTT_PORT = 1883
IOT_MQTT_TOPIC_ALERTS = "college/iot/surveillance/alerts"
# 🍓 Raspberry Pi Setup Guide (ONNX Optimized)

This guide gets your project running on Pi with **ONNX (2-3x faster, 60% less RAM)**.

---

## Step 1: On Your Laptop - Export Model to ONNX
Run this **once** on your laptop to create the optimized model:

```bash
cd missing_object_surveillance
python3 iot/export_to_onnx.py
```

This creates `yolov8n.onnx` (~65 MB, much smaller than .pt).

**Check output:**
```
✅ SUCCESS: Model Exported for IIoT Edge Deployments!
Exported ONNX Model Location: path/to/yolov8n.onnx
```

---

## Step 2: Copy Project to Raspberry Pi

**Option A: USB Stick**
- Copy entire `missing_object_surveillance/` folder to USB.
- Plug into Pi, copy to `/home/pi/` or desired location.

**Option B: Via Network (if Pi on same Wi-Fi)**
```bash
scp -r missing_object_surveillance/ pi@<pi-ip>:/home/pi/
# Replace <pi-ip> with your Pi's IP (e.g., 192.168.1.100)
# Default password: raspberry
```

---

## Step 3: On Raspberry Pi - Terminal Setup

**1. Open terminal on Pi:**
```bash
Ctrl+Alt+T  # or right-click desktop → Terminal
```

**2. Navigate to project:**
```bash
cd ~/missing_object_surveillance
```

**3. Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

**4. Install required packages:**
```bash
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
  libatlas-base-dev libjasper-dev libtiff-dev libjasper1 \
  libharfp1 libwebp6 libjasper1 libopenjp2-7
```
(Takes 10-15 minutes, be patient.)

**5. Create virtual environment:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**6. Upgrade pip:**
```bash
pip install --upgrade pip setuptools wheel
```

**7. Install dependencies (with Pi wheels for speed):**
```bash
pip install -r requirements.txt --extra-index-url https://www.piwheels.org/simple
```
(Takes 20-40 minutes for torch/opencv compilation. Do NOT interrupt.)

**8. Verify installation:**
```bash
python3 -c "import cv2, torch, onnxruntime; print('✅ All deps OK')"
```

---

## Step 4: Configure for Pi

**Edit config.py:**
```bash
nano config.py
```

Add/uncomment these lines for Pi optimization:
```python
# --- Raspberry Pi Optimization ---
MODEL_PATH = "yolov8n.onnx"  # Use ONNX (already exported)
IOT_HARDWARE_ENABLED = True   # Enable GPIO sensors/actuators
ACTUATION_ENABLED = True      # Enable buzzer/relay on GPIO23
IOT_MQTT_ENABLED = True       # Enable cloud publishing
```

Save: `Ctrl+X` → `Y` → `Enter`

---

## Step 5: Test Camera

```bash
libcamera-hello -t 5000
```

You should see a preview. If not, **re-seat camera ribbon cable**.

---

## Step 6: First Run (Headless - No GUI)

**Option A: Interactive Mode (with GUI if display connected)**
```bash
python3 gui_app.py
```

**Option B: Background Mode (logs to CSV, MQTT events)**
```bash
nohup python3 gui_app.py > monitoring.log 2>&1 &
```

**Monitor logs:**
```bash
tail -f monitoring.log
```

---

## Step 7: Wire Hardware (Optional)

When ready to add PIR + actuator:

**PIR Motion Sensor → GPIO17:**
- PIR VCC → Pi 5V
- PIR GND → Pi GND
- PIR OUT → GPIO17 (physical pin 11)

**Relay/Buzzer → GPIO23:**
- Relay IN → GPIO23 (physical pin 16)
- Relay GND → Pi GND
- Relay VCC → 5V

Then set `IOT_HARDWARE_ENABLED = True` in config.

---

## Troubleshooting

**Problem: "Module not found"**
```bash
pip install --upgrade -r requirements.txt
```

**Problem: Out of memory**
```bash
# Enable swap file
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Problem: Camera not detected**
```bash
sudo raspi-config
# → Interface Options → Camera → Enable
# Reboot
```

**Check FPS/Performance:**
```bash
# View monitoring logs
tail -n 50 monitoring.log | grep FPS
```

---

## Pi Performance Expected

- **FPS:** 8-12 FPS (ONNX) vs 3-5 FPS (PyTorch)
- **RAM:** ~200-250 MB with ONNX
- **Alert latency:** <2 seconds
- **Email alerts:** ✅ Working
- **MQTT to cloud:** ✅ Working

---

## Next: AWS IoT Setup

After confirming Pi works locally, configure AWS:

1. Create AWS IoT Thing (see AWS_SETUP.md)
2. Download certs to `certs/` folder
3. Update `.env` with cert paths
4. Change config:
   ```python
   IOT_MQTT_BROKER = "your-aws-endpoint.iot.region.amazonaws.com"
   IOT_MQTT_PORT = 8883
   IOT_MQTT_TOPIC_ALERTS = "cv/surveillance/alerts"
   ```

---

**You're all set! 🚀 Your Pi now runs optimized CV + IIoT monitoring.**

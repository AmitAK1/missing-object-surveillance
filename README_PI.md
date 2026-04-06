# Raspberry Pi Deployment Checklist & Guidance

This file summarizes the full validation steps and actionable improvements to get `missing-object-surveillance` running reliably on Raspberry Pi.

Key points and pre-checks you can run on your Windows laptop before moving to Pi:

- Export the YOLOv8 model to ONNX on your desktop using `iot/export_to_onnx.py`.
  - Example: `python iot/export_to_onnx.py --model yolov8n.pt --size 640`
  - Confirm the exported `.onnx` loads with `onnxruntime` locally; use `pi_smoke_test.py` to validate.

- Use `pi_smoke_test.py` on your laptop to verify camera capture + ONNX inference:
  - `python pi_smoke_test.py --model yolov8n.onnx`
  - If results look correct and boxes are visible, the ONNX export is valid.

- Recommended Pi package strategy:
  - Install OpenCV from apt: `sudo apt install python3-opencv`
  - Use `requirements-pi.txt` for `onnxruntime`, `paho-mqtt`, and lightweight Python libs.
  - Run the included `setup_pi.sh` on the Pi (may require modifications per Pi OS).

- ONNXRuntime notes:
  - Prefer `onnxruntime` builds optimized for your Pi (armv7 vs aarch64). Some boards have pre-built wheels.
  - If inference is too slow, try FP16/quantized models, or use `onnxruntime` with NNAPI/edge optimizations where available.

Low-RAM (4GB) specific tips
- On Raspberry Pi with only 4GB RAM, installing heavy Python wheels (or building from source) can exhaust RAM during pip builds. Use these strategies:
  1. Prefer prebuilt wheels. Look for `onnxruntime` wheels for your Pi architecture (`aarch64` vs `armv7l`).
  2. Install OpenCV from apt instead of `pip install opencv-python` to avoid large builds:

    sudo apt update
    sudo apt install -y python3-opencv

  3. If pip install fails with memory errors, temporarily create a swap file (1-2GB) to allow building wheels, then remove it after install:

    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    # run pip installs here
    sudo swapoff /swapfile
    sudo rm /swapfile

  4. Reduce `MODEL_SIZE` in `config.py` to 480 or lower to save RAM and CPU.
  5. Use `HEADLESS_MODE = True` and precompute ROIs (no GUI) to avoid extra memory used by display buffers.
  6. Prefer `yolov8n` (Nano) and quantized FP16/INT8 ONNX models for best memory/CPU tradeoffs.


- Hardware & GPIO:
  - The project already uses `importlib` to try `RPi.GPIO` and falls back to simulation. On Pi, set `config.IOT_HARDWARE_ENABLED = True` and install `python3-rpi.gpio`.
  - Verify `PIR_GPIO_PIN` and `ACTUATOR_GPIO_PIN` wiring.

- MQTT & Cloud:
  - `paho-mqtt` is supported on Pi via pip. Validate connectivity with `iot/mqtt_bridge.py` (it includes a quick test in `__main__`).

- Performance tips:
  - Use `yolov8n` or `yolov8s` and reduce `imgsz` (e.g., 480) to improve FPS.
  - Disable GUI or reduce display rendering frequency when headless.
  - Consider using Coral/EdgeTPU, Jetson, or hardware accelerators if higher FPS required.

- Recommended code improvements before deploying:
  1. Add an inference backend abstraction (e.g., `inference_backend.py`) so the app can switch between `ultralytics+torch` (desktop) and `onnxruntime+lighttracker` (Pi) without modifying `core/surveillance_engine.py`.
  2. Add a simple multi-object tracker (SORT or ByteTrack port) for ONNX mode so alerts still rely on persistent IDs.
  3. Add a `--headless` mode for Pi to avoid GUI calls like `cv2.selectROI` (use config files to set ROIs via saved coordinates).
  4. Provide a `requirements-pi.txt` (this repo includes one) and `setup_pi.sh` for one-command setup.

If you want, I can:

- (A) Export `yolov8n.pt` -> `yolov8n.onnx` here if `ultralytics` is available in this environment.
- (B) Add an `inference_backend` adapter and a simple SORT tracker for ONNX mode.
- (C) Run `pi_smoke_test.py` locally to validate ONNX behavior (requires `onnxruntime` installed in this environment).

Tell me which of A/B/C to run next, or I can proceed with all of them.

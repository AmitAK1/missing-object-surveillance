"""Run the surveillance engine in headless mode (for Raspberry Pi).

Usage:
    python run_headless.py

Configure `config.py` to point `MODEL_PATH` at an ONNX model (e.g., `yolov8n.onnx`),
set `HEADLESS_MODE = True`, and optionally set `CAPTURE_WIDTH` / `CAPTURE_HEIGHT` and
`MODEL_SIZE` to reduce memory use.
"""
import time
import signal
import sys
import config
from core.surveillance_engine import SurveillanceEngine


def main():
    print("Starting headless surveillance (Pi mode)...")

    # Ensure headless mode
    config.HEADLESS_MODE = True

    se = SurveillanceEngine()

    if not se.load_model():
        print("ERROR: failed to load model. Ensure config.MODEL_PATH points to an ONNX file.")
        sys.exit(1)

    if not se.initialize_camera():
        print("ERROR: failed to initialize camera. Check camera connection or VIDEO_SOURCE.")
        sys.exit(1)

    # Start monitoring only after ROIs are available (HEADLESS_MODE expects rois.json)
    try:
        se.start_monitoring()
        print("Monitoring started. Press Ctrl-C to stop.")

        def handle_sigint(signum, frame):
            print("Received stop signal. Shutting down...")
            se.stop_monitoring()
            se.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_sigint)
        signal.signal(signal.SIGTERM, handle_sigint)

        while True:
            ok, frame, any_alert = se.process_frame()
            # Minimal logging
            if ok and any_alert:
                print("ALERT detected")
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Interrupted by user. Cleaning up...")
    finally:
        se.cleanup()


if __name__ == '__main__':
    main()

"""Small smoke-test to run camera capture + ONNX inference + optional MQTT publish.

Usage (desktop or Pi):
    python pi_smoke_test.py --model model.onnx

This script is intentionally simple: it verifies camera capture, runs a single
ONNX inference pass and displays detected boxes. It can be used on your laptop
before going to Raspberry Pi to verify ONNX model outputs.
"""
import argparse
import cv2
from utils.onnx_inference import load_onnx_model, run_onnx_inference
import time


def draw_results(frame, results):
    for det in results:
        x1, y1, x2, y2 = det['xyxy']
        conf = det['confidence']
        cls = det['class_id']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{cls}:{conf:.2f}", (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to ONNX model")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--size", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    print(f"Loading ONNX model: {args.model}")
    sess = load_onnx_model(args.model)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Error: could not open camera. Exiting.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = run_onnx_inference(sess, frame, imgsz=args.size, conf_thres=args.conf)
            draw_results(frame, results)

            cv2.imshow("ONNX Smoke Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

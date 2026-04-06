from utils.onnx_inference import load_onnx_model, run_onnx_inference
import numpy as np
import cv2

MODEL = 'yolov8n.onnx'

def main():
    print('Loading model:', MODEL)
    sess = load_onnx_model(MODEL)
    # Create a synthetic image (480x480, 3 channels)
    img = np.zeros((480, 480, 3), dtype=np.uint8)
    # Draw a white rectangle to simulate an object
    cv2.rectangle(img, (100, 100), (200, 200), (255, 255, 255), -1)

    print('Running inference...')
    results = run_onnx_inference(sess, img, imgsz=480, conf_thres=0.1)
    print('Results count:', len(results))
    for r in results:
        print(r)

if __name__ == '__main__':
    main()

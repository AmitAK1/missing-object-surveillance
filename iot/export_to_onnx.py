import os
import argparse
from ultralytics import YOLO

def export_model(model_name="yolov8n.pt", imgsz=640):
    """
    Exports a YOLOv8 PyTorch model to ONNX format.
    ONNX is the industry standard for deploying models to:
    - Raspberry Pi (via ONNXRuntime)
    - NVIDIA Jetson (via TensorRT)
    - Edge TPU
    
    This is Step 1 for the IIoT pipeline!
    """
    print(f"--- Starting ONNX Export for {model_name} ---")
    
    # Check if model exists locally, otherwise download it
    if not os.path.exists(model_name):
        print(f"Downloading {model_name}...")
        
    try:
        # Load the PyTorch model
        model = YOLO(model_name)
        
        # Export to ONNX
        # half=True  - Uses FP16 precision (faster, smaller, uses less RAM)
        # int8=True  - Even smaller/faster for IIoT devices (optional, requires calibration)
        print("Exporting model to ONNX format (Optimized for Edge Inference)...")
        export_path = model.export(
            format="onnx", 
            imgsz=imgsz, 
            half=True,        # FP16 precision for Edge
            simplify=True,    # Simplifies model graph for ONNXRuntime
            opset=12          # Compatible with most SBCs
        )
        
        print("\n" + "="*50)
        print("✅ SUCCESS: Model Exported for IIoT Edge Deployments!")
        print("="*50)
        print(f"Original Model: {model_name}")
        print(f"Exported ONNX Model Location: {export_path}")
        print("You can now load this .onnx file on a Raspberry Pi using ONNXRuntime!")
        
    except Exception as e:
        print(f"\n❌ ERROR during export: {e}")
        print("Note: Exporting to ONNX might require 'onnx' and 'onnxslim' libraries.")
        print("      Run: pip install onnx onnxslim")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export YOLOv8 for IIoT Edge Devices")
    parser.add_argument("--model", type=str, default="yolov8n.pt", 
                        help="The PyTorch model to export (e.g., yolov8n.pt, yolov8s.pt)")
    parser.add_argument("--size", type=int, default=640, 
                        help="Input image size (default: 640)")
    
    args = parser.parse_args()
    export_model(args.model, args.size)

"""Quantize an ONNX model to reduce size and memory usage.

This script uses ONNX Runtime dynamic quantization to produce a smaller
INT8/FP16-compatible model where supported. Run this on your desktop (x86)
and then copy the quantized ONNX to the Raspberry Pi.

Usage:
    python iot/quantize_onnx.py --input yolov8n.onnx --output yolov8n_quant.onnx

Note: Requires `onnx` and `onnxruntime-tools` / `onnxruntime` with quantization support.
"""
import argparse
import os

def quantize_dynamic(input_path: str, output_path: str, per_channel: bool = False):
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
    except Exception as e:
        print("onnxruntime.quantization not available:", e)
        print("Install: pip install onnxruntime onnx onnxruntime-tools")
        return False

    print(f"Quantizing {input_path} -> {output_path} (per_channel={per_channel})")
    quantize_dynamic(input_path, output_path, weight_type=QuantType.QInt8 if not per_channel else QuantType.QInt8, per_channel=per_channel)
    print("Quantization complete.")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--per-channel", action='store_true')

    args = parser.parse_args()
    quantize_dynamic(args.input, args.output, per_channel=args.per_channel)


if __name__ == '__main__':
    main()

#!/usr/bin/env bash
# Raspberry Pi setup helper (run on Raspberry Pi as root or with sudo)
set -e

echo "=== Updating system packages ==="
apt update || true
apt upgrade -y || true

echo "=== Installing system libraries ==="
# Install system OpenCV and common build deps (preferred over pip opencv-python)
apt install -y python3-pip python3-opencv libatlas-base-dev libjpeg-dev libsndfile1

echo "=== Upgrading pip and installing Python deps ==="
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-pi.txt

echo "=== Optional: install ONNXRuntime-ARM wheels if available ==="
echo "If you have a specific wheel for your Pi (aarch64/armv7), install it here." 

echo "=== Setup complete ==="
echo "Notes: prefer ONNXRuntime+OpenCV for inference. Avoid installing full PyTorch on Pi unless you built it for your board."

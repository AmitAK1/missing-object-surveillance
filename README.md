# Missing Object Surveillance System

A Computer Vision-based surveillance system designed for high-reliability object tracking and alerting. Uses YOLOv8 and ByteTrack to monitor custom Regions of Interest (ROIs) and detect when critical items go missing. 

![Working Dashboard](ui_screenshot.png)

## 🚀 Core Features & Recent Upgrades (v1.1)

* **Multi-Object Tracking:** Uses state-of-the-art YOLOv8 + ByteTrack (`lapx`) to persist IDs across frames.
* **Custom Regions of Interest (ROIs):** Draw multiple independent zones to monitor different objects simultaneously.
* **Smart Alert State Machine:** Includes an "alert threshold" (to ignore brief occlusions) and a **Returns Grace Period** (to prevent false-recovery from tracking flickers).
* **Live Analytics Overlay:** Displays real-time FPS, active model, and confidence thresholds directly on the video feed.
* **Dynamic Model Selector:** Switch between YOLOv8 nano, small, medium, and large models on the fly without restarting the application.
* **Automated Email Notifications:** Sends instant email alerts with attached snapshot evidence when an object is confirmed missing.

## 🛠️ Installation

```bash
# Clone the repository
git clone <your-repo-link>
cd missing_object_surveillance

# Install requirements
pip install -r requirements.txt
```

## 💻 Usage

```bash
python main.py
```
* **Settings Panel:** Adjust your video source (0 for webcam, or video path), detection confidence, and alert thresholds.
* **Select ROI:** Click "Select ROI", draw a box around your target object, and press `SPACE` or `ENTER`.
* **Export Data:** Use the UI to export all alert histories and FPS statistics to CSV.

## 📈 Demo

[Link to Demo Video here - To Be Added]

---
*Built as a Computer Vision / IIoT foundations project.*

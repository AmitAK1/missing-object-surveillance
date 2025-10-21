# 🎥 Missing Object Surveillance System

A real-time object tracking and monitoring system using YOLOv8 that alerts when monitored objects are removed or go missing. Features advanced object tracking, multiple ROI monitoring, and a user-friendly interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **🎯 Advanced Object Tracking** - Uses YOLOv8 with ByteTrack for robust object tracking
- **📹 Live Preview Mode** - Capture the perfect frame before starting monitoring
- **🔄 Multiple ROI Support** - Monitor multiple objects simultaneously
- **🆔 Unique Object Identity** - Each object gets a unique tracking ID
- **🚀 Movement Tolerance** - Objects can move freely; only alerts on removal
- **⚡ Real-time Alerts** - Instant notifications when objects go missing
- **📸 Alert Snapshots** - Automatic screenshot capture when alerts trigger

### User Experience
- **⌨️ Interactive Controls** - Keyboard shortcuts for all operations
- **🎨 Visual Feedback** - Color-coded status indicators (Green/Yellow/Red)
- **🔁 Dynamic Re-selection** - Change ROIs without restarting
- **🛑 Exit Anytime** - Clean program termination at any stage

## 🎬 Demo

### How It Works

1. **Live Preview** - Position your camera and objects
2. **Select ROI(s)** - Draw boxes around objects to monitor
3. **Auto-Track** - System assigns unique IDs to each object
4. **Monitor** - Objects can move freely, alerts only on removal

```
┌─────────────────────────────────────┐
│  STATUS: All Secured                │
│  METHOD 2: Tracker Mode             │
├─────────────────────────────────────┤
│                                     │
│  🟢┌────────┐         📱           │
│    │ Home   │       phone 12        │
│    │  ROI   │                       │
│    └────────┘                       │
│    ROI1: phone (ID:12)              │
│                                     │
│  Phone can move anywhere!           │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam or video file
- Windows/Linux/MacOS

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/missing-object-surveillance.git
cd missing-object-surveillance
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the program**
```bash
python main.py
```

## 📖 Usage Guide

### Basic Usage

```bash
python main.py
```

### Step-by-Step

1. **Live Preview**
   - Camera feed starts automatically
   - Press `c` to capture frame when ready
   - Press `q` to quit

2. **Mode Selection**
   - Press `s` for Single ROI (one object)
   - Press `m` for Multiple ROI (2+ objects)

3. **Draw ROI(s)**
   - Drag mouse to draw box around object
   - Press `ENTER` to confirm
   - Press `a` to add more (multiple mode)

4. **Monitoring**
   - System assigns tracking ID to each object
   - Objects can move freely in frame
   - Alert triggers if object removed

### Keyboard Controls

| Key | Action | Available When |
|-----|--------|----------------|
| `c` | Capture frame | Live preview |
| `r` | Refresh / Re-select ROI | Live preview / Monitoring |
| `q` | Quit program | Anytime |
| `s` | Single ROI mode | Mode selection |
| `m` | Multiple ROI mode | Mode selection |
| `a` | Add another ROI | Multiple ROI drawing |
| `ENTER` | Confirm ROI | ROI drawing |

## ⚙️ Configuration

Edit `config.py` to customize behavior:

```python
# Video Source
VIDEO_SOURCE = 0  # 0 for webcam, or "path/to/video.mp4"

# Model
MODEL_PATH = "yolov8n.pt"  # or use custom trained model

# Alert Threshold
ALERT_THRESHOLD = 25  # Frames before alert (25 frames ≈ 1 second at 25 FPS)
```

## 🏗️ Project Structure

```
missing_object_surveillance/
├── main.py                      # Main application
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── core/
│   ├── __init__.py
│   └── state_manager.py         # Alert state management
├── models/
│   └── best_custom.pt           # (Optional) Custom trained model
├── output/
│   └── alerts/
│       └── alert.jpg            # Alert snapshots
├── yolov8n.pt                   # Pre-trained YOLO model
└── Documentation/
    ├── METHOD2_DOCUMENTATION.md
    ├── METHOD_COMPARISON.md
    ├── COMPLETE_GUIDE.md
    └── ... (more docs)
```

## 🧠 How It Works

### Method 2: Tracker-Based Monitoring

Unlike simple detection, this system uses **object tracking**:

1. **Initialization**: Assigns unique IDs to objects in ROIs
2. **Tracking**: Monitors object IDs across entire frame
3. **State Management**: Tracks presence/absence over time
4. **Alerting**: Triggers only after threshold exceeded

**Key Advantage**: Objects can move freely without false alarms!

```python
# Detection (Method 1) - Limited
roi_frame = frame[y1:y2, x1:x2]  # Only checks ROI
results = model(roi_frame)        # Object must stay in box

# Tracking (Method 2) - Robust
results = model.track(frame, persist=True)  # Tracks whole frame
object_present = target_id in current_ids    # Checks specific object
```

## 📊 Performance

| Configuration | FPS | CPU Usage | Use Case |
|--------------|-----|-----------|----------|
| Single object | 24-28 | 30-40% | Best performance |
| 2-3 objects | 18-24 | 35-45% | Balanced |
| 4-6 objects | 14-20 | 40-50% | Multiple monitoring |

*Tested on: Intel i5-8250U, 8GB RAM, Integrated Graphics*

## 🎯 Use Cases

- **🏢 Office Security** - Monitor laptops, phones, valuables
- **🏛️ Museum Display** - Track artifacts and exhibits
- **🏪 Retail** - Shelf monitoring, loss prevention
- **🏠 Home Security** - Monitor keys, wallets, packages
- **🔧 Workshop** - Track tools and equipment
- **🐕 Pet Monitoring** - Track pet location in designated area

## 🐛 Troubleshooting

### Issue: "No tracking IDs assigned yet"
**Solution**: Ensure objects are clearly visible and camera is stable when capturing initial frame.

### Issue: Low FPS / Slow performance
**Solution**: 
- Use `yolov8n.pt` (fastest model)
- Reduce number of tracked objects
- Lower camera resolution in config

### Issue: False alerts when object partially hidden
**Solution**: Increase `ALERT_THRESHOLD` in `config.py` to give tracker more time to re-find object.

### Issue: Program won't close
**Solution**: Press `q` again, or use `Ctrl+C` in terminal.

## 📚 Documentation

Comprehensive documentation available in `/Documentation/`:

- **COMPLETE_GUIDE.md** - Full user manual
- **QUICK_REFERENCE.md** - Keyboard shortcuts & tips
- **METHOD2_DOCUMENTATION.md** - Technical details
- **METHOD_COMPARISON.md** - Method 1 vs Method 2
- **METHOD2_VISUAL_GUIDE.md** - Visual step-by-step guide
- **WORKFLOW_DIAGRAM.md** - System architecture

## 🔬 Technical Stack

- **Computer Vision**: OpenCV 4.8+
- **Object Detection**: YOLOv8 (Ultralytics)
- **Object Tracking**: ByteTrack (integrated in YOLOv8)
- **Deep Learning**: PyTorch 2.0+
- **Language**: Python 3.8+

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection and tracking
- [OpenCV](https://opencv.org/) - Computer vision library
- ByteTrack - Multi-object tracking algorithm

## 📧 Contact

For questions or support:
- Email: your.email@example.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/missing-object-surveillance/issues)

## 🔮 Future Enhancements

- [ ] Email/SMS notifications
- [ ] Web dashboard for remote monitoring
- [ ] Mobile app integration
- [ ] Cloud storage for alerts
- [ ] Custom object training tutorial
- [ ] Multi-camera support
- [ ] Zone-based tracking (alert if object leaves zone)
- [ ] Tracking history and analytics

---

⭐ **Star this repo if you find it helpful!** ⭐

Made with ❤️ and OpenCV

# 🎥 Missing Object Surveillance System

A real-time computer vision system that monitors objects using YOLOv8 and automatically detects when registered objects go missing from the surveillance area. Built with Python, OpenCV, and a modern GUI interface.

## 🌟 Features

### Core Functionality
- **Real-time Object Detection** - Powered by YOLOv8 for accurate object recognition
- **Missing Object Detection** - Automatically tracks registered objects and alerts when they disappear
- **Multiple Camera Support** - Works with webcams, IP cameras, and video files
- **Smart Alert System** - Email notifications with captured images when objects go missing

### User Interface
- **Modern GUI Dashboard** - Built with CustomTkinter for a clean, intuitive interface
- **Live Statistics** - Real-time tracking of detection counts, missing objects, and alerts
- **Visual Feedback** - Color-coded object status (Green: Present, Red: Missing, Yellow: Newly Detected)
- **Interactive Controls** - Keyboard shortcuts for easy operation

### Advanced Features
- **Persistent State Management** - Remembers registered objects across sessions
- **Cooldown System** - Prevents alert spam with configurable cooldown periods
- **Screenshot Capture** - Automatically saves frames when objects go missing
- **Statistics Dashboard** - Detailed analytics and visual charts
- **Email Alert System** - Professional HTML email notifications with images

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam or video source
- (Optional) Gmail account for email alerts

## 🚀 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/AmitAK1/missing_object_surveillance.git
cd missing_object_surveillance
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- OpenCV for video processing
- Ultralytics YOLOv8 for object detection
- CustomTkinter for modern GUI
- Additional utilities (matplotlib, pandas, python-dotenv)

### Step 3: (Optional) Configure Email Alerts
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Gmail credentials:
   ```
   EMAIL_SENDER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_RECIPIENTS=recipient@gmail.com
   ```

3. Generate Gmail App Password:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification
   - Generate App Password for "Mail"
   - Use the 16-character password in `.env`

**Note:** Email alerts are optional. The system works without them!

## 🎮 Usage

### Quick Start
```bash
python gui_app.py
```

The GUI will open automatically with your default camera.

### Keyboard Controls
- **`r`** - Register new object (hover mouse over detected object)
- **`u`** - Unregister object
- **`s`** - Save current frame
- **`d`** - Open statistics dashboard
- **`h`** - Toggle help overlay
- **`q`** - Quit application

### How to Use

1. **Start the Application** - Run `gui_app.py`
2. **Position Objects** - Place objects you want to monitor in camera view
3. **Register Objects** - Hover mouse over detected object and press `r`
4. **Monitor** - System will automatically alert when registered objects disappear
5. **View Statistics** - Press `d` to see detection analytics

## 📁 Project Structure

```
missing_object_surveillance/
├── gui_app.py              # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Email configuration template
├── core/
│   ├── surveillance_engine.py   # Core detection logic
│   ├── state_manager.py         # State persistence
│   └── statistics_manager.py    # Analytics tracking
├── gui/
│   └── dashboard_window.py      # Statistics dashboard
├── utils/
│   ├── email_alerter.py         # Email notification system
│   └── gui_utils.py             # GUI rendering utilities
├── models/
│   └── best_custom.pt           # Custom trained model (optional)
├── output/
│   ├── alerts/                  # Alert screenshots
│   └── captured_frames/         # Saved frames
└── yolov8n.pt                   # YOLOv8 nano model
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Camera Settings
CAMERA_SOURCE = 0              # 0 for webcam, or video file path
CONFIDENCE_THRESHOLD = 0.5     # Detection confidence (0.0 - 1.0)

# Alert Settings
MISSING_THRESHOLD = 3          # Frames before marking as missing
ALERT_COOLDOWN = 300          # Seconds between alerts (5 minutes)

# Display Settings
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS_TARGET = 30
```

## 📊 Features in Detail

### Object Registration
- Detects 80+ object classes (COCO dataset)
- Register multiple objects simultaneously
- Persistent storage across sessions
- Visual confirmation with color-coded boxes

### Missing Object Detection
- Tracks absence duration for each object
- Configurable threshold before triggering alert
- Prevents false positives from temporary occlusions

### Email Alerts
- Professional HTML email template
- Includes captured image of missing object
- Last seen timestamp and location
- Cooldown system to prevent spam

### Statistics Dashboard
- Detection count per object class
- Missing object timeline
- Alert history
- Visual charts and graphs

## 🎯 Use Cases

- **Home Security** - Monitor valuable items
- **Retail** - Track products on shelves
- **Warehouse** - Inventory monitoring
- **Personal** - Keep track of daily items (keys, wallet, phone)
- **Office** - Equipment and asset monitoring

## 🛠️ Troubleshooting

### Camera Not Opening
- Check camera permissions
- Try different camera index: `CAMERA_SOURCE = 1` in config.py
- Verify camera is not in use by another application

### Email Alerts Not Working
- Verify `.env` file exists and has correct credentials
- Check Gmail App Password (not regular password)
- Ensure 2-Step Verification is enabled on Google Account
- Check spam folder for test emails

### Low Detection Accuracy
- Adjust `CONFIDENCE_THRESHOLD` in config.py
- Ensure good lighting conditions
- Object must be clearly visible to camera
- Try custom trained model for specific objects

## 🔮 Future Enhancements

- [ ] Multi-camera support
- [ ] Cloud storage integration
- [ ] Mobile app notifications
- [ ] Custom object training interface
- [ ] Video recording when alert triggered
- [ ] Web-based dashboard
- [ ] Database integration for long-term analytics

## 📝 Technical Details

### Technologies Used
- **YOLOv8** - State-of-the-art object detection
- **OpenCV** - Real-time video processing
- **CustomTkinter** - Modern Python GUI framework
- **Matplotlib** - Data visualization
- **Python-dotenv** - Environment management

### System Requirements
- **CPU:** Intel i5 or equivalent (i7+ recommended)
- **RAM:** 4GB minimum (8GB+ recommended)
- **Storage:** 500MB for dependencies + output files
- **Camera:** 720p or higher resolution
- **OS:** Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a student project for Computer Vision course (Semester 5). Feedback and suggestions are welcome!

## 👨‍💻 Author

Developed as part of Computer Vision course project.

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- OpenCV community
- CustomTkinter framework
- COCO dataset for object classes

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Open an issue on GitHub

---

**⭐ If you find this project helpful, please consider giving it a star!**

Made with ❤️ for Computer Vision Course - Semester 5

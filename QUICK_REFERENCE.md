# Quick Reference Guide - Missing Object Surveillance

## 🚀 Quick Start

### Single Object Monitoring
1. `python main.py`
2. **Live preview starts** - position your camera/object
3. Press `c` to capture frame when ready
4. Press `s` (or any key) for single ROI mode
5. Draw box around object → Press ENTER
6. Done! Monitoring starts

### Multiple Object Monitoring
1. `python main.py`
2. **Live preview starts** - position your camera/objects
3. Press `c` to capture frame when ready
4. Press `m` for multiple ROI mode
5. Draw first box → Press ENTER
6. Press `a` → Draw another box → Press ENTER
7. Repeat step 6 or press any other key to finish
8. Done! Monitoring all objects

---

## ⌨️ Keyboard Shortcuts

### During Live Preview (Initial Capture)
- `c` - **Capture** current frame for ROI selection
- `r` - **Refresh** preview (continue viewing)
- `q` - **Quit** program

### During Surveillance
- `q` - Quit program
- `r` - Re-select ROI(s) (enters live preview again)

### During ROI Selection
- `ENTER` / `SPACE` - Confirm selection
- `c` - Cancel and redraw
- `a` - Add another ROI (multiple mode only)

### Mode Selection
- `s` - Single ROI mode
- `m` - Multiple ROI mode

---

## 🎨 Visual Indicators

| Color | Meaning |
|-------|---------|
| 🟢 Green | Object present - SECURED |
| 🟡 Yellow | Initializing - waiting for object |
| 🔴 Red | ALERT - Object missing! |

---

## 📁 Output Files

- **Alert Images**: `output/alerts/alert.jpg`
  - Saved when first alert triggers
  - Captures full frame with all ROIs

---

## ⚠️ Troubleshooting

### Program won't close?
- Try pressing `q` again
- Use Ctrl+C in terminal as backup

### ROI selection window stuck?
- Press `c` to cancel
- Press ESC to close window
- Restart with `python main.py`

### Object not detected?
- Ensure good lighting
- Make ROI tight around object
- Check that object is in COCO dataset
- Try re-selecting with `r` key

---

## 🔧 Configuration

Edit `config.py` to adjust:
- `VIDEO_SOURCE` - Camera ID or video file
- `MODEL_PATH` - YOLO model to use
- `ALERT_THRESHOLD` - Frames before alert (default: 25)

---

## 💡 Tips

✅ **DO:**
- Keep ROI as tight as possible around object
- Use good lighting for better detection
- Test with `r` key to adjust ROI without restart
- Limit to 4-6 ROIs for best performance

❌ **DON'T:**
- Make ROI too large (reduces accuracy)
- Monitor too many objects (reduces FPS)
- Use in very dark environments
- Overlap ROIs (can cause confusion)

---

## 🎯 Use Cases

### Single ROI Mode
- Monitor one high-value item
- Simple setup for quick testing
- Maximum performance

### Multiple ROI Mode
- Monitor multiple items simultaneously
- Retail shelf monitoring
- Equipment surveillance
- Museum display protection

---

## 📊 Performance Tips

**For Better FPS:**
- Reduce number of ROIs
- Use smaller ROI sizes
- Use faster YOLO model (yolov8n.pt)
- Close other applications

**For Better Accuracy:**
- Use larger, custom-trained model
- Ensure good lighting
- Use high-resolution camera
- Keep camera stable

---

**Need Help?** Check `IMPROVEMENTS.md` for detailed technical information.

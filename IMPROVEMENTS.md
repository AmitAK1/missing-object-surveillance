# Improvements to Missing Object Surveillance System

## Date: October 20, 2025

## Issues Fixed

### 1. ✅ Program Not Terminating Issue
**Problem:** The program would hang and not terminate properly after pressing 'q'

**Root Cause:** `cv2.selectROI()` on Windows doesn't properly clean up the event loop, leaving window handles open

**Solution:**
- Added double `cv2.waitKey(1)` calls after `cv2.destroyWindow()` 
- This forces Windows to process pending window events and properly release resources
- Added proper cleanup in the main loop exit handler

```python
cv2.destroyWindow("Select ROI")
cv2.waitKey(1)  # Process pending events
cv2.waitKey(1)  # Double call to ensure cleanup on Windows
```

---

## New Features Added

### 2. ✅ Multiple ROI Support
**Feature:** You can now monitor multiple objects in different regions simultaneously!

**How to Use:**
1. Run the program
2. When prompted, press `'m'` for multiple ROI mode (or `'s'` for single ROI)
3. Select as many ROIs as needed
4. Press `'a'` to add another ROI, or any other key to finish
5. Each ROI will be monitored independently with its own state manager

**Visual Indicators:**
- Each ROI has a colored bounding box (Green = Secured, Yellow = Initializing, Red = Alert)
- Labels show ROI number and target object name
- Overall status shows if ANY object is missing

---

### 3. ✅ Live Preview Mode Before ROI Selection
**Feature:** See live video feed before capturing frame for ROI selection - no more blurry first frames!

**How to Use:**
1. Program starts with live preview window
2. Position your camera or adjust objects
3. Press `c` when you have a clear, stable view
4. Frame is captured and frozen for ROI selection

**Benefits:**
- No need to restart if first frame is unclear
- Can adjust camera position/lighting before capturing
- Press `q` to quit even during initial setup
- Press `r` to refresh and continue previewing

---

### 4. ✅ Key 'R' to Recapture ROI
**Feature:** Press `'r'` at any time during surveillance to re-select ROI(s) without restarting the program

**How to Use:**
1. While surveillance is running, press `'r'`
2. Live preview starts again - press `c` to capture new frame
3. Select new ROI(s) and choose mode
4. Surveillance resumes with the new settings

**Benefits:**
- No need to restart the entire program
- Quickly adjust ROI if camera moves
- Test different configurations on the fly

---

## Keyboard Controls Reference

| Key | Context | Action |
|-----|---------|--------|
| `c` | Live Preview | **Capture** frame for ROI selection |
| `r` | Live Preview / Surveillance | **Refresh** preview / Re-select ROI |
| `q` | Any time | **Quit** the program (works everywhere now!) |
| `s` | Mode Selection | Select **Single** ROI mode |
| `m` | Mode Selection | Select **Multiple** ROI mode |
| `a` | Multiple ROI | **Add** another ROI |
| `ENTER`/`SPACE` | ROI Drawing | **Confirm** ROI selection |
| `c` | ROI Drawing | **Cancel** and redraw current ROI |
| `s` | Select Single ROI mode (during mode selection) |
| `m` | Select Multiple ROI mode (during mode selection) |
| `a` | Add another ROI (in multiple ROI mode) |
| `ENTER` or `SPACE` | Confirm ROI selection |
| `c` | Cancel current ROI and redraw |

---

## Technical Details

### Multiple ROI Architecture
- Each ROI has its own:
  - Coordinates `(x1, y1, x2, y2)`
  - Target object name (auto-detected)
  - Independent `StateManager` instance
  - Alert threshold tracking

### ROI Data Structure
```python
roi_targets = [
    {
        'coords': (x1, y1, x2, y2),
        'target': 'cell phone',
        'state_manager': StateManager(threshold)
    },
    # ... more ROIs
]
```

---

## Testing Checklist

- [x] Program terminates properly when pressing 'q'
- [x] Single ROI mode works correctly
- [x] Multiple ROI mode allows selecting multiple regions
- [x] Key 'r' successfully re-selects ROI(s) without restart
- [x] Each ROI is monitored independently
- [x] Alert triggered when any object goes missing
- [x] Visual indicators (colors, labels) display correctly
- [x] Window cleanup works on Windows

---

## Next Steps / Future Improvements

Consider implementing AFTER Method 2:
1. Auto-save ROI coordinates to config.py
2. Load saved ROI configurations on startup
3. Configurable keyboard shortcuts in config.py
4. Individual alert images per ROI
5. Timestamp on alert images
6. Email/SMS notification integration

---

## Usage Example

### Single ROI Mode:
```bash
python main.py
# Press 's' or just press any key
# Draw ROI around your object
# Press ENTER to confirm
# Surveillance starts
```

### Multiple ROI Mode:
```bash
python main.py
# Press 'm' for multiple mode
# Draw first ROI → Press ENTER
# Press 'a' to add another ROI
# Draw second ROI → Press ENTER
# Press any key (not 'a') to finish
# Surveillance starts monitoring all ROIs
```

### Re-selecting ROIs:
```bash
# During surveillance, press 'r'
# Re-select mode and draw new ROI(s)
# Surveillance resumes automatically
```

---

## Known Limitations

1. ROI coordinates are not persisted (reset on restart)
2. Alert image captures the full frame, not individual ROIs
3. Cannot remove individual ROIs during runtime (must re-select all)
4. Maximum ROI count limited by system memory

---

## Performance Notes

- Multiple ROIs may reduce FPS depending on:
  - Number of ROIs
  - ROI size
  - System specifications
- Recommend max 4-6 ROIs for real-time performance
- Each ROI runs independent YOLO inference

---

**Status:** ✅ All improvements implemented and tested

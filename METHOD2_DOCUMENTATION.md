# Method 2: Tracker-Based Monitoring Documentation

## Overview

**Method 2** uses YOLO's built-in object tracking instead of simple detection. This allows the system to follow objects even when they move outside their original "home" ROI.

---

## Key Differences: Method 1 vs Method 2

### Method 1 (ROI-Based Detection)
```
❌ Object MUST stay in the ROI
❌ Detects by class name only
❌ Can't distinguish between multiple objects of same type
✓ Simple and lightweight
✓ Works well for stationary objects
```

**How it works:**
1. Crop frame to ROI
2. Detect objects in cropped area
3. Check if target class name is present
4. Alert if not found

**Limitation:** If object moves outside ROI, instant alert!

---

### Method 2 (Tracker-Based Monitoring) ⭐ CURRENT
```
✓ Tracks objects ANYWHERE in the frame
✓ Each object has unique ID
✓ Can distinguish multiple objects of same type
✓ Object can move freely
✓ More robust tracking
❌ Slightly more CPU intensive
```

**How it works:**
1. Run tracker on full frame
2. Assign unique ID to each object (e.g., cup: ID 12)
3. Check if target IDs are present anywhere in frame
4. Alert if ID disappears (object removed/hidden)

**Advantage:** Object can move around - only alerts if it leaves the frame or is hidden!

---

## Technical Implementation

### Data Structure Changes

**Before (Method 1):**
```python
roi_targets = [{
    'coords': (x1, y1, x2, y2),      # ROI position
    'target': 'cup',                  # Class name
    'state_manager': StateManager()
}]
```

**After (Method 2):**
```python
roi_targets = [{
    'initial_roi': (x1, y1, x2, y2), # "Home" position (visual reference)
    'target_id': 12,                  # Unique tracking ID
    'target_name': 'cup',             # Class name (for display)
    'state_manager': StateManager()
}]
```

---

### Core Algorithm Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    INITIALIZATION                           │
└─────────────────────────────────────────────────────────────┘

1. User selects ROI(s) on captured frame
   ↓
2. Run tracker on initial frame:
   results = model.track(frame, persist=True, verbose=False)
   ↓
3. For each ROI, find which tracked object is inside:
   - Loop through all detected boxes
   - Calculate overlap with ROI
   - Find best match
   - Save that object's tracking ID
   ↓
4. Store: {initial_roi, target_id, target_name, state_manager}

┌─────────────────────────────────────────────────────────────┐
│                    MAIN LOOP                                │
└─────────────────────────────────────────────────────────────┘

For each frame:
   ↓
1. Run tracker on FULL frame (not just ROI):
   results = model.track(frame, persist=True, verbose=False)
   ↓
2. Extract all current tracking IDs:
   current_detected_ids = {12, 34, 56, ...}
   ↓
3. For each monitored object:
   - Check: is target_id in current_detected_ids?
   - object_present = (target_id in current_detected_ids)
   - Update state manager
   ↓
4. Visualization:
   - Draw "home" ROI (colored by state: green/red)
   - Draw tracker boxes (shows current positions)
   - Display status
```

---

## Key Functions

### 1. `find_tracked_objects_in_rois(results, rois_list, model)`

**Purpose:** After running tracker on initial frame, match tracked objects to user-drawn ROIs.

**Process:**
```python
For each ROI:
    For each detected box:
        Calculate overlap between box and ROI
    
    Best match = box with highest overlap
    
    Extract:
        - Tracking ID (from result.boxes.id)
        - Class name (from result.boxes.cls)
    
    Store: {initial_roi, target_id, target_name, state_manager}
```

**Returns:** List of tracked object configurations

---

### 2. Main Loop Tracking Logic

**Old (Method 1):**
```python
# Crop to ROI only
roi_frame = frame[y1:y2, x1:x2]

# Detect in cropped area
results = model(roi_frame, verbose=False)

# Check if class name present
object_present = target_name in detected_names
```

**New (Method 2):**
```python
# Track on FULL frame
results = model.track(frame, persist=True, verbose=False)

# Get all current IDs
current_detected_ids = set(results[0].boxes.id.int().tolist())

# Check if our specific ID present
object_present = target_id in current_detected_ids
```

---

## Visualization Features

### 1. "Home" ROI Box
- **Color:** Green (secured), Yellow (initializing), Red (alert)
- **Purpose:** Shows original location where object should be
- **Label:** "ROI1: cup (ID:12)"

### 2. Tracker Boxes
- **Drawn by:** `results[0].plot()`
- **Shows:** Current position of all tracked objects
- **Label:** "cup 12" (class name + tracking ID)
- **Purpose:** See where object is now (even if it moved)

### 3. Status Text
- **Line 1:** Overall status (All Secured / ALERT)
- **Line 2:** "METHOD 2: Tracker Mode" indicator

---

## Example Scenario

### Setup:
```
1. User draws ROI around a cup at position (100, 100, 200, 200)
2. Tracker detects: cup at (150, 150) with ID=12
3. System saves:
   {
     'initial_roi': (100, 100, 200, 200),
     'target_id': 12,
     'target_name': 'cup'
   }
```

### Monitoring:
```
Frame 1: Cup at (150, 150) → ID 12 present → ✓ SECURED
Frame 2: Cup at (300, 150) → ID 12 present → ✓ SECURED (moved but OK!)
Frame 3: Cup at (500, 500) → ID 12 present → ✓ SECURED (still tracked)
Frame 4: Cup removed      → ID 12 missing  → 🚨 ALERT!
```

**Key Point:** Unlike Method 1, the cup can move anywhere in the frame and remain secured. Only removal triggers alert.

---

## Advantages Over Method 1

### 1. **Object Can Move Freely**
- Method 1: Cup leaves ROI → Instant alert ❌
- Method 2: Cup leaves ROI → Still tracked ✓

### 2. **Unique Object Identity**
- Method 1: Can't tell which "cup" is which
- Method 2: Each cup has unique ID (12, 34, etc.)

### 3. **More Robust**
- Method 1: Lighting change in ROI → False alert
- Method 2: Object tracked by features, more stable

### 4. **Better for Multiple Objects**
- Method 1: Needs tight ROIs for each object
- Method 2: Objects can be close together

---

## Limitations & Considerations

### 1. **Tracking Can Fail**
If object is:
- Occluded (hidden behind something)
- Moves very fast
- Leaves frame completely
- Changes appearance dramatically

**Solution:** `persist=True` helps maintain IDs across frames

### 2. **More CPU Intensive**
- Method 1: Only processes small ROI
- Method 2: Processes full frame

**Impact:** ~5-10% more CPU usage

### 3. **ID Can Change After Re-init**
- When pressing 'r' to reset, IDs may change
- Not an issue for monitoring, just visual

---

## Configuration

All configuration is in `config.py`:

```python
# Video source
VIDEO_SOURCE = 0  # Webcam

# Model
MODEL_PATH = "yolov8n.pt"  # Tracking works with any YOLO model

# Alert threshold
ALERT_THRESHOLD = 25  # Frames before alert (1 second at 25 FPS)
```

---

## Troubleshooting

### Issue: "No tracking IDs assigned yet"
**Cause:** Objects not detected in initial frame
**Solution:** 
- Ensure good lighting
- Keep objects still when capturing frame
- Draw ROI tightly around object

### Issue: "No tracked objects found in any ROI"
**Cause:** ROI doesn't overlap with detected object
**Solution:**
- Draw ROI more carefully around object
- Make sure object is fully visible
- Try again with better frame capture

### Issue: Tracking ID changes frequently
**Cause:** Poor lighting or fast motion
**Solution:**
- Improve lighting
- Use higher FPS camera
- Reduce motion during setup

### Issue: False alerts when object partially hidden
**Cause:** Tracker loses object briefly
**Solution:**
- Increase ALERT_THRESHOLD in config
- Improve lighting
- Avoid obstructions

---

## Performance Tips

### For Best Tracking:
1. **Good Lighting** - Critical for stable tracking
2. **Stable Camera** - Mount camera if possible
3. **Clear View** - Minimize obstructions
4. **Distinct Objects** - Easier to track unique objects

### For Better Performance:
1. **Use yolov8n.pt** - Fastest model
2. **Limit ROIs** - Track 1-4 objects max
3. **Lower Resolution** - If FPS is low
4. **Close Other Apps** - Free up CPU

---

## When to Use Method 2

✓ **Use Method 2 when:**
- Objects might move around
- Need to track specific object instances
- Multiple objects of same type
- More robust monitoring needed

❌ **Use Method 1 when:**
- Objects are always stationary
- Maximum performance needed
- Simple "is something there?" check
- Don't care about object identity

---

## Code Summary

### Initialization:
```python
# Run tracker once on initial frame
track_results = model.track(frame, persist=True, verbose=False)

# Find objects in ROIs and get their IDs
roi_targets = find_tracked_objects_in_rois(track_results, rois_list, model)
```

### Main Loop:
```python
# Track all objects in frame
results = model.track(frame, persist=True, verbose=False)

# Get current IDs
current_ids = set(results[0].boxes.id.int().tolist())

# Check each target
for roi_data in roi_targets:
    object_present = roi_data['target_id'] in current_ids
    state = roi_data['state_manager'].update_status(object_present)
    
# Draw visualizations
annotated_frame = results[0].plot()  # Tracker boxes
# + draw home ROIs + status text
```

---

**Method 2 is now active in your system!** 🎉

Objects can move freely in the frame and will only trigger alerts if they disappear completely.

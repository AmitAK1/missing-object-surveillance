"""
Surveillance Engine - Backend logic for object tracking and monitoring
Separated from GUI for better architecture
"""

import cv2
import numpy as np
from ultralytics import YOLO
from core.state_manager import StateManager
from core.statistics_manager import get_statistics_manager
from utils.email_alerter import get_email_alerter
import config
import os
from datetime import datetime
import time
from typing import List, Dict, Tuple, Optional, Callable


class SurveillanceEngine:
    """Main surveillance engine handling all tracking and monitoring logic"""
    
    def __init__(self, model_path: str = None, video_source: int = 0):
        """Initialize the surveillance engine"""
        self.model_path = model_path or config.MODEL_PATH
        self.video_source = video_source if video_source is not None else config.VIDEO_SOURCE
        self.alert_threshold = config.ALERT_THRESHOLD
        
        self.model = None
        self.cap = None
        self.roi_targets = []
        self.current_frame = None
        self.reference_frame = None  # Store the captured frame for reselection
        self.is_monitoring = False
        
        # Statistics
        self.total_alerts = 0
        self.alert_history = []
        self.captured_frames = []
        self.stats_manager = get_statistics_manager()
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Callbacks for GUI updates
        self.on_frame_update: Optional[Callable] = None
        self.on_status_update: Optional[Callable] = None
        self.on_alert: Optional[Callable] = None
        
    def load_model(self) -> bool:
        """Load the YOLO model"""
        try:
            print(f"Loading model: {self.model_path}")
            self.model = YOLO(self.model_path)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def initialize_camera(self) -> bool:
        """Initialize video capture"""
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            if not self.cap.isOpened():
                print(f"Error: Could not open video source {self.video_source}")
                return False
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera"""
        if self.cap is None:
            return False, None
        
        success, frame = self.cap.read()
        if success:
            self.current_frame = frame.copy()
        return success, frame
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture and save the current frame"""
        if self.current_frame is None:
            return None
        
        # Save to captured frames list
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        frame_copy = self.current_frame.copy()
        
        # Store as reference frame for reselection
        self.reference_frame = frame_copy.copy()
        
        # Create output directory if it doesn't exist
        os.makedirs("output/captured_frames", exist_ok=True)
        filename = f"output/captured_frames/frame_{timestamp}.jpg"
        cv2.imwrite(filename, frame_copy)
        
        self.captured_frames.append({
            'timestamp': timestamp,
            'filename': filename,
            'frame': frame_copy
        })
        
        print(f"Frame captured and saved: {filename}")
        return frame_copy
    
    def select_roi_coords(self, frame: np.ndarray, window_name: str = "Select ROI", multi: bool = False):
        """
        Let user select ROI(s) on a frame using OpenCV's selectROI / selectROIs
        If multi is False: returns (x, y, w, h) or (0,0,0,0) if cancelled
        If multi is True: returns a list/tuple of ROIs (each is (x,y,w,h)) or an empty tuple if cancelled
        """
        try:
            if multi:
                # Custom multi-ROI selector to avoid cv2.selectROIs bugs
                return self._custom_multi_roi_selector(frame, window_name)
            else:
                roi = cv2.selectROI(window_name, frame, fromCenter=False, showCrosshair=True)
                cv2.destroyAllWindows()
                for _ in range(3):
                    cv2.waitKey(1)
                return roi
        except Exception as e:
            print(f"Error during ROI selection: {e}")
            cv2.destroyAllWindows()
            for _ in range(3):
                cv2.waitKey(1)
            return () if multi else (0, 0, 0, 0)
    
    def _custom_multi_roi_selector(self, frame: np.ndarray, window_name: str):
        """Custom implementation of multi-ROI selection to avoid cv2.selectROIs bugs"""
        print("\n" + "=" * 60)
        print("=== MULTIPLE ROI SELECTION ===")
        print("=" * 60)
        print("📝 Instructions:")
        print("  1. Draw a box around the FIRST object (click & drag)")
        print("  2. Press SPACE/ENTER to confirm the box")
        print("  3. Draw another box OR press 'Q' when DONE")
        print("  4. Press ESC to CANCEL anytime")
        print("=" * 60)
        print()
        
        rois = []
        continue_selection = True
        
        while continue_selection:
            roi_count = len(rois) + 1
            print(f"\n🎯 Draw ROI #{roi_count}... (Click & drag, then press SPACE/ENTER)")
            
            # Create display frame with existing ROIs
            display_frame = frame.copy()
            
            # Draw existing ROIs in green
            for i, (x, y, w, h) in enumerate(rois):
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(display_frame, f"ROI #{i+1}", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add instructions overlay
            overlay_text = f"Selected: {len(rois)} | Draw ROI #{roi_count} | Press 'Q' when done"
            cv2.putText(display_frame, overlay_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Let user select ROI
            roi = cv2.selectROI(window_name, display_frame, fromCenter=False, showCrosshair=True)
            x, y, w, h = roi
            
            # Check if ROI is valid
            if w > 0 and h > 0:
                rois.append([x, y, w, h])
                print(f"✅ ROI #{roi_count} confirmed: ({x}, {y}, {w}, {h})")
                
                # Ask user if they want to continue
                print(f"\n📋 You have selected {len(rois)} ROI(s).")
                print("   Press 'Q' to FINISH, or any other key to add another ROI...")
                
                # Show preview with all ROIs
                preview_frame = frame.copy()
                for i, (rx, ry, rw, rh) in enumerate(rois):
                    cv2.rectangle(preview_frame, (rx, ry), (rx+rw, ry+rh), (0, 255, 0), 3)
                    cv2.putText(preview_frame, f"ROI #{i+1}", (rx, ry-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.putText(preview_frame, f"Total: {len(rois)} ROI(s) | Q=Done | Any key=Add more", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow(window_name, preview_frame)
                
                key = cv2.waitKey(0) & 0xFF
                
                if key == ord('q') or key == ord('Q'):
                    continue_selection = False
                    print(f"✅ Finished! Total {len(rois)} ROI(s) selected.")
                # Any other key continues the loop
                
            else:
                print(f"⚠️ ROI cancelled or invalid (w={w}, h={h})")
                
                if len(rois) == 0:
                    print("❌ No ROIs selected. Exiting...")
                    cv2.destroyAllWindows()
                    for _ in range(3):
                        cv2.waitKey(1)
                    return np.array([])
                else:
                    # Ask if user wants to finish with current ROIs
                    print(f"   You have {len(rois)} ROI(s) already.")
                    print("   Press 'Q' to FINISH with current ROIs, or any other key to try again...")
                    
                    preview_frame = frame.copy()
                    for i, (rx, ry, rw, rh) in enumerate(rois):
                        cv2.rectangle(preview_frame, (rx, ry), (rx+rw, ry+rh), (0, 255, 0), 3)
                        cv2.putText(preview_frame, f"ROI #{i+1}", (rx, ry-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow(window_name, preview_frame)
                    
                    key = cv2.waitKey(0) & 0xFF
                    if key == ord('q') or key == ord('Q'):
                        continue_selection = False
                        print(f"✅ Finished with {len(rois)} ROI(s).")
        
        cv2.destroyAllWindows()
        for _ in range(3):
            cv2.waitKey(1)
        return np.array(rois)
    
    def setup_single_roi(self, frame: np.ndarray) -> bool:
        """Setup single ROI tracking"""
        print("\n=== Single ROI Mode ===")
        
        # Select ROI
        roi = self.select_roi_coords(frame, "Select ROI - Single Object", multi=False)

        print(f"DEBUG: ROI returned: {roi}, type: {type(roi)}")
        
        # If user cancelled selection, selectROI returns (0,0,0,0) or roi with w=0 or h=0
        if roi is None or not roi or len(roi) != 4:
            print("ROI selection cancelled - invalid format.")
            return False
        
        x, y, w, h = roi
        
        print(f"DEBUG: Extracted values - x={x}, y={y}, w={w}, h={h}")
        
        # FIRST: Check if all values are exactly 0 (ESC was pressed without drawing)
        if x == 0 and y == 0 and w == 0 and h == 0:
            print("ROI selection cancelled - ESC pressed or no selection made.")
            return False
        
        # SECOND: Check if width or height is zero or negative (invalid selection)
        if w <= 0 or h <= 0:
            print("ROI selection cancelled or invalid - zero/negative dimensions.")
            return False
        
        # THIRD: Check if ROI is too small (likely accidental)
        if w < 10 or h < 10:
            print("ROI selection too small - invalid.")
            return False

        # Convert to (x1, y1, x2, y2)
        x2, y2 = x + w, y + h
        roi_coords = (int(x), int(y), int(x2), int(y2))
        
        # Run tracker on the frame
        track_results = self.model.track(frame, persist=True, verbose=False)
        
        # Find tracked object in ROI
        self.roi_targets = self._find_tracked_objects_in_rois(track_results, [roi_coords])
        
        if not self.roi_targets:
            print("Warning: No tracked object found in ROI.")
            return False
        
        print(f"✓ Single ROI setup complete. Tracking: {self.roi_targets[0]['target_name']}")
        return True
    
    def setup_multiple_rois(self, frame: np.ndarray) -> bool:
        """Setup multiple ROI tracking"""
        print("\n=== Multiple ROI Mode ===")
        # Use OpenCV's selectROIs to allow multiple selection in one window
        rois = self.select_roi_coords(frame, "Select Multiple ROIs", multi=True)

        # rois is a numpy array or empty tuple if cancelled or no selection made
        print(f"DEBUG: ROIs returned: {rois}, type: {type(rois)}, length: {len(rois) if hasattr(rois, '__len__') else 'N/A'}")
        
        # Check if cancelled or empty (use len() instead of "not rois" to avoid numpy array ambiguity)
        if rois is None or len(rois) == 0:
            print("❌ No ROIs selected or selection cancelled.")
            return False

        print(f"\n📦 Processing {len(rois)} selected ROI(s)...")
        rois_list = []
        for i, roi in enumerate(rois):
            x, y, w, h = roi
            
            # Skip invalid ROIs (width or height is 0)
            if w <= 0 or h <= 0:
                print(f"⚠️ ROI #{i+1} skipped (invalid dimensions: w={w}, h={h})")
                continue
                
            x2, y2 = x + w, y + h
            roi_coords = (int(x), int(y), int(x2), int(y2))
            rois_list.append(roi_coords)
            print(f"✅ ROI #{i+1} confirmed: coordinates {roi_coords}")
        
        # Check if we have any valid ROIs after filtering
        if len(rois_list) == 0:
            print("❌ No valid ROIs selected (all had invalid dimensions).")
            return False

        print(f"🔍 Running object detection on frame to assign tracking IDs...")
        # Run tracker on the frame
        track_results = self.model.track(frame, persist=True, verbose=False)

        # Find tracked objects in all ROIs
        self.roi_targets = self._find_tracked_objects_in_rois(track_results, rois_list)
        
        if not self.roi_targets:
            print("❌ Warning: No tracked objects found in any ROI. Make sure objects are visible in the selected areas.")
            return False
        
        print(f"✅ Multiple ROI setup complete! Tracking {len(self.roi_targets)} objects.")
        for idx, target in enumerate(self.roi_targets):
            print(f"   - Object {idx+1}: {target['target_name']} (ID: {target['target_id']})")
        return True
    
    def _find_tracked_objects_in_rois(self, results, rois_list: List[Tuple]) -> List[Dict]:
        """
        Find which tracked objects are in each ROI
        Returns list of dicts with 'initial_roi', 'target_id', 'target_name', 'state_manager'
        """
        roi_targets = []
        
        if not results or len(results) == 0:
            print("Warning: No tracking results on initial frame.")
            return roi_targets
        
        result = results[0]
        
        if result.boxes is None or len(result.boxes) == 0:
            print("Warning: No objects detected in initial frame.")
            return roi_targets
        
        # Get tracked data
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()
        
        if result.boxes.id is not None:
            track_ids = result.boxes.id.cpu().numpy()
        else:
            print("Warning: No tracking IDs assigned yet.")
            return roi_targets
        
        # For each ROI, find best matching tracked object
        for roi_idx, roi_coords in enumerate(rois_list):
            rx1, ry1, rx2, ry2 = roi_coords
            
            best_match = None
            best_overlap = 0
            
            for i in range(len(boxes)):
                bx1, by1, bx2, by2 = boxes[i]
                
                # Calculate overlap
                inter_x1 = max(rx1, bx1)
                inter_y1 = max(ry1, by1)
                inter_x2 = min(rx2, bx2)
                inter_y2 = min(ry2, by2)
                
                if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                    box_area = (bx2 - bx1) * (by2 - by1)
                    overlap_ratio = inter_area / box_area if box_area > 0 else 0
                    
                    if overlap_ratio > best_overlap:
                        best_overlap = overlap_ratio
                        best_match = i
            
            if best_match is not None:
                target_id = int(track_ids[best_match])
                class_id = int(classes[best_match])
                target_name = self.model.names[class_id]
                
                roi_targets.append({
                    'initial_roi': roi_coords,
                    'target_id': target_id,
                    'target_name': target_name,
                    'state_manager': StateManager(self.alert_threshold)
                })
                
                print(f"ROI #{roi_idx+1}: Found '{target_name}' with tracking ID={target_id}")
            else:
                print(f"ROI #{roi_idx+1}: No object detected inside this ROI")
        
        return roi_targets
    
    def process_frame(self) -> Tuple[bool, Optional[np.ndarray], bool]:
        """
        Process one frame during monitoring
        Returns: (success, annotated_frame, any_alert)
        """
        if not self.is_monitoring or self.model is None:
            return False, None, False
        
        success, frame = self.get_frame()
        if not success:
            return False, None, False
        
        # Calculate FPS
        self.fps_counter += 1
        elapsed = time.time() - self.fps_start_time
        if elapsed >= 1.0:  # Update FPS every second
            self.current_fps = self.fps_counter / elapsed
            self.stats_manager.record_fps(self.current_fps)
            self.fps_counter = 0
            self.fps_start_time = time.time()
        
        # Run tracker on full frame
        results = self.model.track(frame, persist=True, verbose=False)
        
        # Get currently tracked IDs
        current_detected_ids = set()
        if results and len(results) > 0 and results[0].boxes.id is not None:
            current_detected_ids = set(results[0].boxes.id.int().cpu().tolist())
            
            # Record detection confidence (only every 30 frames to reduce overhead)
            if self.fps_counter % 30 == 0 and results[0].boxes.conf is not None:
                confidences = results[0].boxes.conf.cpu().tolist()
                for conf in confidences:
                    self.stats_manager.record_detection_confidence(conf)
        
        # Record number of objects tracked (only every 30 frames to reduce overhead)
        if self.fps_counter % 30 == 0:
            self.stats_manager.record_objects_tracked(len(current_detected_ids))
        
        # Draw tracker boxes first (on a copy)
        if results and len(results) > 0:
            annotated_frame = results[0].plot()
        else:
            annotated_frame = frame.copy()
        
        # Check each target and draw ROI boxes on the annotated frame
        any_alert = False
        alert_objects = []  # Track which objects are in alert state
        
        for idx, roi_data in enumerate(self.roi_targets):
            initial_roi = roi_data['initial_roi']
            target_id = roi_data['target_id']
            target_name = roi_data['target_name']
            state_mgr = roi_data['state_manager']
            
            # Check if target is present
            object_present = target_id in current_detected_ids
            
            # Update state
            current_state = state_mgr.update_status(object_present)
            
            # Determine color
            if current_state == "SECURED":
                color = (0, 255, 0)  # Green
            elif current_state == "INITIALIZING":
                color = (0, 255, 255)  # Yellow
            else:  # ALERT
                color = (0, 0, 255)  # Red
                any_alert = True
                
                # Check if this object hasn't triggered an alert yet (per-ROI tracking)
                if not roi_data.get('alert_triggered', False):
                    alert_objects.append({
                        'name': target_name,
                        'id': target_id,
                        'roi_index': idx + 1
                    })
                    roi_data['alert_triggered'] = True  # Mark this specific ROI as alerted
            
            # Reset alert flag when object returns
            if current_state == "SECURED" and roi_data.get('alert_triggered', False):
                roi_data['alert_triggered'] = False
            
            # Draw ROI on annotated frame (not original)
            x1, y1, x2, y2 = initial_roi
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
            
            # Label with background for better visibility
            label = f"ROI{idx+1}: {target_name} (ID:{target_id})"
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            # Draw background rectangle
            cv2.rectangle(annotated_frame, 
                         (x1, y1-text_height-10), 
                         (x1+text_width, y1),
                         color, -1)
            # Draw text
            cv2.putText(annotated_frame, label, (x1, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Handle alerts for objects that just entered ALERT state
        if len(alert_objects) > 0:
            self._trigger_alert(annotated_frame, alert_objects)
        
        # Callbacks
        if self.on_frame_update:
            self.on_frame_update(annotated_frame)
        
        if self.on_status_update:
            self.on_status_update(self.get_status())
        
        return True, annotated_frame, any_alert
    
    def _trigger_alert(self, frame: np.ndarray, alert_objects: List[Dict]):
        """Trigger an alert and save snapshot for specific objects"""
        timestamp = datetime.now()
        
        # Save alert image
        os.makedirs("output/alerts", exist_ok=True)
        filename = f"output/alerts/alert_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)
        
        # Use the provided alert_objects list (objects that just entered ALERT state)
        missing_objects = alert_objects
        
        # Update total alerts count
        self.total_alerts += len(missing_objects)
        
        # Record alert
        alert_record = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'missing_objects': missing_objects
        }
        self.alert_history.append(alert_record)
        
        print(f"🚨 ALERT! Snapshot saved: {filename}")
        print(f"Missing objects: {[obj['name'] for obj in missing_objects]}")
        
        # Record statistics for each missing object
        for obj in missing_objects:
            self.stats_manager.record_alert(
                object_name=obj['name'],
                object_id=obj['id'],
                roi_index=obj.get('roi_index')
            )
            print(f"📊 Alert recorded: {obj['name']} (Total: {self.stats_manager.total_alerts})")
        
        # Send email alerts asynchronously (in background thread)
        def send_emails_async():
            email_alerter = get_email_alerter()
            for obj in missing_objects:
                success = email_alerter.send_alert(
                    object_name=obj['name'],
                    object_id=obj['id'],
                    image_path=filename,
                    roi_index=obj.get('roi_index')
                )
                self.stats_manager.record_email_sent(success)
        
        # Start email sending in background thread (non-blocking)
        import threading
        email_thread = threading.Thread(target=send_emails_async, daemon=True)
        email_thread.start()
        
        # Callback
        if self.on_alert:
            self.on_alert(alert_record)
    
    def start_monitoring(self):
        """Start monitoring mode"""
        self.is_monitoring = True
        print("✓ Monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring mode"""
        self.is_monitoring = False
        print("✓ Monitoring stopped")
    
    def reset_tracking(self):
        """Reset tracker and ROIs"""
        self.roi_targets = []
        self.is_monitoring = False
        self.alert_triggered = False
        
        # Reload model to reset tracker
        if self.model_path:
            self.model = YOLO(self.model_path)
        
        print("✓ Tracking reset")
    
    def get_status(self) -> Dict:
        """Get current status information"""
        # Check if any ROI is currently in alert state
        any_alert_active = any(roi.get('alert_triggered', False) for roi in self.roi_targets)
        
        return {
            'is_monitoring': self.is_monitoring,
            'num_objects': len(self.roi_targets),
            'total_alerts': self.total_alerts,
            'alert_active': any_alert_active,
            'objects': [
                {
                    'name': roi['target_name'],
                    'id': roi['target_id'],
                    'state': roi['state_manager'].state  # Changed from current_state to state
                }
                for roi in self.roi_targets
            ]
        }
    
    def get_alert_history(self) -> List[Dict]:
        """Get all alert records"""
        return self.alert_history.copy()
    
    def get_captured_frames(self) -> List[Dict]:
        """Get all captured frames"""
        return self.captured_frames.copy()
    
    def cleanup(self):
        """Release resources"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✓ Resources released")

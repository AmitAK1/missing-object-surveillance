import cv2
import sys
from ultralytics import YOLO
from core.state_manager import StateManager
import config

def select_roi(frame):
    """
    Lets the user select an ROI on the given frame.
    Adds key controls to 'c' to cancel/redraw.
    """
    roi = (0, 0, 0, 0)
    print("\n" + "="*50)
    print("ROI Selector: Draw a box around your object.")
    print("Press 'ENTER' or 'SPACE' to confirm.")
    print("Press 'c' to cancel and redraw.")
    print("="*50 + "\n")

    while True:
        # Use OpenCV's selectROI function
        roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=True)
        
        # Force window cleanup
        cv2.destroyWindow("Select ROI")
        cv2.waitKey(1)  # Process pending events
        cv2.waitKey(1)  # Double call to ensure cleanup on Windows

        if roi != (0, 0, 0, 0):
            # Valid ROI selected
            return roi
        else:
            print("ROI selection cancelled. Please redraw.")

def select_multiple_rois(frame):
    """
    Lets the user select multiple ROIs on the given frame.
    Returns a list of (roi_coords, target_name) tuples.
    """
    rois = []
    print("\n" + "="*60)
    print("MULTIPLE ROI MODE")
    print("Select as many ROIs as you want.")
    print("Press 'q' when done selecting ROIs.")
    print("="*60 + "\n")
    
    roi_count = 0
    display_frame = frame.copy()
    
    while True:
        roi_count += 1
        print(f"\n--- Selecting ROI #{roi_count} ---")
        print("Draw the ROI, then press ENTER/SPACE to confirm.")
        print("Press 'c' to cancel this ROI.")
        
        roi = cv2.selectROI(f"Select ROI #{roi_count}", display_frame, fromCenter=False, showCrosshair=True)
        
        # Force window cleanup
        cv2.destroyWindow(f"Select ROI #{roi_count}")
        cv2.waitKey(1)
        cv2.waitKey(1)
        
        if roi == (0, 0, 0, 0):
            print("ROI cancelled. Skipping.")
            continue
        
        # Convert to (x1, y1, x2, y2)
        x1, y1, w, h = roi
        x2, y2 = x1 + w, y1 + h
        roi_coords = (int(x1), int(y1), int(x2), int(y2))
        
        # Draw this ROI on the display frame for reference
        cv2.rectangle(display_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(display_frame, f"ROI {roi_count}", (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        rois.append(roi_coords)
        print(f"ROI #{roi_count} saved: {roi_coords}")
        
        # Ask if user wants to add more
        print("\nPress 'a' to add another ROI, or any other key to finish...")
        cv2.imshow("Selected ROIs", display_frame)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        cv2.waitKey(1)
        
        if key != ord('a'):
            break
    
    return rois
            
def auto_detect_target(model, frame, roi):
    """
    Automatically detects the most confident object inside the ROI
    and sets it as the target.
    """
    # Handle both tuple formats: (x, y, w, h) from selectROI or (x1, y1, x2, y2)
    if len(roi) == 4:
        # Check if it's (x, y, w, h) or (x1, y1, x2, y2)
        # If third value is smaller than first, it's likely (x, y, w, h)
        if roi[2] < roi[0]:  # w < x1, unlikely for x2 format
            x1, y1, w, h = roi
            x2, y2 = x1 + w, y1 + h
        else:
            x1, y1, x2, y2 = roi
    else:
        raise ValueError("ROI must be a tuple of 4 values")
    
    roi_frame = frame[y1:y2, x1:x2]
    
    results = model(roi_frame, verbose=False)
    
    best_conf = 0
    target_name = None
    
    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])
            if conf > best_conf:
                best_conf = conf
                class_id = int(box.cls[0])
                target_name = model.names[class_id]
                
    if target_name:
        print(f"Target object auto-detected: {target_name} (Confidence: {best_conf:.2f})")
    else:
        print("Warning: Could not detect any known object in the ROI.")
        print("Will monitor for 'generic object' presence (any detection).")
        target_name = "any" # Fallback
        
    return target_name

def find_tracked_objects_in_rois(results, rois_list, model):
    """
    METHOD 2 HELPER: After running tracker on initial frame, find which tracked IDs
    are inside each ROI and return the mapping.
    
    Returns: list of dicts with 'initial_roi', 'target_id', 'target_name'
    """
    roi_targets = []
    
    if not results or len(results) == 0:
        print("Warning: No tracking results on initial frame.")
        return roi_targets
    
    result = results[0]
    
    # Check if any objects were tracked
    if result.boxes is None or len(result.boxes) == 0:
        print("Warning: No objects detected in initial frame for tracking.")
        return roi_targets
    
    # Get all tracked boxes
    boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
    classes = result.boxes.cls.cpu().numpy()
    
    # Get tracking IDs (may be None if no objects tracked)
    if result.boxes.id is not None:
        track_ids = result.boxes.id.cpu().numpy()
    else:
        print("Warning: No tracking IDs assigned yet. Trying again...")
        return roi_targets
    
    # For each ROI, find objects inside it
    for roi_idx, roi_coords in enumerate(rois_list):
        rx1, ry1, rx2, ry2 = roi_coords
        
        best_match = None
        best_overlap = 0
        
        # Find which tracked object has the most overlap with this ROI
        for i in range(len(boxes)):
            bx1, by1, bx2, by2 = boxes[i]
            
            # Calculate overlap (Intersection over Union style)
            inter_x1 = max(rx1, bx1)
            inter_y1 = max(ry1, by1)
            inter_x2 = min(rx2, bx2)
            inter_y2 = min(ry2, by2)
            
            if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                # There's an overlap
                inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                box_area = (bx2 - bx1) * (by2 - by1)
                overlap_ratio = inter_area / box_area if box_area > 0 else 0
                
                if overlap_ratio > best_overlap:
                    best_overlap = overlap_ratio
                    best_match = i
        
        if best_match is not None:
            # Found an object in this ROI
            target_id = int(track_ids[best_match])
            class_id = int(classes[best_match])
            target_name = model.names[class_id]
            
            roi_targets.append({
                'initial_roi': roi_coords,
                'target_id': target_id,
                'target_name': target_name,
                'state_manager': StateManager(config.ALERT_THRESHOLD)
            })
            
            print(f"ROI #{roi_idx+1}: Found '{target_name}' with tracking ID={target_id}")
        else:
            print(f"ROI #{roi_idx+1}: No object detected inside this ROI")
    
    return roi_targets

def capture_frame_for_roi(cap):
    """
    Live preview mode - lets user choose when to capture frame for ROI selection.
    Returns the captured frame or None if user quits.
    """
    print("\n" + "="*60)
    print("LIVE PREVIEW MODE")
    print("="*60)
    print("Controls:")
    print("  'c' - Capture current frame for ROI selection")
    print("  'r' - Refresh (continues live preview)")
    print("  'q' - Quit program")
    print("="*60 + "\n")
    
    captured_frame = None
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame from video source.")
            return None
        
        # Display instructions on frame
        display_frame = frame.copy()
        cv2.putText(display_frame, "LIVE PREVIEW - Press 'c' to capture frame", 
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(display_frame, "Press 'q' to quit", 
                    (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Frame Capture", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            print("Frame captured! Proceeding to ROI selection...")
            captured_frame = frame.copy()
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            cv2.waitKey(1)
            return captured_frame
        
        elif key == ord('q'):
            print("User quit during frame capture.")
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            cv2.waitKey(1)
            return None
        
        elif key == ord('r'):
            print("Refreshing preview...")
            continue

def main():
    # Load the model from config
    print(f"Loading model: {config.MODEL_PATH}")
    model = YOLO(config.MODEL_PATH)

    # Initialize video capture
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Error: Could not open video source {config.VIDEO_SOURCE}")
        return

    # --- Initialization Step ---
    print("\nStarting live preview for frame capture...")
    frame = capture_frame_for_roi(cap)
    if frame is None:
        print("Exiting program.")
        cap.release()
        return

    # Ask user if they want single or multiple ROI mode
    print("\nSelect mode:")
    print("Press 's' for SINGLE ROI mode (default)")
    print("Press 'm' for MULTIPLE ROI mode")
    cv2.imshow("Mode Selection", frame)
    mode_key = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.waitKey(1)
    
    multiple_mode = (mode_key == ord('m'))
    
    # Initialize roi_targets list
    roi_targets = []
    
    # --- METHOD 2: Use Tracker to Find Objects in ROIs ---
    print("\n--- Running tracker on initial frame to find objects ---")
    
    # Run tracker once on the initial frame to get tracking IDs
    track_results = model.track(frame, persist=True, verbose=False)
    
    if multiple_mode:
        # Multiple ROI mode
        rois_list = select_multiple_rois(frame)
        if not rois_list:
            print("No ROIs selected. Exiting.")
            cap.release()
            return
        
        # Find tracked objects in each ROI
        roi_targets = find_tracked_objects_in_rois(track_results, rois_list, model)
        
        if not roi_targets:
            print("Warning: No tracked objects found in any ROI.")
            print("Make sure objects are visible and still when selecting ROIs.")
            cap.release()
            return
            
    else:
        # Single ROI mode (default)
        roi_coords = select_roi(frame)
        x1, y1, w, h = roi_coords
        x2, y2 = x1 + w, y1 + h
        roi_coords = (int(x1), int(y1), int(x2), int(y2))

        # Find tracked object in this single ROI
        roi_targets = find_tracked_objects_in_rois(track_results, [roi_coords], model)
        
        if not roi_targets:
            print("Warning: No tracked object found in ROI.")
            print("Make sure an object is visible in the ROI when you draw it.")
            cap.release()
            return
    
    print(f"\n✓ Tracking initialized with {len(roi_targets)} object(s)")
    print("=" * 60)

    alert_triggered = False
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Video feed ended.")
            break

        # --- METHOD 2: Run Tracker on Full Frame ---
        # Track all objects in the entire frame (not just ROI)
        results = model.track(frame, persist=True, verbose=False)
        
        # Get all currently tracked IDs
        current_detected_ids = set()
        if results and len(results) > 0 and results[0].boxes.id is not None:
            current_detected_ids = set(results[0].boxes.id.int().cpu().tolist())
        
        # --- Core Logic: Check if our target IDs are still present ---
        any_alert = False
        
        for idx, roi_data in enumerate(roi_targets):
            initial_roi = roi_data['initial_roi']
            target_id = roi_data['target_id']
            target_name = roi_data['target_name']
            state_mgr = roi_data['state_manager']
            
            # Check if this target ID is in the current frame
            object_present = target_id in current_detected_ids
            
            # Update the state manager
            current_state = state_mgr.update_status(object_present)

            # --- Visualization ---
            
            # Set color based on state
            if current_state == "SECURED":
                color = (0, 255, 0) # Green
            elif current_state == "INITIALIZING":
                color = (0, 255, 255) # Yellow
            else: # ALERT
                color = (0, 0, 255) # Red
                any_alert = True
            
            # Draw the "Home" ROI bounding box on the frame
            x1, y1, x2, y2 = initial_roi
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Label the ROI with ID and name
            label = f"ROI{idx+1}: {target_name} (ID:{target_id})"
            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw tracker bounding boxes (shows where objects are now)
        if results and len(results) > 0:
            annotated_frame = results[0].plot()  # This draws all tracked objects with IDs
            frame = annotated_frame  # Use the annotated frame
        
        # Overall status display
        if any_alert:
            overall_color = (0, 0, 255)
            overall_text = "STATUS: ALERT! - Object(s) Missing"
            
            # Save alert snapshot
            if not alert_triggered:
                import os
                os.makedirs("output/alerts", exist_ok=True)
                alert_filename = "output/alerts/alert.jpg"
                cv2.imwrite(alert_filename, frame)
                print(f"Alert snapshot saved to {alert_filename}")
                alert_triggered = True
        else:
            overall_color = (0, 255, 0)
            overall_text = "STATUS: All Secured"
            alert_triggered = False
        
        # Put the status text on the frame
        cv2.putText(frame, overall_text, (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, overall_color, 2)
        cv2.putText(frame, "METHOD 2: Tracker Mode | 'r' to re-select, 'q' to quit", (50, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Display the frame
        cv2.imshow("Missing Object Surveillance", frame)

        # --- Key Controls ---
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Quitting program...")
            break
        
        if key == ord('r'):
            print("Restarting ROI selection process...")
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            cv2.waitKey(1)
            
            # Reset the tracker by creating a new model instance
            print("Resetting tracker...")
            model = YOLO(config.MODEL_PATH)
            
            # Capture a good frame for re-selection
            frame = capture_frame_for_roi(cap)
            if frame is None:
                print("Re-selection cancelled. Continuing with previous setup.")
                continue
            
            # Ask mode again
            print("\nSelect mode:")
            print("Press 's' for SINGLE ROI mode (default)")
            print("Press 'm' for MULTIPLE ROI mode")
            cv2.imshow("Mode Selection", frame)
            mode_key = cv2.waitKey(0) & 0xFF
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            cv2.waitKey(1)
            
            multiple_mode = (mode_key == ord('m'))
            
            # Run tracker on the new initial frame
            print("\n--- Running tracker on initial frame to find objects ---")
            track_results = model.track(frame, persist=True, verbose=False)
            
            if multiple_mode:
                rois_list = select_multiple_rois(frame)
                if not rois_list:
                    print("No ROIs selected. Continuing with previous setup.")
                    continue
                
                roi_targets = find_tracked_objects_in_rois(track_results, rois_list, model)
                
                if not roi_targets:
                    print("Warning: No tracked objects found. Continuing with previous setup.")
                    continue
            else:
                roi_coords = select_roi(frame)
                x1, y1, w, h = roi_coords
                x2, y2 = x1 + w, y1 + h
                roi_coords = (int(x1), int(y1), int(x2), int(y2))
                
                roi_targets = find_tracked_objects_in_rois(track_results, [roi_coords], model)
                
                if not roi_targets:
                    print("Warning: No tracked object found. Continuing with previous setup.")
                    continue
            
            alert_triggered = False
            print(f"\n✓ Tracking reinitialized with {len(roi_targets)} object(s)")
            print("ROI selection updated. Resuming surveillance...")
            print("=" * 60)

    # Cleanup
    print("\nCleaning up...")
    cap.release()
    cv2.destroyAllWindows()
    
    # Force cleanup on Windows
    cv2.waitKey(1)
    cv2.waitKey(1)
    
    print("Application closed successfully.")

if __name__ == "__main__":
    main()
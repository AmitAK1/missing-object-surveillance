"""
Missing Object Surveillance - CustomTkinter GUI Application
Professional GUI with camera feed, controls, and data viewing
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time
from core.surveillance_engine import SurveillanceEngine
import config
import os
from datetime import datetime

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SurveillanceGUI:
    """Main GUI Application"""
    
    def __init__(self):
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Missing Object Surveillance System")
        self.root.geometry("1400x800")
        
        # Initialize surveillance engine
        self.engine = SurveillanceEngine()
        
        # GUI state
        self.video_running = False
        self.video_thread = None
        self.current_display_frame = None
        
        # Setup callbacks
        self.engine.on_status_update = self.update_status_display
        self.engine.on_alert = self.on_alert_callback
        
        # Build GUI
        self.setup_ui()
        
        # Initialize system
        self.initialize_system()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup the complete UI layout"""
        # Main container with 2 columns
        self.root.grid_columnconfigure(0, weight=3)  # Camera side (larger)
        self.root.grid_columnconfigure(1, weight=1)  # Controls side
        self.root.grid_rowconfigure(0, weight=1)
        
        # ===== LEFT SIDE: Camera Feed =====
        self.setup_camera_panel()
        
        # ===== RIGHT SIDE: Control Panel =====
        self.setup_control_panel()
    
    def setup_camera_panel(self):
        """Setup the left side camera feed panel"""
        camera_frame = ctk.CTkFrame(self.root)
        camera_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(
            camera_frame,
            text="📹 CAMERA FEED",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Camera display label
        self.camera_label = ctk.CTkLabel(camera_frame, text="")
        self.camera_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Status bar at bottom
        self.status_bar = ctk.CTkLabel(
            camera_frame,
            text="⚪ System Ready",
            font=ctk.CTkFont(size=12),
            fg_color=("gray80", "gray20"),
            corner_radius=5
        )
        self.status_bar.pack(fill="x", padx=10, pady=(0, 10))
    
    def setup_control_panel(self):
        """Setup the right side control panel"""
        control_frame = ctk.CTkFrame(self.root)
        control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            control_frame,
            text="🎮 CONTROL PANEL",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Create scrollable frame for all controls
        scrollable = ctk.CTkScrollableFrame(control_frame)
        scrollable.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === MAIN CONTROLS ===
        self.setup_main_controls(scrollable)
        
        # === MODE SELECTION ===
        self.setup_mode_selection(scrollable)
        
        # === STATUS DISPLAY ===
        self.setup_status_display(scrollable)
        
        # === VIEW DATA BUTTONS ===
        self.setup_data_view_buttons(scrollable)
        
        # === SETTINGS ===
        self.setup_settings(scrollable)
        
        # === LOG WINDOW ===
        self.setup_log_window(scrollable)
    
    def setup_main_controls(self, parent):
        """Setup main control buttons"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=10)
        
        label = ctk.CTkLabel(frame, text="Main Controls", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=5)
        
        # Start/Stop Video
        self.btn_start_video = ctk.CTkButton(
            frame,
            text="▶️ Start Video Feed",
            command=self.toggle_video,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_start_video.pack(fill="x", padx=10, pady=5)
        
        # Capture Frame
        self.btn_capture = ctk.CTkButton(
            frame,
            text="📸 Capture Frame",
            command=self.capture_frame,
            state="disabled"
        )
        self.btn_capture.pack(fill="x", padx=10, pady=5)
        
        # Select ROI
        self.btn_select_roi = ctk.CTkButton(
            frame,
            text="🎯 Select ROI & Start",
            command=self.start_roi_selection,
            fg_color="blue",
            hover_color="darkblue",
            state="disabled"
        )
        self.btn_select_roi.pack(fill="x", padx=10, pady=5)
        
        # Re-select ROI
        self.btn_reselect = ctk.CTkButton(
            frame,
            text="🔄 Re-select ROI",
            command=self.reselect_roi,
            state="disabled"
        )
        self.btn_reselect.pack(fill="x", padx=10, pady=5)
        
        # Stop Monitoring
        self.btn_stop = ctk.CTkButton(
            frame,
            text="⏹️ Stop Monitoring",
            command=self.stop_monitoring,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.btn_stop.pack(fill="x", padx=10, pady=5)
        
        # Add separator
        separator = ctk.CTkFrame(frame, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=10, pady=10)
        
        # Exit Button
        self.btn_exit = ctk.CTkButton(
            frame,
            text="❌ Exit Application",
            command=self.on_closing,
            fg_color="darkred",
            hover_color="red"
        )
        self.btn_exit.pack(fill="x", padx=10, pady=5)
    
    def setup_mode_selection(self, parent):
        """Setup ROI mode selection"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=10)
        
        label = ctk.CTkLabel(frame, text="ROI Mode", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=5)
        
        # Radio buttons for mode
        self.roi_mode = ctk.StringVar(value="single")
        
        radio1 = ctk.CTkRadioButton(
            frame,
            text="Single Object",
            variable=self.roi_mode,
            value="single"
        )
        radio1.pack(padx=10, pady=2, anchor="w")
        
        radio2 = ctk.CTkRadioButton(
            frame,
            text="Multiple Objects",
            variable=self.roi_mode,
            value="multiple"
        )
        radio2.pack(padx=10, pady=2, anchor="w")
    
    def setup_status_display(self, parent):
        """Setup status information display"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=10)
        
        label = ctk.CTkLabel(frame, text="📊 Status", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=5)
        
        # Status labels
        self.lbl_state = ctk.CTkLabel(frame, text="State: Ready", anchor="w")
        self.lbl_state.pack(fill="x", padx=10, pady=2)
        
        self.lbl_objects = ctk.CTkLabel(frame, text="Objects Tracked: 0", anchor="w")
        self.lbl_objects.pack(fill="x", padx=10, pady=2)
        
        self.lbl_alerts = ctk.CTkLabel(frame, text="Total Alerts: 0", anchor="w")
        self.lbl_alerts.pack(fill="x", padx=10, pady=2)
        
        self.lbl_last_alert = ctk.CTkLabel(frame, text="Last Alert: None", anchor="w")
        self.lbl_last_alert.pack(fill="x", padx=10, pady=2)
    
    def setup_data_view_buttons(self, parent):
        """Setup buttons to view captured data"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=10)
        
        label = ctk.CTkLabel(frame, text="📁 View Data", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=5)
        
        # View Captured Images
        btn_images = ctk.CTkButton(
            frame,
            text="🖼️ Captured Images",
            command=self.view_captured_images,
            fg_color="purple",
            hover_color="darkviolet"
        )
        btn_images.pack(fill="x", padx=10, pady=5)
        
        # View Alert Logs
        btn_alerts = ctk.CTkButton(
            frame,
            text="🚨 Alert Logs",
            command=self.view_alert_logs,
            fg_color="orange",
            hover_color="darkorange"
        )
        btn_alerts.pack(fill="x", padx=10, pady=5)
        
        # View Missing Objects
        btn_missing = ctk.CTkButton(
            frame,
            text="⚠️ Missing Objects",
            command=self.view_missing_objects,
            fg_color="red",
            hover_color="darkred"
        )
        btn_missing.pack(fill="x", padx=10, pady=5)
        
        # Statistics Dashboard Button
        btn_dashboard = ctk.CTkButton(
            frame,
            text="📊 Statistics Dashboard",
            command=self.open_statistics_dashboard,
            fg_color="purple",
            hover_color="darkviolet"
        )
        btn_dashboard.pack(fill="x", padx=10, pady=5)
        
        # Test Email Button
        btn_test_email = ctk.CTkButton(
            frame,
            text="📧 Test Email Alerts",
            command=self.test_email_alerts,
            fg_color="teal",
            hover_color="darkred"
        )
        btn_missing.pack(fill="x", padx=10, pady=5)
    
    def setup_settings(self, parent):
        """Setup settings panel"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=10)
        
        label = ctk.CTkLabel(frame, text="⚙️ Settings", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=5)
        
        # Alert Threshold
        threshold_label = ctk.CTkLabel(frame, text=f"Alert Threshold: {config.ALERT_THRESHOLD} frames")
        threshold_label.pack(padx=10, pady=2)
        
        self.threshold_slider = ctk.CTkSlider(
            frame,
            from_=10,
            to=100,
            number_of_steps=18,
            command=self.update_threshold
        )
        self.threshold_slider.set(config.ALERT_THRESHOLD)
        self.threshold_slider.pack(fill="x", padx=10, pady=5)
        self.threshold_label = threshold_label
        
        # Video Source
        source_label = ctk.CTkLabel(frame, text="Video Source:")
        source_label.pack(padx=10, pady=(10, 2), anchor="w")
        
        self.video_source_entry = ctk.CTkEntry(frame, placeholder_text="0 for webcam")
        self.video_source_entry.insert(0, str(config.VIDEO_SOURCE))
        self.video_source_entry.pack(fill="x", padx=10, pady=2)
        
        # Model Path
        model_label = ctk.CTkLabel(frame, text="Model:")
        model_label.pack(padx=10, pady=(10, 2), anchor="w")
        
        self.model_entry = ctk.CTkEntry(frame)
        self.model_entry.insert(0, config.MODEL_PATH)
        self.model_entry.pack(fill="x", padx=10, pady=2)
    
    def setup_log_window(self, parent):
        """Setup log display window"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=5, pady=10)
        
        label = ctk.CTkLabel(frame, text="📝 Log", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(frame, height=150, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add initial log
        self.add_log("System initialized. Ready to start.")
    
    # ===== FUNCTIONALITY METHODS =====
    
    def initialize_system(self):
        """Initialize the surveillance system"""
        self.add_log("Loading model...")
        if self.engine.load_model():
            self.add_log("✓ Model loaded successfully")
        else:
            self.add_log("✗ Failed to load model")
            messagebox.showerror("Error", "Failed to load YOLO model")
            return
        
        self.add_log("Initializing camera...")
        if self.engine.initialize_camera():
            self.add_log("✓ Camera initialized")
            self.btn_start_video.configure(state="normal")
        else:
            self.add_log("✗ Failed to initialize camera")
            messagebox.showerror("Error", "Failed to open camera")
    
    def toggle_video(self):
        """Start/Stop video feed"""
        if not self.video_running:
            self.start_video()
        else:
            self.stop_video()
    
    def start_video(self):
        """Start video feed"""
        self.video_running = True
        self.btn_start_video.configure(text="⏸️ Stop Video Feed", fg_color="orange", hover_color="darkorange")
        self.btn_capture.configure(state="normal")
        # Don't enable ROI selection until a frame is captured
        # self.btn_select_roi.configure(state="normal")
        self.add_log("Video feed started")
        
        # Start video thread
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
    
    def stop_video(self):
        """Stop video feed"""
        self.video_running = False
        self.btn_start_video.configure(text="▶️ Start Video Feed", fg_color="green", hover_color="darkgreen")
        self.btn_capture.configure(state="disabled")
        if not self.engine.is_monitoring:
            self.btn_select_roi.configure(state="disabled")
        self.add_log("Video feed stopped")
    
    def video_loop(self):
        """Main video processing loop"""
        while self.video_running:
            if self.engine.is_monitoring:
                # Process frame with tracking
                success, frame, any_alert = self.engine.process_frame()
                if success:
                    self.update_camera_display(frame)
                    
                    # Update status bar
                    if any_alert:
                        self.update_status_bar("🚨 ALERT - Object Missing!", "red")
                    else:
                        self.update_status_bar("✅ All Secured - Monitoring", "green")
            else:
                # Just display current frame
                success, frame = self.engine.get_frame()
                if success:
                    self.update_camera_display(frame)
            
            time.sleep(0.03)  # ~30 FPS
    
    def update_camera_display(self, frame):
        """Update the camera display with a frame"""
        if frame is None:
            return
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to fit display (maintain aspect ratio)
        display_width = 900
        display_height = 650
        h, w = frame_rgb.shape[:2]
        scale = min(display_width/w, display_height/h)
        new_w, new_h = int(w*scale), int(h*scale)
        
        frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
        
        # Convert to PhotoImage
        img = Image.fromarray(frame_resized)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update label
        self.camera_label.configure(image=imgtk)
        self.camera_label.image = imgtk
        self.current_display_frame = frame
    
    def capture_frame(self):
        """Capture current frame"""
        frame = self.engine.capture_frame()
        if frame is not None:
            self.add_log(f"Frame captured successfully")
            # Enable ROI selection button after first capture
            self.btn_select_roi.configure(state="normal")
            messagebox.showinfo("Success", "Frame captured and saved!\n\nYou can now select ROI.")
        else:
            self.add_log("Failed to capture frame")
            messagebox.showerror("Error", "Failed to capture frame")
    
    def start_roi_selection(self):
        """Start ROI selection and monitoring"""
        # Check if frame has been captured first
        if self.engine.current_frame is None:
            messagebox.showwarning(
                "No Frame Captured", 
                "Please capture a frame first using 'Capture Frame' button\nbefore selecting ROI."
            )
            self.add_log("⚠️ ROI selection blocked - No frame captured yet")
            return
        
        self.add_log("Starting ROI selection...")
        
        # Show instruction dialog
        mode = self.roi_mode.get()
        if mode == "single":
            messagebox.showinfo(
                "ROI Selection Instructions",
                "📋 How to select ROI:\n\n"
                "1. Click and drag to draw a box around the object\n"
                "2. Press SPACE or ENTER to confirm\n"
                "3. Press ESC to cancel\n\n"
                "The selection window will open now..."
            )
        else:
            messagebox.showinfo(
                "ROI Selection Instructions",
                "📋 How to select multiple ROIs:\n\n"
                "1. Click and drag to draw boxes around each object\n"
                "2. Repeat for all objects you want to track\n"
                "3. Press ENTER when done selecting all ROIs\n"
                "4. Press ESC to cancel\n\n"
                "The selection window will open now..."
            )

        # Pause video temporarily
        was_running = self.video_running
        if was_running:
            self.video_running = False
            time.sleep(0.1)

        frame = self.engine.current_frame.copy()
        
        # Select ROI based on mode
        success = False
        
        try:
            if mode == "single":
                self.add_log("Single ROI mode selected")
                success = self.engine.setup_single_roi(frame)
            else:
                self.add_log("Multiple ROI mode selected")
                success = self.engine.setup_multiple_rois(frame)
            
            if success:
                self.add_log(f"✓ ROI setup complete. Starting monitoring...")
                self.engine.start_monitoring()
                
                # Update button states
                self.btn_select_roi.configure(state="disabled")
                self.btn_reselect.configure(state="normal")
                self.btn_stop.configure(state="normal")
                
                # ALWAYS resume video after ROI selection
                self.video_running = True
                # Start new video thread (old one stopped)
                self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                self.video_thread.start()
                
                self.update_status_bar("🟢 Monitoring Active", "green")
                messagebox.showinfo("Success", "Monitoring started successfully!")
            else:
                self.add_log("✗ ROI setup failed or cancelled")
                # Resume video if it was running before
                if was_running:
                    self.video_running = True
                    self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                    self.video_thread.start()
        except Exception as e:
            self.add_log(f"Error during ROI selection: {e}")
            messagebox.showerror("Error", f"Failed to setup ROI: {e}")
            # Resume video if it was running before
            if was_running:
                self.video_running = True
                self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                self.video_thread.start()
    
    def reselect_roi(self):
        """Re-select ROI on the same captured frame"""
        # Check if we have a reference frame
        if self.engine.reference_frame is None:
            messagebox.showwarning(
                "No Reference Frame",
                "No captured frame available. Please capture a frame first."
            )
            return
        
        self.add_log("Re-selecting ROI on captured frame...")
        
        # Stop current monitoring
        self.engine.stop_monitoring()
        self.engine.reset_tracking()
        
        # Show instruction dialog
        mode = self.roi_mode.get()
        if mode == "single":
            messagebox.showinfo(
                "ROI Re-selection",
                "📋 Re-select ROI on the SAME captured frame:\n\n"
                "1. Draw a box around the object\n"
                "2. Press SPACE/ENTER to confirm\n"
                "3. Press ESC to cancel\n\n"
                "The selection window will open now..."
            )
        else:
            messagebox.showinfo(
                "ROI Re-selection",
                "📋 Re-select ROIs on the SAME captured frame:\n\n"
                "1. Draw boxes around objects\n"
                "2. Press ENTER when done\n"
                "3. Press ESC to cancel\n\n"
                "The selection window will open now..."
            )
        
        # Pause video temporarily
        was_running = self.video_running
        if was_running:
            self.video_running = False
            time.sleep(0.1)
        
        # Use the stored reference frame
        frame = self.engine.reference_frame.copy()
        
        # Select ROI based on mode
        success = False
        
        try:
            if mode == "single":
                self.add_log("Single ROI mode - reselecting")
                success = self.engine.setup_single_roi(frame)
            else:
                self.add_log("Multiple ROI mode - reselecting")
                success = self.engine.setup_multiple_rois(frame)
            
            if success:
                self.add_log(f"✓ ROI re-selected. Restarting monitoring...")
                self.engine.start_monitoring()
                
                # Update button states
                self.btn_reselect.configure(state="normal")
                self.btn_stop.configure(state="normal")
                
                # Resume video
                self.video_running = True
                self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                self.video_thread.start()
                
                self.update_status_bar("🟢 Monitoring Active", "green")
                messagebox.showinfo("Success", "ROI re-selected and monitoring restarted!")
            else:
                self.add_log("✗ ROI re-selection cancelled")
                # Resume video if it was running
                if was_running:
                    self.video_running = True
                    self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                    self.video_thread.start()
        except Exception as e:
            self.add_log(f"Error during ROI re-selection: {e}")
            messagebox.showerror("Error", f"Failed to re-select ROI: {e}")
            # Resume video if it was running
            if was_running:
                self.video_running = True
                self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                self.video_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.add_log("Stopping monitoring...")
        self.engine.stop_monitoring()
        
        self.btn_select_roi.configure(state="normal")
        self.btn_reselect.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        
        self.update_status_bar("⏹️ Monitoring Stopped", "orange")
        self.add_log("Monitoring stopped")
    
    def update_threshold(self, value):
        """Update alert threshold"""
        threshold = int(value)
        self.engine.alert_threshold = threshold
        config.ALERT_THRESHOLD = threshold
        self.threshold_label.configure(text=f"Alert Threshold: {threshold} frames")
        
        # Update existing state managers
        for roi_data in self.engine.roi_targets:
            roi_data['state_manager'].alert_threshold = threshold
    
    def update_status_display(self, status_dict):
        """Update status labels"""
        state_text = "Monitoring" if status_dict['is_monitoring'] else "Ready"
        self.lbl_state.configure(text=f"State: {state_text}")
        self.lbl_objects.configure(text=f"Objects Tracked: {status_dict['num_objects']}")
        self.lbl_alerts.configure(text=f"Total Alerts: {status_dict['total_alerts']}")
    
    def update_status_bar(self, text, color):
        """Update bottom status bar"""
        self.status_bar.configure(text=text, text_color=color)
    
    def on_alert_callback(self, alert_record):
        """Callback when alert is triggered"""
        self.add_log(f"🚨 ALERT! Objects missing: {[obj['name'] for obj in alert_record['missing_objects']]}")
        self.lbl_last_alert.configure(text=f"Last Alert: {alert_record['timestamp']}")
    
    def add_log(self, message):
        """Add message to log window"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_message)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    # ===== DATA VIEW METHODS =====
    
    def view_captured_images(self):
        """Open window to view captured images"""
        images = self.engine.get_captured_frames()
        
        if not images:
            messagebox.showinfo("Info", "No captured images yet!")
            return
        
        # Create new window
        ImageGalleryWindow(self.root, images, "Captured Images")
    
    def view_alert_logs(self):
        """Open window to view alert logs"""
        alerts = self.engine.get_alert_history()
        
        if not alerts:
            messagebox.showinfo("Info", "No alerts yet!")
            return
        
        # Create new window
        AlertLogWindow(self.root, alerts)
    
    def view_missing_objects(self):
        """Open window to view currently missing objects"""
        if not self.engine.is_monitoring:
            messagebox.showinfo("Info", "Not currently monitoring")
            return
        
        status = self.engine.get_status()
        missing = [obj for obj in status['objects'] if obj['state'] == 'ALERT']
        
        if not missing:
            messagebox.showinfo("Info", "No objects currently missing!")
            return
        
        # Create info window
        MissingObjectsWindow(self.root, missing)
    
    def test_email_alerts(self):
        """Test email alert configuration"""
        from utils.email_alerter import get_email_alerter
        
        self.add_log("Testing email configuration...")
        email_alerter = get_email_alerter()
        
        if not email_alerter.enabled:
            messagebox.showerror(
                "Email Not Configured",
                "Email alerts are not configured.\n\n"
                "Please update the .env file with your email credentials.\n\n"
                "Check the terminal for instructions."
            )
            return
        
        # Send test email
        success = email_alerter.test_connection()
        
        if success:
            messagebox.showinfo(
                "Test Successful",
                f"✅ Test email sent successfully!\n\n"
                f"Check your inbox: {email_alerter.sender_email}\n\n"
                f"Email alerts are now active."
            )
            self.add_log("✅ Email test successful")
        else:
            messagebox.showerror(
                "Test Failed",
                "❌ Failed to send test email.\n\n"
                "Check the terminal for error details."
            )
            self.add_log("❌ Email test failed")
    
    def open_statistics_dashboard(self):
        """Open the statistics dashboard window"""
        from gui.dashboard_window import StatisticsDashboard
        from core.statistics_manager import get_statistics_manager
        
        stats_manager = get_statistics_manager()
        dashboard = StatisticsDashboard(self.root, stats_manager)
        self.add_log("📊 Statistics dashboard opened")
    
    def on_closing(self):
        """Handle window close event"""
        self.video_running = False
        time.sleep(0.2)
        self.engine.cleanup()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


# ===== POPUP WINDOWS =====

class ImageGalleryWindow:
    """Window to display captured images"""
    
    def __init__(self, parent, images, title="Image Gallery"):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        
        self.images = images
        self.current_index = 0
        
        # Title
        title_label = ctk.CTkLabel(
            self.window,
            text=f"📸 {title}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Info label
        self.info_label = ctk.CTkLabel(self.window, text="")
        self.info_label.pack(pady=5)
        
        # Image display
        self.image_label = ctk.CTkLabel(self.window, text="")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.window)
        nav_frame.pack(pady=10)
        
        ctk.CTkButton(nav_frame, text="◀ Previous", command=self.prev_image).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="Next ▶", command=self.next_image).pack(side="left", padx=5)
        
        # Show first image
        self.show_image()
    
    def show_image(self):
        """Display current image"""
        if not self.images:
            return
        
        img_data = self.images[self.current_index]
        
        # Update info
        self.info_label.configure(
            text=f"Image {self.current_index + 1} of {len(self.images)} - {img_data['timestamp']}"
        )
        
        # Load and display image
        frame = img_data['frame']
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize
        h, w = frame_rgb.shape[:2]
        scale = min(700/w, 500/h)
        new_w, new_h = int(w*scale), int(h*scale)
        frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
        
        img = Image.fromarray(frame_resized)
        imgtk = ImageTk.PhotoImage(image=img)
        
        self.image_label.configure(image=imgtk)
        self.image_label.image = imgtk
    
    def next_image(self):
        """Show next image"""
        self.current_index = (self.current_index + 1) % len(self.images)
        self.show_image()
    
    def prev_image(self):
        """Show previous image"""
        self.current_index = (self.current_index - 1) % len(self.images)
        self.show_image()


class AlertLogWindow:
    """Window to display alert logs"""
    
    def __init__(self, parent, alerts):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Alert Logs")
        self.window.geometry("700x500")
        
        # Title
        title_label = ctk.CTkLabel(
            self.window,
            text="🚨 Alert Logs",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self.window)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display each alert
        for i, alert in enumerate(reversed(alerts)):  # Most recent first
            alert_frame = ctk.CTkFrame(scrollable)
            alert_frame.pack(fill="x", padx=5, pady=5)
            
            # Alert info
            time_label = ctk.CTkLabel(
                alert_frame,
                text=f"⏰ {alert['timestamp']}",
                font=ctk.CTkFont(weight="bold")
            )
            time_label.pack(anchor="w", padx=10, pady=(5, 2))
            
            # Missing objects
            objects_text = ", ".join([obj['name'] for obj in alert['missing_objects']])
            objects_label = ctk.CTkLabel(
                alert_frame,
                text=f"Missing: {objects_text}",
                text_color="red"
            )
            objects_label.pack(anchor="w", padx=10, pady=2)
            
            # File path
            file_label = ctk.CTkLabel(
                alert_frame,
                text=f"📁 {alert['filename']}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            file_label.pack(anchor="w", padx=10, pady=(2, 5))
            
            # View button
            btn = ctk.CTkButton(
                alert_frame,
                text="View Image",
                width=100,
                command=lambda f=alert['filename']: self.view_alert_image(f)
            )
            btn.pack(anchor="e", padx=10, pady=5)
    
    def view_alert_image(self, filename):
        """Open alert image in new window"""
        if os.path.exists(filename):
            frame = cv2.imread(filename)
            if frame is not None:
                ImageViewWindow(self.window, frame, filename)
        else:
            messagebox.showerror("Error", "Image file not found!")


class ImageViewWindow:
    """Simple window to view a single image"""
    
    def __init__(self, parent, frame, title="Image"):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        
        # Convert and display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        h, w = frame_rgb.shape[:2]
        scale = min(750/w, 550/h)
        new_w, new_h = int(w*scale), int(h*scale)
        frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
        
        img = Image.fromarray(frame_resized)
        imgtk = ImageTk.PhotoImage(image=img)
        
        label = ctk.CTkLabel(self.window, image=imgtk, text="")
        label.image = imgtk
        label.pack(expand=True, padx=10, pady=10)


class MissingObjectsWindow:
    """Window to show currently missing objects"""
    
    def __init__(self, parent, missing_objects):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Missing Objects")
        self.window.geometry("400x300")
        
        # Title
        title_label = ctk.CTkLabel(
            self.window,
            text="⚠️ Currently Missing",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="red"
        )
        title_label.pack(pady=10)
        
        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self.window)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # List missing objects
        for obj in missing_objects:
            obj_frame = ctk.CTkFrame(scrollable)
            obj_frame.pack(fill="x", padx=5, pady=5)
            
            label = ctk.CTkLabel(
                obj_frame,
                text=f"🚫 {obj['name']} (ID: {obj['id']})",
                font=ctk.CTkFont(size=14),
                text_color="orange"
            )
            label.pack(padx=10, pady=10)


# ===== MAIN ENTRY POINT =====

def main():
    """Main entry point"""
    app = SurveillanceGUI()
    app.run()


if __name__ == "__main__":
    main()

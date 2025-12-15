"""
GUI Utilities for Missing Object Surveillance System
Provides professional overlays and visual feedback for each step
"""

import cv2
import numpy as np

class SurveillanceGUI:
    """Professional GUI overlay system for surveillance application"""
    
    # Color scheme (BGR format)
    COLORS = {
        'primary': (245, 158, 11),      # Orange
        'success': (34, 197, 94),        # Green
        'danger': (220, 38, 38),         # Red
        'warning': (251, 191, 36),       # Yellow
        'info': (59, 130, 246),          # Blue
        'dark': (31, 41, 55),            # Dark Gray
        'light': (243, 244, 246),        # Light Gray
        'white': (255, 255, 255),        # White
        'black': (0, 0, 0)               # Black
    }
    
    @staticmethod
    def draw_rounded_rectangle(img, pt1, pt2, color, thickness=2, radius=15):
        """Draw a rounded rectangle"""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Draw the four corners as circles
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)
        
        # Draw the four edges
        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
    
    @staticmethod
    def draw_panel(img, x, y, width, height, color, alpha=0.85, border_color=None, border_thickness=2):
        """Draw a semi-transparent panel"""
        overlay = img.copy()
        
        # Draw filled rectangle
        cv2.rectangle(overlay, (x, y), (x + width, y + height), color, -1)
        
        # Add border if specified
        if border_color:
            cv2.rectangle(overlay, (x, y), (x + width, y + height), border_color, border_thickness)
        
        # Blend with original
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    @staticmethod
    def draw_text_with_background(img, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, 
                                  font_scale=0.7, text_color=(255, 255, 255), 
                                  bg_color=(31, 41, 55), thickness=2, padding=10):
        """Draw text with a background box"""
        x, y = position
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background rectangle
        cv2.rectangle(img, 
                     (x - padding, y - text_height - padding),
                     (x + text_width + padding, y + baseline + padding),
                     bg_color, -1)
        
        # Draw text
        cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
        
        return text_height + baseline + 2 * padding
    
    @staticmethod
    def draw_header(img, title, subtitle=None):
        """Draw a professional header at the top of the frame"""
        height, width = img.shape[:2]
        
        # Draw header background
        SurveillanceGUI.draw_panel(img, 0, 0, width, 120, SurveillanceGUI.COLORS['dark'], alpha=0.9)
        
        # Draw title
        title_y = 50
        cv2.putText(img, title, (30, title_y), 
                   cv2.FONT_HERSHEY_BOLD, 1.2, SurveillanceGUI.COLORS['primary'], 3, cv2.LINE_AA)
        
        # Draw subtitle if provided
        if subtitle:
            cv2.putText(img, subtitle, (30, title_y + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, SurveillanceGUI.COLORS['light'], 2, cv2.LINE_AA)
    
    @staticmethod
    def draw_footer_controls(img, controls):
        """
        Draw control hints at the bottom
        controls: list of tuples (key, description, color)
        """
        height, width = img.shape[:2]
        footer_height = 80
        
        # Draw footer background
        SurveillanceGUI.draw_panel(img, 0, height - footer_height, width, footer_height, 
                                   SurveillanceGUI.COLORS['dark'], alpha=0.9)
        
        # Calculate spacing
        x_offset = 30
        y_pos = height - 40
        
        for key, description, color_name in controls:
            # Draw key button
            key_bg_color = SurveillanceGUI.COLORS.get(color_name, SurveillanceGUI.COLORS['info'])
            
            # Key background
            key_width = 45
            key_height = 35
            cv2.rectangle(img, (x_offset, y_pos - 25), (x_offset + key_width, y_pos + 10), 
                         key_bg_color, -1)
            cv2.rectangle(img, (x_offset, y_pos - 25), (x_offset + key_width, y_pos + 10), 
                         SurveillanceGUI.COLORS['white'], 2)
            
            # Key text
            key_text = key.upper()
            (kw, kh), _ = cv2.getTextSize(key_text, cv2.FONT_HERSHEY_BOLD, 0.6, 2)
            cv2.putText(img, key_text, 
                       (x_offset + (key_width - kw) // 2, y_pos - 5),
                       cv2.FONT_HERSHEY_BOLD, 0.6, SurveillanceGUI.COLORS['white'], 2, cv2.LINE_AA)
            
            # Description text
            cv2.putText(img, description, (x_offset + key_width + 15, y_pos - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, SurveillanceGUI.COLORS['light'], 1, cv2.LINE_AA)
            
            # Calculate next position
            desc_width = cv2.getTextSize(description, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0][0]
            x_offset += key_width + desc_width + 50
            
            # Wrap to next line if needed
            if x_offset > width - 200:
                x_offset = 30
                y_pos -= 35
    
    @staticmethod
    def draw_instruction_box(img, instructions, position='center'):
        """Draw an instruction box with multiple lines"""
        height, width = img.shape[:2]
        
        # Calculate box dimensions
        box_width = min(700, width - 100)
        line_height = 40
        box_height = len(instructions) * line_height + 60
        
        # Calculate position
        if position == 'center':
            x = (width - box_width) // 2
            y = (height - box_height) // 2
        elif position == 'top':
            x = (width - box_width) // 2
            y = 150
        else:
            x, y = position
        
        # Draw main panel
        SurveillanceGUI.draw_panel(img, x, y, box_width, box_height, 
                                   SurveillanceGUI.COLORS['dark'], alpha=0.92,
                                   border_color=SurveillanceGUI.COLORS['primary'], 
                                   border_thickness=3)
        
        # Draw instructions
        text_y = y + 40
        for instruction in instructions:
            # Draw bullet point
            cv2.circle(img, (x + 20, text_y - 5), 5, SurveillanceGUI.COLORS['primary'], -1)
            
            # Draw instruction text
            cv2.putText(img, instruction, (x + 40, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.65, SurveillanceGUI.COLORS['white'], 
                       2, cv2.LINE_AA)
            text_y += line_height
    
    @staticmethod
    def draw_live_preview_gui(frame):
        """Draw GUI for live preview mode"""
        display_frame = frame.copy()
        
        # Draw header
        SurveillanceGUI.draw_header(display_frame, 
                                    "LIVE PREVIEW MODE",
                                    "Position your camera and objects")
        
        # Draw center crosshair for alignment
        height, width = display_frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Crosshair lines
        cv2.line(display_frame, (center_x - 40, center_y), (center_x + 40, center_y), 
                SurveillanceGUI.COLORS['primary'], 2)
        cv2.line(display_frame, (center_x, center_y - 40), (center_x, center_y + 40), 
                SurveillanceGUI.COLORS['primary'], 2)
        cv2.circle(display_frame, (center_x, center_y), 5, SurveillanceGUI.COLORS['primary'], -1)
        
        # Draw instruction box
        instructions = [
            "Adjust camera position for best view",
            "Ensure good lighting on objects",
            "Keep objects clearly visible",
            "Press 'C' when ready to capture frame"
        ]
        SurveillanceGUI.draw_instruction_box(display_frame, instructions, position='top')
        
        # Draw footer controls
        controls = [
            ('c', 'Capture Frame', 'success'),
            ('r', 'Refresh', 'info'),
            ('q', 'Quit', 'danger')
        ]
        SurveillanceGUI.draw_footer_controls(display_frame, controls)
        
        return display_frame
    
    @staticmethod
    def draw_mode_selection_gui(frame):
        """Draw GUI for mode selection"""
        display_frame = frame.copy()
        height, width = display_frame.shape[:2]
        
        # Draw header
        SurveillanceGUI.draw_header(display_frame, 
                                    "SELECT MONITORING MODE",
                                    "Choose how many objects to monitor")
        
        # Draw two option panels
        panel_width = 350
        panel_height = 200
        gap = 50
        total_width = panel_width * 2 + gap
        start_x = (width - total_width) // 2
        y = (height - panel_height) // 2
        
        # Single ROI Panel
        single_x = start_x
        SurveillanceGUI.draw_panel(display_frame, single_x, y, panel_width, panel_height,
                                   SurveillanceGUI.COLORS['dark'], alpha=0.9,
                                   border_color=SurveillanceGUI.COLORS['success'], 
                                   border_thickness=3)
        
        # Single ROI content
        icon_y = y + 60
        cv2.circle(display_frame, (single_x + panel_width // 2, icon_y), 30, 
                  SurveillanceGUI.COLORS['success'], 3)
        cv2.putText(display_frame, "1", (single_x + panel_width // 2 - 10, icon_y + 15),
                   cv2.FONT_HERSHEY_BOLD, 1.5, SurveillanceGUI.COLORS['success'], 3)
        
        cv2.putText(display_frame, "SINGLE OBJECT", 
                   (single_x + 70, y + 130),
                   cv2.FONT_HERSHEY_BOLD, 0.8, SurveillanceGUI.COLORS['white'], 2, cv2.LINE_AA)
        cv2.putText(display_frame, "Monitor one object", 
                   (single_x + 75, y + 160),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, SurveillanceGUI.COLORS['light'], 1, cv2.LINE_AA)
        
        # Key hint
        cv2.rectangle(display_frame, (single_x + 140, y + panel_height - 40),
                     (single_x + 210, y + panel_height - 10),
                     SurveillanceGUI.COLORS['success'], -1)
        cv2.putText(display_frame, "Press 'S'", (single_x + 150, y + panel_height - 18),
                   cv2.FONT_HERSHEY_BOLD, 0.6, SurveillanceGUI.COLORS['white'], 2)
        
        # Multiple ROI Panel
        multi_x = start_x + panel_width + gap
        SurveillanceGUI.draw_panel(display_frame, multi_x, y, panel_width, panel_height,
                                   SurveillanceGUI.COLORS['dark'], alpha=0.9,
                                   border_color=SurveillanceGUI.COLORS['info'], 
                                   border_thickness=3)
        
        # Multiple ROI content
        spacing = 25
        for i in range(3):
            x_pos = multi_x + panel_width // 2 - spacing + i * spacing
            cv2.circle(display_frame, (x_pos, icon_y), 12, SurveillanceGUI.COLORS['info'], 2)
        
        cv2.putText(display_frame, "MULTIPLE OBJECTS", 
                   (multi_x + 50, y + 130),
                   cv2.FONT_HERSHEY_BOLD, 0.8, SurveillanceGUI.COLORS['white'], 2, cv2.LINE_AA)
        cv2.putText(display_frame, "Monitor 2+ objects", 
                   (multi_x + 75, y + 160),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, SurveillanceGUI.COLORS['light'], 1, cv2.LINE_AA)
        
        # Key hint
        cv2.rectangle(display_frame, (multi_x + 140, y + panel_height - 40),
                     (multi_x + 210, y + panel_height - 10),
                     SurveillanceGUI.COLORS['info'], -1)
        cv2.putText(display_frame, "Press 'M'", (multi_x + 148, y + panel_height - 18),
                   cv2.FONT_HERSHEY_BOLD, 0.6, SurveillanceGUI.COLORS['white'], 2)
        
        return display_frame
    
    @staticmethod
    def draw_roi_selection_gui(frame, roi_count=1, is_multiple=False):
        """Draw GUI for ROI selection"""
        display_frame = frame.copy()
        
        # Draw header
        if is_multiple:
            title = f"DRAW ROI #{roi_count}"
            subtitle = "Draw a box around the object to monitor"
        else:
            title = "DRAW ROI"
            subtitle = "Draw a box around your object"
        
        SurveillanceGUI.draw_header(display_frame, title, subtitle)
        
        # Draw instruction box
        instructions = [
            "Click and drag to draw a box around object",
            "Make the box tight around the object",
            "Press ENTER or SPACE to confirm selection",
            "Press 'C' to cancel and redraw"
        ]
        
        if is_multiple:
            instructions.append("Press 'A' to add another object after this")
        
        SurveillanceGUI.draw_instruction_box(display_frame, instructions, position='top')
        
        # Draw footer controls
        if is_multiple:
            controls = [
                ('enter', 'Confirm', 'success'),
                ('c', 'Cancel', 'warning'),
                ('a', 'Add More', 'info')
            ]
        else:
            controls = [
                ('enter', 'Confirm', 'success'),
                ('c', 'Cancel', 'warning')
            ]
        SurveillanceGUI.draw_footer_controls(display_frame, controls)
        
        return display_frame
    
    @staticmethod
    def draw_tracking_status(frame, roi_targets, any_alert=False):
        """Draw tracking status overlay during monitoring"""
        display_frame = frame.copy()
        height, width = display_frame.shape[:2]
        
        # Draw compact status panel at top
        panel_height = 90
        SurveillanceGUI.draw_panel(display_frame, 0, 0, width, panel_height,
                                   SurveillanceGUI.COLORS['dark'], alpha=0.85)
        
        # Main status
        if any_alert:
            status_text = "⚠ ALERT - Object(s) Missing!"
            status_color = SurveillanceGUI.COLORS['danger']
        else:
            status_text = "✓ All Secured"
            status_color = SurveillanceGUI.COLORS['success']
        
        cv2.putText(display_frame, status_text, (30, 40),
                   cv2.FONT_HERSHEY_BOLD, 1.0, status_color, 2, cv2.LINE_AA)
        
        # Mode indicator
        cv2.putText(display_frame, "METHOD 2: Tracker Mode", (30, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, SurveillanceGUI.COLORS['light'], 1, cv2.LINE_AA)
        
        # Object count
        count_text = f"Tracking: {len(roi_targets)} object(s)"
        text_width = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0][0]
        cv2.putText(display_frame, count_text, (width - text_width - 30, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, SurveillanceGUI.COLORS['primary'], 2, cv2.LINE_AA)
        
        # Draw footer controls
        controls = [
            ('r', 'Re-select ROI', 'warning'),
            ('q', 'Quit', 'danger')
        ]
        SurveillanceGUI.draw_footer_controls(display_frame, controls)
        
        return display_frame
    
    @staticmethod
    def draw_initialization_message(frame, message):
        """Draw initialization/loading message"""
        display_frame = frame.copy()
        height, width = display_frame.shape[:2]
        
        # Draw semi-transparent overlay
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), SurveillanceGUI.COLORS['dark'], -1)
        cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
        
        # Draw message box
        box_width = 500
        box_height = 150
        x = (width - box_width) // 2
        y = (height - box_height) // 2
        
        cv2.rectangle(display_frame, (x, y), (x + box_width, y + box_height),
                     SurveillanceGUI.COLORS['primary'], 3)
        
        # Animated dots
        import time
        dots = "." * (int(time.time() * 2) % 4)
        
        # Draw message
        cv2.putText(display_frame, message + dots, (x + 50, y + 70),
                   cv2.FONT_HERSHEY_BOLD, 0.9, SurveillanceGUI.COLORS['white'], 2, cv2.LINE_AA)
        
        cv2.putText(display_frame, "Please wait...", (x + 180, y + 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, SurveillanceGUI.COLORS['light'], 1, cv2.LINE_AA)
        
        return display_frame

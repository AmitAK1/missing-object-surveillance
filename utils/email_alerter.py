"""
Email Alerter - Send email notifications for missing object alerts
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv
import config

# Load environment variables
load_dotenv()


class EmailAlerter:
    """Handle email notifications for surveillance alerts"""
    
    def __init__(self):
        """Initialize email alerter with credentials from .env file"""
        self.enabled = config.EMAIL_ALERTS_ENABLED
        self.cooldown_seconds = config.EMAIL_ALERT_COOLDOWN
        self.include_image = config.EMAIL_INCLUDE_IMAGE
        
        # Load credentials from environment
        self.sender_email = os.getenv('EMAIL_SENDER', '')
        self.sender_password = os.getenv('EMAIL_PASSWORD', '')
        self.recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Clean recipient emails
        self.recipients = [email.strip() for email in self.recipients if email.strip()]
        
        # Track last email sent time for cooldown
        self.last_email_time = {}
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> bool:
        """Validate email configuration"""
        if not self.enabled:
            print("ℹ️ Email alerts are disabled in config.py")
            return False
        
        if not self.sender_email or 'your-email' in self.sender_email:
            print("⚠️ EMAIL_SENDER not configured in .env file")
            self.enabled = False
            return False
        
        if not self.sender_password or 'your-app-password' in self.sender_password:
            print("⚠️ EMAIL_PASSWORD not configured in .env file")
            print("📧 To setup Gmail App Password:")
            print("   1. Go to https://myaccount.google.com/apppasswords")
            print("   2. Enable 2-Step Verification")
            print("   3. Create App Password for 'Mail'")
            print("   4. Update EMAIL_PASSWORD in .env file")
            self.enabled = False
            return False
        
        if not self.recipients:
            print("⚠️ EMAIL_RECIPIENTS not configured in .env file")
            self.enabled = False
            return False
        
        print(f"✅ Email alerts configured successfully")
        print(f"   Sender: {self.sender_email}")
        print(f"   Recipients: {', '.join(self.recipients)}")
        print(f"   Cooldown: {self.cooldown_seconds} seconds")
        return True
    
    def _check_cooldown(self, object_id: int) -> bool:
        """Check if cooldown period has passed for this object"""
        if object_id not in self.last_email_time:
            return True
        
        elapsed = (datetime.now() - self.last_email_time[object_id]).total_seconds()
        return elapsed >= self.cooldown_seconds
    
    def _create_email_body(self, object_name: str, object_id: int, 
                          timestamp: str, roi_index: int = None) -> str:
        """Create HTML email body"""
        roi_info = f" (ROI #{roi_index})" if roi_index is not None else ""
        
        html = f"""
        <html>
          <head>
            <style>
              body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
              }}
              .header {{
                background-color: #dc3545;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
              }}
              .content {{
                padding: 20px;
                background-color: #f8f9fa;
                margin: 20px 0;
                border-radius: 5px;
              }}
              .alert-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 15px 0;
              }}
              .details {{
                margin: 15px 0;
              }}
              .details-table {{
                width: 100%;
                border-collapse: collapse;
              }}
              .details-table td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
              }}
              .details-table td:first-child {{
                font-weight: bold;
                width: 150px;
              }}
              .footer {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 20px;
              }}
            </style>
          </head>
          <body>
            <div class="header">
              <h1>🚨 Missing Object Alert</h1>
            </div>
            
            <div class="content">
              <div class="alert-box">
                <h2>⚠️ Object Has Gone Missing!</h2>
                <p>The surveillance system has detected that a tracked object is no longer in its designated area.</p>
              </div>
              
              <div class="details">
                <h3>Alert Details:</h3>
                <table class="details-table">
                  <tr>
                    <td>Object:</td>
                    <td><strong>{object_name}</strong></td>
                  </tr>
                  <tr>
                    <td>Tracking ID:</td>
                    <td>{object_id}</td>
                  </tr>
                  <tr>
                    <td>Location:</td>
                    <td>Region of Interest{roi_info}</td>
                  </tr>
                  <tr>
                    <td>Alert Time:</td>
                    <td>{timestamp}</td>
                  </tr>
                  <tr>
                    <td>Status:</td>
                    <td><span style="color: #dc3545; font-weight: bold;">MISSING</span></td>
                  </tr>
                </table>
              </div>
              
              <div class="alert-box">
                <p><strong>📸 Snapshot:</strong> A snapshot from the time the object went missing is attached to this email.</p>
              </div>
            </div>
            
            <div class="footer">
              <p>This is an automated alert from Missing Object Surveillance System</p>
              <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
          </body>
        </html>
        """
        return html
    
    def send_alert(self, object_name: str, object_id: int, 
                   image_path: Optional[str] = None, 
                   roi_index: int = None) -> bool:
        """
        Send email alert for missing object
        
        Args:
            object_name: Name of the missing object (e.g., "person", "bag")
            object_id: Tracking ID of the object
            image_path: Path to alert snapshot image (optional)
            roi_index: Index of the ROI where object went missing (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        # Check cooldown
        if not self._check_cooldown(object_id):
            remaining = self.cooldown_seconds - (datetime.now() - self.last_email_time[object_id]).total_seconds()
            print(f"⏳ Email cooldown active. Next email in {int(remaining)} seconds")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            roi_text = f" (ROI #{roi_index})" if roi_index is not None else ""
            msg['Subject'] = f"🚨 ALERT: {object_name.upper()} Missing{roi_text} - {timestamp}"
            
            # Create HTML body
            html_body = self._create_email_body(object_name, object_id, timestamp, roi_index)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach image if provided and enabled
            if self.include_image and image_path and os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        image = MIMEImage(img_data, name=os.path.basename(image_path))
                        image.add_header('Content-Disposition', 'attachment', 
                                       filename=os.path.basename(image_path))
                        msg.attach(image)
                    print(f"📎 Image attached: {os.path.basename(image_path)}")
                except Exception as e:
                    print(f"⚠️ Failed to attach image: {e}")
            
            # Send email
            print(f"📧 Sending email alert to {len(self.recipients)} recipient(s)...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure connection
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            # Update last email time
            self.last_email_time[object_id] = datetime.now()
            
            print(f"✅ Email alert sent successfully!")
            print(f"   Object: {object_name} (ID: {object_id})")
            print(f"   Recipients: {', '.join(self.recipients)}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Email authentication failed!")
            print("   Check your EMAIL_PASSWORD in .env file")
            print("   Make sure you're using an App Password (not your regular Gmail password)")
            self.enabled = False  # Disable further attempts
            return False
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test email configuration by sending a test email"""
        if not self.enabled:
            print("❌ Email alerts are disabled")
            return False
        
        try:
            print("🧪 Testing email configuration...")
            
            # Create test message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = "✅ Test Email - Surveillance System"
            
            body = """
            <html>
              <body>
                <h2>✅ Email Configuration Test Successful!</h2>
                <p>Your Missing Object Surveillance System is now configured to send email alerts.</p>
                <p><strong>Configuration:</strong></p>
                <ul>
                  <li>Sender: """ + self.sender_email + """</li>
                  <li>Recipients: """ + ', '.join(self.recipients) + """</li>
                  <li>Cooldown: """ + str(self.cooldown_seconds) + """ seconds</li>
                </ul>
                <p>You will receive alerts when tracked objects go missing.</p>
              </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            # Send test email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print("✅ Test email sent successfully!")
            print(f"   Check inbox: {', '.join(self.recipients)}")
            return True
            
        except Exception as e:
            print(f"❌ Test email failed: {e}")
            return False


# Singleton instance
_email_alerter = None

def get_email_alerter() -> EmailAlerter:
    """Get singleton EmailAlerter instance"""
    global _email_alerter
    if _email_alerter is None:
        _email_alerter = EmailAlerter()
    return _email_alerter

"""
Statistics Manager - Track and analyze surveillance system performance
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict


class StatisticsManager:
    """Manage and analyze surveillance statistics"""
    
    def __init__(self):
        """Initialize statistics manager"""
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Alert tracking
        self.alerts = []
        self.total_alerts = 0
        
        # Performance tracking
        self.fps_history = []
        self.max_fps_samples = 1000  # Keep last 1000 samples
        
        # Object tracking
        self.objects_tracked_history = []
        self.detection_confidence_history = []
        
        # Email tracking
        self.emails_sent = 0
        self.email_failures = 0
        
        print(f"📊 Statistics Manager initialized (Session: {self.session_id})")
    
    def record_alert(self, object_name: str, object_id: int, 
                    roi_index: int = None, confidence: float = None,
                    duration_missing: int = None):
        """Record an alert event"""
        alert_record = {
            'timestamp': datetime.now(),
            'object_name': object_name,
            'object_id': object_id,
            'roi_index': roi_index,
            'confidence': confidence,
            'duration_missing': duration_missing,
            'session_id': self.session_id
        }
        
        self.alerts.append(alert_record)
        self.total_alerts += 1
        
        print(f"📊 Alert recorded: {object_name} (Total: {self.total_alerts})")
    
    def record_fps(self, fps: float):
        """Record FPS measurement"""
        self.fps_history.append({
            'timestamp': datetime.now(),
            'fps': fps
        })
        
        # Keep only recent samples
        if len(self.fps_history) > self.max_fps_samples:
            self.fps_history.pop(0)
    
    def record_objects_tracked(self, count: int):
        """Record number of objects currently tracked"""
        self.objects_tracked_history.append({
            'timestamp': datetime.now(),
            'count': count
        })
        
        # Keep only last hour
        cutoff = datetime.now() - timedelta(hours=1)
        self.objects_tracked_history = [
            x for x in self.objects_tracked_history 
            if x['timestamp'] > cutoff
        ]
    
    def record_detection_confidence(self, confidence: float):
        """Record detection confidence score"""
        self.detection_confidence_history.append(confidence)
        
        # Keep only last 500 detections
        if len(self.detection_confidence_history) > 500:
            self.detection_confidence_history.pop(0)
    
    def record_email_sent(self, success: bool = True):
        """Record email send attempt"""
        if success:
            self.emails_sent += 1
        else:
            self.email_failures += 1
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        now = datetime.now()
        uptime = now - self.start_time
        
        # Calculate alerts today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        alerts_today = len([a for a in self.alerts if a['timestamp'] >= today_start])
        
        # Calculate average FPS
        avg_fps = 0.0
        if self.fps_history:
            avg_fps = sum(x['fps'] for x in self.fps_history) / len(self.fps_history)
        
        # Get most common object
        if self.alerts:
            object_counts = defaultdict(int)
            for alert in self.alerts:
                object_counts[alert['object_name']] += 1
            most_common_object = max(object_counts.items(), key=lambda x: x[1])[0]
            most_common_count = object_counts[most_common_object]
        else:
            most_common_object = "None"
            most_common_count = 0
        
        # Current objects tracked
        current_objects = 0
        if self.objects_tracked_history:
            current_objects = self.objects_tracked_history[-1]['count']
        
        return {
            'total_alerts': self.total_alerts,
            'alerts_today': alerts_today,
            'uptime': str(uptime).split('.')[0],  # Remove microseconds
            'uptime_seconds': uptime.total_seconds(),
            'avg_fps': round(avg_fps, 1),
            'current_fps': round(self.fps_history[-1]['fps'], 1) if self.fps_history else 0,
            'most_common_object': most_common_object,
            'most_common_count': most_common_count,
            'current_objects_tracked': current_objects,
            'emails_sent': self.emails_sent,
            'email_failures': self.email_failures,
            'session_start': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_alerts_dataframe(self) -> pd.DataFrame:
        """Get alerts as pandas DataFrame"""
        if not self.alerts:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.alerts)
        return df
    
    def get_alerts_by_hour(self) -> Dict[int, int]:
        """Get alert count by hour of day"""
        hourly_counts = defaultdict(int)
        
        for alert in self.alerts:
            hour = alert['timestamp'].hour
            hourly_counts[hour] += 1
        
        # Fill in missing hours with 0
        for hour in range(24):
            if hour not in hourly_counts:
                hourly_counts[hour] = 0
        
        return dict(sorted(hourly_counts.items()))
    
    def get_alerts_by_object(self) -> Dict[str, int]:
        """Get alert count by object type"""
        object_counts = defaultdict(int)
        
        for alert in self.alerts:
            object_counts[alert['object_name']] += 1
        
        return dict(object_counts)
    
    def get_alerts_over_time(self, hours: int = 24) -> List[Dict]:
        """Get alerts over time (grouped by time intervals)"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alerts if a['timestamp'] >= cutoff]
        
        # Group by 30-minute intervals
        interval_minutes = 30
        time_groups = defaultdict(int)
        
        for alert in recent_alerts:
            # Round timestamp to nearest interval
            minutes = (alert['timestamp'].minute // interval_minutes) * interval_minutes
            time_key = alert['timestamp'].replace(minute=minutes, second=0, microsecond=0)
            time_groups[time_key] += 1
        
        # Convert to list of dicts
        result = [
            {'time': time_key, 'count': count}
            for time_key, count in sorted(time_groups.items())
        ]
        
        return result
    
    def get_fps_stats(self) -> Dict:
        """Get FPS statistics"""
        if not self.fps_history:
            return {
                'current': 0,
                'average': 0,
                'min': 0,
                'max': 0,
                'history': []
            }
        
        fps_values = [x['fps'] for x in self.fps_history]
        
        return {
            'current': round(fps_values[-1], 1),
            'average': round(sum(fps_values) / len(fps_values), 1),
            'min': round(min(fps_values), 1),
            'max': round(max(fps_values), 1),
            'history': self.fps_history[-100:]  # Last 100 samples for plotting
        }
    
    def get_confidence_stats(self) -> Dict:
        """Get detection confidence statistics"""
        if not self.detection_confidence_history:
            return {
                'average': 0,
                'min': 0,
                'max': 0,
                'distribution': []
            }
        
        return {
            'average': round(sum(self.detection_confidence_history) / len(self.detection_confidence_history) * 100, 1),
            'min': round(min(self.detection_confidence_history) * 100, 1),
            'max': round(max(self.detection_confidence_history) * 100, 1),
            'distribution': self.detection_confidence_history
        }
    
    def get_peak_alert_time(self) -> str:
        """Get the hour with most alerts"""
        if not self.alerts:
            return "No data"
        
        hourly = self.get_alerts_by_hour()
        peak_hour = max(hourly.items(), key=lambda x: x[1])[0]
        
        return f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00"
    
    def reset_stats(self):
        """Reset all statistics"""
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.alerts = []
        self.total_alerts = 0
        self.fps_history = []
        self.objects_tracked_history = []
        self.detection_confidence_history = []
        self.emails_sent = 0
        self.email_failures = 0
        
        print(f"📊 Statistics reset (New Session: {self.session_id})")
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export alerts to CSV file"""
        if not self.alerts:
            return None
        
        if filename is None:
            filename = f"statistics_{self.session_id}.csv"
        
        df = self.get_alerts_dataframe()
        df.to_csv(filename, index=False)
        
        print(f"📊 Statistics exported to: {filename}")
        return filename


# Singleton instance
_stats_manager = None

def get_statistics_manager() -> StatisticsManager:
    """Get singleton StatisticsManager instance"""
    global _stats_manager
    if _stats_manager is None:
        _stats_manager = StatisticsManager()
    return _stats_manager

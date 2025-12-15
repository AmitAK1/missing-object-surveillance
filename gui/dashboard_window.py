"""
Statistics Dashboard Window - Visual analytics for surveillance system
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Optional


class StatisticsDashboard:
    """Dashboard window showing surveillance statistics and charts"""
    
    def __init__(self, parent, stats_manager):
        """Initialize dashboard window"""
        self.stats_manager = stats_manager
        
        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("📊 Statistics Dashboard")
        self.window.geometry("1200x800")
        
        # Configure matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Build UI
        self.setup_ui()
        
        # Initial data load
        self.refresh_dashboard()
    
    def setup_ui(self):
        """Setup the dashboard UI"""
        # Main container
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Header
        self.setup_header()
        
        # Summary Cards
        self.setup_summary_cards()
        
        # Charts Container (Scrollable)
        self.setup_charts_container()
        
        # Footer with controls
        self.setup_footer()
    
    def setup_header(self):
        """Setup header section"""
        header = ctk.CTkFrame(self.window, fg_color=("gray80", "gray20"))
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        title = ctk.CTkLabel(
            header,
            text="📊 Surveillance Statistics Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=15)
    
    def setup_summary_cards(self):
        """Setup summary statistics cards"""
        cards_frame = ctk.CTkFrame(self.window)
        cards_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Get summary stats
        stats = self.stats_manager.get_summary_stats()
        
        # Card 1: Total Alerts
        self.card_total_alerts = self.create_summary_card(
            cards_frame, "🚨 Total Alerts", 
            str(stats['total_alerts']), "red", 0
        )
        
        # Card 2: Today's Alerts
        self.card_today_alerts = self.create_summary_card(
            cards_frame, "📅 Today's Alerts", 
            str(stats['alerts_today']), "orange", 1
        )
        
        # Card 3: Objects Tracked
        self.card_objects = self.create_summary_card(
            cards_frame, "🎯 Objects Tracked", 
            str(stats['current_objects_tracked']), "blue", 2
        )
        
        # Card 4: System Uptime
        self.card_uptime = self.create_summary_card(
            cards_frame, "⏱️ System Uptime", 
            stats['uptime'], "green", 3
        )
    
    def create_summary_card(self, parent, title, value, color, column):
        """Create a summary statistics card"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(0, 10))
        
        return value_label
    
    def setup_charts_container(self):
        """Setup scrollable container for charts"""
        # Scrollable frame
        self.charts_frame = ctk.CTkScrollableFrame(self.window, height=500)
        self.charts_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.window.grid_rowconfigure(2, weight=1)
        
        # Configure grid
        self.charts_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Create chart placeholders
        self.chart_alerts_time = None
        self.chart_alerts_object = None
        self.chart_peak_hours = None
        self.chart_confidence = None
        self.chart_fps = None
        self.chart_additional_stats = None
    
    def setup_footer(self):
        """Setup footer with control buttons"""
        footer = ctk.CTkFrame(self.window)
        footer.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        # Refresh Button
        btn_refresh = ctk.CTkButton(
            footer,
            text="🔄 Refresh",
            command=self.refresh_dashboard,
            fg_color="green",
            hover_color="darkgreen",
            width=120
        )
        btn_refresh.pack(side="left", padx=5)
        
        # Export Button
        btn_export = ctk.CTkButton(
            footer,
            text="💾 Export CSV",
            command=self.export_data,
            fg_color="blue",
            hover_color="darkblue",
            width=120
        )
        btn_export.pack(side="left", padx=5)
        
        # Reset Button
        btn_reset = ctk.CTkButton(
            footer,
            text="🔄 Reset Stats",
            command=self.reset_stats,
            fg_color="orange",
            hover_color="darkorange",
            width=120
        )
        btn_reset.pack(side="left", padx=5)
        
        # Last Updated Label
        self.lbl_updated = ctk.CTkLabel(
            footer,
            text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_updated.pack(side="right", padx=10)
        
        # Close Button
        btn_close = ctk.CTkButton(
            footer,
            text="❌ Close",
            command=self.window.destroy,
            fg_color="red",
            hover_color="darkred",
            width=120
        )
        btn_close.pack(side="right", padx=5)
    
    def refresh_dashboard(self):
        """Refresh all dashboard data and charts"""
        # Update summary cards
        self.update_summary_cards()
        
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Create new charts
        self.create_alerts_over_time_chart()
        self.create_alerts_by_object_chart()
        self.create_peak_hours_chart()
        self.create_confidence_chart()
        self.create_fps_chart()
        self.create_additional_stats_panel()
        
        # Update timestamp
        self.lbl_updated.configure(
            text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        print("📊 Dashboard refreshed")
    
    def update_summary_cards(self):
        """Update summary card values"""
        stats = self.stats_manager.get_summary_stats()
        
        self.card_total_alerts.configure(text=str(stats['total_alerts']))
        self.card_today_alerts.configure(text=str(stats['alerts_today']))
        self.card_objects.configure(text=str(stats['current_objects_tracked']))
        self.card_uptime.configure(text=stats['uptime'])
    
    def create_alerts_over_time_chart(self):
        """Create alerts over time line chart"""
        frame = ctk.CTkFrame(self.charts_frame)
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="📈 Alerts Over Time (Last 24 Hours)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=5)
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get data
        alerts_data = self.stats_manager.get_alerts_over_time(hours=24)
        
        if alerts_data:
            times = [d['time'] for d in alerts_data]
            counts = [d['count'] for d in alerts_data]
            
            ax.plot(times, counts, marker='o', color='#FF5733', linewidth=2)
            ax.fill_between(times, counts, alpha=0.3, color='#FF5733')
            ax.set_xlabel('Time')
            ax.set_ylabel('Alert Count')
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=12)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_alerts_by_object_chart(self):
        """Create alerts by object type pie chart"""
        frame = ctk.CTkFrame(self.charts_frame)
        frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="🥧 Alerts by Object Type",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=5)
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get data
        object_counts = self.stats_manager.get_alerts_by_object()
        
        if object_counts:
            labels = list(object_counts.keys())
            sizes = list(object_counts.values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=12)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_peak_hours_chart(self):
        """Create peak alert hours bar chart"""
        frame = ctk.CTkFrame(self.charts_frame)
        frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="📊 Peak Alert Hours",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=5)
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get data
        hourly_data = self.stats_manager.get_alerts_by_hour()
        
        if hourly_data:
            hours = list(hourly_data.keys())
            counts = list(hourly_data.values())
            
            bars = ax.bar(hours, counts, color='#4ECDC4', alpha=0.7)
            
            # Highlight peak hour
            max_count = max(counts)
            for bar, count in zip(bars, counts):
                if count == max_count:
                    bar.set_color('#FF6B6B')
            
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Alert Count')
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=0.3, axis='y')
        else:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=12)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_confidence_chart(self):
        """Create detection confidence histogram"""
        frame = ctk.CTkFrame(self.charts_frame)
        frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="📊 Detection Confidence Distribution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=5)
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get data
        conf_stats = self.stats_manager.get_confidence_stats()
        
        if conf_stats['distribution']:
            # Convert to percentage
            confidences = [c * 100 for c in conf_stats['distribution']]
            
            ax.hist(confidences, bins=20, color='#45B7D1', alpha=0.7, edgecolor='black')
            ax.axvline(conf_stats['average'], color='red', linestyle='--', linewidth=2, label=f"Avg: {conf_stats['average']:.1f}%")
            ax.set_xlabel('Confidence (%)')
            ax.set_ylabel('Frequency')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        else:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=12)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_fps_chart(self):
        """Create FPS over time chart"""
        frame = ctk.CTkFrame(self.charts_frame)
        frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="⚡ System FPS Performance",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=5)
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get data
        fps_stats = self.stats_manager.get_fps_stats()
        
        if fps_stats['history']:
            times = [d['timestamp'] for d in fps_stats['history']]
            fps_values = [d['fps'] for d in fps_stats['history']]
            
            ax.plot(times, fps_values, color='#98D8C8', linewidth=2)
            ax.axhline(fps_stats['average'], color='orange', linestyle='--', linewidth=1, label=f"Avg: {fps_stats['average']} FPS")
            ax.set_xlabel('Time')
            ax.set_ylabel('FPS')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            fig.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=12)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_additional_stats_panel(self):
        """Create additional statistics text panel"""
        frame = ctk.CTkFrame(self.charts_frame)
        frame.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="📋 Additional Statistics",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(pady=5)
        
        # Get data
        stats = self.stats_manager.get_summary_stats()
        fps_stats = self.stats_manager.get_fps_stats()
        conf_stats = self.stats_manager.get_confidence_stats()
        peak_time = self.stats_manager.get_peak_alert_time()
        
        # Create text display
        text_frame = ctk.CTkScrollableFrame(frame, height=200)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        stats_text = f"""
📊 System Performance:
   • Average FPS: {fps_stats['average']} 
   • Min FPS: {fps_stats['min']} | Max FPS: {fps_stats['max']}
   • Current FPS: {fps_stats['current']}

🎯 Detection Accuracy:
   • Average Confidence: {conf_stats['average']}%
   • Min: {conf_stats['min']}% | Max: {conf_stats['max']}%

🚨 Alert Insights:
   • Most Common Object: {stats['most_common_object']} ({stats['most_common_count']} alerts)
   • Peak Alert Time: {peak_time}

📧 Email Notifications:
   • Emails Sent: {stats['emails_sent']}
   • Failures: {stats['email_failures']}

⏱️ Session Info:
   • Started: {stats['session_start']}
   • Uptime: {stats['uptime']}
        """
        
        stats_label = ctk.CTkLabel(
            text_frame,
            text=stats_text.strip(),
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        stats_label.pack(anchor="w", padx=10, pady=10)
    
    def export_data(self):
        """Export statistics to CSV"""
        filename = self.stats_manager.export_to_csv()
        if filename:
            from tkinter import messagebox
            messagebox.showinfo("Export Success", f"Statistics exported to:\n{filename}")
        else:
            from tkinter import messagebox
            messagebox.showwarning("No Data", "No statistics data to export")
    
    def reset_stats(self):
        """Reset all statistics"""
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all statistics?"):
            self.stats_manager.reset_stats()
            self.refresh_dashboard()
            messagebox.showinfo("Reset Complete", "All statistics have been reset")

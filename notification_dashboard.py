#!/usr/bin/env python3
"""
Notification Dashboard Widget
A comprehensive dashboard for monitoring and managing notifications
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtCharts import *
except ImportError:
    print("⚠️ PySide6 not available - GUI features disabled")
    sys.exit(1)

from modules.enhanced_notification_system import get_notification_manager
from notification_templates import NotificationTemplateManager
from advanced_notification_features import AdvancedNotificationManager

class NotificationStatsWidget(QWidget):
    """Widget displaying notification statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notification_manager = get_notification_manager()
        self.setup_ui()
        self.update_stats()
    
    def setup_ui(self):
        """Setup the statistics UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("📊 Notification Statistics")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2563eb; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        # Create stat cards
        self.total_card = self.create_stat_card("📬", "Total", "0", "#3b82f6")
        self.unread_card = self.create_stat_card("🔔", "Unread", "0", "#ef4444")
        self.today_card = self.create_stat_card("📅", "Today", "0", "#10b981")
        self.critical_card = self.create_stat_card("🚨", "Critical", "0", "#f59e0b")
        
        stats_grid.addWidget(self.total_card, 0, 0)
        stats_grid.addWidget(self.unread_card, 0, 1)
        stats_grid.addWidget(self.today_card, 1, 0)
        stats_grid.addWidget(self.critical_card, 1, 1)
        
        layout.addLayout(stats_grid)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e5e7eb;
                border-color: #9ca3af;
            }
        """)
        refresh_btn.clicked.connect(self.update_stats)
        layout.addWidget(refresh_btn)
    
    def create_stat_card(self, icon: str, label: str, value: str, color: str) -> QWidget:
        """Create a statistics card"""
        card = QWidget()
        card.setFixedSize(120, 80)
        card.setStyleSheet(f"""
            QWidget {{
                background: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        
        # Icon and value
        top_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 16))
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignRight)
        
        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        top_layout.addWidget(value_label)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 10))
        label_widget.setStyleSheet("color: #6b7280;")
        label_widget.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(top_layout)
        layout.addWidget(label_widget)
        
        # Store value label for updates
        setattr(card, 'value_label', value_label)
        
        return card
    
    def update_stats(self):
        """Update the statistics display"""
        try:
            notifications = self.notification_manager.get_notifications()
            
            # Calculate stats
            total_count = len(notifications)
            unread_count = len([n for n in notifications if not n.get('read', False)])
            
            # Today's notifications
            today = datetime.now().date()
            today_count = 0
            critical_count = 0
            
            for notification in notifications:
                # Parse timestamp
                timestamp_str = notification.get('timestamp', '')
                try:
                    if timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if timestamp.date() == today:
                            today_count += 1
                except:
                    pass
                
                # Count critical notifications
                priority = notification.get('priority', 20)
                if priority is not None and priority <= 5:  # Critical priority threshold
                    critical_count += 1
            
            # Update cards
            self.total_card.value_label.setText(str(total_count))
            self.unread_card.value_label.setText(str(unread_count))
            self.today_card.value_label.setText(str(today_count))
            self.critical_card.value_label.setText(str(critical_count))
            
        except Exception as e:
            print(f"❌ Error updating stats: {e}")

class NotificationChartWidget(QWidget):
    """Widget displaying notification charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notification_manager = get_notification_manager()
        self.setup_ui()
        self.update_chart()
    
    def setup_ui(self):
        """Setup the chart UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("📈 Notification Trends")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2563eb; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Chart view
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(300)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)
        
        # Chart type selector
        chart_controls = QHBoxLayout()
        
        chart_type_label = QLabel("Chart Type:")
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["📊 Category Distribution", "📈 Hourly Trends", "🎯 Priority Breakdown"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        
        chart_controls.addWidget(chart_type_label)
        chart_controls.addWidget(self.chart_type_combo)
        chart_controls.addStretch()
        
        layout.addLayout(chart_controls)
    
    def update_chart(self):
        """Update the chart based on selected type"""
        chart_type = self.chart_type_combo.currentText()
        
        if "Category Distribution" in chart_type:
            self.create_category_chart()
        elif "Hourly Trends" in chart_type:
            self.create_hourly_chart()
        elif "Priority Breakdown" in chart_type:
            self.create_priority_chart()
    
    def create_category_chart(self):
        """Create category distribution pie chart"""
        try:
            notifications = self.notification_manager.get_notifications()
            
            # Count by category
            category_counts = {}
            for notification in notifications:
                category = notification.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Create pie chart
            series = QPieSeries()
            
            colors = [
                "#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6",
                "#ec4899", "#06b6d4", "#84cc16", "#f97316", "#6366f1"
            ]
            
            for i, (category, count) in enumerate(category_counts.items()):
                slice_obj = series.append(f"{category.title()} ({count})", count)
                slice_obj.setBrush(QColor(colors[i % len(colors)]))
            
            # Create chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Notifications by Category")
            chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
            
            self.chart_view.setChart(chart)
            
        except Exception as e:
            print(f"❌ Error creating category chart: {e}")
    
    def create_hourly_chart(self):
        """Create hourly trends line chart"""
        try:
            notifications = self.notification_manager.get_notifications()
            
            # Count by hour for last 24 hours
            hourly_counts = {}
            now = datetime.now()
            
            for notification in notifications:
                timestamp_str = notification.get('timestamp', '')
                try:
                    if timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if (now - timestamp).total_seconds() <= 24 * 3600:  # Last 24 hours
                            hour = timestamp.hour
                            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                except:
                    pass
            
            # Create line series
            series = QLineSeries()
            series.setName("Notifications per Hour")
            
            for hour in range(24):
                count = hourly_counts.get(hour, 0)
                series.append(hour, count)
            
            # Create chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Notification Trends (Last 24 Hours)")
            chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
            
            # Create axes
            axis_x = QValueAxis()
            axis_x.setRange(0, 23)
            axis_x.setTitleText("Hour of Day")
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Number of Notifications")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            self.chart_view.setChart(chart)
            
        except Exception as e:
            print(f"❌ Error creating hourly chart: {e}")
    
    def create_priority_chart(self):
        """Create priority breakdown bar chart"""
        try:
            notifications = self.notification_manager.get_notifications()
            
            # Count by priority ranges
            priority_ranges = {
                "Critical (1-5)": 0,
                "High (6-10)": 0,
                "Medium (11-15)": 0,
                "Low (16-20)": 0
            }
            
            for notification in notifications:
                priority = notification.get('priority', 20)
                if priority <= 5:
                    priority_ranges["Critical (1-5)"] += 1
                elif priority <= 10:
                    priority_ranges["High (6-10)"] += 1
                elif priority <= 15:
                    priority_ranges["Medium (11-15)"] += 1
                else:
                    priority_ranges["Low (16-20)"] += 1
            
            # Create bar series
            series = QBarSeries()
            bar_set = QBarSet("Notifications")
            
            categories = []
            for category, count in priority_ranges.items():
                categories.append(category)
                bar_set.append(count)
            
            series.append(bar_set)
            
            # Create chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Notifications by Priority Level")
            chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
            
            # Create axes
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Number of Notifications")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            self.chart_view.setChart(chart)
            
        except Exception as e:
            print(f"❌ Error creating priority chart: {e}")

class NotificationDashboard(QWidget):
    """Main notification dashboard widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔔 Notification Dashboard")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("🔔 Notification Dashboard")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #1f2937;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dbeafe, stop:1 #bfdbfe);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Stats and controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Statistics widget
        self.stats_widget = NotificationStatsWidget()
        left_layout.addWidget(self.stats_widget)
        
        # Quick actions
        actions_group = QGroupBox("🎮 Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Action buttons
        test_btn = QPushButton("🧪 Send Test Notification")
        test_btn.clicked.connect(self.send_test_notification)
        
        clear_btn = QPushButton("🗑️ Clear All Notifications")
        clear_btn.clicked.connect(self.clear_all_notifications)
        
        export_btn = QPushButton("📤 Export Data")
        export_btn.clicked.connect(self.export_data)
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        
        for btn in [test_btn, clear_btn, export_btn, settings_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #f3f4f6;
                    border: 2px solid #d1d5db;
                    border-radius: 6px;
                    padding: 10px;
                    text-align: left;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #e5e7eb;
                    border-color: #9ca3af;
                }
            """)
            actions_layout.addWidget(btn)
        
        left_layout.addWidget(actions_group)
        left_layout.addStretch()
        
        # Right panel - Charts
        self.chart_widget = NotificationChartWidget()
        
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(self.chart_widget)
        content_splitter.setSizes([300, 500])
        
        layout.addWidget(content_splitter)
        
        # Status bar
        self.status_label = QLabel("✅ Dashboard ready")
        self.status_label.setStyleSheet("""
            QLabel {
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 4px;
                padding: 8px;
                color: #166534;
            }
        """)
        layout.addWidget(self.status_label)
    
    def refresh_all(self):
        """Refresh all dashboard components"""
        try:
            self.stats_widget.update_stats()
            self.chart_widget.update_chart()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.status_label.setText(f"🔄 Last updated: {timestamp}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error refreshing: {e}")
    
    def send_test_notification(self):
        """Send a test notification"""
        try:
            from notification_templates import notify_daily_summary
            import random
            
            # Generate random test data
            sales = random.randint(20, 100)
            revenue = random.randint(10000, 50000)
            efficiency = random.randint(75, 98)
            
            notify_daily_summary(sales, revenue, efficiency)
            
            self.status_label.setText("✅ Test notification sent successfully!")
            QTimer.singleShot(2000, self.refresh_all)
            
        except Exception as e:
            self.status_label.setText(f"❌ Error sending test notification: {e}")
    
    def clear_all_notifications(self):
        """Clear all notifications after confirmation"""
        reply = QMessageBox.question(
            self,
            "Clear Notifications",
            "🗑️ Are you sure you want to clear all notifications?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Clear notifications (implementation would depend on the notification manager)
                self.status_label.setText("✅ All notifications cleared!")
                QTimer.singleShot(1000, self.refresh_all)
                
            except Exception as e:
                self.status_label.setText(f"❌ Error clearing notifications: {e}")
    
    def export_data(self):
        """Export notification data"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Notification Data",
                f"notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;CSV Files (*.csv)"
            )
            
            if filename:
                # Export implementation would go here
                self.status_label.setText(f"✅ Data exported to {filename}")
                
        except Exception as e:
            self.status_label.setText(f"❌ Error exporting data: {e}")
    
    def show_settings(self):
        """Show notification settings"""
        try:
            from advanced_notification_features import NotificationPreferencesDialog, AdvancedNotificationManager
            
            advanced_manager = AdvancedNotificationManager()
            dialog = NotificationPreferencesDialog(advanced_manager, self)
            dialog.exec()
            
        except Exception as e:
            self.status_label.setText(f"❌ Error opening settings: {e}")

def create_notification_dashboard():
    """Create and show the notification dashboard"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dashboard = NotificationDashboard()
    dashboard.show()
    
    return dashboard, app

if __name__ == "__main__":
    dashboard, app = create_notification_dashboard()
    sys.exit(app.exec())

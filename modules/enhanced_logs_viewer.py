"""
Enhanced Logs Viewer
Command-line style log viewer with real-time updates, filtering, and detailed system activity
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLabel, QPushButton, QComboBox, QLineEdit, 
                             QCheckBox, QSpinBox, QGroupBox, QFormLayout,
                             QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QProgressBar, QFrame, QScrollArea,
                             QDateTimeEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal, QTimer, QDateTime, QThread
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QPalette

# Import activity tracker
try:
    from .activity_tracker import get_activity_tracker, ActivityType, ActivityLevel, ActivityRecord
except ImportError:
    get_activity_tracker = None
    ActivityType = None
    ActivityLevel = None
    ActivityRecord = None

class LogProcessor(QThread):
    """Background thread for processing logs"""

    logs_processed = Signal(list)
    
    def __init__(self, log_file_path: str, parent=None):
        super().__init__(parent)
        self.log_file_path = log_file_path
        self.running = True
    
    def run(self):
        """Process log file and emit results"""
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r') as f:
                    lines = f.readlines()
                
                # Process last 1000 lines for performance
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                self.logs_processed.emit(recent_lines)
        except Exception as e:
            logging.error(f"Error processing logs: {e}")
    
    def stop(self):
        """Stop the thread"""
        self.running = False
        self.quit()
        self.wait()

class ActivityCard(QFrame):
    """Modern activity card widget"""
    
    def __init__(self, activity: ActivityRecord, parent=None):
        super().__init__(parent)
        self.activity = activity
        self.init_ui()
    
    def init_ui(self):
        """Initialize activity card UI"""
        self.setFixedHeight(100)
        self.setStyleSheet(self.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Header with timestamp and type
        header_layout = QHBoxLayout()
        
        timestamp_label = QLabel(datetime.fromisoformat(self.activity.timestamp).strftime("%H:%M:%S"))
        timestamp_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500;")
        header_layout.addWidget(timestamp_label)
        
        type_label = QLabel(self.activity.activity_type.upper())
        type_label.setStyleSheet(f"color: {self.get_type_color()}; font-size: 10px; font-weight: 600; padding: 2px 6px; background-color: rgba(255,255,255,0.1); border-radius: 3px;")
        header_layout.addWidget(type_label)
        
        header_layout.addStretch()
        
        level_label = QLabel(self.activity.level.upper())
        level_label.setStyleSheet(f"color: {self.get_level_color()}; font-size: 10px; font-weight: 600;")
        header_layout.addWidget(level_label)
        
        layout.addLayout(header_layout)
        
        # Module and action
        module_action = QLabel(f"{self.activity.module}.{self.activity.action}")
        module_action.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 600;")
        layout.addWidget(module_action)
        
        # Description
        description = QLabel(self.activity.description)
        description.setStyleSheet("color: #475569; font-size: 11px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Performance info if available
        if self.activity.execution_time:
            perf_label = QLabel(f"⏱️ {self.activity.execution_time:.3f}s")
            perf_label.setStyleSheet("color: #7c3aed; font-size: 10px;")
            layout.addWidget(perf_label)
    
    def get_card_style(self):
        """Get card styling based on activity level"""
        base_style = """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 2px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: rgba(59, 130, 246, 0.05);
            }
        """
        
        if self.activity.level == "error":
            base_style += """
                QFrame {
                    border-left: 4px solid #ef4444;
                }
            """
        elif self.activity.level == "warning":
            base_style += """
                QFrame {
                    border-left: 4px solid #f59e0b;
                }
            """
        elif self.activity.activity_type == "user_action":
            base_style += """
                QFrame {
                    border-left: 4px solid #3b82f6;
                }
            """
        
        return base_style
    
    def get_type_color(self):
        """Get color for activity type"""
        colors = {
            "user_action": "#3b82f6",
            "system_event": "#10b981",
            "data_change": "#8b5cf6",
            "error": "#ef4444",
            "performance": "#f59e0b",
            "navigation": "#06b6d4",
            "import_export": "#84cc16",
            "notification": "#ec4899",
            "ingredient_auto_add": "#a855f7"
        }
        return colors.get(self.activity.activity_type, "#64748b")
    
    def get_level_color(self):
        """Get color for activity level"""
        colors = {
            "debug": "#64748b",
            "info": "#3b82f6",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "critical": "#dc2626"
        }
        return colors.get(self.activity.level, "#64748b")

class EnhancedLogsViewer(QWidget):
    """Enhanced logs viewer with command-line style interface and real-time updates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.activity_tracker = get_activity_tracker() if get_activity_tracker else None
        
        # Initialize UI
        self.init_ui()
        
        # Setup real-time updates
        self.setup_real_time_updates()
        
        # Load initial data
        self.load_logs()
        
        self.logger.info("Enhanced Logs Viewer initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("System Activity & Logs")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Control buttons
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("background-color: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px;")
        self.refresh_btn.clicked.connect(self.load_logs)
        header_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("Export Logs")
        self.export_btn.setStyleSheet("background-color: #10b981; color: white; padding: 8px 16px; border-radius: 6px;")
        self.export_btn.clicked.connect(self.export_logs)
        header_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.setStyleSheet("background-color: #ef4444; color: white; padding: 8px 16px; border-radius: 6px;")
        self.clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Create tabs for different views
        self.create_tabs_section(layout)
    
    def create_tabs_section(self, parent_layout):
        """Create tabbed interface for different log views"""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
        """)
        
        # Activity Stream Tab
        self.create_activity_stream_tab()
        
        # Command Line Logs Tab
        self.create_command_line_tab()
        
        # Performance Metrics Tab
        self.create_performance_tab()
        
        # System Summary Tab
        self.create_summary_tab()
        
        parent_layout.addWidget(self.tabs)
    
    def create_activity_stream_tab(self):
        """Create activity stream tab with modern cards"""
        activity_widget = QWidget()
        layout = QVBoxLayout(activity_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # Activity type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", "")
        if ActivityType:
            for activity_type in ActivityType:
                self.type_filter.addItem(activity_type.value.replace("_", " ").title(), activity_type.value)
        self.type_filter.currentTextChanged.connect(self.filter_activities)
        filters_layout.addWidget(QLabel("Type:"))
        filters_layout.addWidget(self.type_filter)
        
        # Level filter
        self.level_filter = QComboBox()
        self.level_filter.addItem("All Levels", "")
        if ActivityLevel:
            for level in ActivityLevel:
                self.level_filter.addItem(level.value.title(), level.value)
        self.level_filter.currentTextChanged.connect(self.filter_activities)
        filters_layout.addWidget(QLabel("Level:"))
        filters_layout.addWidget(self.level_filter)
        
        # Module filter
        self.module_filter = QLineEdit()
        self.module_filter.setPlaceholderText("Filter by module...")
        self.module_filter.textChanged.connect(self.filter_activities)
        filters_layout.addWidget(QLabel("Module:"))
        filters_layout.addWidget(self.module_filter)
        
        filters_layout.addStretch()
        
        layout.addWidget(filters_group)
        
        # Activity cards scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.activity_cards_widget = QWidget()
        self.activity_cards_layout = QVBoxLayout(self.activity_cards_widget)
        self.activity_cards_layout.setSpacing(8)
        self.activity_cards_layout.addStretch()
        
        scroll_area.setWidget(self.activity_cards_widget)
        layout.addWidget(scroll_area)
        
        self.tabs.addTab(activity_widget, "Activity Stream")
    
    def create_command_line_tab(self):
        """Create command-line style logs tab"""
        cmd_widget = QWidget()
        layout = QVBoxLayout(cmd_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Command line style text area
        self.cmd_logs = QTextEdit()
        self.cmd_logs.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.cmd_logs.setReadOnly(True)
        layout.addWidget(self.cmd_logs)
        
        # Command input
        cmd_input_layout = QHBoxLayout()
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.cmd_input.setPlaceholderText("Enter command (help for available commands)...")
        self.cmd_input.returnPressed.connect(self.execute_command)
        cmd_input_layout.addWidget(QLabel("$"))
        cmd_input_layout.addWidget(self.cmd_input)
        
        layout.addLayout(cmd_input_layout)
        
        self.tabs.addTab(cmd_widget, "Command Line")
    
    def create_performance_tab(self):
        """Create performance metrics tab"""
        perf_widget = QWidget()
        layout = QVBoxLayout(perf_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Performance metrics will be added here
        perf_label = QLabel("Performance metrics will be displayed here")
        perf_label.setAlignment(Qt.AlignCenter)
        perf_label.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(perf_label)
        
        self.tabs.addTab(perf_widget, "Performance")
    
    def create_summary_tab(self):
        """Create system summary tab"""
        summary_widget = QWidget()
        layout = QVBoxLayout(summary_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Summary metrics will be added here
        summary_label = QLabel("System summary will be displayed here")
        summary_label.setAlignment(Qt.AlignCenter)
        summary_label.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(summary_label)
        
        self.tabs.addTab(summary_widget, "Summary")
    
    def setup_real_time_updates(self):
        """Setup real-time log updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_logs)
        self.update_timer.start(5000)  # Update every 5 seconds
        
        # Connect to activity tracker if available
        if self.activity_tracker:
            self.activity_tracker.activity_logged.connect(self.on_new_activity)
    
    def load_logs(self):
        """Load and display logs"""
        try:
            # Load activities from activity tracker
            if self.activity_tracker:
                activities = self.activity_tracker.get_activities(limit=100)
                self.display_activities(activities)
            
            # Load command line logs
            self.load_command_line_logs()
            
        except Exception as e:
            self.logger.error(f"Error loading logs: {e}")
    
    def display_activities(self, activities: List[ActivityRecord]):
        """Display activities as cards"""
        # Clear existing cards
        for i in reversed(range(self.activity_cards_layout.count())):
            child = self.activity_cards_layout.itemAt(i).widget()
            if child and isinstance(child, ActivityCard):
                child.deleteLater()
        
        # Add new activity cards
        for activity in activities:
            card = ActivityCard(activity)
            self.activity_cards_layout.insertWidget(0, card)
    
    def load_command_line_logs(self):
        """Load command line style logs with timeout protection"""
        try:
            log_file = "kitchen_dashboard.log"
            if os.path.exists(log_file):
                # Check file size first to avoid loading huge files
                file_size = os.path.getsize(log_file)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    self.append_cmd_log("Log file too large, showing recent entries only...")
                    # Read only the last part of the file
                    with open(log_file, 'rb') as f:
                        f.seek(max(0, file_size - 50000))  # Last 50KB
                        lines = f.read().decode('utf-8', errors='ignore').splitlines()
                else:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                # Display last 50 lines only to avoid UI freeze
                recent_lines = lines[-50:] if len(lines) > 50 else lines

                self.cmd_logs.clear()
                for line in recent_lines:
                    if line.strip():  # Skip empty lines
                        self.append_cmd_log(line.strip())

        except Exception as e:
            self.logger.error(f"Error loading command line logs: {e}")
            self.append_cmd_log(f"Error loading logs: {str(e)}")
    
    def append_cmd_log(self, text: str):
        """Append text to command line logs with syntax highlighting"""
        cursor = self.cmd_logs.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Simple syntax highlighting
        if "ERROR" in text:
            format = QTextCharFormat()
            format.setForeground(QColor("#ef4444"))
            cursor.insertText(text + "\n", format)
        elif "WARNING" in text:
            format = QTextCharFormat()
            format.setForeground(QColor("#f59e0b"))
            cursor.insertText(text + "\n", format)
        elif "INFO" in text:
            format = QTextCharFormat()
            format.setForeground(QColor("#10b981"))
            cursor.insertText(text + "\n", format)
        else:
            cursor.insertText(text + "\n")
        
        # Auto-scroll to bottom
        self.cmd_logs.setTextCursor(cursor)
    
    def filter_activities(self):
        """Filter activities based on current filter settings with timeout protection"""
        if not self.activity_tracker:
            return

        try:
            # Get filter values
            activity_type = self.type_filter.currentData()
            level = self.level_filter.currentData()
            module = self.module_filter.text().strip()

            # Apply filters with smaller limit to avoid UI freeze
            activities = self.activity_tracker.get_activities(limit=50)

            if activity_type:
                activities = [a for a in activities if a.activity_type == activity_type]

            if level:
                activities = [a for a in activities if a.level == level]

            if module:
                activities = [a for a in activities if module.lower() in a.module.lower()]

            self.display_activities(activities)
        except Exception as e:
            self.logger.error(f"Error filtering activities: {e}")
            # Show error message in UI instead of crashing
            self.append_cmd_log(f"Error loading activities: {str(e)}")
    
    def execute_command(self):
        """Execute command line command"""
        command = self.cmd_input.text().strip()
        if not command:
            return
        
        self.cmd_input.clear()
        self.append_cmd_log(f"$ {command}")
        
        # Process commands
        if command == "help":
            self.append_cmd_log("Available commands:")
            self.append_cmd_log("  help - Show this help")
            self.append_cmd_log("  clear - Clear the log display")
            self.append_cmd_log("  status - Show system status")
            self.append_cmd_log("  activities - Show recent activities")
            self.append_cmd_log("  errors - Show recent errors")
        elif command == "clear":
            self.cmd_logs.clear()
        elif command == "status":
            self.show_system_status()
        elif command == "activities":
            self.show_recent_activities()
        elif command == "errors":
            self.show_recent_errors()
        else:
            self.append_cmd_log(f"Unknown command: {command}")
            self.append_cmd_log("Type 'help' for available commands")
    
    def show_system_status(self):
        """Show system status in command line"""
        if self.activity_tracker:
            summary = self.activity_tracker.get_activity_summary(hours=1)
            self.append_cmd_log(f"System Status (Last Hour):")
            self.append_cmd_log(f"  Total Activities: {summary['total_activities']}")
            self.append_cmd_log(f"  Errors: {summary['errors']}")
            self.append_cmd_log(f"  Most Active Module: {summary.get('most_active_module', 'N/A')}")
            if summary['performance_avg'] > 0:
                self.append_cmd_log(f"  Avg Performance: {summary['performance_avg']:.3f}s")
        else:
            self.append_cmd_log("Activity tracker not available")
    
    def show_recent_activities(self):
        """Show recent activities in command line"""
        if self.activity_tracker:
            activities = self.activity_tracker.get_activities(limit=10)
            self.append_cmd_log("Recent Activities:")
            for activity in activities:
                timestamp = datetime.fromisoformat(activity.timestamp).strftime("%H:%M:%S")
                self.append_cmd_log(f"  [{timestamp}] {activity.module}.{activity.action}: {activity.description}")
        else:
            self.append_cmd_log("Activity tracker not available")
    
    def show_recent_errors(self):
        """Show recent errors in command line"""
        if self.activity_tracker:
            activities = self.activity_tracker.get_activities(level=ActivityLevel.ERROR if ActivityLevel else None, limit=10)
            self.append_cmd_log("Recent Errors:")
            for activity in activities:
                timestamp = datetime.fromisoformat(activity.timestamp).strftime("%H:%M:%S")
                self.append_cmd_log(f"  [{timestamp}] {activity.module}.{activity.action}: {activity.description}")
                if activity.error_details:
                    self.append_cmd_log(f"    Error: {activity.error_details}")
        else:
            self.append_cmd_log("Activity tracker not available")
    
    def on_new_activity(self, activity: ActivityRecord):
        """Handle new activity from tracker"""
        # Add to command line logs
        timestamp = datetime.fromisoformat(activity.timestamp).strftime("%H:%M:%S")
        log_text = f"[{timestamp}] {activity.level.upper()} {activity.module}.{activity.action}: {activity.description}"
        self.append_cmd_log(log_text)
        
        # Refresh activity cards if on that tab
        if self.tabs.currentIndex() == 0:  # Activity Stream tab
            self.filter_activities()
    
    def update_logs(self):
        """Update logs periodically"""
        # Only update if activity tracker is available and tab is visible
        if self.activity_tracker and self.isVisible():
            current_tab = self.tabs.currentIndex()
            if current_tab == 0:  # Activity Stream
                self.filter_activities()
            elif current_tab == 1:  # Command Line
                # Don't auto-refresh command line to avoid interrupting user
                pass
    
    def export_logs(self):
        """Export logs to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path and self.activity_tracker:
                success = self.activity_tracker.export_activities_csv(file_path)
                if success:
                    QMessageBox.information(self, "Export Complete", f"Logs exported to {file_path}")
                else:
                    QMessageBox.warning(self, "Export Failed", "Failed to export logs")
        
        except Exception as e:
            self.logger.error(f"Error exporting logs: {e}")
            QMessageBox.critical(self, "Export Error", f"Error exporting logs: {str(e)}")
    
    def clear_logs(self):
        """Clear logs after confirmation"""
        reply = QMessageBox.question(
            self, "Clear Logs", 
            "Are you sure you want to clear all logs? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.activity_tracker:
                self.activity_tracker.activities.clear()
                self.activity_tracker.save_activities()
            
            self.cmd_logs.clear()
            self.display_activities([])
            
            QMessageBox.information(self, "Logs Cleared", "All logs have been cleared")

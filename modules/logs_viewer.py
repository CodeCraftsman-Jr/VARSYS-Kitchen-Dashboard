from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QLabel, QPushButton, QComboBox, QCheckBox, QHeaderView, 
                               QSplitter, QGroupBox, QTextEdit, QFileDialog)
from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QColor, QFont, QIcon

import os
import time
from datetime import datetime

from utils.app_logger import get_logger, AppLogger

class LogsViewerWidget(QWidget):
    """Widget for displaying application logs in a structured format"""
    
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    # Text colors for log levels
    LOG_COLORS = {
        'DEBUG': QColor(100, 100, 100),  # Gray
        'INFO': QColor(0, 0, 0),         # Black
        'WARNING': QColor(255, 165, 0),  # Orange
        'ERROR': QColor(255, 0, 0),      # Red
        'CRITICAL': QColor(128, 0, 128)  # Purple
    }
    
    # Background colors for log rows
    LOG_BG_COLORS = {
        'DEBUG': QColor(240, 240, 240),    # Light Gray
        'INFO': QColor(255, 255, 255),     # White
        'WARNING': QColor(255, 250, 230),   # Light Yellow
        'ERROR': QColor(255, 235, 235),     # Light Red
        'CRITICAL': QColor(255, 220, 255)   # Light Purple
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get logger instance
        self.app_logger = get_logger()
        self.log_buffer = AppLogger.get_log_buffer()
        
        # Connect to log signal
        self.app_logger.signal.new_log.connect(self.add_log)
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Application Logs")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
        
        # Create filter controls
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        # Log level filter
        level_label = QLabel("Log Level:")
        self.level_combo = QComboBox()
        self.level_combo.addItem("All Levels")
        for level in self.LOG_LEVELS:
            self.level_combo.addItem(level)
        self.level_combo.currentIndexChanged.connect(self.apply_filters)
        
        # Auto-scroll checkbox
        self.auto_scroll = QCheckBox("Auto-scroll")
        self.auto_scroll.setChecked(True)
        
        # Clear logs button
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        
        # Export logs button
        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self.export_logs)
        
        # Add widgets to filter layout
        filter_layout.addWidget(level_label)
        filter_layout.addWidget(self.level_combo)
        filter_layout.addStretch(1)
        filter_layout.addWidget(self.auto_scroll)
        filter_layout.addWidget(self.clear_button)
        filter_layout.addWidget(self.export_button)
        
        self.layout.addWidget(filter_widget)
        
        # Create logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(["Time", "Level", "Caller", "Message"])
        self.logs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.layout.addWidget(self.logs_table)
        
        # Create log detail section
        detail_group = QGroupBox("Log Details")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        self.layout.addWidget(detail_group)
        
        # Set the ratio of tables to details (70:30)
        self.layout.setStretch(2, 7)  # Logs table
        self.layout.setStretch(3, 3)  # Details
        
        # Connect selection change to show details
        self.logs_table.itemSelectionChanged.connect(self.show_log_details)
        
        # Initialize with existing logs
        self.populate_logs()
        
        # Add initial log entry
        self.app_logger.info("Logs viewer initialized")
    
    def populate_logs(self):
        """Populate the logs table with existing log buffer"""
        self.logs_table.setRowCount(0)  # Clear existing rows

        # Add all logs from buffer
        for log_entry in self.log_buffer:
            if len(log_entry) >= 5:  # New format with caller_info and stack_trace
                level, message, timestamp, caller_info, stack_trace = log_entry
                self.add_log_to_table(level, message, timestamp, caller_info, stack_trace)
            elif len(log_entry) >= 3:  # Old format
                level, message, timestamp = log_entry[:3]
                self.add_log_to_table(level, message, timestamp, "", "")
    
    def add_log(self, level, message, timestamp, caller_info="", stack_trace=""):
        """Add a new log entry (connected to logger signal)"""
        self.add_log_to_table(level, message, timestamp, caller_info, stack_trace)
    
    def add_log_to_table(self, level, message, timestamp, caller_info="", stack_trace=""):
        """Add a log entry to the table with proper formatting"""
        # Apply filters
        if self.level_combo.currentText() != "All Levels" and level != self.level_combo.currentText():
            return

        # Add new row
        row_position = self.logs_table.rowCount()
        self.logs_table.insertRow(row_position)

        # Create items
        time_item = QTableWidgetItem(timestamp)
        level_item = QTableWidgetItem(level)
        caller_item = QTableWidgetItem(caller_info)
        message_item = QTableWidgetItem(message)

        # Store additional data for details view
        time_item.setData(Qt.UserRole, {
            'caller_info': caller_info,
            'stack_trace': stack_trace,
            'full_message': message
        })

        # Get colors for this log level
        text_color = self.LOG_COLORS.get(level, QColor(0, 0, 0))
        bg_color = self.LOG_BG_COLORS.get(level, QColor(255, 255, 255))

        # Set text color based on level
        level_item.setForeground(text_color)

        # Apply text color to message for ERROR and CRITICAL logs
        if level in ['ERROR', 'CRITICAL']:
            message_item.setForeground(text_color)
            caller_item.setForeground(text_color)
            # Make text bold for errors
            font = message_item.font()
            font.setBold(True)
            message_item.setFont(font)
            level_item.setFont(font)
            caller_item.setFont(font)

        # Add items to table
        self.logs_table.setItem(row_position, 0, time_item)
        self.logs_table.setItem(row_position, 1, level_item)
        self.logs_table.setItem(row_position, 2, caller_item)
        self.logs_table.setItem(row_position, 3, message_item)

        # Apply background color to all cells in the row
        for col in range(self.logs_table.columnCount()):
            self.logs_table.item(row_position, col).setBackground(bg_color)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll.isChecked():
            self.logs_table.scrollToBottom()
    
    def apply_filters(self):
        """Apply selected filters to the logs table"""
        self.populate_logs()
    
    def show_log_details(self):
        """Show details of the selected log entry"""
        selected_rows = self.logs_table.selectedItems()
        if not selected_rows:
            return

        # Get the row of the first selected item
        row = selected_rows[0].row()

        # Extract log details
        timestamp = self.logs_table.item(row, 0).text()
        level = self.logs_table.item(row, 1).text()
        caller = self.logs_table.item(row, 2).text()
        message = self.logs_table.item(row, 3).text()

        # Get additional data
        additional_data = self.logs_table.item(row, 0).data(Qt.UserRole)
        if additional_data:
            caller_info = additional_data.get('caller_info', '')
            stack_trace = additional_data.get('stack_trace', '')
            full_message = additional_data.get('full_message', message)
        else:
            caller_info = caller
            stack_trace = ''
            full_message = message

        # Format the details
        details = f"Timestamp: {timestamp}\n"
        details += f"Level: {level}\n"
        details += f"Caller: {caller_info}\n"
        details += f"Message: {full_message}\n"

        if stack_trace:
            details += f"\nStack Trace:\n{stack_trace}"

        # Update detail view
        self.detail_text.setText(details)
    
    def clear_logs(self):
        """Clear all logs from the table and buffer"""
        self.logs_table.setRowCount(0)
        AppLogger.clear_log_buffer()
        self.app_logger.info("Logs cleared by user")
    
    def export_logs(self):
        """Export logs to a file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            os.path.expanduser("~/Desktop/kitchen_dashboard_logs.txt"),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for row in range(self.logs_table.rowCount()):
                        timestamp = self.logs_table.item(row, 0).text()
                        level = self.logs_table.item(row, 1).text()
                        caller = self.logs_table.item(row, 2).text()
                        message = self.logs_table.item(row, 3).text()

                        # Get additional data if available
                        additional_data = self.logs_table.item(row, 0).data(Qt.UserRole)
                        if additional_data and additional_data.get('stack_trace'):
                            stack_trace = additional_data.get('stack_trace', '')
                            f.write(f"{timestamp} - {level} - {caller} - {message}\n")
                            if stack_trace:
                                f.write(f"Stack Trace:\n{stack_trace}\n\n")
                        else:
                            f.write(f"{timestamp} - {level} - {caller} - {message}\n")
                
                self.app_logger.info(f"Logs exported to {filename}")
            except Exception as e:
                self.app_logger.error(f"Error exporting logs: {str(e)}")

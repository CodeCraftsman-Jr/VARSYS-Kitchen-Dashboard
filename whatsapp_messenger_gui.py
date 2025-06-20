#!/usr/bin/env python3
"""
WhatsApp Messenger GUI Application
Provides a graphical interface for managing the standalone WhatsApp messenger
"""

import sys
import os
import json
import threading
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QGroupBox, QGridLayout, QProgressBar, QMessageBox,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QColor, QIcon

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from whatsapp_messenger import WhatsAppMessenger

class MessengerWorker(QThread):
    """Worker thread for running the messenger"""
    status_updated = Signal(dict)
    log_message = Signal(str)
    
    def __init__(self, messenger):
        super().__init__()
        self.messenger = messenger
        self.running = False
    
    def run(self):
        """Run the messenger in a separate thread"""
        self.running = True
        self.messenger.running = True
        
        while self.running and self.messenger.running:
            try:
                # Check connection status
                if not self.messenger.whatsapp_driver or not self.messenger.whatsapp_driver.is_connected:
                    self.log_message.emit("⚠️ WhatsApp connection lost, attempting to reconnect...")
                    if not self.messenger.connect_to_whatsapp():
                        self.log_message.emit("❌ Failed to reconnect to WhatsApp")
                        self.msleep(30000)  # Wait 30 seconds
                        continue
                    else:
                        self.log_message.emit("✅ Reconnected to WhatsApp successfully")
                
                # Process pending messages
                self.messenger.process_pending_messages()
                
                # Emit status update
                status = self.messenger.get_status()
                self.status_updated.emit(status)
                
                # Wait for next check
                self.msleep(self.messenger.config.get('check_interval_seconds', 30) * 1000)
                
            except Exception as e:
                self.log_message.emit(f"❌ Error in messenger worker: {e}")
                self.msleep(30000)  # Wait 30 seconds before retry
    
    def stop(self):
        """Stop the worker thread"""
        self.running = False
        if self.messenger:
            self.messenger.stop()

class WhatsAppMessengerGUI(QMainWindow):
    """GUI application for WhatsApp Messenger management"""
    
    def __init__(self):
        super().__init__()
        self.messenger = None
        self.worker = None
        
        self.setWindowTitle("WhatsApp Messenger - Standalone System")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize UI
        self.init_ui()
        
        # Initialize messenger
        self.init_messenger()
        
        # Setup timers
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("WhatsApp Messenger - Standalone System")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2563eb; padding: 10px; background-color: #f0f9ff; border-radius: 8px;")
        layout.addWidget(title_label)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Status Tab
        status_tab = self.create_status_tab()
        tabs.addTab(status_tab, "📊 Status")
        
        # Messages Tab
        messages_tab = self.create_messages_tab()
        tabs.addTab(messages_tab, "💬 Messages")
        
        # Logs Tab
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "📋 Logs")
        
        # Configuration Tab
        config_tab = self.create_config_tab()
        tabs.addTab(config_tab, "⚙️ Configuration")
        
        layout.addWidget(tabs)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶️ Start Messenger")
        self.start_button.clicked.connect(self.start_messenger)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ Stop Messenger")
        self.stop_button.clicked.connect(self.stop_messenger)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        control_layout.addWidget(self.stop_button)
        
        self.test_button = QPushButton("🧪 Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        control_layout.addWidget(self.test_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
    
    def create_status_tab(self):
        """Create the status tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Connection Status
        connection_group = QGroupBox("Connection Status")
        connection_layout = QGridLayout(connection_group)
        
        self.connection_status_label = QLabel("❌ Disconnected")
        self.connection_status_label.setStyleSheet("font-weight: bold; color: #ef4444;")
        connection_layout.addWidget(QLabel("WhatsApp Web:"), 0, 0)
        connection_layout.addWidget(self.connection_status_label, 0, 1)
        
        self.target_group_label = QLabel("Not Set")
        connection_layout.addWidget(QLabel("Target Group:"), 1, 0)
        connection_layout.addWidget(self.target_group_label, 1, 1)
        
        layout.addWidget(connection_group)
        
        # Message Statistics
        stats_group = QGroupBox("Message Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.pending_messages_label = QLabel("0")
        self.pending_messages_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(QLabel("Pending Messages:"), 0, 0)
        stats_layout.addWidget(self.pending_messages_label, 0, 1)
        
        self.last_check_label = QLabel("Never")
        stats_layout.addWidget(QLabel("Last Check:"), 1, 0)
        stats_layout.addWidget(self.last_check_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # System Status
        system_group = QGroupBox("System Status")
        system_layout = QGridLayout(system_group)
        
        self.messenger_status_label = QLabel("❌ Stopped")
        self.messenger_status_label.setStyleSheet("font-weight: bold; color: #ef4444;")
        system_layout.addWidget(QLabel("Messenger:"), 0, 0)
        system_layout.addWidget(self.messenger_status_label, 0, 1)
        
        self.uptime_label = QLabel("00:00:00")
        system_layout.addWidget(QLabel("Uptime:"), 1, 0)
        system_layout.addWidget(self.uptime_label, 1, 1)
        
        layout.addWidget(system_group)
        
        layout.addStretch()
        return widget
    
    def create_messages_tab(self):
        """Create the messages tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setColumnCount(6)
        self.messages_table.setHorizontalHeaderLabels([
            "Timestamp", "Type", "Priority", "Status", "Retries", "Content"
        ])
        
        # Set column widths
        header = self.messages_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        layout.addWidget(self.messages_table)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh Messages")
        refresh_button.clicked.connect(self.refresh_messages)
        layout.addWidget(refresh_button)
        
        return widget
    
    def create_logs_tab(self):
        """Create the logs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        # Clear logs button
        clear_button = QPushButton("🗑️ Clear Logs")
        clear_button.clicked.connect(self.clear_logs)
        layout.addWidget(clear_button)
        
        return widget
    
    def create_config_tab(self):
        """Create the configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        config_label = QLabel("Configuration settings will be displayed here")
        config_label.setAlignment(Qt.AlignCenter)
        config_label.setStyleSheet("color: #6b7280; font-style: italic;")
        layout.addWidget(config_label)
        
        return widget
    
    def init_messenger(self):
        """Initialize the WhatsApp messenger"""
        try:
            self.messenger = WhatsAppMessenger()
            self.add_log("✅ WhatsApp Messenger initialized")
            
            # Update initial status
            self.update_status()
            
        except Exception as e:
            self.add_log(f"❌ Failed to initialize messenger: {e}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize WhatsApp Messenger:\n{e}")
    
    def start_messenger(self):
        """Start the messenger worker"""
        try:
            if not self.messenger:
                self.init_messenger()
                if not self.messenger:
                    return
            
            # Create and start worker thread
            self.worker = MessengerWorker(self.messenger)
            self.worker.status_updated.connect(self.on_status_updated)
            self.worker.log_message.connect(self.add_log)
            self.worker.start()
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.messenger_status_label.setText("✅ Running")
            self.messenger_status_label.setStyleSheet("font-weight: bold; color: #10b981;")
            
            self.add_log("▶️ WhatsApp Messenger started")
            
        except Exception as e:
            self.add_log(f"❌ Failed to start messenger: {e}")
            QMessageBox.critical(self, "Start Error", f"Failed to start messenger:\n{e}")
    
    def stop_messenger(self):
        """Stop the messenger worker"""
        try:
            if self.worker:
                self.worker.stop()
                self.worker.wait(5000)  # Wait up to 5 seconds
                self.worker = None
            
            # Update UI
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.messenger_status_label.setText("❌ Stopped")
            self.messenger_status_label.setStyleSheet("font-weight: bold; color: #ef4444;")
            
            self.add_log("⏹️ WhatsApp Messenger stopped")
            
        except Exception as e:
            self.add_log(f"❌ Failed to stop messenger: {e}")
    
    def test_connection(self):
        """Test WhatsApp connection"""
        try:
            if not self.messenger:
                self.init_messenger()
                if not self.messenger:
                    return
            
            self.add_log("🧪 Testing WhatsApp connection...")
            
            if self.messenger.connect_to_whatsapp():
                self.add_log("✅ Connection test successful!")
                QMessageBox.information(self, "Connection Test", "✅ WhatsApp connection test successful!")
            else:
                self.add_log("❌ Connection test failed!")
                QMessageBox.warning(self, "Connection Test", "❌ WhatsApp connection test failed!")
                
        except Exception as e:
            self.add_log(f"❌ Connection test error: {e}")
            QMessageBox.critical(self, "Connection Test Error", f"Connection test failed:\n{e}")
    
    def update_status(self):
        """Update status display"""
        try:
            if not self.messenger:
                return
            
            status = self.messenger.get_status()
            
            # Update connection status
            if status['whatsapp_connected']:
                self.connection_status_label.setText("✅ Connected")
                self.connection_status_label.setStyleSheet("font-weight: bold; color: #10b981;")
            else:
                self.connection_status_label.setText("❌ Disconnected")
                self.connection_status_label.setStyleSheet("font-weight: bold; color: #ef4444;")
            
            # Update target group
            self.target_group_label.setText(status.get('target_group', 'Not Set'))
            
            # Update pending messages
            self.pending_messages_label.setText(str(status.get('pending_messages', 0)))
            
            # Update last check
            last_check = status.get('last_check', 'Never')
            if last_check != 'Never':
                try:
                    dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                    self.last_check_label.setText(dt.strftime('%Y-%m-%d %H:%M:%S'))
                except:
                    self.last_check_label.setText(last_check)
            else:
                self.last_check_label.setText('Never')
                
        except Exception as e:
            self.add_log(f"❌ Error updating status: {e}")
    
    def on_status_updated(self, status):
        """Handle status updates from worker thread"""
        # Update UI elements (this runs in main thread)
        self.update_status()
    
    def refresh_messages(self):
        """Refresh the messages table"""
        try:
            if not self.messenger:
                return
            
            messages = self.messenger.read_pending_messages()
            
            self.messages_table.setRowCount(len(messages))
            
            for row, message in enumerate(messages):
                self.messages_table.setItem(row, 0, QTableWidgetItem(message.get('timestamp', '')))
                self.messages_table.setItem(row, 1, QTableWidgetItem(message.get('message_type', '')))
                self.messages_table.setItem(row, 2, QTableWidgetItem(message.get('priority', '')))
                self.messages_table.setItem(row, 3, QTableWidgetItem(message.get('sent_status', '')))
                self.messages_table.setItem(row, 4, QTableWidgetItem(str(message.get('retry_count', 0))))
                
                # Truncate content for display
                content = message.get('content', '')
                if len(content) > 100:
                    content = content[:100] + "..."
                self.messages_table.setItem(row, 5, QTableWidgetItem(content))
            
            self.add_log(f"🔄 Refreshed messages table ({len(messages)} messages)")
            
        except Exception as e:
            self.add_log(f"❌ Error refreshing messages: {e}")
    
    def add_log(self, message):
        """Add a log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.clear()
        self.add_log("🗑️ Logs cleared")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Confirm Exit", 
                                       "Messenger is still running. Stop it before exiting?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.stop_messenger()
        
        event.accept()


def main():
    """Main function for GUI application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("WhatsApp Messenger GUI")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = WhatsAppMessengerGUI()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

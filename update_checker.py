#!/usr/bin/env python3
"""
Update checker widget for VARSYS Kitchen Dashboard
"""

import sys
import os
import webbrowser
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QProgressBar, QMessageBox,
                             QFrame, QApplication)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap

from version import version_manager, get_full_version

class UpdateCheckThread(QThread):
    """Thread for checking updates without blocking UI"""
    
    update_found = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)
    
    def run(self):
        try:
            has_update, release_info = version_manager.check_for_updates()
            if has_update:
                self.update_found.emit(release_info)
            else:
                self.no_update.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

class UpdateDialog(QDialog):
    """Dialog for displaying update information"""
    
    def __init__(self, release_info, parent=None):
        super().__init__(parent)
        self.release_info = release_info
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("VARSYS Kitchen Dashboard - Update Available")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #667eea;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("🎉 Update Available!")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        version_label = QLabel(f"New Version: {self.release_info['version']}")
        version_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                background: transparent;
            }
        """)
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_frame)
        
        # Current vs New version
        version_frame = QFrame()
        version_layout = QHBoxLayout(version_frame)
        
        current_label = QLabel(f"Current: {get_full_version()}")
        current_label.setStyleSheet("font-weight: bold; color: #666;")
        version_layout.addWidget(current_label)
        
        version_layout.addStretch()
        
        new_label = QLabel(f"Latest: {self.release_info['version']}")
        new_label.setStyleSheet("font-weight: bold; color: #059669;")
        version_layout.addWidget(new_label)
        
        layout.addWidget(version_frame)
        
        # Release notes
        notes_label = QLabel("Release Notes:")
        notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setPlainText(self.release_info.get('body', 'No release notes available.'))
        notes_text.setMaximumHeight(150)
        notes_text.setReadOnly(True)
        layout.addWidget(notes_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("Download Update")
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        download_btn.clicked.connect(self.download_update)
        button_layout.addWidget(download_btn)
        
        view_btn = QPushButton("View on GitHub")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
        """)
        view_btn.clicked.connect(self.view_on_github)
        button_layout.addWidget(view_btn)
        
        later_btn = QPushButton("Later")
        later_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        later_btn.clicked.connect(self.reject)
        button_layout.addWidget(later_btn)
        
        layout.addLayout(button_layout)
        
    def download_update(self):
        """Download the update"""
        try:
            download_url = self.release_info['download_url']
            webbrowser.open(download_url)
            
            QMessageBox.information(
                self,
                "Download Started",
                "The download has been started in your browser.\n\n"
                "Please save the file and run it to update the application."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Download Error",
                f"Failed to start download:\n{str(e)}"
            )
    
    def view_on_github(self):
        """Open GitHub release page"""
        try:
            webbrowser.open(self.release_info['html_url'])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open GitHub page:\n{str(e)}"
            )

class UpdateChecker:
    """Main update checker class"""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.check_thread = None
        
    def check_for_updates(self, show_no_update_message=False):
        """Check for updates asynchronously"""
        if self.check_thread and self.check_thread.isRunning():
            return
            
        self.show_no_update_message = show_no_update_message
        self.check_thread = UpdateCheckThread()
        self.check_thread.update_found.connect(self.on_update_found)
        self.check_thread.no_update.connect(self.on_no_update)
        self.check_thread.error_occurred.connect(self.on_error)
        self.check_thread.start()
    
    def on_update_found(self, release_info):
        """Handle when update is found"""
        dialog = UpdateDialog(release_info, self.parent)
        dialog.exec()
    
    def on_no_update(self):
        """Handle when no update is available"""
        if self.show_no_update_message:
            QMessageBox.information(
                self.parent,
                "No Updates",
                "You are running the latest version of VARSYS Kitchen Dashboard."
            )
    
    def on_error(self, error_message):
        """Handle update check errors"""
        if self.show_no_update_message:
            QMessageBox.warning(
                self.parent,
                "Update Check Failed",
                f"Failed to check for updates:\n{error_message}\n\n"
                "Please check your internet connection and try again."
            )

def create_update_menu_action(parent_widget):
    """Create a menu action for manual update checking"""
    def check_updates():
        checker = UpdateChecker(parent_widget)
        checker.check_for_updates(show_no_update_message=True)
    
    return check_updates

def auto_check_updates(parent_widget, delay_seconds=5):
    """Automatically check for updates after a delay"""
    def delayed_check():
        checker = UpdateChecker(parent_widget)
        checker.check_for_updates(show_no_update_message=False)
    
    # Use QTimer to delay the check
    timer = QTimer()
    timer.singleShot(delay_seconds * 1000, delayed_check)

if __name__ == "__main__":
    # Test the update checker
    app = QApplication(sys.argv)
    
    checker = UpdateChecker()
    checker.check_for_updates(show_no_update_message=True)
    
    sys.exit(app.exec())

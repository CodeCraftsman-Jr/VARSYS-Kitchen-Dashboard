"""
VARSYS Solutions - Kitchen Dashboard
Update Manager UI Component

Professional update management interface
"""

import os
import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QFrame, QMessageBox, QDialog,
    QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont, QIcon

from updater import get_updater
from varsys_branding import VARSYSBranding
from __version__ import get_version_info

class UpdateCheckThread(QThread):
    """Background thread for checking updates"""
    
    update_found = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, updater):
        super().__init__()
        self.updater = updater
    
    def run(self):
        """Check for updates in background"""
        try:
            update_info = self.updater.check_for_updates()
            if update_info:
                self.update_found.emit(update_info)
            else:
                self.no_update.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

class UpdateDownloadThread(QThread):
    """Background thread for downloading updates"""
    
    download_progress = Signal(int)
    download_completed = Signal(str)
    download_failed = Signal(str)
    
    def __init__(self, updater, update_info):
        super().__init__()
        self.updater = updater
        self.update_info = update_info
    
    def run(self):
        """Download update in background"""
        try:
            def progress_callback(percent):
                self.download_progress.emit(percent)
            
            file_path = self.updater.download_update(self.update_info, progress_callback)
            if file_path:
                self.download_completed.emit(file_path)
            else:
                self.download_failed.emit("Download failed")
        except Exception as e:
            self.download_failed.emit(str(e))

class UpdateDialog(QDialog):
    """Professional update dialog"""
    
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.updater = get_updater()
        
        self.setWindowTitle("Software Update Available")
        self.setFixedSize(600, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        self.apply_styling()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("🔄 Update Available")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_label.setStyleSheet(f"color: {VARSYSBranding.PRIMARY_COLOR};")
        layout.addWidget(header_label)
        
        # Version info
        version_frame = QFrame()
        version_layout = QVBoxLayout(version_frame)
        
        current_version = get_version_info()['version']
        new_version = self.update_info['version']
        
        version_text = f"""
        <p><strong>Current Version:</strong> {current_version}</p>
        <p><strong>New Version:</strong> <span style="color: {VARSYSBranding.SUCCESS_COLOR};">{new_version}</span></p>
        <p><strong>Release Date:</strong> {self.update_info.get('published_at', 'Unknown')}</p>
        """
        
        version_label = QLabel(version_text)
        version_label.setTextFormat(Qt.RichText)
        version_layout.addWidget(version_label)
        
        layout.addWidget(version_frame)
        
        # Release notes
        notes_group = QGroupBox("What's New")
        notes_layout = QVBoxLayout(notes_group)
        
        notes_text = QTextEdit()
        notes_text.setPlainText(self.update_info.get('body', 'No release notes available'))
        notes_text.setMaximumHeight(200)
        notes_text.setReadOnly(True)
        notes_layout.addWidget(notes_text)
        
        layout.addWidget(notes_group)
        
        # Auto-update checkbox
        self.auto_update_checkbox = QCheckBox("Automatically check for updates")
        self.auto_update_checkbox.setChecked(True)
        layout.addWidget(self.auto_update_checkbox)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Download & Install")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VARSYSBranding.SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:disabled {{
                background-color: #a0aec0;
            }}
        """)
        
        self.later_btn = QPushButton("Remind Me Later")
        self.later_btn.clicked.connect(self.remind_later)
        self.later_btn.setStyleSheet("""
            QPushButton {
                background-color: #e2e8f0;
                color: #4a5568;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #cbd5e0;
            }
        """)
        
        self.skip_btn = QPushButton("Skip This Version")
        self.skip_btn.clicked.connect(self.skip_version)
        self.skip_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VARSYSBranding.WARNING_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.later_btn)
        button_layout.addWidget(self.skip_btn)
        
        layout.addLayout(button_layout)
    
    def apply_styling(self):
        """Apply professional styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {VARSYSBranding.BACKGROUND};
                color: {VARSYSBranding.TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {VARSYSBranding.TEXT_SECONDARY};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QTextEdit {{
                border: 1px solid {VARSYSBranding.TEXT_SECONDARY};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }}
            QProgressBar {{
                border: 1px solid {VARSYSBranding.TEXT_SECONDARY};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {VARSYSBranding.SUCCESS_COLOR};
                border-radius: 3px;
            }}
        """)
    
    def start_download(self):
        """Start the download process"""
        self.download_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Downloading update...")
        
        # Start download thread
        self.download_thread = UpdateDownloadThread(self.updater, self.update_info)
        self.download_thread.download_progress.connect(self.update_progress)
        self.download_thread.download_completed.connect(self.download_completed)
        self.download_thread.download_failed.connect(self.download_failed)
        self.download_thread.start()
    
    def update_progress(self, percent):
        """Update download progress with method-specific messages"""
        self.progress_bar.setValue(percent)

        # Check if using Git or HTTP method
        download_method = getattr(self.update_info, 'download_method', 'http')

        if download_method == 'git':
            if percent < 70:
                self.status_label.setText(f"Syncing with Git repository... {percent}%")
            else:
                self.status_label.setText(f"Preparing update files... {percent}%")
        else:
            self.status_label.setText(f"Downloading update... {percent}%")
    
    def download_completed(self, file_path):
        """Handle download completion"""
        self.status_label.setText("Download completed! Installing...")
        
        # Install the update
        if self.updater.install_update(file_path):
            QMessageBox.information(
                self, 
                "Update Installed", 
                "The update has been installed successfully. The application will restart."
            )
            self.accept()
            # Application will restart automatically
        else:
            self.download_failed("Installation failed")
    
    def download_failed(self, error):
        """Handle download failure"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Download failed: {error}")
        
        # Re-enable buttons
        self.download_btn.setEnabled(True)
        self.later_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Download Failed", f"Failed to download update:\n{error}")
    
    def remind_later(self):
        """Remind later"""
        self.reject()
    
    def skip_version(self):
        """Skip this version"""
        # TODO: Save skipped version to avoid showing again
        self.reject()

class UpdateManager(QWidget):
    """Update manager widget for settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.updater = get_updater()
        self.init_ui()
        
        # Auto-check timer
        self.auto_check_timer = QTimer()
        self.auto_check_timer.timeout.connect(self.auto_check_updates)
        self.auto_check_timer.start(3600000)  # Check every hour
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Current version info
        version_group = QGroupBox("Current Version")
        version_layout = QVBoxLayout(version_group)
        
        version_info = get_version_info()
        version_text = f"""
        <p><strong>Version:</strong> {version_info['version']}</p>
        <p><strong>Build:</strong> {version_info['build']}</p>
        <p><strong>Release Type:</strong> {version_info['release_type']}</p>
        """
        
        version_label = QLabel(version_text)
        version_label.setTextFormat(Qt.RichText)
        version_layout.addWidget(version_label)
        
        layout.addWidget(version_group)
        
        # Update controls
        controls_group = QGroupBox("Update Settings")
        controls_layout = QVBoxLayout(controls_group)
        
        # Auto-update checkbox
        self.auto_update_checkbox = QCheckBox("Automatically check for updates")
        self.auto_update_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_update_checkbox)
        
        # Check now button
        check_btn = QPushButton("Check for Updates Now")
        check_btn.clicked.connect(self.manual_check_updates)
        check_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VARSYSBranding.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {VARSYSBranding.SECONDARY_COLOR};
            }}
        """)
        controls_layout.addWidget(check_btn)
        
        layout.addWidget(controls_group)
        
        # Status
        self.status_label = QLabel("Ready to check for updates")
        self.status_label.setStyleSheet(f"color: {VARSYSBranding.TEXT_SECONDARY};")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def auto_check_updates(self):
        """Automatically check for updates"""
        if self.auto_update_checkbox.isChecked() and self.updater.should_check_for_updates():
            self.check_for_updates(silent=True)
    
    def manual_check_updates(self):
        """Manually check for updates"""
        self.check_for_updates(silent=False)
    
    def check_for_updates(self, silent=False):
        """Check for updates"""
        if not silent:
            self.status_label.setText("Checking for updates...")
        
        # Start check thread
        self.check_thread = UpdateCheckThread(self.updater)
        self.check_thread.update_found.connect(lambda info: self.handle_update_found(info, silent))
        self.check_thread.no_update.connect(lambda: self.handle_no_update(silent))
        self.check_thread.error_occurred.connect(lambda error: self.handle_check_error(error, silent))
        self.check_thread.start()
    
    def handle_update_found(self, update_info, silent):
        """Handle update found"""
        self.status_label.setText(f"Update available: v{update_info['version']}")
        
        if not silent:
            dialog = UpdateDialog(update_info, self)
            dialog.exec()
    
    def handle_no_update(self, silent):
        """Handle no update available"""
        self.status_label.setText("You have the latest version")
        
        if not silent:
            QMessageBox.information(self, "No Updates", "You are running the latest version.")
    
    def handle_check_error(self, error, silent):
        """Handle check error"""
        self.status_label.setText("Error checking for updates")
        
        if not silent:
            QMessageBox.warning(self, "Update Check Failed", f"Failed to check for updates:\n{error}")

def get_update_manager(parent=None):
    """Get update manager instance"""
    return UpdateManager(parent)

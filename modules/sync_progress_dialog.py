"""
Sync Progress Dialog for Kitchen Dashboard
Provides comprehensive UI feedback for sync operations
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QTextEdit, QFrame,
                             QScrollArea, QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from datetime import datetime
import logging

class SyncProgressDialog(QDialog):
    """Modal dialog showing sync progress with detailed feedback"""
    
    # Signals
    cancel_requested = Signal(str)  # operation_id
    
    def __init__(self, operation_id: str, operation_type: str, parent=None):
        super().__init__(parent)
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.apply_styling()
        
        # Auto-close timer (safety mechanism)
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self.auto_close)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.start(300000)  # 5 minutes max
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(f"Cloud Sync - {self.operation_type.title()}")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Icon (you could add an actual icon here)
        icon_label = QLabel("☁️")
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        self.title_label = QLabel(f"Synchronizing Data ({self.operation_type.title()})")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_layout.addWidget(self.title_label)
        
        self.description_label = QLabel("Preparing synchronization...")
        self.description_label.setFont(QFont("Segoe UI", 10))
        self.description_label.setStyleSheet("color: #64748b;")
        title_layout.addWidget(self.description_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Progress section
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        
        # Main progress bar
        self.main_progress = QProgressBar()
        self.main_progress.setRange(0, 100)
        self.main_progress.setValue(0)
        self.main_progress.setTextVisible(True)
        self.main_progress.setFormat("%p% Complete")
        progress_layout.addWidget(self.main_progress)
        
        # Current step label
        self.step_label = QLabel("Initializing...")
        self.step_label.setFont(QFont("Segoe UI", 10))
        self.step_label.setStyleSheet("color: #374151; margin-top: 5px;")
        progress_layout.addWidget(self.step_label)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.time_label = QLabel("Elapsed: 00:00")
        self.time_label.setFont(QFont("Segoe UI", 9))
        self.time_label.setStyleSheet("color: #6b7280;")
        stats_layout.addWidget(self.time_label)
        
        stats_layout.addStretch()
        
        self.eta_label = QLabel("ETA: Calculating...")
        self.eta_label.setFont(QFont("Segoe UI", 9))
        self.eta_label.setStyleSheet("color: #6b7280;")
        stats_layout.addWidget(self.eta_label)
        
        progress_layout.addLayout(stats_layout)
        
        layout.addWidget(progress_frame)
        
        # Details section
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Box)
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(15, 10, 15, 15)
        
        details_header = QLabel("Sync Details")
        details_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        details_header.setStyleSheet("color: #374151; margin-bottom: 5px;")
        details_layout.addWidget(details_header)
        
        # Scrollable details area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(120)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setContentsMargins(5, 5, 5, 5)
        self.details_layout.setSpacing(2)
        
        scroll_area.setWidget(self.details_widget)
        details_layout.addWidget(scroll_area)
        
        layout.addWidget(details_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_sync)
        self.cancel_button.setMinimumWidth(100)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setMinimumWidth(100)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Timer for elapsed time
        self.start_time = datetime.now()
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)
        self.elapsed_timer.start(1000)  # Update every second
        
    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QProgressBar {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                border-radius: 6px;
            }
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
            QPushButton:disabled {
                background-color: #f9fafb;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
        """)
        
        # Special styling for cancel button
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                color: #dc2626;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                border-color: #fca5a5;
            }
        """)
        
        # Special styling for close button when enabled
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                color: #1d4ed8;
            }
            QPushButton:hover {
                background-color: #dbeafe;
                border-color: #93c5fd;
            }
            QPushButton:disabled {
                background-color: #f9fafb;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
        """)
    
    def update_progress(self, progress: int = None, step_text: str = None, records_processed: int = None, total_records: int = None, collection: str = None):
        """Update progress display with enhanced information"""
        try:
            # Update main progress bar
            if progress is not None:
                self.main_progress.setValue(max(0, min(100, progress)))

            # Update step text with collection info
            if step_text:
                if collection:
                    display_text = f"{step_text} ({collection})"
                else:
                    display_text = step_text
                self.step_label.setText(display_text)

            # Update records info with better formatting
            if records_processed is not None and total_records is not None:
                if total_records > 0:
                    percentage = (records_processed / total_records) * 100
                    if hasattr(self, 'records_label'):
                        self.records_label.setText(f"Records: {records_processed:,} / {total_records:,} ({percentage:.1f}%)")
                else:
                    if hasattr(self, 'records_label'):
                        self.records_label.setText(f"Records: {records_processed:,}")

            # Update ETA calculation with better accuracy
            current_progress = progress if progress is not None else self.main_progress.value()
            if current_progress > 5:  # Only estimate after 5% to avoid wild estimates
                elapsed = (datetime.now() - self.start_time).total_seconds()
                estimated_total = elapsed * (100 / current_progress)
                remaining = max(0, estimated_total - elapsed)

                if remaining > 0:
                    if remaining < 60:
                        eta_text = f"ETA: {int(remaining)}s"
                    else:
                        eta_text = f"ETA: {int(remaining // 60)}m {int(remaining % 60)}s"
                    self.eta_label.setText(eta_text)
                else:
                    self.eta_label.setText("ETA: Almost done")
            elif current_progress > 0:
                self.eta_label.setText("ETA: Calculating...")

            # Add detail entry with collection info
            if step_text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                if collection:
                    detail_text = f"[{timestamp}] {step_text} - {collection}"
                else:
                    detail_text = f"[{timestamp}] {step_text}"
                self.add_detail(detail_text)

            # Update window title with progress
            if current_progress > 0:
                self.setWindowTitle(f"Cloud Sync - {self.operation_type.title()} ({current_progress}%)")

            # Force UI update but limit frequency to prevent performance issues
            if not hasattr(self, '_last_ui_update') or (datetime.now() - getattr(self, '_last_ui_update', datetime.min)).total_seconds() > 0.1:
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()
                self._last_ui_update = datetime.now()

        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")

    def update_progress_legacy(self, progress: int, status: str):
        """Legacy update method for backward compatibility"""
        self.update_progress(progress=progress, step_text=status)
    
    def add_detail(self, detail: str):
        """Add a detail entry to the details area"""
        detail_label = QLabel(detail)
        detail_label.setFont(QFont("Consolas", 8))
        detail_label.setStyleSheet("color: #4b5563; padding: 1px;")
        detail_label.setWordWrap(True)
        
        self.details_layout.addWidget(detail_label)
        
        # Auto-scroll to bottom
        QTimer.singleShot(10, lambda: self.scroll_to_bottom())
    
    def scroll_to_bottom(self):
        """Scroll details area to bottom"""
        scroll_area = self.details_widget.parent().parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )
    
    def update_elapsed_time(self):
        """Update elapsed time display"""
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.time_label.setText(f"Elapsed: {minutes:02d}:{seconds:02d}")
    
    def sync_completed(self, success: bool, message: str):
        """Handle sync completion"""
        self.elapsed_timer.stop()
        self.auto_close_timer.stop()
        
        if success:
            self.main_progress.setValue(100)
            self.step_label.setText("✅ Sync completed successfully!")
            self.step_label.setStyleSheet("color: #059669; font-weight: bold;")
            self.add_detail(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {message}")
        else:
            self.step_label.setText("❌ Sync failed!")
            self.step_label.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.add_detail(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {message}")
        
        # Enable close button, disable cancel
        self.close_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # Auto-close after 3 seconds if successful
        if success:
            QTimer.singleShot(3000, self.accept)
    
    def cancel_sync(self):
        """Handle cancel button click"""
        self.cancel_requested.emit(self.operation_id)
        self.add_detail(f"[{datetime.now().strftime('%H:%M:%S')}] 🚫 Cancellation requested...")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
    
    def auto_close(self):
        """Auto-close dialog after timeout"""
        self.add_detail(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Auto-closing due to timeout")
        self.accept()
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self.elapsed_timer.stop()
        self.auto_close_timer.stop()
        super().closeEvent(event)

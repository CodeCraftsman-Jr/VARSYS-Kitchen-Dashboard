"""
Performance Monitor Widget
Real-time performance monitoring for Kitchen Dashboard
"""

import logging
import psutil
import time
from typing import Dict, List
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QProgressBar, QPushButton, QTextEdit, QGroupBox,
                              QGridLayout, QFrame)
from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QFont

class PerformanceCard(QFrame):
    """Performance metric card"""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", color: str = "#3b82f6"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin: 4px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: #64748b; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)
        
        # Unit
        if unit:
            unit_label = QLabel(unit)
            unit_label.setFont(QFont("Arial", 9))
            unit_label.setStyleSheet("color: #94a3b8;")
            layout.addWidget(unit_label)
    
    def update_value(self, value: str):
        """Update the displayed value"""
        self.value_label.setText(value)

class PerformanceMonitorWidget(QWidget):
    """Performance monitoring widget"""
    
    # Signals
    cleanup_requested = Signal()
    gc_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kitchen Dashboard - Performance Monitor")
        self.setGeometry(100, 100, 600, 500)
        
        self.logger = logging.getLogger(__name__)
        
        # Performance data
        self.cpu_history = []
        self.memory_history = []
        self.max_history = 60  # Keep 60 data points
        
        # Setup UI
        self.setup_ui()
        
        # Setup monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_metrics)
        self.monitor_timer.start(1000)  # Update every second
        
        # Initial update
        self.update_metrics()
    
    def setup_ui(self):
        """Setup the monitoring UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Performance Monitor")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Metrics cards
        self.create_metrics_section(layout)
        
        # Progress bars
        self.create_progress_section(layout)
        
        # Control buttons
        self.create_controls_section(layout)
        
        # Log area
        self.create_log_section(layout)
    
    def create_metrics_section(self, parent_layout):
        """Create metrics cards section"""
        metrics_group = QGroupBox("System Metrics")
        metrics_layout = QGridLayout(metrics_group)
        metrics_layout.setSpacing(12)
        
        # Create metric cards
        self.cpu_card = PerformanceCard("CPU Usage", "0", "%", "#ef4444")
        self.memory_card = PerformanceCard("Memory Usage", "0", "MB", "#f59e0b")
        self.memory_percent_card = PerformanceCard("Memory %", "0", "%", "#10b981")
        self.threads_card = PerformanceCard("Active Threads", "0", "", "#8b5cf6")
        
        # Add to grid
        metrics_layout.addWidget(self.cpu_card, 0, 0)
        metrics_layout.addWidget(self.memory_card, 0, 1)
        metrics_layout.addWidget(self.memory_percent_card, 1, 0)
        metrics_layout.addWidget(self.threads_card, 1, 1)
        
        parent_layout.addWidget(metrics_group)
    
    def create_progress_section(self, parent_layout):
        """Create progress bars section"""
        progress_group = QGroupBox("Resource Usage")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(12)
        
        # CPU progress
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                background-color: #f3f4f6;
            }
            QProgressBar::chunk {
                background-color: #ef4444;
                border-radius: 3px;
            }
        """)
        cpu_layout.addWidget(self.cpu_progress)
        progress_layout.addLayout(cpu_layout)
        
        # Memory progress
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory:"))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                background-color: #f3f4f6;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 3px;
            }
        """)
        memory_layout.addWidget(self.memory_progress)
        progress_layout.addLayout(memory_layout)
        
        parent_layout.addWidget(progress_group)
    
    def create_controls_section(self, parent_layout):
        """Create control buttons section"""
        controls_layout = QHBoxLayout()
        
        # Garbage collection button
        gc_btn = QPushButton("Force Garbage Collection")
        gc_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        gc_btn.clicked.connect(self.force_garbage_collection)
        controls_layout.addWidget(gc_btn)
        
        # Clear caches button
        clear_btn = QPushButton("Clear Caches")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        clear_btn.clicked.connect(self.clear_caches)
        controls_layout.addWidget(clear_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Now")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        refresh_btn.clicked.connect(self.update_metrics)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        parent_layout.addLayout(controls_layout)
    
    def create_log_section(self, parent_layout):
        """Create log display section"""
        log_group = QGroupBox("Performance Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: #f9fafb;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        parent_layout.addWidget(log_group)
    
    def update_metrics(self):
        """Update performance metrics"""
        try:
            # Get system metrics
            process = psutil.Process()
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            self.cpu_card.update_value(f"{cpu_percent:.1f}")
            self.cpu_progress.setValue(int(cpu_percent))
            
            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.memory_card.update_value(f"{memory_mb:.1f}")
            
            # System memory percentage
            system_memory = psutil.virtual_memory()
            memory_percent = system_memory.percent
            self.memory_percent_card.update_value(f"{memory_percent:.1f}")
            self.memory_progress.setValue(int(memory_percent))
            
            # Thread count
            thread_count = process.num_threads()
            self.threads_card.update_value(str(thread_count))
            
            # Update history
            self.cpu_history.append(cpu_percent)
            self.memory_history.append(memory_percent)
            
            # Keep history size manageable
            if len(self.cpu_history) > self.max_history:
                self.cpu_history.pop(0)
            if len(self.memory_history) > self.max_history:
                self.memory_history.pop(0)
            
            # Log high usage
            if cpu_percent > 80:
                self.log_message(f"⚠️ High CPU usage: {cpu_percent:.1f}%", "warning")
            if memory_percent > 85:
                self.log_message(f"⚠️ High memory usage: {memory_percent:.1f}%", "warning")
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
            self.log_message(f"❌ Error updating metrics: {e}", "error")
    
    def log_message(self, message: str, level: str = "info"):
        """Add message to performance log"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "info": "#60a5fa",
            "warning": "#fbbf24", 
            "error": "#f87171",
            "success": "#34d399"
        }
        
        color = colors.get(level, "#f9fafb")
        
        formatted_message = f'<span style="color: {color}">[{timestamp}] {message}</span>'
        self.log_text.append(formatted_message)
        
        # Keep log size manageable
        if self.log_text.document().blockCount() > 100:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 10)
            cursor.removeSelectedText()
    
    def force_garbage_collection(self):
        """Force garbage collection"""
        try:
            import gc
            collected = gc.collect()
            self.log_message(f"✅ Garbage collection freed {collected} objects", "success")
            self.gc_requested.emit()
        except Exception as e:
            self.log_message(f"❌ Garbage collection failed: {e}", "error")
    
    def clear_caches(self):
        """Clear application caches"""
        try:
            from PySide6.QtGui import QPixmap
            QPixmap.clearCache()
            self.log_message("✅ Caches cleared successfully", "success")
            self.cleanup_requested.emit()
        except Exception as e:
            self.log_message(f"❌ Cache clearing failed: {e}", "error")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        try:
            process = psutil.Process()
            
            return {
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': psutil.virtual_memory().percent,
                'thread_count': process.num_threads(),
                'cpu_avg': sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0,
                'memory_avg': sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}
    
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'monitor_timer'):
            self.monitor_timer.stop()
        event.accept()

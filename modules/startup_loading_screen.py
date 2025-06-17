"""
Kitchen Dashboard - Startup Loading Screen
Professional loading screen with progress indicators during application initialization
"""

import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QProgressBar, QApplication, QSplashScreen)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QBrush
import time


class LoadingWorker(QThread):
    """Worker thread for simulating loading operations"""
    progress_updated = Signal(int, str)
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.loading_steps = [
            (10, "Initializing application..."),
            (20, "Loading configuration..."),
            (30, "Setting up Firebase connection..."),
            (40, "Initializing user interface..."),
            (50, "Loading modules..."),
            (60, "Setting up authentication..."),
            (70, "Preparing data structures..."),
            (80, "Finalizing setup..."),
            (90, "Almost ready..."),
            (100, "Application ready!")
        ]
    
    def run(self):
        """Simulate loading process"""
        for progress, message in self.loading_steps:
            self.progress_updated.emit(progress, message)
            # Simulate work being done
            time.sleep(0.5)  # Adjust timing as needed
        
        self.finished.emit()


class StartupLoadingScreen(QSplashScreen):
    """Professional startup loading screen with progress indicators"""
    
    loading_finished = Signal()
    
    def __init__(self):
        # Create a custom pixmap for the splash screen
        pixmap = self.create_splash_pixmap()
        super().__init__(pixmap)
        
        # Set window flags
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        
        # Initialize UI components
        self.setup_ui()
        
        # Initialize worker thread
        self.worker = LoadingWorker()
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_loading_finished)
        
        # Start loading
        self.start_loading()
    
    def create_splash_pixmap(self):
        """Create a custom splash screen pixmap"""
        width, height = 600, 400
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(255, 255, 255))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(41, 128, 185))  # Blue
        gradient.setColorAt(1, QColor(52, 73, 94))    # Dark blue
        
        painter.fillRect(pixmap.rect(), QBrush(gradient))
        
        # Draw title
        painter.setPen(QColor(255, 255, 255))
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter | Qt.AlignTop, 
                        "VARSYS Kitchen Dashboard")
        
        # Draw subtitle
        subtitle_font = QFont("Segoe UI", 12)
        painter.setFont(subtitle_font)
        painter.drawText(50, height - 100, width - 100, 30, 
                        Qt.AlignCenter, "Professional Kitchen Management System")
        
        # Draw version
        version_font = QFont("Segoe UI", 10)
        painter.setFont(version_font)
        painter.drawText(50, height - 70, width - 100, 20, 
                        Qt.AlignCenter, "Version 1.1.3")
        
        painter.end()
        return pixmap
    
    def setup_ui(self):
        """Setup UI components on the splash screen"""
        # Progress bar will be drawn manually in drawContents
        self._progress_value = 0
        self.status_message = "Initializing..."
    
    def drawContents(self, painter):
        """Draw custom content on the splash screen"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get splash screen dimensions
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # Draw progress bar background
        progress_rect_bg = rect.adjusted(50, height - 50, -50, -20)
        painter.fillRect(progress_rect_bg, QColor(255, 255, 255, 100))
        
        # Draw progress bar
        progress_width = int((width - 100) * (self._progress_value / 100))
        progress_rect = rect.adjusted(50, height - 50, -50 - (width - 100 - progress_width), -20)
        
        # Progress bar gradient
        progress_gradient = QLinearGradient(progress_rect.topLeft(), progress_rect.topRight())
        progress_gradient.setColorAt(0, QColor(46, 204, 113))  # Green
        progress_gradient.setColorAt(1, QColor(39, 174, 96))   # Darker green
        
        painter.fillRect(progress_rect, QBrush(progress_gradient))
        
        # Draw status message
        painter.setPen(QColor(255, 255, 255))
        status_font = QFont("Segoe UI", 11)
        painter.setFont(status_font)
        painter.drawText(50, height - 80, width - 100, 20, 
                        Qt.AlignLeft | Qt.AlignVCenter, self.status_message)
        
        # Draw percentage
        painter.drawText(50, height - 80, width - 100, 20,
                        Qt.AlignRight | Qt.AlignVCenter, f"{self._progress_value}%")
    
    def start_loading(self):
        """Start the loading process"""
        self.show()
        self.worker.start()
    
    def update_progress(self, value, message):
        """Update progress bar and status message"""
        self.status_message = message
        self._progress_value = value

        # Force repaint
        self.repaint()
    
    def on_loading_finished(self):
        """Handle loading completion"""
        QTimer.singleShot(1000, self.finish_loading)  # Show "ready" for 1 second
    
    def finish_loading(self):
        """Finish loading and emit signal"""
        self.loading_finished.emit()
        self.close()
    



class SimpleLoadingDialog(QWidget):
    """Simple loading dialog as fallback"""
    
    loading_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitchen Dashboard - Loading")
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.setup_ui()
        self.start_loading()
    
    def setup_ui(self):
        """Setup simple loading UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("VARSYS Kitchen Dashboard")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Status message
        self.status_label = QLabel("Initializing application...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Version info
        version_label = QLabel("Version 1.1.3")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(version_label)
        
        # Apply window styling
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
        """)
    
    def start_loading(self):
        """Start loading simulation"""
        self.worker = LoadingWorker()
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.on_loading_finished)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Update progress"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def on_loading_finished(self):
        """Handle loading completion"""
        QTimer.singleShot(1000, self.finish_loading)
    
    def finish_loading(self):
        """Finish loading"""
        self.loading_finished.emit()
        self.close()


def show_startup_loading_screen():
    """Show startup loading screen and return it"""
    try:
        # Try to use the advanced splash screen
        loading_screen = StartupLoadingScreen()
        return loading_screen
    except Exception as e:
        print(f"Failed to create advanced loading screen: {e}")
        # Fallback to simple dialog
        loading_screen = SimpleLoadingDialog()
        return loading_screen


if __name__ == "__main__":
    # Test the loading screen
    app = QApplication(sys.argv)
    
    loading_screen = show_startup_loading_screen()
    loading_screen.loading_finished.connect(app.quit)
    
    sys.exit(app.exec())

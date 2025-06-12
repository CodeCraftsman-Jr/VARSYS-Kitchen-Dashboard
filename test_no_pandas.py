#!/usr/bin/env python3
"""
Test script without pandas to confirm it's the issue
"""

import sys
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class TestNoPandasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Test Without Pandas")
        self.resize(400, 300)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("This app works without pandas!")
        layout.addWidget(label)
        
        time_label = QLabel(f"Current time: {datetime.now()}")
        layout.addWidget(time_label)

def main():
    app = QApplication(sys.argv)
    window = TestNoPandasApp()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

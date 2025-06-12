#!/usr/bin/env python3
"""
Test script with only pandas to isolate the issue
"""

import sys
import pandas as pd
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class TestPandasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Test Pandas Only")
        self.resize(400, 300)
        
        # Create simple DataFrame
        data = {'Name': ['Test1', 'Test2'], 'Value': [1, 2]}
        df = pd.DataFrame(data)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        label = QLabel(f"Pandas DataFrame created with {len(df)} rows")
        layout.addWidget(label)
        
        info_label = QLabel(f"Pandas version: {pd.__version__}")
        layout.addWidget(info_label)

def main():
    app = QApplication(sys.argv)
    window = TestPandasApp()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

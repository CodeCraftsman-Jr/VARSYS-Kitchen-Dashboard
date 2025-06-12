#!/usr/bin/env python3
"""
Simple test script for PyInstaller
"""

import sys
import os

def main():
    print("Hello from VARSYS Kitchen Dashboard!")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Simple GUI test
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setWindowTitle("VARSYS Test")
        msg.setText("PyInstaller build successful!")
        msg.exec()
        
    except ImportError:
        print("PySide6 not available, running in console mode")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

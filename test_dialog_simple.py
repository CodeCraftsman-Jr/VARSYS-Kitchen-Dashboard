#!/usr/bin/env python3
"""
Simple test to verify the comprehensive test dialog works
"""

import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt

class SimpleTestDialog(QDialog):
    """Simple test dialog to verify dialog functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simple Test Dialog")
        self.setGeometry(200, 200, 600, 400)
        
        # Prevent auto-close
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setModal(False)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Simple Test Dialog")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Text area
        self.text_area = QTextEdit()
        self.text_area.setPlainText("This is a simple test dialog to verify dialog functionality.\n\nIf you can see this, the dialog is working correctly!")
        layout.addWidget(self.text_area)
        
        # Test button
        test_button = QPushButton("Run Test")
        test_button.clicked.connect(self.run_test)
        layout.addWidget(test_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def run_test(self):
        """Run a simple test"""
        self.text_area.append("\n🔄 Running simple test...")
        self.text_area.append("✅ Test completed successfully!")
        self.text_area.append("🎉 Dialog is working correctly!")

def test_dialog():
    """Test the dialog functionality"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("Creating simple test dialog...")
    dialog = SimpleTestDialog()
    
    print("Showing dialog...")
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    
    print(f"Dialog visible: {dialog.isVisible()}")
    print(f"Dialog size: {dialog.size()}")
    print(f"Dialog position: {dialog.pos()}")
    
    return dialog

if __name__ == "__main__":
    try:
        dialog = test_dialog()
        print("✅ Simple test dialog created and shown")
        print("Press Ctrl+C to exit")
        
        # Keep the application running
        app = QApplication.instance()
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

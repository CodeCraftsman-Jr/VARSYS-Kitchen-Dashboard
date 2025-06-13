#!/usr/bin/env python3
"""
Simple test to verify basic Qt column resizing functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PySide6.QtCore import Qt

class BasicResizeTest(QMainWindow):
    """Simple test window for basic column resizing"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Column Resize Test")
        self.setGeometry(100, 100, 800, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("Basic Column Resize Test")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Add instructions
        instructions = QLabel(
            "Instructions:\n"
            "1. Move your mouse to the column borders in the header\n"
            "2. You should see the resize cursor (↔)\n"
            "3. Click and drag to resize columns\n"
            "4. This tests basic Qt functionality without any custom code"
        )
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f9ff; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Create simple table
        self.table = QTableWidget(5, 4)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3", "Column 4"])
        
        # Add some test data
        for row in range(5):
            for col in range(4):
                item = QTableWidgetItem(f"Row {row+1}, Col {col+1}")
                self.table.setItem(row, col, item)
        
        # BASIC SETUP - Just set Interactive mode
        header = self.table.horizontalHeader()
        
        print("🔧 Setting up basic column resizing...")
        
        # Set all columns to Interactive mode
        for col in range(4):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Column {col}: Interactive mode set")
        
        # Basic configuration
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(50)
        
        # Test the setup
        print("🔧 Testing setup...")
        for col in range(4):
            mode = header.sectionResizeMode(col)
            print(f"   Column {col} mode: {mode} (1=Interactive)")
        
        layout.addWidget(self.table)
        
        # Add status
        status = QLabel("✅ Basic table setup complete. Try resizing columns!")
        status.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
        layout.addWidget(status)
        
        print("✅ Basic resize test window ready!")

def main():
    """Main function to run the basic test"""
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = BasicResizeTest()
    window.show()
    
    print("🔧 Basic resize test started. Try resizing columns in the table!")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

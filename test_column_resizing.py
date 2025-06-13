#!/usr/bin/env python3
"""
Test script to verify column resizing functionality with proper cursor support
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import Qt

# Import our enhanced table utilities
try:
    from utils.resizable_header import create_enhanced_table_with_resizing
    from utils.table_styling import apply_enhanced_table_styling_with_resize_cursor
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    print("⚠️ Enhanced resizing utilities not available")

class ColumnResizeTestWindow(QMainWindow):
    """Test window for column resizing functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Column Resizing Test - Kitchen Dashboard")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("Column Resizing Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Add instructions
        instructions = QLabel(
            "Instructions:\n"
            "1. Hover your mouse over the column borders in the table header\n"
            "2. Look for the resize cursor (↔) to appear\n"
            "3. Click and drag to resize columns\n"
            "4. Test with different columns to ensure all are resizable"
        )
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f9ff; border-radius: 5px;")
        layout.addWidget(instructions)
        
        if ENHANCED_AVAILABLE:
            # Create enhanced table with resizing
            self.test_table = create_enhanced_table_with_resizing(
                parent=self,
                column_headers=[
                    "ID", "Item Name", "Category", "Quantity", "Unit", 
                    "Price", "Total Value", "Location", "Status"
                ]
            )
            
            # Apply enhanced styling
            apply_enhanced_table_styling_with_resize_cursor(self.test_table)
            
            # Add some test data
            self.populate_test_data()
            
            layout.addWidget(self.test_table)
            
            # Add status label
            status = QLabel("✅ Enhanced column resizing is active! Hover over column borders to see resize cursor.")
            status.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
            layout.addWidget(status)
            
        else:
            # Fallback message
            error_label = QLabel("❌ Enhanced resizing utilities not available. Please check imports.")
            error_label.setStyleSheet("color: red; font-weight: bold; margin: 20px;")
            layout.addWidget(error_label)
        
        # Add test button
        test_button = QPushButton("Test Column Resizing")
        test_button.clicked.connect(self.test_resizing)
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        layout.addWidget(test_button)
    
    def populate_test_data(self):
        """Add test data to the table"""
        if not hasattr(self, 'test_table'):
            return
            
        test_data = [
            ["1", "Rice", "Grains", "50", "kg", "₹45.00", "₹2,250.00", "Storage A", "Available"],
            ["2", "Wheat Flour", "Flour", "25", "kg", "₹38.00", "₹950.00", "Storage B", "Low Stock"],
            ["3", "Cooking Oil", "Oil", "10", "L", "₹120.00", "₹1,200.00", "Kitchen", "Available"],
            ["4", "Salt", "Spices", "5", "kg", "₹20.00", "₹100.00", "Pantry", "Available"],
            ["5", "Sugar", "Sweeteners", "15", "kg", "₹42.00", "₹630.00", "Storage A", "Available"],
        ]
        
        self.test_table.setRowCount(len(test_data))
        
        for row, row_data in enumerate(test_data):
            for col, cell_data in enumerate(row_data):
                from PySide6.QtWidgets import QTableWidgetItem
                item = QTableWidgetItem(str(cell_data))
                self.test_table.setItem(row, col, item)
    
    def test_resizing(self):
        """Test the resizing functionality"""
        if not hasattr(self, 'test_table'):
            return
            
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Column Resizing Test")
        msg.setText("Column Resizing Test Instructions")
        msg.setInformativeText(
            "To test column resizing:\n\n"
            "1. Move your mouse slowly over the column header borders\n"
            "2. Watch for the cursor to change to a resize cursor (↔)\n"
            "3. When you see the resize cursor, click and drag to resize\n"
            "4. Try resizing different columns\n"
            "5. Check that the cursor changes back to normal when not over borders\n\n"
            "If the resize cursor doesn't appear, there may be an issue with the implementation."
        )
        msg.setIcon(QMessageBox.Information)
        msg.exec()


def main():
    """Main function to run the test"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show test window
    window = ColumnResizeTestWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

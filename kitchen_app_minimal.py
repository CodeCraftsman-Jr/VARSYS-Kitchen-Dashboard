#!/usr/bin/env python3
"""
Minimal Kitchen Dashboard App for PyInstaller
This version excludes problematic modules to ensure successful compilation
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set matplotlib to use PySide6
import matplotlib
matplotlib.use('QtAgg')

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLabel,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
                             QFrame, QTableWidget, QTableWidgetItem, QComboBox,
                             QLineEdit, QScrollArea, QMessageBox, QSplitter,
                             QFileDialog, QHeaderView, QGroupBox, QFormLayout,
                             QStyleFactory, QSizePolicy, QStackedWidget)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush

class MinimalKitchenDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("VARSYS Kitchen Dashboard - Minimal Edition")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Set window icon
        self.setWindowIcon(self.create_window_icon())
        
        # Initialize data
        self.data = self.load_basic_data()
        
        # Setup UI
        self.setup_ui()
        
        # Apply basic styling
        self.apply_basic_style()
        
    def create_window_icon(self):
        """Create a simple window icon"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(102, 126, 234))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(8, 12, 16, 12)
        painter.drawEllipse(10, 8, 12, 8)
        painter.end()
        
        return QIcon(pixmap)
    
    def load_basic_data(self):
        """Load basic data from CSV files"""
        data = {}
        data_dir = "data"
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Try to load basic CSV files
        csv_files = ['inventory.csv', 'expenses.csv', 'sales.csv']
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            try:
                if os.path.exists(file_path):
                    data[csv_file.replace('.csv', '')] = pd.read_csv(file_path)
                else:
                    # Create empty DataFrame with basic structure
                    if csv_file == 'inventory.csv':
                        data['inventory'] = pd.DataFrame(columns=['Item', 'Quantity', 'Unit', 'Category'])
                    elif csv_file == 'expenses.csv':
                        data['expenses'] = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
                    elif csv_file == 'sales.csv':
                        data['sales'] = pd.DataFrame(columns=['Date', 'Item', 'Quantity', 'Price', 'Total'])
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")
                data[csv_file.replace('.csv', '')] = pd.DataFrame()
        
        return data
    
    def setup_ui(self):
        """Setup the main UI"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.add_dashboard_tab()
        self.add_inventory_tab()
        self.add_expenses_tab()
        self.add_sales_tab()
        
    def create_header(self):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #667eea;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("VARSYS Kitchen Dashboard")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status
        status_label = QLabel(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                background: transparent;
            }
        """)
        header_layout.addWidget(status_label)
        
        return header_frame
    
    def add_dashboard_tab(self):
        """Add dashboard overview tab"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Welcome message
        welcome_label = QLabel("Welcome to VARSYS Kitchen Dashboard")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(welcome_label)
        
        # Stats grid
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        
        # Sample stats
        stats = [
            ("Total Items", len(self.data.get('inventory', pd.DataFrame()))),
            ("Total Expenses", f"₹{self.data.get('expenses', pd.DataFrame()).get('Amount', pd.Series()).sum():.2f}"),
            ("Total Sales", f"₹{self.data.get('sales', pd.DataFrame()).get('Total', pd.Series()).sum():.2f}"),
            ("Active Categories", len(self.data.get('inventory', pd.DataFrame()).get('Category', pd.Series()).unique()) if not self.data.get('inventory', pd.DataFrame()).empty else 0)
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_widget = self.create_stat_widget(label, str(value))
            stats_layout.addWidget(stat_widget, i // 2, i % 2)
        
        layout.addWidget(stats_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard_widget, "Dashboard")
    
    def create_stat_widget(self, label, value):
        """Create a stat display widget"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #667eea;")
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 12px; color: #64748b;")
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return widget
    
    def add_inventory_tab(self):
        """Add inventory management tab"""
        inventory_widget = QWidget()
        layout = QVBoxLayout(inventory_widget)
        
        # Header
        header_label = QLabel("Inventory Management")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Table
        table = QTableWidget()
        inventory_df = self.data.get('inventory', pd.DataFrame())
        
        if not inventory_df.empty:
            table.setRowCount(len(inventory_df))
            table.setColumnCount(len(inventory_df.columns))
            table.setHorizontalHeaderLabels(inventory_df.columns.tolist())
            
            for i, row in inventory_df.iterrows():
                for j, value in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(value)))
        else:
            table.setRowCount(1)
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['Item', 'Quantity', 'Unit', 'Category'])
            table.setItem(0, 0, QTableWidgetItem("No data available"))
        
        layout.addWidget(table)
        self.tab_widget.addTab(inventory_widget, "Inventory")
    
    def add_expenses_tab(self):
        """Add expenses tracking tab"""
        expenses_widget = QWidget()
        layout = QVBoxLayout(expenses_widget)
        
        header_label = QLabel("Expense Tracking")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Simple expenses display
        expenses_df = self.data.get('expenses', pd.DataFrame())
        if not expenses_df.empty:
            total_label = QLabel(f"Total Expenses: ₹{expenses_df.get('Amount', pd.Series()).sum():.2f}")
            total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc2626;")
            layout.addWidget(total_label)
        
        layout.addStretch()
        self.tab_widget.addTab(expenses_widget, "Expenses")
    
    def add_sales_tab(self):
        """Add sales tracking tab"""
        sales_widget = QWidget()
        layout = QVBoxLayout(sales_widget)
        
        header_label = QLabel("Sales Tracking")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Simple sales display
        sales_df = self.data.get('sales', pd.DataFrame())
        if not sales_df.empty:
            total_label = QLabel(f"Total Sales: ₹{sales_df.get('Total', pd.Series()).sum():.2f}")
            total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #059669;")
            layout.addWidget(total_label)
        
        layout.addStretch()
        self.tab_widget.addTab(sales_widget, "Sales")
    
    def apply_basic_style(self):
        """Apply basic styling to the application"""
        style = """
            QMainWindow {
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #667eea;
                color: white;
            }
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: #ffffff;
                alternate-background-color: #f8fafc;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 8px;
                border: 1px solid #e2e8f0;
                font-weight: bold;
            }
        """
        self.setStyleSheet(style)

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("VARSYS Kitchen Dashboard")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VARSYS")
    
    # Create and show main window
    window = MinimalKitchenDashboard()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

"""
Inventory Data Viewer Module
Shows exactly what inventory data is available for pricing calculations
"""

import os
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGroupBox, QTextEdit, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

class InventoryDataViewer(QWidget):
    """Widget to display available inventory data for pricing"""
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.inventory_file = os.path.join('data', 'inventory.csv')
        self.init_ui()
        self.load_inventory_data()
        
        # Auto-refresh every 30 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_inventory_data)
        self.refresh_timer.start(30000)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Available Inventory Data for Pricing")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #28a745;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.load_inventory_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Info box
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        
        info_label = QLabel("✅ <b>Pricing Source:</b> Only items shown below are used for pricing calculations.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #155724; font-size: 14px;")
        info_layout.addWidget(info_label)
        
        source_label = QLabel("📊 <b>Data Source:</b> inventory.csv file - no other sources are used for pricing.")
        source_label.setWordWrap(True)
        source_label.setStyleSheet("color: #155724; font-size: 14px; margin-top: 5px;")
        info_layout.addWidget(source_label)
        
        layout.addWidget(info_box)
        
        # Inventory data table
        self.create_inventory_table(layout)
        
        # Summary section
        self.create_summary_section(layout)
    
    def create_inventory_table(self, parent_layout):
        """Create the inventory data table"""
        table_group = QGroupBox("Available Inventory Items with Pricing Data")
        table_layout = QVBoxLayout(table_group)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item ID", "Item Name", "Category", "Quantity", "Unit", 
            "Price per Unit", "Average Price", "Total Value"
        ])
        
        # Modern table styling
        self.inventory_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                selection-background-color: #e6f7ff;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 13px;
                color: #374151;
            }
        """)
        
        # Set column widths
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Item ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Item Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Unit
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Price per Unit
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Average Price
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Total Value
        
        table_layout.addWidget(self.inventory_table)
        parent_layout.addWidget(table_group)
    
    def create_summary_section(self, parent_layout):
        """Create summary section"""
        summary_group = QGroupBox("Inventory Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_label = QLabel("Loading inventory data...")
        self.summary_label.setStyleSheet("font-size: 14px; color: #6c757d; padding: 10px;")
        summary_layout.addWidget(self.summary_label)
        
        parent_layout.addWidget(summary_group)
    
    def load_inventory_data(self):
        """Load and display inventory data"""
        try:
            if not os.path.exists(self.inventory_file):
                self.inventory_table.setRowCount(0)
                self.summary_label.setText("❌ No inventory.csv file found. No pricing data available.")
                self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px; font-weight: 500;")
                return
            
            # Load inventory data
            inventory_df = pd.read_csv(self.inventory_file)
            
            if inventory_df.empty:
                self.inventory_table.setRowCount(0)
                self.summary_label.setText("❌ Inventory file is empty. No pricing data available.")
                self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px; font-weight: 500;")
                return
            
            # Filter only items with pricing data
            pricing_items = inventory_df[
                (pd.notna(inventory_df.get('price_per_unit', pd.Series()))) | 
                (pd.notna(inventory_df.get('avg_price', pd.Series())))
            ]
            
            # Populate table
            self.inventory_table.setRowCount(len(pricing_items))
            
            total_items = 0
            total_value = 0.0
            categories = set()
            
            for row, (_, item) in enumerate(pricing_items.iterrows()):
                # Item ID
                item_id = item.get('item_id', 'N/A')
                self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
                
                # Item Name
                item_name = item.get('item_name', 'Unknown')
                name_item = QTableWidgetItem(item_name)
                name_item.setFont(QFont("", 0, QFont.Bold))
                name_item.setForeground(QColor("#2563eb"))
                self.inventory_table.setItem(row, 1, name_item)
                
                # Category
                category = item.get('category', 'Unknown')
                categories.add(category)
                self.inventory_table.setItem(row, 2, QTableWidgetItem(category))
                
                # Quantity
                quantity = item.get('quantity', 0)
                self.inventory_table.setItem(row, 3, QTableWidgetItem(f"{quantity}"))
                
                # Unit
                unit = item.get('unit', 'N/A')
                self.inventory_table.setItem(row, 4, QTableWidgetItem(unit))
                
                # Price per Unit
                price_per_unit = item.get('price_per_unit', None)
                if pd.notna(price_per_unit):
                    price_item = QTableWidgetItem(f"₹{float(price_per_unit):.2f}")
                    price_item.setForeground(QColor("#28a745"))
                    price_item.setFont(QFont("", 0, QFont.Bold))
                else:
                    price_item = QTableWidgetItem("N/A")
                    price_item.setForeground(QColor("#6c757d"))
                self.inventory_table.setItem(row, 5, price_item)
                
                # Average Price
                avg_price = item.get('avg_price', None)
                if pd.notna(avg_price):
                    avg_item = QTableWidgetItem(f"₹{float(avg_price):.2f}")
                    avg_item.setForeground(QColor("#17a2b8"))
                    avg_item.setFont(QFont("", 0, QFont.Bold))
                else:
                    avg_item = QTableWidgetItem("N/A")
                    avg_item.setForeground(QColor("#6c757d"))
                self.inventory_table.setItem(row, 6, avg_item)
                
                # Total Value
                total_val = item.get('total_value', None)
                if pd.notna(total_val):
                    total_item = QTableWidgetItem(f"₹{float(total_val):.2f}")
                    total_item.setForeground(QColor("#dc3545"))
                    total_item.setFont(QFont("", 0, QFont.Bold))
                    total_value += float(total_val)
                else:
                    total_item = QTableWidgetItem("N/A")
                    total_item.setForeground(QColor("#6c757d"))
                self.inventory_table.setItem(row, 7, total_item)
                
                total_items += 1
            
            # Update summary
            summary_text = f"✅ <b>{total_items}</b> items available for pricing calculations.\n"
            summary_text += f"📊 Categories: {', '.join(sorted(categories))}\n"
            summary_text += f"💰 Total Inventory Value: <b>₹{total_value:.2f}</b>\n"
            summary_text += f"📁 Data Source: {self.inventory_file}"
            
            self.summary_label.setText(summary_text)
            self.summary_label.setStyleSheet("font-size: 14px; color: #28a745; padding: 10px;")
            
        except Exception as e:
            self.summary_label.setText(f"Error loading inventory data: {e}")
            self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px;")

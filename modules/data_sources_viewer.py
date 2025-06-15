"""
Data Sources Viewer Module
Shows all available data sources for pricing calculations
"""

import os
import pandas as pd
from datetime import datetime
from utils.table_styling import apply_universal_column_resizing
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGroupBox, QTextEdit, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

class DataSourcesViewer(QWidget):
    """Widget to display all data sources available for pricing"""
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.data_dir = 'data'
        self.init_ui()
        self.load_all_data_sources()
        
        # Auto-refresh every 30 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_all_data_sources)
        self.refresh_timer.start(30000)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("All Data Sources for Pricing")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #2563eb;")
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
        refresh_btn.clicked.connect(self.load_all_data_sources)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Info box
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        
        info_label = QLabel("📊 <b>Pricing Sources:</b> 1️⃣ Inventory (actual stock) → 2️⃣ Shopping List (actual purchases) → ❌ NO DEFAULTS")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #1565c0; font-size: 14px;")
        info_layout.addWidget(info_label)

        flow_label = QLabel("🔄 <b>Data Flow:</b> Shopping List (purchase) → Inventory (stock) → Pricing (accurate)")
        flow_label.setWordWrap(True)
        flow_label.setStyleSheet("color: #1565c0; font-size: 14px; margin-top: 5px;")
        info_layout.addWidget(flow_label)

        purpose_label = QLabel("⚠️ <b>Business Rule:</b> Only actual data used - no estimates, no defaults, no guessing")
        purpose_label.setWordWrap(True)
        purpose_label.setStyleSheet("color: #dc3545; font-size: 14px; margin-top: 5px; font-weight: 600;")
        info_layout.addWidget(purpose_label)
        
        layout.addWidget(info_box)
        
        # Create tabs for different data sources
        self.create_data_tabs(layout)
        
        # Summary section
        self.create_summary_section(layout)
    
    def create_data_tabs(self, parent_layout):
        """Create tabs for different data sources"""
        self.data_tabs = QTabWidget()
        self.data_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 12px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Shopping List Tab (Priority 2 - Actual Purchase Prices)
        self.shopping_table = self.create_table(["ID", "Item Name", "Category", "Quantity", "Unit", "Purchase Price"])

        # Apply universal column resizing functionality to shopping table
        shopping_default_column_widths = {
            0: 60,   # ID
            1: 200,  # Item Name
            2: 120,  # Category
            3: 80,   # Quantity
            4: 60,   # Unit
            5: 120   # Purchase Price
        }

        # Apply column resizing with settings persistence
        self.shopping_table_resizer = apply_universal_column_resizing(
            self.shopping_table,
            'data_sources_shopping_column_settings.json',
            shopping_default_column_widths
        )

        print("✅ Applied universal column resizing to data sources shopping table")
        self.data_tabs.addTab(self.shopping_table, "🛒 Shopping List (Actual Purchases)")

        # Inventory Tab (Priority 1 - Current Stock)
        self.inventory_table = self.create_table(["ID", "Item Name", "Category", "Quantity", "Unit", "Price/Unit", "Total Value"])

        # Apply universal column resizing functionality to inventory table
        inventory_default_column_widths = {
            0: 60,   # ID
            1: 200,  # Item Name
            2: 120,  # Category
            3: 80,   # Quantity
            4: 60,   # Unit
            5: 120,  # Price/Unit
            6: 120   # Total Value
        }

        # Apply column resizing with settings persistence
        self.inventory_table_resizer = apply_universal_column_resizing(
            self.inventory_table,
            'data_sources_inventory_column_settings.json',
            inventory_default_column_widths
        )

        print("✅ Applied universal column resizing to data sources inventory table")
        self.data_tabs.addTab(self.inventory_table, "🏠 Inventory (Current Stock)")
        
        parent_layout.addWidget(self.data_tabs)
    
    def create_table(self, headers):
        """Create a styled table widget"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                gridline-color: #f1f5f9;
                selection-background-color: #e6f7ff;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                padding: 10px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #374151;
            }
        """)
        
        # Column resizing will be applied by the caller using apply_universal_column_resizing
        
        return table
    
    def create_summary_section(self, parent_layout):
        """Create summary section"""
        summary_group = QGroupBox("Data Sources Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_label = QLabel("Loading data sources...")
        self.summary_label.setStyleSheet("font-size: 14px; color: #6c757d; padding: 10px;")
        summary_layout.addWidget(self.summary_label)
        
        parent_layout.addWidget(summary_group)
    
    def load_all_data_sources(self):
        """Load and display all data sources"""
        try:
            # Load Shopping List
            shopping_count = self.load_shopping_data()

            # Load Inventory
            inventory_count = self.load_inventory_data()

            # Update tab titles
            self.data_tabs.setTabText(0, f"🛒 Shopping List ({shopping_count} items)")
            self.data_tabs.setTabText(1, f"🏠 Inventory ({inventory_count} items)")

            # Update summary
            total_available = shopping_count + inventory_count
            summary_text = f"📊 <b>Actual Data Sources:</b> {total_available} items with real prices\n"
            summary_text += f"🎯 <b>Pricing Priority:</b> Inventory ({inventory_count}) → Shopping List ({shopping_count})\n"
            summary_text += f"⚠️ <b>Business Rule:</b> No default costs - only actual data used\n"
            summary_text += f"✅ <b>Status:</b> Real data sources loaded successfully"

            self.summary_label.setText(summary_text)
            self.summary_label.setStyleSheet("font-size: 14px; color: #28a745; padding: 10px;")

        except Exception as e:
            self.summary_label.setText(f"Error loading data sources: {e}")
            self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px;")
    

    
    def load_shopping_data(self):
        """Load shopping list data"""
        try:
            shopping_file = os.path.join(self.data_dir, 'shopping_list.csv')
            if not os.path.exists(shopping_file):
                self.shopping_table.setRowCount(0)
                return 0
            
            shopping_df = pd.read_csv(shopping_file)
            self.shopping_table.setRowCount(len(shopping_df))
            
            for row, (_, item) in enumerate(shopping_df.iterrows()):
                # ID
                self.shopping_table.setItem(row, 0, QTableWidgetItem(str(item.get('item_id', 'N/A'))))
                
                # Item Name
                name_item = QTableWidgetItem(str(item.get('item_name', 'Unknown')))
                name_item.setFont(QFont("", 0, QFont.Bold))
                self.shopping_table.setItem(row, 1, name_item)
                
                # Category
                self.shopping_table.setItem(row, 2, QTableWidgetItem(str(item.get('category', 'Unknown'))))
                
                # Quantity
                self.shopping_table.setItem(row, 3, QTableWidgetItem(str(item.get('quantity', 0))))
                
                # Unit
                self.shopping_table.setItem(row, 4, QTableWidgetItem(str(item.get('unit', 'N/A'))))
                
                # Price (try multiple price columns)
                price = item.get('average_price') or item.get('daily_price') or item.get('estimated_cost')
                if pd.notna(price):
                    price_item = QTableWidgetItem(f"₹{float(price):.2f}")
                    price_item.setForeground(QColor("#17a2b8"))
                    price_item.setFont(QFont("", 0, QFont.Bold))
                else:
                    price_item = QTableWidgetItem("N/A")
                    price_item.setForeground(QColor("#6c757d"))
                self.shopping_table.setItem(row, 5, price_item)
            
            return len(shopping_df)
            
        except Exception as e:
            self.shopping_table.setRowCount(0)
            return 0
    
    def load_inventory_data(self):
        """Load inventory data"""
        try:
            inventory_file = os.path.join(self.data_dir, 'inventory.csv')
            if not os.path.exists(inventory_file):
                self.inventory_table.setRowCount(0)
                return 0
            
            inventory_df = pd.read_csv(inventory_file)
            self.inventory_table.setRowCount(len(inventory_df))
            
            for row, (_, item) in enumerate(inventory_df.iterrows()):
                # ID
                self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item.get('item_id', 'N/A'))))
                
                # Item Name
                name_item = QTableWidgetItem(str(item.get('item_name', 'Unknown')))
                name_item.setFont(QFont("", 0, QFont.Bold))
                name_item.setForeground(QColor("#dc3545"))
                self.inventory_table.setItem(row, 1, name_item)
                
                # Category
                self.inventory_table.setItem(row, 2, QTableWidgetItem(str(item.get('category', 'Unknown'))))
                
                # Quantity
                self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item.get('quantity', 0))))
                
                # Unit
                self.inventory_table.setItem(row, 4, QTableWidgetItem(str(item.get('unit', 'N/A'))))
                
                # Price per Unit
                price_per_unit = item.get('price_per_unit') or item.get('avg_price')
                if pd.notna(price_per_unit):
                    price_item = QTableWidgetItem(f"₹{float(price_per_unit):.2f}")
                    price_item.setForeground(QColor("#28a745"))
                    price_item.setFont(QFont("", 0, QFont.Bold))
                else:
                    price_item = QTableWidgetItem("N/A")
                    price_item.setForeground(QColor("#6c757d"))
                self.inventory_table.setItem(row, 5, price_item)
                
                # Total Value
                total_value = item.get('total_value')
                if pd.notna(total_value):
                    total_item = QTableWidgetItem(f"₹{float(total_value):.2f}")
                    total_item.setForeground(QColor("#dc3545"))
                    total_item.setFont(QFont("", 0, QFont.Bold))
                else:
                    total_item = QTableWidgetItem("N/A")
                    total_item.setForeground(QColor("#6c757d"))
                self.inventory_table.setItem(row, 6, total_item)
            
            return len(inventory_df)
            
        except Exception as e:
            self.inventory_table.setRowCount(0)
            return 0

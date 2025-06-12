#!/usr/bin/env python3
"""
Packing Materials Management Module
Manages packing materials inventory and recipe associations
"""

import sys
import os
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.app_logger import get_logger
    from modules.notification_system import notify_success, notify_error, notify_info
except ImportError:
    # Fallback logger and notifications
    import logging
    def get_logger():
        return logging.getLogger(__name__)
    
    def notify_success(title, message, parent=None):
        QMessageBox.information(parent, title, message)
    
    def notify_error(title, message, parent=None):
        QMessageBox.critical(parent, title, message)
    
    def notify_info(title, message, parent=None):
        QMessageBox.information(parent, title, message)


class PackingMaterialsWidget(QWidget):
    """Widget for managing packing materials"""

    data_changed = Signal()
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = get_logger()
        
        # Initialize packing materials data
        self.init_packing_data()
        
        # Set up UI
        self.init_ui()
        
        # Load data
        self.load_data()
    
    def init_packing_data(self):
        """Initialize packing materials data structure"""
        # Load packing materials
        if 'packing_materials' not in self.data:
            try:
                if os.path.exists('data/packing_materials.csv'):
                    self.data['packing_materials'] = pd.read_csv('data/packing_materials.csv')
                else:
                    # Create default structure
                    self.data['packing_materials'] = pd.DataFrame(columns=[
                        'material_id', 'material_name', 'category', 'size', 'unit',
                        'cost_per_unit', 'current_stock', 'minimum_stock', 'supplier',
                        'notes', 'date_added'
                    ])
            except Exception as e:
                self.logger.error(f"Error loading packing materials: {e}")
                self.data['packing_materials'] = pd.DataFrame(columns=[
                    'material_id', 'material_name', 'category', 'size', 'unit',
                    'cost_per_unit', 'current_stock', 'minimum_stock', 'supplier',
                    'notes', 'date_added'
                ])
        
        # Load recipe-packing material relationships
        if 'recipe_packing_materials' not in self.data:
            try:
                if os.path.exists('data/recipe_packing_materials.csv'):
                    self.data['recipe_packing_materials'] = pd.read_csv('data/recipe_packing_materials.csv')
                else:
                    # Create default structure
                    self.data['recipe_packing_materials'] = pd.DataFrame(columns=[
                        'recipe_id', 'recipe_name', 'material_id', 'material_name',
                        'quantity_needed', 'cost_per_recipe', 'notes'
                    ])
            except Exception as e:
                self.logger.error(f"Error loading recipe packing materials: {e}")
                self.data['recipe_packing_materials'] = pd.DataFrame(columns=[
                    'recipe_id', 'recipe_name', 'material_id', 'material_name',
                    'quantity_needed', 'cost_per_recipe', 'notes'
                ])
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Packing Materials Management")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        add_material_btn = QPushButton("Add Material")
        add_material_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_material_btn.clicked.connect(self.add_material)
        header_layout.addWidget(add_material_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Materials Inventory Tab
        self.create_materials_tab()

        # Recipe Associations Tab
        self.create_recipe_associations_tab()

        # Stock Management Tab
        self.create_stock_management_tab()

        # Purchase History Tab
        self.create_purchase_history_tab()

        # Usage History Tab
        self.create_usage_history_tab()

        # Suppliers Management Tab
        self.create_suppliers_tab()

        # Cost Analysis Tab
        self.create_cost_analysis_tab()

        # Reports Tab
        self.create_reports_tab()

        layout.addWidget(self.tabs)
    
    def create_materials_tab(self):
        """Create materials inventory tab"""
        materials_widget = QWidget()
        layout = QVBoxLayout(materials_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with add button
        header_layout = QHBoxLayout()
        header_label = QLabel("Materials Inventory")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Add material button
        add_material_btn = QPushButton("➕ Add New Material")
        add_material_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #229954;
                border-color: #1e8449;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        add_material_btn.clicked.connect(self.add_new_material)
        header_layout.addWidget(add_material_btn)

        layout.addLayout(header_layout)

        # Search and filter
        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)

        self.materials_search = QLineEdit()
        self.materials_search.setPlaceholderText("Search materials...")
        self.materials_search.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.materials_search.textChanged.connect(self.filter_materials)
        search_layout.addWidget(self.materials_search)

        category_label = QLabel("Category:")
        search_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.category_filter.currentTextChanged.connect(self.filter_materials)
        search_layout.addWidget(self.category_filter)

        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Materials table
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(12)
        self.materials_table.setHorizontalHeaderLabels([
            "ID", "Material Name", "Category", "Size", "Unit",
            "Cost/Unit", "Current Stock", "Min Stock", "Supplier", "Status", "Edit", "Delete"
        ])

        # Set column widths
        header = self.materials_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Material Name - Fixed width
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Unit
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Cost/Unit
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Current Stock
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Min Stock
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Supplier
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(10, QHeaderView.Fixed)  # Edit
        header.setSectionResizeMode(11, QHeaderView.Fixed)  # Delete

        # Set specific column widths - MUCH WIDER TO GUARANTEE FIT
        self.materials_table.setColumnWidth(1, 180)   # Material Name
        self.materials_table.setColumnWidth(10, 100)  # Edit button - much wider
        self.materials_table.setColumnWidth(11, 100)  # Delete button - much wider

        # Set row height
        self.materials_table.verticalHeader().setDefaultSectionSize(50)

        # Set table properties
        self.materials_table.setAlternatingRowColors(True)
        self.materials_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.materials_table)
        
        self.tabs.addTab(materials_widget, "Materials Inventory")
    
    def create_recipe_associations_tab(self):
        """Create recipe associations tab"""
        associations_widget = QWidget()
        layout = QVBoxLayout(associations_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Recipe-Material Associations")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Recipe selection
        control_layout.addWidget(QLabel("Recipe:"))

        self.recipe_combo = QComboBox()
        self.recipe_combo.currentTextChanged.connect(self.load_recipe_materials)
        control_layout.addWidget(self.recipe_combo)

        control_layout.addStretch()

        # Bulk operations
        self.bulk_assign_btn = QPushButton("📋 Bulk Assign")
        self.bulk_assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: 1px solid #8e44ad;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
                border-color: #7d3c98;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        self.bulk_assign_btn.clicked.connect(self.bulk_assign_materials)
        self.bulk_assign_btn.setToolTip("Assign materials to multiple recipes at once")
        control_layout.addWidget(self.bulk_assign_btn)

        # Show unassigned recipes button
        unassigned_btn = QPushButton("📋 Show Unassigned Recipes")
        unassigned_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: 1px solid #d35400;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #d35400;
                border-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        unassigned_btn.clicked.connect(self.show_unassigned_recipes)
        control_layout.addWidget(unassigned_btn)

        # Add material button
        self.add_material_btn = QPushButton("➕ Add Material")
        self.add_material_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
                border-color: #1e8449;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.add_material_btn.clicked.connect(self.add_recipe_material_association)
        control_layout.addWidget(self.add_material_btn)

        # Copy from recipe button
        self.copy_from_recipe_btn = QPushButton("📋 Copy From Recipe")
        self.copy_from_recipe_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: 1px solid #e67e22;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e67e22;
                border-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        self.copy_from_recipe_btn.clicked.connect(self.copy_materials_from_recipe)
        self.copy_from_recipe_btn.setToolTip("Copy packing materials from another recipe")
        control_layout.addWidget(self.copy_from_recipe_btn)

        layout.addWidget(control_panel)

        # Recipe materials table
        self.recipe_materials_table = QTableWidget()
        self.recipe_materials_table.setColumnCount(8)
        self.recipe_materials_table.setHorizontalHeaderLabels([
            "Material Name", "Category", "Quantity Needed", "Unit Cost", "Cost per Recipe", "Notes", "Edit", "Remove"
        ])

        # Set column widths
        header = self.recipe_materials_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Edit
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Remove
        self.recipe_materials_table.setColumnWidth(6, 90)   # Fixed width for edit - much wider
        self.recipe_materials_table.setColumnWidth(7, 100)  # Fixed width for remove - much wider

        self.recipe_materials_table.setAlternatingRowColors(True)
        self.recipe_materials_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.recipe_materials_table)

        # Summary panel
        summary_panel = QWidget()
        summary_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        summary_layout = QHBoxLayout(summary_panel)

        # Cost breakdown
        cost_breakdown = QVBoxLayout()
        self.material_count_label = QLabel("Materials: 0")
        self.material_count_label.setFont(QFont("Arial", 10))
        cost_breakdown.addWidget(self.material_count_label)

        self.total_packaging_cost_label = QLabel("Total Packaging Cost: ₹0.00")
        self.total_packaging_cost_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_packaging_cost_label.setStyleSheet("color: #27ae60;")
        cost_breakdown.addWidget(self.total_packaging_cost_label)

        summary_layout.addLayout(cost_breakdown)
        summary_layout.addStretch()

        # Quick actions
        quick_actions = QVBoxLayout()

        self.calculate_cost_btn = QPushButton("🔄 Recalculate Costs")
        self.calculate_cost_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.calculate_cost_btn.clicked.connect(self.recalculate_recipe_costs)
        quick_actions.addWidget(self.calculate_cost_btn)

        self.export_recipe_materials_btn = QPushButton("💾 Export Recipe Materials")
        self.export_recipe_materials_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: 1px solid #138d75;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #138d75;
                border-color: #117a65;
            }
            QPushButton:pressed {
                background-color: #117a65;
            }
        """)
        self.export_recipe_materials_btn.clicked.connect(self.export_recipe_materials)
        quick_actions.addWidget(self.export_recipe_materials_btn)

        summary_layout.addLayout(quick_actions)
        layout.addWidget(summary_panel)

        self.tabs.addTab(associations_widget, "Recipe Associations")
    
    def create_stock_management_tab(self):
        """Create enhanced stock management tab"""
        stock_widget = QWidget()
        layout = QVBoxLayout(stock_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with actions
        header_layout = QHBoxLayout()
        header_label = QLabel("Stock Management")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Quick actions
        purchase_btn = QPushButton("📦 Record Purchase")
        purchase_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #229954;
                border-color: #1e8449;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        purchase_btn.clicked.connect(self.record_purchase)
        header_layout.addWidget(purchase_btn)

        history_btn = QPushButton("📊 View History")
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        history_btn.clicked.connect(self.view_purchase_history)
        header_layout.addWidget(history_btn)

        layout.addLayout(header_layout)

        # Stock alerts
        alerts_frame = QFrame()
        alerts_frame.setFrameStyle(QFrame.Box)
        alerts_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        alerts_layout = QVBoxLayout(alerts_frame)

        alerts_title = QLabel("🚨 Stock Alerts")
        alerts_title.setStyleSheet("font-weight: bold; color: #856404; font-size: 14px;")
        alerts_layout.addWidget(alerts_title)

        self.alerts_list = QListWidget()
        self.alerts_list.setMaximumHeight(100)
        self.alerts_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        alerts_layout.addWidget(self.alerts_list)

        layout.addWidget(alerts_frame)

        # Stock management table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(11)
        self.stock_table.setHorizontalHeaderLabels([
            "Material Name", "Current Stock", "Min Stock", "Status",
            "Last Price", "Current Price", "Avg Price", "Supplier", "Last Updated", "Buy", "History"
        ])

        # Set column widths
        header = self.stock_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Material Name - Fixed width
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Current Stock
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Min Stock
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Last Price
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Current Price
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Avg Price
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Supplier
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Last Updated
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # Buy
        header.setSectionResizeMode(10, QHeaderView.Fixed)  # History

        # Set specific column widths - MUCH WIDER TO GUARANTEE FIT
        self.stock_table.setColumnWidth(0, 180)   # Material Name
        self.stock_table.setColumnWidth(9, 100)   # Buy button - much wider
        self.stock_table.setColumnWidth(10, 120)  # History button - much wider

        # Set row height
        self.stock_table.verticalHeader().setDefaultSectionSize(50)

        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.stock_table)

        self.tabs.addTab(stock_widget, "Stock Management")

    def create_purchase_history_tab(self):
        """Create purchase history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with actions
        header_layout = QHBoxLayout()
        header_label = QLabel("Purchase History")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Export button
        export_btn = QPushButton("📊 Export History")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #21618c;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        export_btn.clicked.connect(self.export_purchase_history)
        header_layout.addWidget(export_btn)

        layout.addLayout(header_layout)

        # Filter controls
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Material:"))
        self.history_material_filter = QComboBox()
        self.history_material_filter.addItem("All Materials")
        self.history_material_filter.currentTextChanged.connect(self.filter_purchase_history)
        filter_layout.addWidget(self.history_material_filter)

        filter_layout.addWidget(QLabel("Date Range:"))
        self.history_start_date = QDateEdit()
        self.history_start_date.setDate(QDate.currentDate().addMonths(-3))
        self.history_start_date.setCalendarPopup(True)
        self.history_start_date.dateChanged.connect(self.filter_purchase_history)
        filter_layout.addWidget(self.history_start_date)

        filter_layout.addWidget(QLabel("to"))
        self.history_end_date = QDateEdit()
        self.history_end_date.setDate(QDate.currentDate())
        self.history_end_date.setCalendarPopup(True)
        self.history_end_date.dateChanged.connect(self.filter_purchase_history)
        filter_layout.addWidget(self.history_end_date)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Purchase history table
        self.purchase_history_table = QTableWidget()
        self.purchase_history_table.setColumnCount(9)
        self.purchase_history_table.setHorizontalHeaderLabels([
            "Date", "Material", "Quantity", "Price/Unit", "Total Cost",
            "Supplier", "Invoice", "Notes", "Actions"
        ])

        # Set column widths
        header = self.purchase_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Material
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Price/Unit
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total Cost
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Supplier
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Invoice
        header.setSectionResizeMode(7, QHeaderView.Stretch)  # Notes
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Actions
        self.purchase_history_table.setColumnWidth(8, 100)  # Fixed width for actions - much wider

        self.purchase_history_table.setAlternatingRowColors(True)
        self.purchase_history_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.purchase_history_table)

        # Summary panel
        summary_panel = QWidget()
        summary_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_panel)

        self.history_total_purchases_label = QLabel("Total Purchases: 0")
        self.history_total_purchases_label.setStyleSheet("font-weight: bold; color: #495057;")
        summary_layout.addWidget(self.history_total_purchases_label)

        self.history_total_cost_label = QLabel("Total Cost: ₹0.00")
        self.history_total_cost_label.setStyleSheet("font-weight: bold; color: #495057;")
        summary_layout.addWidget(self.history_total_cost_label)

        self.history_avg_price_label = QLabel("Average Price: ₹0.00")
        self.history_avg_price_label.setStyleSheet("font-weight: bold; color: #495057;")
        summary_layout.addWidget(self.history_avg_price_label)

        summary_layout.addStretch()
        layout.addWidget(summary_panel)

        self.tabs.addTab(history_widget, "Purchase History")

    def create_usage_history_tab(self):
        """Create usage history tab"""
        usage_widget = QWidget()
        layout = QVBoxLayout(usage_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Material Usage History")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Record usage button
        record_usage_btn = QPushButton("➕ Record Usage")
        record_usage_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: 1px solid #d35400;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        record_usage_btn.clicked.connect(self.manual_record_usage)
        header_layout.addWidget(record_usage_btn)

        # Export button
        export_usage_btn = QPushButton("📊 Export Usage Data")
        export_usage_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: 1px solid #138d75;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        export_usage_btn.clicked.connect(self.export_usage_history)
        header_layout.addWidget(export_usage_btn)

        layout.addLayout(header_layout)

        # Filter controls
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Material:"))
        self.usage_material_filter = QComboBox()
        self.usage_material_filter.addItem("All Materials")
        self.usage_material_filter.currentTextChanged.connect(self.filter_usage_history)
        filter_layout.addWidget(self.usage_material_filter)

        filter_layout.addWidget(QLabel("Recipe:"))
        self.usage_recipe_filter = QComboBox()
        self.usage_recipe_filter.addItem("All Recipes")
        self.usage_recipe_filter.currentTextChanged.connect(self.filter_usage_history)
        filter_layout.addWidget(self.usage_recipe_filter)

        filter_layout.addWidget(QLabel("Date From:"))
        self.usage_start_date = QDateEdit()
        self.usage_start_date.setDate(QDate.currentDate().addDays(-30))
        self.usage_start_date.setCalendarPopup(True)
        self.usage_start_date.dateChanged.connect(self.filter_usage_history)
        filter_layout.addWidget(self.usage_start_date)

        filter_layout.addWidget(QLabel("Date To:"))
        self.usage_end_date = QDateEdit()
        self.usage_end_date.setDate(QDate.currentDate())
        self.usage_end_date.setCalendarPopup(True)
        self.usage_end_date.dateChanged.connect(self.filter_usage_history)
        filter_layout.addWidget(self.usage_end_date)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Usage history table
        self.usage_history_table = QTableWidget()
        self.usage_history_table.setColumnCount(6)
        self.usage_history_table.setHorizontalHeaderLabels([
            "Date", "Recipe", "Material", "Quantity Used", "Order ID", "Notes"
        ])

        # Set column widths
        header = self.usage_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Recipe
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Material
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Order ID
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Notes

        self.usage_history_table.setColumnWidth(1, 150)  # Recipe
        self.usage_history_table.setColumnWidth(2, 150)  # Material

        self.usage_history_table.setAlternatingRowColors(True)
        self.usage_history_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.usage_history_table)

        # Summary panel
        summary_panel = QWidget()
        summary_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        summary_layout = QHBoxLayout(summary_panel)

        self.usage_total_records_label = QLabel("Total Records: 0")
        self.usage_total_records_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.usage_total_records_label.setStyleSheet("color: #2c3e50;")
        summary_layout.addWidget(self.usage_total_records_label)

        self.usage_total_materials_label = QLabel("Total Materials Used: 0")
        self.usage_total_materials_label.setFont(QFont("Arial", 10))
        summary_layout.addWidget(self.usage_total_materials_label)

        summary_layout.addStretch()
        layout.addWidget(summary_panel)

        self.tabs.addTab(usage_widget, "Usage History")

    def create_suppliers_tab(self):
        """Create suppliers management tab"""
        suppliers_widget = QWidget()
        layout = QVBoxLayout(suppliers_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Suppliers Management")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Add supplier button
        add_supplier_btn = QPushButton("➕ Add Supplier")
        add_supplier_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_supplier_btn.clicked.connect(self.add_supplier)
        header_layout.addWidget(add_supplier_btn)

        layout.addLayout(header_layout)

        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(8)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Supplier ID", "Supplier Name", "Contact Person", "Phone", "Email",
            "Address", "Rating", "Actions"
        ])

        # Set column widths
        header = self.suppliers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Contact
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Phone
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Email
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Address
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Rating
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Actions

        self.suppliers_table.setColumnWidth(1, 150)  # Supplier Name
        self.suppliers_table.setColumnWidth(7, 100)  # Actions

        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.suppliers_table)

        self.tabs.addTab(suppliers_widget, "Suppliers")

    def create_cost_analysis_tab(self):
        """Create cost analysis tab"""
        cost_widget = QWidget()
        layout = QVBoxLayout(cost_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("Cost Analysis & Trends")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Analysis controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Analysis Period:"))

        self.analysis_period = QComboBox()
        self.analysis_period.addItems(["Last 30 Days", "Last 3 Months", "Last 6 Months", "Last Year"])
        controls_layout.addWidget(self.analysis_period)

        controls_layout.addStretch()

        generate_report_btn = QPushButton("📊 Generate Report")
        generate_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        generate_report_btn.clicked.connect(self.generate_cost_analysis)
        controls_layout.addWidget(generate_report_btn)

        layout.addLayout(controls_layout)

        # Cost analysis table
        self.cost_analysis_table = QTableWidget()
        self.cost_analysis_table.setColumnCount(7)
        self.cost_analysis_table.setHorizontalHeaderLabels([
            "Material", "Current Price", "Avg Price", "Min Price", "Max Price",
            "Price Trend", "Cost Impact"
        ])

        header = self.cost_analysis_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Material
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Current
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Avg
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Min
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Max
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Trend
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Impact

        self.cost_analysis_table.setColumnWidth(0, 180)  # Material name

        self.cost_analysis_table.setAlternatingRowColors(True)
        layout.addWidget(self.cost_analysis_table)

        self.tabs.addTab(cost_widget, "Cost Analysis")

    def create_reports_tab(self):
        """Create reports tab"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("Reports & Analytics")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Report types
        reports_grid = QGridLayout()

        # Stock Report
        stock_report_btn = QPushButton("📦 Stock Report")
        stock_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        stock_report_btn.clicked.connect(self.generate_stock_report)
        reports_grid.addWidget(stock_report_btn, 0, 0)

        # Purchase Report
        purchase_report_btn = QPushButton("💰 Purchase Report")
        purchase_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        purchase_report_btn.clicked.connect(self.generate_purchase_report)
        reports_grid.addWidget(purchase_report_btn, 0, 1)

        # Usage Report
        usage_report_btn = QPushButton("📊 Usage Report")
        usage_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: 1px solid #d35400;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        usage_report_btn.clicked.connect(self.generate_usage_report)
        reports_grid.addWidget(usage_report_btn, 1, 0)

        # Cost Analysis Report
        cost_report_btn = QPushButton("💹 Cost Analysis")
        cost_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: 1px solid #8e44ad;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        cost_report_btn.clicked.connect(self.generate_cost_report)
        reports_grid.addWidget(cost_report_btn, 1, 1)

        # Clear Test Data Button
        clear_test_data_btn = QPushButton("🗑️ Clear Test Data")
        clear_test_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_test_data_btn.clicked.connect(self.clear_test_data)
        reports_grid.addWidget(clear_test_data_btn, 2, 0, 1, 2)  # Span across both columns

        layout.addLayout(reports_grid)

        # Report output area
        self.report_output = QTextEdit()
        self.report_output.setReadOnly(True)
        self.report_output.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.report_output)

        self.tabs.addTab(reports_widget, "Reports")

    def populate_purchase_history_table(self):
        """Populate purchase history table"""
        try:
            purchase_history = self.load_purchase_history()

            # Apply filters
            material_filter = self.history_material_filter.currentText()
            start_date = self.history_start_date.date().toPython()
            end_date = self.history_end_date.date().toPython()

            if not purchase_history.empty:
                # Filter by material
                if material_filter != "All Materials":
                    purchase_history = purchase_history[purchase_history['material_name'] == material_filter]

                # Filter by date range
                purchase_history['purchase_date'] = pd.to_datetime(purchase_history['purchase_date'])
                purchase_history = purchase_history[
                    (purchase_history['purchase_date'].dt.date >= start_date) &
                    (purchase_history['purchase_date'].dt.date <= end_date)
                ]

            self.purchase_history_table.setRowCount(len(purchase_history))

            total_purchases = len(purchase_history)
            total_cost = 0.0

            for row, (_, purchase) in enumerate(purchase_history.iterrows()):
                purchase_id = int(purchase.get('purchase_id', 0))
                purchase_date = purchase.get('purchase_date', '')
                material_name = purchase.get('material_name', '')
                quantity = float(purchase.get('quantity_purchased', 0))
                price_per_unit = float(purchase.get('price_per_unit', 0))
                total_purchase_cost = float(purchase.get('total_cost', 0))

                # Safe string conversion to handle NaN and overflow issues
                supplier = str(purchase.get('supplier', '')) if pd.notna(purchase.get('supplier', '')) else ''
                invoice = str(purchase.get('invoice_number', '')) if pd.notna(purchase.get('invoice_number', '')) else ''

                # Handle notes with comprehensive validation to prevent overflow
                notes_raw = purchase.get('notes', '')
                try:
                    if pd.isna(notes_raw) or notes_raw is None:
                        notes = ''
                    elif isinstance(notes_raw, (int, float)):
                        # Check for overflow values that cause libshiboken errors
                        if abs(notes_raw) > 2147483647:  # Max 32-bit int
                            notes = ''
                        else:
                            notes = str(notes_raw) if notes_raw != 0 else ''
                    else:
                        notes = str(notes_raw).strip()
                        # Limit notes length to prevent display issues
                        if len(notes) > 100:
                            notes = notes[:100] + "..."
                except (ValueError, TypeError, OverflowError):
                    notes = ''

                total_cost += total_purchase_cost

                # Populate row - store purchase_id as user data in the first column for precise identification
                date_item = QTableWidgetItem(str(purchase_date)[:10])
                date_item.setData(Qt.UserRole, purchase_id)  # Store purchase_id as hidden data
                self.purchase_history_table.setItem(row, 0, date_item)
                self.purchase_history_table.setItem(row, 1, QTableWidgetItem(str(material_name)))
                self.purchase_history_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
                self.purchase_history_table.setItem(row, 3, QTableWidgetItem(f"₹{price_per_unit:.2f}"))
                self.purchase_history_table.setItem(row, 4, QTableWidgetItem(f"₹{total_purchase_cost:.2f}"))
                self.purchase_history_table.setItem(row, 5, QTableWidgetItem(supplier))
                self.purchase_history_table.setItem(row, 6, QTableWidgetItem(invoice))
                self.purchase_history_table.setItem(row, 7, QTableWidgetItem(notes))

                # ULTRA SIMPLE - JUST SMALL BUTTON, NO CONTAINER
                edit_btn = QPushButton("Edit")
                edit_btn.setMaximumSize(60, 25)  # Small button that will definitely fit
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: 1px solid #2980b9;
                        border-radius: 3px;
                        font-size: 9px;
                        font-weight: bold;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_purchase_record(r))
                self.purchase_history_table.setCellWidget(row, 8, edit_btn)

            # Update summary
            avg_price = total_cost / total_purchases if total_purchases > 0 else 0
            self.history_total_purchases_label.setText(f"Total Purchases: {total_purchases}")
            self.history_total_cost_label.setText(f"Total Cost: ₹{total_cost:.2f}")
            self.history_avg_price_label.setText(f"Average Price: ₹{avg_price:.2f}")

            # Update material filter
            self.update_history_material_filter()

        except Exception as e:
            self.logger.error(f"Error populating purchase history table: {e}")

    def update_history_material_filter(self):
        """Update material filter for purchase history"""
        try:
            current_text = self.history_material_filter.currentText()
            self.history_material_filter.clear()
            self.history_material_filter.addItem("All Materials")

            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                materials = self.data['packing_materials']['material_name'].unique()
                materials = [mat for mat in materials if pd.notna(mat)]
                self.history_material_filter.addItems(sorted(materials))

            # Restore selection if possible
            index = self.history_material_filter.findText(current_text)
            if index >= 0:
                self.history_material_filter.setCurrentIndex(index)

        except Exception as e:
            self.logger.error(f"Error updating history material filter: {e}")

    def filter_purchase_history(self):
        """Filter purchase history based on selected criteria"""
        # Don't call populate_purchase_history_table() to avoid recursion
        # The filtering is already handled in populate_purchase_history_table()
        pass

    def export_purchase_history(self):
        """Export purchase history to CSV"""
        try:
            from PySide6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Purchase History",
                f"packing_materials_purchase_history_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )

            if file_path:
                purchase_history = self.load_purchase_history()
                purchase_history.to_csv(file_path, index=False)
                notify_success("Success", f"Purchase history exported to {file_path}", parent=self)

        except Exception as e:
            self.logger.error(f"Error exporting purchase history: {e}")
            notify_error("Error", f"Failed to export purchase history: {str(e)}", parent=self)

    def edit_purchase_record(self, row):
        """Edit a purchase record"""
        try:
            # Get the purchase_id from the stored user data (much more reliable!)
            date_item = self.purchase_history_table.item(row, 0)
            purchase_id = date_item.data(Qt.UserRole)

            if purchase_id is None:
                notify_error("Error", "Could not identify purchase record", parent=self)
                return

            # Find the record in purchase history using the unique purchase_id
            purchase_history = self.load_purchase_history()
            if not purchase_history.empty:
                mask = purchase_history['purchase_id'] == purchase_id

                if mask.any():
                    purchase_data = purchase_history[mask].iloc[0]
                    dialog = EditPurchaseDialog(self.data, purchase_data, self)
                    if dialog.exec() == QDialog.Accepted:
                        self.load_data()
                        self.data_changed.emit()
                        notify_success("Success", "Purchase record updated successfully", parent=self)
                else:
                    notify_error("Error", f"Purchase record with ID {purchase_id} not found", parent=self)
            else:
                notify_error("Error", "No purchase history found", parent=self)

        except Exception as e:
            self.logger.error(f"Error editing purchase record: {e}")
            notify_error("Error", f"Failed to edit purchase record: {str(e)}", parent=self)

    def load_data(self):
        """Load and display all packing materials data"""
        try:
            self.populate_materials_table()
            self.populate_recipe_combo()
            self.populate_stock_table()
            self.populate_purchase_history_table()
            self.populate_usage_history_table()
            self.update_category_filter()
            self.check_stock_alerts()
            self.load_recipe_materials()
        except Exception as e:
            self.logger.error(f"Error loading packing materials data: {e}")
            notify_error("Error", f"Failed to load data: {str(e)}", parent=self)

    def refresh_data_display(self):
        """Refresh all data displays after changes"""
        try:
            # Reload data from CSV files
            self.load_data()

            # Refresh all tables
            if hasattr(self, 'materials_table'):
                self.populate_materials_table()
            if hasattr(self, 'purchase_history_table'):
                self.populate_purchase_history_table()
            if hasattr(self, 'usage_history_table'):
                self.populate_usage_history_table()
            if hasattr(self, 'stock_table'):
                self.load_stock_overview()
            if hasattr(self, 'recipe_materials_table'):
                self.load_recipe_materials()

            # Emit data changed signal
            self.data_changed.emit()

            self.logger.info("Data display refreshed successfully")

        except Exception as e:
            self.logger.error(f"Error refreshing data display: {e}")

    def populate_materials_table(self):
        """Populate the materials table"""
        try:
            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                self.materials_table.setRowCount(0)
                return

            materials_df = self.data['packing_materials']
            self.materials_table.setRowCount(len(materials_df))

            for row, (_, material) in enumerate(materials_df.iterrows()):
                material_id = str(material.get('material_id', ''))
                material_name = str(material.get('material_name', '')) if pd.notna(material.get('material_name', '')) else ''
                category = str(material.get('category', '')) if pd.notna(material.get('category', '')) else ''
                size = str(material.get('size', '')) if pd.notna(material.get('size', '')) else ''
                unit = str(material.get('unit', '')) if pd.notna(material.get('unit', '')) else ''
                cost_per_unit = f"₹{material.get('cost_per_unit', 0):.2f}"
                current_stock = str(int(material.get('current_stock', 0)))
                minimum_stock = str(int(material.get('minimum_stock', 0)))
                supplier = str(material.get('supplier', '')) if pd.notna(material.get('supplier', '')) else ''

                # Determine status
                current = int(material.get('current_stock', 0))
                minimum = int(material.get('minimum_stock', 0))
                if current <= 0:
                    status = "Out of Stock"
                    status_color = "#e74c3c"
                elif current <= minimum:
                    status = "Low Stock"
                    status_color = "#f39c12"
                else:
                    status = "In Stock"
                    status_color = "#27ae60"

                # Populate row
                self.materials_table.setItem(row, 0, QTableWidgetItem(material_id))
                self.materials_table.setItem(row, 1, QTableWidgetItem(material_name))
                self.materials_table.setItem(row, 2, QTableWidgetItem(category))
                self.materials_table.setItem(row, 3, QTableWidgetItem(size))
                self.materials_table.setItem(row, 4, QTableWidgetItem(unit))

                # Make cost/unit field non-editable (calculated field)
                cost_item = QTableWidgetItem(cost_per_unit)
                cost_item.setFlags(cost_item.flags() & ~Qt.ItemIsEditable)
                cost_item.setBackground(QColor("#f8f9fa"))  # Light gray background to indicate read-only
                cost_item.setToolTip("This field is calculated automatically from purchase history")
                self.materials_table.setItem(row, 5, cost_item)

                self.materials_table.setItem(row, 6, QTableWidgetItem(current_stock))
                self.materials_table.setItem(row, 7, QTableWidgetItem(minimum_stock))
                self.materials_table.setItem(row, 8, QTableWidgetItem(supplier))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                self.materials_table.setItem(row, 9, status_item)

                # ULTRA SIMPLE - JUST SMALL BUTTONS, NO CONTAINERS
                edit_btn = QPushButton("Edit")
                edit_btn.setMaximumSize(60, 25)  # Small button that will definitely fit
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: 1px solid #2980b9;
                        border-radius: 3px;
                        font-size: 9px;
                        font-weight: bold;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_material(r))
                self.materials_table.setCellWidget(row, 10, edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.setMaximumSize(60, 25)  # Small button that will definitely fit
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: 1px solid #c0392b;
                        border-radius: 3px;
                        font-size: 9px;
                        font-weight: bold;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_material(r))
                self.materials_table.setCellWidget(row, 11, delete_btn)

        except Exception as e:
            self.logger.error(f"Error populating materials table: {e}")

    def populate_recipe_combo(self):
        """Populate recipe combo box"""
        try:
            self.recipe_combo.clear()
            self.recipe_combo.addItem("Select Recipe...")

            if 'recipes' in self.data and not self.data['recipes'].empty:
                recipes = self.data['recipes']['recipe_name'].tolist()
                self.recipe_combo.addItems(recipes)

        except Exception as e:
            self.logger.error(f"Error populating recipe combo: {e}")

    def populate_stock_table(self):
        """Populate enhanced stock management table"""
        try:
            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                self.stock_table.setRowCount(0)
                return

            materials_df = self.data['packing_materials']
            self.stock_table.setRowCount(len(materials_df))

            # Load purchase history for pricing calculations
            purchase_history = self.load_purchase_history()

            for row, (_, material) in enumerate(materials_df.iterrows()):
                material_id = material.get('material_id', 0)
                material_name = str(material.get('material_name', '')) if pd.notna(material.get('material_name', '')) else ''
                current_stock = str(int(material.get('current_stock', 0)))
                minimum_stock = str(int(material.get('minimum_stock', 0)))
                supplier = str(material.get('supplier', '')) if pd.notna(material.get('supplier', '')) else ''

                # Status
                current = int(material.get('current_stock', 0))
                minimum = int(material.get('minimum_stock', 0))
                if current <= 0:
                    status = "Critical"
                    status_color = "#e74c3c"
                elif current <= minimum:
                    status = "Low"
                    status_color = "#f39c12"
                else:
                    status = "Good"
                    status_color = "#27ae60"

                # Calculate pricing from purchase history
                material_purchases = purchase_history[purchase_history['material_id'] == material_id]

                if not material_purchases.empty:
                    # Sort by date to get latest prices
                    material_purchases = material_purchases.sort_values('purchase_date')

                    # Last price (most recent purchase)
                    last_price = float(material_purchases.iloc[-1]['price_per_unit'])

                    # Current price (same as cost_per_unit from materials table)
                    current_price = float(material.get('cost_per_unit', 0))

                    # Average price from all purchases
                    avg_price = material_purchases['price_per_unit'].mean()

                    # Last updated (most recent purchase date)
                    last_updated = str(material_purchases.iloc[-1]['purchase_date']) if pd.notna(material_purchases.iloc[-1]['purchase_date']) else datetime.now().strftime("%Y-%m-%d")
                else:
                    # No purchase history, use current values
                    last_price = float(material.get('cost_per_unit', 0))
                    current_price = float(material.get('cost_per_unit', 0))
                    avg_price = float(material.get('cost_per_unit', 0))
                    last_updated = datetime.now().strftime("%Y-%m-%d")

                # Populate row
                self.stock_table.setItem(row, 0, QTableWidgetItem(material_name))
                self.stock_table.setItem(row, 1, QTableWidgetItem(current_stock))
                self.stock_table.setItem(row, 2, QTableWidgetItem(minimum_stock))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(status_color))
                self.stock_table.setItem(row, 3, status_item)

                self.stock_table.setItem(row, 4, QTableWidgetItem(f"₹{last_price:.2f}"))
                self.stock_table.setItem(row, 5, QTableWidgetItem(f"₹{current_price:.2f}"))
                self.stock_table.setItem(row, 6, QTableWidgetItem(f"₹{avg_price:.2f}"))
                self.stock_table.setItem(row, 7, QTableWidgetItem(supplier))
                self.stock_table.setItem(row, 8, QTableWidgetItem(str(last_updated)[:10]))

                # ULTRA SIMPLE - JUST SMALL BUTTONS, NO CONTAINERS
                purchase_btn = QPushButton("Buy")
                purchase_btn.setMaximumSize(60, 25)  # Small button that will definitely fit
                purchase_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: 1px solid #229954;
                        border-radius: 3px;
                        font-size: 9px;
                        font-weight: bold;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
                purchase_btn.clicked.connect(lambda checked, r=row: self.quick_purchase(r))
                self.stock_table.setCellWidget(row, 9, purchase_btn)

                history_btn = QPushButton("History")
                history_btn.setMaximumSize(70, 25)  # Small button that will definitely fit
                history_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: 1px solid #2980b9;
                        border-radius: 3px;
                        font-size: 9px;
                        font-weight: bold;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                history_btn.clicked.connect(lambda checked, r=row: self.view_material_history(r))
                self.stock_table.setCellWidget(row, 10, history_btn)

        except Exception as e:
            self.logger.error(f"Error populating stock table: {e}")

    def load_purchase_history(self):
        """Load purchase history from CSV"""
        try:
            import os
            if os.path.exists('data/packing_materials_purchase_history.csv'):
                # Define proper data types to avoid pandas warnings
                dtype_dict = {
                    'purchase_id': 'int64',
                    'material_id': 'int64',
                    'material_name': 'object',
                    'purchase_date': 'object',
                    'quantity_purchased': 'float64',
                    'price_per_unit': 'float64',
                    'total_cost': 'float64',
                    'supplier': 'object',
                    'invoice_number': 'object',
                    'notes': 'object'
                }
                return pd.read_csv('data/packing_materials_purchase_history.csv', dtype=dtype_dict)
            else:
                return pd.DataFrame(columns=[
                    'purchase_id', 'material_id', 'material_name', 'purchase_date',
                    'quantity_purchased', 'price_per_unit', 'total_cost', 'supplier',
                    'invoice_number', 'notes'
                ])
        except Exception as e:
            self.logger.error(f"Error loading purchase history: {e}")
            return pd.DataFrame()

    def load_usage_history(self):
        """Load usage history from CSV"""
        try:
            import os
            if os.path.exists('data/packing_materials_usage_history.csv'):
                return pd.read_csv('data/packing_materials_usage_history.csv')
            else:
                return pd.DataFrame(columns=[
                    'usage_id', 'usage_date', 'recipe_id', 'recipe_name', 'material_id',
                    'material_name', 'quantity_used', 'unit_cost', 'total_cost',
                    'order_id', 'sale_id', 'notes'
                ])
        except Exception as e:
            self.logger.error(f"Error loading usage history: {e}")
            return pd.DataFrame()

    def update_category_filter(self):
        """Update category filter dropdown"""
        try:
            current_text = self.category_filter.currentText()
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")

            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                categories = self.data['packing_materials']['category'].unique()
                categories = [cat for cat in categories if pd.notna(cat)]
                self.category_filter.addItems(sorted(categories))

            # Restore selection if possible
            index = self.category_filter.findText(current_text)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)

        except Exception as e:
            self.logger.error(f"Error updating category filter: {e}")

    def check_stock_alerts(self):
        """Check for low stock alerts"""
        try:
            self.alerts_list.clear()

            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                return

            materials_df = self.data['packing_materials']
            alerts = []

            for _, material in materials_df.iterrows():
                material_name = material.get('material_name', '')
                current_stock = int(material.get('current_stock', 0))
                minimum_stock = int(material.get('minimum_stock', 0))

                if current_stock <= 0:
                    alerts.append(f"🔴 {material_name}: OUT OF STOCK")
                elif current_stock <= minimum_stock:
                    alerts.append(f"🟡 {material_name}: LOW STOCK ({current_stock} remaining)")

            if alerts:
                for alert in alerts:
                    self.alerts_list.addItem(alert)
            else:
                self.alerts_list.addItem("✅ All materials are adequately stocked")

        except Exception as e:
            self.logger.error(f"Error checking stock alerts: {e}")

    def filter_materials(self):
        """Filter materials based on search and category"""
        try:
            search_text = self.materials_search.text().lower()
            category_filter = self.category_filter.currentText()

            for row in range(self.materials_table.rowCount()):
                show_row = True

                # Check search text
                if search_text:
                    material_name = self.materials_table.item(row, 1)
                    if material_name and search_text not in material_name.text().lower():
                        show_row = False

                # Check category filter
                if category_filter != "All Categories":
                    category_item = self.materials_table.item(row, 2)
                    if category_item and category_item.text() != category_filter:
                        show_row = False

                self.materials_table.setRowHidden(row, not show_row)

        except Exception as e:
            self.logger.error(f"Error filtering materials: {e}")

    def load_recipe_materials(self):
        """Load materials for selected recipe"""
        try:
            recipe_name = self.recipe_combo.currentText()
            self.logger.info(f"Loading materials for recipe: {recipe_name}")

            if recipe_name == "Select Recipe...":
                self.recipe_materials_table.setRowCount(0)
                self.update_recipe_cost_summary(0, 0.0)
                return

            if 'recipe_packing_materials' not in self.data:
                self.logger.error("recipe_packing_materials not found in data")
                self.recipe_materials_table.setRowCount(0)
                self.update_recipe_cost_summary(0, 0.0)
                return

            if 'packing_materials' not in self.data:
                self.logger.error("packing_materials not found in data")
                self.recipe_materials_table.setRowCount(0)
                self.update_recipe_cost_summary(0, 0.0)
                return

            # Filter materials for this recipe
            recipe_materials = self.data['recipe_packing_materials'][
                self.data['recipe_packing_materials']['recipe_name'] == recipe_name
            ]

            self.logger.info(f"Found {len(recipe_materials)} materials for recipe {recipe_name}")

            self.recipe_materials_table.setRowCount(len(recipe_materials))
            total_cost = 0.0

            for row, (_, material) in enumerate(recipe_materials.iterrows()):
                try:
                    # Safe extraction of material data with proper type conversion
                    material_name = str(material.get('material_name', ''))

                    # Handle quantity with proper validation
                    try:
                        quantity_needed = float(material.get('quantity_needed', 0))
                        if quantity_needed < 0:
                            quantity_needed = 0.0
                    except (ValueError, TypeError, OverflowError):
                        quantity_needed = 0.0

                    # Handle notes with comprehensive validation
                    notes_raw = material.get('notes', '')
                    try:
                        if pd.isna(notes_raw) or notes_raw is None:
                            notes = ''
                        elif isinstance(notes_raw, (int, float)):
                            # Check for overflow values that cause libshiboken errors
                            if abs(notes_raw) > 2147483647:  # Max 32-bit int
                                notes = ''
                            else:
                                notes = str(notes_raw) if notes_raw != 0 else ''
                        else:
                            notes = str(notes_raw).strip()
                            # Limit notes length to prevent display issues
                            if len(notes) > 100:
                                notes = notes[:100] + "..."
                    except (ValueError, TypeError, OverflowError):
                        notes = ''

                    self.logger.debug(f"Processing row {row}: {material_name}, qty: {quantity_needed}, notes: '{notes}'")

                    # Get material details from packing_materials
                    material_details = self.data['packing_materials'][
                        self.data['packing_materials']['material_name'] == material_name
                    ]

                    if not material_details.empty:
                        category = str(material_details.iloc[0].get('category', ''))
                        try:
                            cost_per_unit = float(material_details.iloc[0].get('cost_per_unit', 0))
                            if cost_per_unit < 0:
                                cost_per_unit = 0.0
                        except (ValueError, TypeError, OverflowError):
                            cost_per_unit = 0.0
                        cost_per_recipe = cost_per_unit * quantity_needed
                        total_cost += cost_per_recipe
                    else:
                        self.logger.warning(f"Material '{material_name}' not found in packing_materials")
                        category = 'Unknown'
                        cost_per_unit = 0.0
                        cost_per_recipe = 0.0

                    # Populate row with ultra-safe string conversion and validation
                    try:
                        self.recipe_materials_table.setItem(row, 0, QTableWidgetItem(material_name))
                        self.recipe_materials_table.setItem(row, 1, QTableWidgetItem(category))
                        self.recipe_materials_table.setItem(row, 2, QTableWidgetItem(f"{quantity_needed:.2f}"))
                        self.recipe_materials_table.setItem(row, 3, QTableWidgetItem(f"₹{cost_per_unit:.2f}"))
                        self.recipe_materials_table.setItem(row, 4, QTableWidgetItem(f"₹{cost_per_recipe:.2f}"))
                        self.recipe_materials_table.setItem(row, 5, QTableWidgetItem(notes))
                    except Exception as table_error:
                        self.logger.error(f"Error setting table items for row {row}: {table_error}")
                        # Set safe fallback values
                        for col in range(6):
                            try:
                                self.recipe_materials_table.setItem(row, col, QTableWidgetItem(""))
                            except:
                                pass

                except Exception as row_error:
                    self.logger.error(f"Error processing row {row}: {row_error}")
                    # Set safe empty values for this row
                    try:
                        for col in range(6):
                            self.recipe_materials_table.setItem(row, col, QTableWidgetItem(""))
                    except Exception as table_error:
                        self.logger.error(f"Error setting empty values for row {row}: {table_error}")
                    continue

                # ULTRA SIMPLE - JUST SMALL BUTTONS, NO CONTAINERS
                edit_btn = QPushButton("Edit")
                edit_btn.setMaximumSize(50, 22)  # Very small button that will definitely fit
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: 1px solid #2980b9;
                        border-radius: 3px;
                        font-size: 8px;
                        font-weight: bold;
                        padding: 1px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_recipe_material(r))
                self.recipe_materials_table.setCellWidget(row, 6, edit_btn)

                remove_btn = QPushButton("Remove")
                remove_btn.setMaximumSize(60, 22)  # Small button that will definitely fit
                remove_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: 1px solid #c0392b;
                        border-radius: 3px;
                        font-size: 8px;
                        font-weight: bold;
                        padding: 1px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                remove_btn.clicked.connect(lambda checked, r=row: self.remove_recipe_material(r))
                self.recipe_materials_table.setCellWidget(row, 7, remove_btn)

            # Update summary
            self.update_recipe_cost_summary(len(recipe_materials), total_cost)

        except Exception as e:
            self.logger.error(f"Error loading recipe materials: {e}")
            # Clear the table on error
            try:
                self.recipe_materials_table.setRowCount(0)
            except:
                pass
            self.update_recipe_cost_summary(0, 0.0)

    def add_material(self):
        """Add new packing material"""
        dialog = AddMaterialDialog(self.data, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
            notify_success("Success", "Material added successfully", parent=self)

    def add_recipe_material_association(self):
        """Add material association to recipe"""
        recipe_name = self.recipe_combo.currentText()
        if recipe_name == "Select Recipe...":
            notify_error("Error", "Please select a recipe first", parent=self)
            return

        dialog = AddRecipeMaterialDialog(self.data, recipe_name, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_recipe_materials()
            self.data_changed.emit()
            notify_success("Success", "Material association added successfully", parent=self)

    def update_stock(self, row):
        """Update stock for a material"""
        material_name = self.stock_table.item(row, 0).text()
        current_stock = int(self.stock_table.item(row, 1).text())

        new_stock, ok = QInputDialog.getInt(
            self, "Update Stock",
            f"Enter new stock quantity for {material_name}:",
            current_stock, 0, 9999
        )

        if ok:
            try:
                # Update in dataframe
                mask = self.data['packing_materials']['material_name'] == material_name
                self.data['packing_materials'].loc[mask, 'current_stock'] = new_stock

                # Save to CSV
                os.makedirs('data', exist_ok=True)
                self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

                # Refresh display
                self.load_data()
                self.data_changed.emit()

                notify_success("Success", f"Stock updated for {material_name}", parent=self)

            except Exception as e:
                self.logger.error(f"Error updating stock: {e}")
                notify_error("Error", f"Failed to update stock: {str(e)}", parent=self)

    def deduct_materials_for_recipe_sale(self, recipe_name, quantity_sold=1):
        """Deduct packing materials when a recipe is sold"""
        try:
            if 'recipe_packing_materials' not in self.data:
                return False

            # Get materials needed for this recipe
            recipe_materials = self.data['recipe_packing_materials'][
                self.data['recipe_packing_materials']['recipe_name'] == recipe_name
            ]

            if recipe_materials.empty:
                return True  # No materials needed

            deductions_made = []

            for _, material_req in recipe_materials.iterrows():
                material_name = material_req.get('material_name', '')
                quantity_needed = float(material_req.get('quantity_needed', 0)) * quantity_sold

                # Find the material in inventory
                material_mask = self.data['packing_materials']['material_name'] == material_name
                if material_mask.any():
                    current_stock = float(self.data['packing_materials'].loc[material_mask, 'current_stock'].iloc[0])

                    if current_stock >= quantity_needed:
                        # Deduct the materials
                        new_stock = current_stock - quantity_needed
                        self.data['packing_materials'].loc[material_mask, 'current_stock'] = new_stock
                        deductions_made.append(f"{material_name}: -{quantity_needed}")
                    else:
                        # Insufficient stock
                        notify_error("Insufficient Stock",
                                   f"Not enough {material_name} in stock. Required: {quantity_needed}, Available: {current_stock}",
                                   parent=self)
                        return False

            # Save updated inventory
            os.makedirs('data', exist_ok=True)
            self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

            # Refresh display
            self.load_data()

            # Show success notification
            if deductions_made:
                notify_success("Materials Deducted",
                             f"Deducted materials for {recipe_name} sale:\n" + "\n".join(deductions_made),
                             parent=self)

            return True

        except Exception as e:
            self.logger.error(f"Error deducting materials for recipe sale: {e}")
            notify_error("Error", f"Failed to deduct materials: {str(e)}", parent=self)
            return False

    def calculate_packing_cost_for_recipe(self, recipe_name, quantity=1):
        """Calculate total packing material cost for a recipe"""
        try:
            if 'recipe_packing_materials' not in self.data:
                return 0.0

            # Get materials needed for this recipe
            recipe_materials = self.data['recipe_packing_materials'][
                self.data['recipe_packing_materials']['recipe_name'] == recipe_name
            ]

            if recipe_materials.empty:
                return 0.0

            total_cost = 0.0

            for _, material_req in recipe_materials.iterrows():
                material_name = material_req.get('material_name', '')
                quantity_needed = float(material_req.get('quantity_needed', 0)) * quantity

                # Find the material cost
                material_match = self.data['packing_materials'][
                    self.data['packing_materials']['material_name'] == material_name
                ]

                if not material_match.empty:
                    cost_per_unit = float(material_match.iloc[0].get('cost_per_unit', 0))
                    total_cost += quantity_needed * cost_per_unit

            return total_cost

        except Exception as e:
            self.logger.error(f"Error calculating packing cost for recipe: {e}")
            return 0.0

    def update_recipe_cost_summary(self, material_count, total_cost):
        """Update the cost summary display"""
        try:
            self.material_count_label.setText(f"Materials: {material_count}")
            self.total_packaging_cost_label.setText(f"Total Packaging Cost: ₹{total_cost:.2f}")
        except Exception as e:
            self.logger.error(f"Error updating cost summary: {e}")

    def bulk_assign_materials(self):
        """Bulk assign materials to multiple recipes"""
        try:
            dialog = BulkAssignMaterialsDialog(self.data, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_recipe_materials()
                self.data_changed.emit()
                notify_success("Success", "Materials assigned to recipes successfully", parent=self)
        except Exception as e:
            self.logger.error(f"Error in bulk assign materials: {e}")
            notify_error("Error", f"Failed to bulk assign materials: {str(e)}", parent=self)

    def show_unassigned_recipes(self):
        """Show recipes that don't have any packing materials assigned"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                notify_info("No Recipes", "No recipes found in the system", parent=self)
                return

            # Get all recipe names
            all_recipes = set(self.data['recipes']['recipe_name'].tolist())

            # Get recipes that have packing materials assigned
            assigned_recipes = set()
            if 'recipe_packing_materials' in self.data and not self.data['recipe_packing_materials'].empty:
                assigned_recipes = set(self.data['recipe_packing_materials']['recipe_name'].unique())

            # Find unassigned recipes
            unassigned_recipes = all_recipes - assigned_recipes

            if not unassigned_recipes:
                notify_success("All Assigned", "All recipes have packing materials assigned!", parent=self)
                return

            # Show dialog with unassigned recipes
            dialog = UnassignedRecipesDialog(list(unassigned_recipes), self.data, self)
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing unassigned recipes: {e}")
            notify_error("Error", f"Failed to show unassigned recipes: {str(e)}", parent=self)

    def copy_materials_from_recipe(self):
        """Copy materials from another recipe"""
        try:
            current_recipe = self.recipe_combo.currentText()
            if current_recipe == "Select Recipe...":
                notify_error("Error", "Please select a target recipe first", parent=self)
                return

            dialog = CopyMaterialsDialog(self.data, current_recipe, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_recipe_materials()
                self.data_changed.emit()
                notify_success("Success", "Materials copied successfully", parent=self)
        except Exception as e:
            self.logger.error(f"Error copying materials from recipe: {e}")
            notify_error("Error", f"Failed to copy materials: {str(e)}", parent=self)

    def edit_recipe_material(self, row):
        """Edit a recipe material association"""
        try:
            recipe_name = self.recipe_combo.currentText()
            material_name = self.recipe_materials_table.item(row, 0).text()

            # Find the material in recipe_packing_materials
            mask = (self.data['recipe_packing_materials']['recipe_name'] == recipe_name) & \
                   (self.data['recipe_packing_materials']['material_name'] == material_name)

            if mask.any():
                material_data = self.data['recipe_packing_materials'][mask].iloc[0]
                dialog = EditRecipeMaterialDialog(self.data, recipe_name, material_data, self)
                if dialog.exec() == QDialog.Accepted:
                    self.load_recipe_materials()
                    self.data_changed.emit()
                    notify_success("Success", "Material association updated successfully", parent=self)
        except Exception as e:
            self.logger.error(f"Error editing recipe material: {e}")
            notify_error("Error", f"Failed to edit material: {str(e)}", parent=self)

    def remove_recipe_material(self, row):
        """Remove a recipe material association"""
        try:
            recipe_name = self.recipe_combo.currentText()
            material_name = self.recipe_materials_table.item(row, 0).text()

            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Are you sure you want to remove {material_name} from {recipe_name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove from dataframe
                mask = (self.data['recipe_packing_materials']['recipe_name'] == recipe_name) & \
                       (self.data['recipe_packing_materials']['material_name'] == material_name)

                self.data['recipe_packing_materials'] = self.data['recipe_packing_materials'][~mask]

                # Save to CSV
                self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)

                # Refresh display
                self.load_recipe_materials()
                self.data_changed.emit()

                notify_success("Success", f"Removed {material_name} from {recipe_name}", parent=self)
        except Exception as e:
            self.logger.error(f"Error removing recipe material: {e}")
            notify_error("Error", f"Failed to remove material: {str(e)}", parent=self)

    def recalculate_recipe_costs(self):
        """Recalculate costs for current recipe"""
        try:
            self.load_recipe_materials()
            notify_success("Success", "Recipe costs recalculated", parent=self)
        except Exception as e:
            self.logger.error(f"Error recalculating costs: {e}")
            notify_error("Error", f"Failed to recalculate costs: {str(e)}", parent=self)

    def export_recipe_materials(self):
        """Export recipe materials to CSV"""
        try:
            recipe_name = self.recipe_combo.currentText()
            if recipe_name == "Select Recipe...":
                notify_error("Error", "Please select a recipe first", parent=self)
                return

            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Recipe Materials",
                f"{recipe_name}_materials.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                # Get materials for this recipe
                recipe_materials = self.data['recipe_packing_materials'][
                    self.data['recipe_packing_materials']['recipe_name'] == recipe_name
                ]

                if not recipe_materials.empty:
                    recipe_materials.to_csv(filename, index=False)
                    notify_success("Success", f"Recipe materials exported to {filename}", parent=self)
                else:
                    notify_error("Error", "No materials found for this recipe", parent=self)
        except Exception as e:
            self.logger.error(f"Error exporting recipe materials: {e}")
            notify_error("Error", f"Failed to export materials: {str(e)}", parent=self)

    def add_new_material(self):
        """Add new packing material"""
        try:
            dialog = AddMaterialDialog(self.data, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_data()
                self.data_changed.emit()
                notify_success("Success", "Material added successfully", parent=self)
        except Exception as e:
            self.logger.error(f"Error adding new material: {e}")
            notify_error("Error", f"Failed to add material: {str(e)}", parent=self)

    def edit_material(self, row):
        """Edit existing material"""
        try:
            material_id = self.materials_table.item(row, 0).text()

            # Find the material in the dataframe
            mask = self.data['packing_materials']['material_id'] == int(material_id)
            if mask.any():
                material_data = self.data['packing_materials'][mask].iloc[0]
                dialog = EditMaterialDialog(self.data, material_data, self)
                if dialog.exec() == QDialog.Accepted:
                    self.load_data()
                    self.data_changed.emit()
                    notify_success("Success", "Material updated successfully", parent=self)
        except Exception as e:
            self.logger.error(f"Error editing material: {e}")
            notify_error("Error", f"Failed to edit material: {str(e)}", parent=self)

    def delete_material(self, row):
        """Delete material"""
        try:
            material_id = self.materials_table.item(row, 0).text()
            material_name = self.materials_table.item(row, 1).text()

            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete '{material_name}'?\n\nThis will also remove all recipe associations with this material.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove from packing_materials
                mask = self.data['packing_materials']['material_id'] == int(material_id)
                self.data['packing_materials'] = self.data['packing_materials'][~mask]

                # Remove from recipe associations
                if 'recipe_packing_materials' in self.data:
                    recipe_mask = self.data['recipe_packing_materials']['material_name'] == material_name
                    self.data['recipe_packing_materials'] = self.data['recipe_packing_materials'][~recipe_mask]
                    self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)

                # Save updated data
                os.makedirs('data', exist_ok=True)
                self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

                # Refresh display
                self.load_data()
                self.data_changed.emit()

                notify_success("Success", f"Deleted '{material_name}' and all its associations", parent=self)
        except Exception as e:
            self.logger.error(f"Error deleting material: {e}")
            notify_error("Error", f"Failed to delete material: {str(e)}", parent=self)

    def record_purchase(self):
        """Record a new material purchase"""
        try:
            dialog = RecordPurchaseDialog(self.data, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_data()
                self.data_changed.emit()
                notify_success("Success", "Purchase recorded successfully", parent=self)
        except Exception as e:
            self.logger.error(f"Error recording purchase: {e}")
            notify_error("Error", f"Failed to record purchase: {str(e)}", parent=self)

    def quick_purchase(self, row):
        """Quick purchase for specific material"""
        try:
            material_name = self.stock_table.item(row, 0).text()

            # Find material in dataframe
            material_match = self.data['packing_materials'][
                self.data['packing_materials']['material_name'] == material_name
            ]

            if not material_match.empty:
                material_data = material_match.iloc[0]
                dialog = RecordPurchaseDialog(self.data, self, material_data)
                if dialog.exec() == QDialog.Accepted:
                    self.load_data()
                    self.data_changed.emit()
                    notify_success("Success", f"Purchase recorded for {material_name}", parent=self)
        except Exception as e:
            self.logger.error(f"Error in quick purchase: {e}")
            notify_error("Error", f"Failed to record purchase: {str(e)}", parent=self)

    def view_purchase_history(self):
        """View complete purchase history"""
        try:
            dialog = PurchaseHistoryDialog(self.data, self)
            dialog.exec()
        except Exception as e:
            self.logger.error(f"Error viewing purchase history: {e}")
            notify_error("Error", f"Failed to load purchase history: {str(e)}", parent=self)

    def quick_purchase_simple(self, row):
        """Simple quick purchase for a material"""
        try:
            material_name = self.stock_table.item(row, 0).text()

            # Simple input dialog for quick purchase
            quantity, ok1 = QInputDialog.getDouble(
                self, "Quick Purchase",
                f"Enter quantity to purchase for {material_name}:",
                0.0, 0.0, 9999.0, 2
            )

            if ok1:
                total_cost, ok2 = QInputDialog.getDouble(
                    self, "Quick Purchase",
                    f"Enter total cost for {quantity} units of {material_name}:",
                    0.0, 0.0, 99999.0, 2
                )

                if ok2:
                    # Calculate price per unit
                    price_per_unit = total_cost / quantity if quantity > 0 else 0

                    # Add to purchase history
                    self.add_purchase_record(material_name, quantity, price_per_unit)

                    # Update stock and average price
                    current_stock = float(self.stock_table.item(row, 1).text())
                    new_stock = current_stock + quantity

                    # Update in dataframe with new average price
                    mask = self.data['packing_materials']['material_name'] == material_name
                    self.data['packing_materials'].loc[mask, 'current_stock'] = new_stock

                    # Calculate new average price from purchase history
                    purchase_history = self.load_purchase_history()
                    material_purchases = purchase_history[purchase_history['material_name'] == material_name]
                    if not material_purchases.empty:
                        new_avg_price = material_purchases['price_per_unit'].mean()
                        self.data['packing_materials'].loc[mask, 'cost_per_unit'] = new_avg_price

                    # Save to CSV
                    os.makedirs('data', exist_ok=True)
                    self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

                    # Refresh display
                    self.load_data()
                    self.data_changed.emit()

                    notify_success("Success", f"Purchased {quantity} units of {material_name} for ₹{total_cost:.2f}", parent=self)

        except Exception as e:
            self.logger.error(f"Error in quick purchase: {e}")
            notify_error("Error", f"Failed to complete purchase: {str(e)}", parent=self)

    def add_purchase_record(self, material_name, quantity, price_per_unit):
        """Add a purchase record to history"""
        try:
            import os

            # Load existing purchase history
            purchase_history = self.load_purchase_history()

            # Get material ID
            material_id = 1  # Default
            if 'packing_materials' in self.data:
                material_match = self.data['packing_materials'][
                    self.data['packing_materials']['material_name'] == material_name
                ]
                if not material_match.empty:
                    material_id = material_match.iloc[0]['material_id']

            # Generate new purchase ID
            if not purchase_history.empty:
                next_id = purchase_history['purchase_id'].max() + 1
            else:
                next_id = 1

            # Create new record
            new_record = {
                'purchase_id': next_id,
                'material_id': material_id,
                'material_name': material_name,
                'purchase_date': datetime.now().strftime('%Y-%m-%d'),
                'quantity_purchased': quantity,
                'price_per_unit': price_per_unit,
                'total_cost': quantity * price_per_unit,
                'supplier': 'Quick Purchase',
                'invoice_number': f'QP{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'notes': 'Quick purchase entry'
            }

            # Add to dataframe
            purchase_history = pd.concat([purchase_history, pd.DataFrame([new_record])], ignore_index=True)

            # Save to CSV
            os.makedirs('data', exist_ok=True)
            purchase_history.to_csv('data/packing_materials_purchase_history.csv', index=False)

        except Exception as e:
            self.logger.error(f"Error adding purchase record: {e}")

    def view_material_history(self, row):
        """View history for specific material"""
        try:
            material_name = self.stock_table.item(row, 0).text()
            dialog = PurchaseHistoryDialog(self.data, self, material_name)
            dialog.exec()
        except Exception as e:
            self.logger.error(f"Error viewing material history: {e}")
            notify_error("Error", f"Failed to load material history: {str(e)}", parent=self)

    def add_new_material(self):
        """Add new material - wrapper for add_material"""
        self.add_material()

    def export_recipe_materials(self):
        """Export recipe materials to CSV"""
        try:
            from PySide6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Recipe Materials",
                f"recipe_materials_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )

            if file_path:
                if 'recipe_packing_materials' in self.data:
                    self.data['recipe_packing_materials'].to_csv(file_path, index=False)
                    notify_success("Success", f"Recipe materials exported to {file_path}", parent=self)
                else:
                    notify_error("Error", "No recipe materials data to export", parent=self)

        except Exception as e:
            self.logger.error(f"Error exporting recipe materials: {e}")
            notify_error("Error", f"Failed to export recipe materials: {str(e)}", parent=self)

    def view_purchase_history(self):
        """View purchase history"""
        try:
            # Switch to purchase history tab
            self.tabs.setCurrentIndex(3)  # Purchase History tab
        except Exception as e:
            self.logger.error(f"Error viewing purchase history: {e}")
            notify_error("Error", f"Failed to view purchase history: {str(e)}", parent=self)

    def add_supplier(self):
        """Add new supplier"""
        try:
            # For now, show a placeholder dialog
            notify_info("Add Supplier", "Supplier management functionality will be implemented", parent=self)
        except Exception as e:
            self.logger.error(f"Error adding supplier: {e}")
            notify_error("Error", f"Failed to add supplier: {str(e)}", parent=self)

    def generate_cost_analysis(self):
        """Generate cost analysis report"""
        try:
            # For now, show a placeholder
            notify_info("Cost Analysis", "Cost analysis report generation will be implemented", parent=self)
        except Exception as e:
            self.logger.error(f"Error generating cost analysis: {e}")
            notify_error("Error", f"Failed to generate cost analysis: {str(e)}", parent=self)

    def generate_stock_report(self):
        """Generate stock report"""
        try:
            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                self.report_output.setText("No packing materials data available for report generation.")
                return

            materials_df = self.data['packing_materials']

            # Generate stock report
            report = "=== PACKING MATERIALS STOCK REPORT ===\n\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Summary statistics
            total_materials = len(materials_df)
            low_stock_count = len(materials_df[materials_df['current_stock'].astype(int) <= materials_df['minimum_stock'].astype(int)])
            out_of_stock_count = len(materials_df[materials_df['current_stock'].astype(int) == 0])

            report += f"Total Materials: {total_materials}\n"
            report += f"Low Stock Items: {low_stock_count}\n"
            report += f"Out of Stock Items: {out_of_stock_count}\n\n"

            # Low stock items
            if low_stock_count > 0:
                report += "=== LOW STOCK ITEMS ===\n"
                low_stock_items = materials_df[materials_df['current_stock'].astype(int) <= materials_df['minimum_stock'].astype(int)]
                for _, item in low_stock_items.iterrows():
                    report += f"- {item['material_name']}: {item['current_stock']} (Min: {item['minimum_stock']})\n"
                report += "\n"

            # Stock by category
            report += "=== STOCK BY CATEGORY ===\n"
            category_stock = materials_df.groupby('category')['current_stock'].sum().astype(int)
            for category, stock in category_stock.items():
                report += f"- {category}: {stock} units\n"

            self.report_output.setText(report)

        except Exception as e:
            self.logger.error(f"Error generating stock report: {e}")
            notify_error("Error", f"Failed to generate stock report: {str(e)}", parent=self)

    def generate_purchase_report(self):
        """Generate purchase report"""
        try:
            purchase_history = self.load_purchase_history()

            if purchase_history.empty:
                self.report_output.setText("No purchase history data available for report generation.")
                return

            # Generate purchase report
            report = "=== PACKING MATERIALS PURCHASE REPORT ===\n\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Summary statistics
            total_purchases = len(purchase_history)
            total_cost = purchase_history['total_cost'].sum()
            avg_purchase_cost = purchase_history['total_cost'].mean()

            report += f"Total Purchases: {total_purchases}\n"
            report += f"Total Cost: ₹{total_cost:.2f}\n"
            report += f"Average Purchase Cost: ₹{avg_purchase_cost:.2f}\n\n"

            # Recent purchases (last 10)
            report += "=== RECENT PURCHASES ===\n"
            recent_purchases = purchase_history.tail(10)
            for _, purchase in recent_purchases.iterrows():
                report += f"- {purchase['purchase_date']}: {purchase['material_name']} - ₹{purchase['total_cost']:.2f}\n"

            self.report_output.setText(report)

        except Exception as e:
            self.logger.error(f"Error generating purchase report: {e}")
            notify_error("Error", f"Failed to generate purchase report: {str(e)}", parent=self)

    def generate_usage_report(self):
        """Generate comprehensive usage report"""
        try:
            # Load usage data
            usage_data = self.load_usage_history()

            report = "=== PACKING MATERIALS USAGE REPORT ===\n\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Check if data is empty or contains only test/sample data
            if usage_data.empty:
                report += "📊 NO USAGE DATA AVAILABLE\n\n"
                report += "To start tracking material usage:\n"
                report += "1. Go to the 'Usage History' tab\n"
                report += "2. Click 'Record Usage' to manually record material consumption\n"
                report += "3. Or use the recipe association feature to automatically track usage\n\n"
                report += "💡 TIP: Usage tracking helps you:\n"
                report += "   • Monitor material consumption patterns\n"
                report += "   • Calculate accurate recipe costs\n"
                report += "   • Identify high-usage materials for better inventory planning\n"
                self.report_output.setText(report)
                return

            # Check if data contains only test/sample data (dates in future or obvious patterns)
            current_date = datetime.now().date()
            usage_data['usage_date'] = pd.to_datetime(usage_data['usage_date'])
            future_dates = usage_data[usage_data['usage_date'].dt.date > current_date]

            # Check for obvious test patterns (perfect order IDs, sale IDs, etc.)
            test_patterns = [
                'ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005',
                'SALE001', 'SALE002', 'SALE003', 'SALE004', 'SALE005',
                'Material used for', 'preparation', 'Manual Entry',
                'Test', 'Sample', 'Demo', 'Example'
            ]

            # Check for 2025 dates (clearly fake since we're in 2024)
            year_2025_dates = usage_data[usage_data['usage_date'].dt.year >= 2025]

            has_test_data = False

            # Check for future dates or 2025 dates
            if not future_dates.empty or not year_2025_dates.empty:
                has_test_data = True
            else:
                # Check for test patterns in any text field
                for pattern in test_patterns:
                    if (usage_data['notes'].str.contains(pattern, case=False, na=False).any() or
                        usage_data['order_id'].str.contains(pattern, case=False, na=False).any() or
                        usage_data['recipe_name'].str.contains(pattern, case=False, na=False).any() or
                        usage_data['material_name'].str.contains(pattern, case=False, na=False).any()):
                        has_test_data = True
                        break

                # Check for sequential patterns that indicate test data
                if 'usage_id' in usage_data.columns:
                    # Check if usage IDs are perfectly sequential starting from 1
                    usage_ids = sorted(usage_data['usage_id'].tolist())
                    expected_ids = list(range(1, len(usage_ids) + 1))
                    if usage_ids == expected_ids and len(usage_ids) > 5:
                        has_test_data = True

            if has_test_data:
                report += "⚠️  FAKE/TEST DATA DETECTED\n\n"
                report += "🚫 ALL DATA IN THE SYSTEM IS FAKE/TEST DATA!\n\n"
                report += "This data is clearly not real because:\n"

                # Specific reasons why it's fake
                if not year_2025_dates.empty:
                    report += f"• Contains dates from 2025 ({len(year_2025_dates)} records) - WE'RE STILL IN 2024!\n"
                if not future_dates.empty:
                    report += f"• Contains future dates ({len(future_dates)} records)\n"

                # Check for specific test patterns found
                found_patterns = []
                for pattern in test_patterns:
                    if (usage_data['notes'].str.contains(pattern, case=False, na=False).any() or
                        usage_data['order_id'].str.contains(pattern, case=False, na=False).any() or
                        usage_data['recipe_name'].str.contains(pattern, case=False, na=False).any() or
                        usage_data['material_name'].str.contains(pattern, case=False, na=False).any()):
                        found_patterns.append(pattern)

                if found_patterns:
                    report += f"• Contains obvious test patterns: {', '.join(found_patterns)}\n"

                report += "• Generated for demonstration/testing purposes\n\n"

                report += "🗑️ SOLUTION: Click 'Clear Test Data' button below to remove ALL fake data.\n\n"
                report += "📋 TO START REAL USAGE TRACKING:\n"
                report += "1. Click the 'Clear Test Data' button to remove all fake entries\n"
                report += "2. Go to 'Usage History' tab\n"
                report += "3. Click 'Record Usage' to manually record ACTUAL material consumption\n"
                report += "4. Or set up recipe associations to automatically track real usage\n\n"

                report += "💡 CURRENT FAKE DATA SUMMARY:\n"
                report += f"   • {len(usage_data)} fake records\n"
                report += f"   • Date range: {usage_data['usage_date'].min().strftime('%Y-%m-%d')} to {usage_data['usage_date'].max().strftime('%Y-%m-%d')}\n"
                report += f"   • Fake total cost: ₹{usage_data['total_cost'].sum():.2f}\n\n"
                report += "❌ THIS IS 100% FAKE DATA - NOT REAL USAGE TRACKING!\n"
                report += "❌ DO NOT USE THIS DATA FOR ANY BUSINESS DECISIONS!\n"
                self.report_output.setText(report)
                return

            # Calculate overall statistics
            total_records = len(usage_data)
            total_cost = usage_data['total_cost'].sum()
            total_materials = len(usage_data['material_name'].unique())
            total_recipes = len(usage_data['recipe_name'].unique())

            # Date range
            usage_data['usage_date'] = pd.to_datetime(usage_data['usage_date'])
            start_date = usage_data['usage_date'].min().strftime('%Y-%m-%d')
            end_date = usage_data['usage_date'].max().strftime('%Y-%m-%d')

            report += f"📊 USAGE SUMMARY\n"
            report += f"Period: {start_date} to {end_date}\n"
            report += f"Total Usage Records: {total_records:,}\n"
            report += f"Total Usage Cost: ₹{total_cost:,.2f}\n"
            report += f"Materials Used: {total_materials}\n"
            report += f"Recipes Involved: {total_recipes}\n\n"

            # Top 5 most used materials by quantity
            report += "🔝 TOP 5 MOST USED MATERIALS (by Quantity)\n"
            material_usage = usage_data.groupby('material_name')['quantity_used'].sum().sort_values(ascending=False)
            for i, (material, quantity) in enumerate(material_usage.head(5).items(), 1):
                report += f"{i}. {material}: {quantity:.2f} units\n"
            report += "\n"

            # Top 5 most expensive materials by total cost
            report += "💰 TOP 5 MOST EXPENSIVE MATERIALS (by Total Cost)\n"
            material_cost = usage_data.groupby('material_name')['total_cost'].sum().sort_values(ascending=False)
            for i, (material, cost) in enumerate(material_cost.head(5).items(), 1):
                report += f"{i}. {material}: ₹{cost:.2f}\n"
            report += "\n"

            # Usage by recipe
            report += "🍽️ USAGE BY RECIPE\n"
            recipe_usage = usage_data.groupby('recipe_name').agg({
                'total_cost': 'sum',
                'quantity_used': 'sum',
                'material_name': 'nunique'
            }).sort_values('total_cost', ascending=False)

            for recipe, data in recipe_usage.head(10).iterrows():
                report += f"• {recipe}:\n"
                report += f"  - Total Cost: ₹{data['total_cost']:.2f}\n"
                report += f"  - Materials Used: {data['material_name']} different materials\n"
                report += f"  - Total Quantity: {data['quantity_used']:.2f} units\n\n"

            # Monthly usage trend (if data spans multiple months)
            usage_data['month'] = usage_data['usage_date'].dt.to_period('M')
            monthly_usage = usage_data.groupby('month')['total_cost'].sum()

            if len(monthly_usage) > 1:
                report += "📈 MONTHLY USAGE TREND\n"
                for month, cost in monthly_usage.items():
                    report += f"• {month}: ₹{cost:.2f}\n"
                report += "\n"

            # Recent usage (last 7 days)
            recent_date = usage_data['usage_date'].max() - pd.Timedelta(days=7)
            recent_usage = usage_data[usage_data['usage_date'] >= recent_date]

            if not recent_usage.empty:
                report += "🕐 RECENT USAGE (Last 7 Days)\n"
                report += f"Records: {len(recent_usage)}\n"
                report += f"Total Cost: ₹{recent_usage['total_cost'].sum():.2f}\n"
                report += f"Average Daily Cost: ₹{recent_usage['total_cost'].sum() / 7:.2f}\n\n"

            # Usage efficiency insights
            report += "💡 INSIGHTS & RECOMMENDATIONS\n"

            # High-cost materials
            high_cost_materials = material_cost.head(3)
            if not high_cost_materials.empty:
                report += f"• Monitor high-cost materials: {', '.join(high_cost_materials.index[:3])}\n"

            # Frequent usage patterns
            avg_daily_cost = total_cost / max(1, (usage_data['usage_date'].max() - usage_data['usage_date'].min()).days)
            report += f"• Average daily usage cost: ₹{avg_daily_cost:.2f}\n"

            # Material efficiency
            material_efficiency = usage_data.groupby('material_name')['unit_cost'].mean()
            if not material_efficiency.empty:
                most_efficient = material_efficiency.idxmin()
                least_efficient = material_efficiency.idxmax()
                report += f"• Most cost-efficient material: {most_efficient} (₹{material_efficiency[most_efficient]:.2f}/unit)\n"
                report += f"• Least cost-efficient material: {least_efficient} (₹{material_efficiency[least_efficient]:.2f}/unit)\n"

            self.report_output.setText(report)

        except Exception as e:
            self.logger.error(f"Error generating usage report: {e}")
            notify_error("Error", f"Failed to generate usage report: {str(e)}", parent=self)

    def clear_test_data(self):
        """Clear test/sample data from usage history"""
        try:
            from PySide6.QtWidgets import QMessageBox

            # Confirm with user
            reply = QMessageBox.question(
                self, "Clear Test Data",
                "Are you sure you want to clear all test/sample data from usage history?\n\n"
                "This will remove:\n"
                "• All usage records with test patterns (ORD001, SALE001, etc.)\n"
                "• Records with future dates\n"
                "• Sample data entries\n\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                import os

                # Load current usage data
                usage_data = self.load_usage_history()

                if usage_data.empty:
                    notify_info("No Data", "No usage data found to clear.", parent=self)
                    return

                # Identify test data patterns
                current_date = datetime.now().date()
                usage_data['usage_date'] = pd.to_datetime(usage_data['usage_date'])

                # Filter out ALL test data
                test_patterns = [
                    'ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005',
                    'SALE001', 'SALE002', 'SALE003', 'SALE004', 'SALE005',
                    'Material used for', 'preparation', 'Manual Entry',
                    'Test', 'Sample', 'Demo', 'Example'
                ]

                # Keep only real data (not test patterns, not future dates, not 2025 dates)
                real_data = usage_data.copy()

                # Remove future dates
                real_data = real_data[real_data['usage_date'].dt.date <= current_date]

                # Remove 2025 dates (clearly fake since we're in 2024)
                real_data = real_data[real_data['usage_date'].dt.year < 2025]

                # Remove test patterns from ALL text fields
                for pattern in test_patterns:
                    real_data = real_data[
                        ~real_data['notes'].str.contains(pattern, case=False, na=False) &
                        ~real_data['order_id'].str.contains(pattern, case=False, na=False) &
                        ~real_data['recipe_name'].str.contains(pattern, case=False, na=False) &
                        ~real_data['material_name'].str.contains(pattern, case=False, na=False)
                    ]

                # Count removed records
                removed_count = len(usage_data) - len(real_data)

                if removed_count == 0:
                    notify_info("No Test Data", "No test data patterns found to remove.", parent=self)
                    return

                # Save cleaned data
                if real_data.empty:
                    # If no real data remains, create empty file
                    empty_df = pd.DataFrame(columns=[
                        'usage_id', 'usage_date', 'recipe_id', 'recipe_name', 'material_id',
                        'material_name', 'quantity_used', 'unit_cost', 'total_cost',
                        'order_id', 'sale_id', 'notes'
                    ])
                    empty_df.to_csv('data/packing_materials_usage_history.csv', index=False)
                else:
                    # Reset usage IDs to be sequential
                    real_data['usage_id'] = range(1, len(real_data) + 1)
                    real_data.to_csv('data/packing_materials_usage_history.csv', index=False)

                # Refresh the display
                self.load_data()
                self.data_changed.emit()

                notify_success(
                    "Test Data Cleared",
                    f"Successfully removed {removed_count} test records.\n"
                    f"Remaining real records: {len(real_data)}",
                    parent=self
                )

                # Regenerate the usage report to show updated status
                self.generate_usage_report()

        except Exception as e:
            self.logger.error(f"Error clearing test data: {e}")
            notify_error("Error", f"Failed to clear test data: {str(e)}", parent=self)

    def generate_cost_report(self):
        """Generate cost analysis report"""
        try:
            if 'packing_materials' not in self.data or self.data['packing_materials'].empty:
                self.report_output.setText("No packing materials data available for cost analysis.")
                return

            materials_df = self.data['packing_materials']
            purchase_history = self.load_purchase_history()

            # Generate cost analysis report
            report = "=== PACKING MATERIALS COST ANALYSIS ===\n\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Cost summary
            total_inventory_value = (materials_df['current_stock'].astype(float) * materials_df['cost_per_unit'].astype(float)).sum()
            report += f"Total Inventory Value: ₹{total_inventory_value:.2f}\n\n"

            # Most expensive materials
            report += "=== TOP 5 MOST EXPENSIVE MATERIALS ===\n"
            expensive_materials = materials_df.nlargest(5, 'cost_per_unit')
            for _, material in expensive_materials.iterrows():
                report += f"- {material['material_name']}: ₹{material['cost_per_unit']:.2f} per {material['unit']}\n"
            report += "\n"

            # Category costs
            report += "=== COST BY CATEGORY ===\n"
            category_costs = materials_df.groupby('category').apply(
                lambda x: (x['current_stock'].astype(float) * x['cost_per_unit'].astype(float)).sum()
            )
            for category, cost in category_costs.items():
                report += f"- {category}: ₹{cost:.2f}\n"

            self.report_output.setText(report)

        except Exception as e:
            self.logger.error(f"Error generating cost report: {e}")
            notify_error("Error", f"Failed to generate cost report: {str(e)}", parent=self)

    def populate_usage_history_table(self):
        """Populate usage history table with real usage data"""
        try:
            # Load actual usage data from CSV
            usage_data = self.load_usage_history()

            # Convert to list of dictionaries for filtering
            usage_records = []
            if not usage_data.empty:
                for _, record in usage_data.iterrows():
                    usage_records.append({
                        'date': record.get('usage_date', ''),
                        'recipe': record.get('recipe_name', ''),
                        'material': record.get('material_name', ''),
                        'quantity_used': float(record.get('quantity_used', 0)),
                        'unit_cost': float(record.get('unit_cost', 0)),
                        'total_cost': float(record.get('total_cost', 0)),
                        'order_id': record.get('order_id', ''),
                        'notes': record.get('notes', '')
                    })

            # Apply filters
            material_filter = self.usage_material_filter.currentText()
            recipe_filter = self.usage_recipe_filter.currentText()
            start_date = self.usage_start_date.date().toPython()
            end_date = self.usage_end_date.date().toPython()

            filtered_data = []
            for record in usage_records:  # Use usage_records instead of usage_data
                try:
                    # Handle different date formats more robustly
                    date_str = str(record.get('date', ''))
                    if not date_str or date_str == 'nan':
                        continue

                    # Try different date parsing approaches
                    record_date = None
                    try:
                        # Try parsing as datetime first
                        if ' ' in date_str:  # Has time component
                            record_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                        else:
                            record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            # Try parsing just the date part
                            date_part = date_str.split(' ')[0] if ' ' in date_str else date_str
                            record_date = datetime.strptime(date_part, '%Y-%m-%d').date()
                        except ValueError:
                            # Skip records with unparseable dates
                            continue

                    if record_date is None:
                        continue

                    # Apply filters
                    if material_filter != "All Materials" and record.get('material', '') != material_filter:
                        continue
                    if recipe_filter != "All Recipes" and record.get('recipe', '') != recipe_filter:
                        continue
                    if record_date < start_date or record_date > end_date:
                        continue

                    filtered_data.append(record)
                except (ValueError, KeyError, TypeError) as e:
                    # Skip records with invalid data
                    continue

            self.usage_history_table.setRowCount(len(filtered_data))

            # Track unique materials used
            materials_used = set()
            for row, record in enumerate(filtered_data):
                # Handle notes with comprehensive validation to prevent overflow
                notes_raw = record.get('notes', '')
                try:
                    if pd.isna(notes_raw) or notes_raw is None:
                        notes = ''
                    elif isinstance(notes_raw, (int, float)):
                        # Check for overflow values that cause libshiboken errors
                        if abs(notes_raw) > 2147483647:  # Max 32-bit int
                            notes = ''
                        else:
                            notes = str(notes_raw) if notes_raw != 0 else ''
                    else:
                        notes = str(notes_raw).strip()
                        # Limit notes length to prevent display issues
                        if len(notes) > 100:
                            notes = notes[:100] + "..."
                except (ValueError, TypeError, OverflowError):
                    notes = ''

                self.usage_history_table.setItem(row, 0, QTableWidgetItem(record['date']))
                self.usage_history_table.setItem(row, 1, QTableWidgetItem(record['recipe']))
                self.usage_history_table.setItem(row, 2, QTableWidgetItem(record['material']))
                self.usage_history_table.setItem(row, 3, QTableWidgetItem(str(record['quantity_used'])))
                self.usage_history_table.setItem(row, 4, QTableWidgetItem(record['order_id']))
                self.usage_history_table.setItem(row, 5, QTableWidgetItem(notes))

                materials_used.add(record['material'])

            # Update summary
            self.usage_total_records_label.setText(f"Total Records: {len(filtered_data)}")
            self.usage_total_materials_label.setText(f"Total Materials Used: {len(materials_used)}")

            # Update filters
            self.update_usage_filters()

        except Exception as e:
            self.logger.error(f"Error populating usage history table: {e}")

    def update_usage_filters(self):
        """Update usage history filters"""
        try:
            # Update material filter
            current_material = self.usage_material_filter.currentText()
            self.usage_material_filter.clear()
            self.usage_material_filter.addItem("All Materials")

            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                materials = self.data['packing_materials']['material_name'].unique()
                materials = [mat for mat in materials if pd.notna(mat)]
                self.usage_material_filter.addItems(sorted(materials))

            # Restore selection
            index = self.usage_material_filter.findText(current_material)
            if index >= 0:
                self.usage_material_filter.setCurrentIndex(index)

            # Update recipe filter
            current_recipe = self.usage_recipe_filter.currentText()
            self.usage_recipe_filter.clear()
            self.usage_recipe_filter.addItem("All Recipes")

            if 'recipes' in self.data and not self.data['recipes'].empty:
                recipes = self.data['recipes']['recipe_name'].unique()
                recipes = [rec for rec in recipes if pd.notna(rec)]
                self.usage_recipe_filter.addItems(sorted(recipes))

            # Restore selection
            index = self.usage_recipe_filter.findText(current_recipe)
            if index >= 0:
                self.usage_recipe_filter.setCurrentIndex(index)

        except Exception as e:
            self.logger.error(f"Error updating usage filters: {e}")

    def filter_usage_history(self):
        """Filter usage history based on selected criteria"""
        # Don't call populate_usage_history_table() to avoid recursion
        # The filtering is already handled in populate_usage_history_table()
        pass

    def export_usage_history(self):
        """Export usage history to CSV"""
        try:
            from PySide6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Usage History",
                f"packing_materials_usage_history_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )

            if file_path:
                usage_data = self.load_usage_history()
                if not usage_data.empty:
                    usage_data.to_csv(file_path, index=False)
                    notify_success("Success", f"Usage history exported to {file_path}", parent=self)
                else:
                    notify_error("Error", "No usage history data to export", parent=self)

        except Exception as e:
            self.logger.error(f"Error exporting usage history: {e}")
            notify_error("Error", f"Failed to export usage history: {str(e)}", parent=self)

    def record_material_usage(self, recipe_id, recipe_name, order_id=None, sale_id=None):
        """Record material usage when a recipe is prepared/sold"""
        try:
            import os

            # Get recipe materials
            if 'recipe_packing_materials' not in self.data or self.data['recipe_packing_materials'].empty:
                return

            recipe_materials = self.data['recipe_packing_materials']
            recipe_items = recipe_materials[recipe_materials['recipe_id'] == recipe_id]

            if recipe_items.empty:
                return

            # Load existing usage history
            usage_history = self.load_usage_history()

            # Get current materials data for costs
            materials_data = self.data.get('packing_materials', pd.DataFrame())

            new_usage_records = []

            for _, item in recipe_items.iterrows():
                material_name = item['material_name']
                quantity_needed = float(item.get('quantity_needed', 0))

                # Get current cost from materials data
                material_cost = 0.0
                if not materials_data.empty:
                    material_row = materials_data[materials_data['material_name'] == material_name]
                    if not material_row.empty:
                        material_cost = float(material_row.iloc[0].get('cost_per_unit', 0))

                total_cost = quantity_needed * material_cost

                # Create usage record
                usage_record = {
                    'usage_id': len(usage_history) + len(new_usage_records) + 1,
                    'usage_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'recipe_id': recipe_id,
                    'recipe_name': recipe_name,
                    'material_id': item.get('material_id', 0),
                    'material_name': material_name,
                    'quantity_used': quantity_needed,
                    'unit_cost': material_cost,
                    'total_cost': total_cost,
                    'order_id': order_id or f"AUTO{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'sale_id': sale_id or '',
                    'notes': f"Material used for {recipe_name} preparation"
                }

                new_usage_records.append(usage_record)

                # Update material stock
                if not materials_data.empty:
                    material_mask = materials_data['material_name'] == material_name
                    if material_mask.any():
                        current_stock = float(materials_data.loc[material_mask, 'current_stock'].iloc[0])
                        new_stock = max(0, current_stock - quantity_needed)
                        materials_data.loc[material_mask, 'current_stock'] = new_stock

            # Save usage records
            if new_usage_records:
                new_df = pd.DataFrame(new_usage_records)
                usage_history = pd.concat([usage_history, new_df], ignore_index=True)

                # Save to CSV
                os.makedirs('data', exist_ok=True)
                usage_history.to_csv('data/packing_materials_usage_history.csv', index=False)

                # Update materials stock
                if not materials_data.empty:
                    materials_data.to_csv('data/packing_materials.csv', index=False)
                    self.data['packing_materials'] = materials_data

                self.logger.info(f"Recorded usage for {len(new_usage_records)} materials for recipe {recipe_name}")

        except Exception as e:
            self.logger.error(f"Error recording material usage: {e}")

    def record_bulk_usage(self, usage_records):
        """Record multiple usage records at once"""
        try:
            import os

            # Load existing usage history
            usage_history = self.load_usage_history()

            # Add new records
            new_df = pd.DataFrame(usage_records)
            usage_history = pd.concat([usage_history, new_df], ignore_index=True)

            # Save to CSV
            os.makedirs('data', exist_ok=True)
            usage_history.to_csv('data/packing_materials_usage_history.csv', index=False)

            self.logger.info(f"Recorded {len(usage_records)} bulk usage records")

        except Exception as e:
            self.logger.error(f"Error recording bulk usage: {e}")

    def get_usage_analytics(self, start_date=None, end_date=None):
        """Get usage analytics for a date range"""
        try:
            usage_data = self.load_usage_history()

            if usage_data.empty:
                return {
                    'total_usage_cost': 0,
                    'total_materials_used': 0,
                    'most_used_materials': [],
                    'usage_by_recipe': {},
                    'usage_by_date': {}
                }

            # Filter by date range if provided
            if start_date or end_date:
                usage_data['usage_date'] = pd.to_datetime(usage_data['usage_date'])
                if start_date:
                    usage_data = usage_data[usage_data['usage_date'] >= start_date]
                if end_date:
                    usage_data = usage_data[usage_data['usage_date'] <= end_date]

            # Calculate analytics
            total_cost = usage_data['total_cost'].sum()
            total_materials = len(usage_data['material_name'].unique())

            # Most used materials
            material_usage = usage_data.groupby('material_name')['quantity_used'].sum().sort_values(ascending=False)
            most_used = material_usage.head(5).to_dict()

            # Usage by recipe
            recipe_usage = usage_data.groupby('recipe_name')['total_cost'].sum().to_dict()

            # Usage by date
            usage_data['date_only'] = pd.to_datetime(usage_data['usage_date']).dt.date
            date_usage = usage_data.groupby('date_only')['total_cost'].sum().to_dict()

            return {
                'total_usage_cost': total_cost,
                'total_materials_used': total_materials,
                'most_used_materials': most_used,
                'usage_by_recipe': recipe_usage,
                'usage_by_date': date_usage
            }

        except Exception as e:
            self.logger.error(f"Error getting usage analytics: {e}")
            return {}

    def manual_record_usage(self):
        """Manually record material usage"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit, QPushButton, QLabel

            dialog = QDialog(self)
            dialog.setWindowTitle("Record Material Usage")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # Form layout
            form_layout = QFormLayout()

            # Recipe selection
            recipe_combo = QComboBox()
            recipe_combo.addItem("Manual Entry", "manual")
            if 'recipes' in self.data and not self.data['recipes'].empty:
                for _, recipe in self.data['recipes'].iterrows():
                    recipe_combo.addItem(recipe['recipe_name'], recipe['recipe_id'])
            form_layout.addRow("Recipe:", recipe_combo)

            # Material selection
            material_combo = QComboBox()
            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                for _, material in self.data['packing_materials'].iterrows():
                    material_combo.addItem(material['material_name'], material['material_id'])
            form_layout.addRow("Material:", material_combo)

            # Quantity used
            quantity_spin = QDoubleSpinBox()
            quantity_spin.setRange(0.01, 9999.99)
            quantity_spin.setDecimals(2)
            quantity_spin.setValue(1.0)
            form_layout.addRow("Quantity Used:", quantity_spin)

            # Order ID
            order_id_edit = QLineEdit()
            order_id_edit.setPlaceholderText("Optional order/sale ID")
            form_layout.addRow("Order ID:", order_id_edit)

            # Notes
            notes_edit = QTextEdit()
            notes_edit.setMaximumHeight(80)
            notes_edit.setPlaceholderText("Optional notes about this usage")
            form_layout.addRow("Notes:", notes_edit)

            layout.addLayout(form_layout)

            # Buttons
            button_layout = QHBoxLayout()

            # Record single usage
            record_single_btn = QPushButton("Record Single Usage")
            record_single_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: 1px solid #2980b9;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

            def record_single():
                try:
                    recipe_name = recipe_combo.currentText()
                    recipe_id = recipe_combo.currentData()
                    material_name = material_combo.currentText()
                    material_id = material_combo.currentData()
                    quantity = quantity_spin.value()
                    order_id = order_id_edit.text().strip() or f"MANUAL{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    notes = notes_edit.toPlainText().strip() or f"Manual usage entry for {material_name}"

                    # Get material cost
                    material_cost = 0.0
                    if 'packing_materials' in self.data:
                        material_row = self.data['packing_materials'][self.data['packing_materials']['material_name'] == material_name]
                        if not material_row.empty:
                            material_cost = float(material_row.iloc[0].get('cost_per_unit', 0))

                    # Create usage record
                    usage_record = {
                        'usage_id': len(self.load_usage_history()) + 1,
                        'usage_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'recipe_id': recipe_id if recipe_id != "manual" else 0,
                        'recipe_name': recipe_name,
                        'material_id': material_id,
                        'material_name': material_name,
                        'quantity_used': quantity,
                        'unit_cost': material_cost,
                        'total_cost': quantity * material_cost,
                        'order_id': order_id,
                        'sale_id': '',
                        'notes': notes
                    }

                    # Record usage
                    self.record_bulk_usage([usage_record])

                    # Update stock
                    if 'packing_materials' in self.data:
                        material_mask = self.data['packing_materials']['material_name'] == material_name
                        if material_mask.any():
                            current_stock = float(self.data['packing_materials'].loc[material_mask, 'current_stock'].iloc[0])
                            new_stock = max(0, current_stock - quantity)
                            self.data['packing_materials'].loc[material_mask, 'current_stock'] = new_stock
                            os.makedirs('data', exist_ok=True)
                            self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

                    # Refresh displays
                    self.load_data()
                    self.data_changed.emit()

                    notify_success("Success", f"Recorded usage of {quantity} {material_name}", parent=self)
                    dialog.accept()

                except Exception as e:
                    self.logger.error(f"Error recording single usage: {e}")
                    notify_error("Error", f"Failed to record usage: {str(e)}", parent=self)

            record_single_btn.clicked.connect(record_single)
            button_layout.addWidget(record_single_btn)

            # Record full recipe usage
            record_recipe_btn = QPushButton("Record Full Recipe Usage")
            record_recipe_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: 1px solid #229954;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)

            def record_recipe():
                try:
                    recipe_id = recipe_combo.currentData()
                    recipe_name = recipe_combo.currentText()
                    order_id = order_id_edit.text().strip()

                    if recipe_id == "manual":
                        notify_error("Error", "Please select a specific recipe for full recipe usage", parent=self)
                        return

                    # Record usage for all materials in the recipe
                    self.record_material_usage(recipe_id, recipe_name, order_id)

                    # Refresh displays
                    self.load_data()
                    self.data_changed.emit()

                    notify_success("Success", f"Recorded full usage for recipe: {recipe_name}", parent=self)
                    dialog.accept()

                except Exception as e:
                    self.logger.error(f"Error recording recipe usage: {e}")
                    notify_error("Error", f"Failed to record recipe usage: {str(e)}", parent=self)

            record_recipe_btn.clicked.connect(record_recipe)
            button_layout.addWidget(record_recipe_btn)

            # Cancel button
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: 1px solid #7f8c8d;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error in manual record usage: {e}")
            notify_error("Error", f"Failed to open usage recording dialog: {str(e)}", parent=self)


class RecordPurchaseDialog(QDialog):
    """Dialog for recording material purchases"""

    def __init__(self, data, parent=None, material_data=None):
        super().__init__(parent)
        self.data = data
        self.material_data = material_data
        self.logger = get_logger()
        self.setWindowTitle("Record Material Purchase")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_label = QLabel("Record Material Purchase")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Material selection
        material_group = QGroupBox("Material Selection")
        material_layout = QFormLayout(material_group)

        self.material_combo = QComboBox()
        if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
            materials = self.data['packing_materials']['material_name'].tolist()
            self.material_combo.addItems(materials)

            # Pre-select material if provided
            if self.material_data is not None:
                material_name = self.material_data.get('material_name', '')
                index = self.material_combo.findText(material_name)
                if index >= 0:
                    self.material_combo.setCurrentIndex(index)

        material_layout.addRow("Material:", self.material_combo)
        layout.addWidget(material_group)

        # Purchase details
        purchase_group = QGroupBox("Purchase Details")
        purchase_layout = QFormLayout(purchase_group)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99999)
        self.quantity_spin.setValue(1)
        purchase_layout.addRow("Quantity Purchased:", self.quantity_spin)

        self.total_cost_spin = QDoubleSpinBox()
        self.total_cost_spin.setMinimum(0.01)
        self.total_cost_spin.setMaximum(99999.99)
        self.total_cost_spin.setDecimals(2)
        self.total_cost_spin.setValue(1.0)
        self.total_cost_spin.valueChanged.connect(self.update_price_per_unit)
        purchase_layout.addRow("Total Cost (₹):", self.total_cost_spin)

        self.price_per_unit_label = QLabel("₹0.00")
        self.price_per_unit_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        purchase_layout.addRow("Price per Unit (Calculated):", self.price_per_unit_label)

        self.supplier_edit = QLineEdit()
        if self.material_data is not None:
            self.supplier_edit.setText(str(self.material_data.get('supplier', '')))
        purchase_layout.addRow("Supplier:", self.supplier_edit)

        self.invoice_edit = QLineEdit()
        self.invoice_edit.setPlaceholderText("Invoice/Receipt number")
        purchase_layout.addRow("Invoice Number:", self.invoice_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        purchase_layout.addRow("Purchase Date:", self.date_edit)

        layout.addWidget(purchase_group)

        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes about this purchase...")
        notes_layout.addWidget(self.notes_edit)

        layout.addWidget(notes_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Record Purchase")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        # Update initial price per unit calculation
        self.quantity_spin.valueChanged.connect(self.update_price_per_unit)
        self.update_price_per_unit()

    def load_purchase_history(self):
        """Load purchase history from CSV"""
        try:
            import os
            if os.path.exists('data/packing_materials_purchase_history.csv'):
                # Define proper data types to avoid pandas warnings
                dtype_dict = {
                    'purchase_id': 'int64',
                    'material_id': 'int64',
                    'material_name': 'object',
                    'purchase_date': 'object',
                    'quantity_purchased': 'float64',
                    'price_per_unit': 'float64',
                    'total_cost': 'float64',
                    'supplier': 'object',
                    'invoice_number': 'object',
                    'notes': 'object'
                }
                return pd.read_csv('data/packing_materials_purchase_history.csv', dtype=dtype_dict)
            else:
                return pd.DataFrame(columns=[
                    'purchase_id', 'material_id', 'material_name', 'purchase_date',
                    'quantity_purchased', 'price_per_unit', 'total_cost', 'supplier',
                    'invoice_number', 'notes'
                ])
        except Exception as e:
            self.logger.error(f"Error loading purchase history: {e}")
            return pd.DataFrame()

    def update_price_per_unit(self):
        """Update price per unit calculation"""
        try:
            quantity = self.quantity_spin.value()
            total_cost = self.total_cost_spin.value()
            if quantity > 0:
                price_per_unit = total_cost / quantity
                self.price_per_unit_label.setText(f"₹{price_per_unit:.2f}")
            else:
                self.price_per_unit_label.setText("₹0.00")
        except Exception as e:
            self.logger.error(f"Error updating price per unit: {e}")
            self.price_per_unit_label.setText("₹0.00")

    def accept(self):
        """Save the purchase record"""
        try:
            material_name = self.material_combo.currentText()
            if not material_name:
                QMessageBox.warning(self, "Validation Error", "Please select a material")
                return

            quantity = self.quantity_spin.value()
            total_cost = self.total_cost_spin.value()
            price_per_unit = total_cost / quantity if quantity > 0 else 0
            supplier = self.supplier_edit.text().strip()
            invoice_number = self.invoice_edit.text().strip()
            purchase_date = self.date_edit.date().toString("yyyy-MM-dd")
            notes = self.notes_edit.toPlainText().strip()

            # Get material ID
            material_match = self.data['packing_materials'][
                self.data['packing_materials']['material_name'] == material_name
            ]

            if material_match.empty:
                QMessageBox.warning(self, "Error", "Material not found")
                return

            material_id = material_match.iloc[0]['material_id']

            # Load existing purchase history
            purchase_history = self.load_purchase_history()

            # Generate new purchase ID
            if not purchase_history.empty:
                next_id = purchase_history['purchase_id'].max() + 1
            else:
                next_id = 1

            # Create new purchase record
            new_purchase = pd.DataFrame({
                'purchase_id': [next_id],
                'material_id': [material_id],
                'material_name': [material_name],
                'purchase_date': [purchase_date],
                'quantity_purchased': [quantity],
                'price_per_unit': [price_per_unit],
                'total_cost': [total_cost],
                'supplier': [supplier],
                'invoice_number': [invoice_number],
                'notes': [notes]
            })

            # Add to purchase history
            if purchase_history.empty:
                updated_history = new_purchase
            else:
                updated_history = pd.concat([purchase_history, new_purchase], ignore_index=True)

            # Save purchase history
            updated_history.to_csv('data/packing_materials_purchase_history.csv', index=False)

            # Update material stock and pricing
            mask = self.data['packing_materials']['material_id'] == material_id
            current_stock = int(self.data['packing_materials'].loc[mask, 'current_stock'].iloc[0])
            new_stock = current_stock + quantity

            # Calculate new average price from all purchase history
            # Get all purchases for this material including the new one
            all_purchases = updated_history[updated_history['material_id'] == material_id]
            if not all_purchases.empty:
                # Calculate running average of all purchases
                new_avg_price = all_purchases['price_per_unit'].mean()
            else:
                new_avg_price = price_per_unit

            self.data['packing_materials'].loc[mask, 'current_stock'] = new_stock
            self.data['packing_materials'].loc[mask, 'cost_per_unit'] = new_avg_price
            self.data['packing_materials'].loc[mask, 'supplier'] = supplier

            # Save updated materials
            os.makedirs('data', exist_ok=True)
            self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

            QMessageBox.information(
                self, "Success",
                f"Purchase recorded successfully!\n\n"
                f"Material: {material_name}\n"
                f"Quantity: {quantity}\n"
                f"Total Cost: ₹{total_cost:.2f}\n"
                f"New Stock: {new_stock}"
            )

            super().accept()

        except Exception as e:
            self.logger.error(f"Error saving purchase: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save purchase: {str(e)}")




class PurchaseHistoryDialog(QDialog):
    """Dialog for viewing purchase history"""

    def __init__(self, data, parent=None, material_name=None):
        super().__init__(parent)
        self.data = data
        self.material_name = material_name
        self.logger = get_logger()

        if material_name:
            self.setWindowTitle(f"Purchase History - {material_name}")
        else:
            self.setWindowTitle("Purchase History - All Materials")

        self.setModal(True)
        self.resize(900, 600)
        self.init_ui()
        self.load_history()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        if self.material_name:
            header_text = f"Purchase History for {self.material_name}"
        else:
            header_text = "Complete Purchase History"

        header_label = QLabel(header_text)
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Filter controls
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Date Range:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-6))
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("to"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date)

        filter_btn = QPushButton("Apply Filter")
        filter_btn.clicked.connect(self.load_history)
        filter_layout.addWidget(filter_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Material", "Quantity", "Price/Unit", "Total Cost",
            "Supplier", "Invoice", "Notes", "Actions"
        ])

        # Set column widths
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Material
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Price/Unit
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total Cost
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Supplier
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Invoice
        header.setSectionResizeMode(7, QHeaderView.Stretch)  # Notes
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions

        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.history_table)

        # Summary panel
        summary_panel = QWidget()
        summary_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_panel)

        self.total_purchases_label = QLabel("Total Purchases: 0")
        self.total_purchases_label.setStyleSheet("font-weight: bold; color: #495057;")
        summary_layout.addWidget(self.total_purchases_label)

        self.total_cost_label = QLabel("Total Cost: ₹0.00")
        self.total_cost_label.setStyleSheet("font-weight: bold; color: #495057;")
        summary_layout.addWidget(self.total_cost_label)

        self.avg_price_label = QLabel("Average Price: ₹0.00")
        self.avg_price_label.setStyleSheet("font-weight: bold; color: #495057;")
        summary_layout.addWidget(self.avg_price_label)

        summary_layout.addStretch()
        layout.addWidget(summary_panel)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_history)
        button_layout.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_purchase_history(self):
        """Load purchase history from CSV"""
        try:
            import os
            if os.path.exists('data/packing_materials_purchase_history.csv'):
                # Define proper data types to avoid pandas warnings
                dtype_dict = {
                    'purchase_id': 'int64',
                    'material_id': 'int64',
                    'material_name': 'object',
                    'purchase_date': 'object',
                    'quantity_purchased': 'float64',
                    'price_per_unit': 'float64',
                    'total_cost': 'float64',
                    'supplier': 'object',
                    'invoice_number': 'object',
                    'notes': 'object'
                }
                return pd.read_csv('data/packing_materials_purchase_history.csv', dtype=dtype_dict)
            else:
                return pd.DataFrame(columns=[
                    'purchase_id', 'material_id', 'material_name', 'purchase_date',
                    'quantity_purchased', 'price_per_unit', 'total_cost', 'supplier',
                    'invoice_number', 'notes'
                ])
        except Exception as e:
            self.logger.error(f"Error loading purchase history: {e}")
            return pd.DataFrame()

    def load_history(self):
        """Load and display purchase history"""
        try:
            # Load purchase history
            purchase_history = self.load_purchase_history()

            if purchase_history.empty:
                self.history_table.setRowCount(0)
                self.update_summary(0, 0.0, 0.0)
                return

            # Filter by material if specified
            if self.material_name:
                purchase_history = purchase_history[
                    purchase_history['material_name'] == self.material_name
                ]

            # Filter by date range
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")

            purchase_history = purchase_history[
                (purchase_history['purchase_date'] >= start_date) &
                (purchase_history['purchase_date'] <= end_date)
            ]

            # Sort by date (newest first)
            purchase_history = purchase_history.sort_values('purchase_date', ascending=False)

            # Populate table
            self.history_table.setRowCount(len(purchase_history))

            total_cost = 0.0
            total_quantity = 0

            for row, (_, purchase) in enumerate(purchase_history.iterrows()):
                purchase_date = purchase.get('purchase_date', '')
                material_name = purchase.get('material_name', '')
                quantity = int(purchase.get('quantity_purchased', 0))
                price_per_unit = float(purchase.get('price_per_unit', 0))
                total_purchase_cost = float(purchase.get('total_cost', 0))
                supplier = purchase.get('supplier', '')
                invoice = purchase.get('invoice_number', '')

                # Handle notes with comprehensive validation to prevent overflow
                notes_raw = purchase.get('notes', '')
                try:
                    if pd.isna(notes_raw) or notes_raw is None:
                        notes = ''
                    elif isinstance(notes_raw, (int, float)):
                        # Check for overflow values that cause libshiboken errors
                        if abs(notes_raw) > 2147483647:  # Max 32-bit int
                            notes = ''
                        else:
                            notes = str(notes_raw) if notes_raw != 0 else ''
                    else:
                        notes = str(notes_raw).strip()
                        # Limit notes length to prevent display issues
                        if len(notes) > 100:
                            notes = notes[:100] + "..."
                except (ValueError, TypeError, OverflowError):
                    notes = ''

                total_cost += total_purchase_cost
                total_quantity += quantity

                # Populate row
                self.history_table.setItem(row, 0, QTableWidgetItem(purchase_date))
                self.history_table.setItem(row, 1, QTableWidgetItem(material_name))
                self.history_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
                self.history_table.setItem(row, 3, QTableWidgetItem(f"₹{price_per_unit:.2f}"))
                self.history_table.setItem(row, 4, QTableWidgetItem(f"₹{total_purchase_cost:.2f}"))
                self.history_table.setItem(row, 5, QTableWidgetItem(supplier))
                self.history_table.setItem(row, 6, QTableWidgetItem(invoice))
                self.history_table.setItem(row, 7, QTableWidgetItem(notes))

                # Action button
                edit_btn = QPushButton("Edit")
                edit_btn.setMaximumSize(50, 28)
                edit_btn.setMinimumSize(45, 25)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: 1px solid #2980b9;
                        border-radius: 4px;
                        font-size: 10px;
                        font-weight: bold;
                        padding: 2px 4px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                        border-color: #21618c;
                    }
                    QPushButton:pressed {
                        background-color: #21618c;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_purchase(r))
                self.history_table.setCellWidget(row, 8, edit_btn)

            # Calculate average price
            avg_price = purchase_history['price_per_unit'].mean() if not purchase_history.empty else 0.0

            # Update summary
            self.update_summary(len(purchase_history), total_cost, avg_price)

        except Exception as e:
            self.logger.error(f"Error loading purchase history: {e}")
            self.history_table.setRowCount(0)
            self.update_summary(0, 0.0, 0.0)

    def update_summary(self, count, total_cost, avg_price):
        """Update summary labels"""
        self.total_purchases_label.setText(f"Total Purchases: {count}")
        self.total_cost_label.setText(f"Total Cost: ₹{total_cost:.2f}")
        self.avg_price_label.setText(f"Average Price: ₹{avg_price:.2f}")

    def edit_purchase(self, row):
        """Edit a purchase record"""
        try:
            # Get purchase data from table
            purchase_id = self.history_table.item(row, 0).text()

            # Find the record in purchase history
            purchase_history = self.load_purchase_history()
            if not purchase_history.empty:
                mask = purchase_history['purchase_id'] == int(purchase_id)

                if mask.any():
                    purchase_data = purchase_history[mask].iloc[0]
                    dialog = EditPurchaseDialog(self.data, purchase_data, self)
                    if dialog.exec() == QDialog.Accepted:
                        self.load_history()  # Refresh the history display
                        notify_success("Success", "Purchase record updated successfully", parent=self)
                else:
                    notify_error("Error", "Purchase record not found", parent=self)
            else:
                notify_error("Error", "No purchase history found", parent=self)

        except Exception as e:
            self.logger.error(f"Error editing purchase record: {e}")
            notify_error("Error", f"Failed to edit purchase record: {str(e)}", parent=self)

    def export_history(self):
        """Export history to CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Purchase History",
                f"purchase_history_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                purchase_history = self.load_purchase_history()

                if self.material_name:
                    purchase_history = purchase_history[
                        purchase_history['material_name'] == self.material_name
                    ]

                purchase_history.to_csv(filename, index=False)
                QMessageBox.information(self, "Success", f"History exported to {filename}")

        except Exception as e:
            self.logger.error(f"Error exporting history: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")




class EditPurchaseDialog(QDialog):
    """Dialog for editing purchase records"""

    def __init__(self, data, purchase_data, parent=None):
        super().__init__(parent)
        self.data = data
        self.purchase_data = purchase_data
        self.logger = get_logger()
        self.setWindowTitle("Edit Purchase Record")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header
        header_label = QLabel(f"Edit Purchase: {self.purchase_data['material_name']}")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Purchase details
        details_group = QGroupBox("Purchase Details")
        details_layout = QFormLayout(details_group)

        # Material (read-only)
        self.material_label = QLabel(str(self.purchase_data.get('material_name', '')))
        self.material_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        details_layout.addRow("Material:", self.material_label)

        # Purchase date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        purchase_date = str(self.purchase_data.get('purchase_date', ''))
        if purchase_date:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                self.date_edit.setDate(date_obj)
            except:
                self.date_edit.setDate(QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())
        details_layout.addRow("Purchase Date:", self.date_edit)

        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setMaximum(99999.99)
        self.quantity_spin.setValue(float(self.purchase_data.get('quantity_purchased', 0)))
        details_layout.addRow("Quantity:", self.quantity_spin)

        # Price per unit
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setDecimals(2)
        self.price_spin.setMaximum(99999.99)
        self.price_spin.setValue(float(self.purchase_data.get('price_per_unit', 0)))
        details_layout.addRow("Price per Unit (₹):", self.price_spin)

        # Total cost (calculated)
        self.total_cost_label = QLabel()
        self.total_cost_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #e8f5e8;
                border: 1px solid #28a745;
                border-radius: 4px;
                font-weight: bold;
                color: #155724;
            }
        """)
        self.update_total_cost()
        details_layout.addRow("Total Cost (₹):", self.total_cost_label)

        # Connect signals to update total cost
        self.quantity_spin.valueChanged.connect(self.update_total_cost)
        self.price_spin.valueChanged.connect(self.update_total_cost)

        layout.addWidget(details_group)

        # Supplier info
        supplier_group = QGroupBox("Supplier Information")
        supplier_layout = QFormLayout(supplier_group)

        self.supplier_edit = QLineEdit()
        self.supplier_edit.setText(str(self.purchase_data.get('supplier', '')))
        supplier_layout.addRow("Supplier:", self.supplier_edit)

        self.invoice_edit = QLineEdit()
        self.invoice_edit.setText(str(self.purchase_data.get('invoice_number', '')))
        supplier_layout.addRow("Invoice Number:", self.invoice_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlainText(str(self.purchase_data.get('notes', '')))
        supplier_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(supplier_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def update_total_cost(self):
        """Update total cost calculation"""
        quantity = self.quantity_spin.value()
        price_per_unit = self.price_spin.value()
        total_cost = quantity * price_per_unit
        self.total_cost_label.setText(f"₹{total_cost:.2f}")

    def accept(self):
        """Save the purchase record changes"""
        try:
            # Validate inputs
            if self.quantity_spin.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Quantity must be greater than 0")
                return

            if self.price_spin.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Price per unit must be greater than 0")
                return

            purchase_id = int(self.purchase_data['purchase_id'])
            material_id = int(self.purchase_data['material_id'])

            # Load purchase history
            purchase_history = self.load_purchase_history()

            if purchase_history.empty:
                QMessageBox.warning(self, "Error", "Purchase history not found")
                return

            # Find and update the record
            mask = purchase_history['purchase_id'] == purchase_id
            if not mask.any():
                QMessageBox.warning(self, "Error", "Purchase record not found")
                return

            # Update the record with proper data types
            purchase_history.loc[mask, 'purchase_date'] = str(self.date_edit.date().toString("yyyy-MM-dd"))
            purchase_history.loc[mask, 'quantity_purchased'] = float(self.quantity_spin.value())
            purchase_history.loc[mask, 'price_per_unit'] = float(self.price_spin.value())
            purchase_history.loc[mask, 'total_cost'] = float(self.quantity_spin.value() * self.price_spin.value())
            purchase_history.loc[mask, 'supplier'] = str(self.supplier_edit.text().strip())
            purchase_history.loc[mask, 'invoice_number'] = str(self.invoice_edit.text().strip())
            purchase_history.loc[mask, 'notes'] = str(self.notes_edit.toPlainText().strip())

            # Save purchase history
            purchase_history.to_csv('data/packing_materials_purchase_history.csv', index=False)

            # Update material cost and stock if needed
            self.update_material_data(material_id, purchase_history)

            super().accept()

        except Exception as e:
            self.logger.error(f"Error saving purchase changes: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")

    def load_purchase_history(self):
        """Load purchase history from CSV"""
        try:
            import os
            if os.path.exists('data/packing_materials_purchase_history.csv'):
                # Define proper data types to avoid pandas warnings
                dtype_dict = {
                    'purchase_id': 'int64',
                    'material_id': 'int64',
                    'material_name': 'object',
                    'purchase_date': 'object',
                    'quantity_purchased': 'float64',
                    'price_per_unit': 'float64',
                    'total_cost': 'float64',
                    'supplier': 'object',
                    'invoice_number': 'object',
                    'notes': 'object'
                }
                return pd.read_csv('data/packing_materials_purchase_history.csv', dtype=dtype_dict)
            else:
                return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error loading purchase history: {e}")
            return pd.DataFrame()

    def update_material_data(self, material_id, purchase_history):
        """Update material cost based on purchase history"""
        try:
            # Calculate new average price from all purchases for this material
            material_purchases = purchase_history[purchase_history['material_id'] == material_id]
            if not material_purchases.empty:
                new_avg_price = material_purchases['price_per_unit'].mean()

                # Update material cost in packing_materials data
                if 'packing_materials' in self.data:
                    mask = self.data['packing_materials']['material_id'] == material_id
                    if mask.any():
                        self.data['packing_materials'].loc[mask, 'cost_per_unit'] = new_avg_price
                        # Save updated materials data
                        os.makedirs('data', exist_ok=True)
                        self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

        except Exception as e:
            self.logger.error(f"Error updating material data: {e}")


class EditMaterialDialog(QDialog):
    """Dialog for editing existing packing material"""

    def __init__(self, data, material_data, parent=None):
        super().__init__(parent)
        self.data = data
        self.material_data = material_data
        self.logger = get_logger()
        self.setWindowTitle("Edit Packing Material")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header
        header_label = QLabel(f"Edit Material: {self.material_data['material_name']}")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Material details
        details_group = QGroupBox("Material Details")
        details_layout = QFormLayout(details_group)

        self.name_edit = QLineEdit()
        self.name_edit.setText(str(self.material_data.get('material_name', '')))
        details_layout.addRow("Material Name:", self.name_edit)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems([
            "Boxes", "Plastic Covers", "Plastic Bags", "Bottles",
            "Wrapping", "Protection", "Sealing", "Labeling",
            "Containers", "Bags"
        ])
        self.category_combo.setCurrentText(str(self.material_data.get('category', '')))
        details_layout.addRow("Category:", self.category_combo)

        self.size_edit = QLineEdit()
        self.size_edit.setText(str(self.material_data.get('size', '')))
        details_layout.addRow("Size:", self.size_edit)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["pieces", "rolls", "sheets", "kg", "meters"])
        self.unit_combo.setCurrentText(str(self.material_data.get('unit', 'pieces')))
        details_layout.addRow("Unit:", self.unit_combo)

        layout.addWidget(details_group)

        # Cost and stock
        cost_group = QGroupBox("Cost & Stock")
        cost_layout = QFormLayout(cost_group)

        # Make cost per unit read-only since it's calculated from purchase history
        cost_value = float(self.material_data.get('cost_per_unit', 0))
        self.cost_label = QLabel(f"₹{cost_value:.2f}")
        self.cost_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        self.cost_label.setToolTip("This field is calculated automatically from purchase history average")
        cost_layout.addRow("Cost per Unit (₹):", self.cost_label)

        self.current_stock_spin = QSpinBox()
        self.current_stock_spin.setMaximum(99999)
        self.current_stock_spin.setValue(int(self.material_data.get('current_stock', 0)))
        cost_layout.addRow("Current Stock:", self.current_stock_spin)

        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setMaximum(9999)
        self.min_stock_spin.setValue(int(self.material_data.get('minimum_stock', 10)))
        cost_layout.addRow("Minimum Stock:", self.min_stock_spin)

        layout.addWidget(cost_group)

        # Supplier info
        supplier_group = QGroupBox("Supplier Information")
        supplier_layout = QFormLayout(supplier_group)

        self.supplier_edit = QLineEdit()
        self.supplier_edit.setText(str(self.material_data.get('supplier', '')))
        supplier_layout.addRow("Supplier:", self.supplier_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlainText(str(self.material_data.get('notes', '')))
        supplier_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(supplier_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def accept(self):
        """Save the changes"""
        try:
            material_id = self.material_data['material_id']

            # Validate inputs
            material_name = self.name_edit.text().strip()
            if not material_name:
                QMessageBox.warning(self, "Validation Error", "Material name cannot be empty")
                return

            # Update the material in the dataframe
            mask = self.data['packing_materials']['material_id'] == material_id
            if not mask.any():
                QMessageBox.critical(self, "Error", "Material not found in database")
                return

            # Update all fields, ensuring proper data types
            self.data['packing_materials'].loc[mask, 'material_name'] = material_name
            self.data['packing_materials'].loc[mask, 'category'] = self.category_combo.currentText()
            self.data['packing_materials'].loc[mask, 'size'] = self.size_edit.text().strip()
            self.data['packing_materials'].loc[mask, 'unit'] = self.unit_combo.currentText()
            # Keep the existing cost_per_unit (it's calculated from purchase history)
            self.data['packing_materials'].loc[mask, 'current_stock'] = float(self.current_stock_spin.value())
            self.data['packing_materials'].loc[mask, 'minimum_stock'] = float(self.min_stock_spin.value())
            self.data['packing_materials'].loc[mask, 'supplier'] = self.supplier_edit.text().strip()
            self.data['packing_materials'].loc[mask, 'notes'] = self.notes_edit.toPlainText().strip()

            # Save to CSV with error handling
            try:
                os.makedirs('data', exist_ok=True)
                self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

                # Force refresh the parent widget if it has the method
                if hasattr(self.parent(), 'refresh_data_display'):
                    self.parent().refresh_data_display()
                elif hasattr(self.parent(), 'load_data'):
                    self.parent().load_data()
                    if hasattr(self.parent(), 'populate_materials_table'):
                        self.parent().populate_materials_table()

                super().accept()

            except Exception as save_error:
                self.logger.error(f"Error saving to CSV: {save_error}")
                QMessageBox.critical(self, "Save Error", f"Failed to save to file: {str(save_error)}")

        except Exception as e:
            self.logger.error(f"Error saving material changes: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
class AddMaterialDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = get_logger()
        self.setWindowTitle("Add Packing Material")
        self.setModal(True)
        self.resize(600, 700)
        self.setMinimumSize(550, 650)
        self.setMaximumSize(800, 900)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        # Create main scroll area to handle content overflow
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Main layout for the dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(scroll_area)

        # Content layout
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("Add New Packing Material")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Material details
        details_group = QGroupBox("Material Details")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                margin-bottom: 10px;
                padding-top: 20px;
                padding-bottom: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        details_layout = QFormLayout(details_group)
        details_layout.setSpacing(12)
        details_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        details_layout.setLabelAlignment(Qt.AlignRight)
        details_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        details_layout.setContentsMargins(15, 15, 15, 15)

        # Material name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter material name")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        details_layout.addRow("Material Name:", self.name_edit)

        # Category with add new option
        category_container = QWidget()
        category_layout = QHBoxLayout(category_container)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(8)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)

        # Load existing categories from data
        existing_categories = set()
        if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
            existing_categories.update(self.data['packing_materials']['category'].dropna().unique())

        # Default categories
        default_categories = [
            "Boxes", "Plastic Covers", "Plastic Bags", "Bottles",
            "Wrapping", "Protection", "Sealing", "Labeling",
            "Containers", "Bags"
        ]

        # Combine and sort categories
        all_categories = sorted(list(existing_categories.union(set(default_categories))))
        self.category_combo.addItems(all_categories)

        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QComboBox:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 5px;
            }
        """)

        # Add tooltip and placeholder to indicate it's editable
        self.category_combo.setToolTip("Select existing category or type a new one")
        self.category_combo.lineEdit().setPlaceholderText("Select or type category...")

        category_layout.addWidget(self.category_combo)

        # Add new category button
        add_category_btn = QPushButton("+ New")
        add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                min-width: 50px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        add_category_btn.clicked.connect(self.add_new_category)
        add_category_btn.setToolTip("Add a new category")
        category_layout.addWidget(add_category_btn)

        details_layout.addRow("Category:", category_container)

        # Size
        self.size_edit = QLineEdit()
        self.size_edit.setPlaceholderText("e.g., Small, Medium, Large, 250ml")
        self.size_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        details_layout.addRow("Size:", self.size_edit)

        # Unit with add new option
        unit_container = QWidget()
        unit_layout = QHBoxLayout(unit_container)
        unit_layout.setContentsMargins(0, 0, 0, 0)
        unit_layout.setSpacing(8)

        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)

        # Load existing units from data
        existing_units = set()
        if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
            existing_units.update(self.data['packing_materials']['unit'].dropna().unique())

        # Default units
        default_units = ["pieces", "rolls", "sheets", "kg", "meters", "liters", "boxes", "packs"]

        # Combine and sort units
        all_units = sorted(list(existing_units.union(set(default_units))))
        self.unit_combo.addItems(all_units)

        self.unit_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QComboBox:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 5px;
            }
        """)

        # Add tooltip and placeholder to indicate it's editable
        self.unit_combo.setToolTip("Select existing unit or type a new one")
        self.unit_combo.lineEdit().setPlaceholderText("Select or type unit...")

        unit_layout.addWidget(self.unit_combo)

        # Add new unit button
        add_unit_btn = QPushButton("+ New")
        add_unit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                min-width: 50px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        add_unit_btn.clicked.connect(self.add_new_unit)
        add_unit_btn.setToolTip("Add a new unit")
        unit_layout.addWidget(add_unit_btn)

        details_layout.addRow("Unit:", unit_container)

        layout.addWidget(details_group)

        # Cost and stock
        cost_group = QGroupBox("Cost & Stock")
        cost_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                margin-bottom: 10px;
                padding-top: 20px;
                padding-bottom: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        cost_layout = QFormLayout(cost_group)
        cost_layout.setSpacing(12)
        cost_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        cost_layout.setLabelAlignment(Qt.AlignRight)
        cost_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        cost_layout.setContentsMargins(15, 15, 15, 15)

        # Cost per unit (read-only since it should be calculated from purchases)
        cost_value = 0.0
        self.cost_label = QLabel(f"₹{cost_value:.2f}")
        self.cost_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        self.cost_label.setToolTip("This field will be calculated automatically from purchase history")
        cost_layout.addRow("Cost per Unit (₹):", self.cost_label)

        # Current stock
        self.current_stock_spin = QSpinBox()
        self.current_stock_spin.setMaximum(99999)
        self.current_stock_spin.setValue(0)
        self.current_stock_spin.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QSpinBox:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        cost_layout.addRow("Current Stock:", self.current_stock_spin)

        # Minimum stock
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setMaximum(9999)
        self.min_stock_spin.setValue(10)
        self.min_stock_spin.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QSpinBox:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        cost_layout.addRow("Minimum Stock:", self.min_stock_spin)

        layout.addWidget(cost_group)

        # Supplier info
        supplier_group = QGroupBox("Supplier Information")
        supplier_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                margin-bottom: 10px;
                padding-top: 20px;
                padding-bottom: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        supplier_layout = QFormLayout(supplier_group)
        supplier_layout.setSpacing(12)
        supplier_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        supplier_layout.setLabelAlignment(Qt.AlignRight)
        supplier_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        supplier_layout.setContentsMargins(15, 15, 15, 15)

        # Supplier name
        self.supplier_edit = QLineEdit()
        self.supplier_edit.setPlaceholderText("Supplier name")
        self.supplier_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        supplier_layout.addRow("Supplier:", self.supplier_edit)

        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(90)
        self.notes_edit.setMinimumHeight(70)
        self.notes_edit.setPlaceholderText("Additional notes...")
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
                font-size: 11px;
            }
            QTextEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        supplier_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(supplier_group)

        # Add flexible spacing before buttons
        layout.addStretch()
        layout.addSpacing(20)

        # Buttons container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.setSpacing(15)
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Add Material")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)

        layout.addWidget(button_container)

    def add_new_category(self):
        """Add a new category to the combo box"""
        from PySide6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(
            self,
            'Add New Category',
            'Enter new category name:',
            text=""
        )

        if ok and text.strip():
            category_name = text.strip()

            # Check if category already exists
            existing_items = [self.category_combo.itemText(i) for i in range(self.category_combo.count())]
            if category_name not in existing_items:
                self.category_combo.addItem(category_name)
                self.category_combo.setCurrentText(category_name)
            else:
                self.category_combo.setCurrentText(category_name)

    def add_new_unit(self):
        """Add a new unit to the combo box"""
        from PySide6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(
            self,
            'Add New Unit',
            'Enter new unit name:',
            text=""
        )

        if ok and text.strip():
            unit_name = text.strip()

            # Check if unit already exists
            existing_items = [self.unit_combo.itemText(i) for i in range(self.unit_combo.count())]
            if unit_name not in existing_items:
                self.unit_combo.addItem(unit_name)
                self.unit_combo.setCurrentText(unit_name)
            else:
                self.unit_combo.setCurrentText(unit_name)

    def accept(self):
        """Save the new material"""
        try:
            # Validate inputs
            if not self.name_edit.text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter a material name")
                return

            # Generate new ID
            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                next_id = self.data['packing_materials']['material_id'].max() + 1
            else:
                next_id = 1

            # Create new material (cost_per_unit starts at 0 and will be calculated from purchases)
            new_material = pd.DataFrame({
                'material_id': [next_id],
                'material_name': [self.name_edit.text().strip()],
                'category': [self.category_combo.currentText()],
                'size': [self.size_edit.text().strip()],
                'unit': [self.unit_combo.currentText()],
                'cost_per_unit': [0.0],  # Will be calculated from purchase history
                'current_stock': [self.current_stock_spin.value()],
                'minimum_stock': [self.min_stock_spin.value()],
                'supplier': [self.supplier_edit.text().strip()],
                'notes': [self.notes_edit.toPlainText().strip()],
                'date_added': [datetime.now().strftime('%Y-%m-%d')]
            })

            # Add to dataframe
            if 'packing_materials' not in self.data:
                self.data['packing_materials'] = new_material
            else:
                self.data['packing_materials'] = pd.concat([self.data['packing_materials'], new_material], ignore_index=True)

            # Save to CSV
            os.makedirs('data', exist_ok=True)
            self.data['packing_materials'].to_csv('data/packing_materials.csv', index=False, encoding='utf-8')

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save material: {str(e)}")


class AddRecipeMaterialDialog(QDialog):
    """Dialog for adding material to recipe"""

    def __init__(self, data, recipe_name, parent=None):
        super().__init__(parent)
        self.data = data
        self.recipe_name = recipe_name
        self.logger = get_logger()
        self.setWindowTitle(f"Add Material to {recipe_name}")
        self.setModal(True)
        self.resize(450, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_label = QLabel(f"Add Packing Material to Recipe")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        recipe_label = QLabel(f"Recipe: <b>{self.recipe_name}</b>")
        recipe_label.setStyleSheet("color: #34495e; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(recipe_label)

        # Material selection
        material_group = QGroupBox("Material Selection")
        material_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        material_layout = QFormLayout(material_group)
        material_layout.setSpacing(15)

        # Material dropdown
        self.material_combo = QComboBox()
        self.material_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 5px;
            }
        """)

        if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
            materials = self.data['packing_materials']['material_name'].tolist()
            self.material_combo.addItems(materials)
            self.material_combo.currentTextChanged.connect(self.update_cost_preview)

        material_layout.addRow("Material:", self.material_combo)

        # Quantity input
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                min-height: 20px;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """)
        self.quantity_spin.setMinimum(0.1)
        self.quantity_spin.setMaximum(999.99)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.valueChanged.connect(self.update_cost_preview)
        material_layout.addRow("Quantity Needed:", self.quantity_spin)

        # Cost preview
        self.cost_preview_label = QLabel("Cost per Recipe: ₹0.00")
        self.cost_preview_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        material_layout.addRow("", self.cost_preview_label)

        layout.addWidget(material_group)

        # Notes
        notes_group = QGroupBox("Notes")
        notes_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        notes_layout = QVBoxLayout(notes_group)

        self.notes_edit = QTextEdit()
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Usage notes...")
        notes_layout.addWidget(self.notes_edit)

        layout.addWidget(notes_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Update initial cost preview
        self.update_cost_preview()

    def update_cost_preview(self):
        """Update cost preview when material or quantity changes"""
        try:
            material_name = self.material_combo.currentText()
            if not material_name:
                self.cost_preview_label.setText("Cost per Recipe: ₹0.00")
                return

            # Get material cost
            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                material_match = self.data['packing_materials'][
                    self.data['packing_materials']['material_name'] == material_name
                ]

                if not material_match.empty:
                    cost_per_unit = float(material_match.iloc[0].get('cost_per_unit', 0))
                    total_cost = cost_per_unit * self.quantity_spin.value()
                    self.cost_preview_label.setText(f"Cost per Recipe: ₹{total_cost:.2f}")

                    # Show unit cost info
                    unit_info = f"(₹{cost_per_unit:.2f} × {self.quantity_spin.value():.2f})"
                    self.cost_preview_label.setToolTip(f"Unit cost: ₹{cost_per_unit:.2f}\nQuantity: {self.quantity_spin.value():.2f}\nTotal: ₹{total_cost:.2f}")
                else:
                    self.cost_preview_label.setText("Cost per Recipe: ₹0.00")
            else:
                self.cost_preview_label.setText("Cost per Recipe: ₹0.00")
        except Exception as e:
            self.logger.error(f"Error updating cost preview: {e}")
            self.cost_preview_label.setText("Cost per Recipe: ₹0.00")

    def accept(self):
        """Save the recipe-material association"""
        try:
            material_name = self.material_combo.currentText()
            if not material_name:
                QMessageBox.warning(self, "Validation Error", "Please select a material")
                return

            quantity = self.quantity_spin.value()
            if quantity <= 0:
                QMessageBox.warning(self, "Validation Error", "Quantity must be greater than 0")
                return

            # Check if association already exists
            if 'recipe_packing_materials' in self.data and not self.data['recipe_packing_materials'].empty:
                existing = self.data['recipe_packing_materials'][
                    (self.data['recipe_packing_materials']['recipe_name'] == self.recipe_name) &
                    (self.data['recipe_packing_materials']['material_name'] == material_name)
                ]

                if not existing.empty:
                    reply = QMessageBox.question(
                        self, "Material Already Exists",
                        f"{material_name} is already assigned to {self.recipe_name}.\n\nDo you want to update the existing assignment?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )

                    if reply == QMessageBox.No:
                        return
                    else:
                        # Update existing association
                        mask = (self.data['recipe_packing_materials']['recipe_name'] == self.recipe_name) & \
                               (self.data['recipe_packing_materials']['material_name'] == material_name)

                        # Get material cost
                        material_match = self.data['packing_materials'][
                            self.data['packing_materials']['material_name'] == material_name
                        ]
                        cost_per_unit = float(material_match.iloc[0].get('cost_per_unit', 0)) if not material_match.empty else 0
                        cost_per_recipe = cost_per_unit * quantity

                        self.data['recipe_packing_materials'].loc[mask, 'quantity_needed'] = quantity
                        self.data['recipe_packing_materials'].loc[mask, 'cost_per_recipe'] = cost_per_recipe
                        self.data['recipe_packing_materials'].loc[mask, 'notes'] = self.notes_edit.toPlainText().strip()

                        # Save to CSV
                        self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)

                        # Force refresh parent widget data
                        self.force_refresh_parent_data()

                        QMessageBox.information(self, "Success", f"Updated {material_name} assignment for {self.recipe_name}")
                        super().accept()
                        return

            # Get recipe ID
            recipe_id = 1  # Default
            if 'recipes' in self.data and not self.data['recipes'].empty:
                recipe_match = self.data['recipes'][self.data['recipes']['recipe_name'] == self.recipe_name]
                if not recipe_match.empty:
                    recipe_id = recipe_match.iloc[0].get('recipe_id', 1)

            # Get material ID and cost
            material_id = 1  # Default
            cost_per_recipe = 0
            if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
                material_match = self.data['packing_materials'][self.data['packing_materials']['material_name'] == material_name]
                if not material_match.empty:
                    material_id = material_match.iloc[0].get('material_id', 1)
                    cost_per_unit = float(material_match.iloc[0].get('cost_per_unit', 0))
                    cost_per_recipe = cost_per_unit * quantity

            # Create new association
            new_association = pd.DataFrame({
                'recipe_id': [recipe_id],
                'recipe_name': [self.recipe_name],
                'material_id': [material_id],
                'material_name': [material_name],
                'quantity_needed': [quantity],
                'cost_per_recipe': [cost_per_recipe],
                'notes': [self.notes_edit.toPlainText().strip()]
            })

            # Add to dataframe
            if 'recipe_packing_materials' not in self.data:
                self.data['recipe_packing_materials'] = new_association
            else:
                self.data['recipe_packing_materials'] = pd.concat([self.data['recipe_packing_materials'], new_association], ignore_index=True)

            # Save to CSV
            self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)

            # Force refresh parent widget data
            self.force_refresh_parent_data()

            QMessageBox.information(self, "Success", f"Added {material_name} to {self.recipe_name}")
            super().accept()

        except Exception as e:
            self.logger.error(f"Error saving material association: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save association: {str(e)}")

    def force_refresh_parent_data(self):
        """Force refresh of parent widget data after saving"""
        try:
            # Reload recipe packing materials from CSV to sync in-memory data
            csv_file = 'data/recipe_packing_materials.csv'
            if os.path.exists(csv_file):
                old_count = len(self.data.get('recipe_packing_materials', pd.DataFrame()))
                self.data['recipe_packing_materials'] = pd.read_csv(csv_file)
                new_count = len(self.data['recipe_packing_materials'])
                self.logger.info(f"🔄 Refreshed recipe packing materials: {old_count} → {new_count} associations")

                # Verify the specific recipe data
                if hasattr(self, 'recipe_name'):
                    recipe_materials = self.data['recipe_packing_materials'][
                        self.data['recipe_packing_materials']['recipe_name'] == self.recipe_name
                    ]
                    self.logger.info(f"🔍 {self.recipe_name} now has {len(recipe_materials)} materials")

            # Force refresh the parent widget display
            parent = self.parent()
            if parent:
                # Try multiple refresh methods in order of preference
                if hasattr(parent, 'load_recipe_materials'):
                    parent.load_recipe_materials()
                    self.logger.info("✅ Called parent.load_recipe_materials()")

                if hasattr(parent, 'update_recipe_cost_summary'):
                    # Recalculate and update the cost summary
                    if hasattr(self, 'recipe_name') and 'recipe_packing_materials' in self.data:
                        recipe_materials = self.data['recipe_packing_materials'][
                            self.data['recipe_packing_materials']['recipe_name'] == self.recipe_name
                        ]
                        total_cost = recipe_materials['cost_per_recipe'].sum() if not recipe_materials.empty else 0.0
                        parent.update_recipe_cost_summary(len(recipe_materials), total_cost)
                        self.logger.info(f"✅ Updated cost summary: {len(recipe_materials)} materials, ₹{total_cost:.2f}")

                if hasattr(parent, 'data_changed'):
                    parent.data_changed.emit()
                    self.logger.info("✅ Emitted data_changed signal")

                # Force table refresh by clearing and reloading
                if hasattr(parent, 'recipe_materials_table'):
                    current_recipe = getattr(parent, 'recipe_combo', None)
                    if current_recipe and hasattr(current_recipe, 'currentText'):
                        recipe_name = current_recipe.currentText()
                        if recipe_name != "Select Recipe...":
                            self.logger.info(f"🔄 Force refreshing table for recipe: {recipe_name}")
                            parent.load_recipe_materials()

        except Exception as e:
            self.logger.error(f"❌ Error refreshing parent data: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")


class BulkAssignMaterialsDialog(QDialog):
    """Dialog for bulk assigning materials to multiple recipes"""

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = get_logger()
        self.setWindowTitle("Bulk Assign Materials")
        self.setModal(True)
        self.resize(900, 700)
        self.setMinimumSize(800, 600)
        self.all_materials = []
        self.all_recipes = []
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("Bulk Assign Packing Materials")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Main content in horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # Left side - Materials
        materials_container = QWidget()
        materials_container_layout = QVBoxLayout(materials_container)
        materials_container_layout.setContentsMargins(0, 0, 0, 0)
        materials_container_layout.setSpacing(10)

        # Material selection
        material_group = QGroupBox("Select Materials")
        material_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        material_layout = QVBoxLayout(material_group)
        material_layout.setSpacing(10)

        # Material search
        material_search_layout = QHBoxLayout()
        material_search_label = QLabel("Search:")
        material_search_label.setMinimumWidth(50)
        self.material_search = QLineEdit()
        self.material_search.setPlaceholderText("Search materials...")
        self.material_search.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.material_search.textChanged.connect(self.filter_materials)
        material_search_layout.addWidget(material_search_label)
        material_search_layout.addWidget(self.material_search)
        material_layout.addLayout(material_search_layout)

        # Materials list
        self.materials_list = QListWidget()
        self.materials_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.materials_list.setMinimumHeight(300)
        self.materials_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)

        # Load materials
        self.load_materials()
        material_layout.addWidget(self.materials_list)

        # Material selection info
        self.material_count_label = QLabel("0 materials selected")
        self.material_count_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        material_layout.addWidget(self.material_count_label)
        self.materials_list.itemSelectionChanged.connect(self.update_selection_counts)

        materials_container_layout.addWidget(material_group)
        main_layout.addWidget(materials_container)

        # Right side - Recipes
        recipes_container = QWidget()
        recipes_container_layout = QVBoxLayout(recipes_container)
        recipes_container_layout.setContentsMargins(0, 0, 0, 0)
        recipes_container_layout.setSpacing(10)

        # Recipe selection
        recipe_group = QGroupBox("Select Recipes")
        recipe_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        recipe_layout = QVBoxLayout(recipe_group)
        recipe_layout.setSpacing(10)

        # Recipe search
        recipe_search_layout = QHBoxLayout()
        recipe_search_label = QLabel("Search:")
        recipe_search_label.setMinimumWidth(50)
        self.recipe_search = QLineEdit()
        self.recipe_search.setPlaceholderText("Search recipes...")
        self.recipe_search.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.recipe_search.textChanged.connect(self.filter_recipes)
        recipe_search_layout.addWidget(recipe_search_label)
        recipe_search_layout.addWidget(self.recipe_search)
        recipe_layout.addLayout(recipe_search_layout)

        # Recipes list
        self.recipes_list = QListWidget()
        self.recipes_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.recipes_list.setMinimumHeight(300)
        self.recipes_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)

        # Load recipes
        self.load_recipes()
        recipe_layout.addWidget(self.recipes_list)

        # Recipe selection info and controls
        recipe_controls_layout = QHBoxLayout()
        self.recipe_count_label = QLabel("0 recipes selected")
        self.recipe_count_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        recipe_controls_layout.addWidget(self.recipe_count_label)

        recipe_controls_layout.addStretch()

        # Select all recipes button
        select_all_recipes_btn = QPushButton("Select All")
        select_all_recipes_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        select_all_recipes_btn.clicked.connect(self.select_all_recipes)
        recipe_controls_layout.addWidget(select_all_recipes_btn)

        # Clear selection button
        clear_recipes_btn = QPushButton("Clear")
        clear_recipes_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_recipes_btn.clicked.connect(self.clear_recipe_selection)
        recipe_controls_layout.addWidget(clear_recipes_btn)

        recipe_layout.addLayout(recipe_controls_layout)
        self.recipes_list.itemSelectionChanged.connect(self.update_selection_counts)

        recipes_container_layout.addWidget(recipe_group)
        main_layout.addWidget(recipes_container)

        layout.addLayout(main_layout)

        # Assignment details
        details_group = QGroupBox("Assignment Details")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        details_layout = QFormLayout(details_group)
        details_layout.setSpacing(12)

        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.1)
        self.quantity_spin.setMaximum(999.99)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """)
        details_layout.addRow("Default Quantity:", self.quantity_spin)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Optional notes for all assignments")
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 11px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        details_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(details_group)

        # Selection summary
        summary_group = QGroupBox("Assignment Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #27ae60;
                background-color: white;
            }
        """)
        summary_layout = QVBoxLayout(summary_group)

        self.summary_label = QLabel("Select materials and recipes to see assignment summary")
        self.summary_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 10px;")
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)

        layout.addWidget(summary_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        assign_btn = QPushButton("Assign Materials")
        assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        assign_btn.clicked.connect(self.assign_materials)
        button_layout.addWidget(assign_btn)

        layout.addLayout(button_layout)

    def load_materials(self):
        """Load all materials into the list"""
        self.all_materials = []
        if 'packing_materials' in self.data and not self.data['packing_materials'].empty:
            for _, material in self.data['packing_materials'].iterrows():
                material_info = {
                    'name': material['material_name'],
                    'cost': float(material['cost_per_unit']),
                    'category': material.get('category', ''),
                    'unit': material.get('unit', ''),
                    'display': f"{material['material_name']} - ₹{material['cost_per_unit']:.2f} ({material.get('category', 'N/A')})"
                }
                self.all_materials.append(material_info)
        self.filter_materials()

    def load_recipes(self):
        """Load all recipes into the list"""
        self.all_recipes = []
        if 'recipes' in self.data and not self.data['recipes'].empty:
            for recipe_name in self.data['recipes']['recipe_name'].tolist():
                self.all_recipes.append(recipe_name)
        self.filter_recipes()

    def filter_materials(self):
        """Filter materials based on search text"""
        search_text = self.material_search.text().lower()
        self.materials_list.clear()

        for material in self.all_materials:
            if (search_text in material['name'].lower() or
                search_text in material['category'].lower() or
                search_text in material['unit'].lower()):
                item = QListWidgetItem(material['display'])
                item.setData(Qt.UserRole, material['name'])
                self.materials_list.addItem(item)

    def filter_recipes(self):
        """Filter recipes based on search text"""
        search_text = self.recipe_search.text().lower()
        self.recipes_list.clear()

        for recipe_name in self.all_recipes:
            if search_text in recipe_name.lower():
                item = QListWidgetItem(recipe_name)
                self.recipes_list.addItem(item)

    def select_all_recipes(self):
        """Select all recipes in the list"""
        for i in range(self.recipes_list.count()):
            item = self.recipes_list.item(i)
            item.setSelected(True)

    def clear_recipe_selection(self):
        """Clear all recipe selections"""
        self.recipes_list.clearSelection()

    def update_selection_counts(self):
        """Update selection count labels and summary"""
        material_count = len(self.materials_list.selectedItems())
        recipe_count = len(self.recipes_list.selectedItems())

        self.material_count_label.setText(f"{material_count} materials selected")
        self.recipe_count_label.setText(f"{recipe_count} recipes selected")

        # Update summary
        if material_count > 0 and recipe_count > 0:
            total_assignments = material_count * recipe_count
            self.summary_label.setText(
                f"Ready to create {total_assignments} assignments:\n"
                f"• {material_count} materials × {recipe_count} recipes\n"
                f"• Default quantity: {self.quantity_spin.value():.2f} per assignment"
            )
            self.summary_label.setStyleSheet("color: #27ae60; font-size: 11px; padding: 10px; font-weight: bold;")
        else:
            self.summary_label.setText("Select materials and recipes to see assignment summary")
            self.summary_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 10px;")

    def assign_materials(self):
        """Assign selected materials to selected recipes"""
        try:
            # Get selected materials
            selected_materials = []
            for item in self.materials_list.selectedItems():
                material_name = item.data(Qt.UserRole)
                selected_materials.append(material_name)

            # Get selected recipes
            selected_recipes = []
            for item in self.recipes_list.selectedItems():
                selected_recipes.append(item.text())

            if not selected_materials:
                notify_error("Error", "Please select at least one material", parent=self)
                return

            if not selected_recipes:
                notify_error("Error", "Please select at least one recipe", parent=self)
                return

            quantity = self.quantity_spin.value()
            notes = self.notes_edit.toPlainText().strip()

            # Show confirmation dialog
            total_assignments = len(selected_materials) * len(selected_recipes)
            reply = QMessageBox.question(
                self, "Confirm Bulk Assignment",
                f"This will create {total_assignments} material assignments:\n\n"
                f"• {len(selected_materials)} materials\n"
                f"• {len(selected_recipes)} recipes\n"
                f"• Quantity: {quantity:.2f} per assignment\n\n"
                f"Existing assignments will be skipped.\n\n"
                f"Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply != QMessageBox.Yes:
                return

            # Create assignments
            assignments_created = 0
            assignments_skipped = 0

            for recipe_name in selected_recipes:
                # Get recipe ID
                recipe_match = self.data['recipes'][self.data['recipes']['recipe_name'] == recipe_name]
                if recipe_match.empty:
                    continue
                recipe_id = recipe_match.iloc[0]['recipe_id']

                for material_name in selected_materials:
                    # Check if association already exists
                    if 'recipe_packing_materials' in self.data and not self.data['recipe_packing_materials'].empty:
                        existing = self.data['recipe_packing_materials'][
                            (self.data['recipe_packing_materials']['recipe_name'] == recipe_name) &
                            (self.data['recipe_packing_materials']['material_name'] == material_name)
                        ]
                    else:
                        existing = pd.DataFrame()

                    if existing.empty:
                        # Get material details
                        material_match = self.data['packing_materials'][
                            self.data['packing_materials']['material_name'] == material_name
                        ]

                        if not material_match.empty:
                            material_id = material_match.iloc[0]['material_id']
                            cost_per_unit = float(material_match.iloc[0]['cost_per_unit'])
                            cost_per_recipe = cost_per_unit * quantity

                            # Create new association
                            new_association = pd.DataFrame({
                                'recipe_id': [recipe_id],
                                'recipe_name': [recipe_name],
                                'material_id': [material_id],
                                'material_name': [material_name],
                                'quantity_needed': [quantity],
                                'cost_per_recipe': [cost_per_recipe],
                                'notes': [notes]
                            })

                            # Add to dataframe
                            if 'recipe_packing_materials' not in self.data:
                                self.data['recipe_packing_materials'] = new_association
                            else:
                                self.data['recipe_packing_materials'] = pd.concat([
                                    self.data['recipe_packing_materials'], new_association
                                ], ignore_index=True)

                            assignments_created += 1
                    else:
                        assignments_skipped += 1

            # Save to CSV
            if assignments_created > 0:
                self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)

                message = f"Successfully created {assignments_created} material assignments!"
                if assignments_skipped > 0:
                    message += f"\n\n{assignments_skipped} assignments were skipped (already exist)."

                notify_success("Success", message, parent=self)
                super().accept()
            else:
                notify_error("Info", "No new assignments were created.\nAll selected combinations already exist.", parent=self)

        except Exception as e:
            self.logger.error(f"Error in bulk assign materials: {e}")
            notify_error("Error", f"Failed to assign materials: {str(e)}", parent=self)


class UnassignedRecipesDialog(QDialog):
    """Dialog showing recipes without packing materials assigned"""

    def __init__(self, unassigned_recipes, data, parent=None):
        super().__init__(parent)
        self.unassigned_recipes = unassigned_recipes
        self.data = data
        self.logger = get_logger()
        self.setWindowTitle("Recipes Without Packing Materials")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel(f"Found {len(self.unassigned_recipes)} recipes without packing materials")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #e67e22; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Info text
        info_label = QLabel("These recipes don't have any packing materials assigned. You can bulk assign materials to them using the buttons below.")
        info_label.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Recipes list
        self.recipes_list = QListWidget()
        self.recipes_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.recipes_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #e67e22;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f39c12;
                color: white;
            }
        """)

        # Populate list
        for recipe in sorted(self.unassigned_recipes):
            item = QListWidgetItem(recipe)
            self.recipes_list.addItem(item)

        layout.addWidget(self.recipes_list)

        # Selection info
        self.selection_label = QLabel("0 recipes selected")
        self.selection_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        self.recipes_list.itemSelectionChanged.connect(self.update_selection_count)
        layout.addWidget(self.selection_label)

        # Buttons
        button_layout = QHBoxLayout()

        # Select all button
        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)

        # Bulk assign button
        bulk_assign_btn = QPushButton("Bulk Assign to Selected")
        bulk_assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #229954;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        bulk_assign_btn.clicked.connect(self.bulk_assign_selected)
        button_layout.addWidget(bulk_assign_btn)

        button_layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: 1px solid #7f8c8d;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def update_selection_count(self):
        """Update selection count label"""
        count = len(self.recipes_list.selectedItems())
        self.selection_label.setText(f"{count} recipes selected")

    def select_all(self):
        """Select all recipes"""
        for i in range(self.recipes_list.count()):
            item = self.recipes_list.item(i)
            item.setSelected(True)

    def bulk_assign_selected(self):
        """Open bulk assign dialog with selected recipes"""
        selected_recipes = [item.text() for item in self.recipes_list.selectedItems()]

        if not selected_recipes:
            notify_error("Error", "Please select at least one recipe", parent=self)
            return

        # Create a modified bulk assign dialog that pre-selects these recipes
        dialog = BulkAssignMaterialsDialog(self.data, self)

        # Pre-select the recipes in the dialog
        dialog.show()

        # Select the recipes in the dialog's list
        for i in range(dialog.recipes_list.count()):
            item = dialog.recipes_list.item(i)
            if item.text() in selected_recipes:
                item.setSelected(True)

        if dialog.exec() == QDialog.Accepted:
            self.accept()  # Close this dialog too


class CopyMaterialsDialog(QDialog):
    """Dialog for copying materials from another recipe"""

    def __init__(self, data, target_recipe, parent=None):
        super().__init__(parent)
        self.data = data
        self.target_recipe = target_recipe
        self.logger = get_logger()
        self.setWindowTitle("Copy Materials from Recipe")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Info label
        info_label = QLabel(f"Copy materials to: <b>{self.target_recipe}</b>")
        info_label.setStyleSheet("font-size: 12px; color: #2c3e50; padding: 10px;")
        layout.addWidget(info_label)

        # Source recipe selection
        source_group = QGroupBox("Select Source Recipe")
        source_layout = QVBoxLayout(source_group)

        self.source_combo = QComboBox()
        if 'recipes' in self.data and not self.data['recipes'].empty:
            recipes = [r for r in self.data['recipes']['recipe_name'].tolist() if r != self.target_recipe]
            self.source_combo.addItems(recipes)
        self.source_combo.currentTextChanged.connect(self.load_source_materials)
        source_layout.addWidget(self.source_combo)

        layout.addWidget(source_group)

        # Materials preview
        preview_group = QGroupBox("Materials to Copy")
        preview_layout = QVBoxLayout(preview_group)

        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(4)
        self.materials_table.setHorizontalHeaderLabels([
            "Material Name", "Quantity", "Cost/Unit", "Total Cost"
        ])
        self.materials_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.materials_table.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.materials_table)

        layout.addWidget(preview_group)

        # Options
        options_group = QGroupBox("Copy Options")
        options_layout = QVBoxLayout(options_group)

        self.replace_existing_cb = QCheckBox("Replace existing materials")
        self.replace_existing_cb.setToolTip("If checked, existing materials will be replaced. Otherwise, only new materials will be added.")
        options_layout.addWidget(self.replace_existing_cb)

        self.copy_quantities_cb = QCheckBox("Copy quantities")
        self.copy_quantities_cb.setChecked(True)
        self.copy_quantities_cb.setToolTip("If unchecked, default quantity of 1 will be used")
        options_layout.addWidget(self.copy_quantities_cb)

        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        copy_btn = QPushButton("Copy Materials")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        copy_btn.clicked.connect(self.copy_materials)
        button_layout.addWidget(copy_btn)

        layout.addLayout(button_layout)

        # Load initial data
        if self.source_combo.count() > 0:
            self.load_source_materials()

    def load_source_materials(self):
        """Load materials from selected source recipe"""
        try:
            source_recipe = self.source_combo.currentText()
            if not source_recipe:
                self.materials_table.setRowCount(0)
                return

            # Get materials for source recipe
            if 'recipe_packing_materials' not in self.data:
                self.materials_table.setRowCount(0)
                return

            source_materials = self.data['recipe_packing_materials'][
                self.data['recipe_packing_materials']['recipe_name'] == source_recipe
            ]

            self.materials_table.setRowCount(len(source_materials))

            for row, (_, material) in enumerate(source_materials.iterrows()):
                material_name = material.get('material_name', '')
                quantity = float(material.get('quantity_needed', 0))

                # Get cost from packing materials
                material_match = self.data['packing_materials'][
                    self.data['packing_materials']['material_name'] == material_name
                ]

                if not material_match.empty:
                    cost_per_unit = float(material_match.iloc[0].get('cost_per_unit', 0))
                    total_cost = cost_per_unit * quantity
                else:
                    cost_per_unit = 0.0
                    total_cost = 0.0

                self.materials_table.setItem(row, 0, QTableWidgetItem(material_name))
                self.materials_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
                self.materials_table.setItem(row, 2, QTableWidgetItem(f"₹{cost_per_unit:.2f}"))
                self.materials_table.setItem(row, 3, QTableWidgetItem(f"₹{total_cost:.2f}"))

        except Exception as e:
            self.logger.error(f"Error loading source materials: {e}")

    def copy_materials(self):
        """Copy materials to target recipe"""
        try:
            source_recipe = self.source_combo.currentText()
            if not source_recipe:
                notify_error("Error", "Please select a source recipe", parent=self)
                return

            # Get source materials
            source_materials = self.data['recipe_packing_materials'][
                self.data['recipe_packing_materials']['recipe_name'] == source_recipe
            ]

            if source_materials.empty:
                notify_error("Error", "No materials found in source recipe", parent=self)
                return

            # Get target recipe ID
            target_recipe_match = self.data['recipes'][self.data['recipes']['recipe_name'] == self.target_recipe]
            if target_recipe_match.empty:
                notify_error("Error", "Target recipe not found", parent=self)
                return
            target_recipe_id = target_recipe_match.iloc[0]['recipe_id']

            replace_existing = self.replace_existing_cb.isChecked()
            copy_quantities = self.copy_quantities_cb.isChecked()
            materials_copied = 0

            for _, material in source_materials.iterrows():
                material_name = material.get('material_name', '')
                quantity = float(material.get('quantity_needed', 1)) if copy_quantities else 1.0
                notes = material.get('notes', '')

                # Check if material already exists for target recipe
                existing = self.data['recipe_packing_materials'][
                    (self.data['recipe_packing_materials']['recipe_name'] == self.target_recipe) &
                    (self.data['recipe_packing_materials']['material_name'] == material_name)
                ]

                if not existing.empty and not replace_existing:
                    continue  # Skip existing materials

                # Get material details
                material_match = self.data['packing_materials'][
                    self.data['packing_materials']['material_name'] == material_name
                ]

                if material_match.empty:
                    continue  # Skip if material doesn't exist

                material_id = material_match.iloc[0]['material_id']
                cost_per_unit = float(material_match.iloc[0]['cost_per_unit'])
                cost_per_recipe = cost_per_unit * quantity

                if not existing.empty and replace_existing:
                    # Update existing
                    mask = (self.data['recipe_packing_materials']['recipe_name'] == self.target_recipe) & \
                           (self.data['recipe_packing_materials']['material_name'] == material_name)
                    self.data['recipe_packing_materials'].loc[mask, 'quantity_needed'] = quantity
                    self.data['recipe_packing_materials'].loc[mask, 'cost_per_recipe'] = cost_per_recipe
                    self.data['recipe_packing_materials'].loc[mask, 'notes'] = notes
                else:
                    # Create new association
                    new_association = pd.DataFrame({
                        'recipe_id': [target_recipe_id],
                        'recipe_name': [self.target_recipe],
                        'material_id': [material_id],
                        'material_name': [material_name],
                        'quantity_needed': [quantity],
                        'cost_per_recipe': [cost_per_recipe],
                        'notes': [notes]
                    })

                    self.data['recipe_packing_materials'] = pd.concat([
                        self.data['recipe_packing_materials'], new_association
                    ], ignore_index=True)

                materials_copied += 1

            # Save to CSV
            if materials_copied > 0:
                self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)
                notify_success("Success", f"Copied {materials_copied} materials to {self.target_recipe}", parent=self)
                super().accept()
            else:
                notify_error("Info", "No materials were copied", parent=self)

        except Exception as e:
            self.logger.error(f"Error copying materials: {e}")
            notify_error("Error", f"Failed to copy materials: {str(e)}", parent=self)


class EditRecipeMaterialDialog(QDialog):
    """Dialog for editing recipe material association"""

    def __init__(self, data, recipe_name, material_data, parent=None):
        super().__init__(parent)
        self.data = data
        self.recipe_name = recipe_name
        self.material_data = material_data
        self.logger = get_logger()
        self.setWindowTitle("Edit Recipe Material")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Info
        info_label = QLabel(f"Editing: <b>{self.material_data['material_name']}</b> for <b>{self.recipe_name}</b>")
        info_label.setStyleSheet("font-size: 12px; color: #2c3e50; padding: 10px;")
        layout.addWidget(info_label)

        # Material details (read-only)
        details_group = QGroupBox("Material Details")
        details_layout = QFormLayout(details_group)

        material_name_label = QLabel(self.material_data['material_name'])
        material_name_label.setStyleSheet("font-weight: bold;")
        details_layout.addRow("Material:", material_name_label)

        # Get material cost
        material_match = self.data['packing_materials'][
            self.data['packing_materials']['material_name'] == self.material_data['material_name']
        ]

        if not material_match.empty:
            cost_per_unit = float(material_match.iloc[0]['cost_per_unit'])
            category = material_match.iloc[0]['category']
        else:
            cost_per_unit = 0.0
            category = 'Unknown'

        category_label = QLabel(category)
        details_layout.addRow("Category:", category_label)

        cost_label = QLabel(f"₹{cost_per_unit:.2f}")
        details_layout.addRow("Cost per Unit:", cost_label)

        layout.addWidget(details_group)

        # Editable fields
        edit_group = QGroupBox("Edit Details")
        edit_layout = QFormLayout(edit_group)

        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(0.1)
        self.quantity_spin.setMaximum(999.99)
        self.quantity_spin.setValue(float(self.material_data.get('quantity_needed', 1)))
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.valueChanged.connect(self.update_cost_preview)
        edit_layout.addRow("Quantity Needed:", self.quantity_spin)

        self.cost_preview_label = QLabel()
        self.cost_preview_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        edit_layout.addRow("Cost per Recipe:", self.cost_preview_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlainText(self.material_data.get('notes', ''))
        edit_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(edit_group)

        # Update cost preview
        self.update_cost_preview()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def update_cost_preview(self):
        """Update cost preview when quantity changes"""
        try:
            material_match = self.data['packing_materials'][
                self.data['packing_materials']['material_name'] == self.material_data['material_name']
            ]

            if not material_match.empty:
                cost_per_unit = float(material_match.iloc[0]['cost_per_unit'])
                total_cost = cost_per_unit * self.quantity_spin.value()
                self.cost_preview_label.setText(f"₹{total_cost:.2f}")
            else:
                self.cost_preview_label.setText("₹0.00")
        except Exception as e:
            self.logger.error(f"Error updating cost preview: {e}")
            self.cost_preview_label.setText("₹0.00")

    def save_changes(self):
        """Save the changes"""
        try:
            # Calculate new cost
            material_match = self.data['packing_materials'][
                self.data['packing_materials']['material_name'] == self.material_data['material_name']
            ]

            if not material_match.empty:
                cost_per_unit = float(material_match.iloc[0]['cost_per_unit'])
                new_cost_per_recipe = cost_per_unit * self.quantity_spin.value()
            else:
                new_cost_per_recipe = 0.0

            # Update the data
            mask = (self.data['recipe_packing_materials']['recipe_name'] == self.recipe_name) & \
                   (self.data['recipe_packing_materials']['material_name'] == self.material_data['material_name'])

            self.data['recipe_packing_materials'].loc[mask, 'quantity_needed'] = self.quantity_spin.value()
            self.data['recipe_packing_materials'].loc[mask, 'cost_per_recipe'] = new_cost_per_recipe
            self.data['recipe_packing_materials'].loc[mask, 'notes'] = self.notes_edit.toPlainText().strip()

            # Save to CSV
            self.data['recipe_packing_materials'].to_csv('data/recipe_packing_materials.csv', index=False)

            super().accept()

        except Exception as e:
            self.logger.error(f"Error saving changes: {e}")
            notify_error("Error", f"Failed to save changes: {str(e)}", parent=self)

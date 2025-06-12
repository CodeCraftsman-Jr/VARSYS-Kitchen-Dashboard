"""
Order Management Module
Handles order creation, tracking, and management for different platforms
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTabWidget,
                             QPushButton, QComboBox, QDateEdit, QGroupBox,
                             QGridLayout, QFrame, QFormLayout, QLineEdit,
                             QSpinBox, QDoubleSpinBox, QMessageBox, QDialog,
                             QDialogButtonBox, QTextEdit, QCheckBox, QListWidget,
                             QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

class OrderItemWidget(QFrame):
    """Widget for individual order item"""
    
    item_changed = Signal()
    
    def __init__(self, recipes_data, parent=None):
        super().__init__(parent)
        self.recipes_data = recipes_data
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the order item UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        
        # Recipe selection
        self.recipe_combo = QComboBox()
        self.recipe_combo.setMinimumWidth(200)
        self.populate_recipes()
        self.recipe_combo.currentTextChanged.connect(self.on_recipe_changed)
        layout.addWidget(QLabel("Recipe:"))
        layout.addWidget(self.recipe_combo)
        
        # Quantity
        layout.addWidget(QLabel("Qty:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.valueChanged.connect(self.on_quantity_changed)
        layout.addWidget(self.quantity_spin)
        
        # Price (auto-filled)
        layout.addWidget(QLabel("Price:"))
        self.price_label = QLabel("₹0.00")
        self.price_label.setStyleSheet("font-weight: 600; color: #059669;")
        layout.addWidget(self.price_label)
        
        # Subtotal
        layout.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-weight: 600; color: #0f172a;")
        layout.addWidget(self.subtotal_label)
        
        # Remove button
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        layout.addWidget(self.remove_btn)
    
    def populate_recipes(self):
        """Populate recipe dropdown with available recipes"""
        try:
            if hasattr(self.recipes_data, 'recipe_pricing_data'):
                recipes = list(self.recipes_data.recipe_pricing_data.keys())
            else:
                # Fallback to sample recipes
                recipes = [
                    "Dosa", "Masala Dosa", "Idli(2 pcs)", "Coffee", "Tea(250 ml)",
                    "Chicken Gravy", "Fish Kolambu(Parai Fish)", "Plain Rice"
                ]
            
            self.recipe_combo.addItems(["Select Recipe..."] + sorted(recipes))
            
        except Exception as e:
            logging.error(f"Error populating recipes: {e}")
            self.recipe_combo.addItems(["Select Recipe..."])
    
    def on_recipe_changed(self):
        """Handle recipe selection change"""
        recipe_name = self.recipe_combo.currentText()
        
        if recipe_name == "Select Recipe...":
            self.price_label.setText("₹0.00")
        else:
            # Get price from recipe data
            price = self.get_recipe_price(recipe_name)
            self.price_label.setText(f"₹{price:.2f}")
        
        self.update_subtotal()
        self.item_changed.emit()
    
    def on_quantity_changed(self):
        """Handle quantity change"""
        self.update_subtotal()
        self.item_changed.emit()
    
    def get_recipe_price(self, recipe_name):
        """Get price for selected recipe"""
        try:
            if hasattr(self.recipes_data, 'recipe_pricing_data'):
                recipe_data = self.recipes_data.recipe_pricing_data.get(recipe_name, {})
                return recipe_data.get('our_pricing', 0)
            else:
                # Fallback prices
                fallback_prices = {
                    "Dosa": 62, "Masala Dosa": 115, "Idli(2 pcs)": 48,
                    "Coffee": 60, "Tea(250 ml)": 40, "Chicken Gravy": 100,
                    "Fish Kolambu(Parai Fish)": 750, "Plain Rice": 50
                }
                return fallback_prices.get(recipe_name, 0)
        except Exception as e:
            logging.error(f"Error getting recipe price: {e}")
            return 0
    
    def update_subtotal(self):
        """Update subtotal calculation"""
        try:
            price_text = self.price_label.text().replace('₹', '').replace(',', '')
            price = float(price_text) if price_text else 0
            quantity = self.quantity_spin.value()
            subtotal = price * quantity
            self.subtotal_label.setText(f"₹{subtotal:.2f}")
        except Exception as e:
            logging.error(f"Error updating subtotal: {e}")
            self.subtotal_label.setText("₹0.00")
    
    def get_item_data(self):
        """Get order item data"""
        try:
            recipe_name = self.recipe_combo.currentText()
            if recipe_name == "Select Recipe...":
                return None
            
            price_text = self.price_label.text().replace('₹', '').replace(',', '')
            price = float(price_text) if price_text else 0
            quantity = self.quantity_spin.value()
            subtotal_text = self.subtotal_label.text().replace('₹', '').replace(',', '')
            subtotal = float(subtotal_text) if subtotal_text else 0
            
            return {
                'recipe_name': recipe_name,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            }
        except Exception as e:
            logging.error(f"Error getting item data: {e}")
            return None

class AddOrderDialog(QDialog):
    """Dialog for adding new orders"""
    
    def __init__(self, recipes_data, parent=None):
        super().__init__(parent)
        self.recipes_data = recipes_data
        self.order_items = []
        
        self.setWindowTitle("Add New Order")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.add_order_item()  # Add first item by default
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header_label = QLabel("Create New Order")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Order details form
        self.create_order_details_form(layout)
        
        # Order items section
        self.create_order_items_section(layout)
        
        # Order summary
        self.create_order_summary(layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_order_details_form(self, parent_layout):
        """Create order details form"""
        details_group = QGroupBox("Order Details")
        details_layout = QFormLayout(details_group)
        
        # Order ID (auto-generated)
        self.order_id_edit = QLineEdit()
        self.order_id_edit.setText(self.generate_order_id())
        self.order_id_edit.setReadOnly(True)
        details_layout.addRow("Order ID:", self.order_id_edit)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        details_layout.addRow("Date:", self.date_edit)
        
        # Platform
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Swiggy", "Zomato", "Local", "Other"])
        self.platform_combo.setEditable(True)  # Allow custom platform entry
        details_layout.addRow("Platform:", self.platform_combo)
        
        # Customer (optional)
        self.customer_edit = QLineEdit()
        self.customer_edit.setPlaceholderText("Customer name (optional)")
        details_layout.addRow("Customer:", self.customer_edit)
        
        parent_layout.addWidget(details_group)
    
    def create_order_items_section(self, parent_layout):
        """Create order items section"""
        items_group = QGroupBox("Order Items")
        items_layout = QVBoxLayout(items_group)
        
        # Items header with add button
        items_header = QHBoxLayout()
        items_header.addWidget(QLabel("Items:"))
        items_header.addStretch()
        
        add_item_btn = QPushButton("+ Add Item")
        add_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_item_btn.clicked.connect(self.add_order_item)
        items_header.addWidget(add_item_btn)
        
        items_layout.addLayout(items_header)
        
        # Scrollable items area
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(8)
        
        items_layout.addWidget(self.items_widget)
        parent_layout.addWidget(items_group)
    
    def create_order_summary(self, parent_layout):
        """Create order summary section"""
        summary_group = QGroupBox("Order Summary")
        summary_layout = QFormLayout(summary_group)
        
        # Subtotal
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        summary_layout.addRow("Subtotal:", self.subtotal_label)
        
        # Discount
        self.discount_edit = QDoubleSpinBox()
        self.discount_edit.setRange(0, 9999)
        self.discount_edit.setDecimals(2)
        self.discount_edit.setSuffix(" ₹")
        self.discount_edit.valueChanged.connect(self.update_total)
        summary_layout.addRow("Discount:", self.discount_edit)
        
        # Total
        self.total_label = QLabel("₹0.00")
        self.total_label.setStyleSheet("font-weight: 700; font-size: 16px; color: #059669;")
        summary_layout.addRow("Total:", self.total_label)
        
        parent_layout.addWidget(summary_group)
    
    def add_order_item(self):
        """Add new order item"""
        item_widget = OrderItemWidget(self.recipes_data)
        item_widget.item_changed.connect(self.update_total)
        item_widget.remove_btn.clicked.connect(lambda: self.remove_order_item(item_widget))
        
        self.order_items.append(item_widget)
        self.items_layout.addWidget(item_widget)
        
        self.update_total()
    
    def remove_order_item(self, item_widget):
        """Remove order item"""
        if len(self.order_items) > 1:  # Keep at least one item
            self.order_items.remove(item_widget)
            item_widget.deleteLater()
            self.update_total()
    
    def update_total(self):
        """Update order total"""
        try:
            subtotal = 0
            
            for item_widget in self.order_items:
                item_data = item_widget.get_item_data()
                if item_data:
                    subtotal += item_data['subtotal']
            
            discount = self.discount_edit.value()
            total = subtotal - discount
            
            self.subtotal_label.setText(f"₹{subtotal:.2f}")
            self.total_label.setText(f"₹{total:.2f}")
            
        except Exception as e:
            logging.error(f"Error updating total: {e}")
    
    def generate_order_id(self):
        """Generate unique order ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
    
    def get_order_data(self):
        """Get complete order data"""
        try:
            # Get order items
            items = []
            for item_widget in self.order_items:
                item_data = item_widget.get_item_data()
                if item_data:
                    items.append(item_data)
            
            if not items:
                return None
            
            # Calculate totals
            subtotal = sum(item['subtotal'] for item in items)
            discount = self.discount_edit.value()
            total = subtotal - discount
            
            # Create order data
            order_data = {
                'order_id': self.order_id_edit.text(),
                'date': self.date_edit.date().toPython().strftime('%Y-%m-%d'),
                'platform': self.platform_combo.currentText(),
                'customer': self.customer_edit.text() or 'Walk-in Customer',
                'items': items,
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
                'status': 'Pending'
            }
            
            return order_data
            
        except Exception as e:
            logging.error(f"Error getting order data: {e}")
            return None

class OrderManagementWidget(QWidget):
    """Main order management widget"""
    
    # Signals
    order_added = Signal(dict)
    order_updated = Signal(dict)
    
    def __init__(self, data, pricing_data=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.pricing_data = pricing_data
        self.logger = logging.getLogger(__name__)
        
        # Initialize orders data
        if 'orders' not in self.data:
            self.data['orders'] = pd.DataFrame()
        
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with add order button
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Order Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        add_order_btn = QPushButton("+ New Order")
        add_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        add_order_btn.clicked.connect(self.add_new_order)
        header_layout.addWidget(add_order_btn)
        
        layout.addLayout(header_layout)
        
        # Orders table
        self.create_orders_table(layout)
    
    def create_orders_table(self, parent_layout):
        """Create orders table"""
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Date", "Order ID", "Platform", "Customer", "Items", 
            "Subtotal", "Discount", "Total"
        ])
        
        # Apply responsive table functionality
        try:
            from modules.responsive_table_utils import make_table_responsive
            
            column_priorities = {
                0: 2,   # Date - high priority
                1: 1,   # Order ID - highest priority
                2: 1,   # Platform - highest priority
                3: 3,   # Customer - medium priority
                4: 2,   # Items - high priority
                5: 4,   # Subtotal - low priority
                6: 4,   # Discount - low priority
                7: 2    # Total - high priority
            }
            
            column_config = {
                'priorities': column_priorities,
                'stretch_columns': [1, 2, 4, 7]  # Order ID, Platform, Items, Total
            }
            
            make_table_responsive(self.orders_table, column_config)
            
        except ImportError:
            # Fallback to standard table
            self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        parent_layout.addWidget(self.orders_table)
    
    def add_new_order(self):
        """Open dialog to add new order"""
        dialog = AddOrderDialog(self.pricing_data, self)
        
        if dialog.exec() == QDialog.Accepted:
            order_data = dialog.get_order_data()
            
            if order_data:
                self.save_order(order_data)
                self.load_orders()
                self.order_added.emit(order_data)
                
                QMessageBox.information(
                    self, "Success", 
                    f"Order {order_data['order_id']} created successfully!"
                )
    
    def save_order(self, order_data):
        """Save order to data"""
        try:
            # Convert items list to string for storage
            items_str = ", ".join([f"{item['recipe_name']} x{item['quantity']}" 
                                 for item in order_data['items']])
            
            # Create order record
            order_record = {
                'date': order_data['date'],
                'order_id': order_data['order_id'],
                'platform': order_data['platform'],
                'customer': order_data['customer'],
                'items': items_str,
                'subtotal': order_data['subtotal'],
                'discount': order_data['discount'],
                'total': order_data['total'],
                'status': order_data['status']
            }
            
            # Add to dataframe
            new_df = pd.DataFrame([order_record])
            self.data['orders'] = pd.concat([self.data['orders'], new_df], ignore_index=True)
            
            # Save to CSV
            import os
            os.makedirs('data', exist_ok=True)
            self.data['orders'].to_csv('data/orders.csv', index=False)
            
        except Exception as e:
            self.logger.error(f"Error saving order: {e}")
            raise
    
    def load_orders(self):
        """Load and display orders"""
        try:
            if self.data['orders'].empty:
                self.orders_table.setRowCount(0)
                return
            
            orders_df = self.data['orders']
            self.orders_table.setRowCount(len(orders_df))
            
            for row, (_, order) in enumerate(orders_df.iterrows()):
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.get('date', ''))))
                self.orders_table.setItem(row, 1, QTableWidgetItem(str(order.get('order_id', ''))))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(order.get('platform', ''))))
                self.orders_table.setItem(row, 3, QTableWidgetItem(str(order.get('customer', ''))))
                self.orders_table.setItem(row, 4, QTableWidgetItem(str(order.get('items', ''))))
                self.orders_table.setItem(row, 5, QTableWidgetItem(f"₹{order.get('subtotal', 0):.2f}"))
                self.orders_table.setItem(row, 6, QTableWidgetItem(f"₹{order.get('discount', 0):.2f}"))
                self.orders_table.setItem(row, 7, QTableWidgetItem(f"₹{order.get('total', 0):.2f}"))
                
        except Exception as e:
            self.logger.error(f"Error loading orders: {e}")

"""
Bulk Pricing Editor
Advanced multi-item pricing management with filters and batch operations
"""

import logging
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QGroupBox, QComboBox, QLineEdit, QHeaderView,
    QCheckBox, QSpinBox, QDoubleSpinBox, QProgressBar, QMessageBox,
    QSplitter, QTabWidget, QScrollArea, QGridLayout, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QObject
from PySide6.QtGui import QFont, QColor, QPalette


class PricingUpdateWorker(QObject):
    """Worker thread for bulk pricing updates"""
    
    progress_updated = Signal(int)
    item_updated = Signal(str, float)
    finished = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, items_to_update, update_type, value):
        super().__init__()
        self.items_to_update = items_to_update
        self.update_type = update_type
        self.value = value
    
    def run(self):
        """Run the bulk update process"""
        try:
            total_items = len(self.items_to_update)
            
            for i, (item_name, current_price) in enumerate(self.items_to_update):
                # Calculate new price based on update type
                if self.update_type == "percentage":
                    new_price = current_price * (1 + self.value / 100)
                elif self.update_type == "fixed_amount":
                    new_price = current_price + self.value
                elif self.update_type == "set_price":
                    new_price = self.value
                else:
                    new_price = current_price
                
                # Emit signals
                self.item_updated.emit(item_name, new_price)
                progress = int((i + 1) / total_items * 100)
                self.progress_updated.emit(progress)
                
                # Small delay to show progress
                QTimer.singleShot(10, lambda: None)
            
            self.finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class AdvancedFilterWidget(QFrame):
    """Advanced filtering widget for pricing items"""
    
    filter_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize filter UI"""
        layout = QGridLayout(self)
        layout.setSpacing(12)
        
        # Category filter
        layout.addWidget(QLabel("Category:"), 0, 0)
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Vegetables", "Fruits", "Grains", "Spices", "Dairy", "Meat", "Seafood"])
        self.category_filter.currentTextChanged.connect(self.filter_changed.emit)
        layout.addWidget(self.category_filter, 0, 1)
        
        # Price range filter
        layout.addWidget(QLabel("Price Range:"), 0, 2)
        price_layout = QHBoxLayout()
        
        self.min_price = QDoubleSpinBox()
        self.min_price.setRange(0, 10000)
        self.min_price.setPrefix("₹")
        self.min_price.valueChanged.connect(self.filter_changed.emit)
        price_layout.addWidget(self.min_price)
        
        price_layout.addWidget(QLabel("to"))
        
        self.max_price = QDoubleSpinBox()
        self.max_price.setRange(0, 10000)
        self.max_price.setValue(1000)
        self.max_price.setPrefix("₹")
        self.max_price.valueChanged.connect(self.filter_changed.emit)
        price_layout.addWidget(self.max_price)
        
        layout.addLayout(price_layout, 0, 3)
        
        # Source filter
        layout.addWidget(QLabel("Source:"), 1, 0)
        self.source_filter = QComboBox()
        self.source_filter.addItems(["All Sources", "Shopping List", "Inventory", "Smart Pricing", "Manual Entry"])
        self.source_filter.currentTextChanged.connect(self.filter_changed.emit)
        layout.addWidget(self.source_filter, 1, 1)
        
        # Search filter
        layout.addWidget(QLabel("Search:"), 1, 2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search ingredients...")
        self.search_input.textChanged.connect(self.filter_changed.emit)
        layout.addWidget(self.search_input, 1, 3)
        
        # Clear filters button
        clear_btn = QPushButton("🗑️ Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        layout.addWidget(clear_btn, 0, 4, 2, 1)
    
    def clear_filters(self):
        """Clear all filters"""
        self.category_filter.setCurrentIndex(0)
        self.source_filter.setCurrentIndex(0)
        self.min_price.setValue(0)
        self.max_price.setValue(1000)
        self.search_input.clear()
        self.filter_changed.emit()
    
    def get_filter_criteria(self):
        """Get current filter criteria"""
        return {
            'category': self.category_filter.currentText(),
            'source': self.source_filter.currentText(),
            'min_price': self.min_price.value(),
            'max_price': self.max_price.value(),
            'search': self.search_input.text().lower()
        }


class BulkEditDialog(QDialog):
    """Dialog for bulk editing operations"""
    
    def __init__(self, selected_items, parent=None):
        super().__init__(parent)
        self.selected_items = selected_items
        self.setWindowTitle("Bulk Edit Pricing")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(f"Editing {len(self.selected_items)} selected items")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Update type selection
        type_group = QGroupBox("Update Type")
        type_layout = QVBoxLayout(type_group)
        
        self.percentage_radio = QCheckBox("Percentage Change")
        self.percentage_radio.setChecked(True)
        type_layout.addWidget(self.percentage_radio)
        
        self.fixed_amount_radio = QCheckBox("Fixed Amount Change")
        type_layout.addWidget(self.fixed_amount_radio)
        
        self.set_price_radio = QCheckBox("Set Specific Price")
        type_layout.addWidget(self.set_price_radio)
        
        layout.addWidget(type_group)
        
        # Value input
        value_group = QGroupBox("Value")
        value_layout = QVBoxLayout(value_group)
        
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(-100, 1000)
        self.value_input.setValue(10)
        self.value_input.setSuffix("%")
        value_layout.addWidget(self.value_input)
        
        layout.addWidget(value_group)
        
        # Connect radio buttons
        self.percentage_radio.toggled.connect(self.on_type_changed)
        self.fixed_amount_radio.toggled.connect(self.on_type_changed)
        self.set_price_radio.toggled.connect(self.on_type_changed)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_type_changed(self):
        """Handle update type change"""
        if self.percentage_radio.isChecked():
            self.value_input.setSuffix("%")
            self.value_input.setRange(-100, 1000)
            self.value_input.setValue(10)
        elif self.fixed_amount_radio.isChecked():
            self.value_input.setSuffix(" ₹")
            self.value_input.setRange(-1000, 1000)
            self.value_input.setValue(5)
        elif self.set_price_radio.isChecked():
            self.value_input.setSuffix(" ₹")
            self.value_input.setRange(0, 10000)
            self.value_input.setValue(50)
    
    def get_update_info(self):
        """Get update information"""
        if self.percentage_radio.isChecked():
            return "percentage", self.value_input.value()
        elif self.fixed_amount_radio.isChecked():
            return "fixed_amount", self.value_input.value()
        elif self.set_price_radio.isChecked():
            return "set_price", self.value_input.value()
        return "percentage", 0


class BulkPricingEditor(QWidget):
    """Advanced bulk pricing editor with filters and batch operations"""
    
    pricing_updated = Signal(list)  # List of updated items
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)
        self.all_items = []
        self.filtered_items = []
        
        self.init_ui()
        self.load_pricing_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Filters
        self.filter_widget = AdvancedFilterWidget()
        self.filter_widget.filter_changed.connect(self.apply_filters)
        layout.addWidget(self.filter_widget)
        
        # Main content
        self.create_main_content(layout)
        
        # Bulk operations panel
        self.create_bulk_operations_panel(layout)
    
    def create_header(self, parent_layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🔧 Bulk Pricing Editor")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Stats labels
        self.total_items_label = QLabel("Total: 0 items")
        self.total_items_label.setStyleSheet("font-size: 14px; color: #64748b;")
        header_layout.addWidget(self.total_items_label)
        
        self.selected_items_label = QLabel("Selected: 0 items")
        self.selected_items_label.setStyleSheet("font-size: 14px; color: #3b82f6; font-weight: 500;")
        header_layout.addWidget(self.selected_items_label)
        
        parent_layout.addLayout(header_layout)
    
    def create_main_content(self, parent_layout):
        """Create main content area"""
        # Pricing table
        self.pricing_table = QTableWidget()
        self.pricing_table.setColumnCount(7)
        self.pricing_table.setHorizontalHeaderLabels([
            "Select", "Ingredient", "Current Price", "Category", "Source", 
            "Last Updated", "New Price"
        ])
        
        # Modern table styling
        self.pricing_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                selection-background-color: #fef2f2;
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
        header = self.pricing_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Select
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Ingredient
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Current Price
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Source
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Last Updated
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # New Price
        
        # Connect selection changes
        self.pricing_table.itemSelectionChanged.connect(self.update_selection_count)
        
        parent_layout.addWidget(self.pricing_table)
    
    def create_bulk_operations_panel(self, parent_layout):
        """Create bulk operations panel"""
        operations_frame = QFrame()
        operations_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        operations_layout = QHBoxLayout(operations_frame)
        
        # Select all/none buttons
        select_all_btn = QPushButton("✅ Select All")
        select_all_btn.clicked.connect(self.select_all_items)
        operations_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("❌ Select None")
        select_none_btn.clicked.connect(self.select_no_items)
        operations_layout.addWidget(select_none_btn)
        
        operations_layout.addStretch()
        
        # Bulk edit button
        bulk_edit_btn = QPushButton("🔧 Bulk Edit Selected")
        bulk_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        bulk_edit_btn.clicked.connect(self.bulk_edit_selected)
        operations_layout.addWidget(bulk_edit_btn)
        
        # Apply changes button
        apply_btn = QPushButton("💾 Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        apply_btn.clicked.connect(self.apply_changes)
        operations_layout.addWidget(apply_btn)
        
        parent_layout.addWidget(operations_frame)
    
    def load_pricing_data(self):
        """Load pricing data from various sources"""
        self.all_items = []
        
        # Load from shopping list
        if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
            for _, item in self.data['shopping_list'].iterrows():
                self.all_items.append({
                    'name': item.get('item_name', ''),
                    'current_price': item.get('estimated_cost', 0),
                    'category': item.get('category', 'Unknown'),
                    'source': 'Shopping List',
                    'last_updated': item.get('date_added', 'Unknown')
                })
        
        # Load from inventory
        if 'inventory' in self.data and not self.data['inventory'].empty:
            for _, item in self.data['inventory'].iterrows():
                self.all_items.append({
                    'name': item.get('item_name', ''),
                    'current_price': item.get('price_per_unit', 0),
                    'category': item.get('category', 'Unknown'),
                    'source': 'Inventory',
                    'last_updated': item.get('last_updated', 'Unknown')
                })
        
        self.filtered_items = self.all_items.copy()
        self.update_table()
        self.update_stats()
    
    def apply_filters(self):
        """Apply current filters to the data"""
        criteria = self.filter_widget.get_filter_criteria()
        
        self.filtered_items = []
        for item in self.all_items:
            # Category filter
            if criteria['category'] != "All Categories" and item['category'] != criteria['category']:
                continue
            
            # Source filter
            if criteria['source'] != "All Sources" and item['source'] != criteria['source']:
                continue
            
            # Price range filter
            if not (criteria['min_price'] <= item['current_price'] <= criteria['max_price']):
                continue
            
            # Search filter
            if criteria['search'] and criteria['search'] not in item['name'].lower():
                continue
            
            self.filtered_items.append(item)
        
        self.update_table()
        self.update_stats()
    
    def update_table(self):
        """Update the pricing table"""
        self.pricing_table.setRowCount(len(self.filtered_items))
        
        for row, item in enumerate(self.filtered_items):
            # Select checkbox
            checkbox = QCheckBox()
            self.pricing_table.setCellWidget(row, 0, checkbox)
            
            # Item data
            self.pricing_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.pricing_table.setItem(row, 2, QTableWidgetItem(f"₹{item['current_price']:.2f}"))
            self.pricing_table.setItem(row, 3, QTableWidgetItem(item['category']))
            self.pricing_table.setItem(row, 4, QTableWidgetItem(item['source']))
            self.pricing_table.setItem(row, 5, QTableWidgetItem(str(item['last_updated'])))
            
            # New price (editable)
            new_price_item = QTableWidgetItem(f"₹{item['current_price']:.2f}")
            new_price_item.setFlags(new_price_item.flags() | Qt.ItemIsEditable)
            self.pricing_table.setItem(row, 6, new_price_item)
    
    def update_stats(self):
        """Update statistics labels"""
        total_count = len(self.filtered_items)
        self.total_items_label.setText(f"Total: {total_count} items")
        
        selected_count = self.get_selected_count()
        self.selected_items_label.setText(f"Selected: {selected_count} items")
    
    def get_selected_count(self):
        """Get count of selected items"""
        count = 0
        for row in range(self.pricing_table.rowCount()):
            checkbox = self.pricing_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                count += 1
        return count
    
    def update_selection_count(self):
        """Update selection count when selection changes"""
        self.update_stats()
    
    def select_all_items(self):
        """Select all visible items"""
        for row in range(self.pricing_table.rowCount()):
            checkbox = self.pricing_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_stats()
    
    def select_no_items(self):
        """Deselect all items"""
        for row in range(self.pricing_table.rowCount()):
            checkbox = self.pricing_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_stats()
    
    def bulk_edit_selected(self):
        """Open bulk edit dialog for selected items"""
        selected_items = []
        for row in range(self.pricing_table.rowCount()):
            checkbox = self.pricing_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                item_name = self.pricing_table.item(row, 1).text()
                current_price = float(self.pricing_table.item(row, 2).text().replace('₹', ''))
                selected_items.append((item_name, current_price))
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select items to edit.")
            return
        
        dialog = BulkEditDialog(selected_items, self)
        if dialog.exec() == QDialog.Accepted:
            update_type, value = dialog.get_update_info()
            self.apply_bulk_update(selected_items, update_type, value)
    
    def apply_bulk_update(self, selected_items, update_type, value):
        """Apply bulk update to selected items"""
        for row in range(self.pricing_table.rowCount()):
            checkbox = self.pricing_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                current_price = float(self.pricing_table.item(row, 2).text().replace('₹', ''))
                
                # Calculate new price
                if update_type == "percentage":
                    new_price = current_price * (1 + value / 100)
                elif update_type == "fixed_amount":
                    new_price = current_price + value
                elif update_type == "set_price":
                    new_price = value
                else:
                    new_price = current_price
                
                # Update table
                new_price_item = QTableWidgetItem(f"₹{new_price:.2f}")
                new_price_item.setFlags(new_price_item.flags() | Qt.ItemIsEditable)
                self.pricing_table.setItem(row, 6, new_price_item)
    
    def apply_changes(self):
        """Apply all pricing changes"""
        updated_items = []
        
        for row in range(self.pricing_table.rowCount()):
            item_name = self.pricing_table.item(row, 1).text()
            current_price = float(self.pricing_table.item(row, 2).text().replace('₹', ''))
            new_price = float(self.pricing_table.item(row, 6).text().replace('₹', ''))
            
            if abs(new_price - current_price) > 0.01:  # Price changed
                updated_items.append({
                    'name': item_name,
                    'old_price': current_price,
                    'new_price': new_price
                })
        
        if updated_items:
            self.pricing_updated.emit(updated_items)
            QMessageBox.information(self, "Success", f"Updated pricing for {len(updated_items)} items.")
        else:
            QMessageBox.information(self, "No Changes", "No pricing changes detected.")

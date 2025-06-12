from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                             QMessageBox, QHeaderView, QSplitter, QCheckBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import os

class ShoppingWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.shopping_df = data['shopping_list'].copy()
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Shopping List")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
    
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for different shopping views
        self.current_list_tab = QWidget()
        self.add_item_tab = QWidget()
        self.shopping_history_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.current_list_tab, "Current Shopping List")
        self.tabs.addTab(self.add_item_tab, "Add Items")
        self.tabs.addTab(self.shopping_history_tab, "Shopping History")
        
        # Set up each tab
        self.setup_current_list_tab()
        self.setup_add_item_tab()
        self.setup_shopping_history_tab()
    
    def setup_current_list_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.current_list_tab)
        
        # Add subheader with bulk pricing button
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        header = QLabel("Current Shopping List")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Bulk pricing editor button - prominently placed
        bulk_pricing_btn = QPushButton("🔧 Bulk Pricing Editor")
        bulk_pricing_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        bulk_pricing_btn.clicked.connect(self.open_bulk_pricing_editor)
        header_layout.addWidget(bulk_pricing_btn)

        layout.addWidget(header_widget)
        
        # Filter section and bulk actions
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        # Status filter
        status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Purchased", "Cancelled"])
        self.status_combo.currentIndexChanged.connect(self.update_shopping_list)
        
        # Priority filter
        priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All", "High", "Medium", "Low"])
        self.priority_combo.currentIndexChanged.connect(self.update_shopping_list)
        
        # Search
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.update_shopping_list)
        
        # Add widgets to filter layout
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addWidget(priority_label)
        filter_layout.addWidget(self.priority_combo)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addStretch(1)

        # Bulk pricing editor button
        bulk_pricing_btn = QPushButton("🔧 Bulk Pricing Editor")
        bulk_pricing_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        bulk_pricing_btn.clicked.connect(self.open_bulk_pricing_editor)
        filter_layout.addWidget(bulk_pricing_btn)
        
        layout.addWidget(filter_widget)
        
        # Shopping list table
        self.shopping_table = QTableWidget()
        self.shopping_table.setColumnCount(8)
        self.shopping_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", "Priority", 
            "Est. Cost", "Store", "Status"
        ])
        self.shopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.shopping_table)
        
        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.mark_purchased_button = QPushButton("Mark as Purchased")
        self.mark_purchased_button.clicked.connect(self.mark_as_purchased)
        buttons_layout.addWidget(self.mark_purchased_button)

        self.mark_cancelled_button = QPushButton("Mark as Cancelled")
        self.mark_cancelled_button.clicked.connect(self.mark_as_cancelled)
        buttons_layout.addWidget(self.mark_cancelled_button)

        self.remove_button = QPushButton("Remove Item")
        self.remove_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(self.remove_button)

        # Add bulk pricing editor button here for better visibility
        bulk_pricing_btn2 = QPushButton("🔧 Bulk Pricing Editor")
        bulk_pricing_btn2.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        bulk_pricing_btn2.clicked.connect(self.open_bulk_pricing_editor)
        buttons_layout.addWidget(bulk_pricing_btn2)

        layout.addWidget(buttons_widget)
        
        # Summary section
        self.summary_widget = QWidget()
        self.summary_layout = QHBoxLayout(self.summary_widget)
        layout.addWidget(self.summary_widget)
        
        # Update the shopping list
        self.update_shopping_list()
    
    def update_shopping_list(self):
        # Apply filters
        filtered_df = self.shopping_df.copy()
        
        # Status filter
        status_filter = self.status_combo.currentText()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        # Priority filter
        priority_filter = self.priority_combo.currentText()
        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
        
        # Search filter
        search_text = self.search_input.text().lower()
        if search_text:
            filtered_df = filtered_df[
                filtered_df['item_name'].str.lower().str.contains(search_text) |
                filtered_df['category'].str.lower().str.contains(search_text) |
                filtered_df['store'].str.lower().str.contains(search_text)
            ]
        
        # Update table
        self.shopping_table.setRowCount(len(filtered_df))
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            self.shopping_table.setItem(i, 0, QTableWidgetItem(row['item_name']))
            self.shopping_table.setItem(i, 1, QTableWidgetItem(row['category']))
            self.shopping_table.setItem(i, 2, QTableWidgetItem(str(row['quantity'])))
            self.shopping_table.setItem(i, 3, QTableWidgetItem(row['unit']))
            self.shopping_table.setItem(i, 4, QTableWidgetItem(row['priority']))
            # Use current_price if available, otherwise last_price
            price = row.get('current_price', row.get('last_price', 0.0))
            self.shopping_table.setItem(i, 5, QTableWidgetItem(f"₹{price:.2f}"))
            self.shopping_table.setItem(i, 6, QTableWidgetItem(row['store']))
            self.shopping_table.setItem(i, 7, QTableWidgetItem(row['status']))
            
            # Color code based on priority
            color = QColor(255, 255, 255)  # Default white
            if row['priority'] == 'High':
                color = QColor(255, 200, 200)  # Light red
            elif row['priority'] == 'Medium':
                color = QColor(255, 255, 200)  # Light yellow
            
            # Apply color to row
            for j in range(self.shopping_table.columnCount()):
                self.shopping_table.item(i, j).setBackground(color)
        
        # Update summary
        self.update_summary(filtered_df)
    
    def update_summary(self, df):
        # Clear the summary layout
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Calculate summary metrics
        total_items = len(df)
        
        # Handle cost calculation using current_price or last_price
        if 'current_price' in df.columns:
            total_cost = df['current_price'].sum()
        elif 'last_price' in df.columns:
            total_cost = df['last_price'].sum()
        else:
            # If neither exists, try to calculate it from other columns
            if 'quantity' in df.columns and 'price_per_unit' in df.columns:
                total_cost = (df['quantity'] * df['price_per_unit']).sum()
            else:
                total_cost = 0.0
        
        # Handle missing 'status' column
        if 'status' in df.columns:
            pending_items = len(df[df['status'] == 'Pending'])
        else:
            pending_items = total_items  # Assume all items are pending if status column doesn't exist
        
        # Create summary widgets
        items_group = QGroupBox("Total Items")
        items_layout = QVBoxLayout(items_group)
        items_label = QLabel(f"{total_items}")
        items_label.setFont(QFont("Arial", 16, QFont.Bold))
        items_label.setAlignment(Qt.AlignCenter)
        items_layout.addWidget(items_label)
        self.summary_layout.addWidget(items_group)
        
        cost_group = QGroupBox("Estimated Cost")
        cost_layout = QVBoxLayout(cost_group)
        
        # Get currency symbol from settings, default to Indian Rupee (₹)
        currency_symbol = "₹"
        if 'settings' in self.data and 'currency' in self.data['settings']:
            currency_symbol = self.data['settings']['currency']
        
        cost_label = QLabel(f"{currency_symbol} {total_cost:.2f}")
        cost_label.setFont(QFont("Arial", 16, QFont.Bold))
        cost_label.setAlignment(Qt.AlignCenter)
        cost_layout.addWidget(cost_label)
        self.summary_layout.addWidget(cost_group)
        
        pending_group = QGroupBox("Pending Items")
        pending_layout = QVBoxLayout(pending_group)
        pending_label = QLabel(f"{pending_items}")
        pending_label.setFont(QFont("Arial", 16, QFont.Bold))
        pending_label.setAlignment(Qt.AlignCenter)
        pending_layout.addWidget(pending_label)
        self.summary_layout.addWidget(pending_group)
    
    def mark_as_purchased(self):
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an item to mark as purchased.")
            return
        
        # Get the selected row index
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()
        quantity = float(self.shopping_table.item(row, 2).text())
        unit = self.shopping_table.item(row, 3).text()
        
        # Update the status in the dataframe
        item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
        if len(item_index) > 0:
            self.shopping_df.loc[item_index, 'status'] = 'Purchased'
            self.data['shopping_list'] = self.shopping_df
            
            # Save to CSV
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)
            
            # Update inventory if the item exists there
            self.update_inventory_quantity(item_name, quantity, unit)
            
            # Update the table
            self.update_shopping_list()
            
            QMessageBox.information(self, "Success", f"{item_name} marked as purchased and inventory updated if applicable.")
    
    def mark_as_cancelled(self):
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an item to mark as cancelled.")
            return
        
        # Get the selected row index
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()
        
        # Update the status in the dataframe
        item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
        if len(item_index) > 0:
            self.shopping_df.loc[item_index, 'status'] = 'Cancelled'
            self.data['shopping_list'] = self.shopping_df
            
            # Save to CSV
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)
            
            # Update the table
            self.update_shopping_list()
            
            QMessageBox.information(self, "Success", f"{item_name} marked as cancelled.")
    
    def remove_item(self):
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove.")
            return
        
        # Get the selected row index
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Confirm Removal", 
            f"Are you sure you want to remove {item_name} from the shopping list?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove from the dataframe
            item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
            if len(item_index) > 0:
                self.shopping_df = self.shopping_df.drop(item_index)
                self.data['shopping_list'] = self.shopping_df
                
                # Save to CSV
                self.shopping_df.to_csv('data/shopping_list.csv', index=False)
                
                # Update the table
                self.update_shopping_list()
                
                QMessageBox.information(self, "Success", f"{item_name} removed from the shopping list.")
    
    def setup_add_item_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_item_tab)
        
        # Add subheader
        header = QLabel("Add Item to Shopping List")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Create form for adding new items
        form_group = QGroupBox("Item Details")
        form_layout = QFormLayout(form_group)
        
        # Item name from inventory items - dropdown only, no custom entries
        self.new_item_name = QComboBox()
        self.new_item_name.setEditable(False)  # Only allow selection from dropdown
        
        # Populate with items from inventory if available
        if 'items' in self.data and len(self.data['items']) > 0:
            items = sorted(self.data['items']['item_name'].unique())
            self.new_item_name.addItems(items)
        else:
            # Add placeholder if no items exist
            self.new_item_name.addItem("No items available - add items in Inventory first")
        form_layout.addRow("Item Name:", self.new_item_name)
        
        # Category - populate from inventory categories if available
        self.new_category = QComboBox()
        if 'categories' in self.data and len(self.data['categories']) > 0:
            categories = sorted(self.data['categories']['category_name'].unique())
            self.new_category.addItems(categories)
        else:
            # Default categories if no inventory categories exist
            self.new_category.addItems(["Produce", "Dairy", "Meat", "Bakery", "Pantry", "Frozen", "Cleaning", "Other"])
        form_layout.addRow("Category:", self.new_category)
        
        # Connect item selection to auto-fill category
        self.new_item_name.currentTextChanged.connect(self.auto_fill_item_details)
        
        # Quantity
        self.new_quantity = QDoubleSpinBox()
        self.new_quantity.setMinimum(0.1)
        self.new_quantity.setMaximum(1000)
        self.new_quantity.setValue(1)
        form_layout.addRow("Quantity:", self.new_quantity)
        
        # Unit - dropdown only, no custom entries
        self.new_unit = QComboBox()
        self.new_unit.addItems(["kg", "g", "L", "ml", "units", "pcs", "loaves", "cans", "bottles"])
        self.new_unit.setEditable(False)  # Only allow selection from dropdown
        form_layout.addRow("Unit:", self.new_unit)
        
        # Priority
        self.new_priority = QComboBox()
        self.new_priority.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priority:", self.new_priority)
        
        # Estimated cost
        self.new_cost = QDoubleSpinBox()
        # Get currency symbol from settings, default to Indian Rupee (₹)
        currency_symbol = "₹"
        if 'settings' in self.data and 'currency' in self.data['settings']:
            currency_symbol = self.data['settings']['currency']
        self.new_cost.setPrefix(currency_symbol)
        self.new_cost.setMinimum(0.01)
        self.new_cost.setMaximum(1000)
        self.new_cost.setValue(1.00)
        form_layout.addRow("Estimated Cost:", self.new_cost)
        
        # Store
        self.new_store = QComboBox()
        # Check if 'store' column exists in the shopping dataframe
        if 'store' in self.shopping_df.columns and len(self.shopping_df) > 0:
            stores = sorted(self.shopping_df['store'].unique())
            self.new_store.addItems(stores if len(stores) > 0 else ["Supermarket", "Bakery", "Butcher", "Farmer's Market"])
        else:
            # Default stores if no store column exists
            self.new_store.addItems(["Supermarket", "Bakery", "Butcher", "Farmer's Market"])
        self.new_store.setEditable(True)
        form_layout.addRow("Store:", self.new_store)

        # Notes
        self.new_notes = QLineEdit()
        form_layout.addRow("Notes:", self.new_notes)

        layout.addWidget(form_group)

        # Add button
        self.add_item_button = QPushButton("Add to Shopping List")
        self.add_item_button.clicked.connect(self.add_shopping_item)
        layout.addWidget(self.add_item_button)
        
        # Add stretch to push form to the top
        layout.addStretch(1)
    
    def add_shopping_item(self):
        # Get form values
        item_name = self.new_item_name.currentText()
        category = self.new_category.currentText()
        quantity = self.new_quantity.value()
        unit = self.new_unit.currentText()
        priority = self.new_priority.currentText()
        current_price = self.new_cost.value()
        store = self.new_store.currentText()
        notes = self.new_notes.text()

        # Validate input
        if not item_name:
            QMessageBox.warning(self, "Input Error", "Please enter an item name.")
            return
        
        # Check if this item exists in the master items list
        item_exists = False
        if 'items' in self.data and len(self.data['items']) > 0:
            item_exists = item_name in self.data['items']['item_name'].values
        
        # If item doesn't exist in master list, show error and prompt
        if not item_exists:
            response = QMessageBox.question(
                self, 
                "Item Not Found", 
                f"'{item_name}' is not in your items database. You must add it to your Items list first. Would you like to do that now?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                # Notify user to switch to inventory module and add item
                QMessageBox.information(
                    self,
                    "Add Item First",
                    "Please go to the Inventory module, select the Items tab, and add this item to your database first."
                )
            return

        # Generate new item ID
        new_item_id = self.shopping_df['item_id'].max() + 1 if len(self.shopping_df) > 0 else 1

        # Create new item record
        new_item = pd.DataFrame({
            'item_id': [new_item_id],
            'item_name': [item_name],
            'category': [category],
            'quantity': [quantity],
            'unit': [unit],
            'priority': [priority],
            'current_price': [current_price],
            'last_price': [current_price],
            'avg_price': [current_price],
            'location': [store],
            'notes': [notes],
            'status': ['Pending']
        })

        # Add to shopping dataframe
        self.shopping_df = pd.concat([self.shopping_df, new_item], ignore_index=True)
        self.data['shopping_list'] = self.shopping_df

        # Save to CSV
        self.shopping_df.to_csv('data/shopping_list.csv', index=False)

        # Show success message
        QMessageBox.information(self, "Success", f"{item_name} added to the shopping list!")

        # Clear form
        self.new_item_name.clear()
        self.new_quantity.setValue(1)
        self.new_cost.setValue(1.00)
        self.new_notes.clear()

        # Update shopping list
        self.update_shopping_list()

    def setup_shopping_history_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.shopping_history_tab)

        # Add subheader
        header = QLabel("Shopping History")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        # Filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        # Status filter for history
        status_label = QLabel("Status:")
        self.history_status_combo = QComboBox()
        self.history_status_combo.addItems(["All", "Purchased", "Cancelled"])
        self.history_status_combo.currentIndexChanged.connect(self.update_shopping_history)

        # Add widgets to filter layout
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.history_status_combo)
        filter_layout.addStretch(1)

        layout.addWidget(filter_widget)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", 
            "Est. Cost", "Store", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)

        # Update the history
        self.update_shopping_history()

    def update_shopping_history(self):
        """Update shopping history table"""
        try:
            # Filter for completed items (purchased or cancelled)
            if 'status' in self.shopping_df.columns:
                history_df = self.shopping_df[
                    self.shopping_df['status'].isin(['Purchased', 'Cancelled'])
                ].copy()
            else:
                history_df = pd.DataFrame()  # Empty if no status column

            # Apply status filter
            status_filter = self.history_status_combo.currentText()
            if status_filter != "All" and not history_df.empty:
                history_df = history_df[history_df['status'] == status_filter]

            # Update table
            self.history_table.setRowCount(len(history_df))
            for i, (_, row) in enumerate(history_df.iterrows()):
                self.history_table.setItem(i, 0, QTableWidgetItem(row['item_name']))
                self.history_table.setItem(i, 1, QTableWidgetItem(row['category']))
                self.history_table.setItem(i, 2, QTableWidgetItem(str(row['quantity'])))
                self.history_table.setItem(i, 3, QTableWidgetItem(row['unit']))
                # Use current_price if available, otherwise last_price
                price = row.get('current_price', row.get('last_price', 0.0))
                self.history_table.setItem(i, 4, QTableWidgetItem(f"₹{price:.2f}"))
                self.history_table.setItem(i, 5, QTableWidgetItem(row['store']))
                self.history_table.setItem(i, 6, QTableWidgetItem(row['status']))

        except Exception as e:
            print(f"Error updating shopping history: {e}")

    def auto_fill_item_details(self, item_name):
        """Auto-fill item details based on inventory data"""
        if not item_name or 'items' not in self.data or len(self.data['items']) == 0:
            return

        # Find the item in inventory
        item_df = self.data['items']
        matching_items = item_df[item_df['item_name'] == item_name]

        if len(matching_items) > 0:
            item = matching_items.iloc[0]

            # Set category if available
            if 'category' in item and item['category']:
                index = self.new_category.findText(item['category'])
                if index >= 0:
                    self.new_category.setCurrentIndex(index)

            # Set unit if available
            if 'unit' in item and item['unit']:
                index = self.new_unit.findText(item['unit'])
                if index >= 0:
                    self.new_unit.setCurrentIndex(index)
                else:
                    # Add the unit if it doesn't exist
                    self.new_unit.addItem(item['unit'])
                    self.new_unit.setCurrentText(item['unit'])

    def open_bulk_pricing_editor(self):
        """Open bulk pricing editor for shopping list items"""
        try:
            from modules.bulk_pricing_editor import BulkPricingEditor
            from PySide6.QtWidgets import QDialog, QVBoxLayout

            # Create bulk editor dialog
            bulk_editor = BulkPricingEditor(self.data, self)
            bulk_editor.pricing_updated.connect(self.on_bulk_pricing_updated)

            # Show as dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Bulk Pricing Editor - Shopping List")
            dialog.setModal(True)
            dialog.resize(1200, 800)

            layout = QVBoxLayout(dialog)
            layout.addWidget(bulk_editor)

            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.exec()

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error opening bulk pricing editor: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open bulk pricing editor: {str(e)}")

    def on_bulk_pricing_updated(self, updated_items):
        """Handle bulk pricing updates"""
        try:
            # Update shopping list with new pricing
            for item in updated_items:
                item_name = item['name']
                new_price = item['new_price']

                # Update in shopping dataframe
                mask = self.shopping_df['item_name'] == item_name
                if mask.any():
                    self.shopping_df.loc[mask, 'current_price'] = new_price
                    self.shopping_df.loc[mask, 'last_price'] = new_price

            # Update data and save
            self.data['shopping_list'] = self.shopping_df
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)

            # Refresh display
            self.update_shopping_list()

            QMessageBox.information(self, "Success", f"Updated pricing for {len(updated_items)} items in shopping list.")

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error handling bulk pricing updates: {e}")
            QMessageBox.warning(self, "Error", f"Failed to update pricing: {str(e)}")

    def update_inventory_quantity(self, item_name, quantity, unit):
        """Update inventory quantity when an item is purchased"""
        # Check if items dataframe exists in data
        if 'items' not in self.data or len(self.data['items']) == 0:
            return

        # Find the item in inventory
        items_df = self.data['items']
        matching_items = items_df[items_df['item_name'] == item_name]

        if len(matching_items) > 0:
            item_id = matching_items.iloc[0]['item_id']

            # Get the current quantity
            current_quantity = matching_items.iloc[0]['quantity'] if 'quantity' in matching_items.iloc[0] else 0
            item_unit = matching_items.iloc[0]['unit'] if 'unit' in matching_items.iloc[0] else unit

            # Convert units if necessary
            converted_quantity = quantity
            if unit != item_unit:
                # Basic unit conversion - this could be expanded for more sophisticated conversions
                if unit.lower() in ['kg'] and item_unit.lower() in ['grams', 'g']:
                    converted_quantity = quantity * 1000
                elif unit.lower() in ['grams', 'g'] and item_unit.lower() in ['kg']:
                    converted_quantity = quantity / 1000
                elif unit.lower() in ['l'] and item_unit.lower() in ['ml']:
                    converted_quantity = quantity * 1000
                elif unit.lower() in ['ml'] and item_unit.lower() in ['l']:
                    converted_quantity = quantity / 1000

            # Update the quantity
            new_quantity = current_quantity + converted_quantity
            self.data['items'].loc[self.data['items']['item_id'] == item_id, 'quantity'] = new_quantity

            # Save to CSV
            self.data['items'].to_csv('data/items.csv', index=False)

            # Log the update
            print(f"Updated inventory: {item_name} from {current_quantity} to {new_quantity} {item_unit}")

    def setup_add_item_form(self, layout):
        """Setup the form for adding new items"""
        # Create form group
        form_group = QGroupBox("Add New Item")
        form_layout = QVBoxLayout(form_group)

        # Add button
        self.add_item_button = QPushButton("Add to Shopping List")
        self.add_item_button.clicked.connect(self.add_shopping_item)
        form_layout.addWidget(self.add_item_button)

        layout.addWidget(form_group)
    
    def add_shopping_item(self):
        # Get form values
        item_name = self.new_item_name.currentText()
        category = self.new_category.currentText()
        quantity = self.new_quantity.value()
        unit = self.new_unit.currentText()
        priority = self.new_priority.currentText()
        current_price = self.new_cost.value()
        store = self.new_store.currentText()
        notes = self.new_notes.text()
        
        # Validate input
        if not item_name:
            QMessageBox.warning(self, "Input Error", "Please enter an item name.")
            return
        
        # Generate new item ID
        new_item_id = self.shopping_df['item_id'].max() + 1 if len(self.shopping_df) > 0 else 1
        
        # Create new item record
        new_item = pd.DataFrame({
            'item_id': [new_item_id],
            'item_name': [item_name],
            'category': [category],
            'quantity': [quantity],
            'unit': [unit],
            'priority': [priority],
            'current_price': [current_price],
            'last_price': [current_price],
            'avg_price': [current_price],
            'location': [store],
            'notes': [notes],
            'status': ['Pending']
        })
        
        # Add to shopping dataframe
        self.shopping_df = pd.concat([self.shopping_df, new_item], ignore_index=True)
        self.data['shopping_list'] = self.shopping_df
        
        # Save to CSV
        self.shopping_df.to_csv('data/shopping_list.csv', index=False)
        
        # Show success message
        QMessageBox.information(self, "Success", f"{item_name} added to the shopping list!")
        
        # Clear form
        self.new_item_name.clear()
        self.new_quantity.setValue(1)
        self.new_cost.setValue(1.00)
        self.new_notes.clear()
        
        # Update shopping list
        self.update_shopping_list()
    
    def setup_shopping_history_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.shopping_history_tab)
        
        # Add subheader
        header = QLabel("Shopping History")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        # Status filter for history
        status_label = QLabel("Status:")
        self.history_status_combo = QComboBox()
        self.history_status_combo.addItems(["All", "Purchased", "Cancelled"])
        self.history_status_combo.currentIndexChanged.connect(self.update_shopping_history)
        
        # Add widgets to filter layout
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.history_status_combo)
        filter_layout.addStretch(1)
        
        layout.addWidget(filter_widget)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", 
            "Est. Cost", "Store", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)
        
        # Update the history
        self.update_shopping_history()
    
    def auto_fill_item_details(self, item_name):
        """Auto-fill item details based on inventory data"""
        if not item_name or 'items' not in self.data or len(self.data['items']) == 0:
            return
            
        # Find the item in inventory
        item_df = self.data['items']
        matching_items = item_df[item_df['item_name'] == item_name]
        
        if len(matching_items) > 0:
            item = matching_items.iloc[0]
            
            # Set category if available
            if 'category' in item and item['category']:
                index = self.new_category.findText(item['category'])
                if index >= 0:
                    self.new_category.setCurrentIndex(index)
            
            # Set unit if available
            if 'unit' in item and item['unit']:
                index = self.new_unit.findText(item['unit'])
                if index >= 0:
                    self.new_unit.setCurrentIndex(index)
    
    def update_shopping_history(self):
        # Filter for completed or cancelled items
        history_df = self.shopping_df[self.shopping_df['status'] != 'Pending'].copy()
        
        # Apply status filter
        status_filter = self.history_status_combo.currentText()
        if status_filter != "All":
            history_df = history_df[history_df['status'] == status_filter]
        
        # Update table
        self.history_table.setRowCount(len(history_df))
        for i, (_, row) in enumerate(history_df.iterrows()):
            self.history_table.setItem(i, 0, QTableWidgetItem(row['item_name']))
            self.history_table.setItem(i, 1, QTableWidgetItem(row['category']))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(row['quantity'])))
            self.history_table.setItem(i, 3, QTableWidgetItem(row['unit']))
            
            # Get currency symbol from settings, default to Indian Rupee (₹)
            currency_symbol = "₹"
            if 'settings' in self.data and 'currency' in self.data['settings']:
                currency_symbol = self.data['settings']['currency']
                
            # Use current_price if available, otherwise last_price
            price = row.get('current_price', row.get('last_price', 0.0))
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{currency_symbol} {price:.2f}"))
            self.history_table.setItem(i, 5, QTableWidgetItem(row['store']))
            self.history_table.setItem(i, 6, QTableWidgetItem(row['status']))
            
            # Color code based on status
            color = QColor(255, 255, 255)  # Default white
            if row['status'] == 'Purchased':
                color = QColor(200, 255, 200)  # Light green
            elif row['status'] == 'Cancelled':
                color = QColor(255, 200, 200)  # Light red
            
            # Apply color to row
            for j in range(self.history_table.columnCount()):
                self.history_table.item(i, j).setBackground(color)

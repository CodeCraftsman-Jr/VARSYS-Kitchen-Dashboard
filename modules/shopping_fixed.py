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
        
        # Create title and refresh button layout
        title_layout = QHBoxLayout()

        title_label = QLabel("Shopping List")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Add refresh button
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        refresh_button.clicked.connect(self.refresh_data)
        title_layout.addWidget(refresh_button)

        self.layout.addLayout(title_layout)
    
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

        # Connect tab change event to refresh data
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        """Handle tab change events to refresh data"""
        try:
            tab_name = self.tabs.tabText(index)
            print(f"🔄 Shopping tab switched to: {tab_name}")

            # Force reload shopping data from CSV
            self.reload_shopping_data_from_file()

            if tab_name == "Current Shopping List":
                self.update_shopping_list()
            elif tab_name == "Shopping History":
                self.update_shopping_history()

        except Exception as e:
            print(f"Error in shopping tab change handler: {e}")

    def reload_shopping_data_from_file(self):
        """Force reload shopping data from CSV file"""
        try:
            import pandas as pd
            import os

            shopping_file = 'data/shopping_list.csv'
            if os.path.exists(shopping_file):
                self.data['shopping_list'] = pd.read_csv(shopping_file)
                self.shopping_df = self.data['shopping_list'].copy()
                print(f"🔄 Reloaded shopping data: {len(self.data['shopping_list'])} items")
            else:
                # Create empty shopping list with proper columns
                self.data['shopping_list'] = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'priority',
                    'last_price', 'location', 'notes', 'status', 'current_price', 'avg_price',
                    'date_added', 'date_purchased'
                ])
                self.shopping_df = self.data['shopping_list'].copy()
                print("🔄 Shopping file not found, created empty dataframe")

        except Exception as e:
            print(f"Error reloading shopping data from file: {e}")

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
        
        # Filter section
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
        
        layout.addWidget(filter_widget)
        
        # Shopping table
        self.shopping_table = QTableWidget()
        self.shopping_table.setColumnCount(12)
        self.shopping_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", "Priority",
            "Last Price", "Location", "Status", "Current Price",
            "Avg Price", "Date Added", "Date Purchased"
        ])
        # Apply responsive table functionality
        try:
            from modules.responsive_table_utils import make_table_responsive

            # Define column priorities for responsive behavior
            column_priorities = {
                0: 1,   # Item - highest priority (always show)
                1: 2,   # Category - high priority
                2: 2,   # Quantity - high priority
                3: 3,   # Unit - medium priority
                4: 3,   # Priority - medium priority
                5: 4,   # Last Price - low priority
                6: 3,   # Location - medium priority
                7: 2,   # Status - high priority
                8: 4,   # Current Price - low priority
                9: 5,   # Avg Price - lowest priority (hide on mobile)
                10: 5,  # Date Added - lowest priority (hide on mobile)
                11: 4   # Date Purchased - low priority
            }

            # Configure responsive table
            column_config = {
                'priorities': column_priorities,
                'stretch_columns': [0, 1, 7]  # Item, Category, Status
            }

            make_table_responsive(self.shopping_table, column_config)
            print("✅ Applied responsive table functionality to shopping table")

        except ImportError:
            print("⚠️ Responsive table utilities not available, using standard styling")
            self.shopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.shopping_table.setSelectionBehavior(QTableWidget.SelectRows)
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

        self.edit_item_button = QPushButton("Edit Item")
        self.edit_item_button.clicked.connect(self.edit_selected_item)
        buttons_layout.addWidget(self.edit_item_button)

        self.remove_button = QPushButton("Remove Item")
        self.remove_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(self.remove_button)
        
        layout.addWidget(buttons_widget)
        
        # Summary section
        self.summary_widget = QWidget()
        self.summary_layout = QHBoxLayout(self.summary_widget)
        layout.addWidget(self.summary_widget)
        
        # Update the shopping list
        self.update_shopping_list()
    
    def update_shopping_list(self):
        """Update shopping list with performance optimization"""
        try:
            # Get filter values
            status_filter = self.status_combo.currentText()
            priority_filter = self.priority_combo.currentText()
            search_text = self.search_input.text().lower()

            # Filter dataframe with error handling
            filtered_df = self.shopping_df.copy() if not self.shopping_df.empty else pd.DataFrame()

            # Apply status filter
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]

            # Apply priority filter
            if priority_filter != "All":
                filtered_df = filtered_df[filtered_df['priority'] == priority_filter]

            # Apply search filter
            if search_text:
                filtered_df = filtered_df[filtered_df['item_name'].str.lower().str.contains(search_text)]

            # Update table
            self.shopping_table.setRowCount(len(filtered_df))
            for i, (_, row) in enumerate(filtered_df.iterrows()):
                self.shopping_table.setItem(i, 0, QTableWidgetItem(str(row['item_name']) if pd.notna(row['item_name']) else ""))
                self.shopping_table.setItem(i, 1, QTableWidgetItem(str(row['category']) if pd.notna(row['category']) else ""))
                self.shopping_table.setItem(i, 2, QTableWidgetItem(str(row['quantity']) if pd.notna(row['quantity']) else "0"))
                self.shopping_table.setItem(i, 3, QTableWidgetItem(str(row['unit']) if pd.notna(row['unit']) else ""))
                self.shopping_table.setItem(i, 4, QTableWidgetItem(str(row['priority']) if pd.notna(row['priority']) else "Medium"))

                # Get currency symbol from settings, default to Indian Rupee (₹)
                currency_symbol = "₹"
                if 'settings' in self.data and 'currency' in self.data['settings']:
                    currency_symbol = self.data['settings']['currency']

                # Last Price - column 5
                if 'last_price' in row and pd.notna(row['last_price']):
                    self.shopping_table.setItem(i, 5, QTableWidgetItem(f"{currency_symbol} {float(row['last_price']):.2f}"))
                elif 'avg_price' in row and pd.notna(row['avg_price']):
                    # Fallback for avg_price
                    self.shopping_table.setItem(i, 5, QTableWidgetItem(f"{currency_symbol} {float(row['avg_price']):.2f}"))
                else:
                    self.shopping_table.setItem(i, 5, QTableWidgetItem("Soon"))

                # Location - column 6 (consolidated from store)
                try:
                    location_value = ""
                    if 'location' in row and pd.notna(row['location']) and str(row['location']).strip() != '':
                        location_value = str(row['location']).strip()
                    elif 'store' in row and pd.notna(row['store']) and str(row['store']).strip() != '':
                        # Fallback to store for data migration
                        location_value = str(row['store']).strip()

                    self.shopping_table.setItem(i, 6, QTableWidgetItem(location_value))
                except Exception as e:
                    print(f"Error setting location value: {str(e)}")
                    self.shopping_table.setItem(i, 6, QTableWidgetItem(""))

                # Status - column 7
                try:
                    if 'status' in row and pd.notna(row['status']) and str(row['status']).strip() != '':
                        status_value = str(row['status']).strip()
                        self.shopping_table.setItem(i, 7, QTableWidgetItem(status_value))
                    else:
                        self.shopping_table.setItem(i, 7, QTableWidgetItem("Pending"))
                except Exception as e:
                    print(f"Error setting status value: {str(e)}")
                    self.shopping_table.setItem(i, 7, QTableWidgetItem("Pending"))

                # Current Price - column 8
                try:
                    if 'current_price' in row and pd.notna(row['current_price']):
                        current_price = float(row['current_price'])
                        self.shopping_table.setItem(i, 8, QTableWidgetItem(f"{currency_symbol} {current_price:.2f}"))
                    else:
                        self.shopping_table.setItem(i, 8, QTableWidgetItem("Soon"))
                except Exception as e:
                    print(f"Error setting current_price value: {str(e)}")
                    self.shopping_table.setItem(i, 8, QTableWidgetItem("Soon"))

                # Avg Price - column 9
                try:
                    if 'avg_price' in row and pd.notna(row['avg_price']):
                        avg_price = float(row['avg_price'])
                        self.shopping_table.setItem(i, 9, QTableWidgetItem(f"{currency_symbol} {avg_price:.2f}"))
                    else:
                        self.shopping_table.setItem(i, 9, QTableWidgetItem("Soon"))
                except Exception as e:
                    print(f"Error setting avg_price value: {str(e)}")
                    self.shopping_table.setItem(i, 9, QTableWidgetItem("Soon"))

                # Date Added - column 10
                try:
                    if 'date_added' in row and pd.notna(row['date_added']):
                        date_added = str(row['date_added']).strip()
                        self.shopping_table.setItem(i, 10, QTableWidgetItem(date_added))
                    else:
                        self.shopping_table.setItem(i, 10, QTableWidgetItem(""))
                except Exception as e:
                    print(f"Error setting date_added value: {str(e)}")
                    self.shopping_table.setItem(i, 10, QTableWidgetItem(""))

                # Date Purchased - column 11
                try:
                    if 'date_purchased' in row and pd.notna(row['date_purchased']) and str(row['date_purchased']).strip() != '' and str(row['date_purchased']).strip().lower() != 'none':
                        date_purchased = str(row['date_purchased']).strip()
                        self.shopping_table.setItem(i, 11, QTableWidgetItem(date_purchased))
                    else:
                        self.shopping_table.setItem(i, 11, QTableWidgetItem(""))
                except Exception as e:
                    print(f"Error setting date_purchased value: {str(e)}")
                    self.shopping_table.setItem(i, 11, QTableWidgetItem(""))

            # Update summary
            self.update_summary(filtered_df)

        except Exception as e:
            print(f"Error updating shopping list: {e}")
            # Show error in table
            self.shopping_table.setRowCount(1)
            self.shopping_table.setItem(0, 0, QTableWidgetItem(f"Error loading data: {str(e)}"))
    
    def update_summary(self, df):
        # Clear existing summary
        for i in reversed(range(self.summary_layout.count())): 
            self.summary_layout.itemAt(i).widget().setParent(None)
        
        # Calculate summary metrics
        total_items = len(df)
        
        # Calculate total cost if the column exists
        total_cost = 0
        if 'current_price' in df.columns:
            total_cost = df['current_price'].sum()
        elif 'last_price' in df.columns:
            total_cost = df['last_price'].sum()
        elif 'avg_price' in df.columns:
            total_cost = df['avg_price'].sum()
        else:
            total_cost = 0
        
        # Items by priority
        high_priority = len(df[df['priority'] == 'High']) if 'priority' in df.columns else 0
        medium_priority = len(df[df['priority'] == 'Medium']) if 'priority' in df.columns else 0
        low_priority = len(df[df['priority'] == 'Low']) if 'priority' in df.columns else 0
        
        # Create summary cards
        items_group = QGroupBox("Total Items")
        items_layout = QVBoxLayout(items_group)
        items_label = QLabel(str(total_items))
        items_label.setFont(QFont("Arial", 16, QFont.Bold))
        items_label.setAlignment(Qt.AlignCenter)
        items_layout.addWidget(items_label)
        self.summary_layout.addWidget(items_group)
        
        priority_group = QGroupBox("By Priority")
        priority_layout = QVBoxLayout(priority_group)
        priority_label = QLabel(f"High: {high_priority}, Medium: {medium_priority}, Low: {low_priority}")
        priority_label.setAlignment(Qt.AlignCenter)
        priority_layout.addWidget(priority_label)
        self.summary_layout.addWidget(priority_group)
        
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
    
    def mark_as_purchased(self):
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an item to mark as purchased.")
            return

        # Get the selected row
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()

        # Ask for actual purchase price
        from PySide6.QtWidgets import QInputDialog

        # Get current price from table or use last_price as default
        current_price = 0.0
        try:
            current_price_text = self.shopping_table.item(row, 8).text()
            if current_price_text != "Soon":
                current_price = float(current_price_text.replace("₹", "").replace("$", "").strip())
        except:
            pass

        # If no current price, try to get last_price
        if current_price == 0.0:
            item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
            if len(item_index) > 0:
                item_data = self.shopping_df.loc[item_index[0]]
                if 'last_price' in item_data and pd.notna(item_data['last_price']):
                    current_price = float(item_data['last_price'])

        # Ask user for actual purchase price
        actual_price, ok = QInputDialog.getDouble(
            self,
            "Purchase Price",
            f"Enter actual purchase price for {item_name}:",
            current_price,
            0.01,
            10000.0,
            2
        )

        if not ok:
            return

        # Find the item in the dataframe
        item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
        if len(item_index) > 0:
            from datetime import datetime

            # Update status and purchase date
            self.shopping_df.loc[item_index, 'status'] = 'Purchased'
            self.shopping_df.loc[item_index, 'date_purchased'] = datetime.now().strftime('%Y-%m-%d')

            # Update current_price with actual purchase price
            self.shopping_df.loc[item_index, 'current_price'] = actual_price

            # Calculate and update avg_price
            avg_price = self.calculate_avg_price(item_name, actual_price)
            self.shopping_df.loc[item_index, 'avg_price'] = avg_price

            # Save to CSV
            self.data['shopping_list'] = self.shopping_df
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)

            # Update the inventory if the item exists there
            quantity = float(self.shopping_table.item(row, 2).text())
            unit = self.shopping_table.item(row, 3).text()
            print(f"DEBUG: Marking {item_name} as purchased, quantity={quantity}, unit={unit}, price={actual_price}")
            self.update_inventory_quantity(item_name, quantity, unit)

            # Refresh the list
            self.update_shopping_list()

            QMessageBox.information(self, "Success", f"{item_name} marked as purchased!\nPrice: ₹{actual_price:.2f}\nAvg Price: ₹{avg_price:.2f}")

    def calculate_avg_price(self, item_name, new_price):
        """Calculate average price for an item based on purchase history"""
        try:
            # Get all purchased instances of this item
            purchased_items = self.shopping_df[
                (self.shopping_df['item_name'] == item_name) &
                (self.shopping_df['status'] == 'Purchased') &
                (self.shopping_df['current_price'].notna())
            ]

            if len(purchased_items) == 0:
                # First purchase
                return new_price

            # Get all prices including the new one
            prices = purchased_items['current_price'].tolist()
            prices.append(new_price)

            # Calculate average
            avg_price = sum(prices) / len(prices)
            return round(avg_price, 2)

        except Exception as e:
            print(f"Error calculating avg price for {item_name}: {e}")
            return new_price
    
    def mark_as_cancelled(self):
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an item to mark as cancelled.")
            return
        
        # Get the selected row
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()
        
        # Find the item in the dataframe
        item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
        if len(item_index) > 0:
            # Update status
            self.shopping_df.loc[item_index, 'status'] = 'Cancelled'
            
            # Save to CSV
            self.data['shopping_list'] = self.shopping_df
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)
            
            # Refresh the list
            self.update_shopping_list()

    def edit_selected_item(self):
        """Edit the selected shopping list item"""
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an item to edit.")
            return

        # Get the selected row
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()

        # Find the item in the dataframe
        item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
        if len(item_index) > 0:
            item_data = self.shopping_df.loc[item_index[0]]
            self.show_edit_dialog(item_data, item_index[0])

    def show_edit_dialog(self, item_data, item_index):
        """Show edit dialog for shopping item"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Item: {item_data['item_name']}")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # Item name (read-only)
        item_name_label = QLabel(str(item_data['item_name']))
        form_layout.addRow("Item Name:", item_name_label)

        # Category
        category_combo = QComboBox()
        category_combo.setEditable(True)
        if 'categories' in self.data and len(self.data['categories']) > 0:
            categories = sorted(self.data['categories']['category_name'].unique())
            category_combo.addItems(categories)
        category_combo.setCurrentText(str(item_data['category']) if pd.notna(item_data['category']) else "")
        form_layout.addRow("Category:", category_combo)

        # Quantity
        quantity_spin = QDoubleSpinBox()
        quantity_spin.setMinimum(0.1)
        quantity_spin.setMaximum(1000)
        quantity_spin.setValue(float(item_data['quantity']) if pd.notna(item_data['quantity']) else 1.0)
        form_layout.addRow("Quantity:", quantity_spin)

        # Unit
        unit_combo = QComboBox()
        unit_combo.setEditable(True)
        unit_combo.addItems(["kg", "g", "L", "ml", "units", "pcs", "loaves", "cans", "bottles"])
        unit_combo.setCurrentText(str(item_data['unit']) if pd.notna(item_data['unit']) else "")
        form_layout.addRow("Unit:", unit_combo)

        # Priority
        priority_combo = QComboBox()
        priority_combo.addItems(["High", "Medium", "Low"])
        priority_combo.setCurrentText(str(item_data['priority']) if pd.notna(item_data['priority']) else "Medium")
        form_layout.addRow("Priority:", priority_combo)

        # Estimated cost
        cost_spin = QDoubleSpinBox()
        cost_spin.setMinimum(0.01)
        cost_spin.setMaximum(10000)
        cost_spin.setValue(float(item_data['estimated_cost']) if pd.notna(item_data['estimated_cost']) else 1.0)
        form_layout.addRow("Estimated Cost:", cost_spin)

        # Location
        location_combo = QComboBox()
        location_combo.setEditable(True)
        location_combo.addItems(["Supermarket", "Bakery", "Butcher", "Farmer's Market", "Pantry", "Refrigerator", "Freezer"])
        # Check both location and store for backward compatibility
        location_value = ""
        if 'location' in item_data and pd.notna(item_data['location']):
            location_value = str(item_data['location'])
        elif 'store' in item_data and pd.notna(item_data['store']):
            location_value = str(item_data['store'])
        location_combo.setCurrentText(location_value)
        form_layout.addRow("Location:", location_combo)

        # Notes
        notes_edit = QLineEdit()
        notes_edit.setText(str(item_data['notes']) if pd.notna(item_data['notes']) else "")
        form_layout.addRow("Notes:", notes_edit)

        layout.addLayout(form_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog and handle result
        if dialog.exec() == QDialog.Accepted:
            # Update the item in the dataframe
            self.shopping_df.loc[item_index, 'category'] = category_combo.currentText()
            self.shopping_df.loc[item_index, 'quantity'] = quantity_spin.value()
            self.shopping_df.loc[item_index, 'unit'] = unit_combo.currentText()
            self.shopping_df.loc[item_index, 'priority'] = priority_combo.currentText()
            self.shopping_df.loc[item_index, 'estimated_cost'] = cost_spin.value()
            self.shopping_df.loc[item_index, 'location'] = location_combo.currentText()
            self.shopping_df.loc[item_index, 'notes'] = notes_edit.text()

            # Save to CSV
            self.data['shopping_list'] = self.shopping_df
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)

            # Refresh the list
            self.update_shopping_list()

            QMessageBox.information(self, "Success", f"Item '{item_data['item_name']}' updated successfully!")

    def remove_item(self):
        selected_rows = self.shopping_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an item to remove.")
            return
        
        # Get the selected row
        row = selected_rows[0].row()
        item_name = self.shopping_table.item(row, 0).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Removal", 
            f"Are you sure you want to remove {item_name} from the shopping list?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Find the item in the dataframe
            item_index = self.shopping_df[self.shopping_df['item_name'] == item_name].index
            if len(item_index) > 0:
                # Remove the item
                self.shopping_df = self.shopping_df.drop(item_index)
                
                # Save to CSV
                self.data['shopping_list'] = self.shopping_df
                self.shopping_df.to_csv('data/shopping_list.csv', index=False)
                
                # Refresh the list
                self.update_shopping_list()
    
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
        self.new_item_name.setMinimumContentsLength(20)  # Make dropdown wider
        self.new_item_name.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        
        # Populate with items from inventory if available
        if 'items' in self.data and len(self.data['items']) > 0:
            # Sort items alphabetically for easier selection
            if 'item_name' in self.data['items'].columns:
                items = sorted(self.data['items']['item_name'].unique())
                self.new_item_name.addItems(items)
            # If no items found in the items dataframe, try inventory
            elif 'inventory' in self.data and 'item_name' in self.data['inventory'].columns:
                items = sorted(self.data['inventory']['item_name'].unique())
                self.new_item_name.addItems(items)
        # Add default items if no items exist
        if self.new_item_name.count() == 0:
            self.new_item_name.addItems(["Milk", "Eggs", "Bread", "Cheese", "Butter", "Rice", "Pasta"])
        form_layout.addRow("Item Name:", self.new_item_name)
        
        # Category - populate from inventory categories if available
        self.new_category = QComboBox()
        self.new_category.setEditable(False)  # Allow custom categories too
        self.new_category.setMinimumContentsLength(15)  # Make dropdown wider
        self.new_category.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        
        # Try to get categories from different sources
        categories_added = False
        if 'categories' in self.data and len(self.data['categories']) > 0:
            if 'category_name' in self.data['categories'].columns:
                categories = sorted(self.data['categories']['category_name'].unique())
                self.new_category.addItems(categories)
                categories_added = True
        
        # If categories not found in categories dataframe, try items dataframe
        if not categories_added and 'items' in self.data and len(self.data['items']) > 0:
            if 'category' in self.data['items'].columns:
                categories = sorted(self.data['items']['category'].unique())
                self.new_category.addItems(categories)
                categories_added = True
        
        # If still no categories, try inventory dataframe
        if not categories_added and 'inventory' in self.data and len(self.data['inventory']) > 0:
            if 'category' in self.data['inventory'].columns:
                categories = sorted(self.data['inventory']['category'].unique())
                self.new_category.addItems(categories)
                categories_added = True
        
        # Default categories if no inventory categories exist
        if not categories_added:
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
        self.new_unit.setEditable(False)  # Only allow selection from dropdown
        self.new_unit.setMinimumContentsLength(10)  # Make dropdown wider
        self.new_unit.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        
        # Try to get units from items dataframe
        units_added = False
        if 'items' in self.data and len(self.data['items']) > 0:
            if 'unit' in self.data['items'].columns:
                units = sorted(set(self.data['items']['unit'].dropna().unique()))
                if len(units) > 0:
                    self.new_unit.addItems(units)
                    units_added = True
        
        # If no units found in items, try inventory
        if not units_added and 'inventory' in self.data and len(self.data['inventory']) > 0:
            if 'unit' in self.data['inventory'].columns:
                units = sorted(set(self.data['inventory']['unit'].dropna().unique()))
                if len(units) > 0:
                    self.new_unit.addItems(units)
                    units_added = True
        
        # Add default units if none found
        if not units_added:
            self.new_unit.addItems(["kg", "g", "L", "ml", "units", "pcs", "loaves", "cans", "bottles"])
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
        self.new_cost.setPrefix(currency_symbol + " ")
        self.new_cost.setMinimum(0.01)
        self.new_cost.setMaximum(1000)
        self.new_cost.setValue(1.00)
        self.new_cost.setDecimals(2)
        form_layout.addRow("Estimated Cost:", self.new_cost)
        
        # Location
        self.new_location = QComboBox()
        # Check for existing location/store values for backward compatibility
        location_values = []
        try:
            if 'location' in self.shopping_df.columns and len(self.shopping_df) > 0:
                location_values.extend([str(s) for s in self.shopping_df['location'].unique() if pd.notna(s) and str(s).strip() != ''])
            if 'store' in self.shopping_df.columns and len(self.shopping_df) > 0:
                location_values.extend([str(s) for s in self.shopping_df['store'].unique() if pd.notna(s) and str(s).strip() != ''])

            # Remove duplicates and sort
            location_values = sorted(list(set(location_values))) if location_values else []

            if location_values:
                self.new_location.addItems(location_values)
            else:
                self.new_location.addItems(["Supermarket", "Bakery", "Butcher", "Farmer's Market", "Pantry", "Refrigerator", "Freezer"])
        except Exception as e:
            print(f"Error processing location values: {str(e)}")
            self.new_location.addItems(["Supermarket", "Bakery", "Butcher", "Farmer's Market", "Pantry", "Refrigerator", "Freezer"])

        self.new_location.setEditable(True)
        form_layout.addRow("Location:", self.new_location)
        
        # Notes
        self.new_notes = QLineEdit()
        form_layout.addRow("Notes:", self.new_notes)
        
        layout.addWidget(form_group)
        
        # Add buttons
        buttons_layout = QHBoxLayout()

        self.add_item_button = QPushButton("Add to Shopping List")
        self.add_item_button.clicked.connect(self.add_shopping_item)
        buttons_layout.addWidget(self.add_item_button)

        self.add_missing_button = QPushButton("Add Missing Ingredients")
        self.add_missing_button.clicked.connect(self.add_missing_ingredients)
        buttons_layout.addWidget(self.add_missing_button)

        layout.addLayout(buttons_layout)
    
    def add_shopping_item(self):
        """Add a new item to the shopping list"""
        # Get values from form
        item_name = self.new_item_name.currentText().strip()
        category = self.new_category.currentText().strip()
        quantity = self.new_quantity.value()
        unit = self.new_unit.currentText().strip()
        priority = self.new_priority.currentText().strip()
        estimated_cost = self.new_cost.value()
        location = self.new_location.currentText().strip()
        notes = self.new_notes.text().strip()
        
        # Validate
        if not item_name:
            QMessageBox.warning(self, "Warning", "Item name cannot be empty.")
            return
        
        # Only single item mode is supported now
        items_to_add = [item_name]
        
        # Process each item
        added_items = []
        for item in items_to_add:
            # Generate new item ID
            new_id = 1
            if len(self.shopping_df) > 0 and 'item_id' in self.shopping_df.columns:
                new_id = self.shopping_df['item_id'].max() + 1 if not self.shopping_df.empty else 1
            
            # Create new item record
            from datetime import datetime
            
            new_item = pd.DataFrame({
                'item_id': [new_id],
                'item_name': [item],
                'category': [category],
                'quantity': [quantity],
                'unit': [unit],
                'priority': [priority],
                'last_price': [estimated_cost],  # Use estimated_cost as last_price
                'location': [location],
                'notes': [notes],
                'status': ['Pending'],
                'current_price': [estimated_cost],  # Initialize with estimated cost
                'avg_price': [estimated_cost],  # Initialize with estimated cost
                'date_added': [datetime.now().strftime('%Y-%m-%d')],
                'date_purchased': [None]
            })
            
            # Add to dataframe
            self.shopping_df = pd.concat([self.shopping_df, new_item], ignore_index=True)
            
            # Synchronize with items database if needed
            self.sync_with_items_database(item, category, unit, estimated_cost)
            
            added_items.append(item)
        
        # Update data dictionary
        self.data['shopping_list'] = self.shopping_df
        
        # Save to CSV
        self.shopping_df.to_csv('data/shopping_list.csv', index=False)
        
        # Update table
        self.update_shopping_list()
        
        # Clear form
        self.new_item_name.setCurrentText("")
        self.new_quantity.setValue(1)
        self.new_cost.setValue(1.00)
        self.new_notes.clear()
        
        # Show success message
        if len(added_items) == 1:
            QMessageBox.information(self, "Success", f"Item '{added_items[0]}' added to shopping list.")
        else:
            QMessageBox.information(self, "Success", f"{len(added_items)} items added to shopping list: {', '.join(added_items[:5])}{' and more...' if len(added_items) > 5 else ''}")
    
    def sync_with_items_database(self, item_name, category, unit, cost):
        """Ensure item exists in the items database for future use"""
        # Check if the item already exists in the items database
        item_exists = False
        if 'items' in self.data and len(self.data['items']) > 0:
            if 'item_name' in self.data['items'].columns:
                item_exists = any(self.data['items']['item_name'] == item_name)
        
        # If item doesn't exist, add it to the items database
        if not item_exists:
            # Initialize items dataframe if it doesn't exist
            if 'items' not in self.data or len(self.data['items']) == 0:
                self.data['items'] = pd.DataFrame(columns=['item_id', 'item_name', 'category', 'description', 'unit', 'default_cost'])
            
            # Generate new item ID
            new_id = 1
            if len(self.data['items']) > 0 and 'item_id' in self.data['items'].columns:
                new_id = self.data['items']['item_id'].max() + 1 if not self.data['items'].empty else 1
            
            # Create new item record
            new_item = pd.DataFrame({
                'item_id': [new_id],
                'item_name': [item_name],
                'category': [category],
                'description': [""],  # Empty description by default
                'unit': [unit],
                'default_cost': [cost]
            })
            
            # Add to dataframe
            self.data['items'] = pd.concat([self.data['items'], new_item], ignore_index=True)
            
            # Save to CSV
            self.data['items'].to_csv('data/items.csv', index=False)
            
            print(f"Added new item '{item_name}' to items database")
        
        # Ensure category exists in categories database
        category_exists = False
        if 'categories' in self.data and len(self.data['categories']) > 0:
            if 'category_name' in self.data['categories'].columns:
                category_exists = any(self.data['categories']['category_name'] == category)
        
        # If category doesn't exist, add it to the categories database
        if not category_exists and category:
            # Initialize categories dataframe if it doesn't exist
            if 'categories' not in self.data or len(self.data['categories']) == 0:
                self.data['categories'] = pd.DataFrame(columns=['category_id', 'category_name', 'description'])
            
            # Generate new category ID
            new_id = 1
            if len(self.data['categories']) > 0 and 'category_id' in self.data['categories'].columns:
                new_id = self.data['categories']['category_id'].max() + 1 if not self.data['categories'].empty else 1
            
            # Create new category record
            new_category = pd.DataFrame({
                'category_id': [new_id],
                'category_name': [category],
                'description': [f"Auto-created when adding {item_name} to shopping list"]
            })
            
            # Add to dataframe
            self.data['categories'] = pd.concat([self.data['categories'], new_category], ignore_index=True)
            
            # Save to CSV
            self.data['categories'].to_csv('data/categories.csv', index=False)
            
            print(f"Added new category '{category}' to categories database")

    def add_missing_ingredients(self):
        """Find missing ingredients from recipes and add them to shopping list"""
        try:
            missing_items = []

            # Check if we have recipes data
            if 'recipes' not in self.data or len(self.data['recipes']) == 0:
                QMessageBox.information(self, "No Recipes", "No recipes found to check for missing ingredients.")
                return

            # Check if we have inventory data
            if 'inventory' not in self.data:
                self.data['inventory'] = pd.DataFrame()

            # Get current inventory items
            inventory_items = set()
            if len(self.data['inventory']) > 0 and 'item_name' in self.data['inventory'].columns:
                inventory_items = set(self.data['inventory']['item_name'].str.lower())

            # Get current shopping list items
            shopping_items = set()
            if len(self.shopping_df) > 0 and 'item_name' in self.shopping_df.columns:
                shopping_items = set(self.shopping_df['item_name'].str.lower())

            # Check each recipe for missing ingredients
            for _, recipe in self.data['recipes'].iterrows():
                if 'ingredients' in recipe and pd.notna(recipe['ingredients']):
                    ingredients_text = str(recipe['ingredients'])
                    # Split ingredients by common separators
                    ingredients = [ing.strip() for ing in ingredients_text.replace(',', '\n').replace(';', '\n').split('\n') if ing.strip()]

                    for ingredient in ingredients:
                        ingredient_lower = ingredient.lower()
                        # Check if ingredient is missing from both inventory and shopping list
                        if (ingredient_lower not in inventory_items and
                            ingredient_lower not in shopping_items and
                            len(ingredient.strip()) > 2):  # Avoid very short strings

                            # Check if we already identified this as missing
                            if ingredient not in [item['name'] for item in missing_items]:
                                missing_items.append({
                                    'name': ingredient,
                                    'recipe': recipe['recipe_name'] if 'recipe_name' in recipe else 'Unknown'
                                })

            if not missing_items:
                QMessageBox.information(self, "No Missing Items", "All recipe ingredients are available in inventory or already in shopping list.")
                return

            # Show dialog to select which items to add
            self.show_missing_ingredients_dialog(missing_items)

        except Exception as e:
            print(f"Error finding missing ingredients: {e}")
            QMessageBox.warning(self, "Error", f"Error finding missing ingredients: {str(e)}")

    def show_missing_ingredients_dialog(self, missing_items):
        """Show dialog to select missing ingredients to add"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QScrollArea

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Missing Ingredients")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        # Header
        header = QLabel(f"Found {len(missing_items)} missing ingredients. Select which ones to add:")
        layout.addWidget(header)

        # Scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        checkboxes = []
        for item in missing_items:
            checkbox = QCheckBox(f"{item['name']} (from {item['recipe']})")
            checkbox.setChecked(True)  # Default to checked
            checkbox.item_data = item
            checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Select/Deselect all buttons
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in checkboxes])
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in checkboxes])

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        layout.addLayout(button_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog and handle result
        if dialog.exec() == QDialog.Accepted:
            selected_items = [cb.item_data for cb in checkboxes if cb.isChecked()]
            if selected_items:
                self.add_selected_missing_items(selected_items)

    def add_selected_missing_items(self, selected_items):
        """Add selected missing items to shopping list"""
        try:
            from datetime import datetime
            added_count = 0

            for item in selected_items:
                # Generate new item ID
                new_id = 1
                if len(self.shopping_df) > 0 and 'item_id' in self.shopping_df.columns:
                    new_id = self.shopping_df['item_id'].max() + 1 if not self.shopping_df.empty else 1

                # Create new item record with default values
                new_item = pd.DataFrame({
                    'item_id': [new_id],
                    'item_name': [item['name']],
                    'category': ['Unknown'],  # Default category for missing items
                    'quantity': [1.0],  # Default quantity
                    'unit': ['units'],  # Default unit
                    'priority': ['Medium'],  # Default priority
                    'last_price': [0.0],  # Default cost
                    'location': [''],  # Empty location
                    'notes': [f"Missing ingredient from recipe: {item['recipe']}"],
                    'status': ['Pending'],
                    'current_price': [0.0],  # Initialize with 0
                    'avg_price': [0.0],  # Initialize with 0
                    'date_added': [datetime.now().strftime('%Y-%m-%d')],
                    'date_purchased': [None]
                })

                # Add to dataframe
                self.shopping_df = pd.concat([self.shopping_df, new_item], ignore_index=True)
                added_count += 1

            # Update data dictionary and save
            self.data['shopping_list'] = self.shopping_df
            self.shopping_df.to_csv('data/shopping_list.csv', index=False)

            # Refresh the list
            self.update_shopping_list()

            QMessageBox.information(self, "Success", f"Added {added_count} missing ingredients to shopping list!")

        except Exception as e:
            print(f"Error adding missing items: {e}")
            QMessageBox.warning(self, "Error", f"Error adding missing items: {str(e)}")

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
        self.history_table.setColumnCount(10)
        self.history_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit",
            "Last Price", "Current Price", "Avg Price", "Location", "Status", "Date Purchased"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)
        
        # Update the history
        self.update_shopping_history()
    
    def update_shopping_history(self):
        """Update the shopping history table with completed/cancelled items"""
        # Get filter value
        status_filter = self.history_status_combo.currentText()
        
        # Get completed/cancelled items
        history_df = self.shopping_df.copy()
        history_df = history_df[history_df['status'] != 'Pending'] if 'status' in history_df.columns else pd.DataFrame()
        
        # Apply status filter
        if status_filter != "All" and not history_df.empty:
            history_df = history_df[history_df['status'] == status_filter]
        
        # Get currency symbol from settings, default to Indian Rupee (₹)
        currency_symbol = "₹"
        if 'settings' in self.data and 'currency' in self.data['settings']:
            currency_symbol = self.data['settings']['currency']
        
        # Update table
        self.history_table.setRowCount(len(history_df))
        for i, (_, row) in enumerate(history_df.iterrows()):
            # Set item_name
            self.history_table.setItem(i, 0, QTableWidgetItem(row['item_name']))
            
            # Set category if it exists
            self.history_table.setItem(i, 1, QTableWidgetItem(row['category'] if 'category' in row else ""))
            
            # Set quantity
            self.history_table.setItem(i, 2, QTableWidgetItem(str(row['quantity']) if 'quantity' in row else ""))
            
            # Set unit if it exists
            self.history_table.setItem(i, 3, QTableWidgetItem(row['unit'] if 'unit' in row else ""))
            
            # Last Price - column 4
            if 'last_price' in row and pd.notna(row['last_price']):
                self.history_table.setItem(i, 4, QTableWidgetItem(f"{currency_symbol} {float(row['last_price']):.2f}"))
            elif 'estimated_cost' in row and pd.notna(row['estimated_cost']):
                self.history_table.setItem(i, 4, QTableWidgetItem(f"{currency_symbol} {float(row['estimated_cost']):.2f}"))
            else:
                self.history_table.setItem(i, 4, QTableWidgetItem("Soon"))

            # Current Price - column 5
            if 'current_price' in row and pd.notna(row['current_price']):
                self.history_table.setItem(i, 5, QTableWidgetItem(f"{currency_symbol} {float(row['current_price']):.2f}"))
            else:
                self.history_table.setItem(i, 5, QTableWidgetItem("Soon"))

            # Avg Price - column 6
            if 'avg_price' in row and pd.notna(row['avg_price']):
                self.history_table.setItem(i, 6, QTableWidgetItem(f"{currency_symbol} {float(row['avg_price']):.2f}"))
            else:
                self.history_table.setItem(i, 6, QTableWidgetItem("Soon"))

            # Location - column 7
            try:
                location_value = ""
                if 'location' in row and pd.notna(row['location']) and str(row['location']).strip() != '':
                    location_value = str(row['location']).strip()
                elif 'store' in row and pd.notna(row['store']) and str(row['store']).strip() != '':
                    location_value = str(row['store']).strip()
                self.history_table.setItem(i, 7, QTableWidgetItem(location_value))
            except Exception as e:
                print(f"Error setting location value in history: {str(e)}")
                self.history_table.setItem(i, 7, QTableWidgetItem(""))

            # Status - column 8
            try:
                if 'status' in row and pd.notna(row['status']) and row['status'] != '':
                    status_value = str(row['status'])
                    self.history_table.setItem(i, 8, QTableWidgetItem(status_value))
                else:
                    self.history_table.setItem(i, 8, QTableWidgetItem(""))
            except Exception as e:
                print(f"Error setting status value in history: {str(e)}")
                self.history_table.setItem(i, 8, QTableWidgetItem(""))

            # Date Purchased - column 9
            if 'date_purchased' in row and pd.notna(row['date_purchased']) and str(row['date_purchased']).strip() != '':
                self.history_table.setItem(i, 9, QTableWidgetItem(str(row['date_purchased'])))
            else:
                self.history_table.setItem(i, 9, QTableWidgetItem(""))
            
            # Add color coding based on status
            color = QColor(255, 255, 255)  # Default white
            if 'status' in row:
                if row['status'] == 'Purchased':
                    color = QColor(230, 255, 230)  # Light green
                elif row['status'] == 'Cancelled':
                    color = QColor(255, 230, 230)  # Light red
            
            # Apply color to row - check if item exists first
            for j in range(self.history_table.columnCount()):
                item = self.history_table.item(i, j)
                if item is not None:
                    item.setBackground(color)
    
    def auto_fill_item_details(self, item_name):
        """Auto-fill item details based on inventory data"""
        if not item_name:
            return
        
        # Try to find the item in different data sources
        item = None
        
        # First check items dataframe
        if 'items' in self.data and len(self.data['items']) > 0 and 'item_name' in self.data['items'].columns:
            matching_items = self.data['items'][self.data['items']['item_name'] == item_name]
            if len(matching_items) > 0:
                item = matching_items.iloc[0]
        
        # If not found in items, check inventory dataframe
        if item is None and 'inventory' in self.data and len(self.data['inventory']) > 0 and 'item_name' in self.data['inventory'].columns:
            matching_items = self.data['inventory'][self.data['inventory']['item_name'] == item_name]
            if len(matching_items) > 0:
                item = matching_items.iloc[0]
        
        if item is not None:
            # Set category if available
            if 'category' in item and item['category']:
                # First check if the category exists in the dropdown
                index = self.new_category.findText(item['category'])
                if index >= 0:
                    self.new_category.setCurrentIndex(index)
                else:
                    # If not found, add it to the dropdown
                    self.new_category.addItem(item['category'])
                    self.new_category.setCurrentText(item['category'])
            
            # Set unit if available
            if 'unit' in item and item['unit']:
                index = self.new_unit.findText(item['unit'])
                if index >= 0:
                    self.new_unit.setCurrentIndex(index)
                else:
                    # Add the unit if it doesn't exist
                    self.new_unit.addItem(item['unit'])
                    self.new_unit.setCurrentText(item['unit'])
            
            # Set default cost if available
            if 'default_cost' in item and item['default_cost']:
                try:
                    cost = float(item['default_cost'])
                    self.new_cost.setValue(cost)
                except (ValueError, TypeError):
                    # If conversion fails, don't change the cost
                    pass
            # If default_cost not available but price_per_unit is
            elif 'price_per_unit' in item and item['price_per_unit']:
                try:
                    cost = float(item['price_per_unit'])
                    self.new_cost.setValue(cost)
                except (ValueError, TypeError):
                    pass
    
    def update_inventory_quantity(self, item_name, quantity, unit):
        """Update inventory quantity and average price when an item is purchased"""
        from datetime import datetime

        # Get the current price from shopping list
        shopping_item = self.shopping_df[self.shopping_df['item_name'] == item_name]
        if len(shopping_item) == 0:
            print(f"ERROR: Could not find {item_name} in shopping list")
            return

        shopping_row = shopping_item.iloc[0]
        current_price = 0.0

        # Get actual purchase price
        if 'current_price' in shopping_row and pd.notna(shopping_row['current_price']):
            current_price = float(shopping_row['current_price'])
        elif 'last_price' in shopping_row and pd.notna(shopping_row['last_price']):
            current_price = float(shopping_row['last_price'])

        # Check if inventory dataframe exists, if not create it
        if 'inventory' not in self.data:
            self.data['inventory'] = pd.DataFrame(columns=[
                'item_id', 'item_name', 'category', 'quantity', 'unit', 'price_per_unit',
                'location', 'expiry_date', 'reorder_level', 'total_value', 'price',
                'qty_purchased', 'qty_used', 'avg_price', 'description', 'default_cost',
                'purchase_count', 'total_spent', 'last_purchase_date', 'last_purchase_price'
            ])

        # Find the item in inventory
        inventory_df = self.data['inventory']
        matching_inventory = inventory_df[inventory_df['item_name'] == item_name]

        if len(matching_inventory) > 0:
            # Item exists in inventory - update it
            item_id = matching_inventory.iloc[0]['item_id']

            # Get current quantities
            current_qty_purchased = matching_inventory.iloc[0].get('qty_purchased', 0) if pd.notna(matching_inventory.iloc[0].get('qty_purchased', 0)) else 0
            current_qty_used = matching_inventory.iloc[0].get('qty_used', 0) if pd.notna(matching_inventory.iloc[0].get('qty_used', 0)) else 0

            # Update quantities
            new_qty_purchased = float(current_qty_purchased) + quantity
            new_quantity = new_qty_purchased - float(current_qty_used)

            # Update inventory
            self.data['inventory'].loc[self.data['inventory']['item_id'] == item_id, 'qty_purchased'] = new_qty_purchased
            self.data['inventory'].loc[self.data['inventory']['item_id'] == item_id, 'quantity'] = new_quantity
            self.data['inventory'].loc[self.data['inventory']['item_id'] == item_id, 'price_per_unit'] = current_price
            self.data['inventory'].loc[self.data['inventory']['item_id'] == item_id, 'total_value'] = new_quantity * current_price
            self.data['inventory'].loc[self.data['inventory']['item_id'] == item_id, 'last_purchase_date'] = datetime.now().strftime('%Y-%m-%d')
            self.data['inventory'].loc[self.data['inventory']['item_id'] == item_id, 'last_purchase_price'] = current_price

            print(f"Updated inventory: {item_name} - New qty: {new_quantity}, Price: ₹{current_price}")
        else:
            # Item doesn't exist in inventory - create new entry
            # Get next item_id
            if len(inventory_df) > 0:
                next_id = inventory_df['item_id'].max() + 1
            else:
                next_id = 1

            # Get category from items table if available
            category = "Unknown"
            if 'items' in self.data and len(self.data['items']) > 0:
                items_match = self.data['items'][self.data['items']['item_name'] == item_name]
                if len(items_match) > 0:
                    category = items_match.iloc[0].get('category', 'Unknown')

            # Create new inventory entry
            new_inventory_item = {
                'item_id': next_id,
                'item_name': item_name,
                'category': category,
                'quantity': quantity,
                'unit': unit,
                'price_per_unit': current_price,
                'location': shopping_row.get('location', 'Local Market'),
                'expiry_date': '',
                'reorder_level': 10,
                'total_value': quantity * current_price,
                'price': current_price,
                'qty_purchased': quantity,
                'qty_used': 0,
                'avg_price': current_price,
                'description': f"Added from shopping list purchase",
                'default_cost': current_price,
                'purchase_count': 1,
                'total_spent': current_price * quantity,
                'last_purchase_date': datetime.now().strftime('%Y-%m-%d'),
                'last_purchase_price': current_price
            }

            # Add to inventory
            new_row = pd.DataFrame([new_inventory_item])
            self.data['inventory'] = pd.concat([self.data['inventory'], new_row], ignore_index=True)

            print(f"Added to inventory: {item_name} - Qty: {quantity}, Price: ₹{current_price}")

        # Save inventory to CSV
        self.data['inventory'].to_csv('data/inventory.csv', index=False)
        print(f"Inventory saved to CSV with {len(self.data['inventory'])} items")

        # Trigger refresh of all tabs to reflect the changes
        self.refresh_all_tabs_after_purchase()

    def update_purchase_tracking(self, inventory_id, current_price, item_name):
        """Update purchase tracking columns in inventory"""
        try:
            # Get current purchase tracking data
            current_count = self.data['inventory'].loc[self.data['inventory']['item_id'] == inventory_id, 'purchase_count'].values[0]
            current_total_spent = self.data['inventory'].loc[self.data['inventory']['item_id'] == inventory_id, 'total_spent'].values[0]

            # Handle NaN values
            if pd.isna(current_count):
                current_count = 0
            if pd.isna(current_total_spent):
                current_total_spent = 0

            # Update purchase tracking
            new_count = int(current_count) + 1
            new_total_spent = float(current_total_spent) + current_price
            today = datetime.now().strftime('%Y-%m-%d')

            # Update the columns
            self.data['inventory'].loc[self.data['inventory']['item_id'] == inventory_id, 'purchase_count'] = new_count
            self.data['inventory'].loc[self.data['inventory']['item_id'] == inventory_id, 'total_spent'] = new_total_spent
            self.data['inventory'].loc[self.data['inventory']['item_id'] == inventory_id, 'last_purchase_date'] = today
            self.data['inventory'].loc[self.data['inventory']['item_id'] == inventory_id, 'last_purchase_price'] = current_price

            print(f"DEBUG: Updated purchase tracking for {item_name} - Count: {new_count}, Total Spent: {new_total_spent}")

        except Exception as e:
            print(f"Error updating purchase tracking for {item_name}: {str(e)}")

    def refresh_all_tabs_after_purchase(self):
        """Refresh data after a purchase without changing the current tab"""
        try:
            # Reload data from CSV files to get the latest changes
            if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, 'load_data'):
                print("DEBUG: Reloading data after purchase...")
                self.main_app.data = self.main_app.load_data()

                # Update the local data reference
                self.data = self.main_app.data

                # Refresh the current shopping list display
                self.load_shopping_data()
                self.update_shopping_list()

                print("DEBUG: Data refreshed successfully without changing tabs")
            else:
                print("DEBUG: Main app reference not available for data refresh")
        except Exception as e:
            print(f"Error refreshing data after purchase: {e}")

    def load_shopping_data(self):
        """Reload shopping data from the main data source"""
        try:
            if 'shopping_list' in self.data:
                self.shopping_df = self.data['shopping_list'].copy()
                print("DEBUG: Shopping data reloaded successfully")
            else:
                print("DEBUG: No shopping_list found in data")
        except Exception as e:
            print(f"Error loading shopping data: {e}")

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

    def refresh_data(self):
        """Refresh shopping list data from CSV file"""
        try:
            # Reload shopping list from CSV
            shopping_file = 'data/shopping_list.csv'
            if os.path.exists(shopping_file):
                self.shopping_df = pd.read_csv(shopping_file)
                self.data['shopping_list'] = self.shopping_df

                # Refresh all displays
                self.update_shopping_list()
                self.update_charts()

                # Show success message
                QMessageBox.information(self, "Refresh Complete",
                    f"Shopping list data refreshed successfully!\n\nLoaded {len(self.shopping_df)} items from CSV file.")

                print(f"[SUCCESS] Shopping list refreshed: {len(self.shopping_df)} items loaded")

            else:
                QMessageBox.warning(self, "File Not Found",
                    f"Shopping list CSV file not found at: {shopping_file}")

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error refreshing shopping data: {e}")
            QMessageBox.critical(self, "Refresh Error",
                f"Failed to refresh shopping list data:\n{str(e)}")
            print(f"[ERROR] Error refreshing shopping data: {e}")

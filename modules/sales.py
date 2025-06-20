from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                               QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                               QMessageBox, QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import calendar
import os
from utils.table_styling import apply_universal_column_resizing


class SalesWidget(QWidget):
    # Signal to notify when a sale is deleted
    sale_deleted = Signal()
    # Signal to notify when a sale is added
    sale_added = Signal()

    def __init__(self, data, inventory_widget=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.sales_df = data['sales'].copy()
        self.inventory_widget = inventory_widget

        # Set up the main layout
        self.layout = QVBoxLayout(self)

        # Create title
        title_label = QLabel("Sales Tracking")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create tabs for different sales views
        self.sales_overview_tab = QWidget()
        self.add_sale_tab = QWidget()
        self.sales_analysis_tab = QWidget()
        self.customer_analysis_tab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.sales_overview_tab, "Sales Overview")
        self.tabs.addTab(self.add_sale_tab, "Add Sale")
        self.tabs.addTab(self.sales_analysis_tab, "Sales Analysis")
        self.tabs.addTab(self.customer_analysis_tab, "Customer Analysis")

        # Set up each tab
        self.setup_sales_overview_tab()
        self.setup_add_sale_tab()
        self.setup_sales_analysis_tab()
        self.setup_customer_analysis_tab()

    def setup_sales_overview_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.sales_overview_tab)

        # Add subheader
        header = QLabel("Sales Overview")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        # Date filter section
        date_filter_widget = QWidget()
        date_filter_layout = QHBoxLayout(date_filter_widget)

        # Period filter
        period_label = QLabel("Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(
            ["Today", "This Week", "This Month", "This Year", "All Time"])

        # Add widgets to date filter layout
        date_filter_layout.addWidget(period_label)
        date_filter_layout.addWidget(self.period_combo)
        date_filter_layout.addStretch(1)

        layout.addWidget(date_filter_widget)

        # Connect signals
        self.period_combo.currentIndexChanged.connect(
            self.update_sales_overview)

        # Sales summary section
        self.sales_summary_widget = QWidget()
        self.sales_summary_layout = QHBoxLayout(self.sales_summary_widget)
        layout.addWidget(self.sales_summary_widget)

        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)  # Added delete column
        self.sales_table.setHorizontalHeaderLabels(
            ["Sale ID", "Item", "Quantity", "Price/Unit", "Total", "Date", "Actions"])

        # Set minimum height for better visibility
        self.sales_table.setMinimumHeight(300)
        self.sales_table.setMaximumHeight(500)

        # Enable sorting functionality for sales table (history table - preserve all records)
        self.sales_table.setSortingEnabled(True)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Apply universal column resizing functionality
        sales_default_column_widths = {
            0: 80,   # Sale ID
            1: 200,  # Item
            2: 100,  # Quantity
            3: 120,  # Price/Unit
            4: 120,  # Total
            5: 120,  # Date
            6: 150   # Actions - increased width for delete button
        }

        # Apply column resizing with settings persistence
        self.sales_table_resizer = apply_universal_column_resizing(
            self.sales_table,
            'sales_column_settings.json',
            sales_default_column_widths
        )

        print("✅ Applied universal column resizing to sales table")
        layout.addWidget(self.sales_table)

        # Update the sales overview
        self.update_sales_overview()

    def update_sales_overview(self):
        # Clear the sales summary layout
        while self.sales_summary_layout.count():
            item = self.sales_summary_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Get selected period
        period = self.period_combo.currentText()

        # Filter data based on selected period
        today = datetime.now().date()
        filtered_sales = self.sales_df.copy()

        # Check if we have any data and if date column exists
        if len(filtered_sales) > 0 and 'date' in filtered_sales.columns:
            # Ensure date column is datetime type
            if filtered_sales['date'].dtype == 'object':
                try:
                    filtered_sales['date'] = pd.to_datetime(
                        filtered_sales['date'], errors='coerce')
                except Exception as e:
                    print(f"Error converting dates: {e}")

            # Only apply date filters if we have datetime data
            if pd.api.types.is_datetime64_any_dtype(filtered_sales['date']):
                if period == "Today":
                    filtered_sales = filtered_sales[filtered_sales['date'].dt.date == today]
                elif period == "This Week":
                    start_of_week = today - timedelta(days=today.weekday())
                    filtered_sales = filtered_sales[filtered_sales['date'].dt.date >= start_of_week]
                elif period == "This Month":
                    filtered_sales = filtered_sales[
                        (filtered_sales['date'].dt.month == today.month) &
                        (filtered_sales['date'].dt.year == today.year)
                    ]
                elif period == "This Year":
                    filtered_sales = filtered_sales[filtered_sales['date'].dt.year == today.year]

        # Calculate summary metrics
        total_sales = len(filtered_sales)

        # Check if total_amount column exists
        if 'total_amount' in filtered_sales.columns:
            total_revenue = filtered_sales['total_amount'].sum()
        elif 'price' in filtered_sales.columns and 'quantity' in filtered_sales.columns:
            # Calculate total_amount from price and quantity
            filtered_sales['total_amount'] = filtered_sales['price'] * \
                filtered_sales['quantity']
            total_revenue = filtered_sales['total_amount'].sum()
        else:
            # If no price or quantity columns, use a default value
            total_revenue = 0

        avg_sale_value = total_revenue / total_sales if total_sales > 0 else 0

        # Create summary widgets
        sales_count_group = QGroupBox("Total Sales")
        sales_count_layout = QVBoxLayout(sales_count_group)
        sales_count_label = QLabel(f"{total_sales}")
        sales_count_label.setFont(QFont("Arial", 16, QFont.Bold))
        sales_count_label.setAlignment(Qt.AlignCenter)
        sales_count_layout.addWidget(sales_count_label)
        self.sales_summary_layout.addWidget(sales_count_group)

        revenue_group = QGroupBox("Total Revenue")
        revenue_layout = QVBoxLayout(revenue_group)
        revenue_label = QLabel(f"₹{total_revenue:.2f}")
        revenue_label.setFont(QFont("Arial", 16, QFont.Bold))
        revenue_label.setAlignment(Qt.AlignCenter)
        revenue_layout.addWidget(revenue_label)
        self.sales_summary_layout.addWidget(revenue_group)

        avg_sale_group = QGroupBox("Average Sale Value")
        avg_sale_layout = QVBoxLayout(avg_sale_group)
        avg_sale_label = QLabel(f"₹{avg_sale_value:.2f}")
        avg_sale_label.setFont(QFont("Arial", 16, QFont.Bold))
        avg_sale_label.setAlignment(Qt.AlignCenter)
        avg_sale_layout.addWidget(avg_sale_label)
        self.sales_summary_layout.addWidget(avg_sale_group)

        # Update the sales table
        self.sales_table.setRowCount(len(filtered_sales))
        for i, (idx, row) in enumerate(filtered_sales.iterrows()):
            # Check if sale_id exists, if not use the index
            if 'sale_id' in row:
                sale_id = str(row['sale_id'])
            else:
                sale_id = str(idx + 1)
            self.sales_table.setItem(i, 0, QTableWidgetItem(sale_id))

            # Item name - check for both item_name and recipe_name
            if 'recipe_name' in row:
                self.sales_table.setItem(
                    i, 1, QTableWidgetItem(row['recipe_name']))
            elif 'item_name' in row:
                self.sales_table.setItem(
                    i, 1, QTableWidgetItem(row['item_name']))
            else:
                self.sales_table.setItem(
                    i, 1, QTableWidgetItem("Unknown Item"))

            # Quantity
            if 'quantity' in row:
                self.sales_table.setItem(
                    i, 2, QTableWidgetItem(str(row['quantity'])))
            else:
                self.sales_table.setItem(i, 2, QTableWidgetItem("1"))

            # Get currency symbol from settings, default to Indian Rupee (₹)
            currency_symbol = "₹"
            if 'settings' in self.data and 'currency' in self.data['settings']:
                currency_symbol = self.data['settings']['currency']

            # Price per unit
            if 'price' in row:
                price_text = f"{currency_symbol}{row['price']:.2f}"
            elif 'price_per_unit' in row:
                price_text = f"{currency_symbol}{row['price_per_unit']:.2f}"
            else:
                price_text = f"{currency_symbol}0.00"
            self.sales_table.setItem(i, 3, QTableWidgetItem(price_text))

            # Total amount
            if 'total_amount' in row:
                total_text = f"{currency_symbol}{row['total_amount']:.2f}"
            elif 'price' in row and 'quantity' in row:
                # Calculate total from price and quantity
                total = float(row['price']) * float(row['quantity'])
                total_text = f"{currency_symbol}{total:.2f}"
            else:
                total_text = f"{currency_symbol}0.00"
            self.sales_table.setItem(i, 4, QTableWidgetItem(total_text))

            # Date
            if 'date' in row and pd.notna(row['date']):
                if isinstance(row['date'], datetime):
                    date_text = str(row['date'].date())
                else:
                    date_text = str(row['date'])
            else:
                date_text = ""
            self.sales_table.setItem(i, 5, QTableWidgetItem(date_text))

            # Actions - Delete button
            delete_button = QPushButton("🗑️ Delete")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                }
                QPushButton:pressed {
                    background-color: #991b1b;
                }
            """)
            # Store the row index in the button for deletion
            delete_button.clicked.connect(lambda checked, row_idx=i: self.delete_sale(row_idx))
            self.sales_table.setCellWidget(i, 6, delete_button)

    def delete_sale(self, row_idx):
        """Delete a sale record"""
        try:
            # Get the sale ID from the table
            sale_id_item = self.sales_table.item(row_idx, 0)
            if sale_id_item is None:
                QMessageBox.warning(self, "Error", "Could not identify sale to delete.")
                return

            sale_id = sale_id_item.text()
            item_name_item = self.sales_table.item(row_idx, 1)
            item_name = item_name_item.text() if item_name_item else "Unknown Item"

            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete this sale?\n\n"
                f"Sale ID: {sale_id}\n"
                f"Item: {item_name}\n\n"
                f"✅ This will restore inventory quantities that were deducted during the sale.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Get the sale data before deletion for inventory restoration
                sale_to_delete = None
                if 'sale_id' in self.sales_df.columns:
                    sale_matches = self.sales_df[self.sales_df['sale_id'] == int(sale_id)]
                    if len(sale_matches) > 0:
                        sale_to_delete = sale_matches.iloc[0]
                else:
                    if row_idx < len(self.sales_df):
                        sale_to_delete = self.sales_df.iloc[row_idx]

                # Restore inventory if we have sale data
                inventory_restored = False
                if sale_to_delete is not None:
                    try:
                        recipe_name = sale_to_delete.get('recipe_name', item_name)
                        quantity_sold = sale_to_delete.get('quantity', 1)

                        # Restore inventory by adding back the quantities
                        inventory_restored = self.restore_inventory_for_deleted_sale(recipe_name, quantity_sold)

                        if inventory_restored:
                            print(f"✅ Inventory restored for deleted sale: {recipe_name} x{quantity_sold}")
                        else:
                            print(f"⚠️ Could not restore inventory for: {recipe_name}")

                    except Exception as e:
                        print(f"❌ Error restoring inventory: {e}")

                # Find and remove the sale from the dataframe
                if 'sale_id' in self.sales_df.columns:
                    # Remove by sale_id
                    self.sales_df = self.sales_df[self.sales_df['sale_id'] != int(sale_id)]
                else:
                    # Remove by index if no sale_id column
                    if row_idx < len(self.sales_df):
                        self.sales_df = self.sales_df.drop(self.sales_df.index[row_idx]).reset_index(drop=True)

                # Save the updated sales data
                self.sales_df.to_csv('data/sales.csv', index=False)

                # Update the data in the main application
                self.data['sales'] = self.sales_df

                # Also remove from sales_orders if it exists there
                try:
                    if 'sales_orders' in self.data and len(self.data['sales_orders']) > 0:
                        sales_orders_df = self.data['sales_orders']

                        # Try to find matching order by recipe name and remove it
                        # Since sales_orders might not have the same sale_id, we match by recipe name and date
                        orders_to_remove = sales_orders_df[
                            (sales_orders_df['recipe'] == item_name) |
                            (sales_orders_df['recipe'].str.contains(item_name, case=False, na=False))
                        ]

                        if len(orders_to_remove) > 0:
                            # Remove the first matching order (most recent logic)
                            order_index_to_remove = orders_to_remove.index[0]
                            self.data['sales_orders'] = sales_orders_df.drop(order_index_to_remove).reset_index(drop=True)

                            # Save updated sales_orders
                            self.data['sales_orders'].to_csv('data/sales_orders.csv', index=False)
                            print(f"✅ Also removed corresponding order from sales_orders for {item_name}")
                        else:
                            print(f"ℹ️ No matching order found in sales_orders for {item_name}")
                    else:
                        print("ℹ️ No sales_orders data to update")

                except Exception as e:
                    print(f"⚠️ Error updating sales_orders: {e}")

                # Refresh the sales overview
                self.update_sales_overview()

                # Show success message
                success_msg = f"Sale {sale_id} has been successfully deleted."
                if inventory_restored:
                    success_msg += "\n\n✅ Inventory quantities have been restored."
                else:
                    success_msg += "\n\n⚠️ Could not restore inventory quantities. Please check manually."

                QMessageBox.information(self, "Sale Deleted", success_msg)

                # Emit signal to notify other widgets that a sale was deleted
                self.sale_deleted.emit()

                print(f"✅ Sale {sale_id} deleted successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete sale: {str(e)}")
            print(f"❌ Error deleting sale: {e}")

    def restore_inventory_for_deleted_sale(self, recipe_name, quantity_sold):
        """Restore inventory quantities when a sale is deleted"""
        try:
            # Find the recipe
            recipe_row = self.data['recipes'][self.data['recipes']['recipe_name'] == recipe_name]
            if len(recipe_row) == 0:
                print(f"⚠️ Recipe '{recipe_name}' not found for inventory restoration")
                return False

            recipe = recipe_row.iloc[0]
            recipe_id = recipe['recipe_id']

            print(f"🔄 Restoring inventory for deleted sale: {quantity_sold} {recipe_name} (Recipe ID: {recipe_id})")

            # Check if we have the recipe_ingredients data structure (new format)
            if 'recipe_ingredients' in self.data:
                try:
                    # Get ingredients for this recipe from the recipe_ingredients dataframe
                    recipe_ingredients_df = self.data['recipe_ingredients']
                    recipe_ingredients = recipe_ingredients_df[recipe_ingredients_df['recipe_id'] == recipe_id]

                    if len(recipe_ingredients) > 0:
                        # Process each ingredient (new format)
                        for _, ingredient_row in recipe_ingredients.iterrows():
                            item_name = ingredient_row['item_name']
                            ingredient_qty_per_serving = ingredient_row['quantity']
                            ingredient_unit = ingredient_row['unit']
                            ingredient_qty_total = ingredient_qty_per_serving * quantity_sold

                            # Add back to inventory
                            self.add_to_inventory(item_name, ingredient_qty_total, ingredient_unit)
                            print(f"  ✅ Restored {ingredient_qty_total} {ingredient_unit} of {item_name}")

                        # Save inventory changes
                        inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                      'data', 'inventory.csv')
                        self.data['inventory'].to_csv(inventory_file, index=False)

                        print(f"✅ Inventory restoration completed for {recipe_name}")
                        return True

                except Exception as e:
                    print(f"❌ Error in new format inventory restoration: {e}")

            # Fallback to old format if new format fails
            if 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
                try:
                    import json
                    ingredients_list = json.loads(recipe['recipe_ingredients'])

                    # Process each ingredient (old format)
                    for ingredient_data in ingredients_list:
                        item_name = ingredient_data['item_name']
                        ingredient_qty_per_serving = ingredient_data['quantity']
                        ingredient_unit = ingredient_data['unit']
                        ingredient_qty_total = ingredient_qty_per_serving * quantity_sold

                        # Add back to inventory
                        self.add_to_inventory(item_name, ingredient_qty_total, ingredient_unit)
                        print(f"  ✅ Restored {ingredient_qty_total} {ingredient_unit} of {item_name}")

                    # Save inventory changes
                    inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                  'data', 'inventory.csv')
                    self.data['inventory'].to_csv(inventory_file, index=False)

                    print(f"✅ Inventory restoration completed for {recipe_name} (old format)")
                    return True

                except Exception as e:
                    print(f"❌ Error in old format inventory restoration: {e}")

            print(f"⚠️ No ingredient data found for recipe '{recipe_name}'")
            return False

        except Exception as e:
            print(f"❌ Error restoring inventory for deleted sale: {e}")
            return False

    def add_to_inventory(self, item_name, quantity, unit):
        """Add quantity back to inventory (opposite of deduct_from_inventory)"""
        try:
            inventory_df = self.data['inventory']

            # Find the item in inventory
            item_mask = inventory_df['item_name'] == item_name

            if item_mask.any():
                # Item exists, add to current quantity
                current_qty = float(inventory_df.loc[item_mask, 'quantity'].iloc[0]) if pd.notna(inventory_df.loc[item_mask, 'quantity'].iloc[0]) else 0
                new_qty = current_qty + float(quantity)

                # Update quantity
                inventory_df.loc[item_mask, 'quantity'] = new_qty

                # Update qty_used (subtract the restored amount)
                current_used = float(inventory_df.loc[item_mask, 'qty_used'].iloc[0]) if pd.notna(inventory_df.loc[item_mask, 'qty_used'].iloc[0]) else 0
                new_used = max(0, current_used - float(quantity))  # Don't go below 0
                inventory_df.loc[item_mask, 'qty_used'] = new_used

                print(f"  📈 {item_name}: {current_qty} + {quantity} = {new_qty} {unit}")
                print(f"  📉 {item_name} used: {current_used} - {quantity} = {new_used} {unit}")

            else:
                print(f"  ⚠️ Item '{item_name}' not found in inventory - cannot restore")

        except Exception as e:
            print(f"❌ Error adding to inventory: {e}")

    def setup_add_sale_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.add_sale_tab)

        # Add subheader
        header = QLabel("Record New Sale")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        # Create form for recording sales
        form_group = QGroupBox("Sale Details")
        form_layout = QFormLayout(form_group)

        # Date selection
        self.sale_date = QDateEdit()
        self.sale_date.setDate(QDate.currentDate())
        self.sale_date.setCalendarPopup(True)
        form_layout.addRow("Date:", self.sale_date)

        # Customer name (optional)
        self.customer_name = QLineEdit()
        form_layout.addRow("Customer (optional):", self.customer_name)

        # Recipe selection
        self.recipe_combo = QComboBox()
        self.recipe_combo.addItem("Select Recipe...")

        # Populate with recipes from recipe database
        if 'recipes' in self.data and len(self.data['recipes']) > 0:
            if 'recipe_name' in self.data['recipes'].columns:
                recipes = sorted(self.data['recipes']['recipe_name'].tolist())
                self.recipe_combo.addItems(recipes)

        self.recipe_combo.currentIndexChanged.connect(self.update_recipe_price)
        form_layout.addRow("Recipe:", self.recipe_combo)

        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        self.quantity_spin.setValue(1)
        self.quantity_spin.valueChanged.connect(self.update_total_amount)
        form_layout.addRow("Quantity:", self.quantity_spin)

        # Price per unit
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0.0)
        self.price_spin.setMaximum(10000.0)
        self.price_spin.setValue(100.0)  # Default price
        self.price_spin.setPrefix("₹")  # Default to Indian Rupee
        self.price_spin.valueChanged.connect(self.update_total_amount)
        form_layout.addRow("Price per Unit:", self.price_spin)

        # Total amount
        self.total_amount_label = QLabel("₹100.00")
        self.total_amount_label.setFont(QFont("Arial", 12, QFont.Bold))
        form_layout.addRow("Total Amount:", self.total_amount_label)

        # Payment method
        self.payment_method = QComboBox()
        self.payment_method.addItems(
            ["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer"])
        form_layout.addRow("Payment Method:", self.payment_method)

        # Notes
        self.sale_notes = QLineEdit()
        form_layout.addRow("Notes:", self.sale_notes)

        layout.addWidget(form_group)

        # Add sale button
        self.add_sale_button = QPushButton("Record Sale")
        self.add_sale_button.clicked.connect(self.add_sale)
        layout.addWidget(self.add_sale_button)

        # Recipe ingredients preview
        ingredients_group = QGroupBox(
            "Recipe Ingredients (will be deducted from inventory)")
        ingredients_layout = QVBoxLayout(ingredients_group)

        # Ingredients table
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(
            ["Ingredient", "Quantity", "Unit", "In Stock"])

        # Set minimum height for better visibility
        self.ingredients_table.setMinimumHeight(200)
        self.ingredients_table.setMaximumHeight(300)

        # Apply universal column resizing functionality
        ingredients_default_column_widths = {
            0: 250,  # Ingredient - increased width
            1: 120,  # Quantity - increased width
            2: 100,  # Unit - increased width
            3: 120   # In Stock - increased width
        }

        # Apply column resizing with settings persistence
        self.ingredients_table_resizer = apply_universal_column_resizing(
            self.ingredients_table,
            'sales_ingredients_column_settings.json',
            ingredients_default_column_widths
        )

        print("✅ Applied universal column resizing to sales ingredients table")
        ingredients_layout.addWidget(self.ingredients_table)

        layout.addWidget(ingredients_group)

        # Initialize the total amount
        self.update_total_amount()

        # Add stretch to push form to the top
        layout.addStretch(1)

    def update_recipe_price(self):
        """Update the price based on the selected recipe"""
        recipe_name = self.recipe_combo.currentText()

        # Only proceed if a valid recipe is selected
        if recipe_name == "Select Recipe...":
            # Clear the ingredients table
            self.ingredients_table.setRowCount(0)
            # Reset to default price
            self.price_spin.setValue(100.0)
            return

        # Find the recipe price from pricing data
        price = self.get_recipe_price(recipe_name)

        # Set the price in the spin box
        self.price_spin.setValue(price)

        # Show ingredients in the table
        self.display_recipe_ingredients(recipe_name)

        # Update the total amount
        self.update_total_amount()

    def get_recipe_price(self, recipe_name):
        """Get the price for a recipe from the pricing data"""
        try:
            # Check if pricing data is available
            if 'pricing' in self.data and len(self.data['pricing']) > 0:
                pricing_df = self.data['pricing']

                # Look for exact match first
                price_row = pricing_df[pricing_df['recipe_name'] == recipe_name]

                if len(price_row) > 0:
                    # Get the 'our_pricing' value
                    if 'our_pricing' in price_row.columns:
                        price = float(price_row.iloc[0]['our_pricing'])
                        print(f"✅ Found price for '{recipe_name}': ₹{price}")
                        return price
                    elif 'price' in price_row.columns:
                        price = float(price_row.iloc[0]['price'])
                        print(f"✅ Found price for '{recipe_name}': ₹{price}")
                        return price

                # If no exact match, try case-insensitive search
                price_row = pricing_df[pricing_df['recipe_name'].str.lower() == recipe_name.lower()]
                if len(price_row) > 0:
                    if 'our_pricing' in price_row.columns:
                        price = float(price_row.iloc[0]['our_pricing'])
                        print(f"✅ Found price for '{recipe_name}' (case-insensitive): ₹{price}")
                        return price

                print(f"⚠️  No price found for '{recipe_name}', using default price")
            else:
                print("⚠️  No pricing data available, using default price")

        except Exception as e:
            print(f"❌ Error getting recipe price: {e}")

        # Return default price if not found
        return 100.0

    def display_recipe_ingredients(self, recipe_name):
        """Display the ingredients for the selected recipe"""
        # Find the recipe in the dataframe
        recipe_row = self.data['recipes'][self.data['recipes']
                                          ['recipe_name'] == recipe_name]
        if len(recipe_row) == 0:
            return

        recipe = recipe_row.iloc[0]

        # Clear the table
        self.ingredients_table.setRowCount(0)

        # Check if we have structured ingredients data
        if 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
            try:
                import json
                ingredients_list = json.loads(recipe['recipe_ingredients'])

                # Set table rows
                self.ingredients_table.setRowCount(len(ingredients_list))

                # Populate table
                for i, ingredient in enumerate(ingredients_list):
                    # Item name
                    self.ingredients_table.setItem(
                        i, 0, QTableWidgetItem(ingredient['item_name']))

                    # Quantity (adjusted for number of servings being sold)
                    qty = ingredient['quantity'] * self.quantity_spin.value()
                    self.ingredients_table.setItem(
                        i, 1, QTableWidgetItem(str(qty)))

                    # Unit
                    self.ingredients_table.setItem(
                        i, 2, QTableWidgetItem(ingredient['unit']))

                    # Check if in stock (now returns tuple)
                    allow_sale, stock_info = self.check_ingredient_stock(
                        ingredient['item_name'], qty, ingredient['unit'])
                    in_stock = stock_info['sufficient']
                    in_stock_item = QTableWidgetItem(
                        "Yes" if in_stock else "No")
                    in_stock_item.setBackground(
                        QColor(200, 255, 200) if in_stock else QColor(255, 200, 200))
                    self.ingredients_table.setItem(i, 3, in_stock_item)
            except Exception as e:
                print(f"Error displaying recipe ingredients: {e}")
        elif 'ingredients' in recipe and pd.notna(recipe['ingredients']):
            # Use simple text ingredients as fallback
            ingredients = recipe['ingredients'].split(',')

            # Set table rows
            self.ingredients_table.setRowCount(len(ingredients))

            # Populate table with basic info
            for i, ingredient_text in enumerate(ingredients):
                ingredient_name = ingredient_text.strip()
                self.ingredients_table.setItem(
                    i, 0, QTableWidgetItem(ingredient_name))
                self.ingredients_table.setItem(
                    i, 1, QTableWidgetItem("1"))  # Default quantity
                self.ingredients_table.setItem(
                    i, 2, QTableWidgetItem("unit"))  # Default unit

                # Check stock status for simple ingredients too
                try:
                    allow_sale, stock_info = self.check_ingredient_stock(ingredient_name, 1, "unit")
                    in_stock = stock_info['sufficient']
                    stock_text = "Yes" if in_stock else "No"
                    in_stock_item = QTableWidgetItem(stock_text)
                    in_stock_item.setBackground(
                        QColor(200, 255, 200) if in_stock else QColor(255, 200, 200))
                    self.ingredients_table.setItem(i, 3, in_stock_item)
                except Exception as e:
                    print(f"Error checking stock for {ingredient_name}: {e}")
                    self.ingredients_table.setItem(i, 3, QTableWidgetItem("Unknown"))

    def check_ingredient_stock(self, item_name, quantity, unit):
        """Check if the ingredient is in stock in sufficient quantity

        This method now allows sales to proceed regardless of stock levels,
        but provides detailed information about stock status for logging purposes.
        Returns a tuple: (allow_sale, stock_info)
        """
        # Get inventory dataframe
        inventory_df = self.data['inventory']

        # Check if item exists
        if 'item_name' not in inventory_df.columns:
            stock_info = {
                'item_name': item_name,
                'requested_qty': float(quantity),
                'requested_unit': unit,
                'current_qty': 0,
                'current_unit': 'unknown',
                'sufficient': False,
                'shortage': float(quantity),
                'status': 'item_not_found',
                'message': f"Item {item_name} not found in inventory - will be created with negative quantity"
            }
            return True, stock_info

        inventory_item = inventory_df[inventory_df['item_name'] == item_name]
        if len(inventory_item) == 0:
            stock_info = {
                'item_name': item_name,
                'requested_qty': float(quantity),
                'requested_unit': unit,
                'current_qty': 0,
                'current_unit': 'unknown',
                'sufficient': False,
                'shortage': float(quantity),
                'status': 'item_not_found',
                'message': f"Item {item_name} not found in inventory - will be created with negative quantity"
            }
            return True, stock_info

        # Check quantity
        item = inventory_item.iloc[0]
        if 'quantity' not in item or pd.isna(item['quantity']):
            stock_info = {
                'item_name': item_name,
                'requested_qty': float(quantity),
                'requested_unit': unit,
                'current_qty': 0,
                'current_unit': item.get('unit', 'unknown'),
                'sufficient': False,
                'shortage': float(quantity),
                'status': 'no_quantity_data',
                'message': f"Item {item_name} has no quantity specified - will be set to negative quantity"
            }
            return True, stock_info

        inv_qty = float(item['quantity'])
        inv_unit = item['unit'] if 'unit' in item and pd.notna(item['unit']) else 'unit'

        # Normalize units to lowercase and strip spaces for better comparison
        inv_unit_lower = inv_unit.lower().strip()
        unit_lower = unit.lower().strip() if isinstance(unit, str) else 'unit'

        # Convert quantities to a common unit for comparison
        qty_needed = float(quantity)  # Ensure quantity is a float
        original_qty_needed = qty_needed

        # Check units match and convert if necessary
        conversion_applied = False
        if inv_unit_lower != unit_lower:
            # Convert to inventory unit
            if (inv_unit_lower in ['kg', 'kilogram', 'kilograms'] and unit_lower in ['grams', 'g', 'gram']):
                # Convert recipe grams to inventory kg
                qty_needed = qty_needed / 1000
                conversion_applied = True
            elif (inv_unit_lower in ['grams', 'g', 'gram'] and unit_lower in ['kg', 'kilogram', 'kilograms']):
                # Convert recipe kg to inventory grams
                qty_needed = qty_needed * 1000
                conversion_applied = True
            elif (inv_unit_lower in ['l', 'liter', 'liters', 'litre', 'litres'] and unit_lower in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres']):
                # Convert recipe ml to inventory L
                qty_needed = qty_needed / 1000
                conversion_applied = True
            elif (inv_unit_lower in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres'] and unit_lower in ['l', 'liter', 'liters', 'litre', 'litres']):
                # Convert recipe L to inventory ml
                qty_needed = qty_needed * 1000
                conversion_applied = True

        # Check if enough quantity is available
        has_enough = inv_qty >= qty_needed
        shortage = max(0, qty_needed - inv_qty) if not has_enough else 0

        # Create detailed stock information
        stock_info = {
            'item_name': item_name,
            'requested_qty': original_qty_needed,
            'requested_unit': unit,
            'current_qty': inv_qty,
            'current_unit': inv_unit,
            'converted_qty': qty_needed if conversion_applied else original_qty_needed,
            'sufficient': has_enough,
            'shortage': shortage,
            'status': 'sufficient' if has_enough else 'insufficient',
            'conversion_applied': conversion_applied,
            'message': f"Need {qty_needed} {inv_unit_lower}, have {inv_qty} {inv_unit_lower}" +
                      (f" - Shortage: {shortage} {inv_unit_lower}" if not has_enough else " - Sufficient")
        }

        # Always allow the sale to proceed
        return True, stock_info

    def log_stock_check_results(self, recipe_name, quantity_sold, stock_check_results):
        """Log comprehensive stock check results for tracking and reconciliation"""
        import logging

        # Get the logger instance
        logger = logging.getLogger(__name__)

        # Create detailed log entry
        log_entry = f"\n{'='*80}\n"
        log_entry += f"SALES TRANSACTION - INVENTORY IMPACT ANALYSIS\n"
        log_entry += f"{'='*80}\n"
        log_entry += f"Recipe: {recipe_name}\n"
        log_entry += f"Quantity Sold: {quantity_sold}\n"
        log_entry += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_entry += f"Total Ingredients Processed: {len(stock_check_results)}\n"
        log_entry += f"{'-'*80}\n"

        sufficient_count = 0
        insufficient_count = 0

        for stock_info in stock_check_results:
            status_icon = "✅" if stock_info['sufficient'] else "⚠️"
            log_entry += f"{status_icon} {stock_info['item_name']}:\n"
            log_entry += f"   Requested: {stock_info['requested_qty']} {stock_info['requested_unit']}\n"
            log_entry += f"   Available: {stock_info['current_qty']} {stock_info['current_unit']}\n"

            if stock_info['conversion_applied']:
                log_entry += f"   Converted: {stock_info['converted_qty']} {stock_info['current_unit']}\n"

            if stock_info['sufficient']:
                sufficient_count += 1
                log_entry += f"   Status: SUFFICIENT STOCK\n"
                log_entry += f"   After Sale: {stock_info['current_qty'] - stock_info.get('converted_qty', stock_info['requested_qty']):.2f} {stock_info['current_unit']}\n"
            else:
                insufficient_count += 1
                log_entry += f"   Status: INSUFFICIENT STOCK\n"
                log_entry += f"   Shortage: {stock_info['shortage']:.2f} {stock_info['current_unit']}\n"
                log_entry += f"   After Sale: -{stock_info['shortage']:.2f} {stock_info['current_unit']} (NEGATIVE INVENTORY)\n"
                log_entry += f"   ⚠️  PURCHASE RECONCILIATION NEEDED\n"

            log_entry += f"   Message: {stock_info['message']}\n"
            log_entry += f"{'-'*40}\n"

        log_entry += f"\nSUMMARY:\n"
        log_entry += f"✅ Sufficient Stock: {sufficient_count} items\n"
        log_entry += f"⚠️  Insufficient Stock: {insufficient_count} items\n"

        if insufficient_count > 0:
            log_entry += f"\n🔍 RECONCILIATION REQUIRED:\n"
            log_entry += f"   - {insufficient_count} items will show negative inventory\n"
            log_entry += f"   - Review purchase records for these items\n"
            log_entry += f"   - Update inventory with missing purchase entries\n"

        log_entry += f"\n{'='*80}\n"

        # Log to application logger
        logger.info(log_entry)

        # Also print to console for immediate visibility
        print(log_entry)

    def log_inventory_changes(self, sale_id, recipe_name, quantity_sold, inventory_changes, packing_changes=None):
        """Log detailed inventory and packing material changes"""
        import logging

        logger = logging.getLogger(__name__)

        log_entry = f"\n{'='*80}\n"
        log_entry += f"INVENTORY UPDATE COMPLETED - SALE ID: {sale_id}\n"
        log_entry += f"{'='*80}\n"
        log_entry += f"Recipe: {recipe_name}\n"
        log_entry += f"Quantity Sold: {quantity_sold}\n"
        log_entry += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_entry += f"{'-'*80}\n"

        log_entry += f"INGREDIENT INVENTORY CHANGES:\n"
        for change in inventory_changes:
            status_icon = "[OK]" if change['final_qty'] >= 0 else "[WARN]"
            log_entry += f"{status_icon} {change['item_name']}:\n"
            log_entry += f"   Before: {change['before_qty']:.2f} {change['unit']}\n"
            log_entry += f"   Deducted: {change['deducted_qty']:.2f} {change['unit']}\n"
            log_entry += f"   After: {change['final_qty']:.2f} {change['unit']}\n"

            if change['final_qty'] < 0:
                log_entry += f"   [WARN] NEGATIVE INVENTORY: {abs(change['final_qty']):.2f} {change['unit']} shortage\n"

            log_entry += f"{'-'*40}\n"

        if packing_changes:
            log_entry += f"\nPACKING MATERIALS CHANGES:\n"
            for change in packing_changes:
                status_icon = "[OK]" if change['final_qty'] >= 0 else "[WARN]"
                log_entry += f"{status_icon} {change['material_name']}:\n"
                log_entry += f"   Before: {change['before_qty']:.2f} {change['unit']}\n"
                log_entry += f"   Used: {change['used_qty']:.2f} {change['unit']}\n"
                log_entry += f"   After: {change['final_qty']:.2f} {change['unit']}\n"
                log_entry += f"{'-'*40}\n"

        log_entry += f"\n{'='*80}\n"

        logger.info(log_entry)
        print(log_entry)

    def update_total_amount(self):
        """Update the total amount label based on price and quantity"""
        price = self.price_spin.value()
        quantity = self.quantity_spin.value()
        total = price * quantity

        # Update the label with the current currency symbol
        currency_symbol = "₹"  # Default to Indian Rupee
        if 'settings' in self.data and 'currency' in self.data['settings']:
            currency_symbol = self.data['settings']['currency']

        self.total_amount_label.setText(f"{currency_symbol}{total:.2f}")

        # If a recipe is selected, update the ingredients table to reflect the new quantity
        recipe_name = self.recipe_combo.currentText()
        if recipe_name != "Select Recipe...":
            self.display_recipe_ingredients(recipe_name)

    def add_sale(self):
        """Record a new sale and update inventory"""
        # Get form values
        date = self.sale_date.date().toString("yyyy-MM-dd")
        customer = self.customer_name.text().strip()
        recipe_name = self.recipe_combo.currentText()
        quantity = self.quantity_spin.value()
        price = self.price_spin.value()
        total_amount = price * quantity
        payment_method = self.payment_method.currentText()
        notes = self.sale_notes.text().strip()

        # Validate inputs
        if recipe_name == "Select Recipe...":
            QMessageBox.warning(self, "Input Error", "Please select a recipe.")
            return

        # Generate new sale ID
        sale_id = 1
        if len(self.sales_df) > 0 and 'sale_id' in self.sales_df.columns:
            sale_id = self.sales_df['sale_id'].max(
            ) + 1 if not self.sales_df.empty else 1

        # Create new sale record
        new_sale = pd.DataFrame({
            'sale_id': [sale_id],
            'date': [date],
            'customer': [customer],
            'recipe_name': [recipe_name],
            'quantity': [quantity],
            'price': [price],
            'total_amount': [total_amount],
            'payment_method': [payment_method],
            'notes': [notes]
        })

        # Add to sales dataframe
        self.sales_df = pd.concat([self.sales_df, new_sale], ignore_index=True)

        # Update data dictionary
        self.data['sales'] = self.sales_df

        # Save to CSV
        self.sales_df.to_csv('data/sales.csv', index=False)

        # Update the main data structure
        self.data['sales'] = self.sales_df

        # Update inventory based on recipe ingredients using new integration system
        self.update_inventory_for_sale(recipe_name, quantity)

        # Create corresponding order entry for order management
        self.create_order_from_sale(sale_id, date, recipe_name, quantity, price, total_amount)

        # Use new inventory integration system for comprehensive updates
        try:
            from modules.inventory_integration import InventoryIntegration

            integration = InventoryIntegration(self.data)
            sale_data = {
                'recipe_name': recipe_name,
                'quantity': quantity,
                'total_amount': total_amount,
                'date': date
            }

            integration_result = integration.process_sale_completion(sale_data)

            if integration_result['success']:
                success_msg = f"Sale of {quantity} {recipe_name} recorded successfully!"
                if integration_result['gas_updated']:
                    success_msg += "\n✅ Gas usage automatically updated"
                if integration_result['packing_updated']:
                    success_msg += "\n✅ Packing materials updated"
                if integration_result['budget_updated']:
                    success_msg += "\n✅ Budget tracking updated"

                QMessageBox.information(self, "Success", success_msg)
            else:
                error_msg = f"Sale recorded but some integrations failed:\n" + "\n".join(integration_result['errors'])
                QMessageBox.warning(self, "Partial Success", error_msg)

        except ImportError:
            # Fallback to original message if integration module not available
            QMessageBox.information(
                self, "Success", f"Sale of {quantity} {recipe_name} recorded successfully!")
        except Exception as e:
            print(f"Integration error: {e}")
            QMessageBox.information(
                self, "Success", f"Sale of {quantity} {recipe_name} recorded successfully!\n(Some automatic updates may have failed)")

        # Refresh the sales overview to show the new sale
        self.update_sales_overview()

        # Reset form
        self.sale_date.setDate(QDate.currentDate())
        self.customer_name.clear()
        self.recipe_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
        self.price_spin.setValue(100.0)
        self.sale_notes.clear()
        self.ingredients_table.setRowCount(0)

    def create_order_from_sale(self, sale_id, date, recipe_name, quantity, price, total_amount):
        """Create a corresponding order entry in sales_orders for order management"""
        try:
            # Generate order ID
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Get recipe information for cost calculation
            recipe_row = self.data['recipes'][self.data['recipes']['recipe_name'] == recipe_name]
            if len(recipe_row) == 0:
                print(f"Recipe '{recipe_name}' not found for order creation")
                return False

            recipe = recipe_row.iloc[0]
            recipe_id = recipe['recipe_id']

            # Calculate costs (simplified version)
            packing_materials = "Standard packaging"
            packing_cost = 5.0  # Default packing cost
            preparation_materials = f"Ingredients for {recipe_name}"
            preparation_cost = 20.0  # Default preparation cost
            gas_charges = 2.0
            electricity_charges = 1.5
            total_cost_making = packing_cost + preparation_cost + gas_charges + electricity_charges

            # Try to get more accurate costs from pricing data
            try:
                if 'pricing' in self.data:
                    pricing_df = self.data['pricing']
                    pricing_row = pricing_df[pricing_df['recipe_name'].str.lower() == recipe_name.lower()]
                    if len(pricing_row) > 0:
                        pricing_data = pricing_row.iloc[0]
                        if 'total_cost_making' in pricing_data and pd.notna(pricing_data['total_cost_making']):
                            total_cost_making = float(pricing_data['total_cost_making'])
                        if 'packing_cost' in pricing_data and pd.notna(pricing_data['packing_cost']):
                            packing_cost = float(pricing_data['packing_cost'])
                        if 'preparation_cost' in pricing_data and pd.notna(pricing_data['preparation_cost']):
                            preparation_cost = float(pricing_data['preparation_cost'])
            except Exception as e:
                print(f"Could not get accurate costs from pricing data: {e}")

            # Calculate profit
            profit = total_amount - total_cost_making
            profit_percentage = (profit / total_amount * 100) if total_amount > 0 else 0

            # Create order record
            new_order = {
                'date': date,
                'order_id': order_id,
                'recipe': recipe_name,
                'quantity': quantity,
                'packing_materials': packing_materials,
                'packing_cost': packing_cost,
                'preparation_materials': preparation_materials,
                'preparation_cost': preparation_cost,
                'gas_charges': gas_charges,
                'electricity_charges': electricity_charges,
                'total_cost_making': total_cost_making,
                'our_pricing': price,
                'subtotal': total_amount,
                'discount': 0.0,
                'final_price_after_discount': total_amount,
                'profit': profit,
                'profit_percentage': profit_percentage
            }

            # Add to sales_orders dataframe
            if 'sales_orders' not in self.data:
                # Create empty sales_orders dataframe if it doesn't exist
                self.data['sales_orders'] = pd.DataFrame()

            sales_orders_df = self.data['sales_orders']
            new_order_df = pd.DataFrame([new_order])

            # Concatenate with existing orders
            self.data['sales_orders'] = pd.concat([sales_orders_df, new_order_df], ignore_index=True)

            # Save to CSV
            self.data['sales_orders'].to_csv('data/sales_orders.csv', index=False)

            # Emit signal to refresh order management
            self.sale_added.emit()

            print(f"✅ Created order {order_id} for sale {sale_id}: {quantity} {recipe_name}")
            return True

        except Exception as e:
            print(f"❌ Error creating order from sale: {e}")
            return False

    def update_inventory_for_sale(self, recipe_name, quantity_sold):
        """Update inventory quantities based on recipe ingredients"""
        # Find the recipe
        recipe_row = self.data['recipes'][self.data['recipes']
                                          ['recipe_name'] == recipe_name]
        if len(recipe_row) == 0:
            QMessageBox.warning(self, "Recipe Not Found",
                                f"Recipe '{recipe_name}' not found in database.")
            return False

        recipe = recipe_row.iloc[0]
        recipe_id = recipe['recipe_id']

        print(
            f"Processing sale of {quantity_sold} {recipe_name} (Recipe ID: {recipe_id})")

        # Get inventory dataframe
        # Not strictly used after assignment, but part of original structure
        inventory_df = self.data['inventory']

        # First check if we have the recipe_ingredients data structure (new format)
        if 'recipe_ingredients' in self.data:
            try:
                # Get ingredients for this recipe from the recipe_ingredients dataframe
                recipe_ingredients_df = self.data['recipe_ingredients']
                recipe_ingredients = recipe_ingredients_df[recipe_ingredients_df['recipe_id'] == recipe_id]

                if len(recipe_ingredients) == 0:
                    print(
                        f"No ingredients found for recipe ID {recipe_id} in new format.")
                    # Try the old format as fallback
                    if 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
                        print(
                            "Falling back to embedded recipe ingredients (old format)")
                        try:
                            import json
                            ingredients_list = json.loads(
                                recipe['recipe_ingredients'])

                            # Process ingredients with comprehensive logging (old format)
                            stock_check_results = []
                            inventory_changes = []

                            # Check all ingredients and collect stock information
                            for ingredient_data in ingredients_list:
                                item_name = ingredient_data['item_name']
                                ingredient_qty_total = ingredient_data['quantity'] * quantity_sold
                                ingredient_unit = ingredient_data['unit']

                                # Get detailed stock information
                                allow_sale, stock_info = self.check_ingredient_stock(item_name, ingredient_qty_total, ingredient_unit)
                                stock_check_results.append(stock_info)

                            # Log stock check results
                            self.log_stock_check_results(recipe_name, quantity_sold, stock_check_results)

                            # Process each ingredient (allowing negative inventory)
                            for ingredient_data in ingredients_list:
                                item_name = ingredient_data['item_name']
                                ingredient_qty_total = ingredient_data['quantity'] * quantity_sold
                                ingredient_unit = ingredient_data['unit']

                                # Get before quantity for logging
                                inventory_df = self.data['inventory']
                                before_qty = 0
                                inventory_item = inventory_df[inventory_df['item_name'] == item_name]
                                if len(inventory_item) > 0:
                                    before_qty = float(inventory_item.iloc[0]['quantity']) if pd.notna(inventory_item.iloc[0]['quantity']) else 0

                                # Deduct from inventory
                                self.deduct_from_inventory(
                                    item_name, ingredient_qty_total, ingredient_unit)

                                # Get after quantity for logging
                                inventory_df = self.data['inventory']  # Refresh after deduction
                                inventory_item = inventory_df[inventory_df['item_name'] == item_name]
                                after_qty = float(inventory_item.iloc[0]['quantity']) if len(inventory_item) > 0 and pd.notna(inventory_item.iloc[0]['quantity']) else 0

                                # Track the change
                                inventory_changes.append({
                                    'item_name': item_name,
                                    'before_qty': before_qty,
                                    'deducted_qty': ingredient_qty_total,
                                    'final_qty': after_qty,
                                    'unit': ingredient_unit
                                })

                            inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                          'data', 'inventory.csv')
                            self.data['inventory'].to_csv(
                                inventory_file, index=False)

                            # Generate sale ID for logging
                            sale_id = len(self.sales_df) + 1 if hasattr(self, 'sales_df') else 1

                            # Log comprehensive inventory changes
                            self.log_inventory_changes(sale_id, recipe_name, quantity_sold, inventory_changes)

                            print("Inventory updated successfully using old format with comprehensive logging.")
                            return True
                        except Exception as e:
                            print(
                                f"Error updating inventory from embedded ingredients (old format): {e}")
                            QMessageBox.critical(
                                self, "Error (Old Format Processing)", f"Error processing sale with old ingredient format: {str(e)}")
                            return False
                    else:
                        QMessageBox.warning(
                            self, "No Ingredients", f"No ingredients found for recipe '{recipe_name}' in any format.")
                        return False

                # New format processing with comprehensive logging
                stock_check_results = []
                insufficient_items = []

                print(
                    f"Found {len(recipe_ingredients)} ingredients for recipe ID {recipe_id} (new format)")

                # Check all ingredients and collect detailed stock information
                for _, ingredient_row in recipe_ingredients.iterrows():
                    item_name = ingredient_row['item_name']
                    ingredient_qty_total = float(
                        ingredient_row['quantity']) * quantity_sold
                    ingredient_unit = ingredient_row['unit'] if pd.notna(
                        ingredient_row.get('unit')) else 'g'  # Handle potential NaN unit

                    print(
                        f"Checking ingredient (new format): {item_name}, {ingredient_qty_total} {ingredient_unit}")

                    # Get detailed stock information
                    allow_sale, stock_info = self.check_ingredient_stock(item_name, ingredient_qty_total, ingredient_unit)
                    stock_check_results.append(stock_info)

                    if not stock_info['sufficient']:
                        insufficient_items.append(stock_info)

                # Log stock check results
                self.log_stock_check_results(recipe_name, quantity_sold, stock_check_results)

                # Always proceed with the sale (allowing negative inventory)
                print(
                    f"Proceeding with inventory update for {len(recipe_ingredients)} ingredients (negative inventory allowed)")

                # Track inventory changes for logging
                inventory_changes = []

                for _, ingredient_row in recipe_ingredients.iterrows():
                    item_name = ingredient_row['item_name']
                    ingredient_qty_total = float(
                        ingredient_row['quantity']) * quantity_sold
                    ingredient_unit = ingredient_row['unit'] if pd.notna(
                        ingredient_row.get('unit')) else 'g'

                    # Get before quantity for logging
                    inventory_df = self.data['inventory']
                    before_qty = 0
                    inventory_item = inventory_df[inventory_df['item_name'] == item_name]
                    if len(inventory_item) > 0:
                        before_qty = float(inventory_item.iloc[0]['quantity']) if pd.notna(inventory_item.iloc[0]['quantity']) else 0

                    # Deduct from inventory
                    self.deduct_from_inventory(
                        item_name, ingredient_qty_total, ingredient_unit)

                    # Get after quantity for logging
                    inventory_df = self.data['inventory']  # Refresh after deduction
                    inventory_item = inventory_df[inventory_df['item_name'] == item_name]
                    after_qty = float(inventory_item.iloc[0]['quantity']) if len(inventory_item) > 0 and pd.notna(inventory_item.iloc[0]['quantity']) else 0

                    # Track the change
                    inventory_changes.append({
                        'item_name': item_name,
                        'before_qty': before_qty,
                        'deducted_qty': ingredient_qty_total,
                        'final_qty': after_qty,
                        'unit': ingredient_unit
                    })

                inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                              'data', 'inventory.csv')
                self.data['inventory'].to_csv(inventory_file, index=False)

                # Generate sale ID for logging
                sale_id = len(self.sales_df) + 1 if hasattr(self, 'sales_df') else 1

                # Log comprehensive inventory changes
                self.log_inventory_changes(sale_id, recipe_name, quantity_sold, inventory_changes)

                print("Inventory updated successfully using new format with comprehensive logging.")
                return True

            except Exception as e:
                error_msg = f"Error updating inventory (new format processing): {str(e)}"
                print(error_msg)
                QMessageBox.critical(
                    self, "Error (New Format Processing)", error_msg)
                return False

        # Fallback to old format if 'recipe_ingredients' key is not in self.data (top level)
        elif 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
            print(
                "Attempting update using old embedded recipe ingredients format directly.")
            try:
                import json
                ingredients_list = json.loads(recipe['recipe_ingredients'])

                # Process ingredients with comprehensive logging (old format direct)
                stock_check_results = []
                inventory_changes = []

                # Check all ingredients and collect stock information
                for ingredient_data in ingredients_list:
                    item_name = ingredient_data['item_name']
                    ingredient_qty_total = ingredient_data['quantity'] * quantity_sold
                    ingredient_unit = ingredient_data['unit']

                    # Get detailed stock information
                    allow_sale, stock_info = self.check_ingredient_stock(item_name, ingredient_qty_total, ingredient_unit)
                    stock_check_results.append(stock_info)

                # Log stock check results
                self.log_stock_check_results(recipe_name, quantity_sold, stock_check_results)

                # Process each ingredient (allowing negative inventory)
                for ingredient_data in ingredients_list:
                    item_name = ingredient_data['item_name']
                    ingredient_qty_total = ingredient_data['quantity'] * quantity_sold
                    ingredient_unit = ingredient_data['unit']

                    # Get before quantity for logging
                    inventory_df = self.data['inventory']
                    before_qty = 0
                    inventory_item = inventory_df[inventory_df['item_name'] == item_name]
                    if len(inventory_item) > 0:
                        before_qty = float(inventory_item.iloc[0]['quantity']) if pd.notna(inventory_item.iloc[0]['quantity']) else 0

                    # Deduct from inventory
                    self.deduct_from_inventory(
                        item_name, ingredient_qty_total, ingredient_unit)

                    # Get after quantity for logging
                    inventory_df = self.data['inventory']  # Refresh after deduction
                    inventory_item = inventory_df[inventory_df['item_name'] == item_name]
                    after_qty = float(inventory_item.iloc[0]['quantity']) if len(inventory_item) > 0 and pd.notna(inventory_item.iloc[0]['quantity']) else 0

                    # Track the change
                    inventory_changes.append({
                        'item_name': item_name,
                        'before_qty': before_qty,
                        'deducted_qty': ingredient_qty_total,
                        'final_qty': after_qty,
                        'unit': ingredient_unit
                    })

                inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                              'data', 'inventory.csv')
                self.data['inventory'].to_csv(inventory_file, index=False)

                # Generate sale ID for logging
                sale_id = len(self.sales_df) + 1 if hasattr(self, 'sales_df') else 1

                # Log comprehensive inventory changes
                self.log_inventory_changes(sale_id, recipe_name, quantity_sold, inventory_changes)

                print("Inventory updated successfully using old format (direct) with comprehensive logging.")
                return True
            except Exception as e:
                error_msg = f"Error updating inventory (old format direct processing): {str(e)}"
                print(error_msg)
                QMessageBox.critical(
                    self, "Error (Old Format Direct Processing)", error_msg)
                return False

        else:  # Correctly indented else for the main if/elif
            QMessageBox.warning(
                self, "Missing Data", "Recipe ingredients data not available in any known format.")
            print("Recipe ingredients data not available in any known format.")
            return False

    def deduct_from_inventory(self, item_name, quantity_to_deduct, unit):
        """Deduct the specified quantity from inventory.

        This method now allows negative inventory quantities and will add missing items to inventory.
        If an item doesn't exist, it will be created with a negative quantity.
        """
        # Get inventory dataframe
        inventory_df = self.data['inventory']
        # Check if the inventory dataframe has the required columns
        required_columns = ['item_name', 'quantity', 'unit']
        for col in required_columns:
            if col not in inventory_df.columns:
                # Add the missing column
                inventory_df[col] = ''
                print(f"Added missing column '{col}' to inventory dataframe")

        # Convert quantity to float
        qty_to_deduct = float(quantity_to_deduct)  # Ensure quantity is a float

        # Check if item exists
        inventory_item = inventory_df[inventory_df['item_name'] == item_name]
        if len(inventory_item) == 0:
            # Item doesn't exist, add it to inventory with negative quantity
            print(
                f"Item {item_name} not found in inventory - adding it with negative quantity")

            # Generate a new item_id
            new_id = 1
            if 'item_id' in inventory_df.columns and not inventory_df.empty:
                new_id = inventory_df['item_id'].max(
                ) + 1 if not pd.isna(inventory_df['item_id'].max()) else 1

            # Create a new row for the item
            new_item = pd.DataFrame({
                'item_id': [new_id],
                'item_name': [item_name],
                # Negative quantity since we're using it without having it
                'quantity': [-qty_to_deduct],
                'unit': [unit],
                'category': ['Ingredients'] if 'category' in inventory_df.columns else None,
                'location': ['Kitchen'] if 'location' in inventory_df.columns else None,
                'price': [0] if 'price' in inventory_df.columns else None,
                'reorder_level': [0] if 'reorder_level' in inventory_df.columns else None
            })

            # Add only columns that exist in the inventory dataframe
            new_item = new_item[[
                col for col in new_item.columns if col in inventory_df.columns]]

            # Add the new item to inventory
            inventory_df = pd.concat(
                [inventory_df, new_item], ignore_index=True)
            print(
                f"Added {item_name} to inventory with quantity -{qty_to_deduct} {unit}")

            # Update the data dictionary
            self.data['inventory'] = inventory_df

            # Also add to items dataframe if it doesn't exist there
            if 'items' in self.data:
                items_df = self.data['items']
                if len(items_df[items_df['item_name'] == item_name]) == 0:
                    # Generate a new item_id for items table
                    new_items_id = 1
                    if 'item_id' in items_df.columns and not items_df.empty:
                        new_items_id = items_df['item_id'].max(
                        ) + 1 if not pd.isna(items_df['item_id'].max()) else 1

                    # Create new item for items table
                    new_items_row = pd.DataFrame({
                        'item_id': [new_items_id],
                        'item_name': [item_name],
                        'unit': [unit],
                        'category': ['Ingredients'],
                        'description': [f'Auto-created during sales process'],
                        'default_cost': [0]
                    })

                    # Add only columns that exist in the items dataframe
                    if not items_df.empty:
                        new_items_row = new_items_row[[
                            col for col in new_items_row.columns if col in items_df.columns]]

                    # Add to items dataframe
                    self.data['items'] = pd.concat(
                        [items_df, new_items_row], ignore_index=True)

                    # Save items to CSV
                    try:
                        items_file = os.path.join(os.path.dirname(os.path.dirname(
                            os.path.abspath(__file__))), 'data', 'items.csv')
                        self.data['items'].to_csv(items_file, index=False)
                        print(
                            f"Added {item_name} to items database and saved to {items_file}")
                    except Exception as e:
                        print(f"Error saving items: {e}")

            # Save the updated inventory to CSV
            try:
                inventory_file = os.path.join(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))), 'data', 'inventory.csv')
                inventory_df.to_csv(inventory_file, index=False)
                print(f"Saved updated inventory to {inventory_file}")
            except Exception as e:
                print(f"Error saving inventory: {e}")

            return True

        # Item exists, get its index
        item_index = inventory_item.index[0]

        # Get item's unit
        inv_unit = inventory_df.loc[item_index, 'unit'] if 'unit' in inventory_df.columns and pd.notna(
            inventory_df.loc[item_index, 'unit']) else 'unit'

        # Normalize units to lowercase and strip spaces for better comparison
        inv_unit_lower = inv_unit.lower().strip() if isinstance(inv_unit, str) else 'unit'
        unit_lower = unit.lower().strip() if isinstance(unit, str) else 'unit'

        # Debug output
        print(
            f"Deducting from inventory for {item_name}: {qty_to_deduct} {unit_lower} from inventory unit {inv_unit_lower}")

        # Convert units if necessary
        if inv_unit_lower != unit_lower:
            # Enhanced conversion for common units with more unit variations
            if inv_unit_lower in ['kg', 'kilogram', 'kilograms'] and unit_lower in ['g', 'gram', 'grams']:
                # Convert recipe grams to inventory kg
                qty_to_deduct /= 1000  # Convert g to kg
                print(
                    f"Converting {quantity_to_deduct} {unit_lower} to {qty_to_deduct} {inv_unit_lower}")
            elif inv_unit_lower in ['g', 'gram', 'grams'] and unit_lower in ['kg', 'kilogram', 'kilograms']:
                # Convert recipe kg to inventory g
                qty_to_deduct *= 1000  # Convert kg to g
                print(
                    f"Converting {quantity_to_deduct} {unit_lower} to {qty_to_deduct} {inv_unit_lower}")
            elif inv_unit_lower in ['l', 'liter', 'liters', 'litre', 'litres'] and unit_lower in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres']:
                # Convert recipe ml to inventory L
                qty_to_deduct /= 1000  # Convert ml to L
                print(
                    f"Converting {quantity_to_deduct} {unit_lower} to {qty_to_deduct} {inv_unit_lower}")
            elif inv_unit_lower in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres'] and unit_lower in ['l', 'liter', 'liters', 'litre', 'litres']:
                # Convert recipe L to inventory ml
                qty_to_deduct *= 1000  # Convert L to ml
                print(
                    f"Converting {quantity_to_deduct} {unit_lower} to {qty_to_deduct} {inv_unit_lower}")
            else:
                # Special case: if no unit is specified in recipe but inventory has a unit
                if unit_lower in ['', 'unit', 'each', 'ea'] and inv_unit_lower in ['kg', 'g', 'l', 'ml']:
                    print(
                        f"Recipe has no specific unit for {item_name}, assuming compatible with inventory unit {inv_unit_lower}")
                else:
                    # Log warning about incompatible units
                    print(
                        f"Warning: Incompatible units for {item_name}: {unit_lower} vs {inv_unit_lower}")
                    print(
                        f"Attempting to use quantities as-is, but this may cause incorrect inventory management")

        # Get current quantity
        current_qty = 0
        if 'quantity' in inventory_df.columns:
            current_qty = float(inventory_df.loc[item_index, 'quantity']) if pd.notna(
                inventory_df.loc[item_index, 'quantity']) else 0

        # Update inventory quantities
        if 'qty_used' in inventory_df.columns:
            # Increment the used quantity
            current_used = float(inventory_df.loc[item_index, 'qty_used']) if pd.notna(
                inventory_df.loc[item_index, 'qty_used']) else 0
            inventory_df.loc[item_index,
                             'qty_used'] = current_used + qty_to_deduct
            print(
                f"Updated qty_used for {item_name} to {current_used + qty_to_deduct} {inv_unit_lower}")

        # Update available quantity - allow negative values
        if 'quantity' in inventory_df.columns:
            new_qty = current_qty - qty_to_deduct  # Allow negative quantity
            inventory_df.loc[item_index, 'quantity'] = new_qty
            print(
                f"Updated quantity for {item_name} from {current_qty} to {new_qty} {inv_unit_lower}")

            # Add a warning if quantity is negative
            if new_qty < 0:
                print(
                    f"WARNING: {item_name} now has a negative quantity of {new_qty} {inv_unit_lower}")

        # Update the data dictionary
        self.data['inventory'] = inventory_df

        # Save the updated inventory to CSV
        try:
            inventory_file = os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), 'data', 'inventory.csv')
            inventory_df.to_csv(inventory_file, index=False)
            print(f"Saved updated inventory to {inventory_file}")
        except Exception as e:
            print(f"Error saving inventory: {e}")

        return True

    def setup_sales_analysis_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.sales_analysis_tab)

        header = QLabel("Sales Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        # Create charts
        if len(self.sales_df) > 0:
            # Sales by date chart
            date_chart_label = QLabel("Sales by Date")
            date_chart_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(date_chart_label)

            # Check if total_amount column exists, if not, create it
            sales_df_analysis = self.sales_df.copy()
            if 'total_amount' not in sales_df_analysis.columns:
                if 'price' in sales_df_analysis.columns and 'quantity' in sales_df_analysis.columns:
                    # Calculate total_amount from price and quantity
                    sales_df_analysis['total_amount'] = sales_df_analysis['price'] * \
                        sales_df_analysis['quantity']
                else:
                    # If no price or quantity columns, use a default value of 1 for analysis
                    sales_df_analysis['total_amount'] = 1

            # Convert date column to datetime if it's not already
            if 'date' in sales_df_analysis.columns:
                # Try to convert dates to datetime objects
                try:
                    # Check if it's already a datetime
                    if not pd.api.types.is_datetime64_any_dtype(sales_df_analysis['date']):
                        # Convert to datetime
                        sales_df_analysis['date'] = pd.to_datetime(
                            sales_df_analysis['date'], errors='coerce')
                except Exception as e:
                    print(f"Error converting dates to datetime: {e}")
                    # Create a dummy date column for analysis
                    sales_df_analysis['date'] = pd.date_range(
                        start='2023-01-01', periods=len(sales_df_analysis), freq='D')
            else:
                # If no date column, create a dummy one for analysis
                sales_df_analysis['date'] = pd.date_range(
                    start='2023-01-01', periods=len(sales_df_analysis), freq='D')

            # Group by date - handle both datetime and date objects
            try:
                # Try to group by date part of datetime
                sales_by_date = sales_df_analysis.groupby(sales_df_analysis['date'].dt.date)[
                    'total_amount'].sum().reset_index()
            except AttributeError:
                # Fallback to grouping by the date column directly
                sales_by_date = sales_df_analysis.groupby(
                    'date')['total_amount'].sum().reset_index()

            # Sort by date
            sales_by_date = sales_by_date.sort_values('date')

            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.bar(sales_by_date['date'], sales_by_date['total_amount'])
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Total Sales (₹)')
            ax1.set_title('Sales by Date')
            plt.tight_layout()

            canvas1 = FigureCanvas(fig1)
            layout.addWidget(canvas1)

            # Top selling items chart
            items_chart_label = QLabel("Top Selling Items")
            items_chart_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(items_chart_label)

            # Create agg dict based on columns available
            agg_dict = {}
            if 'total_amount' in sales_df_analysis.columns:
                agg_dict['total_amount'] = 'sum'
            if 'quantity' in sales_df_analysis.columns:
                agg_dict['quantity'] = 'sum'

            # Check which column to use for grouping (item_name or recipe_name)
            group_by_col = None
            if 'item_name' in sales_df_analysis.columns:
                group_by_col = 'item_name'
            elif 'recipe_name' in sales_df_analysis.columns:
                # Create a copy of recipe_name as item_name for compatibility
                sales_df_analysis['item_name'] = sales_df_analysis['recipe_name']
                group_by_col = 'item_name'  # Now we can use item_name
            else:
                # If neither column exists, create a dummy one
                sales_df_analysis['item_name'] = 'Unknown Item'
                group_by_col = 'item_name'

            # Group by the appropriate column
            sales_by_item = sales_df_analysis.groupby(
                group_by_col).agg(agg_dict).reset_index()
            sales_by_item = sales_by_item.sort_values(
                'total_amount', ascending=False).head(10)

            # Create top selling items chart
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.barh(sales_by_item['item_name'], sales_by_item['total_amount'])
            ax2.set_xlabel('Total Sales (₹)')
            ax2.set_ylabel('Item')
            ax2.set_title('Top Selling Items by Revenue')
            plt.tight_layout()

            canvas2 = FigureCanvas(fig2)
            layout.addWidget(canvas2)
        else:
            no_data_label = QLabel("No sales data available for analysis.")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)

    def setup_customer_analysis_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.customer_analysis_tab)

        # Add subheader
        header = QLabel("Customer Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        # Create charts
        if len(self.sales_df) > 0 and 'customer' in self.sales_df.columns:
            # Top customers chart
            customers_chart_label = QLabel("Top Customers")
            customers_chart_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(customers_chart_label)

            # Check if total_amount column exists, if not, create it
            sales_df_customer = self.sales_df.copy()
            if 'total_amount' not in sales_df_customer.columns:
                if 'price' in sales_df_customer.columns and 'quantity' in sales_df_customer.columns:
                    # Calculate total_amount from price and quantity
                    sales_df_customer['total_amount'] = sales_df_customer['price'] * \
                        sales_df_customer['quantity']
                else:
                    # If no price or quantity columns, use a default value of 1 for analysis
                    sales_df_customer['total_amount'] = 1

            # Group by customer
            # Check if sale_id exists, if not use index for counting
            if 'sale_id' in sales_df_customer.columns:
                count_column = 'sale_id'
            else:
                # Use the first column for counting (could be any column)
                count_column = sales_df_customer.columns[0]

            sales_by_customer = sales_df_customer.groupby('customer').agg({
                count_column: 'count',
                'total_amount': 'sum'
            }).reset_index()
            sales_by_customer.columns = [
                'customer', 'num_purchases', 'total_spent']
            sales_by_customer = sales_by_customer.sort_values(
                'total_spent', ascending=False).head(10)

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.barh(sales_by_customer['customer'],
                    sales_by_customer['total_spent'])
            ax.set_xlabel('Total Spent (₹)')
            ax.set_ylabel('Customer')
            ax.set_title('Top Customers by Spending')
            plt.tight_layout()

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

            # Customer table
            table_label = QLabel("Customer Details")
            table_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(table_label)

            customer_table = QTableWidget()
            customer_table.setColumnCount(3)
            customer_table.setHorizontalHeaderLabels(
                ["Customer", "Number of Purchases", "Total Spent"])
            customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            customer_table.setRowCount(len(sales_by_customer))
            for i, (_, row) in enumerate(sales_by_customer.iterrows()):
                customer_table.setItem(i, 0, QTableWidgetItem(row['customer']))
                customer_table.setItem(
                    i, 1, QTableWidgetItem(str(row['num_purchases'])))
                customer_table.setItem(i, 2, QTableWidgetItem(
                    f"₹{row['total_spent']:.2f}"))

            layout.addWidget(customer_table)
        else:
            no_data_label = QLabel("No customer data available for analysis.")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)

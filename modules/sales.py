from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                               QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                               QMessageBox, QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import calendar
import os


class SalesWidget(QWidget):
    def __init__(self, data, inventory_widget, parent=None):
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
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(
            ["Sale ID", "Item", "Quantity", "Price/Unit", "Total", "Date"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
            return

        # Find the recipe in the dataframe
        recipe_row = self.data['recipes'][self.data['recipes']
                                          ['recipe_name'] == recipe_name]
        if len(recipe_row) > 0:
            # For now, just set a default price
            # In a real application, this would come from a price database
            self.price_spin.setValue(150.0)  # Default price for recipes

            # Show ingredients in the table
            self.display_recipe_ingredients(recipe_name)

        # Update the total amount
        self.update_total_amount()

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

                    # Check if in stock
                    in_stock = self.check_ingredient_stock(
                        ingredient['item_name'], qty, ingredient['unit'])
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
                self.ingredients_table.setItem(
                    i, 0, QTableWidgetItem(ingredient_text.strip()))
                self.ingredients_table.setItem(
                    i, 1, QTableWidgetItem("1"))  # Default quantity
                self.ingredients_table.setItem(
                    i, 2, QTableWidgetItem("unit"))  # Default unit
                self.ingredients_table.setItem(
                    i, 3, QTableWidgetItem("Unknown"))

    def check_ingredient_stock(self, item_name, quantity, unit):
        """Check if the ingredient is in stock in sufficient quantity

        Note: This method now always returns True to allow sales even with insufficient inventory.
        It will report the status of the ingredient stock but won't block the sale.
        """
        # Get inventory dataframe
        inventory_df = self.data['inventory']

        # Check if item exists
        if 'item_name' not in inventory_df.columns:
            print(
                f"Item {item_name} not found in inventory - column 'item_name' missing")
            # Item will be added automatically during the sale process
            return True

        inventory_item = inventory_df[inventory_df['item_name'] == item_name]
        if len(inventory_item) == 0:
            print(f"Item {item_name} not found in inventory")
            # Item will be added automatically during the sale process
            return True

        # Check quantity
        item = inventory_item.iloc[0]
        if 'quantity' not in item or pd.isna(item['quantity']):
            print(f"Item {item_name} has no quantity specified")
            # Item will be updated with a proper quantity during the sale process
            return True

        inv_qty = float(item['quantity'])
        inv_unit = item['unit'] if 'unit' in item and pd.notna(
            item['unit']) else 'unit'

        # Normalize units to lowercase and strip spaces for better comparison
        inv_unit_lower = inv_unit.lower().strip()
        unit_lower = unit.lower().strip() if isinstance(unit, str) else 'unit'

        # Debug output
        print(
            f"Checking stock for {item_name}: Need {quantity} {unit_lower}, have {inv_qty} {inv_unit_lower}")

        # Convert quantities to a common unit for comparison
        qty_needed = float(quantity)  # Ensure quantity is a float

        # Check units match and convert if necessary
        if inv_unit_lower != unit_lower:
            # Convert to inventory unit
            if (inv_unit_lower in ['kg', 'kilogram', 'kilograms'] and unit_lower in ['grams', 'g', 'gram']):
                # Convert recipe grams to inventory kg
                qty_needed = qty_needed / 1000
                print(
                    f"Converting {quantity} {unit_lower} to {qty_needed} {inv_unit_lower}")
            elif (inv_unit_lower in ['grams', 'g', 'gram'] and unit_lower in ['kg', 'kilogram', 'kilograms']):
                # Convert recipe kg to inventory grams
                qty_needed = qty_needed * 1000
                print(
                    f"Converting {quantity} {unit_lower} to {qty_needed} {inv_unit_lower}")
            elif (inv_unit_lower in ['l', 'liter', 'liters', 'litre', 'litres'] and unit_lower in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres']):
                # Convert recipe ml to inventory L
                qty_needed = qty_needed / 1000
                print(
                    f"Converting {quantity} {unit_lower} to {qty_needed} {inv_unit_lower}")
            elif (inv_unit_lower in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres'] and unit_lower in ['l', 'liter', 'liters', 'litre', 'litres']):
                # Convert recipe L to inventory ml
                qty_needed = qty_needed * 1000
                print(
                    f"Converting {quantity} {unit_lower} to {qty_needed} {inv_unit_lower}")
            else:
                # Special case: if no unit is specified in recipe but inventory has a unit
                if unit_lower in ['', 'unit', 'each', 'ea'] and inv_unit_lower in ['kg', 'g', 'l', 'ml']:
                    print(
                        f"Recipe has no specific unit for {item_name}, assuming compatible with inventory unit {inv_unit_lower}")
                else:
                    # Units don't match and can't be converted
                    print(
                        f"Warning: Incompatible units for {item_name}: {unit_lower} vs {inv_unit_lower}")
                    # Continue anyway but with a warning
                    print(
                        f"Attempting to use quantities as-is, but this may cause incorrect inventory management")

        # Check if enough quantity is available
        has_enough = inv_qty >= qty_needed
        print(
            f"Stock check result for {item_name}: Need {qty_needed} {inv_unit_lower}, have {inv_qty} {inv_unit_lower}, enough: {has_enough}")

        # Always return True to allow the sale to proceed, even with insufficient inventory
        return True

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

        # Update inventory based on recipe ingredients using new integration system
        self.update_inventory_for_sale(recipe_name, quantity)

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

        # Reset form
        self.sale_date.setDate(QDate.currentDate())
        self.customer_name.clear()
        self.recipe_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
        self.price_spin.setValue(100.0)
        self.sale_notes.clear()
        self.ingredients_table.setRowCount(0)

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

                            # Check stock before deducting for old format too
                            all_ingredients_available_old = True
                            missing_ingredients_old = []
                            for ingredient_data in ingredients_list:
                                item_name = ingredient_data['item_name']
                                ingredient_qty_total = ingredient_data['quantity'] * \
                                    quantity_sold
                                ingredient_unit = ingredient_data['unit']
                                if not self.check_ingredient_stock(item_name, ingredient_qty_total, ingredient_unit):
                                    all_ingredients_available_old = False
                                    missing_ingredients_old.append(
                                        f"{item_name} ({ingredient_qty_total} {ingredient_unit})")

                            if not all_ingredients_available_old:
                                error_msg = f"Cannot complete sale (old format check) due to insufficient inventory of:\n\n" + "\n".join(
                                    missing_ingredients_old)
                                print(error_msg)
                                QMessageBox.warning(
                                    self, "Insufficient Ingredients (Old Format)", error_msg)
                                return False

                            # Process each ingredient if stock is available
                            for ingredient_data in ingredients_list:
                                item_name = ingredient_data['item_name']
                                ingredient_qty_total = ingredient_data['quantity'] * \
                                    quantity_sold
                                ingredient_unit = ingredient_data['unit']
                                self.deduct_from_inventory(
                                    item_name, ingredient_qty_total, ingredient_unit)

                            inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                          'data', 'inventory.csv')
                            self.data['inventory'].to_csv(
                                inventory_file, index=False)
                            print("Inventory updated successfully using old format.")
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

                # New format processing
                all_ingredients_available = True
                missing_ingredients = []

                print(
                    f"Found {len(recipe_ingredients)} ingredients for recipe ID {recipe_id} (new format)")

                for _, ingredient_row in recipe_ingredients.iterrows():
                    item_name = ingredient_row['item_name']
                    ingredient_qty_total = float(
                        ingredient_row['quantity']) * quantity_sold
                    ingredient_unit = ingredient_row['unit'] if pd.notna(
                        ingredient_row.get('unit')) else 'g'  # Handle potential NaN unit

                    print(
                        f"Checking ingredient (new format): {item_name}, {ingredient_qty_total} {ingredient_unit}")

                    if not self.check_ingredient_stock(item_name, ingredient_qty_total, ingredient_unit):
                        all_ingredients_available = False
                        missing_ingredients.append(
                            f"{item_name} ({ingredient_qty_total} {ingredient_unit})")

                if not all_ingredients_available:
                    error_msg = f"Cannot complete sale (new format check) due to insufficient inventory of:\n\n" + "\n".join(
                        missing_ingredients)
                    print(error_msg)
                    QMessageBox.warning(
                        self, "Insufficient Ingredients (New Format)", error_msg)
                    return False

                print(
                    "All ingredients available (new format), proceeding with inventory update")

                for _, ingredient_row in recipe_ingredients.iterrows():
                    item_name = ingredient_row['item_name']
                    ingredient_qty_total = float(
                        ingredient_row['quantity']) * quantity_sold
                    ingredient_unit = ingredient_row['unit'] if pd.notna(
                        ingredient_row.get('unit')) else 'g'

                    self.deduct_from_inventory(
                        item_name, ingredient_qty_total, ingredient_unit)

                inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                              'data', 'inventory.csv')
                self.data['inventory'].to_csv(inventory_file, index=False)
                print("Inventory updated successfully using new format.")
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

                # Check stock before deducting for old format too
                all_ingredients_available_old_direct = True
                missing_ingredients_old_direct = []
                for ingredient_data in ingredients_list:
                    item_name = ingredient_data['item_name']
                    ingredient_qty_total = ingredient_data['quantity'] * \
                        quantity_sold
                    ingredient_unit = ingredient_data['unit']
                    if not self.check_ingredient_stock(item_name, ingredient_qty_total, ingredient_unit):
                        all_ingredients_available_old_direct = False
                        missing_ingredients_old_direct.append(
                            f"{item_name} ({ingredient_qty_total} {ingredient_unit})")

                if not all_ingredients_available_old_direct:
                    error_msg = f"Cannot complete sale (old format direct check) due to insufficient inventory of:\n\n" + "\n".join(
                        missing_ingredients_old_direct)
                    print(error_msg)
                    QMessageBox.warning(
                        self, "Insufficient Ingredients (Old Format - Direct)", error_msg)
                    return False

                for ingredient_data in ingredients_list:
                    item_name = ingredient_data['item_name']
                    ingredient_qty_total = ingredient_data['quantity'] * \
                        quantity_sold
                    ingredient_unit = ingredient_data['unit']
                    self.deduct_from_inventory(
                        item_name, ingredient_qty_total, ingredient_unit)

                inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                              'data', 'inventory.csv')
                self.data['inventory'].to_csv(inventory_file, index=False)
                print("Inventory updated successfully using old format (direct).")
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

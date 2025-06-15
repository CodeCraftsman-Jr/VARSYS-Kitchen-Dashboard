from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                             QMessageBox, QHeaderView, QSplitter, QTextEdit, QDialog, QCheckBox,
                             QApplication, QMenu, QInputDialog, QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QAction, QKeySequence, QShortcut
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import os
from utils.table_styling import apply_universal_column_resizing

class MealPlanningWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        # Always try to load fresh data from CSV file first
        self.meal_plan_df = self._load_meal_plan_from_csv()

        # If CSV loading failed, fall back to data dictionary
        if self.meal_plan_df.empty:
            # Check if we have the new data structure or the old one
            if 'meal_plan_items' in data:
                self.meal_plan_df = data['meal_plan_items'].copy()
                print(f"Using meal_plan_items with {len(self.meal_plan_df)} rows")
            elif 'meal_plan' in data:
                self.meal_plan_df = data['meal_plan'].copy()
                print(f"Using meal_plan with {len(self.meal_plan_df)} rows")
            else:
                # Create empty DataFrame with required columns
                self.meal_plan_df = pd.DataFrame(columns=['item_id', 'plan_id', 'day', 'meal_type', 'recipe_id', 'recipe_name', 'servings', 'notes'])
                print("Created empty meal plan DataFrame")
        
        # Make sure we have the recipes DataFrame
        if 'recipes' in data:
            self.recipes_df = data['recipes'].copy()
        else:
            self.recipes_df = pd.DataFrame(columns=['recipe_id', 'recipe_name', 'category', 'servings', 'prep_time', 'cook_time', 'description'])
        
        # Make sure required columns exist in the meal plan DataFrame
        required_columns = ['day', 'meal_type', 'recipe_name', 'servings']
        for col in required_columns:
            if col not in self.meal_plan_df.columns:
                self.meal_plan_df[col] = ''
                print(f"Added missing column '{col}' to meal plan data")
        
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Meal Planning")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
    
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs for different meal planning views
        self.meal_plan_tab = QWidget()
        self.recipe_tab = QWidget()
        self.nutrition_tab = QWidget()
        self.shopping_tab = QWidget()
        self.missing_ingredients_tab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.meal_plan_tab, "Weekly Meal Plan")
        self.tabs.addTab(self.recipe_tab, "Recipe Database")
        self.tabs.addTab(self.nutrition_tab, "Nutritional Analysis")
        self.tabs.addTab(self.shopping_tab, "Shopping List Generator")
        self.tabs.addTab(self.missing_ingredients_tab, "Missing Ingredients")
        
        # Set up each tab
        self.setup_meal_plan_tab()
        self.setup_recipe_tab()
        self.setup_nutrition_tab()
        self.setup_shopping_tab()
        self.setup_missing_ingredients_tab()

        # Connect tab change event to refresh data
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        """Handle tab change events to refresh data"""
        try:
            tab_name = self.tabs.tabText(index)

            if tab_name == "Recipe Database":
                # Refresh recipes data
                if 'recipes' in self.data:
                    self.recipes_df = self.data['recipes'].copy()
                    self.populate_recipe_table()

            elif tab_name == "Weekly Meal Plan":
                # Refresh meal plan data
                self.meal_plan_df = self._load_meal_plan_from_csv()
                self.update_meal_plan_table()

            elif tab_name == "Missing Ingredients":
                # Refresh missing ingredients when tab is opened
                if hasattr(self, 'missing_ingredients_table'):
                    self.refresh_missing_ingredients()

        except Exception as e:
            print(f"Error refreshing meal planning tab data: {e}")

    def refresh_all_data(self):
        """Force refresh all data from CSV files"""
        try:
            # Reload data from CSV files
            import pandas as pd
            import os

            if os.path.exists('data/recipes.csv'):
                self.data['recipes'] = pd.read_csv('data/recipes.csv')
                self.recipes_df = self.data['recipes'].copy()

            # Refresh meal plan data
            self.meal_plan_df = self._load_meal_plan_from_csv()

            # Update all tables
            self.populate_recipe_table()
            if hasattr(self, 'update_meal_plan_table'):
                self.update_meal_plan_table()

            print("Meal planning data refreshed successfully")

        except Exception as e:
            print(f"Error refreshing meal planning data: {e}")

    def _load_meal_plan_from_csv(self):
        """Load meal plan data directly from CSV file"""
        try:
            import os
            meal_plan_file = 'data/meal_plan.csv'
            if os.path.exists(meal_plan_file):
                df = pd.read_csv(meal_plan_file)
                print(f"Loaded meal plan data from CSV with {len(df)} rows")
                return df
            else:
                print(f"Meal plan CSV file '{meal_plan_file}' not found")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading meal plan from CSV: {e}")
            return pd.DataFrame()
    
    def setup_meal_plan_tab(self):
        # Clear the existing layout if it exists
        if self.meal_plan_tab.layout():
            QWidget().setLayout(self.meal_plan_tab.layout())

        # Create layout for the tab
        layout = QVBoxLayout(self.meal_plan_tab)

        # Add subheader and refresh button in a horizontal layout
        header_layout = QHBoxLayout()
        header = QLabel("Weekly Meal Plan")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header)

        # Add refresh button
        self.refresh_meal_plan_button = QPushButton("Refresh Meal Plan")
        self.refresh_meal_plan_button.clicked.connect(self.refresh_meal_plan_data)
        header_layout.addWidget(self.refresh_meal_plan_button)
        header_layout.addStretch()  # Push button to the right

        layout.addLayout(header_layout)
        
        # Create table for meal plan
        self.meal_plan_table = QTableWidget()
        layout.addWidget(self.meal_plan_table)
        
        # Set up table columns with added snack options
        columns = ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
        self.meal_plan_table.setColumnCount(len(columns))
        self.meal_plan_table.setHorizontalHeaderLabels(columns)

        # FIXED: Enable manual column resizing for Weekly Meal Plan table
        print("🔧 Setting up Weekly Meal Plan table column resizing...")
        meal_plan_header = self.meal_plan_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        for col in range(len(columns)):
            meal_plan_header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Meal Plan Column {col} ({columns[col]}): Interactive")

        # Set default column widths
        meal_plan_default_widths = {
            0: 100,  # Day
            1: 150,  # Breakfast
            2: 120,  # Morning Snack
            3: 150,  # Lunch
            4: 120,  # Afternoon Snack
            5: 150   # Dinner
        }
        for col, width in meal_plan_default_widths.items():
            self.meal_plan_table.setColumnWidth(col, width)
            print(f"   Meal Plan Column {col}: {width}px")

        # Basic header configuration
        meal_plan_header.setStretchLastSection(False)
        meal_plan_header.setMinimumSectionSize(80)
        print("✅ Weekly Meal Plan table column resizing enabled!")
        
        # Define days of week
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
        
        # Populate the table - allowing for multiple items per meal
        self.meal_plan_table.setRowCount(len(days_of_week))
        
        # Track row heights needed for each day
        day_row_heights = {day: 1 for day in days_of_week}
        
        # First pass: Count how many items we have per day/meal to determine row heights
        for day in days_of_week:
            for meal_type in meal_types:
                # Get all recipes for this day and meal type
                meal_items = self.meal_plan_df[
                    (self.meal_plan_df['day'] == day) & 
                    (self.meal_plan_df['meal_type'] == meal_type)
                ]
                
                # Update the maximum number of items for this day
                if len(meal_items) > day_row_heights[day]:
                    day_row_heights[day] = len(meal_items)
        
        # Create the table with the proper number of rows
        total_rows = sum(day_row_heights.values())
        self.meal_plan_table.setRowCount(total_rows)
        
        # Second pass: Fill in the table
        current_row = 0
        for i, day in enumerate(days_of_week):
            # Set the day in the first column, merge cells if needed
            day_height = day_row_heights[day]
            
            if day_height > 1:
                self.meal_plan_table.setSpan(current_row, 0, day_height, 1)
            
            day_item = QTableWidgetItem(day)
            day_item.setBackground(QColor(240, 240, 240))  # Light gray background
            day_item.setTextAlignment(Qt.AlignCenter)
            self.meal_plan_table.setItem(current_row, 0, day_item)
            
            # Fill in each meal type column
            for j, meal_type in enumerate(meal_types):
                col_index = j + 1  # +1 because column 0 is for days
                
                # Get all recipes for this day and meal type
                meal_items = self.meal_plan_df[
                    (self.meal_plan_df['day'] == day) & 
                    (self.meal_plan_df['meal_type'] == meal_type)
                ]
                
                if len(meal_items) > 0:
                    # We have recipes for this meal
                    for k, (_, recipe) in enumerate(meal_items.iterrows()):
                        recipe_text = recipe['recipe_name']
                        if 'notes' in recipe and pd.notna(recipe['notes']) and recipe['notes'] != '':
                            recipe_text += f" ({recipe['notes']})"
                            
                        recipe_item = QTableWidgetItem(recipe_text)
                        self.meal_plan_table.setItem(current_row + k, col_index, recipe_item)
                else:
                    # No recipes, but we still need to fill cells
                    if day_height > 1:
                        self.meal_plan_table.setSpan(current_row, col_index, day_height, 1)
                    self.meal_plan_table.setItem(current_row, col_index, QTableWidgetItem(""))
            
            # Move to the next row block
            current_row += day_height
        
        # Set row heights to be adequate
        for row in range(self.meal_plan_table.rowCount()):
            self.meal_plan_table.setRowHeight(row, 40)
            
        # Add last updated timestamp row at the bottom
        timestamp_row = self.meal_plan_table.rowCount()
        self.meal_plan_table.setRowCount(timestamp_row + 1)
        
        # Get the latest update time
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'date_added' in self.meal_plan_df.columns and len(self.meal_plan_df) > 0:
            try:
                last_updated = self.meal_plan_df['date_added'].max()
            except:
                pass
                
        update_item = QTableWidgetItem(f"Last Updated: {last_updated}")
        update_item.setBackground(QColor(230, 230, 230))
        self.meal_plan_table.setSpan(timestamp_row, 0, 1, len(columns))
        self.meal_plan_table.setItem(timestamp_row, 0, update_item)
        
        # Enhanced meal plan management section
        meal_management_group = QGroupBox("Meal Plan Management")
        meal_management_layout = QVBoxLayout(meal_management_group)
        layout.addWidget(meal_management_group)

        # Quick add section
        quick_add_group = QGroupBox("Quick Add/Edit Meal")
        quick_add_layout = QFormLayout(quick_add_group)

        # Day selection
        self.day_combo = QComboBox()
        self.day_combo.addItems(days_of_week)
        quick_add_layout.addRow("Day:", self.day_combo)

        # Meal type selection with added snack options
        meal_type_label = QLabel("Meal Type:")
        self.meal_type_combo = QComboBox()
        self.meal_type_combo.addItems(["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"])
        quick_add_layout.addRow(meal_type_label, self.meal_type_combo)

        # Recipe selection with search capability
        recipe_layout = QHBoxLayout()
        self.recipe_combo = QComboBox()
        self.recipe_combo.setEditable(True)
        self.recipe_combo.addItem("Select Recipe...")
        self.recipe_combo.addItems(self.recipes_df['recipe_name'].tolist())
        recipe_layout.addWidget(self.recipe_combo)

        # Recipe search button
        search_recipe_btn = QPushButton("🔍")
        search_recipe_btn.setMaximumWidth(30)
        search_recipe_btn.setToolTip("Search recipes")
        search_recipe_btn.clicked.connect(self.show_recipe_search_dialog)
        recipe_layout.addWidget(search_recipe_btn)

        quick_add_layout.addRow("Recipe:", recipe_layout)

        # Servings
        self.servings_spin = QSpinBox()
        self.servings_spin.setMinimum(1)
        self.servings_spin.setMaximum(20)
        self.servings_spin.setValue(1)
        quick_add_layout.addRow("Servings:", self.servings_spin)

        # Notes
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes (e.g., 'extra spicy', 'for guests')")
        quick_add_layout.addRow("Notes:", self.notes_edit)

        meal_management_layout.addWidget(quick_add_group)

        # Action buttons
        buttons_layout = QHBoxLayout()

        # Add/Update button
        self.add_meal_button = QPushButton("➕ Add/Update Meal")
        self.add_meal_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.add_meal_button.clicked.connect(self.add_update_meal)
        buttons_layout.addWidget(self.add_meal_button)

        # Edit meal plan button
        self.edit_meal_plan_btn = QPushButton("✏️ Edit Meal Plan")
        self.edit_meal_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        self.edit_meal_plan_btn.clicked.connect(self.show_meal_plan_editor)
        buttons_layout.addWidget(self.edit_meal_plan_btn)

        # Delete button
        self.delete_meal_button = QPushButton("🗑️ Delete Selected")
        self.delete_meal_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #b02a37;
            }
        """)
        self.delete_meal_button.clicked.connect(self.delete_selected_meal)
        buttons_layout.addWidget(self.delete_meal_button)

        # Clear all button
        self.clear_week_btn = QPushButton("🗑️ Clear Week")
        self.clear_week_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        self.clear_week_btn.clicked.connect(self.clear_week_meal_plan)
        buttons_layout.addWidget(self.clear_week_btn)

        # Generate meal plan button
        self.generate_plan_btn = QPushButton("🎲 Auto Generate")
        self.generate_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #a569bd;
            }
            QPushButton:pressed {
                background-color: #8e44ad;
            }
        """)
        self.generate_plan_btn.clicked.connect(self.auto_generate_meal_plan)
        buttons_layout.addWidget(self.generate_plan_btn)

        meal_management_layout.addLayout(buttons_layout)

        # Enable table selection for editing
        self.meal_plan_table.itemSelectionChanged.connect(self.on_meal_plan_selection_changed)
    
    def add_update_meal(self):
        # Check if a recipe is selected
        if self.recipe_combo.currentText() == "Select Recipe...":
            QMessageBox.warning(self, "Warning", "Please select a recipe.")
            return

        # Get values from form
        day = self.day_combo.currentText()
        meal_type = self.meal_type_combo.currentText()
        recipe = self.recipe_combo.currentText()
        servings = self.servings_spin.value()
        notes = self.notes_edit.text()

        # Get recipe details
        recipe_matches = self.recipes_df[self.recipes_df['recipe_name'] == recipe]
        if recipe_matches.empty:
            QMessageBox.warning(self, "Warning", f"Recipe '{recipe}' not found in database.")
            return

        recipe_data = recipe_matches.iloc[0]

        # Check if this day and meal type already exists
        existing_meal = self.meal_plan_df[
            (self.meal_plan_df['day'] == day) &
            (self.meal_plan_df['meal_type'] == meal_type)
        ]

        if len(existing_meal) > 0:
            # Confirm update
            reply = QMessageBox.question(
                self,
                "Update Existing Meal",
                f"A meal already exists for {day} {meal_type}.\nDo you want to replace it with {recipe}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

            # Update existing meal
            self.meal_plan_df.loc[
                (self.meal_plan_df['day'] == day) &
                (self.meal_plan_df['meal_type'] == meal_type),
                ['recipe_id', 'recipe_name', 'servings', 'prep_time', 'cook_time', 'notes']
            ] = [recipe_data['recipe_id'], recipe, servings, recipe_data['prep_time'], recipe_data['cook_time'], notes]
            action = "Updated"
        else:
            # Add new meal
            new_meal = {
                'day': day,
                'meal_type': meal_type,
                'recipe_id': recipe_data['recipe_id'],
                'recipe_name': recipe,
                'servings': servings,
                'prep_time': recipe_data['prep_time'],
                'cook_time': recipe_data['cook_time'],
                'notes': notes
            }
            self.meal_plan_df = pd.concat([self.meal_plan_df, pd.DataFrame([new_meal])], ignore_index=True)
            action = "Added"

        # Save to CSV
        self.meal_plan_df.to_csv('data/meal_plan.csv', index=False)

        # Update data dictionary
        self.data['meal_plan'] = self.meal_plan_df

        # Show success message
        QMessageBox.information(self, "Success", f"{action} {recipe} for {day} {meal_type}!")

        # Clear form
        self.recipe_combo.setCurrentIndex(0)
        self.servings_spin.setValue(1)
        self.notes_edit.clear()

        # Update the meal plan table
        self.setup_meal_plan_tab()

    def delete_selected_meal(self):
        """Delete the selected meal from the meal plan"""
        # Check if a meal is selected in the table
        if not hasattr(self, 'meal_plan_table') or not self.meal_plan_table.selectedItems():
            QMessageBox.warning(self, "Warning", "Please select a meal from the meal plan table to delete.")
            return

        # Get selected row
        selected_row = self.meal_plan_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a meal to delete.")
            return

        # Get meal details from the table
        day = self.meal_plan_table.item(selected_row, 0).text()
        meal_type = self.meal_plan_table.item(selected_row, 1).text()
        recipe_name = self.meal_plan_table.item(selected_row, 2).text()

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete:\n\n{day} - {meal_type}\nRecipe: {recipe_name}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Remove from dataframe
                self.meal_plan_df = self.meal_plan_df[
                    ~((self.meal_plan_df['day'] == day) &
                      (self.meal_plan_df['meal_type'] == meal_type))
                ].reset_index(drop=True)

                # Save to CSV
                self.meal_plan_df.to_csv('data/meal_plan.csv', index=False)

                # Update data dictionary
                self.data['meal_plan'] = self.meal_plan_df

                # Refresh the meal plan table
                self.setup_meal_plan_tab()

                # Show success message
                QMessageBox.information(self, "Success", f"Deleted {recipe_name} from {day} {meal_type}!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete meal: {str(e)}")

    def refresh_meal_plan_data(self):
        """Reload meal plan data from CSV file and refresh the display"""
        try:
            import os
            # Reload meal plan data from CSV
            meal_plan_file = 'data/meal_plan.csv'
            if os.path.exists(meal_plan_file):
                # Load fresh data from CSV
                fresh_meal_plan_df = pd.read_csv(meal_plan_file)
                print(f"Reloaded meal plan data with {len(fresh_meal_plan_df)} rows")

                # Update the internal dataframe
                self.meal_plan_df = fresh_meal_plan_df.copy()

                # Update the data dictionary
                self.data['meal_plan'] = self.meal_plan_df

                # Refresh the meal plan table display
                self.setup_meal_plan_tab()

                # Show success message
                QMessageBox.information(self, "Refresh Complete",
                                      f"Meal plan data refreshed successfully. Loaded {len(self.meal_plan_df)} meal entries.")
            else:
                QMessageBox.warning(self, "File Not Found",
                                  f"Meal plan file '{meal_plan_file}' not found.")
        except Exception as e:
            print(f"Error refreshing meal plan data: {e}")
            QMessageBox.warning(self, "Refresh Error",
                              f"Failed to refresh meal plan data: {str(e)}")

    def show_recipe_search_dialog(self):
        """Show a dialog to search and select recipes"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Search Recipes")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)

        layout = QVBoxLayout(dialog)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_input = QLineEdit()
        search_input.setPlaceholderText("Type recipe name or ingredient...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        layout.addLayout(search_layout)

        # Recipe list
        recipe_list = QListWidget()
        layout.addWidget(recipe_list)

        # Populate initial list
        def populate_list(filter_text=""):
            recipe_list.clear()
            for _, recipe in self.recipes_df.iterrows():
                recipe_name = recipe['recipe_name']
                if not filter_text or filter_text.lower() in recipe_name.lower():
                    item = QListWidgetItem(f"{recipe_name} ({recipe['prep_time']}+{recipe['cook_time']} min)")
                    item.setData(Qt.UserRole, recipe_name)
                    recipe_list.addItem(item)

        populate_list()
        search_input.textChanged.connect(populate_list)

        # Buttons
        button_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(select_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # Connect buttons
        def select_recipe():
            current_item = recipe_list.currentItem()
            if current_item:
                recipe_name = current_item.data(Qt.UserRole)
                # Find the recipe in combo box and select it
                index = self.recipe_combo.findText(recipe_name)
                if index >= 0:
                    self.recipe_combo.setCurrentIndex(index)
                dialog.accept()

        select_btn.clicked.connect(select_recipe)
        cancel_btn.clicked.connect(dialog.reject)
        recipe_list.itemDoubleClicked.connect(select_recipe)

        dialog.exec_()

    def on_meal_plan_selection_changed(self):
        """Handle meal plan table selection changes"""
        selected_items = self.meal_plan_table.selectedItems()
        if selected_items:
            # Get the selected row
            row = selected_items[0].row()

            # Skip if it's the timestamp row
            if row >= len(self.meal_plan_df):
                return

            # Try to extract meal information from the table
            try:
                day_item = self.meal_plan_table.item(row, 0)
                if day_item and day_item.text() in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                    # Find the corresponding meal in the dataframe
                    day = day_item.text()

                    # Set the day in the combo box
                    day_index = self.day_combo.findText(day)
                    if day_index >= 0:
                        self.day_combo.setCurrentIndex(day_index)

            except Exception as e:
                print(f"Error handling meal plan selection: {e}")

    def show_meal_plan_editor(self):
        """Show comprehensive meal plan editor dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Meal Plan Editor")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Header
        header_label = QLabel("Weekly Meal Plan Editor")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header_label)

        # Create table for editing
        edit_table = QTableWidget()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meals = ['Breakfast', 'Lunch', 'Dinner']

        edit_table.setRowCount(len(days))
        edit_table.setColumnCount(len(meals) + 1)  # +1 for day column
        edit_table.setHorizontalHeaderLabels(['Day'] + meals)
        edit_table.setVerticalHeaderLabels(days)

        # Populate table with current meal plan
        for i, day in enumerate(days):
            # Day column
            day_item = QTableWidgetItem(day)
            day_item.setFlags(day_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            day_item.setBackground(QColor(240, 240, 240))
            edit_table.setItem(i, 0, day_item)

            # Meal columns
            for j, meal in enumerate(meals):
                # Find existing meal
                existing_meals = self.meal_plan_df[
                    (self.meal_plan_df['day'] == day) &
                    (self.meal_plan_df['meal_type'] == meal)
                ]

                if not existing_meals.empty:
                    recipe_name = existing_meals.iloc[0]['recipe_name']
                    meal_item = QTableWidgetItem(recipe_name)
                else:
                    meal_item = QTableWidgetItem("")

                meal_item.setData(Qt.UserRole, {'day': day, 'meal_type': meal})
                edit_table.setItem(i, j + 1, meal_item)

        edit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(edit_table)

        # Instructions
        instructions = QLabel("Double-click a cell to edit. Enter recipe names or leave blank to remove meals.")
        instructions.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(instructions)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
        """)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        # Save function
        def save_changes():
            try:
                # Create new meal plan dataframe
                new_meal_plan = []

                for i in range(edit_table.rowCount()):
                    day = days[i]
                    for j in range(1, edit_table.columnCount()):  # Skip day column
                        meal_type = meals[j - 1]
                        item = edit_table.item(i, j)

                        if item and item.text().strip():
                            recipe_name = item.text().strip()

                            # Find recipe details
                            recipe_matches = self.recipes_df[self.recipes_df['recipe_name'] == recipe_name]
                            if not recipe_matches.empty:
                                recipe_data = recipe_matches.iloc[0]
                                new_meal_plan.append({
                                    'day': day,
                                    'meal_type': meal_type,
                                    'recipe_id': recipe_data['recipe_id'],
                                    'recipe_name': recipe_name,
                                    'servings': 1,
                                    'prep_time': recipe_data['prep_time'],
                                    'cook_time': recipe_data['cook_time']
                                })

                # Update meal plan dataframe
                self.meal_plan_df = pd.DataFrame(new_meal_plan)

                # Save to CSV
                self.meal_plan_df.to_csv('data/meal_plan.csv', index=False)

                # Update data dictionary
                self.data['meal_plan'] = self.meal_plan_df

                # Refresh display
                self.setup_meal_plan_tab()

                QMessageBox.information(dialog, "Success", "Meal plan updated successfully!")
                dialog.accept()

            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save changes: {str(e)}")

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec_()

    def clear_week_meal_plan(self):
        """Clear the entire week's meal plan"""
        reply = QMessageBox.question(
            self,
            "Clear Week",
            "Are you sure you want to clear the entire week's meal plan?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Clear the meal plan dataframe
                self.meal_plan_df = pd.DataFrame(columns=['day', 'meal_type', 'recipe_id', 'recipe_name', 'servings', 'prep_time', 'cook_time'])

                # Save to CSV
                self.meal_plan_df.to_csv('data/meal_plan.csv', index=False)

                # Update data dictionary
                self.data['meal_plan'] = self.meal_plan_df

                # Refresh display
                self.setup_meal_plan_tab()

                QMessageBox.information(self, "Success", "Week's meal plan cleared successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear meal plan: {str(e)}")

    def auto_generate_meal_plan(self):
        """Auto-generate a meal plan based on available recipes"""
        if len(self.recipes_df) == 0:
            QMessageBox.warning(self, "No Recipes", "No recipes available to generate meal plan.")
            return

        reply = QMessageBox.question(
            self,
            "Auto Generate Meal Plan",
            "This will replace your current meal plan with an automatically generated one.\nDo you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                import random

                # Clear existing meal plan
                new_meal_plan = []

                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                meal_types = ['Breakfast', 'Lunch', 'Dinner']

                # Get recipes by category if available
                breakfast_recipes = self.recipes_df[
                    self.recipes_df['category'].str.contains('Breakfast|breakfast', case=False, na=False)
                ] if 'category' in self.recipes_df.columns else pd.DataFrame()

                lunch_dinner_recipes = self.recipes_df[
                    ~self.recipes_df['category'].str.contains('Breakfast|breakfast', case=False, na=False)
                ] if 'category' in self.recipes_df.columns and not breakfast_recipes.empty else self.recipes_df

                # If no categorized recipes, use all recipes
                if breakfast_recipes.empty:
                    breakfast_recipes = self.recipes_df
                if lunch_dinner_recipes.empty:
                    lunch_dinner_recipes = self.recipes_df

                for day in days:
                    for meal_type in meal_types:
                        # Choose appropriate recipe pool
                        if meal_type == 'Breakfast' and not breakfast_recipes.empty:
                            recipe_pool = breakfast_recipes
                        else:
                            recipe_pool = lunch_dinner_recipes

                        # Randomly select a recipe
                        if not recipe_pool.empty:
                            recipe = recipe_pool.sample(1).iloc[0]

                            new_meal_plan.append({
                                'day': day,
                                'meal_type': meal_type,
                                'recipe_id': recipe['recipe_id'],
                                'recipe_name': recipe['recipe_name'],
                                'servings': random.randint(1, 4),
                                'prep_time': recipe['prep_time'],
                                'cook_time': recipe['cook_time']
                            })

                # Update meal plan dataframe
                self.meal_plan_df = pd.DataFrame(new_meal_plan)

                # Save to CSV
                self.meal_plan_df.to_csv('data/meal_plan.csv', index=False)

                # Update data dictionary
                self.data['meal_plan'] = self.meal_plan_df

                # Refresh display
                self.setup_meal_plan_tab()

                QMessageBox.information(self, "Success", f"Auto-generated meal plan with {len(new_meal_plan)} meals!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate meal plan: {str(e)}")

    def setup_recipe_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.recipe_tab)
    
        # Split view - recipe list on left, details on right
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Recipe list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Recipes:")
        self.recipe_search = QLineEdit()
        self.recipe_search.setPlaceholderText("Enter recipe name or ingredient...")
        self.recipe_search.textChanged.connect(self.filter_recipes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.recipe_search)
        left_layout.addLayout(search_layout)
        
        # Recipe list table with enhanced functionality
        self.recipe_table = QTableWidget()
        self.recipe_table.setColumnCount(3)
        self.recipe_table.setHorizontalHeaderLabels(["Recipe Name", "Prep Time", "Cook Time"])

        # FIXED: Enable manual column resizing for Recipe Database table
        print("🔧 Setting up Recipe Database table column resizing...")
        recipe_header = self.recipe_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        recipe_columns = ["Recipe Name", "Prep Time", "Cook Time"]
        for col in range(3):
            recipe_header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Recipe Column {col} ({recipe_columns[col]}): Interactive")

        # Set default column widths
        recipe_default_widths = {
            0: 250,  # Recipe Name (wider for longer names)
            1: 100,  # Prep Time
            2: 100   # Cook Time
        }
        for col, width in recipe_default_widths.items():
            self.recipe_table.setColumnWidth(col, width)
            print(f"   Recipe Column {col}: {width}px")

        # Basic header configuration
        recipe_header.setStretchLastSection(False)
        recipe_header.setMinimumSectionSize(80)
        print("✅ Recipe Database table column resizing enabled!")

        self.recipe_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recipe_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recipe_table.itemSelectionChanged.connect(self.show_recipe_details)

        # Enable context menu for right-click actions
        self.recipe_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recipe_table.customContextMenuRequested.connect(self.show_recipe_context_menu)

        # Enable double-click to edit
        self.recipe_table.itemDoubleClicked.connect(self.show_edit_recipe_dialog)

        left_layout.addWidget(self.recipe_table)

        # Recipe management buttons
        recipe_buttons_layout = QHBoxLayout()

        self.add_recipe_btn = QPushButton("Add Recipe")
        self.add_recipe_btn.clicked.connect(self.show_add_recipe_dialog)
        recipe_buttons_layout.addWidget(self.add_recipe_btn)

        self.edit_recipe_btn = QPushButton("Edit Recipe")
        self.edit_recipe_btn.clicked.connect(self.show_edit_recipe_dialog)
        self.edit_recipe_btn.setEnabled(False)  # Disabled until a recipe is selected
        recipe_buttons_layout.addWidget(self.edit_recipe_btn)

        self.delete_recipe_btn = QPushButton("Delete Recipe")
        self.delete_recipe_btn.clicked.connect(self.delete_recipe)
        self.delete_recipe_btn.setEnabled(False)  # Disabled until a recipe is selected
        recipe_buttons_layout.addWidget(self.delete_recipe_btn)

        left_layout.addLayout(recipe_buttons_layout)
        
        # Populate recipe table
        print(f"🔄 Initial recipe table setup...")
        print(f"   Recipes DF shape: {self.recipes_df.shape}")
        self.populate_recipe_table()
        print(f"   Recipe table populated with {self.recipe_table.rowCount()} rows")
        
        # Right side - Recipe details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Recipe details widgets
        self.recipe_name_label = QLabel("Select a recipe to view details")
        self.recipe_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(self.recipe_name_label)
        
        # Recipe time details
        self.recipe_time_label = QLabel("")
        right_layout.addWidget(self.recipe_time_label)
        
        # Recipe ingredients table
        ingredients_group = QGroupBox("Ingredients (Per Serving)")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(["Item", "Quantity", "Unit", "In Stock"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ingredients_layout.addWidget(self.ingredients_table)
        
        right_layout.addWidget(ingredients_group)
        
        # Recipe instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        self.recipe_instructions = QTextEdit()
        self.recipe_instructions.setReadOnly(True)
        instructions_layout.addWidget(self.recipe_instructions)
        
        right_layout.addWidget(instructions_group)
        
        # Recipe action buttons
        recipe_actions_layout = QHBoxLayout()

        self.add_recipe_button = QPushButton("➕ Add New Recipe")
        self.add_recipe_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.add_recipe_button.clicked.connect(self.show_add_recipe_dialog)
        recipe_actions_layout.addWidget(self.add_recipe_button)

        # Edit recipe button (initially disabled)
        self.edit_recipe_detail_btn = QPushButton("✏️ Edit This Recipe")
        self.edit_recipe_detail_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.edit_recipe_detail_btn.clicked.connect(self.show_edit_recipe_dialog)
        self.edit_recipe_detail_btn.setEnabled(False)  # Disabled until a recipe is selected
        recipe_actions_layout.addWidget(self.edit_recipe_detail_btn)

        right_layout.addLayout(recipe_actions_layout)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 400])  # Set initial sizes
    
    def populate_recipe_table(self, filter_text=None):
        print(f"🔄 Populating recipe table...")
        print(f"   Recipes DF shape: {self.recipes_df.shape}")

        # Clear the table
        self.recipe_table.setRowCount(0)

        # Filter recipes if filter_text is provided
        recipes_to_show = self.recipes_df
        if filter_text:
            filter_text = filter_text.lower()
            recipes_to_show = self.recipes_df[
                self.recipes_df['recipe_name'].str.lower().str.contains(filter_text) |
                self.recipes_df['ingredients'].str.lower().str.contains(filter_text)
            ]
            print(f"   Filtered to {len(recipes_to_show)} recipes")
        else:
            print(f"   Showing all {len(recipes_to_show)} recipes")

        # Populate the table
        self.recipe_table.setRowCount(len(recipes_to_show))
        print(f"   Setting table rows to: {len(recipes_to_show)}")

        for i, (_, recipe) in enumerate(recipes_to_show.iterrows()):
            recipe_name = recipe['recipe_name']
            prep_time = f"{recipe['prep_time']} min"
            cook_time = f"{recipe['cook_time']} min"

            self.recipe_table.setItem(i, 0, QTableWidgetItem(recipe_name))
            self.recipe_table.setItem(i, 1, QTableWidgetItem(prep_time))
            self.recipe_table.setItem(i, 2, QTableWidgetItem(cook_time))

            if i < 5:  # Only print first 5 for brevity
                print(f"   Row {i}: {recipe_name} - {prep_time} - {cook_time}")

        print(f"✅ Recipe table populated with {len(recipes_to_show)} rows")
    
    def filter_recipes(self):
        self.populate_recipe_table(self.recipe_search.text())
    
    def show_recipe_details(self):
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            # Disable edit and delete buttons when no recipe is selected
            self.edit_recipe_btn.setEnabled(False)
            self.delete_recipe_btn.setEnabled(False)
            if hasattr(self, 'edit_recipe_detail_btn'):
                self.edit_recipe_detail_btn.setEnabled(False)
            return

        # Enable edit and delete buttons when a recipe is selected
        self.edit_recipe_btn.setEnabled(True)
        self.delete_recipe_btn.setEnabled(True)
        if hasattr(self, 'edit_recipe_detail_btn'):
            self.edit_recipe_detail_btn.setEnabled(True)
        
        # Get the recipe name from the first column
        recipe_name = self.recipe_table.item(selected_items[0].row(), 0).text()
        
        # Find the recipe in the dataframe
        recipe = self.recipes_df[self.recipes_df['recipe_name'] == recipe_name].iloc[0]
        
        # Update the recipe name label
        self.recipe_name_label.setText(recipe_name)
        
        # Update time details
        self.recipe_time_label.setText(f"Prep: {recipe['prep_time']} min | Cook: {recipe['cook_time']} min")
        
        # Clear and prepare the ingredients table
        self.ingredients_table.setRowCount(0)
        
        # Check if we have recipe_ingredients data in a structured format
        if 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
            # Parse the recipe_ingredients JSON string
            try:
                import json
                ingredients_list = json.loads(recipe['recipe_ingredients'])
                
                # Set the table row count
                self.ingredients_table.setRowCount(len(ingredients_list))
                
                # Populate the ingredients table
                for i, ingredient in enumerate(ingredients_list):
                    # Item name
                    self.ingredients_table.setItem(i, 0, QTableWidgetItem(ingredient['item_name']))
                    
                    # Quantity
                    self.ingredients_table.setItem(i, 1, QTableWidgetItem(str(ingredient['quantity'])))
                    
                    # Unit
                    self.ingredients_table.setItem(i, 2, QTableWidgetItem(ingredient['unit']))
                    
                    # Check if item is in inventory
                    in_stock = "No"
                    in_stock_color = QColor(255, 200, 200)  # Light red for not in stock
                    
                    # Get the inventory dataframe
                    inventory_df = self.data['inventory']
                    
                    # Check if item exists in inventory
                    if 'item_name' in inventory_df.columns:
                        inventory_item = inventory_df[inventory_df['item_name'] == ingredient['item_name']]
                        if not inventory_item.empty:
                            # Item exists, check quantity
                            if 'quantity' in inventory_item.columns:
                                inv_qty = float(inventory_item['quantity'].values[0])
                                if inv_qty > 0:
                                    in_stock = "Yes"
                                    in_stock_color = QColor(200, 255, 200)  # Light green for in stock
                    
                    # Set the in stock status with color
                    in_stock_item = QTableWidgetItem(in_stock)
                    in_stock_item.setBackground(in_stock_color)
                    self.ingredients_table.setItem(i, 3, in_stock_item)
            
            except Exception as e:
                print(f"Error parsing recipe ingredients: {e}")
                # Fall back to the old format
                self._display_legacy_ingredients(recipe)
        else:
            # Use the old format for ingredients
            self._display_legacy_ingredients(recipe)
        
        # Set the recipe instructions
        if 'instructions' in recipe and pd.notna(recipe['instructions']):
            self.recipe_instructions.setHtml(recipe['instructions'].replace('.', '.<br><br>'))
        else:
            self.recipe_instructions.setPlainText("No instructions available.")
    
    def _display_legacy_ingredients(self, recipe):
        """Display ingredients from the old format as a fallback."""
        if 'ingredients' in recipe and pd.notna(recipe['ingredients']):
            ingredients = recipe['ingredients'].split(',')
            self.ingredients_table.setRowCount(len(ingredients))
            
            for i, ingredient in enumerate(ingredients):
                # Try to parse simple text ingredients
                ingredient = ingredient.strip()
                self.ingredients_table.setItem(i, 0, QTableWidgetItem(ingredient))
                self.ingredients_table.setItem(i, 1, QTableWidgetItem("1"))  # Default quantity
                self.ingredients_table.setItem(i, 2, QTableWidgetItem("unit"))  # Default unit
                
                # Check inventory (same logic as above)
                in_stock = "Unknown"
                in_stock_color = QColor(255, 255, 200)  # Light yellow for unknown
                in_stock_item = QTableWidgetItem(in_stock)
                in_stock_item.setBackground(in_stock_color)
                self.ingredients_table.setItem(i, 3, in_stock_item)
    
    def show_add_recipe_dialog(self):
        # Create a dialog for adding a new recipe with improved layout
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Recipe")
        dialog.setMinimumWidth(1100)  # Increased width for 2-column layout
        dialog.setMinimumHeight(800)  # Increased height for better ingredients visibility
        dialog.resize(1100, 800)  # Set initial size

        # Main layout
        layout = QVBoxLayout(dialog)

        # Create main content splitter for 2-column layout
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Left column - Recipe details and instructions
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Recipe details form
        form_group = QGroupBox("Recipe Details")
        form_layout = QFormLayout(form_group)
        
        # Recipe name
        recipe_name_input = QLineEdit()
        form_layout.addRow("Recipe Name:", recipe_name_input)
        
        # Prep time
        prep_time_spin = QSpinBox()
        prep_time_spin.setMinimum(1)
        prep_time_spin.setMaximum(240)  # 4 hours max
        prep_time_spin.setValue(15)  # Default 15 minutes
        form_layout.addRow("Prep Time (minutes):", prep_time_spin)
        
        # Cook time
        cook_time_spin = QSpinBox()
        cook_time_spin.setMinimum(0)
        cook_time_spin.setMaximum(480)  # 8 hours max
        cook_time_spin.setValue(30)  # Default 30 minutes
        form_layout.addRow("Cook Time (minutes):", cook_time_spin)
        
        # Servings (always 1 as per the requirement)
        servings_spin = QSpinBox()
        servings_spin.setMinimum(1)
        servings_spin.setMaximum(1)  # Fixed at 1 serving
        servings_spin.setValue(1)
        form_layout.addRow("Servings (per recipe):", servings_spin)
        
        # Add the form to the left layout
        left_layout.addWidget(form_group)

        # Instructions section (moved to left column)
        instructions_group = QGroupBox("Cooking Instructions")
        instructions_layout = QVBoxLayout(instructions_group)

        # Text area for instructions
        instructions_text = QTextEdit()
        instructions_text.setMinimumHeight(200)  # Set minimum height
        instructions_layout.addWidget(instructions_text)

        left_layout.addWidget(instructions_group)

        # Add left widget to splitter
        main_splitter.addWidget(left_widget)

        # Right column - Ingredients section with expanded space
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Ingredients section with more space
        ingredients_group = QGroupBox("Ingredients (quantities are per serving)")
        ingredients_layout = QVBoxLayout(ingredients_group)

        # Table for ingredients with improved styling and height
        ingredients_table = QTableWidget()
        ingredients_table.setColumnCount(4)
        ingredients_table.setHorizontalHeaderLabels(["Item", "Quantity", "Unit", "Auto-added to Inventory"])
        ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ingredients_table.setMinimumHeight(350)  # Set minimum height to show multiple rows
        ingredients_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ecf0f1;
                border-radius: 4px;
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 20px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        ingredients_layout.addWidget(ingredients_table)
        
        # Add row button for ingredients with better styling
        add_ingredient_btn = QPushButton("➕ Add Ingredient")
        add_ingredient_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        ingredients_layout.addWidget(add_ingredient_btn)

        # Add the ingredients section to the right layout
        right_layout.addWidget(ingredients_group)

        # Add right widget to splitter
        main_splitter.addWidget(right_widget)

        # Set splitter proportions (45% left, 55% right for ingredients)
        main_splitter.setSizes([495, 605])  # Based on 1100px total width
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save Recipe")
        cancel_btn = QPushButton("Cancel")
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)
        
        # Connect signals
        cancel_btn.clicked.connect(dialog.reject)
        
        # Initial ingredient row
        def add_ingredient_row():
            row = ingredients_table.rowCount()
            ingredients_table.insertRow(row)
            
            # Item combo box with inventory items
            item_combo = QComboBox()
            item_combo.setEditable(True)  # Allow custom entries
            
            # Get inventory items
            inventory_df = self.data['inventory']
            if 'item_name' in inventory_df.columns:
                items = sorted(set(inventory_df['item_name'].dropna().unique()))
                item_combo.addItems(items)
            
            # Quantity spin box
            qty_spin = QDoubleSpinBox()
            qty_spin.setMinimum(0.01)
            qty_spin.setMaximum(1000)
            qty_spin.setValue(1)
            qty_spin.setDecimals(2)
            
            # Unit combo box
            unit_combo = QComboBox()
            unit_combo.addItems(["g", "kg", "ml", "L", "units", "pcs", "tbsp", "tsp"])
            
            # Auto-add checkbox
            auto_add_check = QCheckBox()
            auto_add_check.setChecked(True)  # Default to auto-add
            
            # Add widgets to the table
            ingredients_table.setCellWidget(row, 0, item_combo)
            ingredients_table.setCellWidget(row, 1, qty_spin)
            ingredients_table.setCellWidget(row, 2, unit_combo)
            ingredients_table.setCellWidget(row, 3, auto_add_check)
        
        # Add initial row and connect button
        add_ingredient_row()
        add_ingredient_btn.clicked.connect(add_ingredient_row)
        
        # Save recipe function
        def save_recipe():
            # Validate inputs
            if not recipe_name_input.text().strip():
                QMessageBox.warning(dialog, "Input Error", "Recipe name is required.")
                return
            
            # Create recipe record
            recipe_name = recipe_name_input.text().strip()
            prep_time = prep_time_spin.value()
            cook_time = cook_time_spin.value()
            instructions = instructions_text.toPlainText().strip()
            
            # Get ingredients
            ingredients_list = []
            for i in range(ingredients_table.rowCount()):
                item_combo = ingredients_table.cellWidget(i, 0)
                qty_spin = ingredients_table.cellWidget(i, 1)
                unit_combo = ingredients_table.cellWidget(i, 2)
                auto_add_check = ingredients_table.cellWidget(i, 3)
                
                if item_combo and qty_spin and unit_combo and auto_add_check:
                    item_name = item_combo.currentText().strip()
                    quantity = qty_spin.value()
                    unit = unit_combo.currentText()
                    auto_add = auto_add_check.isChecked()
                    
                    if item_name and quantity > 0:
                        ingredients_list.append({
                            'item_name': item_name,
                            'quantity': quantity,
                            'unit': unit,
                            'auto_add': auto_add
                        })
                        
                        # Auto-add to inventory if it doesn't exist and auto_add is checked
                        if auto_add:
                            self.add_ingredient_to_inventory(item_name, unit)
            
            # Generate a recipe ID
            recipe_id = 1
            if len(self.recipes_df) > 0:
                recipe_id = self.recipes_df['recipe_id'].max() + 1
            
            # Prepare ingredients string for backward compatibility
            ingredients_text = ", ".join([f"{item['quantity']} {item['unit']} {item['item_name']}" for item in ingredients_list])
            
            # Create recipe dataframe row
            import json
            from datetime import datetime
            
            new_recipe = pd.DataFrame({
                'recipe_id': [recipe_id],
                'recipe_name': [recipe_name],
                'prep_time': [prep_time],
                'cook_time': [cook_time],
                'servings': [1],  # Always 1 as per requirement
                'ingredients': [ingredients_text],  # For backward compatibility
                'recipe_ingredients': [json.dumps(ingredients_list)],  # Structured format
                'instructions': [instructions],
                'calories_per_serving': [0],  # Default value
                'date_added': [datetime.now().strftime('%Y-%m-%d')]
            })
            
            # Add to recipes dataframe
            self.recipes_df = pd.concat([self.recipes_df, new_recipe], ignore_index=True)
            
            # Save to CSV
            self.recipes_df.to_csv('data/recipes.csv', index=False)
            
            # Update data dictionary
            self.data['recipes'] = self.recipes_df
            
            # Refresh recipe table
            self.populate_recipe_table()
            
            # Show success message
            QMessageBox.information(dialog, "Success", f"Recipe '{recipe_name}' added successfully!")
            
            # Close dialog
            dialog.accept()
        
        # Connect save button
        save_btn.clicked.connect(save_recipe)
        
        # Show the dialog
        dialog.exec_()

    def show_edit_recipe_dialog(self):
        """Show enhanced dialog to edit the selected recipe with improved validation and features"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a recipe to edit.")
            return

        # Get the selected recipe
        recipe_name = self.recipe_table.item(selected_items[0].row(), 0).text()
        recipe = self.recipes_df[self.recipes_df['recipe_name'] == recipe_name].iloc[0]

        # Create enhanced edit dialog with larger size for better visibility
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Recipe: {recipe_name}")
        dialog.setMinimumWidth(1400)  # Further increased width for better 2-column layout
        dialog.setMinimumHeight(1000)  # Increased height for better ingredients visibility
        dialog.resize(1400, 1000)  # Set initial size for optimal viewing
        dialog.setModal(True)

        # Main layout
        layout = QVBoxLayout(dialog)

        # Add header with recipe info
        header_layout = QHBoxLayout()
        header_label = QLabel(f"Editing Recipe: {recipe_name}")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Add last modified info if available
        if 'date_added' in recipe and pd.notna(recipe['date_added']):
            last_modified = QLabel(f"Created: {recipe['date_added']}")
            last_modified.setStyleSheet("color: #7f8c8d; font-size: 10px;")
            header_layout.addWidget(last_modified)

        layout.addLayout(header_layout)

        # Create main content splitter for 2-column layout with enhanced styling
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 3px;
                margin: 2px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
        main_splitter.setHandleWidth(5)  # Make splitter handle more visible
        layout.addWidget(main_splitter)

        # Left column - Recipe details and instructions
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Recipe details form with enhanced styling
        form_group = QGroupBox("Recipe Details")
        form_group.setStyleSheet("""
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
        form_layout = QFormLayout(form_group)

        # Recipe name (pre-filled) with validation styling
        recipe_name_input = QLineEdit()
        recipe_name_input.setText(recipe['recipe_name'])
        recipe_name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Recipe Name*:", recipe_name_input)

        # Category selection (new feature)
        category_combo = QComboBox()
        category_combo.setEditable(True)
        categories = ["Main Course", "Appetizer", "Dessert", "Beverage", "Snack", "Side Dish", "Breakfast", "Lunch", "Dinner"]
        category_combo.addItems(categories)
        if 'category' in recipe and pd.notna(recipe['category']):
            category_combo.setCurrentText(recipe['category'])
        else:
            category_combo.setCurrentText("Main Course")
        category_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Category:", category_combo)

        # Prep time (pre-filled) with better styling
        prep_time_spin = QSpinBox()
        prep_time_spin.setMinimum(1)
        prep_time_spin.setMaximum(240)
        prep_time_spin.setValue(int(recipe['prep_time']))
        prep_time_spin.setSuffix(" minutes")
        prep_time_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Prep Time*:", prep_time_spin)

        # Cook time (pre-filled) with better styling
        cook_time_spin = QSpinBox()
        cook_time_spin.setMinimum(0)
        cook_time_spin.setMaximum(480)
        cook_time_spin.setValue(int(recipe['cook_time']))
        cook_time_spin.setSuffix(" minutes")
        cook_time_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Cook Time*:", cook_time_spin)

        # Servings (enhanced)
        servings_spin = QSpinBox()
        servings_spin.setMinimum(1)
        servings_spin.setMaximum(20)
        if 'servings' in recipe and pd.notna(recipe['servings']):
            servings_spin.setValue(int(recipe['servings']))
        else:
            servings_spin.setValue(1)
        servings_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
            }
        """)
        form_layout.addRow("Servings:", servings_spin)

        left_layout.addWidget(form_group)

        # Instructions (pre-filled) with enhanced styling
        instructions_group = QGroupBox("Cooking Instructions")
        instructions_group.setStyleSheet("""
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
        instructions_layout = QVBoxLayout(instructions_group)

        instructions_text = QTextEdit()
        instructions_text.setPlainText(recipe.get('instructions', ''))
        instructions_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ecf0f1;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        instructions_text.setPlaceholderText("Enter detailed cooking instructions here...")
        instructions_layout.addWidget(instructions_text)

        left_layout.addWidget(instructions_group)

        # Add left widget to splitter
        main_splitter.addWidget(left_widget)

        # Right column - Ingredients section with expanded space
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Enhanced Ingredients section with better management and more space
        ingredients_group = QGroupBox("Recipe Ingredients")
        ingredients_group.setStyleSheet("""
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
        ingredients_layout = QVBoxLayout(ingredients_group)

        # Get existing ingredients for this recipe with enhanced parsing
        recipe_ingredients_df = self.data.get('recipe_ingredients', pd.DataFrame())
        existing_ingredients = []

        # Try to get ingredients from structured format first
        if 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
            try:
                import json
                structured_ingredients = json.loads(recipe['recipe_ingredients'])
                for ingredient in structured_ingredients:
                    existing_ingredients.append({
                        'item_name': ingredient.get('item_name', ''),
                        'quantity': ingredient.get('quantity', 1.0),
                        'unit': ingredient.get('unit', 'units'),
                        'notes': ingredient.get('notes', '')
                    })
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback to recipe_ingredients table if structured format not available
        if not existing_ingredients and not recipe_ingredients_df.empty:
            recipe_ingredients = recipe_ingredients_df[
                recipe_ingredients_df['recipe_id'] == recipe['recipe_id']
            ]
            for _, ingredient in recipe_ingredients.iterrows():
                existing_ingredients.append({
                    'item_name': ingredient['item_name'],
                    'quantity': ingredient['quantity'],
                    'unit': ingredient['unit'],
                    'notes': ingredient.get('notes', '')
                })

        # Enhanced ingredients table with better styling and expanded height
        ingredients_table = QTableWidget()
        ingredients_table.setColumnCount(5)
        ingredients_table.setHorizontalHeaderLabels(["Ingredient*", "Quantity*", "Unit", "Notes", "In Stock"])

        # Set column resize modes for better visibility
        header = ingredients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Ingredient name - flexible
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Quantity - fit content
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit - fit content
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Notes - flexible
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # In Stock - fit content
        ingredients_table.setMinimumHeight(500)  # Increased height to show more rows clearly
        ingredients_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 13px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 30px;
                border-right: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
                border-right: 1px solid #34495e;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)

        # Populate with existing ingredients and check inventory status
        ingredients_table.setRowCount(len(existing_ingredients))
        inventory_df = self.data.get('inventory', pd.DataFrame())

        for i, ingredient in enumerate(existing_ingredients):
            # Ingredient name
            ingredients_table.setItem(i, 0, QTableWidgetItem(ingredient['item_name']))

            # Quantity
            ingredients_table.setItem(i, 1, QTableWidgetItem(str(ingredient['quantity'])))

            # Unit
            ingredients_table.setItem(i, 2, QTableWidgetItem(ingredient['unit']))

            # Notes
            ingredients_table.setItem(i, 3, QTableWidgetItem(ingredient['notes']))

            # Check inventory status
            in_stock_status = "Unknown"
            if not inventory_df.empty and 'item_name' in inventory_df.columns:
                matching_items = inventory_df[inventory_df['item_name'].str.lower() == ingredient['item_name'].lower()]
                if not matching_items.empty:
                    stock_qty = matching_items.iloc[0].get('quantity', 0)
                    if stock_qty > 0:
                        in_stock_status = f"Yes ({stock_qty})"
                    else:
                        in_stock_status = "Out of Stock"
                else:
                    in_stock_status = "Not in Inventory"

            stock_item = QTableWidgetItem(in_stock_status)
            if "Yes" in in_stock_status:
                stock_item.setBackground(QColor(200, 255, 200))  # Light green
            elif "Out of Stock" in in_stock_status:
                stock_item.setBackground(QColor(255, 200, 200))  # Light red
            else:
                stock_item.setBackground(QColor(255, 255, 200))  # Light yellow
            ingredients_table.setItem(i, 4, stock_item)

        ingredients_layout.addWidget(ingredients_table)

        # Enhanced ingredient management buttons with better styling
        ingredient_buttons = QHBoxLayout()

        add_ingredient_btn = QPushButton("➕ Add Ingredient")
        add_ingredient_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)

        edit_ingredient_btn = QPushButton("✏️ Edit Selected")
        edit_ingredient_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)

        remove_ingredient_btn = QPushButton("🗑️ Remove Selected")
        remove_ingredient_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)

        # Add validation button
        validate_ingredients_btn = QPushButton("🔍 Validate Ingredients")
        validate_ingredients_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f7dc6f;
                color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)

        ingredient_buttons.addWidget(add_ingredient_btn)
        ingredient_buttons.addWidget(edit_ingredient_btn)
        ingredient_buttons.addWidget(remove_ingredient_btn)
        ingredient_buttons.addWidget(validate_ingredients_btn)
        ingredient_buttons.addStretch()

        ingredients_layout.addLayout(ingredient_buttons)
        right_layout.addWidget(ingredients_group)

        # Add right widget to splitter
        main_splitter.addWidget(right_widget)

        # Set splitter proportions (35% left, 65% right for ingredients)
        main_splitter.setSizes([490, 910])  # Based on 1400px total width - more space for ingredients

        # Enhanced dialog buttons with better styling and confirmation
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)

        # Save button
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)

        # Preview button (new feature)
        preview_btn = QPushButton("👁️ Preview Recipe")
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a569bd;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)

        button_layout.addWidget(preview_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        # Connect cancel button with confirmation if changes were made
        def confirm_cancel():
            reply = QMessageBox.question(
                dialog,
                "Confirm Cancel",
                "Are you sure you want to cancel? Any unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                dialog.reject()

        cancel_btn.clicked.connect(confirm_cancel)

        # Enhanced ingredient management functions with better UX
        def add_ingredient():
            row = ingredients_table.rowCount()
            ingredients_table.insertRow(row)

            # Create combo box for ingredient selection
            ingredient_combo = QComboBox()
            ingredient_combo.setEditable(True)

            # Populate with inventory items
            if not inventory_df.empty and 'item_name' in inventory_df.columns:
                items = sorted(set(inventory_df['item_name'].dropna().unique()))
                ingredient_combo.addItems(items)

            # Set default values
            ingredients_table.setItem(row, 0, QTableWidgetItem(""))
            ingredients_table.setItem(row, 1, QTableWidgetItem("1.0"))
            ingredients_table.setItem(row, 2, QTableWidgetItem("units"))
            ingredients_table.setItem(row, 3, QTableWidgetItem(""))
            ingredients_table.setItem(row, 4, QTableWidgetItem("Unknown"))

            # Focus on the new row for immediate editing
            ingredients_table.setCurrentCell(row, 0)
            ingredients_table.editItem(ingredients_table.item(row, 0))

        def edit_ingredient():
            current_row = ingredients_table.currentRow()
            if current_row >= 0:
                ingredients_table.editItem(ingredients_table.item(current_row, 0))
            else:
                QMessageBox.information(dialog, "No Selection", "Please select an ingredient row to edit.")

        def remove_ingredient():
            current_row = ingredients_table.currentRow()
            if current_row >= 0:
                ingredient_name = ingredients_table.item(current_row, 0).text()
                reply = QMessageBox.question(
                    dialog,
                    "Confirm Removal",
                    f"Are you sure you want to remove '{ingredient_name}' from this recipe?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    ingredients_table.removeRow(current_row)
            else:
                QMessageBox.information(dialog, "No Selection", "Please select an ingredient row to remove.")

        def validate_ingredients():
            """Validate all ingredients against inventory and show status"""
            missing_ingredients = []
            available_ingredients = []

            for row in range(ingredients_table.rowCount()):
                ingredient_name = ingredients_table.item(row, 0).text().strip()
                if ingredient_name:
                    # Check inventory status
                    if not inventory_df.empty and 'item_name' in inventory_df.columns:
                        matching_items = inventory_df[inventory_df['item_name'].str.lower() == ingredient_name.lower()]
                        if matching_items.empty:
                            missing_ingredients.append(ingredient_name)
                        else:
                            stock_qty = matching_items.iloc[0].get('quantity', 0)
                            if stock_qty > 0:
                                available_ingredients.append(f"{ingredient_name} ({stock_qty} available)")
                            else:
                                missing_ingredients.append(f"{ingredient_name} (out of stock)")

            # Show validation results
            message = "Ingredient Validation Results:\n\n"
            if available_ingredients:
                message += "✅ Available Ingredients:\n" + "\n".join(available_ingredients) + "\n\n"
            if missing_ingredients:
                message += "❌ Missing/Out of Stock:\n" + "\n".join(missing_ingredients)

            QMessageBox.information(dialog, "Ingredient Validation", message)

        def preview_recipe():
            """Show a preview of how the recipe will look"""
            preview_text = f"Recipe: {recipe_name_input.text()}\n"
            preview_text += f"Category: {category_combo.currentText()}\n"
            preview_text += f"Prep Time: {prep_time_spin.value()} minutes\n"
            preview_text += f"Cook Time: {cook_time_spin.value()} minutes\n"
            preview_text += f"Servings: {servings_spin.value()}\n\n"

            preview_text += "Ingredients:\n"
            for row in range(ingredients_table.rowCount()):
                ingredient = ingredients_table.item(row, 0).text()
                quantity = ingredients_table.item(row, 1).text()
                unit = ingredients_table.item(row, 2).text()
                if ingredient.strip():
                    preview_text += f"• {quantity} {unit} {ingredient}\n"

            preview_text += f"\nInstructions:\n{instructions_text.toPlainText()}"

            preview_dialog = QDialog(dialog)
            preview_dialog.setWindowTitle("Recipe Preview")
            preview_dialog.setMinimumWidth(500)
            preview_dialog.setMinimumHeight(400)

            preview_layout = QVBoxLayout(preview_dialog)
            preview_display = QTextEdit()
            preview_display.setPlainText(preview_text)
            preview_display.setReadOnly(True)
            preview_layout.addWidget(preview_display)

            close_btn = QPushButton("Close Preview")
            close_btn.clicked.connect(preview_dialog.accept)
            preview_layout.addWidget(close_btn)

            preview_dialog.exec_()

        # Connect ingredient buttons
        add_ingredient_btn.clicked.connect(add_ingredient)
        edit_ingredient_btn.clicked.connect(edit_ingredient)
        remove_ingredient_btn.clicked.connect(remove_ingredient)
        validate_ingredients_btn.clicked.connect(validate_ingredients)
        preview_btn.clicked.connect(preview_recipe)

        # Enhanced save recipe function with comprehensive validation
        def save_recipe_changes():
            # Comprehensive input validation
            validation_errors = []

            if not recipe_name_input.text().strip():
                validation_errors.append("• Recipe name is required")

            if prep_time_spin.value() <= 0:
                validation_errors.append("• Prep time must be greater than 0")

            if cook_time_spin.value() < 0:
                validation_errors.append("• Cook time cannot be negative")

            # Validate ingredients
            ingredient_count = 0
            for row in range(ingredients_table.rowCount()):
                ingredient_name = ingredients_table.item(row, 0).text().strip()
                if ingredient_name:
                    ingredient_count += 1
                    try:
                        quantity = float(ingredients_table.item(row, 1).text())
                        if quantity <= 0:
                            validation_errors.append(f"• Quantity for '{ingredient_name}' must be greater than 0")
                    except ValueError:
                        validation_errors.append(f"• Invalid quantity for '{ingredient_name}'")

            if ingredient_count == 0:
                validation_errors.append("• At least one ingredient is required")

            if not instructions_text.toPlainText().strip():
                validation_errors.append("• Cooking instructions are required")

            # Show validation errors if any
            if validation_errors:
                error_message = "Please fix the following errors:\n\n" + "\n".join(validation_errors)
                QMessageBox.warning(dialog, "Validation Errors", error_message)
                return

            # Check for duplicate recipe name (excluding current recipe)
            new_recipe_name = recipe_name_input.text().strip()
            existing_recipes = self.recipes_df[
                (self.recipes_df['recipe_name'].str.lower() == new_recipe_name.lower()) &
                (self.recipes_df['recipe_id'] != recipe['recipe_id'])
            ]
            if not existing_recipes.empty:
                reply = QMessageBox.question(
                    dialog,
                    "Duplicate Recipe Name",
                    f"A recipe named '{new_recipe_name}' already exists. Do you want to continue anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            try:
                # Show progress indicator
                progress_msg = QMessageBox(dialog)
                progress_msg.setWindowTitle("Saving Recipe")
                progress_msg.setText("Saving recipe changes...")
                progress_msg.setStandardButtons(QMessageBox.NoButton)
                progress_msg.show()
                QApplication.processEvents()

                # Update recipe in dataframe
                recipe_id = recipe['recipe_id']
                new_category = category_combo.currentText()
                new_prep_time = prep_time_spin.value()
                new_cook_time = cook_time_spin.value()
                new_servings = servings_spin.value()
                new_instructions = instructions_text.toPlainText().strip()

                # Update recipe data with all fields
                self.recipes_df.loc[
                    self.recipes_df['recipe_id'] == recipe_id,
                    ['recipe_name', 'category', 'prep_time', 'cook_time', 'servings', 'instructions']
                ] = [new_recipe_name, new_category, new_prep_time, new_cook_time, new_servings, new_instructions]

                # Update ingredients with enhanced structure
                recipe_ingredients_df = self.data.get('recipe_ingredients', pd.DataFrame())
                ingredients_list = []

                # Remove existing ingredients for this recipe
                if not recipe_ingredients_df.empty:
                    recipe_ingredients_df = recipe_ingredients_df[
                        recipe_ingredients_df['recipe_id'] != recipe_id
                    ]

                # Process updated ingredients
                for row in range(ingredients_table.rowCount()):
                    item_name = ingredients_table.item(row, 0).text().strip()
                    if item_name:  # Only add non-empty ingredients
                        try:
                            quantity = float(ingredients_table.item(row, 1).text())
                        except ValueError:
                            quantity = 1.0

                        unit = ingredients_table.item(row, 2).text().strip() or "units"
                        notes = ingredients_table.item(row, 3).text().strip()

                        # Add to structured ingredients list
                        ingredients_list.append({
                            'item_name': item_name,
                            'quantity': quantity,
                            'unit': unit,
                            'notes': notes
                        })

                        # Add to recipe_ingredients table for backward compatibility
                        new_ingredient = pd.DataFrame([{
                            'recipe_id': recipe_id,
                            'ingredient_id': len(recipe_ingredients_df) + row + 1,
                            'item_name': item_name,
                            'quantity': quantity,
                            'unit': unit,
                            'notes': notes
                        }])

                        recipe_ingredients_df = pd.concat([recipe_ingredients_df, new_ingredient], ignore_index=True)

                # Update structured ingredients in recipe
                import json
                structured_ingredients = json.dumps(ingredients_list)
                self.recipes_df.loc[
                    self.recipes_df['recipe_id'] == recipe_id,
                    'recipe_ingredients'
                ] = structured_ingredients

                # Update legacy ingredients format for backward compatibility
                legacy_ingredients = ", ".join([f"{item['quantity']} {item['unit']} {item['item_name']}" for item in ingredients_list])
                self.recipes_df.loc[
                    self.recipes_df['recipe_id'] == recipe_id,
                    'ingredients'
                ] = legacy_ingredients

                # Update last modified date
                from datetime import datetime
                self.recipes_df.loc[
                    self.recipes_df['recipe_id'] == recipe_id,
                    'date_modified'
                ] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Save to CSV files with error handling
                try:
                    self.recipes_df.to_csv('data/recipes.csv', index=False)
                    recipe_ingredients_df.to_csv('data/recipe_ingredients.csv', index=False)
                except Exception as save_error:
                    progress_msg.hide()
                    QMessageBox.critical(dialog, "Save Error", f"Failed to save files: {str(save_error)}")
                    return

                # Update data dictionary
                self.data['recipes'] = self.recipes_df
                self.data['recipe_ingredients'] = recipe_ingredients_df

                # Hide progress message
                progress_msg.hide()

                # Refresh recipe table and details
                self.populate_recipe_table()

                # Update the recipe details view if this recipe is currently selected
                if hasattr(self, 'recipe_name_label') and self.recipe_name_label.text() == recipe['recipe_name']:
                    self.show_recipe_details()

                # Show success message with details
                success_message = f"Recipe '{new_recipe_name}' updated successfully!\n\n"
                success_message += f"• {len(ingredients_list)} ingredients\n"
                success_message += f"• Prep time: {new_prep_time} minutes\n"
                success_message += f"• Cook time: {new_cook_time} minutes\n"
                success_message += f"• Category: {new_category}"

                QMessageBox.information(dialog, "Recipe Updated", success_message)

                # Close dialog
                dialog.accept()

            except Exception as e:
                # Hide progress message if it's still showing
                if 'progress_msg' in locals():
                    progress_msg.hide()
                QMessageBox.critical(dialog, "Error", f"Failed to update recipe: {str(e)}")

        # Connect save button
        save_btn.clicked.connect(save_recipe_changes)

        # Add keyboard shortcuts for better UX
        from PySide6.QtGui import QKeySequence
        from PySide6.QtWidgets import QShortcut

        # Ctrl+S to save
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), dialog)
        save_shortcut.activated.connect(save_recipe_changes)

        # Escape to cancel
        cancel_shortcut = QShortcut(QKeySequence("Escape"), dialog)
        cancel_shortcut.activated.connect(confirm_cancel)

        # Set focus to recipe name for immediate editing
        recipe_name_input.setFocus()
        recipe_name_input.selectAll()

        # Show the dialog
        dialog.exec_()

    def show_recipe_context_menu(self, position):
        """Show context menu for recipe table with edit, delete, and other options"""
        if self.recipe_table.itemAt(position) is None:
            return

        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction

        context_menu = QMenu(self)

        # Edit recipe action
        edit_action = QAction("✏️ Edit Recipe", self)
        edit_action.triggered.connect(self.show_edit_recipe_dialog)
        context_menu.addAction(edit_action)

        # Duplicate recipe action
        duplicate_action = QAction("📋 Duplicate Recipe", self)
        duplicate_action.triggered.connect(self.duplicate_selected_recipe)
        context_menu.addAction(duplicate_action)

        context_menu.addSeparator()

        # Delete recipe action
        delete_action = QAction("🗑️ Delete Recipe", self)
        delete_action.triggered.connect(self.delete_recipe)
        context_menu.addAction(delete_action)

        context_menu.addSeparator()

        # Export recipe action
        export_action = QAction("📤 Export Recipe", self)
        export_action.triggered.connect(self.export_selected_recipe)
        context_menu.addAction(export_action)

        # Show the context menu
        context_menu.exec_(self.recipe_table.mapToGlobal(position))

    def duplicate_selected_recipe(self):
        """Duplicate the selected recipe with a new name"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a recipe to duplicate.")
            return

        # Get the selected recipe
        recipe_name = self.recipe_table.item(selected_items[0].row(), 0).text()
        recipe = self.recipes_df[self.recipes_df['recipe_name'] == recipe_name].iloc[0]

        # Ask for new recipe name
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self,
            "Duplicate Recipe",
            f"Enter name for duplicated recipe:",
            text=f"{recipe_name} (Copy)"
        )

        if ok and new_name.strip():
            try:
                # Generate new recipe ID
                new_recipe_id = self.recipes_df['recipe_id'].max() + 1 if len(self.recipes_df) > 0 else 1

                # Create duplicate recipe
                new_recipe = recipe.copy()
                new_recipe['recipe_id'] = new_recipe_id
                new_recipe['recipe_name'] = new_name.strip()
                new_recipe['date_added'] = datetime.now().strftime('%Y-%m-%d')

                # Add to dataframe
                self.recipes_df = pd.concat([self.recipes_df, pd.DataFrame([new_recipe])], ignore_index=True)

                # Duplicate ingredients if they exist
                recipe_ingredients_df = self.data.get('recipe_ingredients', pd.DataFrame())
                if not recipe_ingredients_df.empty:
                    original_ingredients = recipe_ingredients_df[
                        recipe_ingredients_df['recipe_id'] == recipe['recipe_id']
                    ]

                    if not original_ingredients.empty:
                        # Create new ingredients with new recipe ID
                        new_ingredients = original_ingredients.copy()
                        new_ingredients['recipe_id'] = new_recipe_id
                        new_ingredients['ingredient_id'] = range(
                            len(recipe_ingredients_df) + 1,
                            len(recipe_ingredients_df) + len(new_ingredients) + 1
                        )

                        # Add to ingredients dataframe
                        recipe_ingredients_df = pd.concat([recipe_ingredients_df, new_ingredients], ignore_index=True)
                        self.data['recipe_ingredients'] = recipe_ingredients_df
                        recipe_ingredients_df.to_csv('data/recipe_ingredients.csv', index=False)

                # Save recipes
                self.recipes_df.to_csv('data/recipes.csv', index=False)
                self.data['recipes'] = self.recipes_df

                # Refresh table
                self.populate_recipe_table()

                QMessageBox.information(self, "Success", f"Recipe '{new_name}' created successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to duplicate recipe: {str(e)}")

    def export_selected_recipe(self):
        """Export the selected recipe to a text file"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a recipe to export.")
            return

        # Get the selected recipe
        recipe_name = self.recipe_table.item(selected_items[0].row(), 0).text()
        recipe = self.recipes_df[self.recipes_df['recipe_name'] == recipe_name].iloc[0]

        # Create export content
        export_content = f"Recipe: {recipe['recipe_name']}\n"
        export_content += f"Category: {recipe.get('category', 'N/A')}\n"
        export_content += f"Prep Time: {recipe['prep_time']} minutes\n"
        export_content += f"Cook Time: {recipe['cook_time']} minutes\n"
        export_content += f"Servings: {recipe.get('servings', 1)}\n\n"

        export_content += "Ingredients:\n"
        if 'recipe_ingredients' in recipe and pd.notna(recipe['recipe_ingredients']):
            try:
                import json
                ingredients = json.loads(recipe['recipe_ingredients'])
                for ingredient in ingredients:
                    export_content += f"• {ingredient['quantity']} {ingredient['unit']} {ingredient['item_name']}\n"
            except:
                export_content += f"• {recipe.get('ingredients', 'No ingredients listed')}\n"
        else:
            export_content += f"• {recipe.get('ingredients', 'No ingredients listed')}\n"

        export_content += f"\nInstructions:\n{recipe.get('instructions', 'No instructions provided')}\n"

        # Save to file
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Recipe",
            f"{recipe_name.replace(' ', '_')}_recipe.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_content)
                QMessageBox.information(self, "Success", f"Recipe exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export recipe: {str(e)}")

    def delete_recipe(self):
        """Delete the selected recipe"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a recipe to delete.")
            return

        # Get the selected recipe
        recipe_name = self.recipe_table.item(selected_items[0].row(), 0).text()
        recipe = self.recipes_df[self.recipes_df['recipe_name'] == recipe_name].iloc[0]
        recipe_id = recipe['recipe_id']

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the recipe '{recipe_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Remove recipe from dataframe
                self.recipes_df = self.recipes_df[self.recipes_df['recipe_id'] != recipe_id]

                # Remove recipe ingredients
                recipe_ingredients_df = self.data.get('recipe_ingredients', pd.DataFrame())
                if not recipe_ingredients_df.empty:
                    recipe_ingredients_df = recipe_ingredients_df[
                        recipe_ingredients_df['recipe_id'] != recipe_id
                    ]
                    self.data['recipe_ingredients'] = recipe_ingredients_df
                    recipe_ingredients_df.to_csv('data/recipe_ingredients.csv', index=False)

                # Save updated recipes
                self.recipes_df.to_csv('data/recipes.csv', index=False)
                self.data['recipes'] = self.recipes_df

                # Refresh recipe table
                self.populate_recipe_table()

                # Clear recipe details
                self.recipe_name_label.setText("Select a recipe to view details")
                self.recipe_time_label.setText("")
                self.ingredients_table.setRowCount(0)
                self.recipe_instructions.clear()

                # Disable edit and delete buttons
                self.edit_recipe_btn.setEnabled(False)
                self.delete_recipe_btn.setEnabled(False)

                QMessageBox.information(self, "Success", f"Recipe '{recipe_name}' deleted successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete recipe: {str(e)}")
    
    def add_ingredient_to_inventory(self, item_name, unit):
        """Add an ingredient to the inventory if it doesn't exist"""
        if 'inventory' in self.data and len(self.data['inventory']) > 0:
            # Check if item exists
            if 'item_name' in self.data['inventory'].columns:
                if any(self.data['inventory']['item_name'] == item_name):
                    # Item already exists
                    return
        else:
            # Initialize inventory dataframe if it doesn't exist
            self.data['inventory'] = pd.DataFrame(columns=[
                'item_id', 'item_name', 'category', 'quantity', 'qty_purchased', 'qty_used',
                'unit', 'price', 'avg_price', 'location', 'expiry_date', 'reorder_level'
            ])
        
        # Generate new item ID
        item_id = 1
        if len(self.data['inventory']) > 0 and 'item_id' in self.data['inventory'].columns:
            item_id = self.data['inventory']['item_id'].max() + 1 if not self.data['inventory'].empty else 1
        
        # Set default values
        from datetime import datetime, timedelta
        
        # Create new item
        new_item = pd.DataFrame({
            'item_id': [item_id],
            'item_name': [item_name],
            'category': ['Recipe Ingredient'],  # Default category
            'quantity': [0],  # Default quantity
            'qty_purchased': [0],  # Default purchased
            'qty_used': [0],  # Default used
            'unit': [unit],
            'price': [1.0],  # Default price
            'avg_price': [1.0],  # Default avg price
            'location': ['Pantry'],  # Default location
            'expiry_date': [(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')],  # Default expiry
            'reorder_level': [1.0]  # Default reorder level
        })
        
        # Add to inventory dataframe
        self.data['inventory'] = pd.concat([self.data['inventory'], new_item], ignore_index=True)
        
        # Save to CSV
        self.data['inventory'].to_csv('data/inventory.csv', index=False)
    
    def setup_nutrition_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.nutrition_tab)
        
        # Add subheader
        header = QLabel("Nutritional Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Create form for selecting day to analyze
        form_group = QGroupBox("Select Day to Analyze")
        form_layout = QFormLayout(form_group)
        layout.addWidget(form_group)
        
        # Day selection
        self.nutrition_day_combo = QComboBox()
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.nutrition_day_combo.addItems(days_of_week)
        form_layout.addRow("Day:", self.nutrition_day_combo)
        
        # Analyze button
        self.analyze_button = QPushButton("Analyze Nutrition")
        self.analyze_button.clicked.connect(self.analyze_nutrition)
        form_layout.addRow("", self.analyze_button)
        
        # Results section
        results_group = QGroupBox("Nutritional Analysis Results")
        results_layout = QVBoxLayout(results_group)
        layout.addWidget(results_group)
        
        # Create a widget to hold the charts
        self.nutrition_charts = QWidget()
        self.nutrition_charts_layout = QVBoxLayout(self.nutrition_charts)
        results_layout.addWidget(self.nutrition_charts)
        
        # Nutrition summary table
        self.nutrition_table = QTableWidget()
        self.nutrition_table.setColumnCount(5)
        self.nutrition_table.setHorizontalHeaderLabels(["Meal", "Recipe", "Servings", "Calories", "Total Calories"])
        self.nutrition_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.nutrition_table)
    
    def analyze_nutrition(self):
        # Get selected day
        day = self.nutrition_day_combo.currentText()
        
        # Filter meal plan for the selected day
        day_meals = self.meal_plan_df[self.meal_plan_df['day'] == day]
        
        if len(day_meals) == 0:
            # No meals found for this day
            QMessageBox.information(self, "No Meals", f"No meals found for {day}.")
            return
        
        # Clear previous charts
        # Remove all widgets from the layout
        while self.nutrition_charts_layout.count():
            item = self.nutrition_charts_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Calculate nutrition for each meal
        nutrition_data = []
        total_calories = 0
        
        # Clear the table
        self.nutrition_table.setRowCount(0)
        self.nutrition_table.setRowCount(len(day_meals))
        
        for i, (_, meal) in enumerate(day_meals.iterrows()):
            # Get recipe details
            recipe = self.recipes_df[self.recipes_df['recipe_id'] == meal['recipe_id']].iloc[0]
            
            # Calculate calories for this meal
            meal_calories = recipe['calories_per_serving'] * meal['servings']
            total_calories += meal_calories
            
            # Add to table
            self.nutrition_table.setItem(i, 0, QTableWidgetItem(meal['meal_type']))
            self.nutrition_table.setItem(i, 1, QTableWidgetItem(meal['recipe_name']))
            self.nutrition_table.setItem(i, 2, QTableWidgetItem(str(meal['servings'])))
            self.nutrition_table.setItem(i, 3, QTableWidgetItem(str(recipe['calories_per_serving'])))
            self.nutrition_table.setItem(i, 4, QTableWidgetItem(str(meal_calories)))
            
            # Add to nutrition data for chart
            nutrition_data.append({
                'meal_type': meal['meal_type'],
                'calories': meal_calories
            })
        
        # Add a row for total calories
        row = self.nutrition_table.rowCount()
        self.nutrition_table.insertRow(row)
        self.nutrition_table.setItem(row, 0, QTableWidgetItem("Total"))
        self.nutrition_table.setItem(row, 4, QTableWidgetItem(str(total_calories)))
        
        # Create nutrition charts
        # Calories by meal chart
        fig, ax = plt.subplots(figsize=(8, 4))
        meal_types = [item['meal_type'] for item in nutrition_data]
        calories = [item['calories'] for item in nutrition_data]
        ax.bar(meal_types, calories)
        ax.set_title(f'Calories by Meal for {day}')
        ax.set_xlabel('Meal')
        ax.set_ylabel('Calories')
        plt.tight_layout()
        
        # Add the chart to the layout
        canvas = FigureCanvas(fig)
        self.nutrition_charts_layout.addWidget(canvas)
    
    def setup_shopping_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.shopping_tab)
        
        # Add subheader
        header = QLabel("Shopping List Generator")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Create form for generating shopping list
        form_group = QGroupBox("Generate Shopping List")
        form_layout = QFormLayout(form_group)
        layout.addWidget(form_group)
        
        # Date range selection
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(7))
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        form_layout.addRow("Date Range:", date_layout)
        
        # Generate button
        self.generate_button = QPushButton("Generate Shopping List")
        self.generate_button.clicked.connect(self.generate_shopping_list)
        form_layout.addRow("", self.generate_button)
        
        # Shopping list results
        results_group = QGroupBox("Shopping List")
        results_layout = QVBoxLayout(results_group)
        layout.addWidget(results_group)
        
        # Shopping list table
        self.shopping_list_table = QTableWidget()
        self.shopping_list_table.setColumnCount(5)
        self.shopping_list_table.setHorizontalHeaderLabels(["Item", "Quantity Needed", "Current Stock", "Unit", "Priority"])

        # Apply universal column resizing functionality
        shopping_list_default_column_widths = {
            0: 200,  # Item
            1: 120,  # Quantity Needed
            2: 120,  # Current Stock
            3: 80,   # Unit
            4: 100   # Priority
        }

        # Apply column resizing with settings persistence
        self.shopping_list_table_resizer = apply_universal_column_resizing(
            self.shopping_list_table,
            'meal_planning_shopping_column_settings.json',
            shopping_list_default_column_widths
        )

        print("✅ Applied universal column resizing to meal planning shopping list table")
        results_layout.addWidget(self.shopping_list_table)
        
        # Export button
        self.export_button = QPushButton("Export to Shopping List")
        self.export_button.clicked.connect(self.export_to_shopping_list)
        self.export_button.setEnabled(False)  # Disabled until a list is generated
        results_layout.addWidget(self.export_button)
        
        # Current shopping list section
        current_list_group = QGroupBox("Current Shopping List")
        current_list_layout = QVBoxLayout(current_list_group)
        layout.addWidget(current_list_group)
        
        # Current shopping list table
        self.current_shopping_table = QTableWidget()
        self.current_shopping_table.setColumnCount(5)
        self.current_shopping_table.setHorizontalHeaderLabels(["Item", "Quantity", "Unit", "Priority", "Status"])
        self.current_shopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        current_list_layout.addWidget(self.current_shopping_table)
        
        # Populate current shopping list
        self.populate_current_shopping_list()
    
    def populate_current_shopping_list(self):
        # Get shopping list data - create empty if doesn't exist
        if 'shopping_list' not in self.data:
            self.data['shopping_list'] = pd.DataFrame(columns=[
                'item_id', 'item_name', 'category', 'quantity', 'unit', 'priority',
                'estimated_cost', 'location', 'notes', 'status', 'date_added'
            ])

        shopping_df = self.data['shopping_list'].copy()
        
        # Clear the table
        self.current_shopping_table.setRowCount(0)
        
        if len(shopping_df) > 0:
            # Populate the table
            self.current_shopping_table.setRowCount(len(shopping_df))
            for i, (_, item) in enumerate(shopping_df.iterrows()):
                self.current_shopping_table.setItem(i, 0, QTableWidgetItem(item['item_name']))
                self.current_shopping_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
                self.current_shopping_table.setItem(i, 2, QTableWidgetItem(item['unit']))
                self.current_shopping_table.setItem(i, 3, QTableWidgetItem(item['priority']))
                self.current_shopping_table.setItem(i, 4, QTableWidgetItem(item['status']))
        else:
            # Show message if shopping list is empty
            self.current_shopping_table.setRowCount(1)
            self.current_shopping_table.setSpan(0, 0, 1, 5)
            self.current_shopping_table.setItem(0, 0, QTableWidgetItem("Shopping list is empty"))
            item = self.current_shopping_table.item(0, 0)
            item.setTextAlignment(Qt.AlignCenter)
    
    def generate_shopping_list(self):
        # Get date range
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Get all recipes in meal plan for the date range
        # For simplicity, we'll just use all recipes in the meal plan
        # In a real implementation, we would filter by date
        
        # Extract ingredients from recipes
        shopping_items = []
        inventory_df = self.data['inventory'].copy() if 'inventory' in self.data else pd.DataFrame()
        
        for _, meal in self.meal_plan_df.iterrows():
            # Get recipe details
            recipe = self.recipes_df[self.recipes_df['recipe_id'] == meal['recipe_id']].iloc[0]
            
            # Get ingredients
            ingredients_list = recipe['ingredients'].split(",")
            for ingredient in ingredients_list:
                ingredient = ingredient.strip()
                
                # Check if ingredient is already in inventory
                current_stock = 0
                if len(inventory_df) > 0:
                    matching_items = inventory_df[inventory_df['item_name'].str.lower() == ingredient.lower()]
                    if len(matching_items) > 0:
                        current_stock = matching_items.iloc[0]['quantity']
                
                # Check if ingredient has quantity specified
                if "(" in ingredient and ")" in ingredient:
                    # Extract quantity and unit
                    item_name = ingredient.split("(")[0].strip()
                    quantity_str = ingredient.split("(")[1].split(")")[0].strip()
                    
                    # Parse quantity and unit
                    quantity = 1
                    unit = "units"
                    
                    if " " in quantity_str:
                        qty, unit = quantity_str.split(" ", 1)
                        try:
                            quantity = float(qty)
                        except ValueError:
                            quantity = 1
                    else:
                        try:
                            quantity = float(quantity_str)
                        except ValueError:
                            unit = quantity_str
                    
                    # Add to shopping items
                    shopping_items.append({
                        'item_name': item_name,
                        'quantity_needed': quantity * meal['servings'],
                        'current_stock': current_stock,
                        'unit': unit,
                        'priority': 'Medium'
                    })
                else:
                    # No quantity specified, just add the item
                    shopping_items.append({
                        'item_name': ingredient,
                        'quantity_needed': 1 * meal['servings'],
                        'current_stock': current_stock,
                        'unit': 'units',
                        'priority': 'Medium'
                    })
        
        # Convert to dataframe and group by item
        if shopping_items:
            shopping_df = pd.DataFrame(shopping_items)
            shopping_df = shopping_df.groupby('item_name').agg({
                'quantity_needed': 'sum',
                'current_stock': 'first',
                'unit': 'first',
                'priority': 'first'
            }).reset_index()
            
            # Populate the shopping list table
            self.shopping_list_table.setRowCount(len(shopping_df))
            for i, (_, item) in enumerate(shopping_df.iterrows()):
                self.shopping_list_table.setItem(i, 0, QTableWidgetItem(item['item_name']))
                self.shopping_list_table.setItem(i, 1, QTableWidgetItem(str(item['quantity_needed'])))
                self.shopping_list_table.setItem(i, 2, QTableWidgetItem(str(item['current_stock'])))
                self.shopping_list_table.setItem(i, 3, QTableWidgetItem(item['unit']))
                self.shopping_list_table.setItem(i, 4, QTableWidgetItem(item['priority']))
            
            # Enable export button
            self.export_button.setEnabled(True)
            
            # Store the generated shopping list for export
            self.generated_shopping_list = shopping_df
            
            QMessageBox.information(self, "Success", f"Generated shopping list with {len(shopping_df)} items!")
        else:
            self.shopping_list_table.setRowCount(1)
            self.shopping_list_table.setSpan(0, 0, 1, 5)
            self.shopping_list_table.setItem(0, 0, QTableWidgetItem("No items needed for the current meal plan"))
            item = self.shopping_list_table.item(0, 0)
            item.setTextAlignment(Qt.AlignCenter)
            
            # Disable export button
            self.export_button.setEnabled(False)
    

    def showEvent(self, event):
        """Handle widget show event to refresh data"""
        super().showEvent(event)
        try:
            # Force refresh data when widget is shown
            self.refresh_all_data()
        except Exception as e:
            print(f"Error in meal planning showEvent: {e}")

    def export_to_shopping_list(self):
        if not hasattr(self, 'generated_shopping_list'):
            QMessageBox.warning(self, "Warning", "Please generate a shopping list first.")
            return

        # Get existing shopping list - create empty if doesn't exist
        if 'shopping_list' not in self.data:
            self.data['shopping_list'] = pd.DataFrame(columns=[
                'item_id', 'item_name', 'category', 'quantity', 'unit', 'priority',
                'estimated_cost', 'store', 'notes', 'status'
            ])

        existing_shopping = self.data['shopping_list'].copy()
        
        # Add new items
        for _, item in self.generated_shopping_list.iterrows():
            # Check if item already exists in shopping list
            existing_item = existing_shopping[existing_shopping['item_name'] == item['item_name']]
            
            if len(existing_item) > 0:
                # Update quantity
                existing_shopping.loc[existing_shopping['item_name'] == item['item_name'], 'quantity'] += item['quantity_needed']
            else:
                # Add new item
                new_item = {
                    'item_id': existing_shopping['item_id'].max() + 1 if len(existing_shopping) > 0 else 1,
                    'item_name': item['item_name'],
                    'category': 'Ingredients',
                    'quantity': item['quantity_needed'],
                    'unit': item['unit'],
                    'priority': item['priority'],
                    'estimated_cost': 0.0,
                    'store': 'Supermarket',
                    'notes': 'Added from meal plan',
                    'status': 'Pending'
                }
                existing_shopping = pd.concat([existing_shopping, pd.DataFrame([new_item])], ignore_index=True)
        
        # Save to CSV
        existing_shopping.to_csv('data/shopping_list.csv', index=False)
        
        # Update data dictionary
        self.data['shopping_list'] = existing_shopping
        
        # Update current shopping list table
        self.populate_current_shopping_list()
        
        QMessageBox.information(self, "Success", "Items added to shopping list!")

    def setup_missing_ingredients_tab(self):
        """Set up the missing ingredients tab"""
        layout = QVBoxLayout(self.missing_ingredients_tab)

        # Add title
        title = QLabel("Missing Ingredients Analysis")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Control buttons
        controls_layout = QHBoxLayout()

        # Check missing ingredients button
        self.check_missing_btn = QPushButton("Check Missing Ingredients")
        self.check_missing_btn.clicked.connect(self.check_missing_ingredients)
        controls_layout.addWidget(self.check_missing_btn)

        # Refresh button
        self.refresh_missing_btn = QPushButton("Refresh")
        self.refresh_missing_btn.clicked.connect(self.refresh_missing_ingredients)
        controls_layout.addWidget(self.refresh_missing_btn)

        # Add missing to shopping list button
        self.add_to_shopping_btn = QPushButton("Add Missing to Shopping List")
        self.add_to_shopping_btn.clicked.connect(self.add_missing_to_shopping)
        self.add_to_shopping_btn.setEnabled(False)
        controls_layout.addWidget(self.add_to_shopping_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Missing ingredients table
        self.missing_ingredients_table = QTableWidget()
        self.missing_ingredients_table.setColumnCount(6)
        self.missing_ingredients_table.setHorizontalHeaderLabels([
            "Recipe", "Ingredient", "Required Qty", "Unit", "Available Qty", "Status"
        ])
        self.missing_ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.missing_ingredients_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.missing_ingredients_table)

        # Summary section
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.missing_summary_label = QLabel("Click 'Check Missing Ingredients' to analyze your meal plan")
        self.missing_summary_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.missing_summary_label)

        layout.addWidget(summary_group)

    def check_missing_ingredients(self):
        """Check for missing ingredients in the current meal plan"""
        try:
            # Clear the table
            self.missing_ingredients_table.setRowCount(0)

            # Get current meal plan
            if self.meal_plan_df.empty:
                QMessageBox.information(self, "No Meal Plan", "No meals found in the current meal plan.")
                return

            # Get inventory data
            inventory_df = self.data.get('inventory', pd.DataFrame())
            recipe_ingredients_df = self.data.get('recipe_ingredients', pd.DataFrame())

            missing_items = []

            # Check each meal in the plan
            for _, meal in self.meal_plan_df.iterrows():
                recipe_id = meal['recipe_id']
                recipe_name = meal['recipe_name']

                # Get ingredients for this recipe
                if not recipe_ingredients_df.empty:
                    recipe_ingredients = recipe_ingredients_df[
                        recipe_ingredients_df['recipe_id'] == recipe_id
                    ]

                    for _, ingredient in recipe_ingredients.iterrows():
                        item_name = ingredient['item_name']
                        required_qty = ingredient['quantity']
                        unit = ingredient['unit']

                        # Check if ingredient is available in inventory
                        available_qty = 0
                        status = "Missing"

                        if not inventory_df.empty:
                            matching_items = inventory_df[
                                inventory_df['item_name'].str.lower() == item_name.lower()
                            ]

                            if not matching_items.empty:
                                available_qty = matching_items.iloc[0]['quantity']
                                if available_qty >= required_qty:
                                    status = "Available"
                                else:
                                    status = "Insufficient"

                        # Add to missing items if not fully available
                        if status != "Available":
                            missing_items.append({
                                'recipe': recipe_name,
                                'ingredient': item_name,
                                'required_qty': required_qty,
                                'unit': unit,
                                'available_qty': available_qty,
                                'status': status
                            })

            # Populate the table
            if missing_items:
                self.missing_ingredients_table.setRowCount(len(missing_items))

                for i, item in enumerate(missing_items):
                    self.missing_ingredients_table.setItem(i, 0, QTableWidgetItem(item['recipe']))
                    self.missing_ingredients_table.setItem(i, 1, QTableWidgetItem(item['ingredient']))
                    self.missing_ingredients_table.setItem(i, 2, QTableWidgetItem(str(item['required_qty'])))
                    self.missing_ingredients_table.setItem(i, 3, QTableWidgetItem(item['unit']))
                    self.missing_ingredients_table.setItem(i, 4, QTableWidgetItem(str(item['available_qty'])))

                    # Color code the status
                    status_item = QTableWidgetItem(item['status'])
                    if item['status'] == "Missing":
                        status_item.setBackground(QColor(255, 200, 200))  # Light red
                    elif item['status'] == "Insufficient":
                        status_item.setBackground(QColor(255, 255, 200))  # Light yellow

                    self.missing_ingredients_table.setItem(i, 5, status_item)

                # Update summary
                missing_count = len([item for item in missing_items if item['status'] == "Missing"])
                insufficient_count = len([item for item in missing_items if item['status'] == "Insufficient"])

                self.missing_summary_label.setText(
                    f"Found {missing_count} missing ingredients and {insufficient_count} insufficient quantities"
                )

                # Enable add to shopping button
                self.add_to_shopping_btn.setEnabled(True)

            else:
                # No missing ingredients
                self.missing_ingredients_table.setRowCount(1)
                self.missing_ingredients_table.setSpan(0, 0, 1, 6)
                item = QTableWidgetItem("All ingredients are available! ✅")
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor(200, 255, 200))  # Light green
                self.missing_ingredients_table.setItem(0, 0, item)

                self.missing_summary_label.setText("All ingredients for your meal plan are available!")
                self.add_to_shopping_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check missing ingredients: {str(e)}")

    def refresh_missing_ingredients(self):
        """Refresh the missing ingredients analysis"""
        self.check_missing_ingredients()

    def add_missing_to_shopping(self):
        """Add missing ingredients to the shopping list"""
        try:
            # Get missing ingredients from the table
            missing_items = []

            for row in range(self.missing_ingredients_table.rowCount()):
                status_item = self.missing_ingredients_table.item(row, 5)
                if status_item and status_item.text() in ["Missing", "Insufficient"]:
                    ingredient = self.missing_ingredients_table.item(row, 1).text()
                    required_qty = float(self.missing_ingredients_table.item(row, 2).text())
                    available_qty = float(self.missing_ingredients_table.item(row, 4).text())
                    unit = self.missing_ingredients_table.item(row, 3).text()

                    # Calculate needed quantity
                    needed_qty = required_qty - available_qty
                    if needed_qty > 0:
                        missing_items.append({
                            'item_name': ingredient,
                            'quantity': needed_qty,
                            'unit': unit
                        })

            if not missing_items:
                QMessageBox.information(self, "No Items", "No missing ingredients to add to shopping list.")
                return

            # Get existing shopping list
            shopping_df = self.data.get('shopping_list', pd.DataFrame())

            # Add missing items to shopping list
            added_count = 0
            for item in missing_items:
                # Check if item already exists
                existing_item = shopping_df[
                    shopping_df['item_name'].str.lower() == item['item_name'].lower()
                ]

                if not existing_item.empty:
                    # Update quantity
                    shopping_df.loc[
                        shopping_df['item_name'].str.lower() == item['item_name'].lower(),
                        'quantity'
                    ] += item['quantity']
                else:
                    # Add new item
                    new_item = {
                        'item_id': shopping_df['item_id'].max() + 1 if not shopping_df.empty else 1,
                        'item_name': item['item_name'],
                        'category': 'Missing Ingredients',
                        'quantity': item['quantity'],
                        'unit': item['unit'],
                        'priority': 'High',
                        'estimated_cost': 0.0,
                        'location': 'Supermarket',
                        'notes': 'Added from missing ingredients analysis',
                        'status': 'Pending',
                        'daily_price': '',
                        'average_price': '',
                        'date_added': pd.Timestamp.now().strftime('%Y-%m-%d'),
                        'date_purchased': ''
                    }
                    shopping_df = pd.concat([shopping_df, pd.DataFrame([new_item])], ignore_index=True)
                    added_count += 1

            # Save to CSV
            shopping_df.to_csv('data/shopping_list.csv', index=False)

            # Update data dictionary
            self.data['shopping_list'] = shopping_df

            QMessageBox.information(
                self,
                "Success",
                f"Added {added_count} missing ingredients to shopping list!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add items to shopping list: {str(e)}")

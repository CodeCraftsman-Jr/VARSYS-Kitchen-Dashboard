from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                              QLabel, QComboBox, QLineEdit, QPushButton, QTabWidget,
                              QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit, QGroupBox,
                              QMessageBox, QHeaderView, QSplitter, QTextEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import os
import logging
import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QDialog, QLineEdit,
    QSpinBox, QTextEdit, QDialogButtonBox, QHBoxLayout, QComboBox,
    QCalendarWidget, QListWidget, QListWidgetItem, QCheckBox, QStyledItemDelegate, QDateEdit,
    QCompleter, QListView # Added QCompleter, QListView for completeness, may not be used here
)
import logging # Added for diagnostics
from PySide6.QtCore import Qt, Signal, QDate, QModelIndex # Added QModelIndex
from PySide6.QtGui import QFont, QIcon # Added QIcon

# Import notification system
try:
    from .notification_system import notify_info, notify_success, notify_warning, notify_error
except ImportError:
    # Fallback if notification system is not available
    def notify_info(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_success(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_warning(title, message, **kwargs): logging.warning(f"{title}: {message}")
    def notify_error(title, message, **kwargs): logging.error(f"{title}: {message}")

# Import smart ingredient manager
try:
    from .smart_ingredient_manager import SmartIngredientManager
except ImportError:
    SmartIngredientManager = None
    logging.warning("Smart Ingredient Manager not available")

# Ensure pandas is aliased if not already
if 'pd' not in globals():
    import pandas as pd


class IngredientDialog(QDialog):
    def __init__(self, parent=None, ingredient_data=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Ingredient")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.data = data

        main_layout = QVBoxLayout(self)

        # Create tabs for different input methods
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Tab 1: Select from existing items
        existing_tab = QWidget()
        existing_layout = QVBoxLayout(existing_tab)

        # Search for existing items
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Items:")
        self.item_search = QLineEdit()
        self.item_search.setPlaceholderText("Type to search existing items...")
        self.item_search.textChanged.connect(self.filter_existing_items)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.item_search)
        existing_layout.addLayout(search_layout)

        # List of existing items
        self.existing_items_list = QListWidget()
        self.existing_items_list.itemClicked.connect(self.on_existing_item_selected)
        existing_layout.addWidget(self.existing_items_list)

        # Load existing items
        self.load_existing_items()

        tab_widget.addTab(existing_tab, "Select Existing Item")

        # Tab 2: Add new item
        new_tab = QWidget()
        new_layout = QFormLayout(new_tab)

        self.item_name_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)  # Allow custom categories
        self.load_categories()

        new_layout.addRow("Item Name:", self.item_name_edit)
        new_layout.addRow("Category:", self.category_combo)

        tab_widget.addTab(new_tab, "Add New Item")

        # Common fields for both tabs
        common_group = QGroupBox("Ingredient Details")
        common_layout = QFormLayout(common_group)

        self.quantity_edit = QLineEdit()
        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)
        # Common units
        common_units = ["grams", "kg", "ml", "liters", "cups", "tbsp", "tsp", "pcs", "slices", "cloves"]
        self.unit_combo.addItems(common_units)
        self.notes_edit = QLineEdit()

        common_layout.addRow("Quantity:", self.quantity_edit)
        common_layout.addRow("Unit:", self.unit_combo)
        common_layout.addRow("Notes:", self.notes_edit)

        main_layout.addWidget(common_group)

        # Pre-fill data if editing
        if ingredient_data:
            self.item_name_edit.setText(ingredient_data.get('item_name', ''))
            self.quantity_edit.setText(str(ingredient_data.get('quantity', '')))
            unit = ingredient_data.get('unit', '')
            unit_index = self.unit_combo.findText(unit)
            if unit_index >= 0:
                self.unit_combo.setCurrentIndex(unit_index)
            else:
                self.unit_combo.setCurrentText(unit)
            self.notes_edit.setText(ingredient_data.get('notes', ''))

            # Try to find and select the item in existing items
            item_name = ingredient_data.get('item_name', '')
            for i in range(self.existing_items_list.count()):
                item = self.existing_items_list.item(i)
                if item and item.text().split(' - ')[0] == item_name:
                    self.existing_items_list.setCurrentItem(item)
                    tab_widget.setCurrentIndex(0)  # Switch to existing items tab
                    break

        # Dialog buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.buttons)

        # Store selected item info
        self.selected_item_name = ""
        self.selected_category = ""
        self.tab_widget = tab_widget

    def load_existing_items(self):
        """Load existing items from the data"""
        self.existing_items_list.clear()
        if not self.data or 'items' not in self.data:
            return

        items_df = self.data['items']
        if items_df.empty:
            return

        for _, item in items_df.iterrows():
            item_name = str(item.get('item_name', ''))
            category = str(item.get('category', 'Unknown'))
            unit = str(item.get('unit', ''))

            display_text = f"{item_name} - {category}"
            if unit:
                display_text += f" ({unit})"

            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, {
                'item_name': item_name,
                'category': category,
                'unit': unit
            })
            self.existing_items_list.addItem(list_item)

    def filter_existing_items(self):
        """Filter existing items based on search text"""
        search_text = self.item_search.text().lower()

        for i in range(self.existing_items_list.count()):
            item = self.existing_items_list.item(i)
            if item:
                item_text = item.text().lower()
                item.setHidden(search_text not in item_text)

    def on_existing_item_selected(self, item):
        """Handle selection of an existing item"""
        if item:
            item_data = item.data(Qt.UserRole)
            if item_data:
                self.selected_item_name = item_data['item_name']
                self.selected_category = item_data['category']

                # Auto-fill unit if available
                unit = item_data.get('unit', '')
                if unit:
                    unit_index = self.unit_combo.findText(unit)
                    if unit_index >= 0:
                        self.unit_combo.setCurrentIndex(unit_index)
                    else:
                        self.unit_combo.setCurrentText(unit)

    def load_categories(self):
        """Load categories from the data"""
        self.category_combo.clear()

        if self.data and 'categories' in self.data:
            categories_df = self.data['categories']
            if not categories_df.empty and 'category_name' in categories_df.columns:
                categories = categories_df['category_name'].unique().tolist()
                self.category_combo.addItems(sorted(categories))

        # Add some default categories if none exist
        if self.category_combo.count() == 0:
            default_categories = ["Vegetables", "Fruits", "Grains", "Spices", "Meat", "Dairy", "Oils", "Unknown"]
            self.category_combo.addItems(default_categories)

    def get_data(self):
        # Determine which tab is active and get item name accordingly
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0 and self.selected_item_name:  # Existing item selected
            item_name = self.selected_item_name
            category = self.selected_category
        else:  # New item
            item_name = self.item_name_edit.text().strip()
            category = self.category_combo.currentText().strip()

        if not item_name:
            QMessageBox.warning(self, "Input Error", "Ingredient name cannot be empty.")
            return None

        try:
            quantity_text = self.quantity_edit.text().strip()
            if not quantity_text:
                quantity = 0.0
            else:
                quantity = float(quantity_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Quantity must be a valid number.")
            return None

        return {
            'item_name': item_name,
            'quantity': quantity,
            'unit': self.unit_combo.currentText().strip(),
            'notes': self.notes_edit.text().strip(),
            'category': category
        }

class AddNewRecipeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Recipe")
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)
        main_layout = QVBoxLayout(self)

        # Recipe Details
        details_group = QGroupBox("Recipe Details")
        details_form_layout = QFormLayout()
        self.recipe_name_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.servings_edit = QSpinBox()
        self.servings_edit.setRange(1, 100)
        self.servings_edit.setValue(1)
        self.prep_time_edit = QSpinBox()
        self.prep_time_edit.setSuffix(" min")
        self.prep_time_edit.setRange(0, 1000)
        self.cook_time_edit = QSpinBox()
        self.cook_time_edit.setSuffix(" min")
        self.cook_time_edit.setRange(0, 1000)
        self.description_edit = QTextEdit()
        self.description_edit.setFixedHeight(80)

        details_form_layout.addRow("Recipe Name:", self.recipe_name_edit)
        details_form_layout.addRow("Category:", self.category_edit)
        details_form_layout.addRow("Servings:", self.servings_edit)
        details_form_layout.addRow("Prep Time (mins):", self.prep_time_edit)
        details_form_layout.addRow("Cook Time (mins):", self.cook_time_edit)
        details_form_layout.addRow("Description:", self.description_edit)
        details_group.setLayout(details_form_layout)
        main_layout.addWidget(details_group)

        # Ingredients
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout()
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Unit", "Notes"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ingredients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ingredients_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        ingredients_buttons_layout = QHBoxLayout()
        add_ingredient_button = QPushButton("Add Ingredient")
        add_ingredient_button.clicked.connect(self._add_ingredient_to_table)
        self.edit_ingredient_button = QPushButton("Edit Ingredient")
        self.edit_ingredient_button.clicked.connect(self._edit_ingredient_in_table)
        remove_ingredient_button = QPushButton("Remove Ingredient")
        remove_ingredient_button.clicked.connect(self._remove_ingredient_from_table)
        ingredients_buttons_layout.addWidget(add_ingredient_button)
        ingredients_buttons_layout.addWidget(self.edit_ingredient_button)
        ingredients_buttons_layout.addWidget(remove_ingredient_button)
        ingredients_buttons_layout.addStretch()

        ingredients_layout.addWidget(self.ingredients_table)
        ingredients_layout.addLayout(ingredients_buttons_layout)
        ingredients_group.setLayout(ingredients_layout)
        main_layout.addWidget(ingredients_group)

        # Dialog buttons
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.dialog_buttons)

        self.ingredients_list = [] # To store dicts of ingredient data

    def _add_ingredient_to_table(self):
        # Get data from parent widget
        parent_data = None
        if hasattr(self.parent(), 'data'):
            parent_data = self.parent().data

        dialog = IngredientDialog(self, data=parent_data)
        if dialog.exec():
            ingredient_data = dialog.get_data()
            if ingredient_data: # get_data handles validation for name
                self.ingredients_list.append(ingredient_data)
                self._refresh_ingredients_table()

    def _edit_ingredient_in_table(self):
        selected_rows = self.ingredients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an ingredient to edit.")
            return
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "Selection Error", "Please select only one ingredient to edit.")
            return

        row_index = selected_rows[0].row()
        current_ingredient_data = self.ingredients_list[row_index]

        # Get data from parent widget
        parent_data = None
        if hasattr(self.parent(), 'data'):
            parent_data = self.parent().data

        dialog = IngredientDialog(self, ingredient_data=current_ingredient_data, data=parent_data)
        if dialog.exec():
            updated_ingredient_data = dialog.get_data()
            if updated_ingredient_data:
                self.ingredients_list[row_index] = updated_ingredient_data
                self._refresh_ingredients_table()

    def _remove_ingredient_from_table(self):
        selected_rows = self.ingredients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an ingredient to remove.")
            return
        
        # Remove in reverse order to avoid index issues
        for index_obj in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
            del self.ingredients_list[index_obj.row()]
        self._refresh_ingredients_table()

    def _refresh_ingredients_table(self):
        self.ingredients_table.setRowCount(0)
        for i, ingredient in enumerate(self.ingredients_list):
            self.ingredients_table.insertRow(i)
            self.ingredients_table.setItem(i, 0, QTableWidgetItem(ingredient['item_name']))
            self.ingredients_table.setItem(i, 1, QTableWidgetItem(str(ingredient['quantity'])))
            self.ingredients_table.setItem(i, 2, QTableWidgetItem(ingredient['unit']))
            self.ingredients_table.setItem(i, 3, QTableWidgetItem(ingredient['notes']))
            
    def get_data(self):
        recipe_name = self.recipe_name_edit.text().strip()
        if not recipe_name:
            QMessageBox.warning(self, "Input Error", "Recipe name cannot be empty.")
            return None

        recipe_details = {
            'recipe_name': recipe_name,
            'category': self.category_edit.text().strip(),
            'servings': self.servings_edit.value(),
            'prep_time': self.prep_time_edit.value(),
            'cook_time': self.cook_time_edit.value(),
            'description': self.description_edit.toPlainText().strip()
        }
        return recipe_details, self.ingredients_list


class EditRecipeDialog(QDialog):
    def __init__(self, parent=None, recipe=None, recipe_ingredients_df=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Recipe")
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)
        self.recipe = recipe
        self.recipe_ingredients_df = recipe_ingredients_df if recipe_ingredients_df is not None else pd.DataFrame()

        main_layout = QVBoxLayout(self)

        # Recipe Details
        details_group = QGroupBox("Recipe Details")
        details_form_layout = QFormLayout()
        self.recipe_name_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.servings_edit = QSpinBox()
        self.servings_edit.setRange(1, 100)
        self.servings_edit.setValue(1)
        self.prep_time_edit = QSpinBox()
        self.prep_time_edit.setSuffix(" min")
        self.prep_time_edit.setRange(0, 1000)
        self.cook_time_edit = QSpinBox()
        self.cook_time_edit.setSuffix(" min")
        self.cook_time_edit.setRange(0, 1000)
        self.description_edit = QTextEdit()
        self.description_edit.setFixedHeight(80)

        # Pre-fill with existing recipe data
        if recipe is not None:
            self.recipe_name_edit.setText(str(recipe.get('recipe_name', '')))
            self.category_edit.setText(str(recipe.get('category', '')))
            self.servings_edit.setValue(int(recipe.get('servings', 1)))
            self.prep_time_edit.setValue(int(recipe.get('prep_time', 0)))
            self.cook_time_edit.setValue(int(recipe.get('cook_time', 0)))
            self.description_edit.setPlainText(str(recipe.get('description', '')))

        details_form_layout.addRow("Recipe Name:", self.recipe_name_edit)
        details_form_layout.addRow("Category:", self.category_edit)
        details_form_layout.addRow("Servings:", self.servings_edit)
        details_form_layout.addRow("Prep Time (mins):", self.prep_time_edit)
        details_form_layout.addRow("Cook Time (mins):", self.cook_time_edit)
        details_form_layout.addRow("Description:", self.description_edit)
        details_group.setLayout(details_form_layout)
        main_layout.addWidget(details_group)

        # Ingredients
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout()
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Unit", "Notes"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ingredients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ingredients_table.setEditTriggers(QTableWidget.NoEditTriggers)

        ingredients_buttons_layout = QHBoxLayout()
        add_ingredient_button = QPushButton("Add Ingredient")
        add_ingredient_button.clicked.connect(self._add_ingredient_to_table)
        self.edit_ingredient_button = QPushButton("Edit Ingredient")
        self.edit_ingredient_button.clicked.connect(self._edit_ingredient_in_table)
        remove_ingredient_button = QPushButton("Remove Ingredient")
        remove_ingredient_button.clicked.connect(self._remove_ingredient_from_table)
        ingredients_buttons_layout.addWidget(add_ingredient_button)
        ingredients_buttons_layout.addWidget(self.edit_ingredient_button)
        ingredients_buttons_layout.addWidget(remove_ingredient_button)
        ingredients_buttons_layout.addStretch()

        ingredients_layout.addWidget(self.ingredients_table)
        ingredients_layout.addLayout(ingredients_buttons_layout)
        ingredients_group.setLayout(ingredients_layout)
        main_layout.addWidget(ingredients_group)

        # Dialog buttons
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.dialog_buttons)

        # Load existing ingredients
        self.ingredients_list = []
        self._load_existing_ingredients()

    def _load_existing_ingredients(self):
        """Load existing ingredients for the recipe"""
        if self.recipe is not None and not self.recipe_ingredients_df.empty:
            recipe_id = self.recipe.get('recipe_id')
            if recipe_id is not None:
                # Filter ingredients for this recipe
                recipe_ingredients = self.recipe_ingredients_df[
                    self.recipe_ingredients_df['recipe_id'] == recipe_id
                ]

                for _, ingredient in recipe_ingredients.iterrows():
                    ingredient_data = {
                        'item_name': str(ingredient.get('item_name', '')),
                        'quantity': float(ingredient.get('quantity', 0)),
                        'unit': str(ingredient.get('unit', '')),
                        'notes': str(ingredient.get('notes', ''))
                    }
                    self.ingredients_list.append(ingredient_data)

                self._refresh_ingredients_table()

    def _add_ingredient_to_table(self):
        # Get data from parent widget
        parent_data = None
        if hasattr(self.parent(), 'data'):
            parent_data = self.parent().data

        dialog = IngredientDialog(self, data=parent_data)
        if dialog.exec():
            ingredient_data = dialog.get_data()
            if ingredient_data:
                self.ingredients_list.append(ingredient_data)
                self._refresh_ingredients_table()

    def _edit_ingredient_in_table(self):
        selected_rows = self.ingredients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an ingredient to edit.")
            return
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "Selection Error", "Please select only one ingredient to edit.")
            return

        row_index = selected_rows[0].row()
        current_ingredient_data = self.ingredients_list[row_index]

        # Get data from parent widget
        parent_data = None
        if hasattr(self.parent(), 'data'):
            parent_data = self.parent().data

        dialog = IngredientDialog(self, ingredient_data=current_ingredient_data, data=parent_data)
        if dialog.exec():
            updated_ingredient_data = dialog.get_data()
            if updated_ingredient_data:
                self.ingredients_list[row_index] = updated_ingredient_data
                self._refresh_ingredients_table()

    def _remove_ingredient_from_table(self):
        selected_rows = self.ingredients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an ingredient to remove.")
            return

        # Remove in reverse order to avoid index issues
        for index_obj in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
            del self.ingredients_list[index_obj.row()]
        self._refresh_ingredients_table()

    def _refresh_ingredients_table(self):
        self.ingredients_table.setRowCount(0)
        for i, ingredient in enumerate(self.ingredients_list):
            self.ingredients_table.insertRow(i)
            self.ingredients_table.setItem(i, 0, QTableWidgetItem(ingredient['item_name']))
            self.ingredients_table.setItem(i, 1, QTableWidgetItem(str(ingredient['quantity'])))
            self.ingredients_table.setItem(i, 2, QTableWidgetItem(ingredient['unit']))
            self.ingredients_table.setItem(i, 3, QTableWidgetItem(ingredient['notes']))

    def get_data(self):
        recipe_name = self.recipe_name_edit.text().strip()
        if not recipe_name:
            QMessageBox.warning(self, "Input Error", "Recipe name cannot be empty.")
            return None, None

        recipe_details = {
            'recipe_name': recipe_name,
            'category': self.category_edit.text().strip(),
            'servings': self.servings_edit.value(),
            'prep_time': self.prep_time_edit.value(),
            'cook_time': self.cook_time_edit.value(),
            'description': self.description_edit.toPlainText().strip()
        }
        return recipe_details, self.ingredients_list


class FixedMealPlanningWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        logging.info(f"FixedMealPlanningWidget initialized. Data keys: {list(self.data.keys()) if isinstance(self.data, dict) else 'Data is not a dict'}")
        if isinstance(self.data, dict) and 'recipes' in self.data:
            logging.info(f"  'recipes' DataFrame head:\n{self.data['recipes'].head().to_string() if not self.data['recipes'].empty else '  recipes DataFrame is empty'}")
            logging.info(f"  'recipes' DataFrame columns: {self.data['recipes'].columns.tolist()}")
            logging.info(f"  'recipes' DataFrame shape: {self.data['recipes'].shape}")
        elif isinstance(self.data, dict):
            logging.warning("  'recipes' key NOT FOUND in self.data.")
        else:
            logging.error("  self.data is not a dictionary, cannot check for 'recipes'.")

        # Always try to load fresh data from CSV file first
        self.meal_plan_df = self._load_meal_plan_from_csv()

        # If CSV loading failed, fall back to data dictionary
        if self.meal_plan_df.empty:
            # Check if we have the new data structure or the old one
            if 'meal_plan_items' in data:
                self.meal_plan_df = data['meal_plan_items'].copy()
                logging.info(f"Using meal_plan_items with {len(self.meal_plan_df)} rows")
            elif 'meal_plan' in data:
                self.meal_plan_df = data['meal_plan'].copy()
                logging.info(f"Using meal_plan with {len(self.meal_plan_df)} rows")
            else:
                # Create empty DataFrame with required columns
                self.meal_plan_df = pd.DataFrame(columns=['item_id', 'plan_id', 'day', 'meal_type', 'recipe_id', 'recipe_name', 'servings', 'notes'])
                logging.info("Created empty meal plan DataFrame")
        
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
                logging.info(f"Added missing column '{col}' to meal plan data")
        
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
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.meal_plan_tab, "Weekly Meal Plan")
        self.tabs.addTab(self.recipe_tab, "Recipe Database")
        
        # Initialize smart ingredient manager
        if SmartIngredientManager:
            self.smart_ingredient_manager = SmartIngredientManager(self.data, self)
            self.smart_ingredient_manager.ingredient_added.connect(self.on_ingredient_added)
            self.smart_ingredient_manager.missing_ingredients_detected.connect(self.on_missing_ingredients_detected)

            # Try to connect to main app for bell notifications
            self.connect_to_main_app()

            logging.info("Smart Ingredient Manager initialized for meal planning")
        else:
            self.smart_ingredient_manager = None
            logging.warning("Smart Ingredient Manager not available")

        # Set up each tab
        self.setup_meal_plan_tab()
        self.setup_recipe_tab()

    def connect_to_main_app(self):
        """Connect smart ingredient manager to main app for bell notifications"""
        try:
            # Find the main app instance by traversing up the parent hierarchy
            current = self.parent()
            while current and not hasattr(current, 'add_notification'):
                current = current.parent()

            if current and hasattr(current, 'add_notification'):
                self.smart_ingredient_manager.set_main_app(current)
                logging.info("Connected smart ingredient manager to main app notification system")
            else:
                logging.warning("Could not find main app for bell notifications")
        except Exception as e:
            logging.error(f"Error connecting to main app: {e}")

    def _load_meal_plan_from_csv(self):
        """Load meal plan data directly from CSV file"""
        try:
            meal_plan_file = 'data/meal_plan.csv'
            if os.path.exists(meal_plan_file):
                df = pd.read_csv(meal_plan_file)
                logging.info(f"Loaded meal plan data from CSV with {len(df)} rows")
                return df
            else:
                logging.info(f"Meal plan CSV file '{meal_plan_file}' not found")
                return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error loading meal plan from CSV: {e}")
            return pd.DataFrame()
    
    def setup_meal_plan_tab(self):
        # Clear the existing layout if it exists
        if self.meal_plan_tab.layout():
            QWidget().setLayout(self.meal_plan_tab.layout())

        # Create layout for the tab
        layout = QVBoxLayout(self.meal_plan_tab)

        # Add title
        title = QLabel("Weekly Meal Plan")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create table for meal plan
        self.meal_plan_table = QTableWidget()
        layout.addWidget(self.meal_plan_table)
        
        # Set up table columns with added snack options
        columns = ['Day', 'Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
        self.meal_plan_table.setColumnCount(len(columns))
        self.meal_plan_table.setHorizontalHeaderLabels(columns)

        # FIXED: Enable manual column resizing for Weekly Meal Plan table
        print("🔧 Setting up Fixed Weekly Meal Plan table column resizing...")
        meal_plan_header = self.meal_plan_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        for col in range(len(columns)):
            meal_plan_header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Fixed Meal Plan Column {col} ({columns[col]}): Interactive")

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
            print(f"   Fixed Meal Plan Column {col}: {width}px")

        # Basic header configuration
        meal_plan_header.setStretchLastSection(False)
        meal_plan_header.setMinimumSectionSize(80)
        print("✅ Fixed Weekly Meal Plan table column resizing enabled!")
        
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
                # Get all recipes for this day and meal type - safely handle missing columns
                try:
                    if 'day' in self.meal_plan_df.columns and 'meal_type' in self.meal_plan_df.columns:
                        meal_items = self.meal_plan_df[
                            (self.meal_plan_df['day'] == day) & 
                            (self.meal_plan_df['meal_type'] == meal_type)
                        ]
                    else:
                        # If columns don't exist, return empty DataFrame
                        meal_items = pd.DataFrame()
                except Exception as e:
                    logging.error(f"Error filtering meal items: {e}")
                    meal_items = pd.DataFrame()
                
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
            
            # Create day cell
            day_item = QTableWidgetItem(day)
            day_item.setTextAlignment(Qt.AlignCenter)
            day_item.setBackground(QColor("#f8f9fa"))
            self.meal_plan_table.setItem(current_row, 0, day_item)
            
            # Merge cells for the day if needed
            if day_height > 1:
                self.meal_plan_table.setSpan(current_row, 0, day_height, 1)
            
            # Fill in meals for this day
            for j, meal_type in enumerate(meal_types):
                # Get all recipes for this day and meal type
                try:
                    if 'day' in self.meal_plan_df.columns and 'meal_type' in self.meal_plan_df.columns:
                        meal_items = self.meal_plan_df[
                            (self.meal_plan_df['day'] == day) & 
                            (self.meal_plan_df['meal_type'] == meal_type)
                        ]
                    else:
                        # If columns don't exist, return empty DataFrame
                        meal_items = pd.DataFrame()
                except Exception as e:
                    logging.error(f"Error filtering meal items: {e}")
                    meal_items = pd.DataFrame()
                
                # Add each meal item to the table
                if len(meal_items) > 0:
                    for k, (_, item) in enumerate(meal_items.iterrows()):
                        # Calculate the row to place this item
                        item_row = current_row + k
                        
                        # Create cell content
                        if 'recipe_name' in item and 'servings' in item:
                            content = f"{item['recipe_name']} ({item['servings']} servings)"
                        elif 'recipe_name' in item:
                            content = item['recipe_name']
                        else:
                            content = "Unknown Recipe"
                        
                        # Create table item
                        table_item = QTableWidgetItem(content)
                        table_item.setTextAlignment(Qt.AlignCenter)
                        
                        # Set the item in the table
                        self.meal_plan_table.setItem(item_row, j + 1, table_item)
                else:
                    # Create empty cell
                    empty_item = QTableWidgetItem("")
                    self.meal_plan_table.setItem(current_row, j + 1, empty_item)
            
            # Move to the next set of rows
            current_row += day_height

    def on_ingredient_added(self, ingredient_name: str, category: str, quantity: float):
        """Handle ingredient addition notification"""
        logging.info(f"Ingredient added via smart manager: {ingredient_name} (Category: {category})")

        # Send to bell notification if available
        if self.smart_ingredient_manager and hasattr(self.smart_ingredient_manager, 'send_bell_notification'):
            self.smart_ingredient_manager.send_bell_notification(
                "Smart Ingredient Detection",
                f"Added '{ingredient_name}' to inventory with category '{category}'",
                "success"
            )

        # Also show traditional notification as fallback
        notify_success(
            "Smart Ingredient Detection",
            f"Added '{ingredient_name}' to inventory with category '{category}'",
            duration=5000
        )

    def on_missing_ingredients_detected(self, missing_ingredients: list):
        """Handle missing ingredients detection"""
        if missing_ingredients:
            ingredient_list = ", ".join(missing_ingredients[:5])  # Show first 5
            if len(missing_ingredients) > 5:
                ingredient_list += f" and {len(missing_ingredients) - 5} more"

            # Send to bell notification if available
            if self.smart_ingredient_manager and hasattr(self.smart_ingredient_manager, 'send_bell_notification'):
                self.smart_ingredient_manager.send_bell_notification(
                    "Missing Ingredients Detected",
                    f"Found {len(missing_ingredients)} missing ingredients: {ingredient_list}",
                    "warning"
                )

            # Also show traditional notification as fallback
            notify_info(
                "Missing Ingredients Detected",
                f"Found {len(missing_ingredients)} missing ingredients: {ingredient_list}",
                duration=7000
            )
            logging.info(f"Missing ingredients detected: {missing_ingredients}")

    def setup_recipe_tab(self):
        # Create layout for the tab
        layout = QVBoxLayout(self.recipe_tab)
        
        # Add a title
        title = QLabel("Recipe Database")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create a split view for recipe list and details
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Recipe list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Recipe selection label
        selection_label = QLabel("Select Recipe:")
        selection_label.setFont(QFont("Arial", 12))
        left_layout.addWidget(selection_label)

        # Search functionality
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Arial", 10))
        self.recipe_search_input = QLineEdit()
        self.recipe_search_input.setPlaceholderText("Search by name, category, or ingredient...")
        self.recipe_search_input.textChanged.connect(self.filter_recipes)

        # Clear search button
        self.clear_search_button = QPushButton("Clear")
        self.clear_search_button.setMaximumWidth(60)
        self.clear_search_button.clicked.connect(self.clear_search)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.recipe_search_input)
        search_layout.addWidget(self.clear_search_button)
        left_layout.addLayout(search_layout)

        # Recipe table
        self.recipe_table = QTableWidget()
        self.recipe_table.setColumnCount(4)
        self.recipe_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Servings"])
        self.recipe_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recipe_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recipe_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Enable sorting functionality for fixed recipe table (regular table - remove duplicates)
        self.recipe_table.setSortingEnabled(True)

        # FIXED: Enable manual column resizing for Fixed Recipe table
        print("🔧 Setting up Fixed Recipe table column resizing...")
        fixed_recipe_header = self.recipe_table.horizontalHeader()

        # Set ALL columns to Interactive mode for manual resizing
        fixed_recipe_columns = ["ID", "Name", "Category", "Servings"]
        for col in range(4):
            fixed_recipe_header.setSectionResizeMode(col, QHeaderView.Interactive)
            print(f"   Fixed Recipe Column {col} ({fixed_recipe_columns[col]}): Interactive")

        # Set default column widths
        fixed_recipe_default_widths = {
            0: 60,   # ID
            1: 200,  # Name
            2: 120,  # Category
            3: 80    # Servings
        }
        for col, width in fixed_recipe_default_widths.items():
            self.recipe_table.setColumnWidth(col, width)
            print(f"   Fixed Recipe Column {col}: {width}px")

        # Basic header configuration
        fixed_recipe_header.setStretchLastSection(False)
        fixed_recipe_header.setMinimumSectionSize(50)
        print("✅ Fixed Recipe table column resizing enabled!")

        self.recipe_table.verticalHeader().setVisible(False)
        left_layout.addWidget(self.recipe_table)
        
        # Populate recipe table
        self.populate_recipe_table()
        
        # Recipe management buttons
        recipe_buttons_layout = QHBoxLayout()

        # Add button for creating new recipes
        add_button = QPushButton("Add New Recipe")
        add_button.clicked.connect(self.add_new_recipe)
        recipe_buttons_layout.addWidget(add_button)

        # Edit button for modifying existing recipes
        self.edit_recipe_button = QPushButton("Edit Recipe")
        self.edit_recipe_button.clicked.connect(self.edit_recipe)
        self.edit_recipe_button.setEnabled(False)  # Disabled until a recipe is selected
        recipe_buttons_layout.addWidget(self.edit_recipe_button)

        # Delete button for removing recipes
        self.delete_recipe_button = QPushButton("Delete Recipe")
        self.delete_recipe_button.clicked.connect(self.delete_recipe)
        self.delete_recipe_button.setEnabled(False)  # Disabled until a recipe is selected
        recipe_buttons_layout.addWidget(self.delete_recipe_button)

        left_layout.addLayout(recipe_buttons_layout)
        
        # Right panel: Recipe details and ingredients
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Recipe details
        self.recipe_details = QGroupBox("Recipe Details")
        details_layout = QFormLayout(self.recipe_details)
        
        self.recipe_name_label = QLabel("")
        self.recipe_category_label = QLabel("")
        self.recipe_servings_label = QLabel("")
        self.recipe_time_label = QLabel("")
        self.recipe_description_label = QLabel("")
        self.recipe_description_label.setWordWrap(True)
        
        details_layout.addRow("Name:", self.recipe_name_label)
        details_layout.addRow("Category:", self.recipe_category_label)
        details_layout.addRow("Servings:", self.recipe_servings_label)
        details_layout.addRow("Time:", self.recipe_time_label)
        details_layout.addRow("Description:", self.recipe_description_label)
        
        right_layout.addWidget(self.recipe_details)
        
        # Ingredients list
        self.ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout(self.ingredients_group)
        
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(["Ingredient", "Quantity", "Unit", "Notes"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ingredients_table.verticalHeader().setVisible(False)
        ingredients_layout.addWidget(self.ingredients_table)
        
        # Add button for ingredient management
        ingredient_buttons = QHBoxLayout()
        add_ingredient_btn = QPushButton("Add Ingredient")
        add_ingredient_btn.clicked.connect(self.add_ingredient)
        remove_ingredient_btn = QPushButton("Remove Ingredient")
        remove_ingredient_btn.clicked.connect(self.remove_ingredient)
        ingredient_buttons.addWidget(add_ingredient_btn)
        ingredient_buttons.addWidget(remove_ingredient_btn)
        ingredients_layout.addLayout(ingredient_buttons)
        
        right_layout.addWidget(self.ingredients_group)
        
        # Note: Sales tracking has been removed from this tab as requested
        # Sales should be tracked via the Sales tab instead
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 400])
        
        # Connect recipe selection to detail view
        self.recipe_table.itemSelectionChanged.connect(self.load_recipe_details)
        
    def populate_recipe_table(self, filtered_df=None):
        """Populate the recipe table with data from the recipes dataframe"""
        self.recipe_table.setRowCount(0)  # Clear existing rows

        # Use filtered dataframe if provided, otherwise use full dataframe
        df_to_use = filtered_df if filtered_df is not None else self.recipes_df

        if len(df_to_use) == 0:
            return

        # Add recipes to the table
        for i, (_, recipe) in enumerate(df_to_use.iterrows()):
            self.recipe_table.insertRow(i)

            # Add recipe data
            id_item = QTableWidgetItem(str(recipe['recipe_id']))
            name_item = QTableWidgetItem(recipe['recipe_name'])
            category_item = QTableWidgetItem(recipe['category'] if 'category' in recipe else "")
            servings_item = QTableWidgetItem(str(recipe['servings']) if 'servings' in recipe else "")

            self.recipe_table.setItem(i, 0, id_item)
            self.recipe_table.setItem(i, 1, name_item)
            self.recipe_table.setItem(i, 2, category_item)
            self.recipe_table.setItem(i, 3, servings_item)
            
    def load_recipe_details(self):
        """Load the details of the selected recipe"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            # Disable edit and delete buttons when no recipe is selected
            self.edit_recipe_button.setEnabled(False)
            self.delete_recipe_button.setEnabled(False)
            return

        # Enable edit and delete buttons when a recipe is selected
        self.edit_recipe_button.setEnabled(True)
        self.delete_recipe_button.setEnabled(True)

        # Get the recipe ID from the first column
        row = selected_items[0].row()
        recipe_id = float(self.recipe_table.item(row, 0).text())

        # Find the recipe in the dataframe
        recipe = self.recipes_df[self.recipes_df['recipe_id'] == recipe_id].iloc[0]

        # Update the detail view
        self.recipe_name_label.setText(recipe['recipe_name'])
        self.recipe_category_label.setText(recipe['category'] if 'category' in recipe else "")
        self.recipe_servings_label.setText(str(recipe['servings']) if 'servings' in recipe else "")

        prep_time = recipe['prep_time'] if 'prep_time' in recipe else 0
        cook_time = recipe['cook_time'] if 'cook_time' in recipe else 0
        total_time = int(prep_time) + int(cook_time) if prep_time and cook_time else 0
        self.recipe_time_label.setText(f"Prep: {prep_time} min, Cook: {cook_time} min (Total: {total_time} min)")

        self.recipe_description_label.setText(recipe['description'] if 'description' in recipe else "")

        # Load ingredients
        self.load_recipe_ingredients(recipe_id)
        
    def load_recipe_ingredients(self, recipe_id):
        """Load the ingredients for the selected recipe"""
        self.ingredients_table.setRowCount(0)  # Clear existing rows
        
        logging.info(f"Loading ingredients for recipe ID: {recipe_id}")
        
        # Always reload the recipe_ingredients.csv file to ensure we have the latest data
        try:
            ingredients_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'data', 'recipe_ingredients.csv')
            logging.info(f"Looking for recipe ingredients file at: {ingredients_file}")
            
            if os.path.exists(ingredients_file):
                logging.info(f"Loading recipe ingredients from file: {ingredients_file}")
                self.data['recipe_ingredients'] = pd.read_csv(ingredients_file)
                logging.info(f"Loaded {len(self.data['recipe_ingredients'])} recipe ingredients")
            else:
                logging.warning(f"Recipe ingredients file not found: {ingredients_file}")
                # If the file doesn't exist, create it with sample data
                sample_data = [
                    {'recipe_id': 1, 'ingredient_id': 1, 'item_name': 'Tomato', 'quantity': 500, 'unit': 'g', 'notes': 'Fresh tomatoes'},
                    {'recipe_id': 1, 'ingredient_id': 2, 'item_name': 'Onion', 'quantity': 100, 'unit': 'g', 'notes': 'Finely chopped'},
                    {'recipe_id': 1, 'ingredient_id': 3, 'item_name': 'Garlic', 'quantity': 10, 'unit': 'g', 'notes': 'Minced'},
                    {'recipe_id': 1, 'ingredient_id': 4, 'item_name': 'Olive Oil', 'quantity': 15, 'unit': 'ml', 'notes': 'Extra virgin'},
                    {'recipe_id': 2, 'ingredient_id': 1, 'item_name': 'Potato', 'quantity': 800, 'unit': 'g', 'notes': 'Cubed'},
                    {'recipe_id': 2, 'ingredient_id': 2, 'item_name': 'Onion', 'quantity': 200, 'unit': 'g', 'notes': 'Diced'},
                    {'recipe_id': 2, 'ingredient_id': 3, 'item_name': 'Tomato', 'quantity': 100, 'unit': 'g', 'notes': 'Chopped'},
                    {'recipe_id': 3, 'ingredient_id': 1, 'item_name': 'Rice', 'quantity': 300, 'unit': 'g', 'notes': 'Washed'},
                    {'recipe_id': 3, 'ingredient_id': 2, 'item_name': 'Milk', 'quantity': 1, 'unit': 'L', 'notes': 'Full fat'},
                    {'recipe_id': 3, 'ingredient_id': 3, 'item_name': 'Sugar', 'quantity': 100, 'unit': 'g', 'notes': 'White sugar'}
                ]
                self.data['recipe_ingredients'] = pd.DataFrame(sample_data)
                # Save the sample data to the file
                os.makedirs(os.path.dirname(ingredients_file), exist_ok=True)
                self.data['recipe_ingredients'].to_csv(ingredients_file, index=False)
                logging.info(f"Created sample recipe ingredients file at: {ingredients_file}")
        except Exception as e:
            logging.error(f"Error loading recipe ingredients: {e}")
            self.data['recipe_ingredients'] = pd.DataFrame(columns=['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes'])
        
        # Make sure recipe_id is the correct type for comparison
        try:
            recipe_id = int(recipe_id)
        except (ValueError, TypeError):
            pass  # Keep as is if it can't be converted to int
        
        # Filter ingredients for this recipe
        ingredients_df = self.data['recipe_ingredients']
        
        # Debug output to help diagnose issues
        if 'recipe_id' in ingredients_df.columns:
            logging.info(f"Recipe IDs in dataframe: {ingredients_df['recipe_id'].unique()}")
            logging.info(f"Looking for recipe ID: {recipe_id} (type: {type(recipe_id)})")
            
            # Convert dataframe recipe_id to same type as input recipe_id for comparison
            if ingredients_df['recipe_id'].dtype != type(recipe_id):
                try:
                    if isinstance(recipe_id, int):
                        ingredients_df['recipe_id'] = ingredients_df['recipe_id'].astype(int)
                    elif isinstance(recipe_id, float):
                        ingredients_df['recipe_id'] = ingredients_df['recipe_id'].astype(float)
                    elif isinstance(recipe_id, str):
                        ingredients_df['recipe_id'] = ingredients_df['recipe_id'].astype(str)
                except Exception as e:
                    logging.error(f"Error converting recipe_id types: {e}")
        else:
            logging.warning("No recipe_id column found in ingredients dataframe")
        
        # Filter for the specific recipe ID
        recipe_ingredients = ingredients_df[ingredients_df['recipe_id'] == recipe_id] if 'recipe_id' in ingredients_df.columns else pd.DataFrame()
        logging.info(f"Found {len(recipe_ingredients)} ingredients for recipe ID {recipe_id}")
        
        # Add ingredients to the table
        for i, (_, ingredient) in enumerate(recipe_ingredients.iterrows()):
            self.ingredients_table.insertRow(i)
            
            # Add ingredient data
            name_item = QTableWidgetItem(str(ingredient['item_name']) if 'item_name' in ingredient else "")
            quantity_item = QTableWidgetItem(str(ingredient['quantity']) if 'quantity' in ingredient else "")
            unit_item = QTableWidgetItem(str(ingredient['unit']) if 'unit' in ingredient else "")
            notes_item = QTableWidgetItem(str(ingredient['notes']) if 'notes' in ingredient else "")
            
            self.ingredients_table.setItem(i, 0, name_item)
            self.ingredients_table.setItem(i, 1, quantity_item)
            self.ingredients_table.setItem(i, 2, unit_item)
            self.ingredients_table.setItem(i, 3, notes_item)
        
        # If no ingredients were found, display a message in the table
        if len(recipe_ingredients) == 0:
            self.ingredients_table.insertRow(0)
            message_item = QTableWidgetItem("No ingredients found for this recipe")
            self.ingredients_table.setItem(0, 0, message_item)

    def filter_recipes(self):
        """Filter recipes based on search input"""
        search_text = self.recipe_search_input.text().lower().strip()

        if not search_text:
            # If search is empty, show all recipes
            self.populate_recipe_table()
            return

        # Filter recipes based on search criteria
        filtered_recipes = []

        for _, recipe in self.recipes_df.iterrows():
            recipe_matches = False

            # Search in recipe name
            if search_text in str(recipe.get('recipe_name', '')).lower():
                recipe_matches = True

            # Search in category
            elif search_text in str(recipe.get('category', '')).lower():
                recipe_matches = True

            # Search in description
            elif search_text in str(recipe.get('description', '')).lower():
                recipe_matches = True

            # Search in ingredients
            else:
                recipe_id = recipe.get('recipe_id')
                if recipe_id and 'recipe_ingredients' in self.data:
                    recipe_ingredients = self.data['recipe_ingredients'][
                        self.data['recipe_ingredients']['recipe_id'] == recipe_id
                    ]

                    for _, ingredient in recipe_ingredients.iterrows():
                        ingredient_name = str(ingredient.get('item_name', '')).lower()
                        if search_text in ingredient_name:
                            recipe_matches = True
                            break

            if recipe_matches:
                filtered_recipes.append(recipe)

        # Create filtered dataframe
        if filtered_recipes:
            filtered_df = pd.DataFrame(filtered_recipes)
            self.populate_recipe_table(filtered_df)
        else:
            # No matches found, clear the table
            self.recipe_table.setRowCount(0)
            # Show "No results" message
            self.recipe_table.insertRow(0)
            no_results_item = QTableWidgetItem("No recipes found matching your search")
            no_results_item.setFlags(no_results_item.flags() & ~Qt.ItemIsSelectable)
            self.recipe_table.setItem(0, 1, no_results_item)
            self.recipe_table.setSpan(0, 1, 1, 3)  # Span across columns

    def clear_search(self):
        """Clear the search input and show all recipes"""
        self.recipe_search_input.clear()
        self.populate_recipe_table()

    def _get_data_dir(self):
        """Helper function to get the data directory path."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data')

    def _check_and_create_missing_ingredients(self, ingredients_data):
        """Check if ingredients exist in items.csv and create missing ones with 'Unknown' category"""
        missing_ingredients = []

        try:
            # Load current items and categories
            data_dir = self._get_data_dir()
            items_file = os.path.join(data_dir, 'items.csv')
            categories_file = os.path.join(data_dir, 'categories.csv')

            # Load items
            if os.path.exists(items_file):
                items_df = pd.read_csv(items_file)
            else:
                items_df = pd.DataFrame(columns=['item_id', 'item_name', 'category', 'description', 'unit', 'default_cost'])

            # Load categories
            if os.path.exists(categories_file):
                categories_df = pd.read_csv(categories_file)
            else:
                categories_df = pd.DataFrame(columns=['category_id', 'category_name', 'description'])

            # Check each ingredient
            for ingredient in ingredients_data:
                item_name = ingredient['item_name']

                # Check if item exists in items_df
                if not items_df.empty and 'item_name' in items_df.columns:
                    existing_item = items_df[items_df['item_name'].str.lower() == item_name.lower()]
                    if existing_item.empty:
                        missing_ingredients.append(item_name)
                else:
                    missing_ingredients.append(item_name)

            # Create missing ingredients
            if missing_ingredients:
                # Get next item_id
                if not items_df.empty and 'item_id' in items_df.columns:
                    max_item_id = items_df['item_id'].max()
                    next_item_id = max_item_id + 1 if pd.notna(max_item_id) else 1
                else:
                    next_item_id = 1

                # Ensure 'Unknown' category exists
                unknown_category_id = self._ensure_unknown_category_exists(categories_df, categories_file)

                # Create new items
                new_items = []
                for i, item_name in enumerate(missing_ingredients):
                    new_item = {
                        'item_id': next_item_id + i,
                        'item_name': item_name,
                        'category': 'Unknown',
                        'description': 'Auto-created from recipe',
                        'unit': 'grams',  # Default unit
                        'default_cost': 0.1  # Default cost
                    }
                    new_items.append(new_item)

                # Add new items to dataframe
                if new_items:
                    new_items_df = pd.DataFrame(new_items)
                    items_df = pd.concat([items_df, new_items_df], ignore_index=True)

                    # Save updated items
                    items_df.to_csv(items_file, index=False)

                    # Update data dictionary if it exists
                    if 'items' in self.data:
                        self.data['items'] = items_df

                    # Show notification
                    notify_warning(
                        "Missing Ingredients Added",
                        f"Added {len(missing_ingredients)} missing ingredients to inventory with 'Unknown' category: {', '.join(missing_ingredients)}",
                        parent=self
                    )

                    # Log the action
                    logging.info(f"Auto-created {len(missing_ingredients)} missing ingredients: {missing_ingredients}")

        except Exception as e:
            logging.error(f"Error checking/creating missing ingredients: {e}")
            notify_error("Error", f"Failed to check missing ingredients: {str(e)}", parent=self)

        return missing_ingredients

    def _ensure_unknown_category_exists(self, categories_df, categories_file):
        """Ensure 'Unknown' category exists in categories"""
        try:
            # Check if 'Unknown' category exists
            if not categories_df.empty and 'category_name' in categories_df.columns:
                unknown_category = categories_df[categories_df['category_name'].str.lower() == 'unknown']
                if not unknown_category.empty:
                    return unknown_category.iloc[0]['category_id']

            # Create 'Unknown' category
            if not categories_df.empty and 'category_id' in categories_df.columns:
                max_category_id = categories_df['category_id'].max()
                next_category_id = max_category_id + 1 if pd.notna(max_category_id) else 1
            else:
                next_category_id = 1

            new_category = {
                'category_id': next_category_id,
                'category_name': 'Unknown',
                'description': 'Items with unknown category'
            }

            new_category_df = pd.DataFrame([new_category])
            categories_df = pd.concat([categories_df, new_category_df], ignore_index=True)

            # Save updated categories
            categories_df.to_csv(categories_file, index=False)

            # Update data dictionary if it exists
            if 'categories' in self.data:
                self.data['categories'] = categories_df

            logging.info("Created 'Unknown' category for auto-created ingredients")
            return next_category_id

        except Exception as e:
            logging.error(f"Error ensuring Unknown category exists: {e}")
            return 1

    def add_new_recipe(self):
        """Open a dialog to add a new recipe and its ingredients."""
        dialog = AddNewRecipeDialog(self)
        if dialog.exec():
            recipe_data, ingredients_data = dialog.get_data()

            if not recipe_data['recipe_name']:
                QMessageBox.warning(self, "Input Error", "Recipe name cannot be empty.")
                return

            data_dir = self._get_data_dir()
            os.makedirs(data_dir, exist_ok=True)
            
            recipes_file = os.path.join(data_dir, 'recipes.csv')
            ingredients_file = os.path.join(data_dir, 'recipe_ingredients.csv')

            if os.path.exists(recipes_file):
                try:
                    self.recipes_df = pd.read_csv(recipes_file)
                except pd.errors.EmptyDataError:
                    self.recipes_df = pd.DataFrame(columns=['recipe_id', 'recipe_name', 'category', 'servings', 'prep_time', 'cook_time', 'description'])
                    logging.warning(f"{recipes_file} is empty. Initializing with empty DataFrame.")
            else:
                self.recipes_df = pd.DataFrame(columns=['recipe_id', 'recipe_name', 'category', 'servings', 'prep_time', 'cook_time', 'description'])

            if os.path.exists(ingredients_file):
                try:
                    self.data['recipe_ingredients'] = pd.read_csv(ingredients_file)
                except pd.errors.EmptyDataError:
                    self.data['recipe_ingredients'] = pd.DataFrame(columns=['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes'])
                    logging.warning(f"{ingredients_file} is empty. Initializing with empty DataFrame.")
            else:
                self.data['recipe_ingredients'] = pd.DataFrame(columns=['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes'])

            if self.recipes_df.empty or 'recipe_id' not in self.recipes_df.columns or self.recipes_df['recipe_id'].isnull().all():
                new_recipe_id = 1
            else:
                valid_recipe_ids = pd.to_numeric(self.recipes_df['recipe_id'], errors='coerce').dropna()
                new_recipe_id = valid_recipe_ids.max() + 1 if not valid_recipe_ids.empty else 1
            
            recipe_data['recipe_id'] = new_recipe_id
            new_recipe_df = pd.DataFrame([recipe_data])
            
            expected_recipe_cols = ['recipe_id', 'recipe_name', 'category', 'servings', 'prep_time', 'cook_time', 'description']
            for col in expected_recipe_cols:
                if col not in new_recipe_df.columns:
                    new_recipe_df[col] = pd.NA 
            
            self.recipes_df = pd.concat([self.recipes_df, new_recipe_df[expected_recipe_cols]], ignore_index=True)
            self.recipes_df.to_csv(recipes_file, index=False)
            logging.info(f"Recipe '{recipe_data['recipe_name']}' added with ID {new_recipe_id} and saved to {recipes_file}")

            if ingredients_data:
                # Check for missing ingredients and auto-create them
                missing_ingredients = self._check_and_create_missing_ingredients(ingredients_data)

                new_ingredients_list = []
                current_max_ingredient_id = 0
                if not self.data['recipe_ingredients'].empty and 'ingredient_id' in self.data['recipe_ingredients'].columns and not self.data['recipe_ingredients']['ingredient_id'].isnull().all():
                    numeric_ingredient_ids = pd.to_numeric(self.data['recipe_ingredients']['ingredient_id'], errors='coerce').dropna()
                    if not numeric_ingredient_ids.empty:
                        current_max_ingredient_id = numeric_ingredient_ids.max()

                for idx, ing_dict in enumerate(ingredients_data):
                    ing_dict['recipe_id'] = new_recipe_id
                    ing_dict['ingredient_id'] = int(current_max_ingredient_id + 1 + idx) # Ensure int
                    new_ingredients_list.append(ing_dict)

                if new_ingredients_list:
                    new_ingredients_df = pd.DataFrame(new_ingredients_list)
                
                    expected_ingredient_cols = ['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes']
                    for col in expected_ingredient_cols:
                        if col not in new_ingredients_df.columns:
                            new_ingredients_df[col] = pd.NA
                    # Ensure all columns are present in self.data['recipe_ingredients'] before concat
                    for col in expected_ingredient_cols:
                         if col not in self.data['recipe_ingredients'].columns:
                            self.data['recipe_ingredients'][col] = pd.NA
                            
                    self.data['recipe_ingredients'] = pd.concat([self.data['recipe_ingredients'], new_ingredients_df[expected_ingredient_cols]], ignore_index=True)
                
                self.data['recipe_ingredients'].to_csv(ingredients_file, index=False)
                logging.info(f"Added {len(ingredients_data)} ingredients for recipe ID {new_recipe_id} and saved to {ingredients_file}")

            self.populate_recipe_table()
            QMessageBox.information(self, "Success", f"Recipe '{recipe_data['recipe_name']}' added successfully.")
        else:
            logging.info("Add new recipe dialog cancelled.")

    def edit_recipe(self):
        """Edit the selected recipe"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a recipe to edit.")
            return

        # Get the selected recipe
        row = selected_items[0].row()
        recipe_id = float(self.recipe_table.item(row, 0).text())
        recipe = self.recipes_df[self.recipes_df['recipe_id'] == recipe_id].iloc[0]

        # Create edit dialog with pre-filled data
        dialog = EditRecipeDialog(self, recipe, self.data['recipe_ingredients'])
        if dialog.exec():
            recipe_data, ingredients_data = dialog.get_data()

            if not recipe_data['recipe_name']:
                QMessageBox.warning(self, "Input Error", "Recipe name cannot be empty.")
                return

            try:
                data_dir = self._get_data_dir()
                recipes_file = os.path.join(data_dir, 'recipes.csv')
                ingredients_file = os.path.join(data_dir, 'recipe_ingredients.csv')

                # Update recipe in dataframe
                recipe_data['recipe_id'] = recipe_id
                for key, value in recipe_data.items():
                    if key in self.recipes_df.columns:
                        self.recipes_df.loc[self.recipes_df['recipe_id'] == recipe_id, key] = value

                # Save updated recipes
                self.recipes_df.to_csv(recipes_file, index=False)

                # Update ingredients - remove old ones and add new ones
                if 'recipe_ingredients' in self.data:
                    # Remove existing ingredients for this recipe
                    self.data['recipe_ingredients'] = self.data['recipe_ingredients'][
                        self.data['recipe_ingredients']['recipe_id'] != recipe_id
                    ]

                    # Add new ingredients
                    if ingredients_data:
                        # Check for missing ingredients and auto-create them
                        missing_ingredients = self._check_and_create_missing_ingredients(ingredients_data)

                        new_ingredients_list = []
                        current_max_ingredient_id = 0
                        if not self.data['recipe_ingredients'].empty and 'ingredient_id' in self.data['recipe_ingredients'].columns:
                            numeric_ingredient_ids = pd.to_numeric(self.data['recipe_ingredients']['ingredient_id'], errors='coerce').dropna()
                            if not numeric_ingredient_ids.empty:
                                current_max_ingredient_id = numeric_ingredient_ids.max()

                        for idx, ing_dict in enumerate(ingredients_data):
                            ing_dict['recipe_id'] = recipe_id
                            ing_dict['ingredient_id'] = int(current_max_ingredient_id + 1 + idx)
                            new_ingredients_list.append(ing_dict)

                        if new_ingredients_list:
                            new_ingredients_df = pd.DataFrame(new_ingredients_list)
                            expected_ingredient_cols = ['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes']
                            for col in expected_ingredient_cols:
                                if col not in new_ingredients_df.columns:
                                    new_ingredients_df[col] = pd.NA
                                if col not in self.data['recipe_ingredients'].columns:
                                    self.data['recipe_ingredients'][col] = pd.NA

                            self.data['recipe_ingredients'] = pd.concat([
                                self.data['recipe_ingredients'],
                                new_ingredients_df[expected_ingredient_cols]
                            ], ignore_index=True)

                    # Save updated ingredients
                    self.data['recipe_ingredients'].to_csv(ingredients_file, index=False)

                # Refresh the UI
                self.populate_recipe_table()
                self.load_recipe_details()  # Refresh the details view

                QMessageBox.information(self, "Success", f"Recipe '{recipe_data['recipe_name']}' updated successfully.")
                logging.info(f"Recipe '{recipe_data['recipe_name']}' (ID: {recipe_id}) updated successfully")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update recipe: {str(e)}")
                logging.error(f"Error updating recipe: {e}")

    def delete_recipe(self):
        """Delete the selected recipe"""
        selected_items = self.recipe_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a recipe to delete.")
            return

        # Get the selected recipe
        row = selected_items[0].row()
        recipe_id = float(self.recipe_table.item(row, 0).text())
        recipe = self.recipes_df[self.recipes_df['recipe_id'] == recipe_id].iloc[0]
        recipe_name = recipe['recipe_name']

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the recipe '{recipe_name}'?\n\n"
            f"This will also delete all associated ingredients and cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                data_dir = self._get_data_dir()
                recipes_file = os.path.join(data_dir, 'recipes.csv')
                ingredients_file = os.path.join(data_dir, 'recipe_ingredients.csv')

                # Remove recipe from dataframe
                self.recipes_df = self.recipes_df[self.recipes_df['recipe_id'] != recipe_id]

                # Remove recipe ingredients
                if 'recipe_ingredients' in self.data:
                    self.data['recipe_ingredients'] = self.data['recipe_ingredients'][
                        self.data['recipe_ingredients']['recipe_id'] != recipe_id
                    ]
                    self.data['recipe_ingredients'].to_csv(ingredients_file, index=False)

                # Save updated recipes
                self.recipes_df.to_csv(recipes_file, index=False)

                # Update data dictionary
                if 'recipes' in self.data:
                    self.data['recipes'] = self.recipes_df

                # Refresh the UI
                self.populate_recipe_table()

                # Clear recipe details
                self.recipe_name_label.setText("")
                self.recipe_category_label.setText("")
                self.recipe_servings_label.setText("")
                self.recipe_time_label.setText("")
                self.recipe_description_label.setText("")
                self.ingredients_table.setRowCount(0)

                # Disable edit and delete buttons
                self.edit_recipe_button.setEnabled(False)
                self.delete_recipe_button.setEnabled(False)

                QMessageBox.information(self, "Success", f"Recipe '{recipe_name}' deleted successfully!")
                logging.info(f"Recipe '{recipe_name}' (ID: {recipe_id}) deleted successfully")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete recipe: {str(e)}")
                logging.error(f"Error deleting recipe: {e}")

    def add_ingredient(self):
        """Add an ingredient to the selected recipe"""
        selected_recipe_items = self.recipe_table.selectedItems()
        if not selected_recipe_items:
            QMessageBox.warning(self, "No Recipe Selected", "Please select a recipe to add ingredients to.")
            return

        # Get the selected recipe
        row = selected_recipe_items[0].row()
        recipe_id = float(self.recipe_table.item(row, 0).text())
        recipe = self.recipes_df[self.recipes_df['recipe_id'] == recipe_id].iloc[0]
        recipe_name = recipe['recipe_name']

        # Open ingredient dialog
        dialog = IngredientDialog(self, data=self.data)
        if dialog.exec():
            ingredient_data = dialog.get_data()
            if ingredient_data:
                try:
                    data_dir = self._get_data_dir()
                    ingredients_file = os.path.join(data_dir, 'recipe_ingredients.csv')

                    # Get next ingredient ID
                    current_max_ingredient_id = 0
                    if 'recipe_ingredients' in self.data and not self.data['recipe_ingredients'].empty:
                        if 'ingredient_id' in self.data['recipe_ingredients'].columns:
                            numeric_ingredient_ids = pd.to_numeric(self.data['recipe_ingredients']['ingredient_id'], errors='coerce').dropna()
                            if not numeric_ingredient_ids.empty:
                                current_max_ingredient_id = numeric_ingredient_ids.max()

                    # Create new ingredient entry
                    new_ingredient = {
                        'recipe_id': recipe_id,
                        'ingredient_id': int(current_max_ingredient_id + 1),
                        'item_name': ingredient_data['item_name'],
                        'quantity': ingredient_data['quantity'],
                        'unit': ingredient_data['unit'],
                        'notes': ingredient_data['notes']
                    }

                    # Add to dataframe
                    new_ingredient_df = pd.DataFrame([new_ingredient])
                    expected_cols = ['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes']

                    # Ensure all columns exist
                    for col in expected_cols:
                        if col not in self.data['recipe_ingredients'].columns:
                            self.data['recipe_ingredients'][col] = pd.NA

                    self.data['recipe_ingredients'] = pd.concat([
                        self.data['recipe_ingredients'],
                        new_ingredient_df[expected_cols]
                    ], ignore_index=True)

                    # Save to CSV
                    self.data['recipe_ingredients'].to_csv(ingredients_file, index=False)

                    # Check if we need to add the ingredient to items.csv
                    if 'category' in ingredient_data and ingredient_data['category']:
                        self._check_and_create_missing_ingredients([ingredient_data])

                    # Refresh the ingredients display
                    self.load_recipe_ingredients(recipe_id)

                    QMessageBox.information(self, "Success",
                                          f"Ingredient '{ingredient_data['item_name']}' added to recipe '{recipe_name}' successfully!")
                    logging.info(f"Added ingredient '{ingredient_data['item_name']}' to recipe '{recipe_name}' (ID: {recipe_id})")

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add ingredient: {str(e)}")
                    logging.error(f"Error adding ingredient: {e}")

    def remove_ingredient(self):
        """Remove the selected ingredient from the recipe"""
        selected_recipe_items = self.recipe_table.selectedItems()
        if not selected_recipe_items:
            QMessageBox.warning(self, "No Recipe Selected", "Please select a recipe first.")
            return

        selected_ingredient_items = self.ingredients_table.selectedItems()
        if not selected_ingredient_items:
            QMessageBox.warning(self, "No Ingredient Selected", "Please select an ingredient to remove.")
            return

        # Get the selected recipe and ingredient
        recipe_row = selected_recipe_items[0].row()
        recipe_id = int(self.recipe_table.item(recipe_row, 0).text())

        ingredient_row = selected_ingredient_items[0].row()
        ingredient_name = self.ingredients_table.item(ingredient_row, 0).text()

        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove '{ingredient_name}' from this recipe?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                data_dir = self._get_data_dir()
                ingredients_file = os.path.join(data_dir, 'recipe_ingredients.csv')

                # Find and remove the ingredient
                recipe_ingredients = self.data['recipe_ingredients'][
                    (self.data['recipe_ingredients']['recipe_id'] == recipe_id) &
                    (self.data['recipe_ingredients']['item_name'] == ingredient_name)
                ]

                if not recipe_ingredients.empty:
                    # Remove the ingredient(s) - there might be multiple entries
                    self.data['recipe_ingredients'] = self.data['recipe_ingredients'][
                        ~((self.data['recipe_ingredients']['recipe_id'] == recipe_id) &
                          (self.data['recipe_ingredients']['item_name'] == ingredient_name))
                    ]

                    # Save to CSV
                    self.data['recipe_ingredients'].to_csv(ingredients_file, index=False)

                    # Refresh the ingredients display
                    self.load_recipe_ingredients(recipe_id)

                    QMessageBox.information(self, "Success",
                                          f"Ingredient '{ingredient_name}' removed successfully!")
                    logging.info(f"Removed ingredient '{ingredient_name}' from recipe ID {recipe_id}")
                else:
                    QMessageBox.warning(self, "Not Found", "Ingredient not found in the recipe.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove ingredient: {str(e)}")
                logging.error(f"Error removing ingredient: {e}")
        
    def record_recipe_sale(self):
        """This method is deprecated - sales should be recorded through the Sales tab"""
        QMessageBox.information(self, "Feature Moved", 
                              "Recipe sales should now be recorded through the Sales tab.\n\n"
                              "This ensures proper inventory management and sales tracking.")
    
    def deduct_ingredients_from_inventory(self, recipe_id, quantity):
        """Deduct the ingredients for a recipe from inventory based on the quantity sold"""
        # This method is now only used by the sales module, not directly from the meal planning tab
        # Check if we have the recipe_ingredients data loaded
        if 'recipe_ingredients' not in self.data:
            logging.error("Recipe ingredients data not available")
            return False
            
        # Filter ingredients for this recipe
        ingredients_df = self.data['recipe_ingredients']
        recipe_ingredients = ingredients_df[ingredients_df['recipe_id'] == recipe_id] if 'recipe_id' in ingredients_df.columns else pd.DataFrame()
        
        if len(recipe_ingredients) == 0:
            logging.error(f"No ingredients found for recipe ID {recipe_id}")
            return False
            
        # Check if we have inventory data
        if 'inventory' not in self.data or len(self.data['inventory']) == 0:
            logging.error("Inventory data not available")
            return False
            
        inventory_df = self.data['inventory'].copy()
        updated_inventory = inventory_df.copy()
        
        # Track if we have enough of all ingredients
        enough_inventory = True
        
        # Check and update each ingredient
        for _, ingredient in recipe_ingredients.iterrows():
            item_name = ingredient['item_name']
            ingredient_qty = float(ingredient['quantity'])
            ingredient_unit = ingredient['unit'].lower() if 'unit' in ingredient else 'g'
            
            # Find this item in inventory
            item_in_inventory = updated_inventory[updated_inventory['item_name'] == item_name]
            
            if len(item_in_inventory) == 0:
                logging.error(f"Item {item_name} not found in inventory")
                enough_inventory = False
                continue
                
            # Get current quantity and unit from inventory
            idx = item_in_inventory.index[0]
            current_qty = 0
            inventory_unit = ''
            
            # Try different column names for quantity
            if 'available_qty' in updated_inventory.columns:
                current_qty = float(updated_inventory.at[idx, 'available_qty']) if pd.notna(updated_inventory.at[idx, 'available_qty']) else 0
            elif 'quantity' in updated_inventory.columns:
                current_qty = float(updated_inventory.at[idx, 'quantity']) if pd.notna(updated_inventory.at[idx, 'quantity']) else 0
            
            # Get unit from inventory
            if 'unit' in updated_inventory.columns:
                inventory_unit = str(updated_inventory.at[idx, 'unit']).lower() if pd.notna(updated_inventory.at[idx, 'unit']) else 'g'
            
            # Convert units if necessary
            required_qty = ingredient_qty * quantity  # Base quantity needed for recipe
            
            # Handle unit conversions
            if ingredient_unit != inventory_unit:
                # Normalize units for better matching
                ingredient_unit_norm = ingredient_unit.lower().strip()
                inventory_unit_norm = inventory_unit.lower().strip()
                
                # Debug log
                logging.info(f"Converting units for {item_name}: {required_qty} {ingredient_unit_norm} to {inventory_unit_norm}")
                
                # Convert between common units
                if ingredient_unit_norm in ['g', 'gram', 'grams'] and inventory_unit_norm in ['kg', 'kilogram', 'kilograms']:
                    # Convert grams to kilograms
                    required_qty = required_qty / 1000
                    logging.info(f"Converted {item_name}: {ingredient_qty * quantity} {ingredient_unit_norm} → {required_qty} {inventory_unit_norm}")
                elif ingredient_unit_norm in ['kg', 'kilogram', 'kilograms'] and inventory_unit_norm in ['g', 'gram', 'grams']:
                    # Convert kilograms to grams
                    required_qty = required_qty * 1000
                    logging.info(f"Converted {item_name}: {ingredient_qty * quantity} {ingredient_unit_norm} → {required_qty} {inventory_unit_norm}")
                elif ingredient_unit_norm in ['ml', 'milliliter', 'milliliters'] and inventory_unit_norm in ['l', 'liter', 'liters']:
                    # Convert milliliters to liters
                    required_qty = required_qty / 1000
                    logging.info(f"Converted {item_name}: {ingredient_qty * quantity} {ingredient_unit_norm} → {required_qty} {inventory_unit_norm}")
                elif ingredient_unit_norm in ['l', 'liter', 'liters'] and inventory_unit_norm in ['ml', 'milliliter', 'milliliters']:
                    # Convert liters to milliliters
                    required_qty = required_qty * 1000
                    logging.info(f"Converted {item_name}: {ingredient_qty * quantity} {ingredient_unit_norm} → {required_qty} {inventory_unit_norm}")
                else:
                    logging.warning(f"Unit conversion not supported: {ingredient_unit_norm} to {inventory_unit_norm} for {item_name}")
                    # If units don't match and we can't convert, log a warning but continue with the quantity as is
            
            # Check if we have enough
            if current_qty < required_qty:
                logging.error(f"Not enough {item_name} in inventory. Need {required_qty} {inventory_unit}, have {current_qty} {inventory_unit}")
                enough_inventory = False
                continue
                
            # Update inventory quantity
            new_qty = current_qty - required_qty
            
            if 'available_qty' in updated_inventory.columns:
                updated_inventory.at[idx, 'available_qty'] = new_qty
            elif 'quantity' in updated_inventory.columns:
                updated_inventory.at[idx, 'quantity'] = new_qty
                
            # Update used quantity if that column exists
            if 'used_qty' in updated_inventory.columns:
                used_qty = float(updated_inventory.at[idx, 'used_qty']) if pd.notna(updated_inventory.at[idx, 'used_qty']) else 0
                updated_inventory.at[idx, 'used_qty'] = used_qty + required_qty
                
        # If we have enough of all ingredients, update the inventory
        if enough_inventory:
            self.data['inventory'] = updated_inventory
            
            # Save to CSV file
            try:
                inventory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                          'data', 'inventory.csv')
                self.data['inventory'].to_csv(inventory_file, index=False)
                logging.info(f"Updated inventory after recipe sale (Recipe ID: {recipe_id}, Quantity: {quantity})")
                return True
            except Exception as e:
                logging.error(f"Error saving inventory data: {e}")
                return False
        else:
            return False
    
    # Note: setup_nutrition_tab and setup_shopping_tab have been removed as requested

def refresh_recipe_data(self):
    """Reload recipe and ingredient data from CSV files and repopulate the recipe table"""
    try:
        # Reload recipes from CSV
        recipes_file = os.path.join(self._get_data_dir(), 'recipes.csv')
        if os.path.exists(recipes_file):
            self.recipes_df = pd.read_csv(recipes_file)
            logging.info(f"Reloaded {len(self.recipes_df)} recipes from {recipes_file}")
        
        # Reload recipe ingredients from CSV
        ingredients_file = os.path.join(self._get_data_dir(), 'recipe_ingredients.csv')
        if os.path.exists(ingredients_file):
            self.data['recipe_ingredients'] = pd.read_csv(ingredients_file)
            logging.info(f"Reloaded {len(self.data['recipe_ingredients'])} recipe ingredients from {ingredients_file}")
        
        # Repopulate the recipe table
        self.populate_recipe_table()
        
        # Clear recipe details
        self.recipe_name_label.setText("")
        self.recipe_category_label.setText("")
        self.recipe_servings_label.setText("")
        self.recipe_time_label.setText("")
        self.recipe_description_label.setText("")
        self.ingredients_table.setRowCount(0)
        
        QMessageBox.information(self, "Refresh Complete", "Recipe data has been refreshed from files.")
    except Exception as e:
        logging.error(f"Error refreshing recipe data: {e}")
        QMessageBox.warning(self, "Refresh Error", f"Failed to refresh recipe data: {str(e)}")

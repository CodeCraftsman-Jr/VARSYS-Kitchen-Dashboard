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
from utils.table_styling import apply_universal_column_resizing
from modules.universal_table_widget import UniversalTableWidget

class BudgetManager(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        # Ensure we have budget data
        if 'budget' in data:
            self.budget_df = data['budget'].copy()
        else:
            self.budget_df = pd.DataFrame(columns=['budget_id', 'category', 'amount', 'period', 'notes'])

        # Ensure we have expense data
        if 'expenses' in data:
            self.expenses_df = data['expenses'].copy()
        else:
            # Try to create expense data from inventory purchases and other sources
            self.expenses_df = self.create_expense_data()
            self.data['expenses'] = self.expenses_df

        # Set up the main layout
        self.layout = QVBoxLayout(self)

        # Create title
        title_label = QLabel("Budget Management")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create tabs for budget management
        self.budget_tab = QWidget()
        self.expenses_tab = QWidget()
        self.analysis_tab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.budget_tab, "Budget Allocation")
        self.tabs.addTab(self.expenses_tab, "Expense Tracking")
        self.tabs.addTab(self.analysis_tab, "Budget Analysis")

        # Set up each tab
        self.setup_budget_tab()
        self.setup_expenses_tab()
        self.setup_analysis_tab()

    def setup_budget_tab(self):
        """Set up the budget allocation tab with new 3-level hierarchy management"""
        layout = QVBoxLayout(self.budget_tab)

        # Header
        header = QLabel("Budget Category Management & Allocation")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Initialize budget categories data structure
        self.initialize_budget_categories()

        # Auto-sync with inventory categories
        self.sync_with_inventory_categories()

        # Add the new category management section (our new UI)
        self.add_category_management_section(layout)

    def add_category_management_section(self, layout):
        """Add budget category hierarchy display section"""
        # Budget Category Hierarchy section
        category_section = QGroupBox("Budget Category Hierarchy")
        category_layout = QVBoxLayout(category_section)

        # Hierarchy display
        hierarchy_label = QLabel("3-Level Budget Category Structure:")
        hierarchy_label.setFont(QFont("Arial", 11, QFont.Bold))
        category_layout.addWidget(hierarchy_label)

        # Category hierarchy table
        self.hierarchy_table = QTableWidget()
        self.hierarchy_table.setColumnCount(4)
        self.hierarchy_table.setHorizontalHeaderLabels(["Category", "Type", "Budget", "Spent"])
        self.hierarchy_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.hierarchy_table.verticalHeader().setVisible(False)
        self.hierarchy_table.setMinimumHeight(600)  # Increased minimum height
        self.hierarchy_table.setMaximumHeight(800)  # Increased maximum height

        # Apply column resizing
        hierarchy_default_widths = {
            0: 250,  # Category (with indentation)
            1: 100,  # Type
            2: 120,  # Budget
            3: 120   # Spent
        }

        self.hierarchy_resizer = apply_universal_column_resizing(
            self.hierarchy_table,
            'budget_hierarchy_settings.json',
            hierarchy_default_widths
        )

        # Enable sorting functionality for budget hierarchy table (regular table - remove duplicates)
        self.hierarchy_table.setSortingEnabled(True)
        self.hierarchy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        category_layout.addWidget(self.hierarchy_table)

        # Edit category section
        edit_group = QGroupBox("Edit Selected Category")
        edit_layout = QHBoxLayout(edit_group)

        # Edit button
        self.edit_category_btn = QPushButton("Edit Selected Category")
        self.edit_category_btn.clicked.connect(self.edit_selected_category)
        self.edit_category_btn.setEnabled(False)  # Disabled until selection
        edit_layout.addWidget(self.edit_category_btn)

        # Delete button
        self.delete_category_btn = QPushButton("Delete Selected Category")
        self.delete_category_btn.clicked.connect(self.delete_selected_category)
        self.delete_category_btn.setEnabled(False)  # Disabled until selection
        edit_layout.addWidget(self.delete_category_btn)

        edit_layout.addStretch()
        category_layout.addWidget(edit_group)

        # Connect selection change to enable/disable edit buttons
        self.hierarchy_table.itemSelectionChanged.connect(self.on_hierarchy_selection_changed)

        # Budget allocation section (more compact)
        allocation_group = QGroupBox("Budget Allocation")
        allocation_layout = QHBoxLayout(allocation_group)  # Changed to horizontal layout

        # Main category selection for budget allocation
        allocation_layout.addWidget(QLabel("Category:"))
        self.budget_category_combo = QComboBox()
        self.budget_category_combo.setPlaceholderText("Select main category...")
        self.budget_category_combo.setMinimumWidth(200)
        allocation_layout.addWidget(self.budget_category_combo)

        # Budget amount input
        allocation_layout.addWidget(QLabel("Budget:"))
        self.budget_amount_spin = QDoubleSpinBox()
        self.budget_amount_spin.setRange(0, 9999999)
        self.budget_amount_spin.setPrefix("₹")
        self.budget_amount_spin.setValue(0)
        self.budget_amount_spin.setMinimumWidth(150)
        allocation_layout.addWidget(self.budget_amount_spin)

        # Update budget button
        self.update_budget_btn = QPushButton("Update Budget")
        self.update_budget_btn.clicked.connect(self.update_budget_allocation)
        allocation_layout.addWidget(self.update_budget_btn)

        allocation_layout.addStretch()  # Add stretch to push everything to the left
        category_layout.addWidget(allocation_group)

        # Add new main category section (more compact)
        add_category_group = QGroupBox("Add New Main Category")
        add_category_layout = QHBoxLayout(add_category_group)  # Changed to horizontal layout

        # New category name input
        add_category_layout.addWidget(QLabel("Name:"))
        self.new_category_name = QLineEdit()
        self.new_category_name.setPlaceholderText("Category name...")
        self.new_category_name.setMinimumWidth(150)
        add_category_layout.addWidget(self.new_category_name)

        # New category budget input
        add_category_layout.addWidget(QLabel("Budget:"))
        self.new_category_budget = QDoubleSpinBox()
        self.new_category_budget.setRange(0, 9999999)
        self.new_category_budget.setPrefix("₹")
        self.new_category_budget.setValue(0)
        self.new_category_budget.setMinimumWidth(120)
        add_category_layout.addWidget(self.new_category_budget)

        # New category description input
        add_category_layout.addWidget(QLabel("Description:"))
        self.new_category_description = QLineEdit()
        self.new_category_description.setPlaceholderText("Optional...")
        self.new_category_description.setMinimumWidth(120)
        add_category_layout.addWidget(self.new_category_description)

        # Add category button
        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_new_main_category)
        add_category_layout.addWidget(self.add_category_btn)

        add_category_layout.addStretch()  # Add stretch to push everything to the left
        category_layout.addWidget(add_category_group)

        # Add new sub-category section
        add_sub_category_group = QGroupBox("Add New Sub-Category")
        add_sub_category_layout = QHBoxLayout(add_sub_category_group)

        # Parent category selection
        add_sub_category_layout.addWidget(QLabel("Parent:"))
        self.parent_category_combo = QComboBox()
        self.parent_category_combo.setPlaceholderText("Select parent category...")
        self.parent_category_combo.setMinimumWidth(150)
        add_sub_category_layout.addWidget(self.parent_category_combo)

        # Sub-category name input
        add_sub_category_layout.addWidget(QLabel("Sub-Category:"))
        self.new_sub_category_name = QLineEdit()
        self.new_sub_category_name.setPlaceholderText("Sub-category name...")
        self.new_sub_category_name.setMinimumWidth(150)
        add_sub_category_layout.addWidget(self.new_sub_category_name)

        # Sub-category description input
        add_sub_category_layout.addWidget(QLabel("Description:"))
        self.new_sub_category_description = QLineEdit()
        self.new_sub_category_description.setPlaceholderText("Optional...")
        self.new_sub_category_description.setMinimumWidth(120)
        add_sub_category_layout.addWidget(self.new_sub_category_description)

        # Add sub-category button
        self.add_sub_category_btn = QPushButton("Add Sub-Category")
        self.add_sub_category_btn.clicked.connect(self.add_new_sub_category)
        add_sub_category_layout.addWidget(self.add_sub_category_btn)

        add_sub_category_layout.addStretch()
        category_layout.addWidget(add_sub_category_group)

        # Info labels (more compact)
        info_group = QGroupBox("Current Structure")
        info_layout = QHBoxLayout(info_group)

        info_text = QLabel("📋 Kitchen Essentials → All inventory items  |  🔧 Maintenance → Repairing, Spares  |  ⛽ Gas → Indian/HP/Local Gas")
        info_text.setStyleSheet("color: #666; font-size: 10px;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        category_layout.addWidget(info_group)
        layout.addWidget(category_section)

        # Initialize data
        self.populate_budget_hierarchy()
        self.populate_budget_category_combo()
        self.populate_parent_category_combo()
        self.populate_expense_main_categories()

    def populate_budget_hierarchy(self):
        """Populate the budget hierarchy table with 3-level structure"""
        try:
            self.hierarchy_table.setRowCount(0)

            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return

            # Get main categories first
            main_categories = self.budget_categories_df[
                self.budget_categories_df['category_type'] == 'Parent'
            ].sort_values('category_id')

            row = 0
            for _, main_cat in main_categories.iterrows():
                # Add main category row
                self.hierarchy_table.setRowCount(row + 1)

                # Main category name (bold)
                main_name_item = QTableWidgetItem(f"📁 {main_cat['category_name']}")
                main_name_item.setFont(QFont("Arial", 10, QFont.Bold))
                self.hierarchy_table.setItem(row, 0, main_name_item)

                # Type
                type_item = QTableWidgetItem("Main")
                self.hierarchy_table.setItem(row, 1, type_item)

                # Budget
                budget_amount = float(main_cat.get('budget_amount', 0))
                budget_item = QTableWidgetItem(f"₹{budget_amount:,.2f}")
                self.hierarchy_table.setItem(row, 2, budget_item)

                # Spent
                spent_amount = float(main_cat.get('spent_amount', 0))
                spent_item = QTableWidgetItem(f"₹{spent_amount:,.2f}")
                self.hierarchy_table.setItem(row, 3, spent_item)

                row += 1

                # Add sub-categories
                sub_categories = self.budget_categories_df[
                    (self.budget_categories_df['category_type'] == 'Child') &
                    (self.budget_categories_df['parent_id'] == main_cat['category_id'])
                ].sort_values('category_name')

                for _, sub_cat in sub_categories.iterrows():
                    self.hierarchy_table.setRowCount(row + 1)

                    # Sub-category name (indented)
                    sub_name_item = QTableWidgetItem(f"    └─ {sub_cat['category_name']}")
                    self.hierarchy_table.setItem(row, 0, sub_name_item)

                    # Type
                    sub_type_item = QTableWidgetItem("Sub")
                    self.hierarchy_table.setItem(row, 1, sub_type_item)

                    # Budget (inherited from parent)
                    sub_budget_item = QTableWidgetItem("—")
                    self.hierarchy_table.setItem(row, 2, sub_budget_item)

                    # Spent
                    sub_spent_amount = float(sub_cat.get('spent_amount', 0))
                    sub_spent_item = QTableWidgetItem(f"₹{sub_spent_amount:,.2f}")
                    self.hierarchy_table.setItem(row, 3, sub_spent_item)

                    row += 1

        except Exception as e:
            logging.error(f"Error populating budget hierarchy: {e}")

    def populate_budget_category_combo(self):
        """Populate the budget category combo with main categories"""
        try:
            self.budget_category_combo.clear()

            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return

            # Get main categories
            main_categories = self.budget_categories_df[
                self.budget_categories_df['category_type'] == 'Parent'
            ]['category_name'].sort_values()

            self.budget_category_combo.addItems(main_categories.tolist())

        except Exception as e:
            logging.error(f"Error populating budget category combo: {e}")

    def update_budget_allocation(self):
        """Update budget allocation for selected main category"""
        try:
            category_name = self.budget_category_combo.currentText()
            budget_amount = self.budget_amount_spin.value()

            if not category_name:
                QMessageBox.warning(self, "Selection Error", "Please select a main category.")
                return

            if budget_amount <= 0:
                QMessageBox.warning(self, "Input Error", "Please enter a valid budget amount.")
                return

            # Update budget amount in dataframe
            category_mask = (
                (self.budget_categories_df['category_name'] == category_name) &
                (self.budget_categories_df['category_type'] == 'Parent')
            )

            if not category_mask.any():
                QMessageBox.warning(self, "Error", f"Category '{category_name}' not found.")
                return

            self.budget_categories_df.loc[category_mask, 'budget_amount'] = budget_amount

            # Save to file
            self.save_budget_categories()

            # Refresh displays
            self.populate_budget_hierarchy()
            self.populate_budget_table()

            # Reset form
            self.budget_amount_spin.setValue(0)

            QMessageBox.information(self, "Budget Updated",
                                  f"Budget for '{category_name}' updated to ₹{budget_amount:,.2f}")

        except Exception as e:
            logging.error(f"Error updating budget allocation: {e}")
            QMessageBox.warning(self, "Error", f"Error updating budget: {e}")

    def add_new_main_category(self):
        """Add a new main budget category"""
        try:
            category_name = self.new_category_name.text().strip()
            budget_amount = self.new_category_budget.value()
            description = self.new_category_description.text().strip()

            if not category_name:
                QMessageBox.warning(self, "Input Error", "Please enter a category name.")
                return

            if budget_amount <= 0:
                QMessageBox.warning(self, "Input Error", "Please enter a valid budget amount.")
                return

            # Check if category already exists
            if hasattr(self, 'budget_categories_df') and len(self.budget_categories_df) > 0:
                existing_categories = self.budget_categories_df[
                    self.budget_categories_df['category_type'] == 'Parent'
                ]['category_name'].str.lower()
                if category_name.lower() in existing_categories.values:
                    QMessageBox.warning(self, "Category Exists", f"Category '{category_name}' already exists.")
                    return

            # Get next category ID
            if hasattr(self, 'budget_categories_df') and len(self.budget_categories_df) > 0:
                next_id = self.budget_categories_df['category_id'].max() + 1
            else:
                next_id = 1

            # Create new category
            new_category = pd.DataFrame({
                'category_id': [next_id],
                'category_name': [category_name],
                'category_type': ['Parent'],
                'parent_id': [''],
                'budget_amount': [budget_amount],
                'spent_amount': [0.0],
                'description': [description if description else f"Main budget category for {category_name}"]
            })

            # Add to dataframe
            if hasattr(self, 'budget_categories_df') and len(self.budget_categories_df) > 0:
                self.budget_categories_df = pd.concat([self.budget_categories_df, new_category], ignore_index=True)
            else:
                self.budget_categories_df = new_category

            # Save to file
            self.save_budget_categories()

            # Refresh displays
            self.populate_budget_hierarchy()
            self.populate_budget_category_combo()
            self.populate_parent_category_combo()
            self.populate_budget_table()

            # Clear form
            self.new_category_name.clear()
            self.new_category_budget.setValue(0)
            self.new_category_description.clear()

            QMessageBox.information(self, "Category Added",
                                  f"Main category '{category_name}' added successfully with budget of ₹{budget_amount:,.2f}")

        except Exception as e:
            logging.error(f"Error adding new main category: {e}")
            QMessageBox.warning(self, "Error", f"Error adding category: {e}")

    def add_new_sub_category(self):
        """Add a new sub-category under a selected main category"""
        try:
            parent_category_name = self.parent_category_combo.currentText()
            sub_category_name = self.new_sub_category_name.text().strip()
            description = self.new_sub_category_description.text().strip()

            if not parent_category_name:
                QMessageBox.warning(self, "Selection Error", "Please select a parent category.")
                return

            if not sub_category_name:
                QMessageBox.warning(self, "Input Error", "Please enter a sub-category name.")
                return

            # Find parent category ID
            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                QMessageBox.warning(self, "Error", "No parent categories found.")
                return

            parent_category = self.budget_categories_df[
                (self.budget_categories_df['category_name'] == parent_category_name) &
                (self.budget_categories_df['category_type'] == 'Parent')
            ]

            if len(parent_category) == 0:
                QMessageBox.warning(self, "Error", f"Parent category '{parent_category_name}' not found.")
                return

            parent_id = parent_category.iloc[0]['category_id']

            # Check if sub-category already exists under this parent
            existing_sub_categories = self.budget_categories_df[
                (self.budget_categories_df['category_type'] == 'Child') &
                (self.budget_categories_df['parent_id'] == parent_id)
            ]['category_name'].str.lower()

            if sub_category_name.lower() in existing_sub_categories.values:
                QMessageBox.warning(self, "Category Exists",
                                  f"Sub-category '{sub_category_name}' already exists under '{parent_category_name}'.")
                return

            # Get next category ID
            next_id = self.budget_categories_df['category_id'].max() + 1

            # Create new sub-category
            new_sub_category = pd.DataFrame({
                'category_id': [next_id],
                'category_name': [sub_category_name],
                'category_type': ['Child'],
                'parent_id': [parent_id],
                'budget_amount': [0.0],  # Sub-categories inherit from parent
                'spent_amount': [0.0],
                'description': [description if description else f"Sub-category under {parent_category_name}"]
            })

            # Add to dataframe
            self.budget_categories_df = pd.concat([self.budget_categories_df, new_sub_category], ignore_index=True)

            # Save to file
            self.save_budget_categories()

            # Refresh displays
            self.populate_budget_hierarchy()
            self.populate_budget_category_combo()
            self.populate_parent_category_combo()
            self.populate_budget_table()

            # Clear form
            self.new_sub_category_name.clear()
            self.new_sub_category_description.clear()

            QMessageBox.information(self, "Sub-Category Added",
                                  f"Sub-category '{sub_category_name}' added successfully under '{parent_category_name}'")

        except Exception as e:
            logging.error(f"Error adding new sub-category: {e}")
            QMessageBox.warning(self, "Error", f"Error adding sub-category: {e}")

    def populate_parent_category_combo(self):
        """Populate the parent category combo with main categories for sub-category creation"""
        try:
            self.parent_category_combo.clear()

            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return

            # Get main categories
            main_categories = self.budget_categories_df[
                self.budget_categories_df['category_type'] == 'Parent'
            ]['category_name'].sort_values()

            self.parent_category_combo.addItems(main_categories.tolist())

        except Exception as e:
            logging.error(f"Error populating parent category combo: {e}")

    def on_hierarchy_selection_changed(self):
        """Handle selection changes in the hierarchy table"""
        try:
            selected_items = self.hierarchy_table.selectedItems()
            has_selection = len(selected_items) > 0

            # Enable/disable edit and delete buttons based on selection
            self.edit_category_btn.setEnabled(has_selection)
            self.delete_category_btn.setEnabled(has_selection)

        except Exception as e:
            logging.error(f"Error handling hierarchy selection change: {e}")

    def edit_selected_category(self):
        """Edit the selected category in the hierarchy table"""
        try:
            selected_items = self.hierarchy_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a category to edit.")
                return

            # Get the selected row
            row = selected_items[0].row()
            category_name_item = self.hierarchy_table.item(row, 0)
            category_type_item = self.hierarchy_table.item(row, 1)

            if not category_name_item or not category_type_item:
                QMessageBox.warning(self, "Invalid Selection", "Please select a valid category.")
                return

            # Extract category name (remove tree symbols)
            category_name = category_name_item.text().replace("📁 ", "").replace("    └─ ", "").strip()
            category_type = category_type_item.text()

            # Find the category in the dataframe
            if category_type == "Main":
                category_data = self.budget_categories_df[
                    (self.budget_categories_df['category_name'] == category_name) &
                    (self.budget_categories_df['category_type'] == 'Parent')
                ]
            else:  # Sub category
                category_data = self.budget_categories_df[
                    (self.budget_categories_df['category_name'] == category_name) &
                    (self.budget_categories_df['category_type'] == 'Child')
                ]

            if len(category_data) == 0:
                QMessageBox.warning(self, "Category Not Found", f"Category '{category_name}' not found in database.")
                return

            # Open edit dialog
            self.open_edit_category_dialog(category_data.iloc[0], category_type)

        except Exception as e:
            logging.error(f"Error editing selected category: {e}")
            QMessageBox.warning(self, "Error", f"Error editing category: {e}")

    def delete_selected_category(self):
        """Delete the selected category from the hierarchy table"""
        try:
            selected_items = self.hierarchy_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a category to delete.")
                return

            # Get the selected row
            row = selected_items[0].row()
            category_name_item = self.hierarchy_table.item(row, 0)
            category_type_item = self.hierarchy_table.item(row, 1)

            if not category_name_item or not category_type_item:
                QMessageBox.warning(self, "Invalid Selection", "Please select a valid category.")
                return

            # Extract category name (remove tree symbols)
            category_name = category_name_item.text().replace("📁 ", "").replace("    └─ ", "").strip()
            category_type = category_type_item.text()

            # Confirm deletion
            reply = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete the {category_type.lower()} category '{category_name}'?\n\n"
                                       f"This action cannot be undone.",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply != QMessageBox.Yes:
                return

            # Delete the category
            if category_type == "Main":
                # Delete main category and all its sub-categories
                main_category = self.budget_categories_df[
                    (self.budget_categories_df['category_name'] == category_name) &
                    (self.budget_categories_df['category_type'] == 'Parent')
                ]

                if len(main_category) > 0:
                    main_category_id = main_category.iloc[0]['category_id']

                    # Remove all sub-categories first
                    self.budget_categories_df = self.budget_categories_df[
                        ~((self.budget_categories_df['category_type'] == 'Child') &
                          (self.budget_categories_df['parent_id'] == main_category_id))
                    ]

                    # Remove main category
                    self.budget_categories_df = self.budget_categories_df[
                        ~((self.budget_categories_df['category_name'] == category_name) &
                          (self.budget_categories_df['category_type'] == 'Parent'))
                    ]
            else:  # Sub category
                # Delete only the sub-category
                self.budget_categories_df = self.budget_categories_df[
                    ~((self.budget_categories_df['category_name'] == category_name) &
                      (self.budget_categories_df['category_type'] == 'Child'))
                ]

            # Save changes
            self.save_budget_categories()

            # Refresh displays
            self.populate_budget_hierarchy()
            self.populate_budget_category_combo()
            self.populate_parent_category_combo()

            QMessageBox.information(self, "Category Deleted",
                                  f"{category_type} category '{category_name}' has been deleted successfully.")

        except Exception as e:
            logging.error(f"Error deleting selected category: {e}")
            QMessageBox.warning(self, "Error", f"Error deleting category: {e}")

    def open_edit_category_dialog(self, category_data, category_type):
        """Open a dialog to edit category details"""
        try:
            from PySide6.QtWidgets import QDialog, QDialogButtonBox

            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit {category_type} Category")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # Form for editing
            form_group = QGroupBox(f"Edit {category_type} Category Details")
            form_layout = QFormLayout(form_group)

            # Category name
            name_edit = QLineEdit()
            name_edit.setText(str(category_data['category_name']))
            form_layout.addRow("Category Name:", name_edit)

            # Description
            description_edit = QLineEdit()
            description_edit.setText(str(category_data.get('description', '')))
            form_layout.addRow("Description:", description_edit)

            # Budget amount (only for main categories)
            budget_edit = None
            if category_type == "Main":
                budget_edit = QDoubleSpinBox()
                budget_edit.setRange(0, 9999999)
                budget_edit.setPrefix("₹")
                budget_edit.setValue(float(category_data.get('budget_amount', 0)))
                form_layout.addRow("Budget Amount:", budget_edit)

            layout.addWidget(form_group)

            # Dialog buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            # Show dialog and handle result
            if dialog.exec() == QDialog.Accepted:
                # Get updated values
                new_name = name_edit.text().strip()
                new_description = description_edit.text().strip()
                new_budget = budget_edit.value() if budget_edit else None

                # Validate
                if not new_name:
                    QMessageBox.warning(self, "Invalid Input", "Category name cannot be empty.")
                    return

                # Check for duplicate names (if name changed)
                if new_name != category_data['category_name']:
                    if category_type == "Main":
                        existing = self.budget_categories_df[
                            (self.budget_categories_df['category_name'] == new_name) &
                            (self.budget_categories_df['category_type'] == 'Parent')
                        ]
                    else:
                        existing = self.budget_categories_df[
                            (self.budget_categories_df['category_name'] == new_name) &
                            (self.budget_categories_df['category_type'] == 'Child') &
                            (self.budget_categories_df['parent_id'] == category_data['parent_id'])
                        ]

                    if len(existing) > 0:
                        QMessageBox.warning(self, "Duplicate Name",
                                          f"A category with the name '{new_name}' already exists.")
                        return

                # Update the category
                category_id = category_data['category_id']
                mask = self.budget_categories_df['category_id'] == category_id

                self.budget_categories_df.loc[mask, 'category_name'] = new_name
                self.budget_categories_df.loc[mask, 'description'] = new_description

                if budget_edit and category_type == "Main":
                    self.budget_categories_df.loc[mask, 'budget_amount'] = new_budget

                # Save changes
                self.save_budget_categories()

                # Refresh displays
                self.populate_budget_hierarchy()
                self.populate_budget_category_combo()
                self.populate_parent_category_combo()

                QMessageBox.information(self, "Category Updated",
                                      f"{category_type} category updated successfully.")

        except Exception as e:
            logging.error(f"Error opening edit category dialog: {e}")
            QMessageBox.warning(self, "Error", f"Error opening edit dialog: {e}")

    def populate_expense_main_categories(self):
        """Populate the main category dropdown for expense tracking"""
        try:
            self.expense_main_category.clear()

            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return

            # Get main categories
            main_categories = self.budget_categories_df[
                self.budget_categories_df['category_type'] == 'Parent'
            ]['category_name'].sort_values()

            self.expense_main_category.addItems(main_categories.tolist())

        except Exception as e:
            logging.error(f"Error populating expense main categories: {e}")

    def on_expense_main_category_changed(self, main_category_name):
        """Handle main category selection change in expense form"""
        try:
            self.expense_sub_category.clear()
            self.expense_sub_category.setEnabled(False)

            if not main_category_name or not hasattr(self, 'budget_categories_df'):
                return

            # Find the main category
            main_category = self.budget_categories_df[
                (self.budget_categories_df['category_name'] == main_category_name) &
                (self.budget_categories_df['category_type'] == 'Parent')
            ]

            if len(main_category) == 0:
                return

            main_category_id = main_category.iloc[0]['category_id']

            # Get sub-categories for this main category
            sub_categories = self.budget_categories_df[
                (self.budget_categories_df['category_type'] == 'Child') &
                (self.budget_categories_df['parent_id'] == main_category_id)
            ]['category_name'].sort_values()

            if len(sub_categories) > 0:
                self.expense_sub_category.addItems(sub_categories.tolist())
                self.expense_sub_category.setEnabled(True)
            else:
                # If no sub-categories, add a default option
                self.expense_sub_category.addItem("General")
                self.expense_sub_category.setEnabled(True)

        except Exception as e:
            logging.error(f"Error handling expense main category change: {e}")

    def sync_with_inventory_categories(self):
        """Ensure ALL inventory categories appear as sub-categories under Kitchen Essentials"""
        try:
            # Get inventory categories
            if 'categories' not in self.data:
                logging.warning("No inventory categories found to sync")
                return

            inventory_categories_df = self.data['categories']
            if len(inventory_categories_df) == 0:
                return

            # Get Kitchen Essentials category ID (should be 1 based on our structure)
            kitchen_essentials_id = 1

            # Get current child categories under Kitchen Essentials
            existing_children = set()
            if hasattr(self, 'budget_categories_df') and len(self.budget_categories_df) > 0:
                children = self.budget_categories_df[
                    (self.budget_categories_df['category_type'] == 'Child') &
                    (self.budget_categories_df['parent_id'] == kitchen_essentials_id)
                ]
                existing_children = set(children['category_name'].values)

            # Get all inventory category names
            inventory_category_names = set(inventory_categories_df['category_name'].values)

            # Find missing categories that need to be added
            missing_categories = inventory_category_names - existing_children

            # Find extra categories that should be removed (if inventory category was deleted)
            extra_categories = existing_children - inventory_category_names

            # Remove extra categories
            if extra_categories and hasattr(self, 'budget_categories_df'):
                for extra_cat in extra_categories:
                    mask = (
                        (self.budget_categories_df['category_name'] == extra_cat) &
                        (self.budget_categories_df['category_type'] == 'Child') &
                        (self.budget_categories_df['parent_id'] == kitchen_essentials_id)
                    )
                    self.budget_categories_df = self.budget_categories_df[~mask]
                    logging.info(f"Removed obsolete category: {extra_cat}")

            # Add missing categories
            if missing_categories:
                new_categories = []
                next_id = self.budget_categories_df['category_id'].max() + 1 if hasattr(self, 'budget_categories_df') and len(self.budget_categories_df) > 0 else 28

                for category_name in missing_categories:
                    # Get description from inventory categories
                    inv_cat_row = inventory_categories_df[
                        inventory_categories_df['category_name'] == category_name
                    ]
                    description = inv_cat_row.iloc[0]['description'] if len(inv_cat_row) > 0 else category_name

                    # Create child category under Kitchen Essentials
                    new_category = {
                        'category_id': next_id,
                        'category_name': category_name,
                        'category_type': 'Child',
                        'parent_id': kitchen_essentials_id,
                        'budget_amount': 0.0,
                        'spent_amount': 0.0,
                        'description': description
                    }
                    new_categories.append(new_category)
                    next_id += 1

                # Add new categories to budget_categories_df
                if new_categories:
                    new_categories_df = pd.DataFrame(new_categories)
                    if hasattr(self, 'budget_categories_df') and len(self.budget_categories_df) > 0:
                        self.budget_categories_df = pd.concat([self.budget_categories_df, new_categories_df], ignore_index=True)
                    else:
                        self.budget_categories_df = new_categories_df

                    logging.info(f"Added {len(new_categories)} new inventory categories under Kitchen Essentials")

            # Save changes if any were made
            if missing_categories or extra_categories:
                self.save_budget_categories()
                # Refresh displays
                if hasattr(self, 'populate_budget_hierarchy'):
                    self.populate_budget_hierarchy()
                if hasattr(self, 'populate_budget_table'):
                    self.populate_budget_table()

                logging.info("Inventory-Kitchen Essentials sync completed")

        except Exception as e:
            logging.error(f"Error syncing with inventory categories: {e}")

    def get_subcategories_for_main_category(self, main_category_name):
        """Get all sub-categories (inventory categories) for a given main budget category"""
        try:
            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return []

            # Find the main category
            main_category = self.budget_categories_df[
                (self.budget_categories_df['category_name'] == main_category_name) &
                (self.budget_categories_df['category_type'] == 'Parent')
            ]

            if len(main_category) == 0:
                return []

            main_category_id = main_category.iloc[0]['category_id']

            # Get child categories
            child_categories = self.budget_categories_df[
                (self.budget_categories_df['category_type'] == 'Child') &
                (self.budget_categories_df['parent_id'] == main_category_id)
            ]

            return child_categories['category_name'].tolist()

        except Exception as e:
            logging.error(f"Error getting sub-categories for {main_category_name}: {e}")
            return []

    def get_main_budget_categories(self):
        """Get list of all main budget categories"""
        try:
            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return []

            main_categories = self.budget_categories_df[
                self.budget_categories_df['category_type'] == 'Parent'
            ]

            return main_categories['category_name'].tolist()

        except Exception as e:
            logging.error(f"Error getting main budget categories: {e}")
            return []

    def update_budget_spending(self, budget_category, amount):
        """Update spending amount for a budget category"""
        try:
            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return False

            # Find the budget category
            category_mask = (
                (self.budget_categories_df['category_name'] == budget_category) &
                (self.budget_categories_df['category_type'] == 'Parent')
            )

            if not category_mask.any():
                logging.warning(f"Budget category '{budget_category}' not found")
                return False

            # Update spent amount
            current_spent = float(self.budget_categories_df.loc[category_mask, 'spent_amount'].iloc[0])
            new_spent = current_spent + float(amount)
            self.budget_categories_df.loc[category_mask, 'spent_amount'] = new_spent

            # Save to file
            self.save_budget_categories()

            # Refresh displays
            self.populate_budget_hierarchy()
            self.populate_budget_table()

            logging.info(f"Updated spending for '{budget_category}': +₹{amount:,.2f} (Total: ₹{new_spent:,.2f})")
            return True

        except Exception as e:
            logging.error(f"Error updating budget spending: {e}")
            return False

    def get_budget_status(self, budget_category):
        """Get budget status for a category (allocated, spent, remaining)"""
        try:
            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return None

            # Find the budget category
            category_mask = (
                (self.budget_categories_df['category_name'] == budget_category) &
                (self.budget_categories_df['category_type'] == 'Parent')
            )

            if not category_mask.any():
                return None

            category_row = self.budget_categories_df.loc[category_mask].iloc[0]
            allocated = float(category_row['budget_amount'])
            spent = float(category_row['spent_amount'])
            remaining = allocated - spent

            return {
                'category': budget_category,
                'allocated': allocated,
                'spent': spent,
                'remaining': remaining,
                'percentage_used': (spent / allocated * 100) if allocated > 0 else 0
            }

        except Exception as e:
            logging.error(f"Error getting budget status: {e}")
            return None

    def get_all_budget_status(self):
        """Get budget status for all main categories"""
        try:
            main_categories = self.get_main_budget_categories()
            status_list = []

            for category in main_categories:
                status = self.get_budget_status(category)
                if status:
                    status_list.append(status)

            return status_list

        except Exception as e:
            logging.error(f"Error getting all budget status: {e}")
            return []

    def setup_expenses_tab(self):
        """Set up the expense tracking tab"""
        layout = QVBoxLayout(self.expenses_tab)

        # Header
        header = QLabel("Expense Tracking")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Expense table with universal filtering and sorting
        expense_columns = ["Date", "Main Category", "Sub Category", "Amount", "Source", "Notes"]
        self.expense_table_widget = UniversalTableWidget(
            data=self.expenses_df if hasattr(self, 'expenses_df') else pd.DataFrame(),
            columns=expense_columns,
            parent=self,
            is_history_table=True  # Expense tracking is a history table - preserve all records
        )

        # Connect signals for row selection
        self.expense_table_widget.row_selected.connect(self.on_expense_row_selected)

        print("✅ Applied universal column resizing to expense table")
        layout.addWidget(self.expense_table_widget)

        # Populate expense table
        self.populate_expense_table()

        # Form for adding expenses
        form_group = QGroupBox("Add Expense")
        form_layout = QFormLayout(form_group)

        # Date picker
        self.expense_date = QDateEdit()
        self.expense_date.setDate(QDate.currentDate())
        self.expense_date.setCalendarPopup(True)

        # Main category selection
        self.expense_main_category = QComboBox()
        self.expense_main_category.setPlaceholderText("Select main category...")
        self.populate_expense_main_categories()
        self.expense_main_category.currentTextChanged.connect(self.on_expense_main_category_changed)

        # Sub-category selection
        self.expense_sub_category = QComboBox()
        self.expense_sub_category.setPlaceholderText("Select sub-category...")
        self.expense_sub_category.setEnabled(False)  # Disabled until main category is selected

        # Amount field
        self.expense_amount = QDoubleSpinBox()
        self.expense_amount.setMinimum(0)
        self.expense_amount.setMaximum(1000000)
        self.expense_amount.setSingleStep(10)
        self.expense_amount.setPrefix("₹ ")  # Default currency symbol

        # Source field
        self.expense_source = QComboBox()
        self.expense_source.addItems(["Inventory Purchase", "Utilities", "Maintenance", "Salaries", "Other"])
        self.expense_source.setEditable(True)

        # Notes field
        self.expense_notes = QLineEdit()
        self.expense_notes.setPlaceholderText("Enter any notes about this expense...")

        # Add fields to form
        form_layout.addRow("Date:", self.expense_date)
        form_layout.addRow("Main Category:", self.expense_main_category)
        form_layout.addRow("Sub Category:", self.expense_sub_category)
        form_layout.addRow("Amount:", self.expense_amount)
        form_layout.addRow("Source:", self.expense_source)
        form_layout.addRow("Notes:", self.expense_notes)

        # Add expense button
        add_expense_btn = QPushButton("Add Expense")
        add_expense_btn.clicked.connect(self.add_expense)
        form_layout.addRow("", add_expense_btn)

        layout.addWidget(form_group)

    def setup_analysis_tab(self):
        """Set up the budget analysis tab"""
        layout = QVBoxLayout(self.analysis_tab)

        # Header
        header = QLabel("Budget Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Create charts for budget analysis
        self.create_budget_charts(layout)

    def populate_budget_table(self):
        """Populate the budget table with data"""
        self.budget_table.setRowCount(0)  # Clear existing rows

        if len(self.budget_df) == 0:
            return

        # Add budgets to the table
        for i, (_, budget) in enumerate(self.budget_df.iterrows()):
            self.budget_table.insertRow(i)

            # Add budget data
            id_item = QTableWidgetItem(str(budget['budget_id']) if 'budget_id' in budget else str(i+1))
            category_item = QTableWidgetItem(str(budget['category']) if 'category' in budget else "")

            # Format amount with currency symbol
            amount = float(budget['amount']) if 'amount' in budget and pd.notna(budget['amount']) else 0
            amount_item = QTableWidgetItem(f"₹ {amount:.2f}")

            period_item = QTableWidgetItem(str(budget['period']) if 'period' in budget else "Monthly")

            self.budget_table.setItem(i, 0, id_item)
            self.budget_table.setItem(i, 1, category_item)
            self.budget_table.setItem(i, 2, amount_item)
            self.budget_table.setItem(i, 3, period_item)

    def populate_expense_table(self):
        """Populate the expense table with hierarchical category data using universal table widget"""
        try:
            if len(self.expenses_df) == 0:
                # Update with empty dataframe
                self.expense_table_widget.update_data(pd.DataFrame())
                return

            # Prepare data for universal table widget
            display_data = self.expenses_df.copy()

            # Ensure all required columns exist
            required_columns = ['date', 'main_category', 'sub_category', 'amount', 'source', 'notes']
            for col in required_columns:
                if col not in display_data.columns:
                    if col == 'main_category' and 'category' in display_data.columns:
                        display_data['main_category'] = display_data['category']
                    elif col == 'sub_category':
                        display_data['sub_category'] = 'General'
                    else:
                        display_data[col] = ''

            # Format amount column with currency
            if 'amount' in display_data.columns:
                display_data['amount'] = display_data['amount'].apply(
                    lambda x: f"₹ {float(x):.2f}" if pd.notna(x) else "₹ 0.00"
                )

            # Reorder columns to match expected layout
            column_order = ['date', 'main_category', 'sub_category', 'amount', 'source', 'notes']
            display_data = display_data.reindex(columns=column_order, fill_value='')

            # Update the universal table widget
            self.expense_table_widget.update_data(display_data)
            print(f"✅ Updated expense table with {len(display_data)} entries")

        except Exception as e:
            print(f"❌ Error populating expense table: {e}")
            self.expense_table_widget.update_data(pd.DataFrame())

    def on_expense_row_selected(self, row_index):
        """Handle expense row selection"""
        try:
            if row_index >= 0 and row_index < len(self.expenses_df):
                selected_expense = self.expenses_df.iloc[row_index]
                print(f"Selected expense: {selected_expense.get('main_category', 'Unknown')} - ₹{selected_expense.get('amount', 0)}")
        except Exception as e:
            print(f"Error handling expense row selection: {e}")

    def load_budget_details(self):
        """Load the selected budget details into the form"""
        selected_items = self.budget_table.selectedItems()
        if not selected_items:
            return

        # Get the budget ID from the first column
        row = selected_items[0].row()
        budget_id = self.budget_table.item(row, 0).text()

        # Find the budget in the dataframe
        budget = self.budget_df[self.budget_df['budget_id'].astype(str) == budget_id].iloc[0] if len(self.budget_df) > 0 else None

        if budget is not None:
            # Update the form fields
            self.category_combo.setCurrentText(str(budget['category']) if 'category' in budget else "")

            amount = float(budget['amount']) if 'amount' in budget and pd.notna(budget['amount']) else 0
            self.amount_spin.setValue(amount)

            self.period_combo.setCurrentText(str(budget['period']) if 'period' in budget else "Monthly")
            self.notes_edit.setText(str(budget['notes']) if 'notes' in budget and pd.notna(budget['notes']) else "")

            # Enable update and delete buttons
            self.update_budget_btn.setEnabled(True)
            self.delete_budget_btn.setEnabled(True)

    def add_budget(self):
        """Add a new budget allocation"""
        category = self.category_combo.currentText()
        amount = self.amount_spin.value()
        period = self.period_combo.currentText()
        notes = self.notes_edit.toPlainText()

        if not category:
            QMessageBox.warning(self, "Missing Information", "Please enter a budget category for the budget.")
            return

        # Generate new budget ID
        next_id = len(self.budget_df) + 1 if len(self.budget_df) > 0 else 1

        # Create new budget entry
        new_budget = pd.DataFrame({
            'budget_id': [next_id],
            'category': [category],
            'amount': [amount],
            'period': [period],
            'notes': [notes]
        })

        # Add to dataframe
        self.budget_df = pd.concat([self.budget_df, new_budget], ignore_index=True)
        self.data['budget'] = self.budget_df

        # Save to CSV file
        try:
            budget_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'data', 'budget.csv')
            self.budget_df.to_csv(budget_file, index=False)

            # Update the budget table
            self.populate_budget_table()

            # Clear the form
            self.category_combo.setCurrentIndex(0)
            self.amount_spin.setValue(0)
            self.period_combo.setCurrentText("Monthly")
            self.notes_edit.clear()

            # Update analysis charts
            self.update_analysis_charts()

            QMessageBox.information(self, "Budget Added", f"Budget allocation of ₹{amount:.2f} added for {category}.")
        except Exception as e:
            logging.error(f"Error saving budget data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving budget data: {e}")

    def update_budget(self):
        """Update the selected budget allocation"""
        selected_items = self.budget_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a budget to update.")
            return

        # Get the budget ID from the first column
        row = selected_items[0].row()
        budget_id = self.budget_table.item(row, 0).text()

        # Get form values
        category = self.category_combo.currentText()
        amount = self.amount_spin.value()
        period = self.period_combo.currentText()
        notes = self.notes_edit.toPlainText()

        if not category:
            QMessageBox.warning(self, "Missing Information", "Please enter a category for the budget.")
            return

        # Update budget in dataframe
        idx = self.budget_df[self.budget_df['budget_id'].astype(str) == budget_id].index
        if len(idx) > 0:
            self.budget_df.at[idx[0], 'category'] = category
            self.budget_df.at[idx[0], 'amount'] = amount
            self.budget_df.at[idx[0], 'period'] = period
            self.budget_df.at[idx[0], 'notes'] = notes

            # Save to CSV file
            try:
                budget_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'data', 'budget.csv')
                self.budget_df.to_csv(budget_file, index=False)

                # Update the budget table
                self.populate_budget_table()

                # Update analysis charts
                self.update_analysis_charts()

                QMessageBox.information(self, "Budget Updated", f"Budget allocation for {category} updated to ₹{amount:.2f}.")
            except Exception as e:
                logging.error(f"Error saving budget data: {e}")
                QMessageBox.warning(self, "Error", f"Error saving budget data: {e}")
        else:
            QMessageBox.warning(self, "Error", "Could not find budget to update.")

    def delete_budget(self):
        """Delete the selected budget allocation"""
        selected_items = self.budget_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a budget to delete.")
            return

        # Get the budget ID from the first column
        row = selected_items[0].row()
        budget_id = self.budget_table.item(row, 0).text()
        category = self.budget_table.item(row, 1).text()

        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion",
                                   f"Are you sure you want to delete the budget for {category}?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # Delete budget from dataframe
        self.budget_df = self.budget_df[self.budget_df['budget_id'].astype(str) != budget_id]
        self.data['budget'] = self.budget_df

        # Save to CSV file
        try:
            budget_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'data', 'budget.csv')
            self.budget_df.to_csv(budget_file, index=False)

            # Update the budget table
            self.populate_budget_table()

            # Clear the form
            self.category_combo.setCurrentIndex(0)
            self.amount_spin.setValue(0)
            self.period_combo.setCurrentText("Monthly")
            self.notes_edit.clear()

            # Disable update and delete buttons
            self.update_budget_btn.setEnabled(False)
            self.delete_budget_btn.setEnabled(False)

            # Update analysis charts
            self.update_analysis_charts()

            QMessageBox.information(self, "Budget Deleted", f"Budget allocation for {category} has been deleted.")
        except Exception as e:
            logging.error(f"Error saving budget data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving budget data: {e}")

    def add_expense(self):
        """Add a new expense record with hierarchical category system"""
        try:
            date = self.expense_date.date().toString("yyyy-MM-dd")
            main_category = self.expense_main_category.currentText()
            sub_category = self.expense_sub_category.currentText()
            amount = self.expense_amount.value()
            source = self.expense_source.currentText()
            notes = self.expense_notes.text()

            if not main_category:
                QMessageBox.warning(self, "Missing Information", "Please select a main category for the expense.")
                return

            if not sub_category:
                QMessageBox.warning(self, "Missing Information", "Please select a sub-category for the expense.")
                return

            if amount <= 0:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid expense amount.")
                return

            # Create expense dataframe if it doesn't exist
            if 'expenses' not in self.data:
                self.data['expenses'] = pd.DataFrame(columns=['expense_id', 'date', 'main_category', 'sub_category', 'amount', 'source', 'notes'])
                self.expenses_df = self.data['expenses']

            # Generate new expense ID
            next_id = len(self.expenses_df) + 1 if len(self.expenses_df) > 0 else 1

            # Create new expense entry with hierarchical categories
            new_expense = pd.DataFrame({
                'expense_id': [next_id],
                'date': [date],
                'main_category': [main_category],
                'sub_category': [sub_category],
                'amount': [amount],
                'source': [source],
                'notes': [notes]
            })

            # Add to dataframe
            self.expenses_df = pd.concat([self.expenses_df, new_expense], ignore_index=True)
            self.data['expenses'] = self.expenses_df

            # Update spending amounts in budget categories
            self.update_category_spending(main_category, sub_category, amount)

            # Save to CSV file
            expenses_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                      'data', 'expenses.csv')
            self.expenses_df.to_csv(expenses_file, index=False)

            # Update the expense table
            self.populate_expense_table()

            # Clear the form
            self.expense_date.setDate(QDate.currentDate())
            self.expense_main_category.setCurrentText("")
            self.expense_sub_category.clear()
            self.expense_sub_category.setEnabled(False)
            self.expense_amount.setValue(0)
            self.expense_source.setCurrentIndex(0)
            self.expense_notes.clear()

            # Update analysis charts and hierarchy display
            self.update_analysis_charts()
            self.populate_budget_hierarchy()

            QMessageBox.information(self, "Expense Added", f"Expense of ₹{amount:.2f} added for {main_category} → {sub_category}.")

        except Exception as e:
            logging.error(f"Error saving expense data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving expense data: {e}")

    def update_category_spending(self, main_category, sub_category, amount):
        """Update spending amounts for the selected categories"""
        try:
            if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
                return

            # Update sub-category spending
            sub_mask = (
                (self.budget_categories_df['category_name'] == sub_category) &
                (self.budget_categories_df['category_type'] == 'Child')
            )

            if sub_mask.any():
                current_spent = float(self.budget_categories_df.loc[sub_mask, 'spent_amount'].iloc[0])
                self.budget_categories_df.loc[sub_mask, 'spent_amount'] = current_spent + amount

            # Update main category spending (sum of all sub-categories)
            main_category_data = self.budget_categories_df[
                (self.budget_categories_df['category_name'] == main_category) &
                (self.budget_categories_df['category_type'] == 'Parent')
            ]

            if len(main_category_data) > 0:
                main_category_id = main_category_data.iloc[0]['category_id']

                # Calculate total spending for all sub-categories under this main category
                sub_categories_spending = self.budget_categories_df[
                    (self.budget_categories_df['category_type'] == 'Child') &
                    (self.budget_categories_df['parent_id'] == main_category_id)
                ]['spent_amount'].sum()

                # Update main category spending
                main_mask = (
                    (self.budget_categories_df['category_name'] == main_category) &
                    (self.budget_categories_df['category_type'] == 'Parent')
                )
                self.budget_categories_df.loc[main_mask, 'spent_amount'] = sub_categories_spending

            # Save budget categories
            self.save_budget_categories()

        except Exception as e:
            logging.error(f"Error updating category spending: {e}")

    def create_expense_data(self):
        """Create expense data from inventory purchases and other sources if available"""
        expenses = pd.DataFrame(columns=['expense_id', 'date', 'category', 'amount', 'source', 'notes'])

        # Try to extract expenses from inventory purchases
        if 'inventory' in self.data and len(self.data['inventory']) > 0:
            inventory_df = self.data['inventory']

            # Check if we have purchase data
            if 'purchase_date' in inventory_df.columns and 'price' in inventory_df.columns:
                for i, (_, item) in enumerate(inventory_df.iterrows()):
                    if pd.notna(item['purchase_date']) and pd.notna(item['price']):
                        category = item['category'] if 'category' in item and pd.notna(item['category']) else "Inventory"
                        price = float(item['price']) if pd.notna(item['price']) else 0
                        qty = float(item['quantity']) if 'quantity' in item and pd.notna(item['quantity']) else 1

                        # Create expense entry
                        new_expense = pd.DataFrame({
                            'expense_id': [i+1],
                            'date': [item['purchase_date']],
                            'category': [category],
                            'amount': [price * qty],
                            'source': ['Inventory Purchase'],
                            'notes': [f"Purchase of {item['item_name']}"]
                        })

                        expenses = pd.concat([expenses, new_expense], ignore_index=True)

        # Save the expenses data
        try:
            expenses_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                      'data', 'expenses.csv')
            expenses.to_csv(expenses_file, index=False)
        except Exception as e:
            logging.error(f"Error saving expense data: {e}")

        return expenses

    def create_budget_charts(self, layout):
        """Create charts for budget analysis"""
        # Create container for charts
        charts_container = QWidget()
        charts_layout = QVBoxLayout(charts_container)

        # Budget vs. Expense chart
        budget_chart_group = QGroupBox("Budget vs. Actual Expenses")
        budget_chart_layout = QVBoxLayout(budget_chart_group)

        # Create figure and canvas
        self.budget_fig, self.budget_ax = plt.subplots(figsize=(8, 5))
        self.budget_canvas = FigureCanvas(self.budget_fig)
        budget_chart_layout.addWidget(self.budget_canvas)

        # Category breakdown chart
        category_chart_group = QGroupBox("Expense Categories Breakdown")
        category_chart_layout = QVBoxLayout(category_chart_group)

        # Create figure and canvas
        self.category_fig, self.category_ax = plt.subplots(figsize=(8, 5))
        self.category_canvas = FigureCanvas(self.category_fig)
        category_chart_layout.addWidget(self.category_canvas)

        # Add charts to layout
        charts_layout.addWidget(budget_chart_group)
        charts_layout.addWidget(category_chart_group)

        # Add charts container to main layout
        layout.addWidget(charts_container)

        # Update charts with data
        self.update_analysis_charts()

    def update_analysis_charts(self):
        """Update the budget analysis charts with current data"""
        # Clear existing charts
        self.budget_ax.clear()
        self.category_ax.clear()

        # Budget vs. Expense chart
        if len(self.budget_df) > 0:
            # Group budgets by category
            budget_by_category = self.budget_df.groupby('category')['amount'].sum().reset_index()

            # Group expenses by category if we have any
            expense_by_category = pd.DataFrame(columns=['category', 'amount'])
            if len(self.expenses_df) > 0:
                expense_by_category = self.expenses_df.groupby('category')['amount'].sum().reset_index()

            # Merge budgets and expenses
            categories = budget_by_category['category'].unique()
            budget_amounts = []
            expense_amounts = []

            for category in categories:
                # Get budget amount
                budget_amount = budget_by_category[budget_by_category['category'] == category]['amount'].sum()
                budget_amounts.append(budget_amount)

                # Get expense amount
                expense_amount = 0
                if category in expense_by_category['category'].values:
                    expense_amount = expense_by_category[expense_by_category['category'] == category]['amount'].sum()
                expense_amounts.append(expense_amount)

            # Create chart data
            x = range(len(categories))
            width = 0.35

            # Create bars
            self.budget_ax.bar(x, budget_amounts, width, label='Budget', color='#3498db')
            self.budget_ax.bar([i + width for i in x], expense_amounts, width, label='Actual', color='#e74c3c')

            # Add labels
            self.budget_ax.set_xlabel('Category')
            self.budget_ax.set_ylabel('Amount (₹)')
            self.budget_ax.set_title('Budget vs. Actual Expenses by Category')
            self.budget_ax.set_xticks([i + width/2 for i in x])
            self.budget_ax.set_xticklabels(categories)
            self.budget_ax.legend()

            # Format y-axis as currency
            self.budget_ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'₹{int(x):,}'))

            # Rotate x labels for better readability
            plt.setp(self.budget_ax.get_xticklabels(), rotation=45, ha='right')

            self.budget_fig.tight_layout()

        # Category breakdown chart (pie chart)
        if len(self.expenses_df) > 0:
            # Group expenses by category
            expense_by_category = self.expenses_df.groupby('category')['amount'].sum()

            # Create pie chart
            self.category_ax.pie(expense_by_category, labels=expense_by_category.index, autopct='%1.1f%%',
                               startangle=90, shadow=True, explode=[0.05] * len(expense_by_category),
                               colors=plt.cm.tab10.colors)
            self.category_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            self.category_ax.set_title('Expense Distribution by Category')

            self.category_fig.tight_layout()

        # Update canvases
        self.budget_canvas.draw()
        self.category_canvas.draw()



        # Right panel: Category management form
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Category management form
        form_group = QGroupBox("Budget Category Management")
        form_layout = QFormLayout(form_group)

        # Category name
        self.new_category_name = QLineEdit()
        self.new_category_name.setPlaceholderText("Enter budget category name...")

        # Category type with clear labels and help text
        type_layout = QVBoxLayout()
        self.category_type_combo = QComboBox()
        self.category_type_combo.addItems([
            "🏢 Parent Category (Main budget area)",
            "📁 Child Category (Sub-category under parent)"
        ])

        # Help text for category types
        self.category_type_help = QLabel()
        self.category_type_help.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        self.category_type_help.setText("💡 Parent: Create main budget areas (e.g., Food, Equipment)\n   Child: Create sub-categories under a parent")
        self.category_type_help.setWordWrap(True)

        type_layout.addWidget(self.category_type_combo)
        type_layout.addWidget(self.category_type_help)

        # Parent category selection (for child categories)
        self.parent_category_combo = QComboBox()
        self.parent_category_combo.setEnabled(False)
        self.parent_category_combo.setPlaceholderText("Select parent category...")

        # Budget allocation
        self.category_budget_spin = QDoubleSpinBox()
        self.category_budget_spin.setMinimum(0)
        self.category_budget_spin.setMaximum(1000000)
        self.category_budget_spin.setSingleStep(100)
        self.category_budget_spin.setPrefix("₹ ")

        # Description
        self.category_description = QTextEdit()
        self.category_description.setMaximumHeight(80)
        self.category_description.setPlaceholderText("Enter category description...")

        # Add fields to form
        form_layout.addRow("Budget Category Name:", self.new_category_name)
        form_layout.addRow("Category Type:", type_layout)
        form_layout.addRow("Parent Category:", self.parent_category_combo)
        form_layout.addRow("Budget Allocation (₹):", self.category_budget_spin)
        form_layout.addRow("Description:", self.category_description)

        right_layout.addWidget(form_group)

        # Button group
        button_layout = QHBoxLayout()

        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_budget_category)

        self.update_category_btn = QPushButton("Update Category")
        self.update_category_btn.clicked.connect(self.update_budget_category)
        self.update_category_btn.setEnabled(False)

        self.delete_category_btn = QPushButton("Delete Category")
        self.delete_category_btn.clicked.connect(self.delete_budget_category)
        self.delete_category_btn.setEnabled(False)

        button_layout.addWidget(self.add_category_btn)
        button_layout.addWidget(self.update_category_btn)
        button_layout.addWidget(self.delete_category_btn)



    def initialize_budget_categories(self):
        """Initialize budget categories data structure"""
        # Create budget categories dataframe if it doesn't exist
        if 'budget_categories' not in self.data:
            self.data['budget_categories'] = pd.DataFrame(columns=[
                'category_id', 'category_name', 'category_type', 'parent_id',
                'budget_amount', 'spent_amount', 'description'
            ])

            # Create default "Kitchen Essentials" parent category with no budget allocation
            default_category = pd.DataFrame({
                'category_id': [1],
                'category_name': ['Kitchen Essentials'],
                'category_type': ['Parent'],
                'parent_id': [None],
                'budget_amount': [0.0],
                'spent_amount': [0.0],
                'description': ['Default parent category for kitchen-related expenses - set your own budget allocation']
            })

            self.data['budget_categories'] = pd.concat([self.data['budget_categories'], default_category], ignore_index=True)

            # Save to CSV
            try:
                budget_categories_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    'data', 'budget_categories.csv')
                self.data['budget_categories'].to_csv(budget_categories_file, index=False)
            except Exception as e:
                logging.error(f"Error saving budget categories: {e}")

        self.budget_categories_df = self.data['budget_categories'].copy()

    def on_category_type_changed(self, category_type):
        """Handle category type change"""
        # Extract the actual type from the display text
        if "Child Category" in category_type:
            self.parent_category_combo.setEnabled(True)
            self.populate_parent_categories()
            # Update help text for child category
            self.category_type_help.setText("💡 Creating a child category under a parent category\n   Select the parent category below")
        else:
            self.parent_category_combo.setEnabled(False)
            self.parent_category_combo.clear()
            # Update help text for parent category
            self.category_type_help.setText("💡 Creating a main budget category\n   This will be a top-level budget area")

    def populate_parent_categories(self):
        """Populate parent category dropdown"""
        self.parent_category_combo.clear()

        # Get parent categories
        parent_categories = self.budget_categories_df[
            self.budget_categories_df['category_type'] == 'Parent'
        ]['category_name'].tolist()

        self.parent_category_combo.addItems(parent_categories)

    def populate_category_tree(self):
        """Populate the category tree table"""
        # Check if category_tree_table exists (it's in the category management section)
        if not hasattr(self, 'category_tree_table'):
            return

        self.category_tree_table.setRowCount(0)

        if not hasattr(self, 'budget_categories_df') or len(self.budget_categories_df) == 0:
            return

        # Sort categories: parents first, then children
        sorted_categories = []

        # Add parent categories first
        parent_categories = self.budget_categories_df[
            self.budget_categories_df['category_type'] == 'Parent'
        ].sort_values('category_name')

        for _, parent in parent_categories.iterrows():
            sorted_categories.append(parent)

            # Add child categories under this parent
            child_categories = self.budget_categories_df[
                (self.budget_categories_df['category_type'] == 'Child') &
                (self.budget_categories_df['parent_id'] == parent['category_id'])
            ].sort_values('category_name')

            for _, child in child_categories.iterrows():
                sorted_categories.append(child)

        # Populate table
        for i, category in enumerate(sorted_categories):
            self.category_tree_table.insertRow(i)

            # Category name with indentation for children
            category_name = category['category_name']
            if category['category_type'] == 'Child':
                category_name = f"    └─ {category_name}"

            name_item = QTableWidgetItem(category_name)
            type_item = QTableWidgetItem(category['category_type'])

            # Format budget amount
            budget_amount = float(category['budget_amount']) if pd.notna(category['budget_amount']) else 0
            budget_item = QTableWidgetItem(f"₹ {budget_amount:.2f}")

            # Format spent amount
            spent_amount = float(category['spent_amount']) if pd.notna(category['spent_amount']) else 0
            spent_item = QTableWidgetItem(f"₹ {spent_amount:.2f}")

            self.category_tree_table.setItem(i, 0, name_item)
            self.category_tree_table.setItem(i, 1, type_item)
            self.category_tree_table.setItem(i, 2, budget_item)
            self.category_tree_table.setItem(i, 3, spent_item)

    def load_category_details(self):
        """Load selected category details into the form"""
        selected_items = self.category_tree_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        category_name = self.category_tree_table.item(row, 0).text().strip().replace("└─ ", "")

        # Find category in dataframe
        category = self.budget_categories_df[
            self.budget_categories_df['category_name'] == category_name
        ]

        if len(category) > 0:
            cat_data = category.iloc[0]

            # Update form fields
            self.new_category_name.setText(cat_data['category_name'])

            # Set category type combo to match the display format
            if cat_data['category_type'] == 'Parent':
                self.category_type_combo.setCurrentText("🏢 Parent Category (Main budget area)")
            else:
                self.category_type_combo.setCurrentText("📁 Child Category (Sub-category under parent)")

            if cat_data['category_type'] == 'Child' and pd.notna(cat_data['parent_id']):
                parent = self.budget_categories_df[
                    self.budget_categories_df['category_id'] == cat_data['parent_id']
                ]
                if len(parent) > 0:
                    self.parent_category_combo.setCurrentText(parent.iloc[0]['category_name'])

            budget_amount = float(cat_data['budget_amount']) if pd.notna(cat_data['budget_amount']) else 0
            self.category_budget_spin.setValue(budget_amount)

            description = cat_data['description'] if pd.notna(cat_data['description']) else ""
            self.category_description.setText(description)

            # Enable update and delete buttons
            self.update_category_btn.setEnabled(True)
            self.delete_category_btn.setEnabled(True)

    def add_budget_category(self):
        """Add a new budget category"""
        category_name = self.new_category_name.text().strip()
        category_type_display = self.category_type_combo.currentText()
        budget_amount = self.category_budget_spin.value()
        description = self.category_description.toPlainText()

        if not category_name:
            QMessageBox.warning(self, "Missing Information", "Please enter a budget category name.")
            return

        # Extract actual category type from display text
        if "Parent Category" in category_type_display:
            category_type = "Parent"
        else:
            category_type = "Child"

        # Check if category already exists
        if len(self.budget_categories_df[self.budget_categories_df['category_name'] == category_name]) > 0:
            QMessageBox.warning(self, "Category Exists", f"Budget category '{category_name}' already exists.")
            return

        # Get parent ID if child category
        parent_id = None
        if category_type == "Child":
            parent_name = self.parent_category_combo.currentText()
            if not parent_name:
                QMessageBox.warning(self, "Missing Parent", "Please select a parent category for this child category.")
                return

            parent = self.budget_categories_df[
                self.budget_categories_df['category_name'] == parent_name
            ]
            if len(parent) > 0:
                parent_id = parent.iloc[0]['category_id']
            else:
                QMessageBox.warning(self, "Invalid Parent", f"Parent category '{parent_name}' not found.")
                return

        # Generate new category ID
        next_id = self.budget_categories_df['category_id'].max() + 1 if len(self.budget_categories_df) > 0 else 1

        # Create new category
        new_category = pd.DataFrame({
            'category_id': [next_id],
            'category_name': [category_name],
            'category_type': [category_type],
            'parent_id': [parent_id],
            'budget_amount': [budget_amount],
            'spent_amount': [0.0],
            'description': [description]
        })

        # Add to dataframe
        self.budget_categories_df = pd.concat([self.budget_categories_df, new_category], ignore_index=True)
        self.data['budget_categories'] = self.budget_categories_df

        # Save to CSV
        try:
            budget_categories_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                'data', 'budget_categories.csv')
            self.budget_categories_df.to_csv(budget_categories_file, index=False)

            # Refresh displays
            self.populate_category_tree()
            self.populate_parent_categories()

            # Notify other modules about category changes
            self.sync_categories_with_inventory()

            # Clear form
            self.clear_category_form()

            QMessageBox.information(self, "Category Added", f"Budget category '{category_name}' added successfully.")

        except Exception as e:
            logging.error(f"Error saving budget categories: {e}")
            QMessageBox.warning(self, "Error", f"Error saving budget categories: {e}")

    def update_budget_category(self):
        """Update selected budget category"""
        selected_items = self.category_tree_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a category to update.")
            return

        row = selected_items[0].row()
        old_category_name = self.category_tree_table.item(row, 0).text().strip().replace("└─ ", "")

        # Get form values
        category_name = self.new_category_name.text().strip()
        category_type_display = self.category_type_combo.currentText()
        budget_amount = self.category_budget_spin.value()
        description = self.category_description.toPlainText()

        if not category_name:
            QMessageBox.warning(self, "Missing Information", "Please enter a budget category name.")
            return

        # Extract actual category type from display text
        if "Parent Category" in category_type_display:
            category_type = "Parent"
        else:
            category_type = "Child"

        # Find category in dataframe
        category_idx = self.budget_categories_df[
            self.budget_categories_df['category_name'] == old_category_name
        ].index

        if len(category_idx) > 0:
            idx = category_idx[0]

            # Get parent ID if child category
            parent_id = None
            if category_type == "Child":
                parent_name = self.parent_category_combo.currentText()
                if parent_name:
                    parent = self.budget_categories_df[
                        self.budget_categories_df['category_name'] == parent_name
                    ]
                    if len(parent) > 0:
                        parent_id = parent.iloc[0]['category_id']
                else:
                    QMessageBox.warning(self, "Missing Parent", "Please select a parent category for this child category.")
                    return

            # Update category
            self.budget_categories_df.at[idx, 'category_name'] = category_name
            self.budget_categories_df.at[idx, 'category_type'] = category_type
            self.budget_categories_df.at[idx, 'parent_id'] = parent_id
            self.budget_categories_df.at[idx, 'budget_amount'] = budget_amount
            self.budget_categories_df.at[idx, 'description'] = description

            self.data['budget_categories'] = self.budget_categories_df

            # Save to CSV
            try:
                budget_categories_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    'data', 'budget_categories.csv')
                self.budget_categories_df.to_csv(budget_categories_file, index=False)

                # Refresh displays
                self.populate_category_tree()
                self.populate_parent_categories()

                # Notify other modules about category changes
                self.sync_categories_with_inventory()

                QMessageBox.information(self, "Category Updated", f"Budget category '{category_name}' updated successfully.")

            except Exception as e:
                logging.error(f"Error saving budget categories: {e}")
                QMessageBox.warning(self, "Error", f"Error saving budget categories: {e}")

    def delete_budget_category(self):
        """Delete selected budget category"""
        selected_items = self.category_tree_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a category to delete.")
            return

        row = selected_items[0].row()
        category_name = self.category_tree_table.item(row, 0).text().strip().replace("└─ ", "")

        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion",
                                   f"Are you sure you want to delete the budget category '{category_name}'?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # Check if category has children
        category = self.budget_categories_df[
            self.budget_categories_df['category_name'] == category_name
        ]

        if len(category) > 0:
            category_id = category.iloc[0]['category_id']
            children = self.budget_categories_df[
                self.budget_categories_df['parent_id'] == category_id
            ]

            if len(children) > 0:
                QMessageBox.warning(self, "Cannot Delete",
                                  f"Cannot delete '{category_name}' because it has child categories. Please delete child categories first.")
                return

        # Delete category
        self.budget_categories_df = self.budget_categories_df[
            self.budget_categories_df['category_name'] != category_name
        ]
        self.data['budget_categories'] = self.budget_categories_df

        # Save to CSV
        try:
            budget_categories_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                'data', 'budget_categories.csv')
            self.budget_categories_df.to_csv(budget_categories_file, index=False)

            # Refresh displays
            self.populate_category_tree()
            self.populate_parent_categories()

            # Clear form
            self.clear_category_form()

            # Disable buttons
            self.update_category_btn.setEnabled(False)
            self.delete_category_btn.setEnabled(False)

            QMessageBox.information(self, "Category Deleted", f"Budget category '{category_name}' deleted successfully.")

        except Exception as e:
            logging.error(f"Error saving budget categories: {e}")
            QMessageBox.warning(self, "Error", f"Error saving budget categories: {e}")

    def sync_categories_with_inventory(self):
        """Synchronize budget categories with inventory categories for bidirectional consistency"""
        try:
            # Get all budget category names (both parent and child)
            budget_category_names = self.budget_categories_df['category_name'].tolist()

            # Check if we have access to inventory data
            if 'categories' not in self.data:
                self.data['categories'] = pd.DataFrame(columns=['category_name', 'description'])

            categories_df = self.data['categories']

            # Add budget categories to inventory categories if they don't exist
            for budget_category in budget_category_names:
                if len(categories_df[categories_df['category_name'] == budget_category]) == 0:
                    # Add budget category to inventory categories
                    new_category = pd.DataFrame({
                        'category_name': [budget_category],
                        'description': [f'Budget category: {budget_category}']
                    })
                    categories_df = pd.concat([categories_df, new_category], ignore_index=True)

            # Update the data
            self.data['categories'] = categories_df

            # Save to categories CSV
            try:
                categories_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             'data', 'categories.csv')
                categories_df.to_csv(categories_file, index=False)
            except Exception as e:
                logging.error(f"Error saving categories: {e}")

            # Notify other modules to refresh their category dropdowns
            self.notify_category_change()

        except Exception as e:
            logging.error(f"Error syncing categories with inventory: {e}")

    def notify_category_change(self):
        """Notify other modules that categories have changed"""
        try:
            # Try to find and update inventory module if it exists
            # This is a simple approach - in a more complex app, you'd use signals/slots

            # Check if we have a parent widget that might contain other modules
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, 'inventory_widget'):
                parent_widget = parent_widget.parent()

            if parent_widget and hasattr(parent_widget, 'inventory_widget'):
                inventory_widget = parent_widget.inventory_widget
                # Update inventory category dropdowns if the method exists
                if hasattr(inventory_widget, 'update_category_combos'):
                    inventory_widget.update_category_combos()
                elif hasattr(inventory_widget, 'refresh_filter_options'):
                    inventory_widget.refresh_filter_options()

            # Also try to update expenses module
            if parent_widget and hasattr(parent_widget, 'expenses_widget'):
                expenses_widget = parent_widget.expenses_widget
                if hasattr(expenses_widget, 'refresh_budget_categories_dropdown'):
                    expenses_widget.refresh_budget_categories_dropdown()

        except Exception as e:
            logging.error(f"Error notifying category change: {e}")

    def clear_category_form(self):
        """Clear the category form"""
        self.new_category_name.clear()
        self.category_type_combo.setCurrentIndex(0)
        self.parent_category_combo.clear()
        self.category_budget_spin.setValue(0)
        self.category_description.clear()
        self.update_category_btn.setEnabled(False)
        self.delete_category_btn.setEnabled(False)

    def populate_inventory_categories(self):
        """Populate the inventory categories table"""
        # This method is no longer needed as inventory categories are handled elsewhere
        pass

        # Get inventory data
        if 'inventory' not in self.data or len(self.data['inventory']) == 0:
            return

        inventory_df = self.data['inventory']

        # Group by category and calculate metrics
        if 'category' in inventory_df.columns:
            category_stats = inventory_df.groupby('category').agg({
                'item_name': 'count',  # Count of items
                'total_value': 'sum'   # Sum of total values
            }).reset_index()

            # Populate table
            for i, row in category_stats.iterrows():
                self.inventory_categories_table.insertRow(i)

                # Category name
                category_item = QTableWidgetItem(str(row['category']))
                self.inventory_categories_table.setItem(i, 0, category_item)

                # Items count
                count_item = QTableWidgetItem(str(row['item_name']))
                self.inventory_categories_table.setItem(i, 1, count_item)

                # Total value
                total_value = float(row['total_value']) if pd.notna(row['total_value']) else 0
                value_item = QTableWidgetItem(f"₹ {total_value:.2f}")
                self.inventory_categories_table.setItem(i, 2, value_item)

    def update_budget_tracking(self):
        """Update budget tracking by matching expenses against allocated budgets"""
        try:
            # Get expenses data
            if 'expenses_list' not in self.data or len(self.data['expenses_list']) == 0:
                return

            expenses_df = self.data['expenses_list']

            # Filter for purchased items only
            purchased_expenses = expenses_df[expenses_df['status'] == 'Purchased'] if 'status' in expenses_df.columns else pd.DataFrame()

            if len(purchased_expenses) == 0:
                return

            # Group by budget category and sum the spending
            if 'budget_category' in purchased_expenses.columns and 'current_price' in purchased_expenses.columns:
                spending_by_category = purchased_expenses.groupby('budget_category')['current_price'].sum().reset_index()

                # Update budget categories with spent amounts
                for _, spending_row in spending_by_category.iterrows():
                    budget_category = spending_row['budget_category']
                    spent_amount = spending_row['current_price']

                    # Find matching budget category and update spent amount
                    mask = self.budget_categories_df['category_name'] == budget_category
                    if mask.any():
                        self.budget_categories_df.loc[mask, 'spent_amount'] = spent_amount

                # Save updated budget categories
                self.data['budget_categories'] = self.budget_categories_df
                budget_categories_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    'data', 'budget_categories.csv')
                self.budget_categories_df.to_csv(budget_categories_file, index=False)

                # Refresh the category tree to show updated spending
                self.populate_category_tree()

        except Exception as e:
            logging.error(f"Error updating budget tracking: {e}")
            print(f"Error updating budget tracking: {e}")

    def refresh_budget_data(self):
        """Refresh all budget-related displays"""
        try:
            # Refresh budget categories from data
            if 'budget_categories' in self.data:
                self.budget_categories_df = self.data['budget_categories'].copy()

            # Update budget tracking
            self.update_budget_tracking()

            # Refresh displays
            self.populate_category_tree()
            self.populate_inventory_categories()

        except Exception as e:
            logging.error(f"Error refreshing budget data: {e}")
            print(f"Error refreshing budget data: {e}")

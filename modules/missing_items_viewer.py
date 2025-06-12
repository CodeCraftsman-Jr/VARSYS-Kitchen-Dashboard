"""
Missing Items Viewer Module
Shows ingredients that need to be added to inventory for accurate pricing
"""

import os
import json
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGroupBox, QTextEdit, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

class MissingItemsViewer(QWidget):
    """Widget to display missing ingredients that need to be added to inventory"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.missing_file = os.path.join('data', 'missing_ingredients.json')
        self.init_ui()
        self.load_missing_items()
        
        # Auto-refresh every 10 seconds to catch updates quickly
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_missing_items)
        self.refresh_timer.start(10000)  # Check every 10 seconds for updates
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header - Title only
        header_layout = QHBoxLayout()

        title_label = QLabel("Missing Ingredients for Pricing")
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #dc3545;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Info box
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_box)
        
        info_label = QLabel("⚠️ <b>Important:</b> These ingredients are missing from your inventory and need to be added for accurate pricing calculations.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #856404; font-size: 14px;")
        info_layout.addWidget(info_label)
        
        action_label = QLabel("📝 <b>Action Required:</b> Add these items to your inventory with proper prices to get accurate cost calculations.")
        action_label.setWordWrap(True)
        action_label.setStyleSheet("color: #856404; font-size: 14px; margin-top: 5px;")
        info_layout.addWidget(action_label)
        
        layout.addWidget(info_box)

        # Button row with better spacing and sizing
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        action_layout.setContentsMargins(0, 10, 0, 10)

        # Add to Shopping List button (make it smaller to fit others)
        self.add_shopping_btn_main = QPushButton("🛒 Add Missing Items to Shopping")
        self.add_shopping_btn_main.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.add_shopping_btn_main.clicked.connect(self.add_to_shopping_list)
        action_layout.addWidget(self.add_shopping_btn_main)

        # Refresh button (smaller)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_missing_items)
        action_layout.addWidget(refresh_btn)

        # Force regenerate button (for debugging)
        regenerate_btn = QPushButton("🔄 Force Regenerate")
        regenerate_btn.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #e8590c;
            }
        """)
        regenerate_btn.clicked.connect(self.force_regenerate_missing_items)
        action_layout.addWidget(regenerate_btn)

        # Clear all button (smaller)
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_btn.clicked.connect(self.clear_missing_items)
        action_layout.addWidget(clear_btn)

        # Add stretch to push buttons to left and prevent overflow
        action_layout.addStretch()

        layout.addLayout(action_layout)

        # Missing items table
        self.create_missing_items_table(layout)
        
        # Summary section
        self.create_summary_section(layout)
    
    def create_missing_items_table(self, parent_layout):
        """Create the missing items table"""
        table_group = QGroupBox("Missing Ingredients by Recipe")
        table_layout = QVBoxLayout(table_group)
        
        self.missing_table = QTableWidget()
        self.missing_table.setColumnCount(3)
        self.missing_table.setHorizontalHeaderLabels([
            "Recipe Name", "Missing Ingredient", "Last Checked"
        ])
        
        # Modern table styling
        self.missing_table.setStyleSheet("""
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
        header = self.missing_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Recipe Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Missing Ingredient
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Last Checked
        
        table_layout.addWidget(self.missing_table)
        parent_layout.addWidget(table_group)
    
    def create_summary_section(self, parent_layout):
        """Create summary section"""
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_label = QLabel("No missing ingredients data available.")
        self.summary_label.setStyleSheet("font-size: 14px; color: #6c757d; padding: 10px;")
        summary_layout.addWidget(self.summary_label)
        
        parent_layout.addWidget(summary_group)
    
    def load_missing_items(self):
        """Load and display missing ingredients"""
        try:
            if not os.path.exists(self.missing_file):
                self.missing_table.setRowCount(0)
                self.summary_label.setText("✅ No missing ingredients found. All recipes can be priced accurately!")
                self.summary_label.setStyleSheet("font-size: 14px; color: #28a745; padding: 10px; font-weight: 500;")
                return
            
            with open(self.missing_file, 'r') as f:
                missing_data = json.load(f)
            
            if not missing_data:
                self.missing_table.setRowCount(0)
                self.summary_label.setText("✅ No missing ingredients found. All recipes can be priced accurately!")
                self.summary_label.setStyleSheet("font-size: 14px; color: #28a745; padding: 10px; font-weight: 500;")
                return
            
            # Flatten the data for table display
            table_data = []
            total_missing = 0
            affected_recipes = 0
            
            for recipe_key, recipe_data in missing_data.items():
                recipe_id = recipe_data.get('recipe_id', 'Unknown')
                recipe_name = recipe_data.get('recipe_name', f'Recipe {recipe_id}')
                last_checked = recipe_data.get('last_checked', 'Unknown')
                missing_items = recipe_data.get('missing_items', [])

                if missing_items:
                    affected_recipes += 1

                    for item in missing_items:
                        table_data.append({
                            'recipe_name': recipe_name,
                            'ingredient': item.get('name', 'Unknown'),
                            'last_checked': last_checked
                        })
                        total_missing += 1
            
            # Populate table
            self.missing_table.setRowCount(len(table_data))
            
            for row, item in enumerate(table_data):
                # Recipe name
                recipe_item = QTableWidgetItem(item['recipe_name'])
                recipe_item.setForeground(QColor("#dc3545"))
                recipe_item.setFont(QFont("", 0, QFont.Bold))
                self.missing_table.setItem(row, 0, recipe_item)

                # Ingredient name
                ingredient_item = QTableWidgetItem(item['ingredient'])
                self.missing_table.setItem(row, 1, ingredient_item)

                # Last checked
                try:
                    checked_time = datetime.fromisoformat(item['last_checked'])
                    time_str = checked_time.strftime("%Y-%m-%d %H:%M")
                except:
                    time_str = "Unknown"

                time_item = QTableWidgetItem(time_str)
                time_item.setForeground(QColor("#6c757d"))
                self.missing_table.setItem(row, 2, time_item)
            
            # Update summary
            summary_text = f"❌ <b>{total_missing}</b> missing ingredients across <b>{affected_recipes}</b> recipes.\n"
            summary_text += f"📊 Pricing calculations are incomplete until these items are added to inventory."
            
            self.summary_label.setText(summary_text)
            self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px;")
            
        except Exception as e:
            self.summary_label.setText(f"Error loading missing items: {e}")
            self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px;")

    def refresh_missing_items(self):
        """Refresh missing items without regenerating - just reload from file"""
        try:
            self.load_missing_items()
        except Exception as e:
            print(f"Error refreshing missing items: {e}")
            self.summary_label.setText(f"❌ Error refreshing: {str(e)}")
            self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px;")

    def force_regenerate_missing_items(self):
        """Force regeneration of missing items using the latest logic"""
        try:
            # Show progress dialog
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import QTimer

            progress = QProgressDialog("Regenerating missing items data...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Processing")
            progress.setModal(True)
            progress.setValue(10)
            progress.show()

            # Process events to show the dialog
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()

            # Delete the old JSON file to force regeneration
            if os.path.exists(self.missing_file):
                os.remove(self.missing_file)
                print("🗑️ Deleted old missing ingredients file")

            progress.setValue(30)
            QApplication.processEvents()

            # Update status to show we're regenerating
            self.summary_label.setText("🔄 Regenerating missing items data with latest logic...")
            self.summary_label.setStyleSheet("font-size: 14px; color: #17a2b8; padding: 10px; font-weight: 500;")

            progress.setValue(50)
            QApplication.processEvents()

            # Try to trigger regeneration by importing and calling the pricing management
            try:
                from modules.pricing_management import PricingManagementWidget

                # Create a temporary instance to regenerate the data
                # We need to pass the parent's data to it
                parent_app = self.parent()
                while parent_app and not hasattr(parent_app, 'data'):
                    parent_app = parent_app.parent()

                progress.setValue(70)
                QApplication.processEvents()

                if parent_app and hasattr(parent_app, 'data'):
                    print("📊 Found parent app with data, regenerating missing items...")
                    temp_pricing = PricingManagementWidget(parent_app.data)
                    temp_pricing.check_missing_items_manual()
                    print("[SUCCESS] Missing items regenerated successfully")
                else:
                    print("⚠️ Could not find parent app data")

            except Exception as e:
                print(f"⚠️ Could not regenerate via pricing management: {e}")
                # Fallback: just clear the file and show empty state
                pass

            progress.setValue(90)
            QApplication.processEvents()

            # Reload the data
            self.load_missing_items()

            progress.setValue(100)
            progress.close()

            # Show success message
            self.summary_label.setText("✅ Missing items data regenerated successfully!")
            self.summary_label.setStyleSheet("font-size: 14px; color: #28a745; padding: 10px; font-weight: 500;")

            # Reset to normal after 3 seconds
            QTimer.singleShot(3000, self.load_missing_items)

        except Exception as e:
            print(f"Error force regenerating missing items: {e}")
            self.summary_label.setText(f"❌ Error regenerating: {str(e)}")
            self.summary_label.setStyleSheet("font-size: 14px; color: #dc3545; padding: 10px;")

    def clear_missing_items(self):
        """Clear all missing items data"""
        try:
            reply = QMessageBox.question(
                self, 
                "Clear Missing Items", 
                "Are you sure you want to clear all missing items data?\n\nThis will remove the record but won't fix the underlying pricing issues.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if os.path.exists(self.missing_file):
                    os.remove(self.missing_file)
                
                self.missing_table.setRowCount(0)
                self.summary_label.setText("✅ Missing items data cleared. Pricing calculations will be recalculated on next recipe analysis.")
                self.summary_label.setStyleSheet("font-size: 14px; color: #28a745; padding: 10px;")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear missing items: {e}")

    def add_to_shopping_list(self):
        """Add missing items directly to shopping list"""
        print("🛒 Add to shopping list button clicked!")
        try:
            if not os.path.exists(self.missing_file):
                QMessageBox.information(self, "No Missing Items", "No missing items found to add.")
                return

            # Load missing items
            with open(self.missing_file, 'r') as f:
                missing_data = json.load(f)

            # Collect all missing items with deduplication
            unique_missing = {}  # Use dict to automatically deduplicate by item name
            recipe_usage = {}    # Track which recipes use each ingredient

            for recipe_key, recipe_data in missing_data.items():
                recipe_name = recipe_data.get('recipe_name', f'Recipe {recipe_data.get("recipe_id", "Unknown")}')
                for item in recipe_data.get('missing_items', []):
                    item_name = item.get('name', 'Unknown')

                    # Add to unique items (will overwrite duplicates, keeping latest)
                    unique_missing[item_name] = {
                        'name': item_name,
                        'quantity': item.get('quantity', 0),
                        'unit': item.get('unit', 'units'),
                        'reason': item.get('reason', 'unknown')
                    }

                    # Track recipe usage for this ingredient
                    if item_name not in recipe_usage:
                        recipe_usage[item_name] = []
                    if recipe_name not in recipe_usage[item_name]:
                        recipe_usage[item_name].append(recipe_name)

            # Convert to list and add recipe usage info
            all_missing = []
            for item_name, item_data in unique_missing.items():
                item_data['recipes'] = recipe_usage[item_name]
                item_data['recipe_count'] = len(recipe_usage[item_name])
                all_missing.append(item_data)

            print(f"Found {len(all_missing)} unique missing items (deduplicated from {sum(len(recipe_data.get('missing_items', [])) for recipe_data in missing_data.values())} total)")

            if not all_missing:
                QMessageBox.information(self, "No Missing Items", "No missing items found to add.")
                return

            # Show selection dialog
            print("Showing selection dialog...")
            self.show_add_to_shopping_dialog(all_missing)

        except Exception as e:
            print(f"Error in add_to_shopping_list: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add items to shopping list: {e}")

    def show_add_to_shopping_dialog(self, missing_items):
        """Show dialog to select items to add to shopping list with performance optimization"""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
                                       QDialogButtonBox, QScrollArea, QPushButton,
                                       QProgressBar, QApplication)

        # Check if too many items - offer bulk add option with better messaging
        if len(missing_items) > 100:
            reply = QMessageBox.question(
                self,
                "Large Number of Items",
                f"Found {len(missing_items)} missing items. This is a large number that may cause performance issues.\n\n"
                "Recommended options:\n"
                "• 'Yes' - Add ALL items automatically (RECOMMENDED - fast & reliable)\n"
                "• 'No' - Show selection dialog (may be slow, use for small selections only)\n"
                "• 'Cancel' - Cancel operation\n\n"
                "Note: Bulk add processes items in small chunks to prevent freezing.",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                # Add all items automatically with chunked processing
                print(f"Adding all {len(missing_items)} items automatically with chunked processing...")
                try:
                    self.add_selected_to_shopping(missing_items)
                except Exception as e:
                    print(f"Error in bulk add: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to add items in bulk: {e}")
                return
            elif reply == QMessageBox.Cancel:
                return
            # If No, continue with dialog but warn about performance

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Missing Items to Shopping List")
        dialog.setModal(True)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        # Header with performance warning
        if len(missing_items) > 50:
            header = QLabel(f"⚠️ Large selection: {len(missing_items)} items found. Consider using 'Select All' for better performance.")
            header.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 10px; color: #d63384;")
        else:
            header = QLabel(f"Select missing items to add to shopping list ({len(missing_items)} items found):")
            header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(header)

        # Control buttons
        control_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet("background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px;")

        select_none_btn = QPushButton("Select None")
        select_none_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 5px 10px; border-radius: 4px;")

        control_layout.addWidget(select_all_btn)
        control_layout.addWidget(select_none_btn)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Progress bar for loading
        progress_bar = QProgressBar()
        progress_bar.setVisible(False)
        layout.addWidget(progress_bar)

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Create checkboxes with performance optimization
        checkboxes = []

        # Limit initial load to prevent freezing
        items_to_show = missing_items[:50] if len(missing_items) > 50 else missing_items

        print(f"Creating checkboxes for {len(items_to_show)} items (showing first 50 of {len(missing_items)})")

        for i, item in enumerate(items_to_show):
            # Handle both old and new data structures
            recipe_info = ""
            if 'recipe' in item:
                recipe_info = f" - from {item['recipe']}"
            elif 'recipes' in item and item['recipes']:
                if len(item['recipes']) == 1:
                    recipe_info = f" - from {item['recipes'][0]}"
                else:
                    recipe_info = f" - used in {len(item['recipes'])} recipes"

            checkbox = QCheckBox(f"{item['name']}{recipe_info}")
            checkbox.setChecked(True)  # Pre-select items for convenience
            checkbox.item_data = item
            checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

            # Process events every 10 items to keep UI responsive
            if i % 10 == 0:
                QApplication.processEvents()

        # Add remaining items button if there are more
        if len(missing_items) > 50:
            remaining_count = len(missing_items) - 50
            load_more_btn = QPushButton(f"Load {remaining_count} more items...")
            load_more_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px; border-radius: 4px; margin: 10px;")

            def load_remaining():
                load_more_btn.setText("Loading...")
                load_more_btn.setEnabled(False)
                progress_bar.setVisible(True)
                progress_bar.setRange(0, remaining_count)

                # Load remaining items in chunks
                remaining_items = missing_items[50:]
                for i, item in enumerate(remaining_items):
                    # Handle both old and new data structures
                    recipe_info = ""
                    if 'recipe' in item:
                        recipe_info = f" - from {item['recipe']}"
                    elif 'recipes' in item and item['recipes']:
                        if len(item['recipes']) == 1:
                            recipe_info = f" - from {item['recipes'][0]}"
                        else:
                            recipe_info = f" - used in {len(item['recipes'])} recipes"

                    checkbox = QCheckBox(f"{item['name']}{recipe_info}")
                    checkbox.setChecked(True)
                    checkbox.item_data = item
                    checkboxes.append(checkbox)
                    scroll_layout.addWidget(checkbox)

                    progress_bar.setValue(i + 1)

                    # Process events every 5 items to keep UI responsive
                    if i % 5 == 0:
                        QApplication.processEvents()

                load_more_btn.setVisible(False)
                progress_bar.setVisible(False)
                scroll_widget.adjustSize()

            load_more_btn.clicked.connect(load_remaining)
            scroll_layout.addWidget(load_more_btn)

        # Connect control buttons
        def select_all():
            for cb in checkboxes:
                cb.setChecked(True)

        def select_none():
            for cb in checkboxes:
                cb.setChecked(False)

        select_all_btn.clicked.connect(select_all)
        select_none_btn.clicked.connect(select_none)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Execute dialog
        result = dialog.exec()
        print(f"Dialog result: {result}")
        if result == QDialog.Accepted:
            selected_items = [cb.item_data for cb in checkboxes if cb.isChecked()]
            print(f"Selected items count: {len(selected_items)}")
            if selected_items:
                print("Adding selected items to shopping list...")
                self.add_selected_to_shopping(selected_items)
            else:
                QMessageBox.information(self, "No Items Selected", "No items were selected to add to the shopping list.")
        else:
            print("Dialog was cancelled")

    def add_selected_to_shopping(self, selected_items):
        """Add selected items to shopping list with user input for quantity and price"""
        print(f"💾 Adding {len(selected_items)} selected items to shopping list...")

        total_items = len(selected_items)

        # Ask user for each item's quantity and price
        items_with_user_input = []

        for i, item in enumerate(selected_items):
            item_name = str(item.get('name', '')).strip()
            if not item_name:
                continue

            # Show input dialog for quantity and price
            user_data = self.get_user_input_for_item(item_name, i + 1, total_items)
            if user_data is None:  # User cancelled
                print(f"User cancelled input for item: {item_name}")
                return

            if user_data == 'skip':  # User skipped this item
                print(f"User skipped item: {item_name}")
                continue

            # Add user input to item data
            item_with_input = {
                'name': item_name,
                'quantity': user_data['quantity'],
                'unit': user_data['unit'],
                'price': user_data['price'],
                'recipe': item.get('recipe', 'Unknown Recipe')
            }
            items_with_user_input.append(item_with_input)

        if not items_with_user_input:
            QMessageBox.information(self, "No Items", "No items were processed.")
            return

        # Show progress dialog for CSV operations
        progress_dialog = None
        if len(items_with_user_input) > 5:
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt
            progress_dialog = QProgressDialog("Adding items to shopping list...", "Cancel", 0, len(items_with_user_input), self)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setMinimumDuration(0)
            progress_dialog.show()
            progress_dialog.setValue(0)

        try:
            import csv
            from datetime import datetime
            from PySide6.QtWidgets import QApplication

            shopping_file = 'data/shopping_list.csv'

            # Read existing items with status tracking
            existing_items = set()  # All items (any status)
            purchased_items = set()  # Items marked as purchased
            pending_items = set()   # Items marked as pending
            next_id = 1

            if os.path.exists(shopping_file):
                print("Reading existing shopping list...")
                with open(shopping_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'item_name' in row and row['item_name']:
                            item_name = row['item_name'].lower().strip()
                            status = str(row.get('status', '')).strip().lower()

                            existing_items.add(item_name)
                            if status == 'purchased':
                                purchased_items.add(item_name)
                            elif status == 'pending':
                                pending_items.add(item_name)

                        if 'item_id' in row and row['item_id']:
                            try:
                                next_id = max(next_id, int(row['item_id']) + 1)
                            except:
                                pass
                print(f"Found {len(existing_items)} existing items ({len(purchased_items)} purchased, {len(pending_items)} pending), next ID: {next_id}")
            else:
                print("Creating new shopping list file")

            # Prepare new items to add
            new_items = []
            added_count = 0
            skipped_existing = 0
            skipped_duplicates = 0
            reactivated_count = 0  # Track items that were purchased but are now needed again
            processed_items = set()  # Track items we've already processed in this batch

            for i, item in enumerate(items_with_user_input):
                # Update progress frequently
                if progress_dialog:
                    progress_dialog.setValue(i)
                    progress_dialog.setLabelText(f"Processing {i + 1} of {len(items_with_user_input)}")
                    if progress_dialog.wasCanceled():
                        print("Operation cancelled by user")
                        return

                # Process events every item for responsiveness
                QApplication.processEvents()

                item_name = str(item.get('name', '')).strip()
                item_name_lower = item_name.lower()

                if not item_name:
                    continue

                # Check if already in shopping list
                if item_name_lower in existing_items:
                    # If item exists but is marked as "Purchased", allow re-adding as new "Pending" item
                    if item_name_lower in purchased_items:
                        print(f"Re-activating purchased item: {item_name} (adding as new pending item)")
                        reactivated_count += 1
                        # Continue to add as new item with today's date
                    else:
                        print(f"Skipping existing pending item: {item_name}")
                        skipped_existing += 1
                        continue

                # Check if we've already processed this item in this batch (duplicate)
                if item_name_lower in processed_items:
                    skipped_duplicates += 1
                    continue

                # Add new unique item with user-provided data
                new_item = {
                    'item_id': next_id,
                    'item_name': item_name,
                    'category': 'Missing Ingredient',
                    'quantity': float(item.get('quantity', 1)),
                    'unit': str(item.get('unit', 'units')),
                    'priority': 'High',
                    'last_price': float(item.get('price', 0)),
                    'location': 'Local Market',
                    'notes': f"Missing from {str(item.get('recipe', 'Unknown Recipe'))}",
                    'status': 'Pending',
                    'current_price': float(item.get('price', 0)),
                    'avg_price': float(item.get('price', 0)),
                    'date_added': datetime.now().strftime('%Y-%m-%d'),
                    'date_purchased': ''
                }
                new_items.append(new_item)
                existing_items.add(item_name_lower)
                processed_items.add(item_name_lower)
                next_id += 1
                added_count += 1

            # Write new items to CSV using append mode for better performance
            if new_items:
                print(f"Writing {len(new_items)} new items to CSV...")

                # Define CSV columns
                fieldnames = [
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'priority',
                    'last_price', 'location', 'notes', 'status', 'current_price', 'avg_price',
                    'date_added', 'date_purchased'
                ]

                # Check if file exists and has header
                file_exists = os.path.exists(shopping_file)

                with open(shopping_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)

                    # Write header if file is new
                    if not file_exists:
                        writer.writeheader()

                    # Write new items in small batches
                    batch_size = 10
                    for batch_start in range(0, len(new_items), batch_size):
                        batch_end = min(batch_start + batch_size, len(new_items))
                        batch = new_items[batch_start:batch_end]

                        for item in batch:
                            writer.writerow(item)

                        # Update progress
                        if progress_dialog:
                            progress_dialog.setValue(len(items_with_user_input) - len(new_items) + batch_end)
                            progress_dialog.setLabelText(f"Writing batch {batch_start//batch_size + 1}")

                        # Process events to keep UI responsive
                        QApplication.processEvents()

                print(f"Successfully wrote {len(new_items)} items to CSV")

            # Close progress dialog
            if progress_dialog:
                progress_dialog.setValue(len(items_with_user_input))
                progress_dialog.close()

            # Show detailed success/info message
            if added_count > 0:
                message = f"✅ Successfully added {added_count} items to shopping list!"
                if reactivated_count > 0:
                    message += f"\n   • {reactivated_count} items were re-activated (previously purchased, now needed again)"
                    message += f"\n   • {added_count - reactivated_count} completely new items"
                message += "\n\nItems were added with 'High' priority and 'Missing Ingredient' category."
            else:
                message = "ℹ️ No new items were added to the shopping list."

            if skipped_existing > 0:
                message += f"\n\n📋 Found {skipped_existing} items that already exist as pending in your shopping list:"
                message += "\n   • These items are already marked as 'Pending' to purchase"
                message += "\n   • Check the 'Shopping' tab to view existing items"
                message += "\n   • You can update quantities or status there if needed"

            if skipped_duplicates > 0:
                message += f"\n\n🔄 Consolidated {skipped_duplicates} duplicate ingredients across recipes."

            if len(items_with_user_input) > added_count:
                message += f"\n\n📊 Summary: Processed {len(items_with_user_input)} total entries → {added_count} new items added."

            # Add helpful tip
            if skipped_existing > 0:
                message += "\n\n💡 Tip: Navigate to the 'Shopping' tab to see all your shopping list items and their current status."

            # Show message with option to view shopping list
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Shopping List Update")
            msg_box.setText(message)

            if skipped_existing > 0:
                msg_box.setIcon(QMessageBox.Information)
                # Add button to view shopping list
                view_shopping_btn = msg_box.addButton("View Shopping List", QMessageBox.ActionRole)
                msg_box.addButton("OK", QMessageBox.AcceptRole)

                result = msg_box.exec()

                # Check if user clicked "View Shopping List"
                if msg_box.clickedButton() == view_shopping_btn:
                    self.navigate_to_shopping_list()
            else:
                msg_box.setIcon(QMessageBox.Information)
                msg_box.addButton("OK", QMessageBox.AcceptRole)
                msg_box.exec()

            print(f"Operation completed: Added {added_count}, Skipped existing {skipped_existing}, Skipped duplicates {skipped_duplicates}")

            # Notify parent app to refresh shopping list data
            try:
                parent_app = self.parent()
                while parent_app and not hasattr(parent_app, 'data'):
                    parent_app = parent_app.parent()

                if parent_app and hasattr(parent_app, 'data') and hasattr(parent_app, 'load_data'):
                    print("🔄 Refreshing parent app data to show new shopping list items...")
                    parent_app.load_data()  # Reload all data including shopping list
                    print("[SUCCESS] Parent app data refreshed")
                else:
                    print("⚠️ Could not find parent app to refresh data")
            except Exception as e:
                print(f"⚠️ Could not refresh parent app data: {e}")
                # Don't show error to user as the items were still added successfully

        except Exception as e:
            if progress_dialog:
                progress_dialog.close()
            print(f"Error in add_selected_to_shopping: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to add items to shopping list: {e}")

    def navigate_to_shopping_list(self):
        """Navigate to the shopping list tab"""
        try:
            # Find the parent application
            parent_app = self.parent()
            while parent_app and not hasattr(parent_app, 'show_shopping'):
                parent_app = parent_app.parent()

            if parent_app and hasattr(parent_app, 'show_shopping'):
                print("🔄 Navigating to Shopping List tab...")
                parent_app.show_shopping()
                print("[SUCCESS] Successfully navigated to Shopping List")
            else:
                print("⚠️ Could not find parent app to navigate to shopping list")
                QMessageBox.information(self, "Navigation",
                    "Please manually navigate to the 'Shopping' tab to view your shopping list items.")
        except Exception as e:
            print(f"⚠️ Error navigating to shopping list: {e}")
            QMessageBox.information(self, "Navigation",
                "Please manually navigate to the 'Shopping' tab to view your shopping list items.")

    def get_user_input_for_item(self, item_name, current_item, total_items):
        """Get user input for quantity, unit, and price for an item"""
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                       QLineEdit, QComboBox, QPushButton, QFormLayout,
                                       QDialogButtonBox, QDoubleSpinBox, QSpinBox)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Enter Details for Item ({current_item}/{total_items})")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Header
        header = QLabel(f"📝 Enter quantity and price for:")
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(header)

        # Item name (read-only)
        item_label = QLabel(f"🛒 {item_name}")
        item_label.setStyleSheet("font-size: 16px; color: #2563eb; font-weight: bold; padding: 10px; background-color: #eff6ff; border-radius: 6px; margin-bottom: 15px;")
        layout.addWidget(item_label)

        # Form layout
        form_layout = QFormLayout()

        # Quantity input
        quantity_spin = QDoubleSpinBox()
        quantity_spin.setRange(0.1, 9999.0)
        quantity_spin.setValue(1.0)
        quantity_spin.setDecimals(1)
        quantity_spin.setSuffix(" ")
        form_layout.addRow("📦 Quantity:", quantity_spin)

        # Unit selection
        unit_combo = QComboBox()
        unit_combo.addItems(['grams', 'kg', 'ml', 'units'])  # Only standardized units
        unit_combo.setCurrentText('grams')
        form_layout.addRow("📏 Unit:", unit_combo)

        # Price input
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0.0, 99999.0)
        price_spin.setValue(0.0)
        price_spin.setDecimals(2)
        price_spin.setPrefix("₹ ")
        form_layout.addRow("💰 Price:", price_spin)

        layout.addLayout(form_layout)

        # Note
        note_label = QLabel("💡 Tip: You can enter 0 for price if unknown - you can update it later in the shopping list.")
        note_label.setStyleSheet("font-size: 12px; color: #6b7280; font-style: italic; margin-top: 10px;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()

        skip_btn = QPushButton("⏭️ Skip Item")
        skip_btn.setStyleSheet("background-color: #6b7280; color: white; padding: 8px 16px; border-radius: 6px;")

        cancel_btn = QPushButton("❌ Cancel All")
        cancel_btn.setStyleSheet("background-color: #dc2626; color: white; padding: 8px 16px; border-radius: 6px;")

        ok_btn = QPushButton("✅ Add Item")
        ok_btn.setStyleSheet("background-color: #16a34a; color: white; padding: 8px 16px; border-radius: 6px;")
        ok_btn.setDefault(True)

        button_layout.addWidget(skip_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Connect buttons
        result = {'action': None}

        def on_ok():
            result['action'] = 'ok'
            dialog.accept()

        def on_skip():
            result['action'] = 'skip'
            dialog.accept()

        def on_cancel():
            result['action'] = 'cancel'
            dialog.reject()

        ok_btn.clicked.connect(on_ok)
        skip_btn.clicked.connect(on_skip)
        cancel_btn.clicked.connect(on_cancel)

        # Focus on quantity input
        quantity_spin.setFocus()
        quantity_spin.selectAll()

        # Execute dialog
        dialog_result = dialog.exec()

        if dialog_result == QDialog.Rejected or result['action'] == 'cancel':
            return None  # User cancelled

        if result['action'] == 'skip':
            return 'skip'  # Skip this item

        # Return user input
        return {
            'quantity': quantity_spin.value(),
            'unit': unit_combo.currentText(),
            'price': price_spin.value()
        }

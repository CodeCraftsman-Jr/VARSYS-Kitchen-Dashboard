"""
Kitchen Dashboard - Settings Module
This module provides the settings functionality for the Kitchen Dashboard application,
including currency settings and data management.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QGroupBox, QFormLayout,
                              QMessageBox, QFileDialog, QTextEdit, QSplitter,
                              QDoubleSpinBox)
from PySide6.QtCore import Qt, Signal
import logging
import traceback
from PySide6.QtGui import QFont, QColor
import os
import pandas as pd
import json
from datetime import datetime
import io
import logging
import json

# Import Firebase integration if available
try:
    from modules import firebase_integration
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class SettingsWidget(QWidget):
    """Widget for application settings including currency and data management"""
    
    # Signal to notify when currency is changed
    currency_changed = Signal(str)
    data_imported = Signal() # Signal to notify when data is imported
    
    def __init__(self, main_app, parent=None, data=None):
        super().__init__(parent)
        self.main_app = main_app # Store reference to the main application instance
        self.logger = logging.getLogger(__name__)
        self.data = data if data else {}
        
        # Initialize settings if not exists
        if 'settings' not in self.data:
            self.data['settings'] = {'currency': '₹'}  # Default to Indian Rupee
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the settings UI"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel("Settings")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(header)
        
        # Currency settings group
        currency_group = QGroupBox("Currency Settings")
        currency_layout = QFormLayout(currency_group)
        
        # Currency selector
        self.currency_combo = QComboBox()
        currencies = [
            ("Indian Rupee (₹)", "₹"),
            ("US Dollar ($)", "$"),
            ("Euro (€)", "€"),
            ("British Pound (£)", "£"),
            ("Japanese Yen (¥)", "¥")
        ]
        
        for display_name, symbol in currencies:
            self.currency_combo.addItem(display_name, symbol)
        
        # Set current currency from settings
        current_currency = self.data['settings'].get('currency', '₹')
        for i in range(self.currency_combo.count()):
            if self.currency_combo.itemData(i) == current_currency:
                self.currency_combo.setCurrentIndex(i)
                break
        
        # Initialize selected_currency based on the combo box's current state
        self.selected_currency = self.currency_combo.itemData(self.currency_combo.currentIndex())
        self.currency_combo.currentIndexChanged.connect(self.update_currency)
        currency_layout.addRow("Select Currency:", self.currency_combo)
        
        # Apply button
        self.apply_button = QPushButton("Apply Currency Changes")
        self.apply_button.clicked.connect(self.apply_currency_changes)
        currency_layout.addRow("", self.apply_button)
        
        layout.addWidget(currency_group)

        # Tax Settings Group
        tax_group = QGroupBox("Tax Settings (GST & SGST)")
        tax_layout = QFormLayout(tax_group)

        # GST Rate
        self.gst_rate_spinbox = QDoubleSpinBox()
        self.gst_rate_spinbox.setRange(0.0, 50.0)
        self.gst_rate_spinbox.setSingleStep(0.1)
        self.gst_rate_spinbox.setSuffix("%")
        self.gst_rate_spinbox.setValue(7.5)  # Default 7.5%
        tax_layout.addRow("GST Rate:", self.gst_rate_spinbox)

        # SGST Rate
        self.sgst_rate_spinbox = QDoubleSpinBox()
        self.sgst_rate_spinbox.setRange(0.0, 50.0)
        self.sgst_rate_spinbox.setSingleStep(0.1)
        self.sgst_rate_spinbox.setSuffix("%")
        self.sgst_rate_spinbox.setValue(7.5)  # Default 7.5%
        tax_layout.addRow("SGST Rate:", self.sgst_rate_spinbox)

        # Total Tax Rate (read-only display)
        self.total_tax_label = QLabel("15.0%")
        self.total_tax_label.setStyleSheet("font-weight: bold; color: #2563eb;")
        tax_layout.addRow("Total Tax Rate:", self.total_tax_label)

        # Connect spinboxes to update total
        self.gst_rate_spinbox.valueChanged.connect(self.update_total_tax_rate)
        self.sgst_rate_spinbox.valueChanged.connect(self.update_total_tax_rate)

        # Save Tax Settings button
        self.save_tax_button = QPushButton("Save Tax Settings")
        self.save_tax_button.clicked.connect(self.save_tax_settings)
        tax_layout.addRow("", self.save_tax_button)

        layout.addWidget(tax_group)

        # Load current tax settings
        self.load_tax_settings()

        # Data Import section (replacing sample data management)
        import_group = QGroupBox("Data Import")
        import_layout = QFormLayout(import_group)

        # Import data button
        self.import_data_button = QPushButton("Import Historical Data")
        self.import_data_button.setStyleSheet("background-color: #2563eb; color: white; padding: 8px 16px; border-radius: 6px;")
        self.import_data_button.clicked.connect(self.open_import_wizard)
        import_layout.addRow("Data Import:", self.import_data_button)

        # Import info label
        import_info = QLabel("Import sales data from Zomato, Swiggy, or other sources")
        import_info.setStyleSheet("color: #64748b; font-size: 11px;")
        import_layout.addRow("", import_info)

        layout.addWidget(import_group)
        
        # Data management group
        data_group = self.create_data_management_section()
        layout.addWidget(data_group)
        
        # Cloud Sync group (Firebase integration)
        if FIREBASE_AVAILABLE:
            cloud_group = QGroupBox("Cloud Sync")
            cloud_layout = QVBoxLayout(cloud_group)
            
            # Create form layout for controls
            form_layout = QFormLayout()
            
            # Sync status label
            self.sync_status_label = QLabel("Firebase connected. Ready to sync data.")
            self.sync_status_label.setStyleSheet("font-weight: bold;")
            form_layout.addRow("Status:", self.sync_status_label)
            
            # Buttons layout
            buttons_layout = QHBoxLayout()
            
            # Sync to cloud button
            self.sync_to_cloud_button = QPushButton("Sync Data to Cloud")
            self.sync_to_cloud_button.setStyleSheet("background-color: #2980b9; color: white; padding: 8px;")
            self.sync_to_cloud_button.clicked.connect(self.sync_to_cloud)
            buttons_layout.addWidget(self.sync_to_cloud_button)
            
            # Sync from cloud button
            self.sync_from_cloud_button = QPushButton("Sync Data from Cloud")
            self.sync_from_cloud_button.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
            self.sync_from_cloud_button.clicked.connect(self.sync_from_cloud)
            buttons_layout.addWidget(self.sync_from_cloud_button)

            # Full Sync button
            self.full_sync_button = QPushButton("Perform Full Sync (Upload then Download)")
            self.full_sync_button.setStyleSheet("background-color: #8e44ad; color: white; padding: 8px;")
            self.full_sync_button.clicked.connect(self.handle_manual_full_sync_request)
            buttons_layout.addWidget(self.full_sync_button)
            
            # Add buttons to form layout
            form_layout.addRow("", buttons_layout)
            
            # Add form to cloud layout
            cloud_layout.addLayout(form_layout)
            
            # Add a log display
            log_group = QGroupBox("Sync Log")
            log_layout = QVBoxLayout(log_group)
            
            # Create log text area
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)
            self.log_display.setMinimumHeight(150)
            self.log_display.setStyleSheet("background-color: #f5f5f5; font-family: Consolas, monospace;")
            log_layout.addWidget(self.log_display)
            
            # Add clear log button
            clear_log_button = QPushButton("Clear Log")
            clear_log_button.clicked.connect(self.clear_log)
            log_layout.addWidget(clear_log_button)
            
            # Add log group to cloud layout
            cloud_layout.addWidget(log_group)
            
            # Add cloud group to main layout
            layout.addWidget(cloud_group)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)

    def create_data_management_section(self):
        """Creates the data management section with refresh button."""
        data_group = QGroupBox("Data Management")
        data_layout = QFormLayout(data_group)
        data_layout.setSpacing(10)

        self.refresh_data_button = QPushButton("🔄 Refresh Data from Files")
        self.refresh_data_button.setFont(self.parent().button_font if self.parent() else QFont("Segoe UI", 10, QFont.Bold))
        self.refresh_data_button.setIcon(self.parent().create_icon("🔄") if self.parent() else QIcon())
        self.refresh_data_button.setToolTip("Reload all data from CSV files and update the application views.")
        self.refresh_data_button.clicked.connect(self.handle_refresh_data_request)
        self.refresh_data_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db; /* Blue */
                color: white;
                padding: 10px;
                border-radius: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        data_layout.addRow(self.refresh_data_button)
        
        # Add other data management buttons (Save, Restore, Clear) as previously defined
        # Save data button
        self.save_button = QPushButton("💾 Save Current Data to Backup")
        self.save_button.setFont(self.parent().button_font if self.parent() else QFont("Segoe UI", 10, QFont.Bold))
        self.save_button.setIcon(self.parent().create_icon("💾") if self.parent() else QIcon())
        self.save_button.setToolTip("Save all current data (inventory, recipes, etc.) to a local backup.")
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; /* Green */
                color: white;
                padding: 10px;
                border-radius: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        data_layout.addRow(self.save_button)

        # Restore data button
        self.restore_button = QPushButton("📂 Restore Data from Backup")
        self.restore_button.setFont(self.parent().button_font if self.parent() else QFont("Segoe UI", 10, QFont.Bold))
        self.restore_button.setIcon(self.parent().create_icon("📂") if self.parent() else QIcon())
        self.restore_button.setToolTip("Restore data from a previously saved local backup.")
        self.restore_button.clicked.connect(self.restore_data)
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; /* Orange */
                color: white;
                padding: 10px;
                border-radius: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        data_layout.addRow(self.restore_button)

        # Clear data button
        self.clear_button = QPushButton("🗑️ Clear All Application Data")
        self.clear_button.setFont(self.parent().button_font if self.parent() else QFont("Segoe UI", 10, QFont.Bold))
        self.clear_button.setIcon(self.parent().create_icon("🗑️") if self.parent() else QIcon())
        self.clear_button.setToolTip("WARNING: This will delete all data and reset the application.")
        self.clear_button.clicked.connect(self.clear_data)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; /* Red */
                color: white;
                padding: 10px;
                border-radius: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        data_layout.addRow(self.clear_button)       
        
        return data_group

    def load_tax_settings(self):
        """Load current tax settings from configuration file"""
        try:
            config_path = os.path.join('data', 'tax_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    tax_config = json.load(f)
                    tax_settings = tax_config.get('tax_settings', {})

                    # Convert from decimal to percentage for display
                    gst_rate = tax_settings.get('gst_rate', 0.075) * 100
                    sgst_rate = tax_settings.get('sgst_rate', 0.075) * 100

                    self.gst_rate_spinbox.setValue(gst_rate)
                    self.sgst_rate_spinbox.setValue(sgst_rate)
                    self.update_total_tax_rate()
        except Exception as e:
            self.logger.error(f"Error loading tax settings: {e}")

    def update_total_tax_rate(self):
        """Update the total tax rate display"""
        total_rate = self.gst_rate_spinbox.value() + self.sgst_rate_spinbox.value()
        self.total_tax_label.setText(f"{total_rate:.1f}%")

    def save_tax_settings(self):
        """Save tax settings to configuration file"""
        try:
            config_path = os.path.join('data', 'tax_config.json')

            # Convert from percentage to decimal for storage
            gst_rate = self.gst_rate_spinbox.value() / 100
            sgst_rate = self.sgst_rate_spinbox.value() / 100
            total_rate = gst_rate + sgst_rate

            tax_config = {
                "tax_settings": {
                    "gst_rate": gst_rate,
                    "sgst_rate": sgst_rate,
                    "total_tax_rate": total_rate,
                    "description": "GST (Goods and Services Tax) and SGST (State Goods and Services Tax) rates for pricing calculations",
                    "location": "India",
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                },
                "tax_breakdown": {
                    "gst_percentage": f"{self.gst_rate_spinbox.value():.1f}%",
                    "sgst_percentage": f"{self.sgst_rate_spinbox.value():.1f}%",
                    "total_percentage": f"{total_rate * 100:.1f}%",
                    "note": "GST and SGST are applied separately but calculated together for total tax amount"
                },
                "calculation_notes": {
                    "formula": "Total Tax = (Base Cost) × (GST Rate + SGST Rate)",
                    "base_cost_includes": "Cost of Making + Packaging Cost + Electricity Cost + Gas Cost + Other Charges",
                    "display_format": "Shows combined GST+SGST amount in pricing table"
                }
            }

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(tax_config, f, indent=2, ensure_ascii=False)

            QMessageBox.information(
                self,
                "Tax Settings Saved",
                f"Tax rates updated successfully:\nGST: {self.gst_rate_spinbox.value():.1f}%\nSGST: {self.sgst_rate_spinbox.value():.1f}%\nTotal: {total_rate * 100:.1f}%"
            )

            self.logger.info(f"Tax settings saved: GST={gst_rate:.3f}, SGST={sgst_rate:.3f}, Total={total_rate:.3f}")

        except Exception as e:
            self.logger.error(f"Error saving tax settings: {e}")
            QMessageBox.warning(
                self,
                "Save Error",
                f"Failed to save tax settings: {str(e)}"
            )

    def handle_manual_full_sync_request(self):
        if self.main_app and hasattr(self.main_app, 'trigger_manual_full_sync'):
            self.main_app.trigger_manual_full_sync()
        else:
            # Log details if main_app or method is missing
            detailed_error = "Main application link or method unavailable."
            if not self.main_app:
                detailed_error = "self.main_app is None."
                self.logger.error(f"SettingsWidget: Failed to trigger manual sync: {detailed_error}")
            elif not hasattr(self.main_app, 'trigger_manual_full_sync'):
                detailed_error = f"self.main_app (type: {type(self.main_app)}) does not have 'trigger_manual_full_sync'."
                self.logger.error(f"SettingsWidget: Failed to trigger manual sync: {detailed_error}")
            
            QMessageBox.critical(self, "Error", f"Cannot trigger manual sync. {detailed_error}")
            self.logger.error(f"SettingsWidget: Failed to trigger manual sync: {detailed_error} (summary).")

    def handle_refresh_data_request(self):
        """Handles the request to refresh data from files."""
        self.logger.info("Refresh Data from Files button clicked. Requesting main app to refresh.")
        if self.main_app and hasattr(self.main_app, 'refresh_all_tabs'):
            self.main_app.refresh_all_tabs()
            QMessageBox.information(self, "Data Refresh", "Application data has been reloaded from files.")
            self.logger.info("Main app refresh_all_tabs called successfully.")
        else:
            # Detailed logging for why the call might fail
            detailed_error = "Main application link or method unavailable."
            if not self.main_app:
                detailed_error = "self.main_app is None."
                self.logger.error(f"Failed to call refresh_all_tabs: {detailed_error}")
            elif not hasattr(self.main_app, 'refresh_all_tabs'):
                detailed_error = f"self.main_app (type: {type(self.main_app)}) does not have 'refresh_all_tabs'."
                self.logger.error(f"Failed to call refresh_all_tabs: {detailed_error}")
                # Log attributes only if main_app exists but lacks the method
                self.logger.error("Attributes of main_app object: " + str(dir(self.main_app)))
            else: # Should not happen if the main condition failed, but as a fallback
                detailed_error = f"Unknown issue with self.main_app (type: {type(self.main_app)})."
                self.logger.error(f"Failed to call refresh_all_tabs on main_app for an unknown reason: {detailed_error}")
            
            QMessageBox.warning(self, "Error", f"Could not trigger data refresh. {detailed_error}")
            # Summary error log
            self.logger.error(f"Failed to call refresh_all_tabs on main_app (summary). {detailed_error}")

    def update_currency(self, index):
        """Store the selected currency symbol"""
        self.selected_currency = self.currency_combo.itemData(index)
    
    def apply_currency_changes(self):
        """Apply the selected currency throughout the application"""
        # Update the settings
        self.data['settings']['currency'] = self.selected_currency
        
        # Emit signal to notify other widgets
        self.currency_changed.emit(self.selected_currency)
        
        QMessageBox.information(
            self,
            "Currency Updated",
            f"Currency has been updated to {self.currency_combo.currentText()}"
        )
    
    def save_data(self):
        """Save the current data to backup files"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Save each dataframe to the backup directory with proper encoding
            for key, df in self.data.items():
                if isinstance(df, pd.DataFrame):
                    backup_file = os.path.join(backup_dir, f"{key}_backup.csv")
                    df.to_csv(backup_file, index=False, encoding='utf-8')
            
            # Save currency setting with proper encoding
            settings_file = os.path.join(backup_dir, 'settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.data['settings'], f, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Data Saved",
                "Current data has been successfully backed up."
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Error",
                f"An error occurred while saving data: {str(e)}"
            )
    
    def restore_data(self):
        """Restore data from backup files"""
        try:
            # Check if backup directory exists
            backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_backup')
            if not os.path.exists(backup_dir):
                QMessageBox.warning(
                    self,
                    "Restore Error",
                    "No backup data found."
                )
                return
            
            # Confirm before restoring
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                "This will replace your current data with the backup data. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Restore each dataframe from the backup directory with proper encoding
                for key in self.data.keys():
                    if key != 'settings':  # Skip settings, handle separately
                        backup_file = os.path.join(backup_dir, f"{key}_backup.csv")
                        if os.path.exists(backup_file):
                            self.data[key] = pd.read_csv(backup_file, encoding='utf-8')
                
                # Restore currency setting if available with proper encoding
                settings_file = os.path.join(backup_dir, 'settings.json')
                if os.path.exists(settings_file):
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        self.data['settings'] = json.load(f)
                        
                    # Update the combo box to match the restored currency
                    for i in range(self.currency_combo.count()):
                        if self.currency_combo.itemData(i) == self.data['settings'].get('currency'):
                            self.currency_combo.setCurrentIndex(i)
                            break
                
                QMessageBox.information(
                    self,
                    "Data Restored",
                    "Data has been successfully restored from backup."
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Restore Error",
                f"An error occurred while restoring data: {str(e)}"
            )
    


    def _infer_category(self, item_name, item_type):
        """Infer category for an item (ingredient or recipe) based on its name and type."""
        name_lower = item_name.lower()
        if item_type == "recipe":
            if any(keyword in name_lower for keyword in ["coffee", "tea", "milk", "juice", "boost", "horlicks"]):
                return "Beverages"
            if any(keyword in name_lower for keyword in ["chutney", "gravy", "sambar", "kurma", "pickle"]):
                return "Condiments & Sauces"
            if any(keyword in name_lower for keyword in ["omelette", "bhurji", "podimas"]):
                 if "egg" in name_lower: return "Egg Dishes"
            if any(keyword in name_lower for keyword in ["dosa", "idli", "chapathi", "roast", "uthapam", "paniyaram", "parotta"]):
                return "Main Course - Tiffins"
            if "rice" in name_lower and not any(k in name_lower for k in ["milk"]): # avoid kheer/payasam if they were beverages
                return "Main Course - Rice"
            if any(keyword in name_lower for keyword in ["curry", "fry", "masala"]):
                return "Main Course - Curries/Sides"
            return "Main Course" # Default for recipes
        elif item_type == "ingredient":
            if any(keyword in name_lower for keyword in ["milk", "cheese", "paneer", "yogurt", "curd", "butter", "ghee"]):
                return "Dairy & Alternatives"
            if any(keyword in name_lower for keyword in ["onion", "tomato", "potato", "carrot", "spinach", "beans", "garlic", "ginger", "chilli", "lemon", "coconut"]):
                return "Fruits & Vegetables"
            if any(keyword in name_lower for keyword in ["chicken", "fish", "egg"]):
                return "Meat, Poultry & Seafood"
            if any(keyword in name_lower for keyword in ["rice", "wheat", "flour", "dal", "parupu", "gram", "batter"]):
                return "Grains, Legumes & Pasta"
            if any(keyword in name_lower for keyword in ["oil", "spice", "powder", "masala", "salt", "sugar"]):
                return "Pantry Staples"
            if any(keyword in name_lower for keyword in ["coffee", "tea", "boost", "horlicks"]):
                return "Beverages (Ingredients)"
            return "Groceries" # Default for ingredients
        return "Unknown"

    def open_import_wizard(self):
        """Open the data import wizard"""
        try:
            from .data_import_wizard import DataImportWizard

            wizard = DataImportWizard(self)
            wizard.data_imported.connect(self.handle_imported_data)
            wizard.exec()

        except ImportError as e:
            self.logger.error(f"Failed to import data wizard: {e}")
            QMessageBox.warning(
                self,
                "Import Wizard Error",
                "Data import wizard is not available. Please check the installation."
            )

    def handle_imported_data(self, results):
        """Handle data imported from wizard"""
        try:
            # Refresh the main application data
            if hasattr(self.main_app, 'load_data'):
                self.main_app.load_data()

            QMessageBox.information(
                self,
                "Import Complete",
                f"Successfully imported {results['records_count']} records of type {results['import_type']}"
            )

        except Exception as e:
            self.logger.error(f"Error handling imported data: {e}")
            QMessageBox.warning(
                self,
                "Import Error",
                f"Error processing imported data: {str(e)}"
            )

    def remove_sample_data(self):
        """Remove all sample data and reset to empty dataframes"""
        try:
            # Confirm before removing sample data
            reply = QMessageBox.question(
                self,
                "Confirm Remove Sample Data",
                "This will remove all data from your application and reset to empty dataframes. \n\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Create data directory if it doesn't exist
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
                os.makedirs(data_dir, exist_ok=True)
                
                # Define empty dataframes for all data types
                empty_dataframes = {
                    'inventory': ['item_id', 'item_name', 'category', 'quantity', 'unit', 'price_per_unit', 'location', 'expiry_date', 'reorder_level', 'total_value'],
                    'items': ['item_id', 'item_name', 'category', 'description', 'unit', 'default_cost'],
                    'categories': ['category_id', 'category_name', 'description'],
                    'meal_plan': ['day', 'meal_type', 'recipe_id', 'recipe_name', 'servings', 'prep_time', 'cook_time'],
                    'recipes': ['recipe_id', 'recipe_name', 'category', 'ingredients', 'instructions', 'servings', 'prep_time', 'cook_time', 'calories_per_serving'],
                    'budget': ['budget_id', 'category', 'amount', 'period', 'date'],
                    'sales': ['sale_id', 'item_name', 'quantity', 'price_per_unit', 'total_amount', 'customer', 'date'],
                    'shopping_list': ['item_id', 'item_name', 'category', 'quantity', 'unit', 'priority', 'estimated_cost', 'store', 'notes', 'status'],
                    'waste': ['waste_id', 'item_name', 'quantity', 'unit', 'reason', 'cost', 'date'],
                    'cleaning_maintenance': ['task_id', 'task_name', 'frequency', 'last_completed', 'next_due', 'priority', 'notes']
                }
                
                # Create empty CSV files with headers
                for key, columns in empty_dataframes.items():
                    df = pd.DataFrame(columns=columns)
                    df.to_csv(os.path.join(data_dir, f'{key}.csv'), index=False)
                    self.data[key] = df
                
                QMessageBox.information(
                    self,
                    "Sample Data Removed",
                    "All sample data has been removed from the application."
                )
                
                # Emit signal to notify other widgets that data has changed
                current_currency = self.data['settings'].get('currency', '₹')
                self.currency_changed.emit(current_currency)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Remove Sample Data Error",
                f"An error occurred while removing sample data: {str(e)}"
            )
    
    def add_log(self, message, level="info"):
        """Add a message to the log display"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Choose color based on level
            color = "black"  # Default color
            if level == "error":
                color = "red"
            elif level == "warning":
                color = "orange"
            elif level == "success":
                color = "green"
            
            # Format message with timestamp and color
            formatted_message = f"<span style='color:{color};'>[{timestamp}] {message}</span><br>"
            
            # Append to log display if available
            if hasattr(self, 'log_display') and self.log_display:
                # Get cursor and move to end
                cursor = self.log_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                
                # Insert HTML formatted text
                cursor.insertHtml(formatted_message)
                
                # Scroll to the new content
                self.log_display.setTextCursor(cursor)
                self.log_display.ensureCursorVisible()
        except Exception as e:
            # Fallback to console logging if something goes wrong
            print(f"[LOG {level.upper()}] {message} (Error: {str(e)})")
    
    def clear_log(self):
        """Clear the log display"""
        if hasattr(self, 'log_display'):
            self.log_display.clear()
            self.add_log("Log cleared")
    
    def sync_to_cloud(self, show_message=True):
        """Sync data to Firebase cloud storage"""
        if not FIREBASE_AVAILABLE:
            self.add_log("Firebase integration is not available", "error")
            if show_message:
                QMessageBox.warning(
                    self,
                    "Firebase Not Available",
                    "Firebase integration is not available. Please run setup_firebase.py first."
                )
            return False
        
        try:
            self.add_log("Starting sync to cloud operation...")
            # Get parent's firebase_sync instance if available
            if hasattr(self.parent(), 'firebase_sync'):
                # Use the parent's firebase_sync instance
                self.add_log("Using Firebase sync instance from parent")
                
                # Check if user is authenticated
                if not self.parent().firebase_sync.is_authenticated():
                    self.add_log("User not authenticated, authentication required", "warning")
                    # Show a prompt to authenticate if needed
                    reply = QMessageBox.question(
                        self,
                        "Authentication Required",
                        "You need to sign in to sync data to the cloud. Would you like to sign in now?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.add_log("Showing login dialog...")
                        if not self.parent().firebase_sync.show_login_dialog():
                            self.add_log("Login failed or cancelled", "error")
                            return False
                        self.add_log("Login successful", "success")
                    else:
                        self.add_log("Login cancelled by user", "warning")
                        return False
                
                # Attempt to sync data
                self.add_log("Syncing data to cloud...")
                success = self.parent().firebase_sync.sync_to_cloud(False)  # Don't show additional messages
                
                # Update status based on result
                if success:
                    self.add_log("Data successfully synced to cloud", "success")
                    if hasattr(self, 'sync_status_label'):
                        self.sync_status_label.setText("Data successfully synced to cloud.")
                    
                    if show_message:
                        QMessageBox.information(
                            self,
                            "Sync Successful",
                            "All data has been synced to Firebase cloud storage."
                        )
                else:
                    self.add_log("Failed to sync data to cloud", "error")
                    if hasattr(self, 'sync_status_label'):
                        self.sync_status_label.setText("Failed to sync data to cloud.")
                    
                    if show_message:
                        QMessageBox.warning(
                            self,
                            "Sync Failed",
                            "Failed to sync data to Firebase. Check the log for details."
                        )
                
                return success
            else:
                # No firebase_sync instance available
                self.add_log("Firebase sync is not initialized in the main application", "error")
                if show_message:
                    QMessageBox.warning(
                        self,
                        "Firebase Not Initialized",
                        "Firebase sync is not initialized in the main application."
                    )
                return False
        except Exception as e:
            self.add_log(f"Error in sync_to_cloud: {str(e)}", "error")
            if show_message:
                QMessageBox.critical(
                    self,
                    "Sync Error",
                    f"An error occurred while syncing to Firebase: {str(e)}"
                )
            return False
    
    def sync_from_cloud(self, show_message=True):
        """Sync data from Firebase cloud storage"""
        if not FIREBASE_AVAILABLE:
            self.add_log("Firebase integration is not available", "error")
            if show_message:
                QMessageBox.warning(
                    self,
                    "Firebase Not Available",
                    "Firebase integration is not available. Please run setup_firebase.py first."
                )
            return False
        
        try:
            self.add_log("Starting sync from cloud operation...")
            # Get parent's firebase_sync instance if available
            if hasattr(self.parent(), 'firebase_sync'):
                # Use the parent's firebase_sync instance
                self.add_log("Using Firebase sync instance from parent")
                
                # Check if user is authenticated
                if not self.parent().firebase_sync.is_authenticated():
                    self.add_log("User not authenticated, authentication required", "warning")
                    # Show a prompt to authenticate if needed
                    reply = QMessageBox.question(
                        self,
                        "Authentication Required",
                        "You need to sign in to download data from the cloud. Would you like to sign in now?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.add_log("Showing login dialog...")
                        if not self.parent().firebase_sync.show_login_dialog():
                            self.add_log("Login failed or cancelled", "error")
                            return False
                        self.add_log("Login successful", "success")
                    else:
                        self.add_log("Login cancelled by user", "warning")
                        return False
                
                # Confirm before syncing from cloud (will overwrite local data)
                reply = QMessageBox.question(
                    self,
                    "Confirm Download",
                    "This will download data from the cloud and overwrite your local data. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Attempt to sync data
                    self.add_log("Downloading data from cloud...")
                    success = self.parent().firebase_sync.sync_from_cloud(False)  # Don't show additional messages
                    
                    # Update status based on result
                    if success:
                        self.add_log("Data successfully downloaded from cloud", "success")
                        if hasattr(self, 'sync_status_label'):
                            self.sync_status_label.setText("Data successfully synced from cloud.")
                        
                        if show_message:
                            QMessageBox.information(
                                self,
                                "Download Successful",
                                "All data has been downloaded from Firebase cloud storage."
                            )
                    else:
                        self.add_log("Failed to download data from cloud", "error")
                        if hasattr(self, 'sync_status_label'):
                            self.sync_status_label.setText("Failed to sync data from cloud.")
                        
                        if show_message:
                            QMessageBox.warning(
                                self,
                                "Download Failed",
                                "Failed to download data from Firebase. Check the log for details."
                            )
                    
                    return success
                else:
                    self.add_log("Download cancelled by user", "warning")
                    return False
            else:
                # No firebase_sync instance available
                self.add_log("Firebase sync is not initialized in the main application", "error")
                if show_message:
                    QMessageBox.warning(
                        self,
                        "Firebase Not Initialized",
                        "Firebase sync is not initialized in the main application."
                    )
                return False
        except Exception as e:
            self.add_log(f"Error in sync_from_cloud: {str(e)}", "error")
            if show_message:
                QMessageBox.critical(
                    self,
                    "Sync Error",
                    f"An error occurred while syncing from Firebase: {str(e)}"
                )
            return False
    
    def clear_data(self):
        """Clear all application data and reset to defaults"""
        try:
            # Confirm before clearing data
            reply = QMessageBox.warning(
                self,
                "Confirm Data Reset",
                "This will delete ALL data and reset the application to its default state. \n\n"
                "This action cannot be undone! \n\n"
                "Are you sure you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Create data directory if it doesn't exist
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
                os.makedirs(data_dir, exist_ok=True)
                
                # Define the CSV files and their headers
                csv_files = {
                    'inventory.csv': ['item_id', 'item_name', 'category', 'quantity', 'unit', 'price_per_unit', 'location', 'expiry_date'],
                    'items.csv': ['item_id', 'item_name', 'unit', 'category', 'description', 'default_cost'],
                    'categories.csv': ['category_id', 'category_name', 'description'],
                    'meal_plans.csv': ['plan_id', 'plan_name', 'start_date', 'end_date', 'description'],
                    'recipes.csv': ['recipe_id', 'recipe_name', 'category', 'servings', 'prep_time', 'cook_time', 'description'],
                    'recipe_ingredients.csv': ['recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes'],
                    'shopping_list.csv': ['list_id', 'item_name', 'quantity', 'unit', 'category', 'priority', 'purchased'],
                    'waste.csv': ['waste_id', 'item_name', 'quantity', 'unit', 'reason', 'date', 'cost'],
                    'budget.csv': ['budget_id', 'category', 'amount', 'period', 'date'],
                    'cleaning_maintenance.csv': ['task_id', 'task_name', 'frequency', 'last_completed', 'next_due', 'priority', 'notes'],
                    'meal_plan_items.csv': ['meal_plan_item_id', 'meal_plan_id', 'day_of_week', 'meal_type', 'recipe_id', 'item_name', 'servings', 'notes'],
                    'sales.csv': ['sale_id', 'date', 'customer', 'recipe_name', 'quantity', 'price', 'total_amount', 'payment_method', 'notes']
                }
                
                # Create empty CSV files with headers
                for filename, headers in csv_files.items():
                    filepath = os.path.join(data_dir, filename)
                    # Create empty DataFrame with the specified headers
                    df = pd.DataFrame(columns=headers)
                    # Save to CSV
                    df.to_csv(filepath, index=False)
                    
                    # Also update the data dictionary
                    key = os.path.splitext(filename)[0]  # Remove .csv extension
                    self.data[key] = df
                
                # Reset settings to default (keep the current currency)
                current_currency = self.data['settings'].get('currency', '₹')
                self.data['settings'] = {'currency': current_currency}
                
                QMessageBox.information(
                    self,
                    "Data Reset Complete",
                    "All data has been cleared and the application has been reset to its default state."
                )
                
                # Emit signal to notify other widgets that data has changed
                self.currency_changed.emit(current_currency)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Reset Error",
                f"An error occurred while resetting data: {str(e)}"
            )

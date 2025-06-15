"""
Appliance Management Module
Manages cooking appliances and their electricity consumption mapping
"""

import os
import json
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QDoubleSpinBox, QLineEdit, QTextEdit,
    QGroupBox, QFormLayout, QMessageBox, QDialog, QDialogButtonBox,
    QHeaderView, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class ApplianceManagementWidget(QWidget):
    """Widget for managing cooking appliances and recipe mappings"""
    
    appliance_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.config_path = os.path.join('data', 'electricity_cost_config.json')
        self.config = self.load_config()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("⚡ Appliance & Electricity Management")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2563eb; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Current settings overview
        self.create_current_settings_section(layout)
        
        # Appliances management
        self.create_appliances_section(layout)
        
        # Recipe mapping section
        self.create_recipe_mapping_section(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
    
    def create_current_settings_section(self, parent_layout):
        """Create current settings overview section"""
        settings_group = QGroupBox("Current Electricity Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Current settings display
        self.current_appliance_label = QLabel()
        self.electricity_rate_label = QLabel()
        self.minimum_cost_label = QLabel()
        
        settings_layout.addWidget(QLabel("Default Appliance:"), 0, 0)
        settings_layout.addWidget(self.current_appliance_label, 0, 1)
        settings_layout.addWidget(QLabel("Electricity Rate:"), 1, 0)
        settings_layout.addWidget(self.electricity_rate_label, 1, 1)
        settings_layout.addWidget(QLabel("Minimum Cost:"), 2, 0)
        settings_layout.addWidget(self.minimum_cost_label, 2, 1)
        
        parent_layout.addWidget(settings_group)
    
    def create_appliances_section(self, parent_layout):
        """Create appliances management section"""
        appliances_group = QGroupBox("Available Appliances")
        appliances_layout = QVBoxLayout(appliances_group)
        
        # Appliances table
        self.appliances_table = QTableWidget()
        self.appliances_table.setColumnCount(4)
        self.appliances_table.setHorizontalHeaderLabels([
            "Appliance Name", "Power (kW)", "Efficiency", "Description"
        ])
        
        # Make table responsive
        header = self.appliances_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        appliances_layout.addWidget(self.appliances_table)
        
        # Appliance management buttons
        appliance_buttons = QHBoxLayout()
        
        self.add_appliance_btn = QPushButton("➕ Add Appliance")
        self.add_appliance_btn.clicked.connect(self.add_appliance)
        
        self.edit_appliance_btn = QPushButton("✏️ Edit Appliance")
        self.edit_appliance_btn.clicked.connect(self.edit_appliance)
        
        self.delete_appliance_btn = QPushButton("🗑️ Delete Appliance")
        self.delete_appliance_btn.clicked.connect(self.delete_appliance)
        
        appliance_buttons.addWidget(self.add_appliance_btn)
        appliance_buttons.addWidget(self.edit_appliance_btn)
        appliance_buttons.addWidget(self.delete_appliance_btn)
        appliance_buttons.addStretch()
        
        appliances_layout.addLayout(appliance_buttons)
        parent_layout.addWidget(appliances_group)
    
    def create_recipe_mapping_section(self, parent_layout):
        """Create recipe-to-appliance mapping section"""
        mapping_group = QGroupBox("Recipe-Appliance Mapping (Future Use)")
        mapping_layout = QVBoxLayout(mapping_group)
        
        info_label = QLabel("ℹ️ All recipes use basic ₹0.50 charge (tubelight only) by default.\n"
                           "Table shows only recipes mapped to electric appliances.\n"
                           "Use 'Map Recipe to Appliance' to add electric appliance mappings.")
        info_label.setStyleSheet("color: #6b7280; font-style: italic; padding: 10px;")
        mapping_layout.addWidget(info_label)
        
        # Recipe mapping table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(3)
        self.mapping_table.setHorizontalHeaderLabels([
            "Recipe Name", "Current Appliance", "Electricity Cost (15 min)"
        ])
        
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        mapping_layout.addWidget(self.mapping_table)
        
        # Mapping buttons
        mapping_buttons = QHBoxLayout()
        
        self.map_recipe_btn = QPushButton("🔗 Map Recipe to Appliance")
        self.map_recipe_btn.clicked.connect(self.map_recipe_to_appliance)
        
        self.reset_mapping_btn = QPushButton("🔄 Reset to Default")
        self.reset_mapping_btn.clicked.connect(self.reset_recipe_mapping)
        
        mapping_buttons.addWidget(self.map_recipe_btn)
        mapping_buttons.addWidget(self.reset_mapping_btn)
        mapping_buttons.addStretch()
        
        mapping_layout.addLayout(mapping_buttons)
        parent_layout.addWidget(mapping_group)
    
    def create_action_buttons(self, parent_layout):
        """Create action buttons"""
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_config)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)
    
    def load_config(self):
        """Load electricity configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            "electricity_settings": {
                "default_appliance": "Basic Kitchen Lighting",
                "electricity_rate_per_kwh_inr": 7.50,
                "minimum_cost_inr": 0.50,
                "use_cooking_time_only": True
            },
            "appliances": {
                "Basic Kitchen Lighting": {
                    "power_consumption_kw": 0.0,
                    "description": "Basic tubelight electricity charge for all items",
                    "efficiency_rating": "Standard"
                },
                "Electric Induction Cooktop": {
                    "power_consumption_kw": 2.0,
                    "description": "Electric induction cooking surface",
                    "efficiency_rating": "High"
                },
                "Mixer": {
                    "power_consumption_kw": 0.5,
                    "description": "Electric mixer for grinding and blending",
                    "efficiency_rating": "High"
                }
            },
            "recipe_appliance_mapping": {}
        }
    
    def load_data(self):
        """Load and display current data"""
        self.config = self.load_config()
        self.update_current_settings()
        self.populate_appliances_table()
        self.populate_mapping_table()
    
    def update_current_settings(self):
        """Update current settings display"""
        settings = self.config.get('electricity_settings', {})
        
        default_appliance = settings.get('default_appliance', 'Electric Induction Cooktop')
        rate = settings.get('electricity_rate_per_kwh_inr', 7.50)
        min_cost = settings.get('minimum_cost_inr', 0.25)
        
        self.current_appliance_label.setText(f"<b>{default_appliance}</b>")
        self.electricity_rate_label.setText(f"<b>₹{rate}/kWh</b> (Puducherry Commercial)")
        self.minimum_cost_label.setText(f"<b>₹{min_cost}</b>")
    
    def populate_appliances_table(self):
        """Populate appliances table"""
        appliances = self.config.get('appliances', {})
        self.appliances_table.setRowCount(len(appliances))
        
        for row, (name, data) in enumerate(appliances.items()):
            self.appliances_table.setItem(row, 0, QTableWidgetItem(name))
            self.appliances_table.setItem(row, 1, QTableWidgetItem(f"{data.get('power_consumption_kw', 0):.1f}"))
            self.appliances_table.setItem(row, 2, QTableWidgetItem(data.get('efficiency_rating', 'Medium')))
            self.appliances_table.setItem(row, 3, QTableWidgetItem(data.get('description', '')))
    
    def populate_mapping_table(self):
        """Populate recipe mapping table - show only electric appliance mappings"""
        # Get configuration data
        appliances = self.config.get('appliances', {})
        recipe_mapping = self.config.get('recipe_appliance_mapping', {})
        rate_per_kwh = self.config.get('electricity_settings', {}).get('electricity_rate_per_kwh_inr', 7.50)
        basic_charge = self.config.get('electricity_settings', {}).get('minimum_cost_inr', 0.50)

        # Filter to show only electric appliance mappings (not basic charges)
        electric_mappings = {k: v for k, v in recipe_mapping.items()
                           if not k.startswith('_') and v != 'Basic Kitchen Lighting'}

        if not electric_mappings:
            # Show message when no electric mappings exist
            self.mapping_table.setRowCount(1)
            self.mapping_table.setItem(0, 0, QTableWidgetItem("No electric appliance mappings"))
            self.mapping_table.setItem(0, 1, QTableWidgetItem("All recipes use basic ₹0.50 charge"))
            self.mapping_table.setItem(0, 2, QTableWidgetItem("₹0.50"))

            # Style the message row
            for col in range(3):
                item = self.mapping_table.item(0, col)
                if item:
                    item.setStyleSheet("color: #6b7280; font-style: italic;")
            return

        self.mapping_table.setRowCount(len(electric_mappings))

        for row, (recipe, appliance) in enumerate(electric_mappings.items()):
            # Calculate cost for this mapping
            appliance_data = appliances.get(appliance, {})
            power_kw = appliance_data.get('power_consumption_kw', 0.0)

            if power_kw > 0:
                # Calculate cost for 15 minutes
                cost_15_min = max(power_kw * (15/60) * rate_per_kwh, basic_charge)
            else:
                cost_15_min = basic_charge

            self.mapping_table.setItem(row, 0, QTableWidgetItem(recipe))
            self.mapping_table.setItem(row, 1, QTableWidgetItem(appliance))
            self.mapping_table.setItem(row, 2, QTableWidgetItem(f"₹{cost_15_min:.2f}"))
    
    def add_appliance(self):
        """Add new appliance"""
        dialog = ApplianceDialog(self)
        if dialog.exec() == QDialog.Accepted:
            appliance_data = dialog.get_appliance_data()
            self.config['appliances'][appliance_data['name']] = {
                'power_consumption_kw': appliance_data['power'],
                'efficiency_rating': appliance_data['efficiency'],
                'description': appliance_data['description']
            }
            self.populate_appliances_table()
            QMessageBox.information(self, "Success", f"Appliance '{appliance_data['name']}' added successfully!")
    
    def edit_appliance(self):
        """Edit selected appliance"""
        current_row = self.appliances_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an appliance to edit.")
            return
        
        appliance_name = self.appliances_table.item(current_row, 0).text()
        appliance_data = self.config['appliances'].get(appliance_name, {})
        
        dialog = ApplianceDialog(self, appliance_name, appliance_data)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_appliance_data()
            
            # Remove old entry if name changed
            if new_data['name'] != appliance_name:
                del self.config['appliances'][appliance_name]
            
            self.config['appliances'][new_data['name']] = {
                'power_consumption_kw': new_data['power'],
                'efficiency_rating': new_data['efficiency'],
                'description': new_data['description']
            }
            self.populate_appliances_table()
            QMessageBox.information(self, "Success", f"Appliance updated successfully!")
    
    def delete_appliance(self):
        """Delete selected appliance"""
        current_row = self.appliances_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an appliance to delete.")
            return
        
        appliance_name = self.appliances_table.item(current_row, 0).text()
        
        # Don't allow deleting the default appliance
        default_appliance = self.config.get('electricity_settings', {}).get('default_appliance')
        if appliance_name == default_appliance:
            QMessageBox.warning(self, "Warning", "Cannot delete the default appliance. Please change the default first.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete '{appliance_name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            del self.config['appliances'][appliance_name]
            self.populate_appliances_table()
            QMessageBox.information(self, "Success", f"Appliance '{appliance_name}' deleted successfully!")
    
    def map_recipe_to_appliance(self):
        """Map recipe to specific appliance"""
        dialog = RecipeMappingDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            recipe_name, appliance_name = dialog.get_mapping()
            if recipe_name and appliance_name:
                # Update the mapping
                if appliance_name == "Basic Kitchen Lighting":
                    # Remove mapping to use default
                    if recipe_name in self.config.get('recipe_appliance_mapping', {}):
                        del self.config['recipe_appliance_mapping'][recipe_name]
                else:
                    # Add specific mapping
                    if 'recipe_appliance_mapping' not in self.config:
                        self.config['recipe_appliance_mapping'] = {}
                    self.config['recipe_appliance_mapping'][recipe_name] = appliance_name

                self.populate_mapping_table()
                QMessageBox.information(self, "Success", f"Recipe '{recipe_name}' mapped to '{appliance_name}'!")
    
    def reset_recipe_mapping(self):
        """Reset recipe mapping to default"""
        self.config['recipe_appliance_mapping'] = {}
        self.populate_mapping_table()
        QMessageBox.information(self, "Success", "Recipe mapping reset to default!")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.appliance_updated.emit()
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.logger.info("Appliance configuration saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")


class ApplianceDialog(QDialog):
    """Dialog for adding/editing appliances"""
    
    def __init__(self, parent=None, appliance_name="", appliance_data=None):
        super().__init__(parent)
        self.appliance_data = appliance_data or {}
        self.setWindowTitle("Add Appliance" if not appliance_name else "Edit Appliance")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui(appliance_name)
    
    def setup_ui(self, appliance_name):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Appliance name
        self.name_input = QLineEdit(appliance_name)
        form_layout.addRow("Appliance Name:", self.name_input)
        
        # Power consumption
        self.power_input = QDoubleSpinBox()
        self.power_input.setRange(0.1, 10.0)
        self.power_input.setSingleStep(0.1)
        self.power_input.setSuffix(" kW")
        self.power_input.setValue(self.appliance_data.get('power_consumption_kw', 2.0))
        form_layout.addRow("Power Consumption:", self.power_input)
        
        # Efficiency rating
        self.efficiency_combo = QComboBox()
        self.efficiency_combo.addItems(["High", "Medium", "Low"])
        self.efficiency_combo.setCurrentText(self.appliance_data.get('efficiency_rating', 'Medium'))
        form_layout.addRow("Efficiency Rating:", self.efficiency_combo)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlainText(self.appliance_data.get('description', ''))
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_appliance_data(self):
        """Get appliance data from form"""
        return {
            'name': self.name_input.text().strip(),
            'power': self.power_input.value(),
            'efficiency': self.efficiency_combo.currentText(),
            'description': self.description_input.toPlainText().strip()
        }


class RecipeMappingDialog(QDialog):
    """Dialog for mapping recipes to appliances"""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Map Recipe to Appliance")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_recipes()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Recipe selection from database
        self.recipe_combo = QComboBox()
        self.recipe_combo.setEditable(True)  # Allow filtering
        self.recipe_combo.setInsertPolicy(QComboBox.NoInsert)
        form_layout.addRow("Select Recipe:", self.recipe_combo)

        # Appliance selection
        self.appliance_combo = QComboBox()
        appliances = self.config.get('appliances', {})

        # Add appliances to combo box
        for appliance_name in appliances.keys():
            self.appliance_combo.addItem(appliance_name)

        form_layout.addRow("Select Appliance:", self.appliance_combo)

        # Info label
        info_label = QLabel("💡 Select 'Basic Kitchen Lighting' to use ₹0.50 basic charge\n"
                           "Only Electric Induction Cooktop and Mixer will be saved to CSV")
        info_label.setStyleSheet("color: #6b7280; font-style: italic; padding: 5px;")
        form_layout.addRow(info_label)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_recipes(self):
        """Load recipes from database"""
        try:
            import pandas as pd
            recipes_path = os.path.join('data', 'recipes.csv')

            if os.path.exists(recipes_path):
                df = pd.read_csv(recipes_path)
                if 'recipe_name' in df.columns:
                    recipes = sorted(df['recipe_name'].dropna().unique().tolist())
                    self.recipe_combo.addItems(recipes)
                else:
                    self.recipe_combo.addItem("No recipes found - recipe_name column missing")
            else:
                self.recipe_combo.addItem("No recipes found - recipes.csv not found")

        except Exception as e:
            self.recipe_combo.addItem(f"Error loading recipes: {str(e)}")

    def get_mapping(self):
        """Get recipe-appliance mapping from form"""
        return self.recipe_combo.currentText().strip(), self.appliance_combo.currentText()

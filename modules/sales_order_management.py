"""
Sales Order Management Module
Simplified order management focused on the specific requirements:
- Date, Order ID, Platform (Swiggy/Zomato/Local + custom), Recipe selection, 
- Automatic price fetching, Manual discount entry, Total calculation
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QComboBox, QDateEdit, QFormLayout, QLineEdit,
                             QSpinBox, QDoubleSpinBox, QMessageBox, QDialog,
                             QDialogButtonBox, QFrame, QGridLayout, QGroupBox,
                             QScrollArea, QSizePolicy, QApplication)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor

class SalesOrderDialog(QDialog):
    """Comprehensive order dialog with detailed cost breakdown"""

    def __init__(self, recipes_data, parent=None):
        super().__init__(parent)
        self.recipes_data = recipes_data

        self.setWindowTitle("Create Sales Order - Detailed Cost Analysis")
        self.setModal(True)

        # Get screen dimensions and set appropriate size
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Set dialog size to 90% of screen size with maximum constraints
        dialog_width = min(800, int(screen_geometry.width() * 0.9))
        dialog_height = min(600, int(screen_geometry.height() * 0.85))

        self.resize(dialog_width, dialog_height)

        # Center the dialog on screen
        self.move(
            screen_geometry.center().x() - dialog_width // 2,
            screen_geometry.center().y() - dialog_height // 2
        )

        self.setup_ui()
    
    def setup_ui(self):
        """Setup the comprehensive order dialog with scrolling and compact layout"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Header (fixed at top)
        header_label = QLabel("Create Sales Order - Cost Analysis")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #0f172a; padding: 8px; background: #f8fafc; border-radius: 6px;")
        main_layout.addWidget(header_label)

        # Create scroll area for the form content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)

        # Create scrollable content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        scroll_layout.setSpacing(12)

        # Add all form sections to scrollable content
        self.create_date_section(scroll_layout)
        self.create_recipe_section(scroll_layout)
        self.create_cost_breakdown_section(scroll_layout)
        self.create_quantity_pricing_section(scroll_layout)
        self.create_final_totals_section(scroll_layout)

        # Add stretch to push content to top
        scroll_layout.addStretch()

        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Dialog buttons (fixed at bottom)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton[text="OK"] {
                background-color: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton[text="OK"]:hover {
                background-color: #2563eb;
            }
            QPushButton[text="Cancel"] {
                background-color: #6b7280;
                color: white;
                border: none;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #4b5563;
            }
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def create_date_section(self, parent_layout):
        """Create compact date selection section"""
        date_group = QGroupBox("📅 Order Details")
        date_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)

        date_layout = QFormLayout(date_group)
        date_layout.setSpacing(8)
        date_layout.setContentsMargins(12, 15, 12, 12)

        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet("padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px;")
        date_layout.addRow("Date:", self.date_edit)

        # Order ID (auto-generated)
        self.order_id_edit = QLineEdit()
        self.order_id_edit.setText(self.generate_order_id())
        self.order_id_edit.setReadOnly(True)
        self.order_id_edit.setStyleSheet("padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; background: #f9fafb; font-size: 13px;")
        date_layout.addRow("Order ID:", self.order_id_edit)

        parent_layout.addWidget(date_group)

    def create_recipe_section(self, parent_layout):
        """Create compact recipe selection section"""
        recipe_group = QGroupBox("🍽️ Recipe Selection")
        recipe_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)

        recipe_layout = QFormLayout(recipe_group)
        recipe_layout.setSpacing(8)
        recipe_layout.setContentsMargins(12, 15, 12, 12)

        # Recipe dropdown
        self.recipe_combo = QComboBox()
        self.recipe_combo.setStyleSheet("padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px;")
        self.populate_recipes()
        self.recipe_combo.currentTextChanged.connect(self.on_recipe_changed)
        recipe_layout.addRow("Select Recipe:", self.recipe_combo)

        parent_layout.addWidget(recipe_group)

    def create_cost_breakdown_section(self, parent_layout):
        """Create compact cost breakdown section with grid layout"""
        self.cost_breakdown_group = QGroupBox("💰 Cost Breakdown Analysis")
        self.cost_breakdown_group.setVisible(False)  # Hidden until recipe selected
        self.cost_breakdown_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #374151;
                border: 2px solid #fbbf24;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background: #fffbeb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)

        # Use grid layout for compact display
        breakdown_layout = QGridLayout(self.cost_breakdown_group)
        breakdown_layout.setSpacing(8)
        breakdown_layout.setContentsMargins(12, 15, 12, 12)

        # Row 1: Packing materials
        breakdown_layout.addWidget(QLabel("🎁 Packing:"), 0, 0)
        self.packing_materials_label = QLabel("No recipe selected")
        self.packing_materials_label.setStyleSheet("color: #64748b; font-style: italic; font-size: 12px;")
        self.packing_materials_label.setWordWrap(True)
        breakdown_layout.addWidget(self.packing_materials_label, 0, 1)

        self.packing_cost_label = QLabel("₹0.00")
        self.packing_cost_label.setStyleSheet("font-weight: 600; color: #059669; font-size: 13px;")
        breakdown_layout.addWidget(self.packing_cost_label, 0, 2)

        # Row 2: Preparation materials
        breakdown_layout.addWidget(QLabel("🍳 Ingredients:"), 1, 0)
        self.prep_materials_label = QLabel("No recipe selected")
        self.prep_materials_label.setStyleSheet("color: #64748b; font-style: italic; font-size: 12px;")
        self.prep_materials_label.setWordWrap(True)
        breakdown_layout.addWidget(self.prep_materials_label, 1, 1)

        self.prep_cost_label = QLabel("₹0.00")
        self.prep_cost_label.setStyleSheet("font-weight: 600; color: #059669; font-size: 13px;")
        breakdown_layout.addWidget(self.prep_cost_label, 1, 2)

        # Row 3: Gas charges
        breakdown_layout.addWidget(QLabel("⛽ Gas:"), 2, 0)
        gas_desc_label = QLabel("Cooking gas consumption")
        gas_desc_label.setStyleSheet("color: #64748b; font-size: 12px;")
        breakdown_layout.addWidget(gas_desc_label, 2, 1)

        self.gas_charges_label = QLabel("₹0.00")
        self.gas_charges_label.setStyleSheet("font-weight: 600; color: #f59e0b; font-size: 13px;")
        breakdown_layout.addWidget(self.gas_charges_label, 2, 2)

        # Row 4: Electricity charges
        breakdown_layout.addWidget(QLabel("⚡ Electricity:"), 3, 0)
        elec_desc_label = QLabel("Equipment power usage")
        elec_desc_label.setStyleSheet("color: #64748b; font-size: 12px;")
        breakdown_layout.addWidget(elec_desc_label, 3, 1)

        self.electricity_charges_label = QLabel("₹0.00")
        self.electricity_charges_label.setStyleSheet("font-weight: 600; color: #3b82f6; font-size: 13px;")
        breakdown_layout.addWidget(self.electricity_charges_label, 3, 2)

        # Row 5: Total cost (spanning all columns)
        total_label = QLabel("📊 Total Cost of Making:")
        total_label.setStyleSheet("font-weight: 700; color: #dc2626; font-size: 14px;")
        breakdown_layout.addWidget(total_label, 4, 0, 1, 2)

        self.total_cost_making_label = QLabel("₹0.00")
        self.total_cost_making_label.setStyleSheet("font-weight: 700; color: #dc2626; font-size: 16px; background: #fef2f2; padding: 4px 8px; border-radius: 4px;")
        breakdown_layout.addWidget(self.total_cost_making_label, 4, 2)

        # Set column stretch
        breakdown_layout.setColumnStretch(1, 1)  # Middle column stretches

        parent_layout.addWidget(self.cost_breakdown_group)

    def create_quantity_pricing_section(self, parent_layout):
        """Create compact quantity and pricing section"""
        self.quantity_pricing_group = QGroupBox("📊 Quantity & Pricing")
        self.quantity_pricing_group.setVisible(False)  # Hidden until recipe selected
        self.quantity_pricing_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #374151;
                border: 2px solid #10b981;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background: #f0fdf4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)

        qp_layout = QGridLayout(self.quantity_pricing_group)
        qp_layout.setSpacing(8)
        qp_layout.setContentsMargins(12, 15, 12, 12)

        # Row 1: Quantity
        qp_layout.addWidget(QLabel("Quantity:"), 0, 0)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setStyleSheet("padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px;")
        self.quantity_spin.valueChanged.connect(self.calculate_totals)
        qp_layout.addWidget(self.quantity_spin, 0, 1)

        # Row 2: Our pricing (auto-fetched, uneditable)
        qp_layout.addWidget(QLabel("Our Pricing:"), 1, 0)
        self.our_pricing_label = QLabel("₹0.00")
        self.our_pricing_label.setStyleSheet("font-weight: 600; color: #059669; font-size: 14px; background: #dcfce7; padding: 6px 8px; border-radius: 4px;")
        qp_layout.addWidget(self.our_pricing_label, 1, 1)

        auto_label = QLabel("(Auto-fetched)")
        auto_label.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        qp_layout.addWidget(auto_label, 1, 2)

        # Row 3: Subtotal before discount
        qp_layout.addWidget(QLabel("Subtotal:"), 2, 0)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-weight: 600; color: #0f172a; font-size: 14px;")
        qp_layout.addWidget(self.subtotal_label, 2, 1)

        subtotal_desc = QLabel("(Qty × Price)")
        subtotal_desc.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        qp_layout.addWidget(subtotal_desc, 2, 2)

        parent_layout.addWidget(self.quantity_pricing_group)

    def create_final_totals_section(self, parent_layout):
        """Create compact final totals section"""
        self.final_totals_group = QGroupBox("🎯 Final Pricing & Profit")
        self.final_totals_group.setVisible(False)  # Hidden until recipe selected
        self.final_totals_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                color: #374151;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background: #eff6ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background: white;
            }
        """)

        ft_layout = QGridLayout(self.final_totals_group)
        ft_layout.setSpacing(8)
        ft_layout.setContentsMargins(12, 15, 12, 12)

        # Row 1: Manual discount entry
        ft_layout.addWidget(QLabel("💸 Discount:"), 0, 0)
        self.discount_edit = QDoubleSpinBox()
        self.discount_edit.setRange(0, 9999)
        self.discount_edit.setDecimals(2)
        self.discount_edit.setSuffix(" ₹")
        self.discount_edit.setStyleSheet("padding: 6px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px;")
        self.discount_edit.valueChanged.connect(self.calculate_totals)
        ft_layout.addWidget(self.discount_edit, 0, 1)

        # Row 2: Final price after discount
        final_price_title = QLabel("🏆 Final Price:")
        final_price_title.setStyleSheet("font-weight: 700; color: #059669; font-size: 14px;")
        ft_layout.addWidget(final_price_title, 1, 0)

        self.final_price_label = QLabel("₹0.00")
        self.final_price_label.setStyleSheet("font-weight: 700; color: #059669; font-size: 16px; background: #dcfce7; padding: 8px 12px; border-radius: 6px; border: 2px solid #059669;")
        ft_layout.addWidget(self.final_price_label, 1, 1)

        # Row 3: Profit analysis
        ft_layout.addWidget(QLabel("📈 Profit:"), 2, 0)
        self.profit_label = QLabel("₹0.00")
        self.profit_label.setStyleSheet("font-weight: 600; color: #10b981; font-size: 14px;")
        ft_layout.addWidget(self.profit_label, 2, 1)

        ft_layout.addWidget(QLabel("📊 Profit %:"), 3, 0)
        self.profit_percentage_label = QLabel("0%")
        self.profit_percentage_label.setStyleSheet("font-weight: 600; color: #10b981; font-size: 14px;")
        ft_layout.addWidget(self.profit_percentage_label, 3, 1)

        parent_layout.addWidget(self.final_totals_group)

    def create_order_form(self, parent_layout):
        """Create order details form"""
        form_group = QGroupBox("Order Details")
        form_layout = QFormLayout(form_group)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        form_layout.addRow("Date:", self.date_edit)
        
        # Order ID (auto-generated)
        self.order_id_edit = QLineEdit()
        self.order_id_edit.setText(self.generate_order_id())
        self.order_id_edit.setReadOnly(True)
        self.order_id_edit.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; background: #f9fafb;")
        form_layout.addRow("Order ID:", self.order_id_edit)
        
        # Platform selection with custom option
        platform_layout = QHBoxLayout()
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Swiggy", "Zomato", "Local", "Other"])
        self.platform_combo.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        self.platform_combo.currentTextChanged.connect(self.on_platform_changed)
        platform_layout.addWidget(self.platform_combo)
        
        # Custom platform entry (hidden by default)
        self.custom_platform_edit = QLineEdit()
        self.custom_platform_edit.setPlaceholderText("Enter custom platform name")
        self.custom_platform_edit.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        self.custom_platform_edit.setVisible(False)
        platform_layout.addWidget(self.custom_platform_edit)
        
        form_layout.addRow("Platform:", platform_layout)
        
        parent_layout.addWidget(form_group)
    
    def create_recipe_section(self, parent_layout):
        """Create recipe selection section"""
        recipe_group = QGroupBox("Recipe Selection")
        recipe_layout = QFormLayout(recipe_group)
        
        # Recipe dropdown
        self.recipe_combo = QComboBox()
        self.recipe_combo.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        self.populate_recipes()
        self.recipe_combo.currentTextChanged.connect(self.on_recipe_changed)
        recipe_layout.addRow("Recipe:", self.recipe_combo)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        self.quantity_spin.valueChanged.connect(self.calculate_totals)
        recipe_layout.addRow("Quantity:", self.quantity_spin)
        
        parent_layout.addWidget(recipe_group)
    
    def create_pricing_section(self, parent_layout):
        """Create pricing and totals section"""
        pricing_group = QGroupBox("Pricing & Totals")
        pricing_layout = QFormLayout(pricing_group)
        
        # Selling price (auto-fetched, read-only)
        self.selling_price_label = QLabel("₹0.00")
        self.selling_price_label.setStyleSheet("font-weight: 600; color: #059669; font-size: 14px;")
        pricing_layout.addRow("Selling Price (Our Pricing):", self.selling_price_label)
        
        # Subtotal (calculated)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-weight: 600; color: #0f172a; font-size: 14px;")
        pricing_layout.addRow("Subtotal:", self.subtotal_label)
        
        # Manual discount entry
        self.discount_edit = QDoubleSpinBox()
        self.discount_edit.setRange(0, 9999)
        self.discount_edit.setDecimals(2)
        self.discount_edit.setSuffix(" ₹")
        self.discount_edit.setStyleSheet("padding: 8px; border: 1px solid #d1d5db; border-radius: 4px;")
        self.discount_edit.valueChanged.connect(self.calculate_totals)
        pricing_layout.addRow("Discount:", self.discount_edit)
        
        # Total after discount
        self.total_label = QLabel("₹0.00")
        self.total_label.setStyleSheet("font-weight: 700; color: #059669; font-size: 16px;")
        pricing_layout.addRow("Total:", self.total_label)
        
        parent_layout.addWidget(pricing_group)
    
    def populate_recipes(self):
        """Populate recipe dropdown"""
        try:
            if hasattr(self.recipes_data, 'recipe_pricing_data'):
                recipes = list(self.recipes_data.recipe_pricing_data.keys())
            else:
                # Fallback recipes
                recipes = [
                    "Dosa", "Masala Dosa", "Idli(2 pcs)", "Coffee", "Tea(250 ml)",
                    "Chicken Gravy", "Fish Kolambu(Parai Fish)", "Plain Rice"
                ]
            
            self.recipe_combo.addItems(["Select Recipe..."] + sorted(recipes))
            
        except Exception as e:
            logging.error(f"Error populating recipes: {e}")
            self.recipe_combo.addItems(["Select Recipe..."])
    
    def on_platform_changed(self):
        """Handle platform selection change"""
        platform = self.platform_combo.currentText()
        
        if platform == "Other":
            self.custom_platform_edit.setVisible(True)
            self.custom_platform_edit.setFocus()
        else:
            self.custom_platform_edit.setVisible(False)
    
    def on_recipe_changed(self):
        """Handle recipe selection change and show detailed cost breakdown"""
        recipe_name = self.recipe_combo.currentText()

        if recipe_name == "Select Recipe...":
            # Hide all sections
            self.cost_breakdown_group.setVisible(False)
            self.quantity_pricing_group.setVisible(False)
            self.final_totals_group.setVisible(False)
        else:
            # Show all sections
            self.cost_breakdown_group.setVisible(True)
            self.quantity_pricing_group.setVisible(True)
            self.final_totals_group.setVisible(True)

            # Load detailed cost breakdown
            self.load_recipe_cost_breakdown(recipe_name)

            # Get and display our pricing
            price = self.get_recipe_price(recipe_name)
            self.our_pricing_label.setText(f"₹{price:.2f}")

        self.calculate_totals()

    def load_recipe_cost_breakdown(self, recipe_name):
        """Load detailed cost breakdown for selected recipe"""
        try:
            # Get recipe data from pricing system
            recipe_data = self.get_recipe_data(recipe_name)

            # Packing materials
            packing_materials = recipe_data.get('packing_materials', 'Standard packaging')
            packing_cost = recipe_data.get('packing_cost', 5.0)

            self.packing_materials_label.setText(packing_materials)
            self.packing_cost_label.setText(f"₹{packing_cost:.2f}")

            # Preparation materials (ingredients)
            prep_materials = recipe_data.get('ingredients', 'Standard ingredients')
            prep_cost = recipe_data.get('ingredient_cost', 25.0)

            self.prep_materials_label.setText(prep_materials)
            self.prep_cost_label.setText(f"₹{prep_cost:.2f}")

            # Utility charges
            gas_charges = recipe_data.get('gas_charges', 3.0)
            electricity_charges = recipe_data.get('electricity_charges', 2.0)

            self.gas_charges_label.setText(f"₹{gas_charges:.2f}")
            self.electricity_charges_label.setText(f"₹{electricity_charges:.2f}")

            # Total cost of making
            total_cost = packing_cost + prep_cost + gas_charges + electricity_charges
            self.total_cost_making_label.setText(f"₹{total_cost:.2f}")

            # Store for calculations
            self.current_recipe_data = recipe_data

        except Exception as e:
            logging.error(f"Error loading recipe cost breakdown: {e}")
            # Set default values
            self.packing_materials_label.setText("Standard packaging")
            self.packing_cost_label.setText("₹5.00")
            self.prep_materials_label.setText("Standard ingredients")
            self.prep_cost_label.setText("₹25.00")
            self.gas_charges_label.setText("₹3.00")
            self.electricity_charges_label.setText("₹2.00")
            self.total_cost_making_label.setText("₹35.00")

            self.current_recipe_data = {
                'packing_cost': 5.0,
                'ingredient_cost': 25.0,
                'gas_charges': 3.0,
                'electricity_charges': 2.0
            }

    def get_recipe_data(self, recipe_name):
        """Get comprehensive recipe data including cost breakdown from pricing tab"""
        try:
            # First try to get data from pricing management system
            if hasattr(self.recipes_data, 'recipe_pricing_data'):
                base_data = self.recipes_data.recipe_pricing_data.get(recipe_name, {})

                # Enhanced data with cost breakdown from pricing tab
                enhanced_data = {
                    'our_pricing': base_data.get('our_pricing', 50.0),
                    'others_pricing': base_data.get('others_pricing', 50.0),
                    'cooking_time': base_data.get('cooking_time', '15 mins'),
                    'packing_materials': self.get_packing_materials_from_pricing(recipe_name),
                    'packing_cost': self.get_packing_cost_from_pricing(recipe_name),
                    'ingredients': self.get_ingredients_from_pricing(recipe_name),
                    'ingredient_cost': self.get_ingredient_cost_from_pricing(recipe_name),
                    'gas_charges': self.get_gas_charges_from_pricing(recipe_name),
                    'electricity_charges': self.get_electricity_charges_from_pricing(recipe_name)
                }

                return enhanced_data
            else:
                # Fallback data
                return self.get_fallback_recipe_data(recipe_name)

        except Exception as e:
            logging.error(f"Error getting recipe data: {e}")
            return self.get_fallback_recipe_data(recipe_name)

    def get_packing_materials_from_pricing(self, recipe_name):
        """Get actual packing materials from recipe_packing_materials.csv"""
        try:
            # Try to get actual materials from CSV data
            actual_materials = self.get_actual_packing_materials(recipe_name)
            if actual_materials:
                return actual_materials

            # Try to get from pricing data as fallback
            if hasattr(self.recipes_data, 'data') and 'pricing' in self.recipes_data.data:
                pricing_df = self.recipes_data.data['pricing']
                recipe_row = pricing_df[pricing_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    # Get packing materials from pricing data
                    return recipe_row.iloc[0].get('packing_materials', self.get_packing_materials(recipe_name))

            # Fallback to default mapping
            return self.get_packing_materials(recipe_name)
        except Exception as e:
            logging.error(f"Error getting packing materials from pricing: {e}")
            return self.get_packing_materials(recipe_name)

    def get_actual_packing_materials(self, recipe_name):
        """Get actual packing materials list from recipe_packing_materials.csv"""
        try:
            import os
            import pandas as pd

            # Load recipe packing materials data
            packing_file = os.path.join('data', 'recipe_packing_materials.csv')
            if not os.path.exists(packing_file):
                logging.warning(f"Packing file not found: {packing_file}")
                return ""

            packing_df = pd.read_csv(packing_file)

            # Filter for the specific recipe (exact match, case-sensitive)
            recipe_materials = packing_df[packing_df['recipe_name'].str.strip() == recipe_name.strip()]

            if recipe_materials.empty:
                logging.info(f"No packing materials found for recipe: {recipe_name}")
                return ""

            # Get list of materials with quantities
            materials_list = []
            for _, row in recipe_materials.iterrows():
                material_name = row['material_name']
                quantity = row['quantity_needed']
                cost = row['cost_per_recipe']

                if quantity == 1.0:
                    materials_list.append(f"{material_name} (₹{cost:.2f})")
                else:
                    materials_list.append(f"{material_name} x{quantity} (₹{cost:.2f})")

            result = ", ".join(materials_list)
            logging.info(f"Actual packing materials for {recipe_name}: {result}")
            return result

        except Exception as e:
            logging.error(f"Error getting actual packing materials for {recipe_name}: {e}")
            return ""

    def get_packing_cost_from_pricing(self, recipe_name):
        """Get actual packing cost from recipe_packing_materials.csv"""
        try:
            # Try to calculate from actual packing materials data
            total_packing_cost = self.calculate_actual_packing_cost(recipe_name)
            if total_packing_cost > 0:
                return total_packing_cost

            # Try to get from pricing data as fallback
            if hasattr(self.recipes_data, 'data') and 'pricing' in self.recipes_data.data:
                pricing_df = self.recipes_data.data['pricing']
                recipe_row = pricing_df[pricing_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    # Get packing cost from pricing data
                    return float(recipe_row.iloc[0].get('pkg_cost', self.get_packing_cost(recipe_name)))

            # Fallback to default mapping
            return self.get_packing_cost(recipe_name)
        except Exception as e:
            logging.error(f"Error getting packing cost from pricing: {e}")
            return self.get_packing_cost(recipe_name)

    def calculate_actual_packing_cost(self, recipe_name):
        """Calculate actual packing cost from in-memory data first, then CSV fallback"""
        try:
            # First try to get from in-memory data (from Packing Materials Management interface)
            if hasattr(self.recipes_data, 'data') and 'recipe_packing_materials' in self.recipes_data.data:
                recipe_materials_df = self.recipes_data.data['recipe_packing_materials']

                if not recipe_materials_df.empty:
                    # Filter for the specific recipe
                    recipe_materials = recipe_materials_df[recipe_materials_df['recipe_name'].str.strip() == recipe_name.strip()]

                    if not recipe_materials.empty:
                        # Sum up all packing costs for this recipe from in-memory data
                        total_cost = recipe_materials['cost_per_recipe'].sum()

                        # Debug information
                        materials_list = []
                        for _, row in recipe_materials.iterrows():
                            materials_list.append(f"{row['material_name']} (₹{row['cost_per_recipe']:.2f})")

                        logging.info(f"✅ Packing cost from IN-MEMORY data for {recipe_name}: {', '.join(materials_list)} = ₹{total_cost:.2f}")
                        return float(total_cost)

            # Fallback to CSV file if in-memory data is not available
            import os
            import pandas as pd

            packing_file = os.path.join('data', 'recipe_packing_materials.csv')
            if not os.path.exists(packing_file):
                logging.warning(f"Packing file not found: {packing_file}")
                return 0

            packing_df = pd.read_csv(packing_file)

            # Filter for the specific recipe (exact match)
            recipe_materials = packing_df[packing_df['recipe_name'].str.strip() == recipe_name.strip()]

            if recipe_materials.empty:
                logging.info(f"No packing materials found for recipe: {recipe_name}")
                return 0

            # Sum up all packing costs for this recipe
            total_cost = recipe_materials['cost_per_recipe'].sum()

            # Debug information
            materials_list = []
            for _, row in recipe_materials.iterrows():
                materials_list.append(f"{row['material_name']} (₹{row['cost_per_recipe']:.2f})")

            logging.info(f"⚠️ Packing cost from CSV FALLBACK for {recipe_name}: {', '.join(materials_list)} = ₹{total_cost:.2f}")
            return float(total_cost)

        except Exception as e:
            logging.error(f"Error calculating actual packing cost for {recipe_name}: {e}")
            return 0

    def get_ingredients_from_pricing(self, recipe_name):
        """Get ingredients from pricing tab data"""
        try:
            # Try to get from recipe/inventory data
            if hasattr(self.recipes_data, 'data') and 'recipes' in self.recipes_data.data:
                recipes_df = self.recipes_data.data['recipes']
                recipe_row = recipes_df[recipes_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    # Get ingredients from recipe data
                    ingredients = recipe_row.iloc[0].get('ingredients', '')
                    if ingredients:
                        return ingredients

            # Fallback to default mapping
            return self.get_ingredients(recipe_name)
        except Exception as e:
            logging.error(f"Error getting ingredients from pricing: {e}")
            return self.get_ingredients(recipe_name)

    def get_ingredient_cost_from_pricing(self, recipe_name):
        """Get ingredient cost from pricing tab data"""
        try:
            # Try to get from pricing data first
            if hasattr(self.recipes_data, 'data') and 'pricing' in self.recipes_data.data:
                pricing_df = self.recipes_data.data['pricing']
                recipe_row = pricing_df[pricing_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    # Get cost of making from pricing data
                    cost_of_making = float(recipe_row.iloc[0].get('cost_of_making', 0))
                    if cost_of_making > 0:
                        return cost_of_making

            # Fallback to default mapping
            return self.get_ingredient_cost(recipe_name)
        except Exception as e:
            logging.error(f"Error getting ingredient cost from pricing: {e}")
            return self.get_ingredient_cost(recipe_name)

    def get_gas_charges_from_pricing(self, recipe_name):
        """Get gas charges from pricing tab data"""
        try:
            # Try to get from pricing data first
            if hasattr(self.recipes_data, 'data') and 'pricing' in self.recipes_data.data:
                pricing_df = self.recipes_data.data['pricing']
                recipe_row = pricing_df[pricing_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    # Get gas cost from pricing data
                    return float(recipe_row.iloc[0].get('gas_cost', self.get_gas_charges(recipe_name)))

            # Fallback to default mapping
            return self.get_gas_charges(recipe_name)
        except Exception as e:
            logging.error(f"Error getting gas charges from pricing: {e}")
            return self.get_gas_charges(recipe_name)

    def get_electricity_charges_from_pricing(self, recipe_name):
        """Get electricity charges from pricing tab data"""
        try:
            # Try to get from pricing data first
            if hasattr(self.recipes_data, 'data') and 'pricing' in self.recipes_data.data:
                pricing_df = self.recipes_data.data['pricing']
                recipe_row = pricing_df[pricing_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    # Get electricity cost from pricing data
                    return float(recipe_row.iloc[0].get('electricity_cost', self.get_electricity_charges(recipe_name)))

            # Fallback to default mapping
            return self.get_electricity_charges(recipe_name)
        except Exception as e:
            logging.error(f"Error getting electricity charges from pricing: {e}")
            return self.get_electricity_charges(recipe_name)

    def get_packing_materials(self, recipe_name):
        """Get packing materials for recipe"""
        # This would ideally come from your packing materials data
        packing_map = {
            "Dosa": "Food container, lid, napkin",
            "Coffee": "Paper cup, lid, stirrer",
            "Tea(250 ml)": "Paper cup, lid, stirrer",
            "Idli(2 pcs)": "Food container, lid, chutney cup",
            "Chicken Gravy": "Food container, lid, rice container",
            "Fish Kolambu(Parai Fish)": "Food container, lid, rice container"
        }
        return packing_map.get(recipe_name, "Standard food container, lid")

    def get_packing_cost(self, recipe_name):
        """Get packing cost for recipe"""
        # This would ideally come from your packing materials cost data
        cost_map = {
            "Dosa": 8.0,
            "Coffee": 5.0,
            "Tea(250 ml)": 5.0,
            "Idli(2 pcs)": 10.0,
            "Chicken Gravy": 12.0,
            "Fish Kolambu(Parai Fish)": 15.0
        }
        return cost_map.get(recipe_name, 8.0)

    def get_ingredients(self, recipe_name):
        """Get ingredients for recipe"""
        # This would ideally come from your recipe/inventory data
        ingredients_map = {
            "Dosa": "Rice, Urad dal, Oil, Salt",
            "Coffee": "Coffee powder, Milk, Sugar",
            "Tea(250 ml)": "Tea leaves, Milk, Sugar, Ginger",
            "Idli(2 pcs)": "Rice, Urad dal, Salt",
            "Chicken Gravy": "Chicken, Onion, Tomato, Spices",
            "Fish Kolambu(Parai Fish)": "Fish, Tamarind, Onion, Spices"
        }
        return ingredients_map.get(recipe_name, "Standard ingredients")

    def get_ingredient_cost(self, recipe_name):
        """Get ingredient cost for recipe"""
        # This would ideally come from your inventory cost data
        cost_map = {
            "Dosa": 15.0,
            "Coffee": 20.0,
            "Tea(250 ml)": 12.0,
            "Idli(2 pcs)": 10.0,
            "Chicken Gravy": 45.0,
            "Fish Kolambu(Parai Fish)": 60.0
        }
        return cost_map.get(recipe_name, 20.0)

    def get_gas_charges(self, recipe_name):
        """Get gas charges for recipe"""
        # This would ideally come from your gas management data
        gas_map = {
            "Dosa": 4.0,
            "Coffee": 2.0,
            "Tea(250 ml)": 2.0,
            "Idli(2 pcs)": 5.0,
            "Chicken Gravy": 8.0,
            "Fish Kolambu(Parai Fish)": 10.0
        }
        return gas_map.get(recipe_name, 4.0)

    def get_electricity_charges(self, recipe_name):
        """Get electricity charges for recipe"""
        # This would ideally come from your electricity tracking data
        electricity_map = {
            "Dosa": 3.0,
            "Coffee": 1.5,
            "Tea(250 ml)": 1.5,
            "Idli(2 pcs)": 4.0,
            "Chicken Gravy": 2.0,
            "Fish Kolambu(Parai Fish)": 2.5
        }
        return electricity_map.get(recipe_name, 2.5)

    def get_fallback_recipe_data(self, recipe_name):
        """Get fallback recipe data when main data is not available"""
        fallback_prices = {
            "Dosa": 62, "Masala Dosa": 115, "Idli(2 pcs)": 48,
            "Coffee": 60, "Tea(250 ml)": 40, "Chicken Gravy": 100,
            "Fish Kolambu(Parai Fish)": 750, "Plain Rice": 50
        }

        return {
            'our_pricing': fallback_prices.get(recipe_name, 50.0),
            'packing_materials': self.get_packing_materials(recipe_name),
            'packing_cost': self.get_packing_cost(recipe_name),
            'ingredients': self.get_ingredients(recipe_name),
            'ingredient_cost': self.get_ingredient_cost(recipe_name),
            'gas_charges': self.get_gas_charges(recipe_name),
            'electricity_charges': self.get_electricity_charges(recipe_name)
        }

    def get_recipe_price(self, recipe_name):
        """Get price for selected recipe from pricing tab data"""
        try:
            # First try to get from pricing management system
            if hasattr(self.recipes_data, 'recipe_pricing_data'):
                recipe_data = self.recipes_data.recipe_pricing_data.get(recipe_name, {})
                our_pricing = recipe_data.get('our_pricing', 0)
                if our_pricing > 0:
                    return our_pricing

            # Try to get from pricing data table
            if hasattr(self.recipes_data, 'data') and 'pricing' in self.recipes_data.data:
                pricing_df = self.recipes_data.data['pricing']
                recipe_row = pricing_df[pricing_df['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    our_pricing = float(recipe_row.iloc[0].get('our_pricing', 0))
                    if our_pricing > 0:
                        return our_pricing

            # Fallback prices from the comprehensive pricing data
            fallback_prices = {
                "Dosa": 62, "Masala Dosa": 115, "Idli(2 pcs)": 48,
                "Coffee": 60, "Tea(250 ml)": 40, "Chicken Gravy": 100,
                "Fish Kolambu(Parai Fish)": 750, "Plain Rice": 50,
                "2 Masala Dosa": 120, "2 Ghee Dosa": 125, "2 Paper Roast": 96,
                "Podi Idli": 56, "Mini Idli": 62, "Idli Podimas": 100,
                "Tomato Chutney": 250, "Coconut Chutney": 135, "Sambar": 400,
                "Kurma": 65, "Ginger Tea": 38, "Boost": 65, "Horlicks": 65,
                "Black Coffee": 30, "Tea(125ml)": 22, "Tea(500ml)": 70,
                "Tea(750ml)": 105, "Milk": 32, "Chapathi": 40,
                "Kuli Paniyaram": 100, "Lemon Rice": 56, "Tomato Rice": 60,
                "Curd Rice": 62, "Onion Egg Dosa": 110, "Onion Dosa": 90,
                "Tomato Dosa": 60, "Egg Dosa": 85, "Paper Roast": 62,
                "Ghee Dosa": 90, "Onion Podi Dosa": 90, "Idly 5 pcs": 52,
                "Mini Podi Idli": 50, "Ghee Mini Idli with Sambhar (15 pcs)": 68,
                "Chappathi and Channa (2 pcs)": 105, "Boiled Egg": 22,
                "Carrot and Coriander Uthapam": 125, "Onion Uttapam": 90,
                "Tomato Uttapam": 80, "Plain Uttapam": 70, "Double Omelette": 58,
                "Onion bread omellete": 102, "Plain bread omellete": 92,
                "Chicken Gravy(250G)": 190
            }
            return fallback_prices.get(recipe_name, 50)

        except Exception as e:
            logging.error(f"Error getting recipe price: {e}")
            return 50
    
    def calculate_totals(self):
        """Calculate comprehensive totals including profit analysis"""
        try:
            # Get our pricing
            price_text = self.our_pricing_label.text().replace('₹', '').replace(',', '')
            price = float(price_text) if price_text else 0

            # Get quantity
            quantity = self.quantity_spin.value()

            # Calculate subtotal
            subtotal = price * quantity
            self.subtotal_label.setText(f"₹{subtotal:.2f}")

            # Get discount
            discount = self.discount_edit.value()

            # Calculate final price after discount
            final_price = subtotal - discount
            self.final_price_label.setText(f"₹{final_price:.2f}")

            # Calculate profit analysis
            if hasattr(self, 'current_recipe_data'):
                # Total cost per unit
                cost_per_unit = (
                    self.current_recipe_data.get('packing_cost', 0) +
                    self.current_recipe_data.get('ingredient_cost', 0) +
                    self.current_recipe_data.get('gas_charges', 0) +
                    self.current_recipe_data.get('electricity_charges', 0)
                )

                # Total cost for quantity
                total_cost = cost_per_unit * quantity

                # Profit calculation
                profit = final_price - total_cost
                self.profit_label.setText(f"₹{profit:.2f}")

                # Profit percentage
                if final_price > 0:
                    profit_percentage = (profit / final_price) * 100
                    self.profit_percentage_label.setText(f"{profit_percentage:.1f}%")

                    # Color coding for profit
                    if profit > 0:
                        self.profit_label.setStyleSheet("font-weight: 600; color: #10b981; font-size: 14px;")
                        self.profit_percentage_label.setStyleSheet("font-weight: 600; color: #10b981; font-size: 14px;")
                    else:
                        self.profit_label.setStyleSheet("font-weight: 600; color: #dc2626; font-size: 14px;")
                        self.profit_percentage_label.setStyleSheet("font-weight: 600; color: #dc2626; font-size: 14px;")
                else:
                    self.profit_percentage_label.setText("0%")

        except Exception as e:
            logging.error(f"Error calculating totals: {e}")
    
    def generate_order_id(self):
        """Generate unique order ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
    
    def get_order_data(self):
        """Get comprehensive order data with detailed cost breakdown"""
        try:
            recipe_name = self.recipe_combo.currentText()
            if recipe_name == "Select Recipe...":
                QMessageBox.warning(self, "Warning", "Please select a recipe.")
                return None

            # Get pricing data
            price_text = self.our_pricing_label.text().replace('₹', '').replace(',', '')
            our_pricing = float(price_text) if price_text else 0
            quantity = self.quantity_spin.value()
            subtotal_text = self.subtotal_label.text().replace('₹', '').replace(',', '')
            subtotal = float(subtotal_text) if subtotal_text else 0
            discount = self.discount_edit.value()
            final_price_text = self.final_price_label.text().replace('₹', '').replace(',', '')
            final_price = float(final_price_text) if final_price_text else 0

            # Get cost breakdown data
            packing_cost_text = self.packing_cost_label.text().replace('₹', '').replace(',', '')
            packing_cost = float(packing_cost_text) if packing_cost_text else 0

            prep_cost_text = self.prep_cost_label.text().replace('₹', '').replace(',', '')
            prep_cost = float(prep_cost_text) if prep_cost_text else 0

            gas_charges_text = self.gas_charges_label.text().replace('₹', '').replace(',', '')
            gas_charges = float(gas_charges_text) if gas_charges_text else 0

            electricity_charges_text = self.electricity_charges_label.text().replace('₹', '').replace(',', '')
            electricity_charges = float(electricity_charges_text) if electricity_charges_text else 0

            total_cost_text = self.total_cost_making_label.text().replace('₹', '').replace(',', '')
            total_cost_making = float(total_cost_text) if total_cost_text else 0

            profit_text = self.profit_label.text().replace('₹', '').replace(',', '')
            profit = float(profit_text) if profit_text else 0

            profit_percentage_text = self.profit_percentage_label.text().replace('%', '')
            profit_percentage = float(profit_percentage_text) if profit_percentage_text else 0

            # Create comprehensive order data
            order_data = {
                'date': self.date_edit.date().toPython().strftime('%Y-%m-%d'),
                'order_id': self.order_id_edit.text(),
                'recipe': recipe_name,
                'quantity': quantity,
                'packing_materials': self.packing_materials_label.text(),
                'packing_cost': packing_cost,
                'preparation_materials': self.prep_materials_label.text(),
                'preparation_cost': prep_cost,
                'gas_charges': gas_charges,
                'electricity_charges': electricity_charges,
                'total_cost_making': total_cost_making,
                'our_pricing': our_pricing,
                'subtotal': subtotal,
                'discount': discount,
                'final_price_after_discount': final_price,
                'profit': profit,
                'profit_percentage': profit_percentage
            }

            return order_data

        except Exception as e:
            logging.error(f"Error getting order data: {e}")
            QMessageBox.critical(self, "Error", f"Error creating order: {str(e)}")
            return None

class SalesOrderManagementWidget(QWidget):
    """Simplified sales order management widget"""
    
    # Signals
    order_added = Signal(dict)
    
    def __init__(self, data, pricing_data=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.pricing_data = pricing_data
        self.logger = logging.getLogger(__name__)
        
        # Initialize orders data
        if 'sales_orders' not in self.data:
            self.data['sales_orders'] = pd.DataFrame()
        
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Sales - Order Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add order button
        add_order_btn = QPushButton("+ Create Order")
        add_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        add_order_btn.clicked.connect(self.create_new_order)
        header_layout.addWidget(add_order_btn)
        
        layout.addLayout(header_layout)
        
        # Orders table
        self.create_orders_table(layout)
    
    def create_orders_table(self, parent_layout):
        """Create comprehensive orders table with detailed cost breakdown"""
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(16)
        self.orders_table.setHorizontalHeaderLabels([
            "Date", "Order ID", "Recipe", "Quantity", "Packing Cost",
            "Prep Cost", "Gas Charges", "Electricity", "Total Cost",
            "Our Pricing", "Subtotal", "Discount", "Final Price",
            "Profit", "Profit %", "Status"
        ])
        
        # Apply responsive table functionality
        try:
            from modules.responsive_table_utils import make_table_responsive

            column_priorities = {
                0: 2,   # Date - high priority
                1: 1,   # Order ID - highest priority
                2: 1,   # Recipe - highest priority
                3: 3,   # Quantity - medium priority
                4: 5,   # Packing Cost - lowest priority
                5: 5,   # Prep Cost - lowest priority
                6: 5,   # Gas Charges - lowest priority
                7: 5,   # Electricity - lowest priority
                8: 4,   # Total Cost - low priority
                9: 3,   # Our Pricing - medium priority
                10: 4,  # Subtotal - low priority
                11: 4,  # Discount - low priority
                12: 2,  # Final Price - high priority
                13: 2,  # Profit - high priority
                14: 3,  # Profit % - medium priority
                15: 4   # Status - low priority
            }

            column_config = {
                'priorities': column_priorities,
                'stretch_columns': [1, 2, 12, 13]  # Order ID, Recipe, Final Price, Profit
            }

            make_table_responsive(self.orders_table, column_config)

        except ImportError:
            self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        parent_layout.addWidget(self.orders_table)
    
    def create_new_order(self):
        """Open dialog to create new order"""
        dialog = SalesOrderDialog(self.pricing_data, self)
        
        if dialog.exec() == QDialog.Accepted:
            order_data = dialog.get_order_data()
            
            if order_data:
                self.save_order(order_data)
                self.load_orders()
                self.order_added.emit(order_data)
                
                QMessageBox.information(
                    self, "Success", 
                    f"Order {order_data['order_id']} created successfully!"
                )
    
    def save_order(self, order_data):
        """Save order to data"""
        try:
            # Add to dataframe
            new_df = pd.DataFrame([order_data])
            self.data['sales_orders'] = pd.concat([self.data['sales_orders'], new_df], ignore_index=True)
            
            # Save to CSV
            import os
            os.makedirs('data', exist_ok=True)
            self.data['sales_orders'].to_csv('data/sales_orders.csv', index=False)
            
        except Exception as e:
            self.logger.error(f"Error saving order: {e}")
            raise
    
    def load_orders(self):
        """Load and display comprehensive orders with detailed cost breakdown"""
        try:
            if self.data['sales_orders'].empty:
                self.orders_table.setRowCount(0)
                return

            orders_df = self.data['sales_orders']
            self.orders_table.setRowCount(len(orders_df))

            for row, (_, order) in enumerate(orders_df.iterrows()):
                # Basic order info
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.get('date', ''))))
                self.orders_table.setItem(row, 1, QTableWidgetItem(str(order.get('order_id', ''))))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(order.get('recipe', ''))))
                self.orders_table.setItem(row, 3, QTableWidgetItem(str(order.get('quantity', ''))))

                # Cost breakdown
                self.orders_table.setItem(row, 4, QTableWidgetItem(f"₹{order.get('packing_cost', 0):.2f}"))
                self.orders_table.setItem(row, 5, QTableWidgetItem(f"₹{order.get('preparation_cost', 0):.2f}"))
                self.orders_table.setItem(row, 6, QTableWidgetItem(f"₹{order.get('gas_charges', 0):.2f}"))
                self.orders_table.setItem(row, 7, QTableWidgetItem(f"₹{order.get('electricity_charges', 0):.2f}"))
                self.orders_table.setItem(row, 8, QTableWidgetItem(f"₹{order.get('total_cost_making', 0):.2f}"))

                # Pricing and totals
                self.orders_table.setItem(row, 9, QTableWidgetItem(f"₹{order.get('our_pricing', 0):.2f}"))
                self.orders_table.setItem(row, 10, QTableWidgetItem(f"₹{order.get('subtotal', 0):.2f}"))
                self.orders_table.setItem(row, 11, QTableWidgetItem(f"₹{order.get('discount', 0):.2f}"))
                self.orders_table.setItem(row, 12, QTableWidgetItem(f"₹{order.get('final_price_after_discount', 0):.2f}"))

                # Profit analysis
                profit = order.get('profit', 0)
                profit_percentage = order.get('profit_percentage', 0)

                profit_item = QTableWidgetItem(f"₹{profit:.2f}")
                profit_percent_item = QTableWidgetItem(f"{profit_percentage:.1f}%")

                # Color coding for profit
                if profit > 0:
                    profit_item.setForeground(QColor("#10b981"))
                    profit_percent_item.setForeground(QColor("#10b981"))
                else:
                    profit_item.setForeground(QColor("#dc2626"))
                    profit_percent_item.setForeground(QColor("#dc2626"))

                self.orders_table.setItem(row, 13, profit_item)
                self.orders_table.setItem(row, 14, profit_percent_item)

                # Status
                status = "Completed" if profit > 0 else "Review Required"
                status_item = QTableWidgetItem(status)
                if profit > 0:
                    status_item.setForeground(QColor("#10b981"))
                else:
                    status_item.setForeground(QColor("#f59e0b"))

                self.orders_table.setItem(row, 15, status_item)

        except Exception as e:
            self.logger.error(f"Error loading orders: {e}")

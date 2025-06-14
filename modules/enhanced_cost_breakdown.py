"""
Enhanced Cost Breakdown Panel
Provides detailed, interactive cost analysis for recipes and ingredients
"""

import logging
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QSplitter, QGroupBox, QComboBox, QLineEdit,
    QHeaderView, QTabWidget, QScrollArea, QGridLayout, QProgressBar,
    QCheckBox, QSpinBox, QDoubleSpinBox, QLayout, QLayoutItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QSize, QPoint
from PySide6.QtGui import QFont, QColor, QPalette


class FlowLayout(QLayout):
    """A layout that arranges widgets in a flow, wrapping to the next line when needed"""

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = self.spacing()

        for item in self.item_list:
            wid = item.widget()
            spaceX = spacing + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = spacing + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class CostBreakdownCard(QFrame):
    """Individual cost breakdown card widget"""
    
    def __init__(self, title, amount, percentage, color="#3498db"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
                margin: 4px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #f8fafc;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #64748b;")
        layout.addWidget(title_label)
        
        # Amount
        amount_label = QLabel(f"₹{amount:.2f}")
        amount_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {color};")
        layout.addWidget(amount_label)
        
        # Percentage
        percentage_label = QLabel(f"{percentage:.1f}% of total")
        percentage_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        layout.addWidget(percentage_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(percentage))
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #f1f5f9;
                border-radius: 4px;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(progress)


class IngredientCostTable(QTableWidget):
    """Enhanced table for ingredient-level cost breakdown"""
    
    ingredient_selected = Signal(str, dict)  # ingredient_name, cost_data
    
    def __init__(self):
        super().__init__()
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Ingredient", "Quantity", "Unit", "Cost/Unit", "Total Cost", 
            "Source", "Last Updated"
        ])
        
        # Modern table styling
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                selection-background-color: #fef2f2;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
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
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)      # Ingredient
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Cost/Unit
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total Cost
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Source
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Last Updated
        
        # Connect selection signal
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def on_selection_changed(self):
        """Handle ingredient selection"""
        current_row = self.currentRow()
        if current_row >= 0:
            ingredient_name = self.item(current_row, 0).text()
            cost_data = {
                'quantity': self.item(current_row, 1).text(),
                'unit': self.item(current_row, 2).text(),
                'cost_per_unit': self.item(current_row, 3).text(),
                'total_cost': self.item(current_row, 4).text(),
                'source': self.item(current_row, 5).text(),
                'last_updated': self.item(current_row, 6).text()
            }
            self.ingredient_selected.emit(ingredient_name, cost_data)


class EnhancedCostBreakdownPanel(QWidget):
    """Enhanced cost breakdown panel with detailed analysis"""
    
    cost_updated = Signal(str, float)  # recipe_id, new_cost
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)
        self.current_recipe_id = None
        self.cost_cache = {}

        self.init_ui()

        # Load recipes after UI is initialized
        QTimer.singleShot(100, self.load_recipes)
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with recipe selector
        self.create_header(layout)
        
        # Main content with vertical layout - cost breakdown cards on top, ingredients table below
        main_content_widget = QWidget()
        main_content_layout = QVBoxLayout(main_content_widget)
        main_content_layout.setSpacing(20)

        # Top section - Cost breakdown cards
        self.create_cost_cards_panel(main_content_layout)

        # Bottom section - Detailed ingredient table
        self.create_ingredient_panel(main_content_layout)

        layout.addWidget(main_content_widget)
        
        # Bottom panel - Cost adjustment tools
        self.create_adjustment_panel(layout)
    
    def create_header(self, parent_layout):
        """Create header with recipe selector"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("📊 Enhanced Cost Breakdown")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Recipe selector
        recipe_label = QLabel("Recipe:")
        recipe_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #64748b;")
        header_layout.addWidget(recipe_label)
        
        self.recipe_selector = QComboBox()
        self.recipe_selector.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                min-width: 200px;
            }
        """)
        self.recipe_selector.currentTextChanged.connect(self.on_recipe_changed)
        header_layout.addWidget(self.recipe_selector)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(header_frame)
    
    def create_cost_cards_panel(self, parent_layout):
        """Create cost breakdown cards panel with vertical layout"""
        # Cards title
        cards_title = QLabel("💰 Cost Breakdown")
        cards_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 15px;")
        parent_layout.addWidget(cards_title)

        # Cards container with responsive flow layout (wraps to next line if needed)
        self.cards_container = QWidget()
        self.cards_layout = FlowLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        # Add cards container directly
        parent_layout.addWidget(self.cards_container)
    
    def create_ingredient_panel(self, parent_layout):
        """Create detailed ingredient analysis panel below cost breakdown cards"""
        # Ingredient table title
        table_title = QLabel("🥘 Ingredient Details")
        table_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #374151; margin-bottom: 10px; margin-top: 20px;")
        parent_layout.addWidget(table_title)

        # Ingredient table
        self.ingredient_table = IngredientCostTable()
        self.ingredient_table.ingredient_selected.connect(self.on_ingredient_selected)
        parent_layout.addWidget(self.ingredient_table)
    
    def create_adjustment_panel(self, parent_layout):
        """Create cost adjustment tools panel"""
        adjustment_frame = QFrame()
        adjustment_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        adjustment_layout = QHBoxLayout(adjustment_frame)
        
        # Bulk adjustment tools
        bulk_label = QLabel("Bulk Adjustments:")
        bulk_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #64748b;")
        adjustment_layout.addWidget(bulk_label)
        
        # Percentage adjustment
        percentage_label = QLabel("Adjust by %:")
        adjustment_layout.addWidget(percentage_label)
        
        self.percentage_input = QDoubleSpinBox()
        self.percentage_input.setRange(-50, 100)
        self.percentage_input.setValue(0)
        self.percentage_input.setSuffix("%")
        adjustment_layout.addWidget(self.percentage_input)
        
        apply_percentage_btn = QPushButton("Apply")
        apply_percentage_btn.clicked.connect(self.apply_percentage_adjustment)
        adjustment_layout.addWidget(apply_percentage_btn)
        
        adjustment_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("📊 Export Analysis")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        export_btn.clicked.connect(self.export_analysis)
        adjustment_layout.addWidget(export_btn)
        
        parent_layout.addWidget(adjustment_frame)
    
    def load_recipes(self):
        """Load recipes into selector"""
        self.recipe_selector.clear()
        if 'recipes' in self.data and not self.data['recipes'].empty:
            for _, recipe in self.data['recipes'].iterrows():
                recipe_name = recipe.get('recipe_name', f"Recipe {recipe.get('recipe_id', 'Unknown')}")
                recipe_id = recipe.get('recipe_id', 'Unknown')
                self.recipe_selector.addItem(recipe_name, recipe_id)
    
    def on_recipe_changed(self, recipe_name):
        """Handle recipe selection change"""
        if recipe_name:
            recipe_id = self.recipe_selector.currentData()
            self.current_recipe_id = recipe_id
            self.analyze_recipe_cost(recipe_id)
    
    def analyze_recipe_cost(self, recipe_id):
        """Analyze cost breakdown for selected recipe"""
        if not recipe_id:
            return
        
        try:
            # Get recipe ingredients and calculate detailed costs
            cost_breakdown = self.calculate_detailed_cost_breakdown(recipe_id)
            
            # Update cost cards
            self.update_cost_cards(cost_breakdown)
            
            # Update ingredient table
            self.update_ingredient_table(cost_breakdown.get('ingredients', []))
            
        except Exception as e:
            self.logger.error(f"Error analyzing recipe cost: {e}")
    
    def calculate_detailed_cost_breakdown(self, recipe_id):
        """Calculate detailed cost breakdown for recipe"""
        try:
            # Get actual recipe data
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return self.get_default_breakdown()

            # Find the recipe
            recipe_row = self.data['recipes'][self.data['recipes']['recipe_id'] == recipe_id]
            if recipe_row.empty:
                return self.get_default_breakdown()

            recipe = recipe_row.iloc[0]
            recipe_name = recipe.get('recipe_name', f'Recipe {recipe_id}')

            # Calculate ingredient cost
            ingredient_cost = self.calculate_recipe_ingredient_cost(recipe_id)

            # Calculate making cost - same as ingredient cost (not 20%)
            making_cost = ingredient_cost

            # Calculate actual packaging cost from packing materials mapping
            packaging_cost = self.calculate_actual_packaging_cost(recipe_name)

            cook_time = recipe.get('cook_time', 30)
            electricity_cost = self.calculate_electricity_cost(cook_time)
            gas_cost = self.calculate_gas_cost(recipe_data=recipe)
            other_charges = 2.0

            # Calculate overhead (15% of subtotal)
            subtotal = ingredient_cost + making_cost + packaging_cost + electricity_cost + gas_cost + other_charges
            overhead_cost = subtotal * 0.15
            total_cost = subtotal + overhead_cost

            # Get ingredient details
            ingredients = self.get_recipe_ingredients(recipe_id)

            return {
                'recipe_name': recipe_name,
                'total_cost': total_cost,
                'ingredient_cost': ingredient_cost,
                'making_cost': making_cost,
                'packaging_cost': packaging_cost,
                'electricity_cost': electricity_cost,
                'gas_cost': gas_cost,
                'other_charges': other_charges,
                'overhead_cost': overhead_cost,
                'ingredients': ingredients
            }

        except Exception as e:
            self.logger.error(f"Error calculating detailed cost breakdown: {e}")
            return self.get_default_breakdown()

    def get_default_breakdown(self):
        """Get default breakdown when no data available"""
        return {
            'recipe_name': 'No Recipe Selected',
            'total_cost': 0.0,
            'ingredient_cost': 0.0,
            'making_cost': 0.0,
            'packaging_cost': 0.0,
            'electricity_cost': 0.0,
            'gas_cost': 0.0,
            'other_charges': 0.0,
            'overhead_cost': 0.0,
            'ingredients': []
        }

    def calculate_recipe_ingredient_cost(self, recipe_id):
        """Calculate ingredient cost for recipe"""
        try:
            # Check if recipe_ingredients exists
            if 'recipe_ingredients' not in self.data or self.data['recipe_ingredients'].empty:
                return 50.0  # Default cost

            # Get ingredients for this recipe
            recipe_ingredients = self.data['recipe_ingredients'][
                self.data['recipe_ingredients']['recipe_id'] == recipe_id
            ]

            total_cost = 0.0
            for _, ingredient in recipe_ingredients.iterrows():
                item_name = ingredient.get('item_name', '')
                quantity = ingredient.get('quantity', 0)

                # Get price from shopping list or inventory
                price_per_unit = self.get_ingredient_price(item_name)
                total_cost += quantity * price_per_unit

            return max(total_cost, 10.0)  # Minimum cost

        except Exception as e:
            self.logger.error(f"Error calculating ingredient cost: {e}")
            return 50.0

    def get_ingredient_price(self, item_name):
        """Get ingredient price per unit from shopping list or inventory"""
        try:
            # Try shopping list first
            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                shopping_item = self.data['shopping_list'][
                    self.data['shopping_list']['item_name'].str.lower() == item_name.lower()
                ]
                if not shopping_item.empty:
                    item = shopping_item.iloc[0]
                    # Use avg_price if available, otherwise current_price, otherwise last_price
                    price = item.get('avg_price', item.get('current_price', item.get('last_price', 0)))
                    quantity = item.get('quantity', 1)
                    if price > 0 and quantity > 0:
                        return price / quantity  # Price per unit
                    return 5.0

            # Try inventory
            if 'inventory' in self.data and not self.data['inventory'].empty:
                inventory_item = self.data['inventory'][
                    self.data['inventory']['item_name'].str.lower() == item_name.lower()
                ]
                if not inventory_item.empty:
                    return inventory_item.iloc[0].get('price_per_unit', 5.0)

            # Default price based on common ingredients
            default_prices = {
                'rice': 0.08, 'chicken': 0.25, 'onion': 0.04, 'tomato': 0.06,
                'oil': 0.15, 'salt': 0.02, 'sugar': 0.04, 'flour': 0.05
            }

            for key, price in default_prices.items():
                if key in item_name.lower():
                    return price

            return 5.0  # Default price

        except Exception as e:
            self.logger.error(f"Error getting ingredient price: {e}")
            return 5.0

    def get_recipe_ingredients(self, recipe_id):
        """Get detailed ingredient list for recipe"""
        try:
            ingredients = []

            if 'recipe_ingredients' not in self.data or self.data['recipe_ingredients'].empty:
                return ingredients

            recipe_ingredients = self.data['recipe_ingredients'][
                self.data['recipe_ingredients']['recipe_id'] == recipe_id
            ]

            for _, ingredient in recipe_ingredients.iterrows():
                item_name = ingredient.get('item_name', '')
                quantity = ingredient.get('quantity', 0)
                unit = ingredient.get('unit', 'g')

                cost_per_unit = self.get_ingredient_price(item_name)
                total_cost = quantity * cost_per_unit

                # Determine source
                source = 'Default'
                if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                    if not self.data['shopping_list'][
                        self.data['shopping_list']['item_name'].str.lower() == item_name.lower()
                    ].empty:
                        source = 'Shopping List'
                elif 'inventory' in self.data and not self.data['inventory'].empty:
                    if not self.data['inventory'][
                        self.data['inventory']['item_name'].str.lower() == item_name.lower()
                    ].empty:
                        source = 'Inventory'

                ingredients.append({
                    'name': item_name,
                    'quantity': quantity,
                    'unit': unit,
                    'cost_per_unit': cost_per_unit,
                    'total_cost': total_cost,
                    'source': source,
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })

            return ingredients

        except Exception as e:
            self.logger.error(f"Error getting recipe ingredients: {e}")
            return []

    def calculate_electricity_cost(self, cook_time_minutes):
        """Calculate electricity cost based on cooking time"""
        try:
            power_kw = 2.0  # 2kW average
            rate_per_kwh = 6.0  # ₹6 per kWh
            hours = cook_time_minutes / 60.0
            return max(power_kw * hours * rate_per_kwh, 0.5)
        except:
            return 1.0

    def calculate_gas_cost(self, recipe_data=None, cook_time_minutes=None):
        """Calculate gas cost based on total preparation time (prep_time + cook_time)"""
        try:
            # Load gas cost configuration
            gas_config = self.load_gas_cost_config()
            gas_settings = gas_config.get('gas_cost_settings', {})
            cylinder_settings = gas_config.get('cylinder_settings', {})

            gas_consumption_per_hour = gas_settings.get('gas_consumption_per_hour_kg', 0.3)
            rate_per_kg = cylinder_settings.get('cost_per_kg_inr', gas_settings.get('gas_rate_per_kg_inr', 60.67))
            minimum_cost = gas_settings.get('minimum_cost_inr', 0.5)
            use_total_prep_time = gas_settings.get('use_total_preparation_time', True)

            total_time_minutes = 0

            # If recipe_data is provided, calculate preparation time based on config
            if recipe_data is not None:
                prep_time = recipe_data.get('prep_time', 0)
                cook_time = recipe_data.get('cook_time', 0)

                if use_total_prep_time:
                    total_time_minutes = prep_time + cook_time
                    self.logger.debug(f"Gas cost calculation - Prep: {prep_time}min, Cook: {cook_time}min, Total: {total_time_minutes}min")
                else:
                    total_time_minutes = cook_time
                    self.logger.debug(f"Gas cost calculation - Using cook_time only: {total_time_minutes}min")

            # Fallback to cook_time_minutes parameter if recipe_data not available
            elif cook_time_minutes is not None:
                total_time_minutes = cook_time_minutes
                self.logger.debug(f"Gas cost calculation - Using cook_time only: {total_time_minutes}min")

            # Default to 30 minutes if no time data available
            else:
                total_time_minutes = 30
                self.logger.warning("No time data available for gas cost calculation, using default 30 minutes")

            # Calculate gas cost
            hours = total_time_minutes / 60.0
            cost = gas_consumption_per_hour * hours * rate_per_kg
            final_cost = max(cost, minimum_cost)

            self.logger.debug(f"Gas cost calculated: {total_time_minutes}min = ₹{final_cost:.2f}")
            return final_cost

        except Exception as e:
            self.logger.error(f"Error calculating gas cost: {e}")
            return 1.0

    def load_gas_cost_config(self):
        """Load gas cost configuration from JSON file"""
        try:
            import json
            import os

            config_path = os.path.join('data', 'gas_cost_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('gas_cost_settings', {})
            else:
                self.logger.warning(f"Gas cost config file not found at {config_path}, using defaults")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading gas cost config: {e}")
            return {}
    
    def update_cost_cards(self, cost_breakdown):
        """Update cost breakdown cards with responsive flow layout (wraps to next line if needed)"""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        total_cost = cost_breakdown['total_cost']

        # Create cards for each cost component
        cost_components = [
            ('Ingredient Cost', cost_breakdown['ingredient_cost'], '#3b82f6'),
            ('Making Cost', cost_breakdown['making_cost'], '#10b981'),
            ('Packaging Cost', cost_breakdown['packaging_cost'], '#f59e0b'),
            ('Electricity Cost', cost_breakdown['electricity_cost'], '#ef4444'),
            ('Gas Cost', cost_breakdown['gas_cost'], '#8b5cf6'),
            ('Other Charges', cost_breakdown['other_charges'], '#06b6d4'),
            ('Overhead Cost', cost_breakdown['overhead_cost'], '#84cc16')
        ]

        # Arrange cards in flow layout (wraps to next line if needed)
        for i, (name, amount, color) in enumerate(cost_components):
            percentage = (amount / total_cost * 100) if total_cost > 0 else 0
            card = CostBreakdownCard(name, amount, percentage, color)

            # Add each card to flow layout (will wrap automatically)
            self.cards_layout.addWidget(card)
    
    def update_ingredient_table(self, ingredients):
        """Update ingredient details table"""
        self.ingredient_table.setRowCount(len(ingredients))
        
        for row, ingredient in enumerate(ingredients):
            self.ingredient_table.setItem(row, 0, QTableWidgetItem(ingredient['name']))
            self.ingredient_table.setItem(row, 1, QTableWidgetItem(str(ingredient['quantity'])))
            self.ingredient_table.setItem(row, 2, QTableWidgetItem(ingredient['unit']))
            self.ingredient_table.setItem(row, 3, QTableWidgetItem(f"₹{ingredient['cost_per_unit']:.2f}"))
            self.ingredient_table.setItem(row, 4, QTableWidgetItem(f"₹{ingredient['total_cost']:.2f}"))
            self.ingredient_table.setItem(row, 5, QTableWidgetItem(ingredient['source']))
            self.ingredient_table.setItem(row, 6, QTableWidgetItem(ingredient['last_updated']))
    
    def on_ingredient_selected(self, ingredient_name, cost_data):
        """Handle ingredient selection"""
        self.logger.info(f"Selected ingredient: {ingredient_name}")
        # Could open detailed ingredient cost editor here
    
    def apply_percentage_adjustment(self):
        """Apply percentage adjustment to all costs"""
        percentage = self.percentage_input.value()
        if percentage != 0:
            self.logger.info(f"Applying {percentage}% adjustment to recipe costs")
            # Implement cost adjustment logic
    
    def export_analysis(self):
        """Export cost analysis to file"""
        self.logger.info("Exporting cost analysis")
        # Implement export functionality
    
    def calculate_actual_packaging_cost(self, recipe_name):
        """Calculate actual packaging cost from packing materials mapping"""
        try:
            # Check if recipe packing materials data exists
            if 'recipe_packing_materials' in self.data and not self.data['recipe_packing_materials'].empty:
                # Get materials for this recipe from in-memory data
                recipe_materials = self.data['recipe_packing_materials'][
                    self.data['recipe_packing_materials']['recipe_name'] == recipe_name
                ]

                if not recipe_materials.empty:
                    # Use the pre-calculated cost_per_recipe from in-memory data
                    total_cost = recipe_materials['cost_per_recipe'].sum()

                    if total_cost > 0:
                        # Debug information
                        materials_list = []
                        for _, row in recipe_materials.iterrows():
                            materials_list.append(f"{row['material_name']} (₹{row['cost_per_recipe']:.2f})")

                        self.logger.info(f"✅ Packing cost from data for {recipe_name}: {', '.join(materials_list)} = ₹{total_cost:.2f}")
                        return float(total_cost)

            # Fallback to CSV file if in-memory data is not available or empty
            import os
            import pandas as pd

            packing_file = os.path.join('data', 'recipe_packing_materials.csv')
            if os.path.exists(packing_file):
                packing_df = pd.read_csv(packing_file)

                # Filter for the specific recipe
                recipe_materials = packing_df[packing_df['recipe_name'] == recipe_name]

                if not recipe_materials.empty:
                    # Sum up all packing costs for this recipe (cost_per_recipe column already calculated)
                    total_cost = recipe_materials['cost_per_recipe'].sum()

                    if total_cost > 0:
                        # Debug information
                        materials_list = []
                        for _, row in recipe_materials.iterrows():
                            materials_list.append(f"{row['material_name']} (₹{row['cost_per_recipe']:.2f})")

                        self.logger.info(f"⚠️ Packing cost from CSV for {recipe_name}: {', '.join(materials_list)} = ₹{total_cost:.2f}")
                        return float(total_cost)

            # If no packing materials found, return default cost
            self.logger.warning(f"No packing materials found for {recipe_name}, using default cost of ₹5.00")
            return 5.0

        except Exception as e:
            self.logger.error(f"Error calculating actual packaging cost for {recipe_name}: {e}")
            return 5.0  # Default fallback

    def refresh_data(self):
        """Refresh cost data"""
        self.load_recipes()
        if self.current_recipe_id:
            self.analyze_recipe_cost(self.current_recipe_id)

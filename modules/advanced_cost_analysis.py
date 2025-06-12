"""
Advanced Cost Analysis Module
Provides comprehensive cost analysis, comparison tools, and trend visualization
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QSplitter, QGroupBox, QComboBox, QTabWidget,
    QScrollArea, QGridLayout, QProgressBar, QSlider, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Import table styling utility
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.table_styling import apply_recipe_table_styling
except ImportError:
    print("Warning: Could not import table styling utility")
    apply_recipe_table_styling = None


class CostComparisonWidget(QWidget):
    """Widget for comparing costs between recipes"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.selected_recipes = []

        # Debug: Print data information
        print("🔍 CostComparisonWidget - Data Debug:")
        print(f"  Data type: {type(self.data)}")
        if self.data:
            print(f"  Data keys: {list(self.data.keys())}")
            if 'recipes' in self.data:
                print(f"  Recipes count: {len(self.data['recipes'])}")
                if not self.data['recipes'].empty:
                    print(f"  Recipe columns: {list(self.data['recipes'].columns)}")
                    print(f"  Sample recipes: {self.data['recipes']['recipe_name'].head(3).tolist() if 'recipe_name' in self.data['recipes'].columns else 'No recipe_name column'}")
                else:
                    print("  Recipes dataframe is empty")
            else:
                print("  No 'recipes' key in data")
        else:
            print("  Data is None or empty")

        self.init_ui()
    
    def init_ui(self):
        """Initialize comparison UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 Recipe Cost Comparison")
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add recipe button with proper styling
        add_recipe_btn = QPushButton("➕ Add Recipe")
        add_recipe_btn.clicked.connect(self.add_recipe_to_comparison)
        add_recipe_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 120px;
                max-width: 120px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        header_layout.addWidget(add_recipe_btn)
        
        layout.addLayout(header_layout)
        
        # Comparison table
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(8)
        self.comparison_table.setHorizontalHeaderLabels([
            "Recipe", "Ingredient Cost", "Making Cost", "Total Cost",
            "Profit Margin", "Selling Price", "Efficiency Score", "Actions"
        ])
        
        # Apply modern table styling using utility function
        if apply_recipe_table_styling:
            apply_recipe_table_styling(self.comparison_table)
        else:
            # Fallback styling if utility not available
            self.comparison_table.setStyleSheet("""
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
                    min-height: 40px;
                }
                QHeaderView::section {
                    background-color: #f8fafc;
                    border: none;
                    border-bottom: 1px solid #e2e8f0;
                    border-right: 1px solid #e2e8f0;
                    padding: 12px 8px;
                    font-weight: 600;
                    color: #374151;
                    min-height: 40px;
                }
            """)

            # Set proper table properties
            self.comparison_table.horizontalHeader().setStretchLastSection(True)
            self.comparison_table.setAlternatingRowColors(True)
            self.comparison_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.comparison_table.verticalHeader().setDefaultSectionSize(60)  # Row height
            self.comparison_table.horizontalHeader().setDefaultSectionSize(120)  # Column width

            # Set specific column widths
            header = self.comparison_table.horizontalHeader()
            header.resizeSection(0, 200)  # Recipe name - wider
            header.resizeSection(1, 120)  # Ingredient Cost
            header.resizeSection(2, 120)  # Making Cost
            header.resizeSection(3, 120)  # Total Cost
            header.resizeSection(4, 120)  # Profit Margin
            header.resizeSection(5, 120)  # Selling Price
            header.resizeSection(6, 120)  # Efficiency Score
            header.resizeSection(7, 100)  # Actions
        
        layout.addWidget(self.comparison_table)
        
        # Comparison insights
        self.create_insights_panel(layout)
    
    def create_insights_panel(self, parent_layout):
        """Create insights panel"""
        insights_frame = QFrame()
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        insights_layout = QVBoxLayout(insights_frame)
        
        insights_title = QLabel("💡 Cost Insights")
        insights_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #374151;")
        insights_layout.addWidget(insights_title)
        
        self.insights_label = QLabel("Add recipes to see cost comparison insights.")
        self.insights_label.setStyleSheet("color: #64748b; font-size: 14px;")
        self.insights_label.setWordWrap(True)
        insights_layout.addWidget(self.insights_label)
        
        parent_layout.addWidget(insights_frame)
    
    def add_recipe_to_comparison(self):
        """Add recipe to comparison"""
        try:
            from PySide6.QtWidgets import QInputDialog

            print("🔍 Add Recipe Button Clicked!")
            print("Debug - Available data keys:", list(self.data.keys()) if self.data else "No data")

            # Get available recipes
            if 'recipes' not in self.data:
                print("❌ No 'recipes' key in data")
                QMessageBox.warning(self, "No Recipes", "No recipes data found. Please check if recipes are loaded.")
                return

            if self.data['recipes'].empty:
                print("❌ Recipes dataframe is empty")
                QMessageBox.warning(self, "No Recipes", "No recipes available. Please add recipes first.")
                return

            print(f"✅ Found {len(self.data['recipes'])} recipes")
            print("✅ Recipe columns:", list(self.data['recipes'].columns))

            # Get recipe names
            if 'recipe_name' not in self.data['recipes'].columns:
                print("❌ No 'recipe_name' column found")
                QMessageBox.warning(self, "Data Error", "Recipe name column not found in recipes data.")
                return

            recipe_names = self.data['recipes']['recipe_name'].tolist()
            print(f"✅ Recipe names count: {len(recipe_names)}")
            print("✅ First 5 recipe names:", recipe_names[:5])

            # Show selection dialog
            print("🔍 Opening recipe selection dialog...")
            print(f"Dialog will show {len(recipe_names)} recipes")

            recipe_name, ok = QInputDialog.getItem(
                self, "Select Recipe", "Choose a recipe to add:", recipe_names, 0, False
            )

            print(f"Dialog result: ok={ok}, selected_recipe='{recipe_name}'")

            if ok and recipe_name:
                # Find recipe ID
                recipe_row = self.data['recipes'][self.data['recipes']['recipe_name'] == recipe_name]
                if not recipe_row.empty:
                    recipe_id = recipe_row.iloc[0]['recipe_id']

                    print(f"Debug - Adding recipe: {recipe_name} (ID: {recipe_id})")

                    # Add to selected recipes if not already added
                    if recipe_id not in [r['id'] for r in self.selected_recipes]:
                        ingredient_cost = self.calculate_ingredient_cost(recipe_id)
                        making_cost = ingredient_cost * 0.2  # 20% of ingredient cost

                        recipe_data = {
                            'id': recipe_id,
                            'name': recipe_name,
                            'ingredient_cost': ingredient_cost,
                            'making_cost': making_cost,
                            'total_cost': ingredient_cost + making_cost
                        }

                        print(f"Debug - Recipe cost breakdown: Ingredient: ₹{ingredient_cost:.2f}, Making: ₹{making_cost:.2f}, Total: ₹{recipe_data['total_cost']:.2f}")

                        self.selected_recipes.append(recipe_data)
                        self.update_comparison()

                        QMessageBox.information(self, "Recipe Added", f"Added {recipe_name} to comparison with total cost ₹{recipe_data['total_cost']:.2f}")
                    else:
                        QMessageBox.information(self, "Already Added", "This recipe is already in the comparison.")

        except Exception as e:
            print(f"❌ Exception in add_recipe_to_comparison: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to add recipe: {str(e)}")

    def calculate_ingredient_cost(self, recipe_id):
        """Calculate ingredient cost for a recipe"""
        try:
            print(f"🔍 Calculating cost for recipe_id: {recipe_id}")

            if 'recipe_ingredients' not in self.data or self.data['recipe_ingredients'].empty:
                print("❌ No recipe_ingredients data available")
                return 50.0  # Default cost

            recipe_ingredients = self.data['recipe_ingredients'][
                self.data['recipe_ingredients']['recipe_id'] == recipe_id
            ]

            print(f"✅ Found {len(recipe_ingredients)} ingredients for recipe {recipe_id}")

            if recipe_ingredients.empty:
                print("❌ No ingredients found for this recipe")
                return 50.0

            total_cost = 0.0
            ingredient_details = []

            for _, ingredient in recipe_ingredients.iterrows():
                item_name = ingredient.get('item_name', '')
                quantity = float(ingredient.get('quantity', 0))
                unit = ingredient.get('unit', 'piece')

                # Get price from shopping list or inventory
                price_per_unit = self.get_ingredient_price(item_name)
                ingredient_cost = quantity * price_per_unit
                total_cost += ingredient_cost

                ingredient_details.append({
                    'name': item_name,
                    'quantity': quantity,
                    'unit': unit,
                    'price_per_unit': price_per_unit,
                    'total_cost': ingredient_cost
                })

                print(f"  - {item_name}: {quantity} {unit} × ₹{price_per_unit:.2f} = ₹{ingredient_cost:.2f}")

            print(f"✅ Total ingredient cost: ₹{total_cost:.2f}")
            return max(total_cost, 10.0)  # Minimum cost

        except Exception as e:
            print(f"❌ Error calculating ingredient cost: {e}")
            import traceback
            traceback.print_exc()
            return 50.0

    def get_ingredient_price(self, item_name):
        """Get ingredient price from shopping list or inventory with realistic Tamil Nadu pricing"""
        try:
            print(f"🔍 Getting price for ingredient: {item_name}")

            # Try shopping list first
            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                shopping_item = self.data['shopping_list'][
                    self.data['shopping_list']['item_name'].str.lower() == item_name.lower()
                ]
                if not shopping_item.empty:
                    price = float(shopping_item.iloc[0].get('estimated_cost', 0))
                    if price > 0:
                        print(f"  ✅ Found in shopping list: ₹{price:.2f}")
                        return price

            # Try inventory
            if 'inventory' in self.data and not self.data['inventory'].empty:
                inventory_item = self.data['inventory'][
                    self.data['inventory']['item_name'].str.lower() == item_name.lower()
                ]
                if not inventory_item.empty:
                    price = float(inventory_item.iloc[0].get('price_per_unit', 0))
                    if price > 0:
                        print(f"  ✅ Found in inventory: ₹{price:.2f}")
                        return price

            # Try items.csv for default pricing
            if 'items' in self.data and not self.data['items'].empty:
                items_data = self.data['items'][
                    self.data['items']['item_name'].str.lower() == item_name.lower()
                ]
                if not items_data.empty:
                    price = float(items_data.iloc[0].get('default_cost', 0))
                    if price > 0:
                        print(f"  ✅ Found in items: ₹{price:.2f}")
                        return price

            # Realistic default pricing based on common Tamil Nadu ingredients
            default_prices = {
                'rice': 50.0, 'dal': 80.0, 'oil': 120.0, 'onion': 30.0, 'tomato': 40.0,
                'potato': 25.0, 'ginger': 200.0, 'garlic': 150.0, 'turmeric': 300.0,
                'chili': 100.0, 'coriander': 80.0, 'cumin': 400.0, 'mustard': 200.0,
                'coconut': 35.0, 'curry leaves': 50.0, 'tamarind': 120.0, 'salt': 20.0,
                'sugar': 45.0, 'milk': 55.0, 'egg': 6.0, 'chicken': 180.0, 'fish': 200.0,
                'wheat': 40.0, 'flour': 45.0, 'ghee': 500.0, 'yogurt': 60.0
            }

            # Check for partial matches
            item_lower = item_name.lower()
            for key, price in default_prices.items():
                if key in item_lower or item_lower in key:
                    print(f"  ✅ Default price match for '{key}': ₹{price:.2f}")
                    return price

            # Final fallback
            default_price = 25.0
            print(f"  ⚠️ Using fallback price: ₹{default_price:.2f}")
            return default_price

        except Exception as e:
            print(f"❌ Error getting ingredient price: {e}")
            return 25.0

    def update_comparison(self):
        """Update comparison table and insights"""
        try:
            # Update table
            self.comparison_table.setRowCount(len(self.selected_recipes))

            for row, recipe in enumerate(self.selected_recipes):
                self.comparison_table.setItem(row, 0, QTableWidgetItem(recipe['name']))
                self.comparison_table.setItem(row, 1, QTableWidgetItem(f"₹{recipe['ingredient_cost']:.2f}"))
                self.comparison_table.setItem(row, 2, QTableWidgetItem(f"₹{recipe['making_cost']:.2f}"))
                self.comparison_table.setItem(row, 3, QTableWidgetItem(f"₹{recipe['total_cost']:.2f}"))

                # Calculate profit margin (30% default)
                profit_margin = recipe['total_cost'] * 0.3
                selling_price = recipe['total_cost'] + profit_margin
                efficiency_score = (recipe['ingredient_cost'] / recipe['total_cost']) * 100

                self.comparison_table.setItem(row, 4, QTableWidgetItem(f"₹{profit_margin:.2f}"))
                self.comparison_table.setItem(row, 5, QTableWidgetItem(f"₹{selling_price:.2f}"))
                self.comparison_table.setItem(row, 6, QTableWidgetItem(f"{efficiency_score:.1f}%"))

                # Remove button
                remove_btn = QPushButton("Remove")
                remove_btn.clicked.connect(lambda checked, r=row: self.remove_recipe(r))
                self.comparison_table.setCellWidget(row, 7, remove_btn)

            # Update insights
            self.update_insights()

        except Exception as e:
            print(f"Error updating comparison: {e}")

    def remove_recipe(self, row):
        """Remove recipe from comparison"""
        if 0 <= row < len(self.selected_recipes):
            self.selected_recipes.pop(row)
            self.update_comparison()

    def update_insights(self):
        """Update comparison insights"""
        if not self.selected_recipes:
            self.insights_label.setText("Add recipes to see cost comparison insights.")
            return

        # Calculate insights
        costs = [r['total_cost'] for r in self.selected_recipes]
        min_cost = min(costs)
        max_cost = max(costs)
        avg_cost = sum(costs) / len(costs)

        cheapest_recipe = min(self.selected_recipes, key=lambda x: x['total_cost'])
        most_expensive = max(self.selected_recipes, key=lambda x: x['total_cost'])

        insights_text = f"""
        📊 Comparison Summary:
        • Cheapest Recipe: {cheapest_recipe['name']} (₹{cheapest_recipe['total_cost']:.2f})
        • Most Expensive: {most_expensive['name']} (₹{most_expensive['total_cost']:.2f})
        • Average Cost: ₹{avg_cost:.2f}
        • Cost Range: ₹{max_cost - min_cost:.2f}

        💡 Recommendations:
        • Consider {cheapest_recipe['name']} for cost-effective meals
        • {most_expensive['name']} might be suitable for premium offerings
        """

        self.insights_label.setText(insights_text)


class ProfitMarginCalculator(QWidget):
    """Interactive profit margin calculator"""
    
    margin_changed = Signal(float, float)  # cost, margin
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize calculator UI"""
        layout = QVBoxLayout(self)
        
        # Header
        title_label = QLabel("💰 Profit Margin Calculator")
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title_label)
        
        # Calculator grid
        calc_frame = QFrame()
        calc_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        calc_layout = QGridLayout(calc_frame)
        
        # Cost input
        calc_layout.addWidget(QLabel("Total Cost (₹):"), 0, 0)
        self.cost_input = QSpinBox()
        self.cost_input.setRange(1, 10000)
        self.cost_input.setValue(100)
        self.cost_input.valueChanged.connect(self.calculate_margins)
        calc_layout.addWidget(self.cost_input, 0, 1)
        
        # Margin percentage slider
        calc_layout.addWidget(QLabel("Profit Margin (%):"), 1, 0)
        self.margin_slider = QSlider(Qt.Horizontal)
        self.margin_slider.setRange(0, 100)
        self.margin_slider.setValue(30)
        self.margin_slider.valueChanged.connect(self.calculate_margins)
        calc_layout.addWidget(self.margin_slider, 1, 1)
        
        self.margin_value_label = QLabel("30%")
        calc_layout.addWidget(self.margin_value_label, 1, 2)
        
        # Results
        calc_layout.addWidget(QLabel("Selling Price:"), 2, 0)
        self.selling_price_label = QLabel("₹130.00")
        self.selling_price_label.setStyleSheet("font-weight: bold; color: #10b981;")
        calc_layout.addWidget(self.selling_price_label, 2, 1)
        
        calc_layout.addWidget(QLabel("Profit Amount:"), 3, 0)
        self.profit_amount_label = QLabel("₹30.00")
        self.profit_amount_label.setStyleSheet("font-weight: bold; color: #3b82f6;")
        calc_layout.addWidget(self.profit_amount_label, 3, 1)
        
        layout.addWidget(calc_frame)
        
        # Margin scenarios
        self.create_scenarios_panel(layout)
        
        # Initial calculation
        self.calculate_margins()
    
    def create_scenarios_panel(self, parent_layout):
        """Create margin scenarios panel"""
        scenarios_frame = QFrame()
        scenarios_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        scenarios_layout = QVBoxLayout(scenarios_frame)
        
        scenarios_title = QLabel("📈 Margin Scenarios")
        scenarios_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #374151;")
        scenarios_layout.addWidget(scenarios_title)
        
        # Scenarios table
        self.scenarios_table = QTableWidget()
        self.scenarios_table.setColumnCount(4)
        self.scenarios_table.setHorizontalHeaderLabels([
            "Margin %", "Selling Price", "Profit", "Competitiveness"
        ])
        self.scenarios_table.setRowCount(5)
        
        scenarios_layout.addWidget(self.scenarios_table)
        parent_layout.addWidget(scenarios_frame)
    
    def calculate_margins(self):
        """Calculate profit margins and update display"""
        cost = self.cost_input.value()
        margin_percent = self.margin_slider.value()
        
        # Update margin label
        self.margin_value_label.setText(f"{margin_percent}%")
        
        # Calculate selling price and profit
        selling_price = cost * (1 + margin_percent / 100)
        profit_amount = selling_price - cost
        
        # Update labels
        self.selling_price_label.setText(f"₹{selling_price:.2f}")
        self.profit_amount_label.setText(f"₹{profit_amount:.2f}")
        
        # Update scenarios
        self.update_scenarios(cost)
        
        # Emit signal
        self.margin_changed.emit(cost, margin_percent)
    
    def update_scenarios(self, cost):
        """Update margin scenarios table"""
        scenarios = [
            (15, "Low margin - High volume"),
            (25, "Competitive margin"),
            (35, "Standard margin"),
            (45, "Premium margin"),
            (60, "Luxury margin")
        ]
        
        for row, (margin, description) in enumerate(scenarios):
            selling_price = cost * (1 + margin / 100)
            profit = selling_price - cost
            
            self.scenarios_table.setItem(row, 0, QTableWidgetItem(f"{margin}%"))
            self.scenarios_table.setItem(row, 1, QTableWidgetItem(f"₹{selling_price:.2f}"))
            self.scenarios_table.setItem(row, 2, QTableWidgetItem(f"₹{profit:.2f}"))
            self.scenarios_table.setItem(row, 3, QTableWidgetItem(description))


class CostTrendVisualization(QWidget):
    """Cost trend visualization widget"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        
        if MATPLOTLIB_AVAILABLE:
            self.init_ui()
        else:
            self.init_fallback_ui()
    
    def init_ui(self):
        """Initialize visualization UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📈 Cost Trend Analysis")
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Time period selector
        period_label = QLabel("Period:")
        header_layout.addWidget(period_label)
        
        self.period_selector = QComboBox()
        self.period_selector.addItems(["Last 7 days", "Last 30 days", "Last 3 months", "Last year"])
        self.period_selector.currentTextChanged.connect(self.update_trends)
        header_layout.addWidget(self.period_selector)
        
        layout.addLayout(header_layout)
        
        # Chart area
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Trend insights
        self.create_trend_insights(layout)
        
        # Load initial data
        self.update_trends()
    
    def init_fallback_ui(self):
        """Initialize fallback UI when matplotlib is not available"""
        layout = QVBoxLayout(self)
        
        fallback_label = QLabel("📈 Cost Trend Analysis\n\nMatplotlib not available.\nInstall matplotlib to see cost trend visualizations.")
        fallback_label.setAlignment(Qt.AlignCenter)
        fallback_label.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
        layout.addWidget(fallback_label)
    
    def create_trend_insights(self, parent_layout):
        """Create trend insights panel"""
        insights_frame = QFrame()
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        insights_layout = QHBoxLayout(insights_frame)
        
        # Trend indicators
        self.trend_up_label = QLabel("📈 Increasing: 0 items")
        self.trend_up_label.setStyleSheet("color: #ef4444; font-weight: 500;")
        insights_layout.addWidget(self.trend_up_label)
        
        self.trend_stable_label = QLabel("➡️ Stable: 0 items")
        self.trend_stable_label.setStyleSheet("color: #64748b; font-weight: 500;")
        insights_layout.addWidget(self.trend_stable_label)
        
        self.trend_down_label = QLabel("📉 Decreasing: 0 items")
        self.trend_down_label.setStyleSheet("color: #10b981; font-weight: 500;")
        insights_layout.addWidget(self.trend_down_label)
        
        insights_layout.addStretch()
        
        parent_layout.addWidget(insights_frame)
    
    def update_trends(self):
        """Update cost trend visualization"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        period = self.period_selector.currentText()
        
        # Generate sample trend data
        dates, costs = self.generate_sample_trend_data(period)
        
        # Clear and plot
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(dates, costs, marker='o', linewidth=2, markersize=4, color='#3b82f6')
        ax.fill_between(dates, costs, alpha=0.3, color='#3b82f6')
        
        ax.set_title(f'Cost Trends - {period}', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Average Cost (₹)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Update insights
        self.update_trend_insights(costs)
    
    def generate_sample_trend_data(self, period):
        """Generate sample trend data"""
        if period == "Last 7 days":
            days = 7
        elif period == "Last 30 days":
            days = 30
        elif period == "Last 3 months":
            days = 90
        else:  # Last year
            days = 365
        
        dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
        
        # Generate realistic cost trend
        base_cost = 100
        costs = []
        for i, date in enumerate(dates):
            # Add some trend and noise
            trend = i * 0.1  # Slight upward trend
            noise = np.random.normal(0, 5)  # Random variation
            cost = base_cost + trend + noise
            costs.append(max(cost, 50))  # Minimum cost of 50
        
        return dates, costs
    
    def update_trend_insights(self, costs):
        """Update trend insights based on cost data"""
        if len(costs) < 2:
            return
        
        # Calculate trend direction
        recent_avg = np.mean(costs[-7:]) if len(costs) >= 7 else costs[-1]
        older_avg = np.mean(costs[:7]) if len(costs) >= 14 else costs[0]
        
        change_percent = ((recent_avg - older_avg) / older_avg) * 100
        
        # Update labels (simplified for demo)
        if change_percent > 5:
            self.trend_up_label.setText("📈 Increasing: 15 items")
            self.trend_stable_label.setText("➡️ Stable: 8 items")
            self.trend_down_label.setText("📉 Decreasing: 3 items")
        elif change_percent < -5:
            self.trend_up_label.setText("📈 Increasing: 3 items")
            self.trend_stable_label.setText("➡️ Stable: 8 items")
            self.trend_down_label.setText("📉 Decreasing: 15 items")
        else:
            self.trend_up_label.setText("📈 Increasing: 5 items")
            self.trend_stable_label.setText("➡️ Stable: 18 items")
            self.trend_down_label.setText("📉 Decreasing: 3 items")


class AdvancedCostAnalysisPanel(QWidget):
    """Main advanced cost analysis panel"""
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.logger = logging.getLogger(__name__)

        # Debug: Print data information
        print("🔍 AdvancedCostAnalysisPanel - Data Debug:")
        print(f"  Data type: {type(self.data)}")
        if self.data:
            print(f"  Data keys: {list(self.data.keys())}")
            if 'recipes' in self.data:
                print(f"  Recipes count: {len(self.data['recipes'])}")
                if not self.data['recipes'].empty:
                    print(f"  Recipe columns: {list(self.data['recipes'].columns)}")
                    print(f"  First recipe: {self.data['recipes'].iloc[0]['recipe_name'] if 'recipe_name' in self.data['recipes'].columns else 'No recipe_name column'}")
                else:
                    print("  Recipes dataframe is empty")
            else:
                print("  No 'recipes' key in data")
        else:
            print("  Data is None or empty")

        self.init_ui()
    
    def init_ui(self):
        """Initialize the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("🔬 Advanced Cost Analysis")
        header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        layout.addWidget(header_label)
        
        # Tabbed interface
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Add tabs
        tabs.addTab(CostComparisonWidget(self.data), "📊 Recipe Comparison")
        tabs.addTab(ProfitMarginCalculator(), "💰 Profit Calculator")
        tabs.addTab(CostTrendVisualization(self.data), "📈 Cost Trends")
        
        layout.addWidget(tabs)

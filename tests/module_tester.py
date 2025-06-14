"""
Module Tester
Tests individual modules with sample data
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QProgressBar, QLabel
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont

class ModuleTester:
    """Tests individual modules with sample data"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = app_instance.logger
        
    def test_all_modules(self):
        """Test all available modules"""
        self.logger.info("Starting module testing...")
        
        # Create test dialog
        dialog = ModuleTestDialog(self.app)
        dialog.show()
        
        # Test each module
        modules_to_test = [
            ("Inventory Module", self.test_inventory_module),
            ("Shopping Module", self.test_shopping_module),
            ("Pricing Module", self.test_pricing_module),
            ("Sales Module", self.test_sales_module),
            ("Cleaning Module", self.test_cleaning_module),
            ("Settings Module", self.test_settings_module),
            ("Meal Planning Module", self.test_meal_planning_module),
            ("Budget Module", self.test_budget_module),
            ("Waste Module", self.test_waste_module),
            ("Packing Materials Module", self.test_packing_materials_module),
            ("Firebase Module", self.test_firebase_module),
            ("Notification Module", self.test_notification_module),
            ("Category Manager", self.test_category_manager),
            ("Analytics Engine", self.test_analytics_engine),
            ("AI Engine", self.test_ai_engine),
            ("Responsive Design", self.test_responsive_design),
            ("Performance Modules", self.test_performance_modules)
        ]
        
        results = []
        for module_name, test_function in modules_to_test:
            try:
                dialog.update_status(f"Testing {module_name}...")
                start_time = time.time()
                
                test_function()
                
                execution_time = time.time() - start_time
                result = f"✅ {module_name}: PASSED ({execution_time:.2f}s)"
                self.logger.info(f"Module test passed: {module_name}")
                
            except Exception as e:
                execution_time = time.time() - start_time
                result = f"❌ {module_name}: FAILED - {str(e)} ({execution_time:.2f}s)"
                self.logger.error(f"Module test failed: {module_name} - {str(e)}")
                
            results.append(result)
            dialog.add_result(result)
            
        dialog.update_status("All module tests completed!")
        self.logger.info("Module testing completed")
        
    def create_sample_inventory_data(self):
        """Create sample inventory data"""
        return pd.DataFrame({
            'item_id': range(1, 21),
            'item_name': [
                'Tomatoes', 'Onions', 'Potatoes', 'Carrots', 'Bell Peppers',
                'Rice', 'Wheat Flour', 'Lentils', 'Chickpeas', 'Quinoa',
                'Chicken Breast', 'Ground Beef', 'Salmon', 'Eggs', 'Milk',
                'Olive Oil', 'Salt', 'Black Pepper', 'Garlic', 'Ginger'
            ],
            'category': [
                'Vegetables', 'Vegetables', 'Vegetables', 'Vegetables', 'Vegetables',
                'Grains', 'Grains', 'Legumes', 'Legumes', 'Grains',
                'Meat', 'Meat', 'Seafood', 'Dairy', 'Dairy',
                'Oils', 'Spices', 'Spices', 'Vegetables', 'Spices'
            ],
            'quantity': [10, 5, 15, 8, 6, 25, 10, 5, 3, 2, 3, 2, 1, 24, 4, 1, 1, 0.5, 0.5, 0.3],
            'unit': ['kg'] * 10 + ['kg'] * 5 + ['liters'] * 2 + ['kg'] * 3,
            'price_per_unit': [50, 30, 25, 40, 80, 60, 45, 120, 150, 200, 300, 250, 500, 8, 60, 150, 20, 100, 80, 200],
            'location': ['Fridge'] * 5 + ['Pantry'] * 10 + ['Fridge'] * 5,
            'expiry_date': [(datetime.now() + timedelta(days=np.random.randint(1, 30))).date() for _ in range(20)],
            'reorder_level': [5, 2, 10, 5, 3, 10, 5, 2, 1, 1, 1, 1, 0, 12, 2, 0, 0, 0, 0, 0]
        })
        
    def create_sample_shopping_data(self):
        """Create sample shopping list data"""
        return pd.DataFrame({
            'item_id': range(1, 16),
            'item_name': [
                'Bread', 'Butter', 'Cheese', 'Yogurt', 'Apples',
                'Bananas', 'Oranges', 'Pasta', 'Tomato Sauce', 'Basil',
                'Mushrooms', 'Spinach', 'Chicken Thighs', 'Fish Fillets', 'Shrimp'
            ],
            'category': [
                'Bakery', 'Dairy', 'Dairy', 'Dairy', 'Fruits',
                'Fruits', 'Fruits', 'Grains', 'Canned Goods', 'Herbs',
                'Vegetables', 'Vegetables', 'Meat', 'Seafood', 'Seafood'
            ],
            'quantity': [2, 1, 0.5, 4, 2, 1, 3, 1, 2, 1, 0.5, 1, 1, 1, 0.5],
            'unit': ['loaves', 'pack', 'kg', 'cups', 'kg', 'bunch', 'kg', 'pack', 'cans', 'pack', 'kg', 'bunch', 'kg', 'kg', 'kg'],
            'priority': ['High', 'Medium', 'Low', 'Medium', 'High', 'Medium', 'Low', 'High', 'Medium', 'Low', 'Medium', 'High', 'Medium', 'Low', 'Medium'],
            'last_price': [40, 80, 400, 15, 120, 60, 80, 50, 25, 30, 150, 40, 280, 350, 600],
            'status': ['Pending'] * 15,
            'date_added': [datetime.now().date()] * 15
        })
        
    def create_sample_recipe_data(self):
        """Create sample recipe data"""
        recipes = pd.DataFrame({
            'recipe_id': range(1, 11),
            'recipe_name': [
                'Pasta Marinara', 'Chicken Curry', 'Vegetable Stir Fry', 'Caesar Salad', 'Tomato Soup',
                'Grilled Salmon', 'Beef Tacos', 'Mushroom Risotto', 'Greek Salad', 'Chicken Sandwich'
            ],
            'category': [
                'Main Course', 'Main Course', 'Main Course', 'Salad', 'Soup',
                'Main Course', 'Main Course', 'Main Course', 'Salad', 'Sandwich'
            ],
            'servings': [4, 6, 4, 2, 4, 2, 4, 4, 3, 2],
            'prep_time': [15, 20, 10, 15, 10, 5, 15, 10, 10, 10],
            'cook_time': [20, 45, 15, 0, 25, 15, 20, 30, 0, 10],
            'description': [
                'Classic pasta with marinara sauce',
                'Spicy chicken curry with rice',
                'Fresh vegetables stir-fried',
                'Traditional Caesar salad',
                'Creamy tomato soup',
                'Grilled salmon with herbs',
                'Mexican-style beef tacos',
                'Creamy mushroom risotto',
                'Fresh Greek salad',
                'Grilled chicken sandwich'
            ]
        })
        
        ingredients = pd.DataFrame({
            'recipe_id': [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10],
            'item_name': [
                'Pasta', 'Tomato Sauce', 'Basil',
                'Chicken Breast', 'Rice', 'Curry Powder',
                'Bell Peppers', 'Mushrooms',
                'Lettuce', 'Cheese',
                'Tomatoes', 'Milk',
                'Salmon',
                'Ground Beef',
                'Rice',
                'Lettuce',
                'Chicken Breast'
            ],
            'quantity': [500, 400, 20, 600, 300, 15, 200, 150, 200, 100, 400, 200, 300, 400, 250, 150, 200],
            'unit': ['g', 'ml', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'ml', 'g', 'g', 'g', 'g', 'g']
        })
        
        return recipes, ingredients
        
    def create_sample_sales_data(self):
        """Create sample sales data"""
        return pd.DataFrame({
            'sale_id': range(1, 21),
            'item_name': [
                'Pasta Marinara', 'Chicken Curry', 'Caesar Salad', 'Tomato Soup', 'Grilled Salmon',
                'Beef Tacos', 'Mushroom Risotto', 'Greek Salad', 'Chicken Sandwich', 'Vegetable Stir Fry'
            ] * 2,
            'quantity': [2, 1, 3, 2, 1, 4, 1, 2, 3, 2] * 2,
            'price_per_unit': [150, 200, 120, 80, 300, 180, 220, 100, 140, 160] * 2,
            'total_amount': [300, 200, 360, 160, 300, 720, 220, 200, 420, 320] * 2,
            'customer': [f'Customer {i}' for i in range(1, 21)],
            'date': [(datetime.now() - timedelta(days=np.random.randint(0, 30))).date() for _ in range(20)]
        })
        
    def test_inventory_module(self):
        """Test inventory module"""
        try:
            from modules.inventory_fixed import InventoryWidget
            
            sample_data = self.create_sample_inventory_data()
            data = {'inventory': sample_data}
            
            # Test widget creation
            widget = InventoryWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            # Test data loading
            widget.load_data()
            
            # Test table population
            if hasattr(widget, 'table'):
                assert widget.table.rowCount() > 0, "Table should have data"
                
            self.logger.info("Inventory module test completed successfully")
            
        except ImportError:
            raise Exception("Inventory module not available")
            
    def test_shopping_module(self):
        """Test shopping module"""
        try:
            from modules.shopping_fixed import ShoppingWidget
            
            sample_data = self.create_sample_shopping_data()
            data = {'shopping_list': sample_data}
            
            # Test widget creation
            widget = ShoppingWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            # Test data loading
            widget.load_data()
            
            self.logger.info("Shopping module test completed successfully")
            
        except ImportError:
            raise Exception("Shopping module not available")
            
    def test_pricing_module(self):
        """Test pricing module"""
        try:
            from modules.pricing_management import PricingWidget
            
            recipes, ingredients = self.create_sample_recipe_data()
            inventory_data = self.create_sample_inventory_data()
            
            data = {
                'recipes': recipes,
                'recipe_ingredients': ingredients,
                'inventory': inventory_data,
                'packing_materials': pd.DataFrame()
            }
            
            # Test widget creation
            widget = PricingWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Pricing module test completed successfully")
            
        except ImportError:
            raise Exception("Pricing module not available")
            
    def test_sales_module(self):
        """Test sales module"""
        try:
            from modules.enhanced_sales import EnhancedSalesWidget
            
            sample_data = self.create_sample_sales_data()
            data = {'sales': sample_data}
            
            # Test widget creation
            widget = EnhancedSalesWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Sales module test completed successfully")
            
        except ImportError:
            raise Exception("Sales module not available")
            
    def test_cleaning_module(self):
        """Test cleaning module"""
        try:
            from modules.cleaning_fixed import CleaningWidget
            
            sample_data = pd.DataFrame({
                'task_id': range(1, 11),
                'task_name': [
                    'Clean Kitchen Counters', 'Sanitize Equipment', 'Mop Floors', 'Clean Refrigerator',
                    'Wash Dishes', 'Clean Stove', 'Sanitize Cutting Boards', 'Clean Sink',
                    'Empty Trash', 'Wipe Tables'
                ],
                'frequency': ['Daily'] * 5 + ['Weekly'] * 3 + ['Daily'] * 2,
                'last_completed': [(datetime.now() - timedelta(days=np.random.randint(0, 7))).date() for _ in range(10)],
                'next_due': [(datetime.now() + timedelta(days=np.random.randint(1, 7))).date() for _ in range(10)],
                'priority': ['High'] * 3 + ['Medium'] * 4 + ['Low'] * 3,
                'notes': [''] * 10
            })
            
            data = {'cleaning_maintenance': sample_data}
            
            # Test widget creation
            widget = CleaningWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Cleaning module test completed successfully")
            
        except ImportError:
            raise Exception("Cleaning module not available")
            
    def test_settings_module(self):
        """Test settings module"""
        try:
            from modules.settings_fixed import SettingsWidget
            
            # Test widget creation
            widget = SettingsWidget(self.app, self.app.data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Settings module test completed successfully")
            
        except ImportError:
            raise Exception("Settings module not available")
            
    def test_meal_planning_module(self):
        """Test meal planning module"""
        try:
            from modules.fixed_meal_planning import MealPlanningWidget
            
            sample_data = pd.DataFrame({
                'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] * 3,
                'meal_type': ['Breakfast'] * 7 + ['Lunch'] * 7 + ['Dinner'] * 7,
                'recipe_id': range(1, 22),
                'recipe_name': [
                    'Oatmeal', 'Pancakes', 'Toast', 'Cereal', 'Eggs', 'Smoothie', 'Yogurt',
                    'Sandwich', 'Salad', 'Soup', 'Pasta', 'Rice Bowl', 'Wrap', 'Pizza',
                    'Steak', 'Fish', 'Chicken', 'Curry', 'Stir Fry', 'Tacos', 'Burger'
                ],
                'servings': [2] * 21,
                'prep_time': [10] * 7 + [15] * 7 + [30] * 7,
                'cook_time': [5] * 7 + [10] * 7 + [25] * 7
            })
            
            data = {'meal_plan': sample_data}
            
            # Test widget creation
            widget = MealPlanningWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Meal planning module test completed successfully")
            
        except ImportError:
            raise Exception("Meal planning module not available")
            
    def test_budget_module(self):
        """Test budget module"""
        try:
            from modules.enhanced_budget import EnhancedBudgetWidget
            
            sample_data = pd.DataFrame({
                'budget_id': range(1, 11),
                'category': [
                    'Vegetables', 'Fruits', 'Meat', 'Dairy', 'Grains',
                    'Spices', 'Oils', 'Beverages', 'Snacks', 'Cleaning'
                ],
                'amount': [5000, 3000, 8000, 4000, 3000, 1000, 1500, 2000, 1500, 1000],
                'period': ['Monthly'] * 10,
                'date': [datetime.now().date()] * 10
            })
            
            data = {'budget': sample_data}
            
            # Test widget creation
            widget = EnhancedBudgetWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Budget module test completed successfully")
            
        except ImportError:
            raise Exception("Budget module not available")
            
    def test_waste_module(self):
        """Test waste module"""
        try:
            from modules.waste import WasteWidget
            
            sample_data = pd.DataFrame({
                'waste_id': range(1, 11),
                'item_name': [
                    'Expired Milk', 'Spoiled Vegetables', 'Burnt Food', 'Overripe Fruits',
                    'Stale Bread', 'Expired Yogurt', 'Moldy Cheese', 'Rotten Meat',
                    'Wilted Lettuce', 'Sour Cream'
                ],
                'quantity': [1, 2, 0.5, 1.5, 1, 2, 0.3, 1, 0.5, 1],
                'unit': ['liter', 'kg', 'kg', 'kg', 'loaf', 'cups', 'kg', 'kg', 'kg', 'cup'],
                'reason': [
                    'Expired', 'Spoiled', 'Burnt', 'Overripe', 'Stale',
                    'Expired', 'Moldy', 'Rotten', 'Wilted', 'Sour'
                ],
                'cost': [60, 100, 50, 80, 40, 30, 120, 300, 25, 45],
                'date': [(datetime.now() - timedelta(days=np.random.randint(0, 30))).date() for _ in range(10)]
            })
            
            data = {'waste': sample_data}
            
            # Test widget creation
            widget = WasteWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Waste module test completed successfully")
            
        except ImportError:
            raise Exception("Waste module not available")
            
    def test_packing_materials_module(self):
        """Test packing materials module"""
        try:
            from modules.packing_materials import PackingMaterialsWidget
            
            sample_data = pd.DataFrame({
                'material_id': range(1, 11),
                'material_name': [
                    'Small Box', 'Medium Box', 'Large Box', 'Bubble Wrap', 'Packing Tape',
                    'Food Containers', 'Plastic Bags', 'Paper Bags', 'Aluminum Foil', 'Cling Wrap'
                ],
                'category': [
                    'Boxes', 'Boxes', 'Boxes', 'Protection', 'Adhesive',
                    'Containers', 'Bags', 'Bags', 'Wrapping', 'Wrapping'
                ],
                'size': ['Small', 'Medium', 'Large', 'Roll', 'Roll', 'Various', 'Small', 'Medium', 'Roll', 'Roll'],
                'unit': ['piece', 'piece', 'piece', 'meter', 'meter', 'piece', 'piece', 'piece', 'meter', 'meter'],
                'cost_per_unit': [5, 8, 12, 2, 1, 15, 0.5, 1, 3, 2],
                'current_stock': [100, 50, 25, 200, 150, 80, 500, 200, 100, 150],
                'minimum_stock': [20, 10, 5, 50, 30, 20, 100, 50, 20, 30],
                'supplier': ['Supplier A'] * 5 + ['Supplier B'] * 5,
                'notes': [''] * 10,
                'date_added': [datetime.now().date()] * 10
            })
            
            data = {'packing_materials': sample_data}
            
            # Test widget creation
            widget = PackingMaterialsWidget(self.app, data)
            assert widget is not None, "Widget creation failed"
            
            self.logger.info("Packing materials module test completed successfully")
            
        except ImportError:
            raise Exception("Packing materials module not available")
            
    def test_firebase_module(self):
        """Test Firebase module"""
        try:
            from modules.firebase_sync import FirebaseSync
            
            # Test Firebase sync creation
            firebase_sync = FirebaseSync(self.app, self.app.data, "data")
            assert firebase_sync is not None, "Firebase sync creation failed"
            
            # Test availability check
            is_available = firebase_sync.is_firebase_available()
            assert isinstance(is_available, bool), "Firebase availability check failed"
            
            self.logger.info("Firebase module test completed successfully")
            
        except ImportError:
            raise Exception("Firebase module not available")
            
    def test_notification_module(self):
        """Test notification module"""
        try:
            from modules.notification_system import get_notification_manager
            
            # Test notification manager
            notification_manager = get_notification_manager(self.app)
            assert notification_manager is not None, "Notification manager creation failed"
            
            self.logger.info("Notification module test completed successfully")
            
        except ImportError:
            raise Exception("Notification module not available")
            
    def test_category_manager(self):
        """Test category manager"""
        try:
            from modules.category_manager import CategoryManager
            
            # Test category manager creation
            category_manager = CategoryManager(self.app.data)
            assert category_manager is not None, "Category manager creation failed"
            
            # Test synchronization
            result = category_manager.synchronize_categories()
            assert isinstance(result, dict), "Category synchronization should return a dict"
            assert 'success' in result, "Synchronization result should have 'success' key"
            
            self.logger.info("Category manager test completed successfully")
            
        except ImportError:
            raise Exception("Category manager not available")
            
    def test_analytics_engine(self):
        """Test analytics engine"""
        try:
            from modules.analytics_engine import AnalyticsEngine
            
            # Test analytics engine creation
            analytics = AnalyticsEngine(self.app.data)
            assert analytics is not None, "Analytics engine creation failed"
            
            self.logger.info("Analytics engine test completed successfully")
            
        except ImportError:
            raise Exception("Analytics engine not available")
            
    def test_ai_engine(self):
        """Test AI engine"""
        try:
            from modules.multi_ai_engine import MultiAIEngine
            
            # Test AI engine creation
            ai_engine = MultiAIEngine(self.app.data)
            assert ai_engine is not None, "AI engine creation failed"
            
            self.logger.info("AI engine test completed successfully")
            
        except ImportError:
            raise Exception("AI engine not available")
            
    def test_responsive_design(self):
        """Test responsive design"""
        try:
            from modules.responsive_design_manager import get_responsive_manager
            
            # Test responsive manager
            responsive_manager = get_responsive_manager()
            assert responsive_manager is not None, "Responsive manager creation failed"
            
            self.logger.info("Responsive design test completed successfully")
            
        except ImportError:
            raise Exception("Responsive design not available")
            
    def test_performance_modules(self):
        """Test performance modules"""
        try:
            # Test performance optimizer
            from modules.performance_optimizer import PerformanceOptimizer
            
            optimizer = PerformanceOptimizer()
            assert optimizer is not None, "Performance optimizer creation failed"
            
            self.logger.info("Performance modules test completed successfully")
            
        except ImportError:
            raise Exception("Performance modules not available")


class ModuleTestDialog(QDialog):
    """Dialog for displaying module test results"""
    
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.app = app_instance
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Module Testing")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Kitchen Dashboard - Module Testing")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header_label)
        
        # Status label
        self.status_label = QLabel("Preparing tests...")
        layout.addWidget(self.status_label)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
        
    def add_result(self, result):
        """Add test result"""
        self.results_text.append(result)

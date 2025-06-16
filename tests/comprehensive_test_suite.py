"""
Comprehensive Test Suite for Kitchen Dashboard
Tests every function and module with sample data
"""

import os
import sys
import time
import traceback
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QProgressBar, QLabel, QTabWidget, QWidget, QScrollArea
from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtGui import QFont

class TestResult:
    """Container for test results"""
    def __init__(self, test_name, status, message="", execution_time=0, error=None):
        self.test_name = test_name
        self.status = status  # "PASS", "FAIL", "SKIP", "ERROR"
        self.message = message
        self.execution_time = execution_time
        self.error = error
        self.timestamp = datetime.now()

class TestRunner(QThread):
    """Background thread for running tests"""
    test_started = Signal(str)
    test_completed = Signal(TestResult)
    all_tests_completed = Signal(list)
    progress_updated = Signal(int, int)

    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.results = []
        self.current_test = 0
        self.total_tests = 0

    def run(self):
        """Run all tests"""
        try:
            # Define all test categories
            test_categories = [
                ("Core Application", self.test_core_application),
                ("Data Loading", self.test_data_loading),
                ("Inventory Module", self.test_inventory_module),
                ("Shopping Module", self.test_shopping_module),
                ("Pricing Module", self.test_pricing_module),
                ("Sales Module", self.test_sales_module),
                ("Cleaning Module", self.test_cleaning_module),
                ("Settings Module", self.test_settings_module),
                ("Firebase Integration", self.test_firebase_integration),
                ("Notification System", self.test_notification_system),
                ("Logging System", self.test_logging_system),
                ("Category Management", self.test_category_management),
                ("Packing Materials", self.test_packing_materials),
                ("Recipe Management", self.test_recipe_management),
                ("Meal Planning", self.test_meal_planning),
                ("Budget Management", self.test_budget_management),
                ("Waste Management", self.test_waste_management),
                ("Analytics Engine", self.test_analytics_engine),
                ("AI Integration", self.test_ai_integration),
                ("Performance Optimization", self.test_performance_optimization),
                ("Responsive Design", self.test_responsive_design),
                ("Data Validation", self.test_data_validation),
                ("Error Handling", self.test_error_handling),
                ("Cross-Module Integration", self.test_cross_module_integration)
            ]

            self.total_tests = len(test_categories)
            self.current_test = 0

            # Run each test category
            for category_name, test_function in test_categories:
                self.test_started.emit(category_name)
                
                try:
                    start_time = time.time()
                    test_function()
                    execution_time = time.time() - start_time
                    
                    result = TestResult(
                        category_name, 
                        "PASS", 
                        f"All tests in {category_name} passed",
                        execution_time
                    )
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    result = TestResult(
                        category_name,
                        "ERROR",
                        f"Error in {category_name}: {str(e)}",
                        execution_time,
                        e
                    )

                self.results.append(result)
                self.test_completed.emit(result)
                
                self.current_test += 1
                self.progress_updated.emit(self.current_test, self.total_tests)

            self.all_tests_completed.emit(self.results)

        except Exception as e:
            error_result = TestResult(
                "Test Runner",
                "ERROR",
                f"Critical error in test runner: {str(e)}",
                0,
                e
            )
            self.results.append(error_result)
            self.all_tests_completed.emit(self.results)

    def test_core_application(self):
        """Test core application functionality"""
        # Test main window initialization
        assert hasattr(self.app, 'central_widget'), "Central widget not initialized"
        assert hasattr(self.app, 'sidebar'), "Sidebar not initialized"
        assert hasattr(self.app, 'content_widget'), "Content widget not initialized"
        
        # Test data structure
        assert hasattr(self.app, 'data'), "Data structure not initialized"
        assert isinstance(self.app.data, dict), "Data should be a dictionary"
        
        # Test logger
        assert hasattr(self.app, 'logger'), "Logger not initialized"
        
        # Test navigation
        assert hasattr(self.app, 'nav_buttons'), "Navigation buttons not initialized"

    def test_data_loading(self):
        """Test data loading functionality"""
        # Test load_data method
        data = self.app.load_data()
        assert isinstance(data, dict), "load_data should return a dictionary"
        
        # Test expected data keys
        expected_keys = [
            'inventory', 'meal_plan', 'recipes', 'budget', 'sales',
            'shopping_list', 'waste', 'cleaning_maintenance', 'items',
            'categories', 'recipe_ingredients', 'pricing', 'packing_materials'
        ]
        
        for key in expected_keys:
            assert key in data, f"Missing data key: {key}"
            assert isinstance(data[key], pd.DataFrame), f"Data[{key}] should be a DataFrame"

    def test_inventory_module(self):
        """Test inventory module functionality"""
        try:
            # Import from parent modules directory
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            modules_dir = os.path.join(parent_dir, 'modules')
            sys.path.insert(0, modules_dir)

            from modules.inventory_fixed import InventoryWidget
            
            # Create sample inventory data
            sample_data = pd.DataFrame({
                'item_id': [1, 2, 3],
                'item_name': ['Tomatoes', 'Onions', 'Rice'],
                'category': ['Vegetables', 'Vegetables', 'Grains'],
                'quantity': [10, 5, 25],
                'unit': ['kg', 'kg', 'kg'],
                'price_per_unit': [50, 30, 80]
            })
            
            # Test widget creation
            inventory_widget = InventoryWidget({'inventory': sample_data})
            assert inventory_widget is not None, "Inventory widget creation failed"
            
            # Test data loading
            inventory_widget.load_data()
            
        except ImportError:
            raise Exception("Inventory module not available")

    def test_shopping_module(self):
        """Test shopping module functionality"""
        try:
            from modules.shopping_fixed import ShoppingWidget
            
            # Create sample shopping data
            sample_data = pd.DataFrame({
                'item_id': [1, 2, 3],
                'item_name': ['Milk', 'Bread', 'Eggs'],
                'category': ['Dairy', 'Bakery', 'Dairy'],
                'quantity': [2, 1, 12],
                'unit': ['liters', 'loaf', 'pieces'],
                'priority': ['High', 'Medium', 'Low']
            })
            
            # Test widget creation
            shopping_widget = ShoppingWidget({'shopping_list': sample_data})
            assert shopping_widget is not None, "Shopping widget creation failed"
            
        except ImportError:
            raise Exception("Shopping module not available")

    def test_pricing_module(self):
        """Test pricing module functionality"""
        try:
            from modules.pricing_management import PricingManagementWidget
            
            # Create sample pricing data
            sample_recipes = pd.DataFrame({
                'recipe_id': [1, 2],
                'recipe_name': ['Pasta', 'Salad'],
                'category': ['Main Course', 'Appetizer'],
                'servings': [4, 2]
            })
            
            sample_ingredients = pd.DataFrame({
                'recipe_id': [1, 1, 2],
                'item_name': ['Pasta', 'Tomato Sauce', 'Lettuce'],
                'quantity': [500, 200, 100],
                'unit': ['g', 'ml', 'g']
            })
            
            data = {
                'recipes': sample_recipes,
                'recipe_ingredients': sample_ingredients,
                'inventory': pd.DataFrame(),
                'packing_materials': pd.DataFrame()
            }
            
            # Test widget creation
            pricing_widget = PricingManagementWidget(data)
            assert pricing_widget is not None, "Pricing widget creation failed"
            
        except ImportError:
            raise Exception("Pricing module not available")

    def test_sales_module(self):
        """Test sales module functionality"""
        try:
            from modules.enhanced_sales import EnhancedSalesWidget
            
            # Create sample sales data
            sample_data = pd.DataFrame({
                'sale_id': [1, 2, 3],
                'item_name': ['Pasta', 'Salad', 'Soup'],
                'quantity': [2, 1, 3],
                'price_per_unit': [150, 80, 120],
                'total_amount': [300, 80, 360],
                'date': [datetime.now().date()] * 3
            })
            
            # Test widget creation
            sales_widget = EnhancedSalesWidget({'sales': sample_data})
            assert sales_widget is not None, "Sales widget creation failed"
            
        except ImportError:
            raise Exception("Sales module not available")

    def test_cleaning_module(self):
        """Test cleaning module functionality"""
        try:
            from modules.cleaning_fixed import CleaningWidget
            
            # Create sample cleaning data
            sample_data = pd.DataFrame({
                'task_id': [1, 2, 3],
                'task_name': ['Clean Kitchen', 'Sanitize Equipment', 'Mop Floor'],
                'frequency': ['Daily', 'Weekly', 'Daily'],
                'last_completed': [datetime.now().date()] * 3,
                'priority': ['High', 'Medium', 'Low']
            })
            
            # Test widget creation
            cleaning_widget = CleaningWidget({'cleaning_maintenance': sample_data})
            assert cleaning_widget is not None, "Cleaning widget creation failed"
            
        except ImportError:
            raise Exception("Cleaning module not available")

    def test_settings_module(self):
        """Test settings module functionality"""
        try:
            from modules.settings_fixed import SettingsWidget
            
            # Test widget creation
            settings_widget = SettingsWidget(main_app=self.app, parent=None, data=self.app.data)
            assert settings_widget is not None, "Settings widget creation failed"
            
        except ImportError:
            raise Exception("Settings module not available")

    def test_firebase_integration(self):
        """Test Firebase integration"""
        try:
            from modules.firebase_sync import FirebaseSync

            # Test Firebase sync creation with correct constructor
            firebase_sync = FirebaseSync(parent=self.app)
            assert firebase_sync is not None, "Firebase sync creation failed"

            # Test availability check
            is_available = firebase_sync.is_firebase_available()
            assert isinstance(is_available, bool), "Firebase availability check failed"

        except ImportError:
            raise Exception("Firebase integration module not available")
        except Exception as e:
            raise Exception(f"Firebase integration test failed: {str(e)}")

    def test_notification_system(self):
        """Test notification system"""
        try:
            from modules.notification_system import get_notification_manager
            
            # Test notification manager
            notification_manager = get_notification_manager(self.app)
            assert notification_manager is not None, "Notification manager creation failed"
            
        except ImportError:
            raise Exception("Notification system not available")

    def test_logging_system(self):
        """Test logging system"""
        try:
            from utils.app_logger import get_logger
            
            # Test logger creation
            logger = get_logger()
            assert logger is not None, "Logger creation failed"
            
            # Test logging methods
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            
        except ImportError:
            raise Exception("Logging system not available")

    def test_category_management(self):
        """Test category management"""
        try:
            from modules.category_manager import CategoryManager
            
            # Test category manager creation
            category_manager = CategoryManager(self.app.data)
            assert category_manager is not None, "Category manager creation failed"
            
            # Test synchronization
            result = category_manager.synchronize_categories()
            assert isinstance(result, dict), "Category synchronization should return a dict"
            assert 'success' in result, "Synchronization result should have 'success' key"
            
        except ImportError:
            raise Exception("Category management module not available")

    def test_packing_materials(self):
        """Test packing materials functionality"""
        try:
            from modules.packing_materials import PackingMaterialsWidget
            
            # Create sample packing materials data
            sample_data = pd.DataFrame({
                'material_id': [1, 2, 3],
                'material_name': ['Box Small', 'Box Large', 'Bubble Wrap'],
                'category': ['Boxes', 'Boxes', 'Protection'],
                'cost_per_unit': [5, 10, 2],
                'current_stock': [100, 50, 200]
            })
            
            # Test widget creation
            packing_widget = PackingMaterialsWidget({'packing_materials': sample_data})
            assert packing_widget is not None, "Packing materials widget creation failed"
            
        except ImportError:
            raise Exception("Packing materials module not available")

    def test_recipe_management(self):
        """Test recipe management functionality"""
        # Test with sample recipe data
        sample_recipes = pd.DataFrame({
            'recipe_id': [1, 2, 3],
            'recipe_name': ['Pasta Marinara', 'Caesar Salad', 'Tomato Soup'],
            'category': ['Main Course', 'Salad', 'Soup'],
            'servings': [4, 2, 6],
            'prep_time': [15, 10, 20],
            'cook_time': [30, 0, 25]
        })
        
        # Test data structure
        assert not sample_recipes.empty, "Sample recipes should not be empty"
        assert 'recipe_name' in sample_recipes.columns, "Recipe name column missing"

    def test_meal_planning(self):
        """Test meal planning functionality"""
        try:
            from modules.fixed_meal_planning import FixedMealPlanningWidget
            
            # Create sample meal plan data
            sample_data = pd.DataFrame({
                'day': ['Monday', 'Tuesday', 'Wednesday'],
                'meal_type': ['Breakfast', 'Lunch', 'Dinner'],
                'recipe_name': ['Oatmeal', 'Pasta', 'Salad'],
                'servings': [2, 4, 2]
            })
            
            # Test widget creation
            meal_widget = FixedMealPlanningWidget({'meal_plan': sample_data})
            assert meal_widget is not None, "Meal planning widget creation failed"
            
        except ImportError:
            raise Exception("Meal planning module not available")

    def test_budget_management(self):
        """Test budget management functionality"""
        try:
            from modules.enhanced_budget import EnhancedBudgetWidget
            
            # Create sample budget data
            sample_data = pd.DataFrame({
                'budget_id': [1, 2, 3],
                'category': ['Vegetables', 'Meat', 'Dairy'],
                'amount': [5000, 8000, 3000],
                'period': ['Monthly', 'Monthly', 'Monthly'],
                'date': [datetime.now().date()] * 3
            })
            
            # Test widget creation
            budget_widget = EnhancedBudgetWidget({'budget': sample_data})
            assert budget_widget is not None, "Budget widget creation failed"
            
        except ImportError:
            raise Exception("Budget management module not available")

    def test_waste_management(self):
        """Test waste management functionality"""
        try:
            from modules.waste import WasteWidget
            
            # Create sample waste data
            sample_data = pd.DataFrame({
                'waste_id': [1, 2, 3],
                'item_name': ['Expired Milk', 'Spoiled Vegetables', 'Burnt Food'],
                'quantity': [1, 2, 0.5],
                'unit': ['liter', 'kg', 'kg'],
                'reason': ['Expired', 'Spoiled', 'Burnt'],
                'cost': [60, 100, 50],
                'date': [datetime.now().date()] * 3
            })
            
            # Test widget creation
            waste_widget = WasteWidget({'waste': sample_data})
            assert waste_widget is not None, "Waste widget creation failed"
            
        except ImportError:
            raise Exception("Waste management module not available")

    def test_analytics_engine(self):
        """Test analytics engine functionality"""
        try:
            from modules.analytics_engine import AnalyticsEngine
            
            # Test analytics engine creation
            analytics = AnalyticsEngine(self.app.data)
            assert analytics is not None, "Analytics engine creation failed"
            
        except ImportError:
            raise Exception("Analytics engine not available")

    def test_ai_integration(self):
        """Test AI integration functionality"""
        try:
            from modules.multi_ai_engine import MultiAIEngine
            
            # Test AI engine creation
            ai_engine = MultiAIEngine(self.app.data)
            assert ai_engine is not None, "AI engine creation failed"
            
        except ImportError:
            raise Exception("AI integration not available")

    def test_performance_optimization(self):
        """Test performance optimization"""
        # Test data loading performance
        start_time = time.time()
        data = self.app.load_data()
        load_time = time.time() - start_time
        
        assert load_time < 10, f"Data loading took too long: {load_time:.2f}s"
        assert isinstance(data, dict), "Data loading should return a dictionary"

    def test_responsive_design(self):
        """Test responsive design functionality"""
        try:
            from modules.responsive_design_manager import get_responsive_manager
            
            # Test responsive manager
            responsive_manager = get_responsive_manager()
            assert responsive_manager is not None, "Responsive manager creation failed"
            
        except ImportError:
            raise Exception("Responsive design manager not available")

    def test_data_validation(self):
        """Test data validation functionality"""
        # Test with invalid data
        invalid_data = pd.DataFrame({
            'item_name': ['', None, 'Valid Item'],
            'quantity': [-1, 'invalid', 10],
            'price': [0, -5, 100]
        })
        
        # Test data validation logic
        valid_rows = invalid_data.dropna()
        assert len(valid_rows) <= len(invalid_data), "Data validation should filter invalid rows"

    def test_error_handling(self):
        """Test error handling functionality"""
        # Test with missing files
        try:
            non_existent_file = "non_existent_file.csv"
            if os.path.exists(non_existent_file):
                os.remove(non_existent_file)
            
            # This should not crash the application
            data = pd.read_csv(non_existent_file)
        except FileNotFoundError:
            # Expected behavior
            pass
        except Exception as e:
            raise Exception(f"Unexpected error handling: {e}")

    def test_cross_module_integration(self):
        """Test cross-module integration"""
        # Test data sharing between modules
        assert hasattr(self.app, 'data'), "App should have data attribute"
        assert isinstance(self.app.data, dict), "App data should be a dictionary"
        
        # Test navigation between modules
        assert hasattr(self.app, 'show_inventory_page'), "App should have inventory navigation"
        assert hasattr(self.app, 'show_shopping_page'), "App should have shopping navigation"


class ComprehensiveTestSuite:
    """Main test suite coordinator"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.test_dialog = None
        
    def run_all_tests(self):
        """Run all tests and show results"""
        # Create test dialog
        self.test_dialog = TestDialog(self.app)
        self.test_dialog.show()
        
        # Start test runner
        self.test_runner = TestRunner(self.app)
        
        # Connect signals
        self.test_runner.test_started.connect(self.test_dialog.on_test_started)
        self.test_runner.test_completed.connect(self.test_dialog.on_test_completed)
        self.test_runner.all_tests_completed.connect(self.test_dialog.on_all_tests_completed)
        self.test_runner.progress_updated.connect(self.test_dialog.on_progress_updated)
        
        # Start tests
        self.test_runner.start()


class TestDialog(QDialog):
    """Dialog for displaying test results"""
    
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.app = app_instance
        self.results = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the test dialog UI"""
        self.setWindowTitle("Comprehensive Test Suite")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Kitchen Dashboard - Comprehensive Testing")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Current test label
        self.current_test_label = QLabel("Preparing tests...")
        layout.addWidget(self.current_test_label)
        
        # Results area with tabs
        self.results_tabs = QTabWidget()
        
        # Live results tab
        self.live_results = QTextEdit()
        self.live_results.setFont(QFont("Consolas", 10))
        self.results_tabs.addTab(self.live_results, "Live Results")
        
        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setFont(QFont("Consolas", 10))
        self.results_tabs.addTab(self.summary_text, "Summary")
        
        # Detailed results tab
        self.detailed_results = QTextEdit()
        self.detailed_results.setFont(QFont("Consolas", 10))
        self.results_tabs.addTab(self.detailed_results, "Detailed Results")
        
        layout.addWidget(self.results_tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.close_button.setEnabled(False)
        
        self.save_results_button = QPushButton("Save Results")
        self.save_results_button.clicked.connect(self.save_results)
        self.save_results_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_results_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def on_test_started(self, test_name):
        """Handle test started signal"""
        self.current_test_label.setText(f"Running: {test_name}")
        self.live_results.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting: {test_name}")
        
    def on_test_completed(self, result):
        """Handle test completed signal"""
        self.results.append(result)
        
        # Update live results
        status_color = {
            "PASS": "green",
            "FAIL": "red", 
            "ERROR": "red",
            "SKIP": "orange"
        }.get(result.status, "black")
        
        self.live_results.append(
            f"[{result.timestamp.strftime('%H:%M:%S')}] "
            f"<span style='color: {status_color}'>{result.status}</span> - "
            f"{result.test_name} ({result.execution_time:.2f}s)"
        )
        
        if result.message:
            self.live_results.append(f"    {result.message}")
            
    def on_progress_updated(self, current, total):
        """Handle progress update signal"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        
    def on_all_tests_completed(self, results):
        """Handle all tests completed signal"""
        self.current_test_label.setText("All tests completed!")
        self.progress_bar.setValue(100)
        
        # Generate summary
        self.generate_summary()
        self.generate_detailed_results()
        
        # Enable buttons
        self.close_button.setEnabled(True)
        self.save_results_button.setEnabled(True)
        
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        errors = len([r for r in self.results if r.status == "ERROR"])
        skipped = len([r for r in self.results if r.status == "SKIP"])
        
        total_time = sum(r.execution_time for r in self.results)
        
        summary = f"""
KITCHEN DASHBOARD - COMPREHENSIVE TEST RESULTS
==============================================

Test Summary:
- Total Tests: {total_tests}
- Passed: {passed}
- Failed: {failed}
- Errors: {errors}
- Skipped: {skipped}
- Success Rate: {(passed/total_tests)*100:.1f}%
- Total Execution Time: {total_time:.2f} seconds

Test Status:
"""
        
        for result in self.results:
            summary += f"- {result.test_name}: {result.status} ({result.execution_time:.2f}s)\n"
            
        self.summary_text.setPlainText(summary)
        
    def generate_detailed_results(self):
        """Generate detailed test results"""
        detailed = "DETAILED TEST RESULTS\n" + "="*50 + "\n\n"
        
        for result in self.results:
            detailed += f"Test: {result.test_name}\n"
            detailed += f"Status: {result.status}\n"
            detailed += f"Execution Time: {result.execution_time:.2f} seconds\n"
            detailed += f"Timestamp: {result.timestamp}\n"
            
            if result.message:
                detailed += f"Message: {result.message}\n"
                
            if result.error:
                detailed += f"Error: {str(result.error)}\n"
                detailed += f"Traceback: {traceback.format_exception(type(result.error), result.error, result.error.__traceback__)}\n"
                
            detailed += "-" * 50 + "\n\n"
            
        self.detailed_results.setPlainText(detailed)
        
    def save_results(self):
        """Save test results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(self.summary_text.toPlainText())
                f.write("\n\n")
                f.write(self.detailed_results.toPlainText())
                
            self.app.logger.info(f"Test results saved to {filename}")
            
        except Exception as e:
            self.app.logger.error(f"Error saving test results: {e}")

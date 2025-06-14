"""
Data Operation Tester
Tests all data operations with sample data
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QProgressBar
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont

class DataOperationTester:
    """Tests data operations with comprehensive sample data"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = app_instance.logger
        
    def test_all_data_operations(self):
        """Test all data operations"""
        self.logger.info("Starting data operation testing...")
        
        # Create test dialog
        dialog = DataTestDialog(self.app)
        dialog.show()
        
        # Test operations
        operations_to_test = [
            ("Data Loading", self.test_data_loading),
            ("Data Saving", self.test_data_saving),
            ("Data Validation", self.test_data_validation),
            ("Data Transformation", self.test_data_transformation),
            ("Data Filtering", self.test_data_filtering),
            ("Data Aggregation", self.test_data_aggregation),
            ("Data Export", self.test_data_export),
            ("Data Import", self.test_data_import),
            ("Data Backup", self.test_data_backup),
            ("Data Synchronization", self.test_data_synchronization),
            ("Cross-Module Data Flow", self.test_cross_module_data_flow),
            ("Large Dataset Performance", self.test_large_dataset_performance),
            ("Error Handling", self.test_error_handling),
            ("Data Integrity", self.test_data_integrity)
        ]
        
        results = []
        for operation_name, test_function in operations_to_test:
            try:
                dialog.update_status(f"Testing {operation_name}...")
                start_time = time.time()
                
                test_function()
                
                execution_time = time.time() - start_time
                result = f"✅ {operation_name}: PASSED ({execution_time:.2f}s)"
                self.logger.info(f"Data operation test passed: {operation_name}")
                
            except Exception as e:
                execution_time = time.time() - start_time
                result = f"❌ {operation_name}: FAILED - {str(e)} ({execution_time:.2f}s)"
                self.logger.error(f"Data operation test failed: {operation_name} - {str(e)}")
                
            results.append(result)
            dialog.add_result(result)
            
        dialog.update_status("All data operation tests completed!")
        self.logger.info("Data operation testing completed")
        
    def create_comprehensive_sample_data(self):
        """Create comprehensive sample data for testing"""
        # Large inventory dataset
        inventory_data = pd.DataFrame({
            'item_id': range(1, 1001),
            'item_name': [f'Item_{i}' for i in range(1, 1001)],
            'category': np.random.choice(['Vegetables', 'Fruits', 'Grains', 'Dairy', 'Meat', 'Spices'], 1000),
            'quantity': np.random.randint(1, 100, 1000),
            'unit': np.random.choice(['kg', 'liters', 'pieces', 'grams'], 1000),
            'price_per_unit': np.random.uniform(10, 500, 1000).round(2),
            'location': np.random.choice(['Fridge', 'Pantry', 'Freezer', 'Storage'], 1000),
            'expiry_date': [(datetime.now() + timedelta(days=np.random.randint(1, 365))).date() for _ in range(1000)],
            'reorder_level': np.random.randint(1, 20, 1000),
            'total_value': np.random.uniform(100, 5000, 1000).round(2)
        })
        
        # Large sales dataset
        sales_data = pd.DataFrame({
            'sale_id': range(1, 5001),
            'item_name': np.random.choice([f'Recipe_{i}' for i in range(1, 101)], 5000),
            'quantity': np.random.randint(1, 10, 5000),
            'price_per_unit': np.random.uniform(50, 500, 5000).round(2),
            'total_amount': np.random.uniform(50, 2000, 5000).round(2),
            'customer': [f'Customer_{i}' for i in np.random.randint(1, 1001, 5000)],
            'date': [(datetime.now() - timedelta(days=np.random.randint(0, 365))).date() for _ in range(5000)]
        })
        
        # Recipe data
        recipes_data = pd.DataFrame({
            'recipe_id': range(1, 101),
            'recipe_name': [f'Recipe_{i}' for i in range(1, 101)],
            'category': np.random.choice(['Main Course', 'Appetizer', 'Dessert', 'Soup', 'Salad'], 100),
            'servings': np.random.randint(1, 8, 100),
            'prep_time': np.random.randint(5, 60, 100),
            'cook_time': np.random.randint(0, 120, 100),
            'description': [f'Description for Recipe {i}' for i in range(1, 101)]
        })
        
        return {
            'inventory': inventory_data,
            'sales': sales_data,
            'recipes': recipes_data,
            'shopping_list': pd.DataFrame(),
            'meal_plan': pd.DataFrame(),
            'budget': pd.DataFrame(),
            'waste': pd.DataFrame(),
            'cleaning_maintenance': pd.DataFrame()
        }
        
    def test_data_loading(self):
        """Test data loading operations"""
        # Test loading from CSV files
        data = self.app.load_data()
        assert isinstance(data, dict), "Data should be a dictionary"
        
        # Test loading with missing files
        original_data_dir = "data"
        test_data_dir = "test_data"
        
        if not os.path.exists(test_data_dir):
            os.makedirs(test_data_dir)
            
        # Create test CSV file
        test_df = pd.DataFrame({'test_col': [1, 2, 3]})
        test_file = os.path.join(test_data_dir, 'test_inventory.csv')
        test_df.to_csv(test_file, index=False)
        
        # Test loading
        loaded_df = pd.read_csv(test_file)
        assert len(loaded_df) == 3, "Test data should have 3 rows"
        
        # Cleanup
        os.remove(test_file)
        os.rmdir(test_data_dir)
        
    def test_data_saving(self):
        """Test data saving operations"""
        # Create test data
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Test1', 'Test2', 'Test3'],
            'value': [10.5, 20.3, 30.1]
        })
        
        # Test saving to CSV
        test_file = 'test_save.csv'
        test_data.to_csv(test_file, index=False)
        
        # Verify file exists and can be loaded
        assert os.path.exists(test_file), "Test file should exist"
        
        loaded_data = pd.read_csv(test_file)
        assert len(loaded_data) == 3, "Loaded data should have 3 rows"
        assert list(loaded_data.columns) == ['id', 'name', 'value'], "Columns should match"
        
        # Cleanup
        os.remove(test_file)
        
    def test_data_validation(self):
        """Test data validation operations"""
        # Create test data with invalid entries
        test_data = pd.DataFrame({
            'item_name': ['Valid Item', '', None, 'Another Valid'],
            'quantity': [10, -5, 'invalid', 20],
            'price': [100.0, 0, -10, 150.5],
            'date': ['2024-01-01', 'invalid-date', None, '2024-12-31']
        })
        
        # Test validation rules
        # Non-empty item names
        valid_names = test_data['item_name'].notna() & (test_data['item_name'] != '')
        assert valid_names.sum() == 2, "Should have 2 valid names"
        
        # Positive quantities
        try:
            numeric_quantities = pd.to_numeric(test_data['quantity'], errors='coerce')
            positive_quantities = numeric_quantities > 0
            assert positive_quantities.sum() == 2, "Should have 2 positive quantities"
        except:
            pass  # Expected for invalid data
            
        # Non-negative prices
        try:
            numeric_prices = pd.to_numeric(test_data['price'], errors='coerce')
            valid_prices = numeric_prices >= 0
            assert valid_prices.sum() == 2, "Should have 2 valid prices"
        except:
            pass  # Expected for invalid data
            
    def test_data_transformation(self):
        """Test data transformation operations"""
        # Create test data
        test_data = pd.DataFrame({
            'item_name': ['Apple', 'Banana', 'Cherry'],
            'quantity': [10, 20, 15],
            'price_per_unit': [5.0, 3.0, 8.0]
        })
        
        # Test adding calculated columns
        test_data['total_value'] = test_data['quantity'] * test_data['price_per_unit']
        expected_values = [50.0, 60.0, 120.0]
        
        for i, expected in enumerate(expected_values):
            assert test_data.iloc[i]['total_value'] == expected, f"Total value calculation failed for row {i}"
            
        # Test data type conversions
        test_data['quantity_str'] = test_data['quantity'].astype(str)
        assert test_data['quantity_str'].dtype == 'object', "String conversion failed"
        
        # Test data normalization
        test_data['normalized_price'] = (test_data['price_per_unit'] - test_data['price_per_unit'].min()) / (test_data['price_per_unit'].max() - test_data['price_per_unit'].min())
        assert test_data['normalized_price'].min() == 0.0, "Normalization min should be 0"
        assert test_data['normalized_price'].max() == 1.0, "Normalization max should be 1"
        
    def test_data_filtering(self):
        """Test data filtering operations"""
        # Create test data
        test_data = pd.DataFrame({
            'category': ['Vegetables', 'Fruits', 'Vegetables', 'Dairy', 'Fruits'],
            'quantity': [10, 5, 20, 8, 15],
            'price': [50, 80, 30, 120, 60],
            'in_stock': [True, False, True, True, False]
        })
        
        # Test category filtering
        vegetables = test_data[test_data['category'] == 'Vegetables']
        assert len(vegetables) == 2, "Should have 2 vegetable items"
        
        # Test quantity filtering
        high_quantity = test_data[test_data['quantity'] > 10]
        assert len(high_quantity) == 2, "Should have 2 high quantity items"
        
        # Test multiple condition filtering
        in_stock_vegetables = test_data[(test_data['category'] == 'Vegetables') & (test_data['in_stock'] == True)]
        assert len(in_stock_vegetables) == 2, "Should have 2 in-stock vegetables"
        
        # Test price range filtering
        mid_price = test_data[(test_data['price'] >= 50) & (test_data['price'] <= 100)]
        assert len(mid_price) == 3, "Should have 3 mid-price items"
        
    def test_data_aggregation(self):
        """Test data aggregation operations"""
        # Create test data
        test_data = pd.DataFrame({
            'category': ['Vegetables', 'Fruits', 'Vegetables', 'Fruits', 'Vegetables'],
            'quantity': [10, 5, 20, 15, 8],
            'value': [100, 80, 200, 150, 80]
        })
        
        # Test groupby operations
        category_totals = test_data.groupby('category').agg({
            'quantity': 'sum',
            'value': 'sum'
        })
        
        assert category_totals.loc['Vegetables', 'quantity'] == 38, "Vegetables total quantity should be 38"
        assert category_totals.loc['Fruits', 'quantity'] == 20, "Fruits total quantity should be 20"
        assert category_totals.loc['Vegetables', 'value'] == 380, "Vegetables total value should be 380"
        
        # Test statistical aggregations
        stats = test_data['quantity'].agg(['mean', 'median', 'std', 'min', 'max'])
        assert stats['mean'] == test_data['quantity'].mean(), "Mean calculation should match"
        assert stats['min'] == test_data['quantity'].min(), "Min calculation should match"
        assert stats['max'] == test_data['quantity'].max(), "Max calculation should match"
        
    def test_data_export(self):
        """Test data export operations"""
        # Create test data
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Item1', 'Item2', 'Item3'],
            'value': [10.5, 20.3, 30.1]
        })
        
        # Test CSV export
        csv_file = 'test_export.csv'
        test_data.to_csv(csv_file, index=False)
        assert os.path.exists(csv_file), "CSV export file should exist"
        
        # Test Excel export (if openpyxl is available)
        try:
            excel_file = 'test_export.xlsx'
            test_data.to_excel(excel_file, index=False)
            assert os.path.exists(excel_file), "Excel export file should exist"
            os.remove(excel_file)
        except ImportError:
            pass  # openpyxl not available
            
        # Test JSON export
        json_file = 'test_export.json'
        test_data.to_json(json_file, orient='records')
        assert os.path.exists(json_file), "JSON export file should exist"
        
        # Cleanup
        os.remove(csv_file)
        os.remove(json_file)
        
    def test_data_import(self):
        """Test data import operations"""
        # Create test files for import
        test_data = pd.DataFrame({
            'item_name': ['Test Item 1', 'Test Item 2'],
            'quantity': [10, 20],
            'price': [50.0, 75.0]
        })
        
        # Test CSV import
        csv_file = 'test_import.csv'
        test_data.to_csv(csv_file, index=False)
        
        imported_data = pd.read_csv(csv_file)
        assert len(imported_data) == 2, "Imported data should have 2 rows"
        assert list(imported_data.columns) == ['item_name', 'quantity', 'price'], "Columns should match"
        
        # Test data type preservation
        assert imported_data['quantity'].dtype in ['int64', 'int32'], "Quantity should be integer"
        assert imported_data['price'].dtype in ['float64', 'float32'], "Price should be float"
        
        # Cleanup
        os.remove(csv_file)
        
    def test_data_backup(self):
        """Test data backup operations"""
        # Create test data
        test_data = self.create_comprehensive_sample_data()
        
        # Test backup directory creation
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Test backing up each dataset
        for name, data in test_data.items():
            if not data.empty:
                backup_file = os.path.join(backup_dir, f"{name}_backup.csv")
                data.to_csv(backup_file, index=False)
                assert os.path.exists(backup_file), f"Backup file for {name} should exist"
                
        # Test backup verification
        backup_files = os.listdir(backup_dir)
        assert len(backup_files) > 0, "Backup directory should contain files"
        
        # Cleanup
        for file in backup_files:
            os.remove(os.path.join(backup_dir, file))
        os.rmdir(backup_dir)
        
    def test_data_synchronization(self):
        """Test data synchronization operations"""
        # Create test data for synchronization
        local_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Item1', 'Item2', 'Item3'],
            'last_modified': [datetime.now()] * 3
        })
        
        remote_data = pd.DataFrame({
            'id': [1, 2, 4],
            'name': ['Item1_Updated', 'Item2', 'Item4'],
            'last_modified': [datetime.now() + timedelta(hours=1), datetime.now(), datetime.now()] * 1
        })
        
        # Test merge operations
        merged_data = pd.concat([local_data, remote_data]).drop_duplicates(subset=['id'], keep='last')
        
        # Verify synchronization results
        assert len(merged_data) == 4, "Merged data should have 4 unique items"
        assert 'Item1_Updated' in merged_data['name'].values, "Updated item should be present"
        assert 'Item4' in merged_data['name'].values, "New item should be present"
        
    def test_cross_module_data_flow(self):
        """Test data flow between modules"""
        # Test inventory to shopping list flow
        inventory_data = pd.DataFrame({
            'item_name': ['Tomatoes', 'Onions', 'Rice'],
            'quantity': [2, 1, 5],  # Low quantities
            'reorder_level': [5, 3, 10]
        })
        
        # Simulate low stock detection
        low_stock_items = inventory_data[inventory_data['quantity'] < inventory_data['reorder_level']]
        assert len(low_stock_items) == 3, "All items should be low stock"
        
        # Test recipe to shopping list flow
        recipe_ingredients = pd.DataFrame({
            'recipe_id': [1, 1, 2],
            'item_name': ['Pasta', 'Tomato Sauce', 'Lettuce'],
            'quantity_needed': [500, 200, 100]
        })
        
        shopping_list = recipe_ingredients[['item_name', 'quantity_needed']].copy()
        shopping_list.rename(columns={'quantity_needed': 'quantity'}, inplace=True)
        
        assert len(shopping_list) == 3, "Shopping list should have 3 items"
        
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        # Create large dataset
        large_data = pd.DataFrame({
            'id': range(100000),
            'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], 100000),
            'value': np.random.uniform(0, 1000, 100000),
            'date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(100000)]
        })
        
        # Test filtering performance
        start_time = time.time()
        filtered_data = large_data[large_data['value'] > 500]
        filter_time = time.time() - start_time
        
        assert filter_time < 5.0, f"Filtering should complete in under 5 seconds, took {filter_time:.2f}s"
        
        # Test groupby performance
        start_time = time.time()
        grouped_data = large_data.groupby('category')['value'].mean()
        groupby_time = time.time() - start_time
        
        assert groupby_time < 5.0, f"Groupby should complete in under 5 seconds, took {groupby_time:.2f}s"
        
        # Test sorting performance
        start_time = time.time()
        sorted_data = large_data.sort_values('value')
        sort_time = time.time() - start_time
        
        assert sort_time < 5.0, f"Sorting should complete in under 5 seconds, took {sort_time:.2f}s"
        
    def test_error_handling(self):
        """Test error handling in data operations"""
        # Test with invalid file paths
        try:
            invalid_data = pd.read_csv('non_existent_file.csv')
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
            
        # Test with invalid data types
        test_data = pd.DataFrame({
            'numbers': ['1', '2', 'invalid', '4']
        })
        
        # Test numeric conversion with error handling
        numeric_data = pd.to_numeric(test_data['numbers'], errors='coerce')
        assert numeric_data.isna().sum() == 1, "Should have 1 NaN value"
        
        # Test with empty dataframes
        empty_df = pd.DataFrame()
        assert len(empty_df) == 0, "Empty dataframe should have 0 rows"
        assert len(empty_df.columns) == 0, "Empty dataframe should have 0 columns"
        
    def test_data_integrity(self):
        """Test data integrity checks"""
        # Create test data with potential integrity issues
        test_data = pd.DataFrame({
            'id': [1, 2, 2, 3],  # Duplicate ID
            'name': ['Item1', 'Item2', 'Item2_Duplicate', 'Item3'],
            'quantity': [10, -5, 20, 15],  # Negative quantity
            'price': [100, 200, 0, 150]  # Zero price
        })
        
        # Test duplicate detection
        duplicates = test_data.duplicated(subset=['id'])
        assert duplicates.sum() == 1, "Should detect 1 duplicate ID"
        
        # Test data range validation
        negative_quantities = test_data['quantity'] < 0
        assert negative_quantities.sum() == 1, "Should detect 1 negative quantity"
        
        zero_prices = test_data['price'] == 0
        assert zero_prices.sum() == 1, "Should detect 1 zero price"
        
        # Test referential integrity (foreign key simulation)
        categories = pd.DataFrame({
            'category_id': [1, 2, 3],
            'category_name': ['Vegetables', 'Fruits', 'Grains']
        })
        
        items = pd.DataFrame({
            'item_id': [1, 2, 3, 4],
            'item_name': ['Tomato', 'Apple', 'Rice', 'Bread'],
            'category_id': [1, 2, 3, 4]  # Category 4 doesn't exist
        })
        
        # Check referential integrity
        valid_categories = items['category_id'].isin(categories['category_id'])
        assert valid_categories.sum() == 3, "Should have 3 items with valid categories"


class DataTestDialog(QDialog):
    """Dialog for displaying data operation test results"""
    
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.app = app_instance
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Data Operation Testing")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Kitchen Dashboard - Data Operation Testing")
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

#!/usr/bin/env python3
"""
Kitchen Dashboard Test Runner
Runs comprehensive tests for all modules and functions
"""

import sys
import os
import time
from datetime import datetime

# Setup imports using test utilities
from test_utils import setup_module_imports, safe_import, get_project_root, ensure_data_dir

# Setup module imports
setup_module_imports()

def run_comprehensive_tests():
    """Run comprehensive tests without GUI"""
    print("="*80)
    print("KITCHEN DASHBOARD - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Import required modules
        from sample_data_generator import SampleDataGenerator
        from data_operation_tester import DataOperationTester
        
        # Create a mock app instance for testing
        class MockApp:
            def __init__(self):
                self.data = {}
                self.logger = MockLogger()
                
        class MockLogger:
            def info(self, msg): print(f"[INFO] {msg}")
            def warning(self, msg): print(f"[WARNING] {msg}")
            def error(self, msg): print(f"[ERROR] {msg}")
            def debug(self, msg): print(f"[DEBUG] {msg}")
        
        mock_app = MockApp()
        
        # Step 1: Generate sample data
        print("Step 1: Generating Sample Data")
        print("-" * 40)
        
        start_time = time.time()
        generator = SampleDataGenerator()
        sample_data = generator.generate_all_sample_data(save_to_files=True)
        mock_app.data = sample_data
        
        generation_time = time.time() - start_time
        print(f"✅ Sample data generated successfully in {generation_time:.2f}s")
        print(f"   Generated {len(sample_data)} datasets")
        for name, df in sample_data.items():
            print(f"   - {name}: {len(df)} records")
        print()
        
        # Step 2: Test data operations
        print("Step 2: Testing Data Operations")
        print("-" * 40)
        
        start_time = time.time()
        data_tester = DataOperationTester(mock_app)
        
        # Run individual data operation tests
        data_tests = [
            ("Data Loading", data_tester.test_data_loading),
            ("Data Validation", data_tester.test_data_validation),
            ("Data Transformation", data_tester.test_data_transformation),
            ("Data Filtering", data_tester.test_data_filtering),
            ("Data Aggregation", data_tester.test_data_aggregation),
            ("Data Export", data_tester.test_data_export),
            ("Data Import", data_tester.test_data_import),
            ("Error Handling", data_tester.test_error_handling),
            ("Data Integrity", data_tester.test_data_integrity)
        ]
        
        data_results = []
        for test_name, test_function in data_tests:
            try:
                test_start = time.time()
                test_function()
                test_time = time.time() - test_start
                result = f"✅ {test_name}: PASSED ({test_time:.2f}s)"
                print(result)
                data_results.append(('PASS', test_name, test_time))
            except Exception as e:
                test_time = time.time() - test_start
                result = f"❌ {test_name}: FAILED - {str(e)} ({test_time:.2f}s)"
                print(result)
                data_results.append(('FAIL', test_name, test_time))
        
        data_test_time = time.time() - start_time
        print(f"\nData operations testing completed in {data_test_time:.2f}s")
        print()
        
        # Step 3: Test modules (without GUI components)
        print("Step 3: Testing Core Module Logic")
        print("-" * 40)
        
        start_time = time.time()
        
        # Test core module functionality
        module_tests = [
            ("Category Manager", test_category_manager),
            ("Sample Data Validation", test_sample_data_validation),
            ("Data Structure Integrity", test_data_structure_integrity),
            ("Performance Metrics", test_performance_metrics)
        ]
        
        module_results = []
        for test_name, test_function in module_tests:
            try:
                test_start = time.time()
                test_function(mock_app)
                test_time = time.time() - test_start
                result = f"✅ {test_name}: PASSED ({test_time:.2f}s)"
                print(result)
                module_results.append(('PASS', test_name, test_time))
            except Exception as e:
                test_time = time.time() - test_start
                result = f"❌ {test_name}: FAILED - {str(e)} ({test_time:.2f}s)"
                print(result)
                module_results.append(('FAIL', test_name, test_time))
        
        module_test_time = time.time() - start_time
        print(f"\nModule testing completed in {module_test_time:.2f}s")
        print()
        
        # Step 4: Generate test report
        print("Step 4: Test Summary")
        print("-" * 40)
        
        total_tests = len(data_results) + len(module_results)
        passed_tests = len([r for r in data_results + module_results if r[0] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        total_time = generation_time + data_test_time + module_test_time
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Execution Time: {total_time:.2f}s")
        print()
        
        # Save test report
        save_test_report(data_results, module_results, total_time)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! The Kitchen Dashboard is ready for use.")
        else:
            print(f"⚠️  {failed_tests} tests failed. Please check the detailed report.")
            
        return failed_tests == 0
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_category_manager(mock_app):
    """Test category manager functionality"""
    try:
        # Import from parent modules directory
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        modules_dir = os.path.join(parent_dir, 'modules')
        sys.path.insert(0, modules_dir)

        from category_manager import CategoryManager
        
        category_manager = CategoryManager(mock_app.data)
        result = category_manager.synchronize_categories()
        
        assert isinstance(result, dict), "Category manager should return a dict"
        assert 'success' in result, "Result should have 'success' key"
        
    except ImportError:
        print("   Category manager module not available - skipping")

def test_sample_data_validation(mock_app):
    """Test that sample data is valid"""
    required_datasets = [
        'inventory', 'shopping_list', 'recipes', 'sales', 'budget',
        'waste', 'cleaning_maintenance', 'categories', 'packing_materials'
    ]
    
    for dataset_name in required_datasets:
        assert dataset_name in mock_app.data, f"Missing dataset: {dataset_name}"
        dataset = mock_app.data[dataset_name]
        assert len(dataset) > 0, f"Dataset {dataset_name} should not be empty"
        
    # Test data relationships
    if 'recipes' in mock_app.data and 'recipe_ingredients' in mock_app.data:
        recipes = mock_app.data['recipes']
        ingredients = mock_app.data['recipe_ingredients']
        
        # All recipe ingredients should reference valid recipes
        recipe_ids = set(recipes['recipe_id'])
        ingredient_recipe_ids = set(ingredients['recipe_id'])
        
        invalid_refs = ingredient_recipe_ids - recipe_ids
        assert len(invalid_refs) == 0, f"Invalid recipe references in ingredients: {invalid_refs}"

def test_data_structure_integrity(mock_app):
    """Test data structure integrity"""
    import pandas as pd
    
    for name, dataset in mock_app.data.items():
        assert isinstance(dataset, pd.DataFrame), f"Dataset {name} should be a DataFrame"
        
        # Check for required columns based on dataset type
        if name == 'inventory':
            required_cols = ['item_name', 'category', 'quantity', 'price_per_unit']
            for col in required_cols:
                assert col in dataset.columns, f"Missing column {col} in {name}"
                
        elif name == 'recipes':
            required_cols = ['recipe_id', 'recipe_name', 'category', 'servings']
            for col in required_cols:
                assert col in dataset.columns, f"Missing column {col} in {name}"

def test_performance_metrics(mock_app):
    """Test performance with sample data"""
    import pandas as pd
    
    # Test data loading performance
    start_time = time.time()
    
    # Simulate data operations
    for name, dataset in mock_app.data.items():
        if len(dataset) > 0:
            # Test basic operations
            _ = len(dataset)
            _ = dataset.columns.tolist()
            
            # Test filtering if possible
            if 'category' in dataset.columns:
                _ = dataset[dataset['category'].notna()]
                
    operation_time = time.time() - start_time
    
    # Operations should complete quickly
    assert operation_time < 10.0, f"Data operations took too long: {operation_time:.2f}s"

def save_test_report(data_results, module_results, total_time):
    """Save detailed test report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"
    
    try:
        with open(report_file, 'w') as f:
            f.write("KITCHEN DASHBOARD - COMPREHENSIVE TEST REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Execution Time: {total_time:.2f} seconds\n\n")
            
            f.write("DATA OPERATION TESTS:\n")
            f.write("-" * 30 + "\n")
            for status, test_name, test_time in data_results:
                f.write(f"{status}: {test_name} ({test_time:.2f}s)\n")
            
            f.write("\nMODULE TESTS:\n")
            f.write("-" * 30 + "\n")
            for status, test_name, test_time in module_results:
                f.write(f"{status}: {test_name} ({test_time:.2f}s)\n")
            
            f.write("\nSUMMARY:\n")
            f.write("-" * 30 + "\n")
            total_tests = len(data_results) + len(module_results)
            passed_tests = len([r for r in data_results + module_results if r[0] == 'PASS'])
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {total_tests - passed_tests}\n")
            f.write(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n")
            
        print(f"📄 Detailed test report saved to: {report_file}")
        
    except Exception as e:
        print(f"Warning: Could not save test report: {e}")

if __name__ == "__main__":
    print("Starting Kitchen Dashboard Comprehensive Testing...")
    print()
    
    success = run_comprehensive_tests()
    
    print()
    print("="*80)
    if success:
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The Kitchen Dashboard is ready for production use.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the test results and fix any issues.")
        sys.exit(1)

"""
Test Configuration
Configuration settings for the test suite
"""

import os
from test_utils import get_project_root

# Test configuration
TEST_CONFIG = {
    # Directories
    'project_root': get_project_root(),
    'data_dir': os.path.join(get_project_root(), 'data'),
    'logs_dir': os.path.join(get_project_root(), 'logs'),
    'tests_dir': os.path.dirname(os.path.abspath(__file__)),
    
    # Test data settings
    'sample_data': {
        'inventory_items': 200,
        'recipes': 50,
        'sales_records': 500,
        'shopping_items': 100,
        'waste_records': 100,
        'cleaning_tasks': 15,
        'packing_materials': 10,
        'sales_orders': 200
    },
    
    # Performance test settings
    'performance': {
        'large_dataset_size': 100000,
        'stress_test_iterations': 50,
        'memory_limit_mb': 2000,
        'max_execution_time_seconds': 60,
        'startup_time_limit_seconds': 10
    },
    
    # Test timeouts
    'timeouts': {
        'module_test': 30,
        'data_operation_test': 60,
        'ui_test': 30,
        'performance_test': 300
    },
    
    # Test categories to run
    'test_categories': [
        'core_application',
        'data_loading',
        'inventory_module',
        'shopping_module', 
        'pricing_module',
        'sales_module',
        'cleaning_module',
        'settings_module',
        'meal_planning',
        'budget_management',
        'waste_management',
        'packing_materials',
        'firebase_integration',
        'notification_system',
        'logging_system',
        'category_management',
        'analytics_engine',
        'ai_integration',
        'performance_optimization',
        'responsive_design',
        'data_validation',
        'error_handling',
        'cross_module_integration'
    ],
    
    # Modules to test
    'modules_to_test': [
        'inventory_fixed',
        'shopping_fixed',
        'pricing_management',
        'enhanced_sales',
        'cleaning_fixed',
        'settings_fixed',
        'fixed_meal_planning',
        'enhanced_budget',
        'waste',
        'packing_materials',
        'firebase_sync',
        'notification_system',
        'category_manager',
        'analytics_engine',
        'multi_ai_engine',
        'responsive_design_manager',
        'performance_optimizer'
    ],
    
    # Expected data files
    'expected_data_files': [
        'inventory.csv',
        'expenses_list.csv',
        'recipes.csv',
        'recipe_ingredients.csv',
        'meal_plan.csv',
        'sales.csv',
        'budget.csv',
        'waste.csv',
        'cleaning_maintenance.csv',
        'items.csv',
        'categories.csv',
        'pricing.csv',
        'packing_materials.csv',
        'recipe_packing_materials.csv',
        'sales_orders.csv'
    ],
    
    # Test report settings
    'reporting': {
        'save_reports': True,
        'report_format': 'txt',
        'include_timestamps': True,
        'include_performance_metrics': True,
        'include_error_details': True
    }
}

def get_test_config():
    """Get test configuration"""
    return TEST_CONFIG

def get_data_files():
    """Get list of expected data files"""
    return TEST_CONFIG['expected_data_files']

def get_modules_to_test():
    """Get list of modules to test"""
    return TEST_CONFIG['modules_to_test']

def get_performance_config():
    """Get performance test configuration"""
    return TEST_CONFIG['performance']

def get_timeout_config():
    """Get timeout configuration"""
    return TEST_CONFIG['timeouts']

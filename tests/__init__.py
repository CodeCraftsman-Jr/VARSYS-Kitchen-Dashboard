"""
Kitchen Dashboard Test Suite
Comprehensive testing framework for all modules and functions
"""

__version__ = "1.0.0"
__author__ = "Kitchen Dashboard Team"

# Import all test modules for easy access
from .comprehensive_test_suite import ComprehensiveTestSuite, TestRunner, TestDialog
from .module_tester import ModuleTester, ModuleTestDialog
from .data_operation_tester import DataOperationTester, DataTestDialog
from .ui_component_tester import UIComponentTester, UITestDialog
from .performance_tester import PerformanceTester, PerformanceTestDialog, PerformanceMonitor
from .sample_data_generator import SampleDataGenerator, generate_sample_data

__all__ = [
    'ComprehensiveTestSuite',
    'TestRunner', 
    'TestDialog',
    'ModuleTester',
    'ModuleTestDialog',
    'DataOperationTester',
    'DataTestDialog', 
    'UIComponentTester',
    'UITestDialog',
    'PerformanceTester',
    'PerformanceTestDialog',
    'PerformanceMonitor',
    'SampleDataGenerator',
    'generate_sample_data'
]

# 🧪 Kitchen Dashboard Test Suite

This directory contains the comprehensive testing framework for the Kitchen Dashboard application.

## 📁 Directory Structure

```
tests/
├── __init__.py                    # Package initialization
├── README.md                      # This file
├── TESTING_GUIDE.md              # Comprehensive testing guide
├── run_tests.py                   # Main test runner
├── test_config.py                 # Test configuration
├── test_utils.py                  # Test utilities
├── exe_compatibility_test.py      # EXE compilation testing
├── comprehensive_test_suite.py    # Complete test suite
├── module_tester.py              # Individual module testing
├── data_operation_tester.py      # Data operation testing
├── ui_component_tester.py        # UI component testing
├── performance_tester.py         # Performance testing
└── sample_data_generator.py      # Sample data generation
```

## 🚀 Quick Start

### From Root Directory
```bash
# Run all tests
python run_tests.py

# Or run from tests directory
cd tests
python run_tests.py
```

### From GUI Application
1. Start the application: `python kitchen_app.py`
2. Use the **Testing** menu:
   - `Generate Sample Data` - Create test data
   - `Run Comprehensive Tests` - Run all tests
   - `Test All Modules` - Test individual modules
   - `Test Data Operations` - Test data handling
   - `Test UI Components` - Test interface
   - `Test Performance` - Performance testing

## 🧪 Test Categories

### 1. **Core Application Tests**
- Main window initialization
- Navigation functionality
- Data structure integrity
- Logger functionality

### 2. **Module Tests** (17+ modules)
- Inventory management
- Shopping list management
- Recipe pricing and costing
- Sales tracking
- Cleaning and maintenance
- Settings and configuration
- Meal planning
- Budget management
- Waste tracking
- Packing materials
- Firebase integration
- Notifications
- Category management
- Analytics engine
- AI integration
- Responsive design
- Performance optimization

### 3. **Data Operation Tests**
- Data loading and saving
- Data validation and sanitization
- Data transformation and calculations
- Filtering and search operations
- Aggregation and statistics
- Import/export functionality
- Backup and restore
- Error handling
- Data integrity checks
- Large dataset performance

### 4. **UI Component Tests**
- Tables and data grids
- Forms and input controls
- Buttons and interactions
- Dialogs and modals
- Menus and navigation
- Charts and visualizations
- Responsive design
- Keyboard navigation
- Mouse interactions
- Accessibility features

### 5. **Performance Tests**
- Application startup time
- Memory usage monitoring
- CPU usage optimization
- Large dataset handling
- UI responsiveness
- File I/O performance
- Database operations
- Concurrent operations
- Memory leak detection
- Stress testing

## 📊 Sample Data Generated

The test suite generates comprehensive sample data:

- **📦 Inventory:** 200+ items across 16 categories
- **🍽️ Recipes:** 50 recipes with 264 ingredients
- **🛒 Shopping:** 100 shopping list items
- **💰 Sales:** 500 sales transactions
- **📊 Budget:** 16 category budgets
- **🗑️ Waste:** 100 waste tracking records
- **🧹 Cleaning:** 15 maintenance tasks
- **📦 Packing:** 10 packing materials + usage data
- **📅 Meal Plans:** 19 planned meals
- **📈 Sales Orders:** 200 detailed orders

## 🔧 Configuration

### Test Configuration (`test_config.py`)
```python
TEST_CONFIG = {
    'sample_data': {
        'inventory_items': 200,
        'recipes': 50,
        'sales_records': 500,
        # ... more settings
    },
    'performance': {
        'large_dataset_size': 100000,
        'memory_limit_mb': 2000,
        'max_execution_time_seconds': 60
    },
    'timeouts': {
        'module_test': 30,
        'data_operation_test': 60,
        'performance_test': 300
    }
}
```

## 🏗️ EXE Compilation Support

### Testing EXE Compatibility
```bash
cd tests
python exe_compatibility_test.py
```

### Building EXE with Tests Included
1. Run EXE compatibility test
2. Use generated `kitchen_dashboard.spec` file
3. Build with PyInstaller:
   ```bash
   pyinstaller kitchen_dashboard.spec
   ```

The EXE will include all test modules and can run tests internally.

## 📈 Test Results

### Console Output
```
KITCHEN DASHBOARD - COMPREHENSIVE TEST RESULTS
==============================================

Test Summary:
- Total Tests: 24
- Passed: 22
- Failed: 2
- Success Rate: 91.7%
- Total Execution Time: 45.23 seconds
```

### Detailed Reports
- Timestamped test reports saved automatically
- Performance metrics included
- Error details and stack traces
- Execution time for each test

## 🛠️ Utilities

### Test Utils (`test_utils.py`)
- `setup_module_imports()` - Configure import paths
- `safe_import()` - Safely import modules
- `get_project_root()` - Get project directory
- `ensure_data_dir()` - Create data directory

### Sample Data Generator
```python
from sample_data_generator import generate_sample_data

# Generate all sample data
data = generate_sample_data()

# Or use the class directly
generator = SampleDataGenerator()
data = generator.generate_all_sample_data()
```

## 🔍 Individual Test Modules

### Module Tester
```python
from module_tester import ModuleTester

tester = ModuleTester(app_instance)
tester.test_all_modules()
```

### Data Operation Tester
```python
from data_operation_tester import DataOperationTester

tester = DataOperationTester(app_instance)
tester.test_all_data_operations()
```

### Performance Tester
```python
from performance_tester import PerformanceTester

tester = PerformanceTester(app_instance)
tester.test_performance()
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from correct directory
   - Check Python path configuration
   - Verify all dependencies installed

2. **Permission Errors**
   - Ensure write permissions for data directory
   - Run as administrator if needed

3. **Memory Issues**
   - Reduce test dataset sizes in config
   - Close other applications
   - Check available RAM

4. **GUI Test Failures**
   - Ensure display is available
   - Check Qt installation
   - Verify PySide6 compatibility

### Debug Mode
Set environment variable for detailed logging:
```bash
export KITCHEN_DASHBOARD_DEBUG=1
python run_tests.py
```

## 📝 Adding New Tests

### 1. Create Test Function
```python
def test_new_feature(self):
    """Test new feature functionality"""
    # Setup test data
    test_data = create_test_data()
    
    # Execute test
    result = feature_function(test_data)
    
    # Verify results
    assert result is not None, "Feature should return result"
    assert len(result) > 0, "Result should not be empty"
```

### 2. Add to Test Suite
Add your test to the appropriate tester class and update the test list.

### 3. Update Configuration
Add any new settings to `test_config.py`.

## 📊 Continuous Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py
```

## 📞 Support

For issues with the test suite:
1. Check the logs in `logs/` directory
2. Review test reports for detailed error information
3. Ensure all dependencies are installed
4. Verify system requirements are met

The test suite is designed to be comprehensive, reliable, and easy to use both during development and in production environments.

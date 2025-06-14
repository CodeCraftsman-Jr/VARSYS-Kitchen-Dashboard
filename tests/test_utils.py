"""
Test Utilities
Helper functions for testing framework
"""

import sys
import os

def setup_module_imports():
    """Setup imports for modules from parent directory"""
    # Get parent directory (project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Add parent directory to path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Add modules directory to path
    modules_dir = os.path.join(parent_dir, 'modules')
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    
    # Add utils directory to path
    utils_dir = os.path.join(parent_dir, 'utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    
    return parent_dir, modules_dir, utils_dir

def safe_import(module_name, class_name=None):
    """Safely import a module or class"""
    try:
        setup_module_imports()
        
        if class_name:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}.{class_name if class_name else ''}: {e}")
        return None

def get_project_root():
    """Get the project root directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def get_data_dir():
    """Get the data directory path"""
    return os.path.join(get_project_root(), 'data')

def ensure_data_dir():
    """Ensure data directory exists"""
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

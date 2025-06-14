#!/usr/bin/env python3
"""
Kitchen Dashboard Test Runner (Main Entry Point)
Runs comprehensive tests for all modules and functions from root directory
"""

import sys
import os
import subprocess
from datetime import datetime

def main():
    """Main test runner entry point"""
    print("="*80)
    print("KITCHEN DASHBOARD - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get the current directory (should be root of project)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(current_dir, 'tests')
    
    # Check if tests directory exists
    if not os.path.exists(tests_dir):
        print("❌ Tests directory not found!")
        print(f"Expected location: {tests_dir}")
        return False
    
    # Check if test runner exists
    test_runner_path = os.path.join(tests_dir, 'run_tests.py')
    if not os.path.exists(test_runner_path):
        print("❌ Test runner not found!")
        print(f"Expected location: {test_runner_path}")
        return False
    
    print(f"📁 Tests directory: {tests_dir}")
    print(f"🚀 Running tests from: {test_runner_path}")
    print()
    
    try:
        # Change to tests directory and run tests
        original_cwd = os.getcwd()
        os.chdir(tests_dir)
        
        # Run the test runner
        result = subprocess.run([sys.executable, 'run_tests.py'], 
                              capture_output=False, 
                              text=True)
        
        # Return to original directory
        os.chdir(original_cwd)
        
        # Return success/failure based on exit code
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    print("Kitchen Dashboard - Test Suite Launcher")
    print("This will run all comprehensive tests...")
    print()
    
    success = main()
    
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

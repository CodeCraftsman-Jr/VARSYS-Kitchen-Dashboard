#!/bin/bash

echo "Kitchen Dashboard - Test Suite Runner"
echo "====================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"
echo "Running comprehensive tests..."
echo

# Run the test suite
$PYTHON_CMD run_tests.py

echo
echo "Test execution completed!"
echo "Check the test reports for detailed results."
echo

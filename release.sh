#!/bin/bash
# VARSYS Kitchen Dashboard - Main Release Launcher
# Launches the release tools from the release_tools folder

# Check if release_tools directory exists
if [ ! -d "release_tools" ]; then
    echo "❌ Error: release_tools directory not found"
    echo "Please make sure the release tools are properly installed."
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    echo "Please install Python 3.x and try again"
    exit 1
fi

# Run the Python launcher
python release.py "$@"

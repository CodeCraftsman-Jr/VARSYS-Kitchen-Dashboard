#!/bin/bash

echo "========================================"
echo "   WhatsApp Messenger - Standalone"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later"
    exit 1
fi

echo "Python found. Starting WhatsApp Messenger..."
echo

# Start the GUI version by default
echo "Starting GUI version..."
echo "Press Ctrl+C to stop the messenger"
echo

python3 whatsapp_messenger_gui.py

echo
echo "WhatsApp Messenger stopped."

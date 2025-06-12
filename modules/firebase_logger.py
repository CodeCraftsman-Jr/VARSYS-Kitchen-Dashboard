"""
Firebase Logger Module for Kitchen Dashboard Application.
This module provides logging functionality for Firebase operations.
"""

import os
import logging
import traceback
from datetime import datetime

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create log file with timestamp
log_file = os.path.join(log_dir, f'firebase_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('firebase')

def log_info(message):
    """Log an info message"""
    logger.info(message)
    print(f"INFO: {message}")

def log_warning(message):
    """Log a warning message"""
    logger.warning(message)
    print(f"WARNING: {message}")

def log_error(message, exception=None):
    """Log an error message with optional exception details"""
    logger.error(message)
    print(f"ERROR: {message}")
    
    if exception:
        logger.error(f"Exception details: {str(exception)}")
        logger.error(traceback.format_exc())
        print(f"Exception details: {str(exception)}")

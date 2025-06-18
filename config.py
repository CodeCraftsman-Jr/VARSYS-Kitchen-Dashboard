"""
Configuration settings for the Kitchen Dashboard application.
This file centralizes all configuration options for easier management.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(BASE_DIR, "data_backup")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# File paths
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
EXPENSES_LIST_FILE = os.path.join(DATA_DIR, "expenses_list.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
RECIPES_FILE = os.path.join(DATA_DIR, "recipes.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Default settings
DEFAULT_CURRENCY = "₹"
AVAILABLE_CURRENCIES = ["₹", "$", "€", "£", "¥"]
DEFAULT_DATE_FORMAT = "%d-%m-%Y"

# Firebase configuration (retrieved from environment variables)
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")
FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID", "")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOGS_DIR, "kitchen_dashboard.log")

# Application settings
APP_NAME = "Kitchen Dashboard"
APP_VERSION = "1.2.0"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")

# UI settings
THEME = os.getenv("THEME", "light")  # "light" or "dark"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

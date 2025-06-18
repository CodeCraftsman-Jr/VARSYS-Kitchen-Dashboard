import sys
import os

# Fix Python paths for frozen application (cx_Freeze)
if getattr(sys, 'frozen', False):
    # Running in a frozen application
    current_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'modules'))
    sys.path.insert(0, os.path.join(current_dir, 'utils'))
    sys.path.insert(0, os.path.join(current_dir, 'tests'))
    print("Fixed Python paths for frozen application")
else:
    # Running in development
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'modules'))
    sys.path.insert(0, os.path.join(current_dir, 'utils'))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Firebase integration with error handling
try:
    import firebase_integration
    FIREBASE_AVAILABLE = True
except ImportError:
    try:
        from modules import firebase_integration
        FIREBASE_AVAILABLE = True
    except ImportError:
        FIREBASE_AVAILABLE = False

# Set matplotlib to use PySide6
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLabel,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
                             QFrame, QScrollArea, QMessageBox, QSplitter,
                             QGroupBox, QFormLayout, QStyleFactory, QSizePolicy,
                             QRadioButton, QDialog, QCheckBox, QButtonGroup)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QPalette, QPainter, QPen, QPixmap

# Import modules with fallback handling for frozen application
def safe_import(module_name, fallback=None):
    """Safely import modules with fallback for frozen applications"""
    try:
        # Try direct import first (for frozen app)
        return __import__(module_name)
    except ImportError:
        try:
            # Try with modules prefix
            return __import__(f'modules.{module_name}', fromlist=[module_name])
        except ImportError:
            if fallback:
                return fallback
            return None

# Import modules with safe fallback
try:
    from settings_fixed import SettingsWidget
except ImportError:
    try:
        from modules.settings_fixed import SettingsWidget
    except ImportError:
        SettingsWidget = None

try:
    from shopping_fixed import ShoppingWidget
except ImportError:
    try:
        from modules.shopping_fixed import ShoppingWidget
    except ImportError:
        ShoppingWidget = None

try:
    from logs_viewer import LogsViewerWidget
except ImportError:
    try:
        from modules.logs_viewer import LogsViewerWidget
    except ImportError:
        LogsViewerWidget = None

try:
    from firebase_sync import FirebaseSync
except ImportError:
    try:
        from modules.firebase_sync import FirebaseSync
    except ImportError:
        FirebaseSync = None

try:
    from login_dialog import LoginDialog
except ImportError:
    try:
        from modules.login_dialog import LoginDialog
    except ImportError:
        LoginDialog = None

# Import logger with fallback
try:
    from app_logger import get_logger
except ImportError:
    try:
        from utils.app_logger import get_logger
    except ImportError:
        # Fallback logger
        import logging
        def get_logger():
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger(__name__)

# Import notification system with fallback
try:
    from notification_system import get_notification_manager
except ImportError:
    try:
        from modules.notification_system import get_notification_manager
    except ImportError:
        def get_notification_manager(parent):
            return None

# Import modern theme with fallback
try:
    from modern_theme import ModernTheme
except ImportError:
    try:
        from modules.modern_theme import ModernTheme
    except ImportError:
        class ModernTheme:
            @staticmethod
            def apply_theme(app):
                pass

# Import activity tracker with fallback
try:
    from activity_tracker import get_activity_tracker, track_user_action, track_navigation, track_system_event
except ImportError:
    try:
        from modules.activity_tracker import get_activity_tracker, track_user_action, track_navigation, track_system_event
    except ImportError:
        get_activity_tracker = None
        def track_user_action(*args, **kwargs): pass
        def track_navigation(*args, **kwargs): pass
        def track_system_event(*args, **kwargs): pass

# Import update system with fallback
try:
    from update_manager import UpdateManager
    from updater import get_updater
    from version import version_manager
    UPDATE_SYSTEM_AVAILABLE = True
except ImportError:
    UPDATE_SYSTEM_AVAILABLE = False
    UpdateManager = None
    get_updater = None
    version_manager = None

print("All imports completed with fallback handling for frozen application")

# Continue with the rest of the original kitchen_app.py code...
# (The class definition and methods would continue here)

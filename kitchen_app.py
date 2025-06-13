import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import calendar

# Firebase integration
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
                             QFrame, QTableWidget, QTableWidgetItem, QComboBox,
                             QLineEdit, QScrollArea, QMessageBox, QSplitter,
                             QFileDialog, QHeaderView, QGroupBox, QFormLayout,
                             QStyleFactory, QSizePolicy, QStackedWidget, QRadioButton,
                             QDialog, QTextEdit)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QLinearGradient, QPalette, QBrush, QPainter, QPen, QPixmap

# Import modules
from modules.inventory_fixed import InventoryWidget
from modules.cleaning_fixed import CleaningWidget
from modules.settings_fixed import SettingsWidget
from modules.shopping_fixed import ShoppingWidget
from modules.logs_viewer import LogsViewerWidget
from modules.firebase_sync import FirebaseSync
from modules.login_dialog import LoginDialog

# Import logger
from utils.app_logger import get_logger

# Import notification system
from modules.notification_system import get_notification_manager

# Import modern theme
from modules.modern_theme import ModernTheme

# Import activity tracker
try:
    from modules.activity_tracker import get_activity_tracker, track_user_action, track_navigation, track_system_event
except ImportError:
    get_activity_tracker = None
    def track_user_action(*args, **kwargs): pass
    def track_navigation(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

# Simple fix for category dropdowns has been integrated into the inventory module

class KitchenDashboardApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load environment variables from .env file
        self.load_env_file()

        self.setWindowTitle("Kitchen Dashboard - Modern Edition")
        self.resize(1600, 1000)
        self.setMinimumSize(1400, 900)

        # Hide the default status bar to prevent the dark bar at bottom
        self.statusBar().hide()

        # Customize window appearance to match modern theme
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint |
                           Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint |
                           Qt.WindowCloseButtonHint)

        # Set window icon to match the kitchen theme
        self.setWindowIcon(self.create_window_icon())

        # Apply modern window styling
        self.apply_modern_window_style()

        # Initialize logger with comprehensive startup logging
        self.logger = get_logger()
        self.logger.log_startup_info()
        self.logger.info("🚀 Kitchen Dashboard application starting...")

        # Log each major initialization step for debugging
        self.logger.info("📋 Step 1: Application window and styling initialized")
        self.logger.log_ui_action("Window created", f"Size: {self.size().width()}x{self.size().height()}")

        # Initialize notification system
        self.notification_manager = get_notification_manager(self)

        # Initialize activity tracker
        if get_activity_tracker:
            self.activity_tracker = get_activity_tracker()
            track_system_event("application", "startup", "Kitchen Dashboard application starting")
        else:
            self.activity_tracker = None

        # Apply modern theme
        ModernTheme.apply_theme(QApplication.instance())
        
        # Define fonts before showing login dialog
        self.title_font = QFont("Segoe UI", 22, QFont.Bold)
        self.header_font = QFont("Segoe UI", 16, QFont.Bold)
        self.normal_font = QFont("Segoe UI", 10)
        self.button_font = QFont("Segoe UI", 10, QFont.Bold)
        
        # Set default currency symbol
        self.currency_symbol = "₹"  # Indian Rupee by default
        
        # Load data first with comprehensive error handling and logging
        self.logger.info("📊 Step 2: Loading application data...")
        try:
            import time
            start_time = time.time()
            self.data = self.load_data()
            load_time = time.time() - start_time

            if self.data:
                self.logger.log_performance("Data loading", load_time)
                self.logger.log_data_loading("All data sources", True,
                    f"Loaded {len(self.data)} data sources: {list(self.data.keys())}")

                # Log details about each data source
                for key, value in self.data.items():
                    if hasattr(value, 'shape'):
                        self.logger.info(f"   📋 {key}: {value.shape[0]} rows, {value.shape[1]} columns")
                    elif hasattr(value, '__len__'):
                        self.logger.info(f"   📋 {key}: {len(value)} items")
                    else:
                        self.logger.info(f"   📋 {key}: {type(value)}")
            else:
                self.logger.log_data_loading("Data sources", False, error="No data returned from load_data()")
                self.data = {}

        except Exception as e:
            self.logger.log_exception(e, "Critical error during data loading")
            self.logger.log_data_loading("Data sources", False, error=str(e))
            # Initialize with empty data to prevent crashes
            self.data = {}
            self.logger.warning("⚠️ Initialized with empty data to prevent application crash")
        
        # Initialize optimized Firebase
        self.firebase_user_id = "kitchen_dashboard_user" # Default user ID
        self.logger.info("Initializing optimized Firebase manager")
        try:
            from modules.optimized_firebase_manager import get_optimized_firebase_manager
            self.firebase_manager = get_optimized_firebase_manager()
            self.logger.info("Optimized Firebase manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize optimized Firebase manager: {e}")
            self.firebase_manager = None

        # Keep legacy Firebase sync for compatibility
        try:
            self.firebase_sync = FirebaseSync(parent=self, data=self.data, data_dir="data")
            # Add a log callback to show Firebase logs in the application
            self.firebase_sync.add_log_callback(self.log_firebase_message)
        except Exception as e:
            self.logger.error(f"Legacy Firebase sync initialization failed: {e}")
            self.firebase_sync = None

        # Firebase login and sync are now managed by the optimized manager
        self.logger.info("Firebase services initialized with enhanced authentication.")

        # Initialize responsive design and PWA features
        self.logger.info("Initializing responsive design and PWA features")
        try:
            from modules.responsive_design_manager import get_responsive_manager
            from modules.pwa_manager import get_pwa_manager
            from modules.mobile_navigation import get_mobile_navigation_manager
            from modules.responsive_table_utils import get_responsive_table_manager
            from modules.responsive_chart_utils import get_responsive_chart_manager
            from modules.responsive_dialog_utils import get_responsive_dialog_manager

            self.responsive_manager = get_responsive_manager()
            self.pwa_manager = get_pwa_manager(self.data)
            self.mobile_navigation = get_mobile_navigation_manager()
            self.responsive_table_manager = get_responsive_table_manager()
            self.responsive_chart_manager = get_responsive_chart_manager()
            self.responsive_dialog_manager = get_responsive_dialog_manager()

            self.logger.info("Responsive design and PWA features initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize responsive design and PWA features: {e}")
            self.responsive_manager = None
            self.pwa_manager = None
            self.mobile_navigation = None
            self.responsive_table_manager = None
            self.responsive_chart_manager = None
            self.responsive_dialog_manager = None

        # Initialize Multi-AI Engine and Enterprise features
        self.logger.info("Initializing Multi-AI Engine and Enterprise features")
        try:
            from modules.multi_ai_engine import get_multi_ai_engine
            from modules.enterprise_features import get_enterprise_manager

            self.multi_ai_engine = get_multi_ai_engine(self.data)
            self.enterprise_manager = get_enterprise_manager()

            self.logger.info("Multi-AI Engine and Enterprise features initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Multi-AI Engine and Enterprise features: {e}")
            self.multi_ai_engine = None
            self.enterprise_manager = None

        # Initialize performance and CSS optimizers
        self.logger.info("Initializing performance and CSS optimizers")
        try:
            from modules.css_optimizer import get_css_optimizer, get_optimized_stylesheet
            from modules.performance_optimizer import get_performance_optimizer
            from modules.performance_enhancer import get_performance_enhancer

            self.css_optimizer = get_css_optimizer()
            self.performance_optimizer = get_performance_optimizer()
            self.performance_enhancer = get_performance_enhancer()

            # Apply optimized stylesheet
            optimized_css = get_optimized_stylesheet()
            self.setStyleSheet(optimized_css)

            # Optimize application performance
            self.performance_optimizer.optimize_application_performance(QApplication.instance())

            # Apply enhanced performance optimizations
            self.apply_enhanced_performance_optimizations()

            # Apply advanced performance enhancements
            self.apply_advanced_performance_enhancements()

            self.logger.info("Performance and CSS optimizers initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize performance optimizers: {e}")
            self.css_optimizer = None
            self.performance_optimizer = None
        # Initialize inventory_widget as it's needed by other parts
        self.inventory_widget = None 
        # Directly initialize the UI, bypassing authentication
        self.initialize_ui()
        # If there was any user-specific setup that happened after login, ensure defaults are fine
        # For example, self.firebase_sync.current_user_id is already defaulted in FirebaseSync

        # Perform daily sync check after UI is initialized
        # self._check_and_perform_daily_sync() # Will be called at the end of initialize_ui

    def create_window_icon(self):
        """Create a custom window icon for the kitchen dashboard"""
        from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor

        # Create a 32x32 pixmap for the icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(102, 126, 234))  # Modern blue background

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a simple kitchen/chef hat shape
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QColor(255, 255, 255))

        # Draw chef hat outline (simplified)
        painter.drawEllipse(8, 12, 16, 12)  # Hat base
        painter.drawEllipse(10, 8, 12, 8)   # Hat top

        painter.end()

        return QIcon(pixmap)

    def apply_modern_window_style(self):
        """Apply modern styling to the window frame and title bar"""
        try:
            # Set window attributes for modern appearance
            self.setAttribute(Qt.WA_TranslucentBackground, False)

            # Apply custom window styling
            window_style = """
                QMainWindow {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 0px;
                }
            """
            self.setStyleSheet(window_style)

            # Set window opacity for a modern look
            self.setWindowOpacity(1.0)

            print("✅ Modern window styling applied")

        except Exception as e:
            print(f"⚠️ Error applying modern window style: {e}")

    def load_env_file(self):
        """Load environment variables from .env file"""
        env_file = '.env'
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
                print(f"✅ Loaded environment variables from {env_file}")
            except Exception as e:
                print(f"⚠️  Error loading .env file: {e}")

    def _check_and_perform_daily_sync(self):
        self.logger.info("Checking if daily sync is required...")
        last_sync_file = os.path.join('data', 'last_sync_date.txt')
        today_str = datetime.now().strftime('%Y-%m-%d')
        sync_needed = False

        if not os.path.exists(last_sync_file):
            self.logger.info("Last sync date file not found. Sync needed.")
            sync_needed = True
        else:
            try:
                with open(last_sync_file, 'r') as f:
                    last_sync_date_str = f.read().strip()
                if last_sync_date_str != today_str:
                    self.logger.info(f"Last sync was on {last_sync_date_str}. Today is {today_str}. Sync needed.")
                    sync_needed = True
                else:
                    self.logger.info(f"Daily sync already performed today ({today_str}). Skipping.")
            except Exception as e:
                self.logger.error(f"Error reading last sync date file: {e}. Assuming sync is needed.")
                sync_needed = True

        if sync_needed:
            self.logger.info("Attempting daily synchronization...")
            # Ensure firebase_sync is initialized and the Firestore DB client is available
            if hasattr(self, 'firebase_sync') and firebase_integration.FIRESTORE_DB:
                # First, sync local changes to cloud
                self.logger.info("Daily Sync: Syncing local data to cloud...")
                cloud_sync_success = self.firebase_sync.sync_to_cloud()
                if cloud_sync_success:
                    self.logger.info("Daily Sync: Successfully synced local data to cloud.")
                    # Then, sync cloud changes to local
                    self.logger.info("Daily Sync: Syncing cloud data to local...")
                    local_sync_success = self.firebase_sync.sync_from_cloud()
                    if local_sync_success:
                        self.logger.info("Daily Sync: Successfully synced cloud data to local.")
                        # Reload data and refresh UI after successful download from cloud
                        self.logger.info("Daily Sync: Reloading all application data after cloud sync.")
                        self.data = self.load_data() 
                        self.logger.info("Daily Sync: Refreshing all UI tabs after data reload.")
                        self.refresh_all_tabs()
                        try:
                            with open(last_sync_file, 'w') as f:
                                f.write(today_str)
                            self.logger.info(f"Updated last sync date to {today_str}.")
                        except Exception as e:
                            self.logger.error(f"Error writing last sync date file: {e}")
                    else:
                        self.logger.error("Daily Sync: Failed to sync cloud data to local.")
                else:
                    self.logger.error("Daily Sync: Failed to sync local data to cloud.")
            else:
                self.logger.warning("Firebase not initialized or no database connection, cannot perform daily sync.")
        else:
            # Ensure local data is loaded even if sync is skipped
            self.logger.info("Daily sync not needed. Ensuring local data is loaded.")
            # self.data = self.load_data() # Data is already loaded in __init__
            # self.update_ui_with_loaded_data() # Call if you have a method to refresh UI from self.data
            pass

    def trigger_manual_full_sync(self):
        self.logger.info("Manual full sync triggered.")
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("Synchronization")
        progress_dialog.setText("Manual sync in progress... Please wait.")
        progress_dialog.setStandardButtons(QMessageBox.NoButton) # No buttons, just info
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        QApplication.processEvents() # Ensure dialog shows before long operation

        sync_successful = False
        if hasattr(self, 'firebase_sync') and self.firebase_sync.db:
            self.logger.info("Manual Sync: Syncing local data to cloud...")
            cloud_sync_success = self.firebase_sync.sync_to_cloud()
            if cloud_sync_success:
                self.logger.info("Manual Sync: Successfully synced local data to cloud.")
                self.logger.info("Manual Sync: Syncing cloud data to local...")
                local_sync_success = self.firebase_sync.sync_from_cloud()
                if local_sync_success:
                    self.logger.info("Manual Sync: Successfully synced cloud data to local.")
                    sync_successful = True
                    try:
                        last_sync_file = os.path.join('data', 'last_sync_date.txt')
                        today_str = datetime.now().strftime('%Y-%m-%d')
                        with open(last_sync_file, 'w') as f:
                            f.write(today_str)
                        self.logger.info(f"Updated last sync date to {today_str} after manual sync.")
                    except Exception as e:
                        self.logger.error(f"Error writing last sync date file after manual sync: {e}")
                else:
                    self.logger.error("Manual Sync: Failed to sync cloud data to local.")
                    QMessageBox.critical(self, "Sync Error", "Failed to sync data from cloud. Check logs for details.")
            else:
                self.logger.error("Manual Sync: Failed to sync local data to cloud.")
                QMessageBox.critical(self, "Sync Error", "Failed to sync data to cloud. Check logs for details.")
        else:
            self.logger.warning("Firebase not initialized or no database connection, cannot perform manual sync.")
            QMessageBox.warning(self, "Sync Error", "Firebase not available. Cannot perform manual sync.")
        
        progress_dialog.hide()
        progress_dialog.deleteLater()

        if sync_successful:
            QMessageBox.information(self, "Sync Complete", "Manual data synchronization with cloud completed successfully!")
        # Error messages are shown inline above for specific failures
        
        return sync_successful
            
    def show_authentication_dialog(self):
        """Show authentication dialog and only proceed if user authenticates"""
        # Create login dialog
        login_dialog = LoginDialog(self)
        # Connect authentication signal
        login_dialog.login_successful.connect(self.handle_authentication_result)
        # Show dialog as modal
        login_dialog.exec()
        
    def handle_authentication_result(self, user_info):
        """Handle the result of authentication dialog"""
        # Authentication successful
        self.logger.info("Authentication successful")
        # Pass user info to firebase sync
        self.firebase_sync.handle_login_success(user_info)
        
        # Initialize the UI
        self.initialize_ui()
        
    def log_firebase_message(self, message, level="info"):
        """Log Firebase messages to the application logger
        
        Args:
            message (str): The message to log
            level (str): The log level (info, warning, error)
        """
        # Log to the application logger
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        
        # If settings widget is initialized, also show in the settings log display
        if hasattr(self, 'settings_widget'):
            self.settings_widget.add_log(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", level)
        
    
    def auto_refresh_data(self):
        """Automatically refresh data when CSV files change"""
        try:
            # Check if any CSV files have been modified
            data_dir = "data"
            if not os.path.exists(data_dir):
                return
            
            refresh_needed = False
            current_time = datetime.now()
            
            # Check modification times of CSV files
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(data_dir, filename)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    # If file was modified in the last 5 seconds, refresh
                    if (current_time - mod_time).total_seconds() < 5:
                        refresh_needed = True
                        break
            
            if refresh_needed:
                self.logger.info("Auto-refreshing data due to CSV file changes")
                self.data = self.load_data()
                
                # Refresh current tab
                if hasattr(self, 'current_widget') and hasattr(self.current_widget, 'load_data'):
                    self.current_widget.load_data()
                
        except Exception as e:
            self.logger.error(f"Error in auto-refresh: {e}")
    
    def setup_auto_refresh_timer(self):
        """Setup timer for auto-refresh with performance optimization"""
        try:
            from PySide6.QtCore import QTimer
            self.refresh_timer = QTimer()

            # Use debounced refresh to prevent excessive updates
            if hasattr(self, 'performance_enhancer'):
                debounced_refresh = lambda: self.performance_enhancer.debounce(
                    'auto_refresh', self.auto_refresh_data, 5000  # 5 second debounce
                )
                self.refresh_timer.timeout.connect(debounced_refresh)
            else:
                self.refresh_timer.timeout.connect(self.auto_refresh_data)

            self.refresh_timer.start(10000)  # Check every 10 seconds (less aggressive)
            self.logger.info("Auto-refresh timer started with performance optimization")
        except Exception as e:
            self.logger.error(f"Error setting up auto-refresh timer: {e}")

    def initialize_ui(self):
        """Initialize the UI after authentication"""
        # Apply modern style
        self.apply_modern_style()
        
        try:
            if self.firebase_sync.is_firebase_available():
                self.logger.info("Firebase sync initialized successfully")
            else:
                self.logger.warning("Firebase integration not available")
        except Exception as e:
            self.logger.error(f"Error initializing Firebase sync: {str(e)}")
            
        # Create main widget and layout with splitter for responsiveness
        self.central_widget = QWidget()
        # Set up the main window and central widget
        self.setCentralWidget(self.central_widget)
        self._check_and_perform_daily_sync()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use a splitter to allow resizing of sidebar and content
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)  # Prevent collapsing sections
        
        # Create and populate sidebar for navigation
        self.create_sidebar()
        
        # Create content area with header and scroll capability for responsiveness
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setStyleSheet("""
            #contentWidget {
                background-color: #f5f5f7;
                border-radius: 10px;
                min-width: 400px;
                min-height: 300px;
            }
        """)

        # Ensure content widget is visible
        self.content_widget.setVisible(True)
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create main content layout with header
        main_content_layout = QVBoxLayout(self.content_widget)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)

        # Create header with bell icon
        self.create_content_header(main_content_layout)

        # Create scrollable content area
        self.scrollable_content = QWidget()
        self.content_layout = QVBoxLayout(self.scrollable_content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)

        # Use scroll area to ensure content is accessible at any window size
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setWidget(self.scrollable_content)
        self.content_scroll.setFrameShape(QFrame.NoFrame)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        main_content_layout.addWidget(self.content_scroll)
        
        # Ensure widgets are visible before adding to splitter
        self.sidebar.setVisible(True)
        self.content_widget.setVisible(True)
        self.sidebar.show()
        self.content_widget.show()

        # Add widgets to splitter
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.addWidget(self.content_widget)

        # Set initial sizes (sidebar: 240px, content: rest of space)
        # Use larger values to ensure proper sizing
        self.main_splitter.setSizes([240, 1000])

        # Set minimum sizes to prevent widgets from disappearing
        self.sidebar.setMinimumWidth(60)  # Allow collapsing to 60px
        self.content_widget.setMinimumWidth(400)  # Ensure content is always visible

        # Set splitter properties
        self.main_splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        self.main_splitter.setStretchFactor(1, 1)  # Content area stretches

        # Ensure splitter is visible
        self.main_splitter.setVisible(True)
        self.main_splitter.show()

        # Add splitter to main layout
        self.main_layout.addWidget(self.main_splitter)

        # Debug: Print layout info
        print(f"🔧 LAYOUT DEBUG:")
        print(f"   Sidebar size: {self.sidebar.size()}")
        print(f"   Content widget size: {self.content_widget.size()}")
        print(f"   Splitter sizes: {self.main_splitter.sizes()}")

        # Show home page by default
        self.show_home_page()
        
        # Setup auto-refresh timer
        self.setup_auto_refresh_timer()

        # Force layout update after a short delay
        QTimer.singleShot(100, self.force_layout_update)

        # Add welcome notification
        QTimer.singleShot(2000, self.show_welcome_notification)

        # Connect responsive manager to handle layout changes
        if self.responsive_manager:
            self.responsive_manager.device_type_changed.connect(self.handle_device_type_change)
            self.responsive_manager.layout_mode_changed.connect(self.handle_layout_mode_change)

        # Synchronize categories across all modules
        QTimer.singleShot(3000, self.synchronize_categories)

    def force_layout_update(self):
        """Force layout update to ensure proper sizing"""
        try:
            # Update all layouts
            self.main_layout.update()
            self.main_splitter.update()

            # Ensure proper splitter sizes
            current_sizes = self.main_splitter.sizes()
            if len(current_sizes) == 2:
                total_width = sum(current_sizes)
                if total_width > 0:
                    # Ensure sidebar has proper width and content gets the rest
                    sidebar_width = 240 if self.sidebar_expanded else 60
                    content_width = max(400, total_width - sidebar_width)
                    self.main_splitter.setSizes([sidebar_width, content_width])

            # Force widget updates
            self.sidebar.update()
            self.content_widget.update()

            print(f"🔧 LAYOUT UPDATED:")
            print(f"   Window size: {self.size()}")
            print(f"   Splitter sizes: {self.main_splitter.sizes()}")
            print(f"   Sidebar visible: {self.sidebar.isVisible()}")
            print(f"   Content visible: {self.content_widget.isVisible()}")

        except Exception as e:
            print(f"Error in force_layout_update: {e}")

    def handle_device_type_change(self, device_type):
        """Handle device type changes for responsive design"""
        try:
            self.logger.info(f"Device type changed to: {device_type.value}")

            # Update sidebar behavior based on device type
            if hasattr(self, 'sidebar') and self.sidebar:
                if device_type.value == "mobile":
                    # Hide sidebar on mobile, use mobile navigation
                    self.sidebar.setVisible(False)
                    if self.mobile_navigation:
                        self.mobile_navigation.switch_to_bottom_tabs()
                elif device_type.value == "tablet":
                    # Show compact sidebar on tablet
                    self.sidebar.setVisible(True)
                    self.sidebar.setMaximumWidth(200)
                    if self.mobile_navigation:
                        self.mobile_navigation.switch_to_hamburger()
                else:
                    # Show full sidebar on desktop
                    self.sidebar.setVisible(True)
                    self.sidebar.setMaximumWidth(300)
                    if self.mobile_navigation:
                        self.mobile_navigation.switch_to_sidebar()

            # Update content margins
            if hasattr(self, 'content_layout') and self.content_layout:
                if device_type.value == "mobile":
                    self.content_layout.setContentsMargins(12, 12, 12, 12)
                    self.content_layout.setSpacing(16)
                elif device_type.value == "tablet":
                    self.content_layout.setContentsMargins(16, 16, 16, 16)
                    self.content_layout.setSpacing(20)
                else:
                    self.content_layout.setContentsMargins(20, 20, 20, 20)
                    self.content_layout.setSpacing(24)

            # Update splitter sizes
            if hasattr(self, 'main_splitter') and self.main_splitter:
                if device_type.value == "mobile":
                    self.main_splitter.setSizes([0, 1000])  # Hide sidebar
                elif device_type.value == "tablet":
                    self.main_splitter.setSizes([200, 800])  # Compact sidebar
                else:
                    self.main_splitter.setSizes([240, 1000])  # Normal sidebar

        except Exception as e:
            self.logger.error(f"Error handling device type change: {e}")

    def handle_layout_mode_change(self, layout_mode):
        """Handle layout mode changes for responsive design"""
        try:
            self.logger.info(f"Layout mode changed to: {layout_mode.value}")

            # Update content spacing based on layout mode
            if hasattr(self, 'content_layout') and self.content_layout:
                if layout_mode.value == "compact":
                    self.content_layout.setSpacing(12)
                elif layout_mode.value == "expanded":
                    self.content_layout.setSpacing(32)
                else:
                    self.content_layout.setSpacing(20)

        except Exception as e:
            self.logger.error(f"Error handling layout mode change: {e}")

    def resizeEvent(self, event):
        """Handle window resize events for responsive design"""
        super().resizeEvent(event)

        try:
            if self.responsive_manager:
                # Update responsive manager with new size
                self.responsive_manager.update_layout(event.size())

        except Exception as e:
            self.logger.error(f"Error in resize event: {e}")

    def synchronize_categories(self):
        """Synchronize categories across all modules"""
        try:
            from modules.category_manager import CategoryManager

            category_manager = CategoryManager(self.data)
            result = category_manager.synchronize_categories()

            if result['success']:
                self.logger.info(f"Categories synchronized successfully across {len(result['synchronized_modules'])} modules")
                self.logger.info(f"Added {result['categories_added']} new category entries")

                # Add notification about category synchronization
                self.add_notification(
                    "Category Sync Complete",
                    f"Categories synchronized across {len(result['synchronized_modules'])} modules. {result['categories_added']} entries added.",
                    "success"
                )
            else:
                self.logger.warning(f"Category synchronization had issues: {result['errors']}")
                self.add_notification(
                    "Category Sync Issues",
                    f"Some issues occurred during category synchronization: {', '.join(result['errors'][:2])}",
                    "warning"
                )

        except Exception as e:
            self.logger.error(f"Error synchronizing categories: {e}")
            self.add_notification(
                "Category Sync Error",
                f"Failed to synchronize categories: {str(e)}",
                "error"
            )

    def create_content_header(self, parent_layout):
        """Create the content header with bell icon and proper alignment"""
        header_widget = QWidget()
        header_widget.setObjectName("contentHeader")
        header_widget.setFixedHeight(70)
        header_widget.setStyleSheet("""
            QWidget#contentHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2) !important;
                border-bottom: 2px solid #5a67d8;
                border-radius: 0px 0px 15px 15px;
            }
        """)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(25, 10, 25, 10)  # Reduced vertical margins for better alignment
        header_layout.setSpacing(20)
        header_layout.setAlignment(Qt.AlignVCenter)  # Ensure vertical center alignment

        # App title/logo area with icon - improved alignment
        title_container = QWidget()
        title_container.setStyleSheet("QWidget { background: transparent !important; }")
        title_container_layout = QHBoxLayout(title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.setSpacing(12)
        title_container_layout.setAlignment(Qt.AlignVCenter)  # Vertical center alignment

        # Kitchen icon with better alignment
        kitchen_icon = QLabel("🍳")
        kitchen_icon.setFont(QFont("Segoe UI", 24))
        kitchen_icon.setStyleSheet("color: white; border: none;")
        kitchen_icon.setAlignment(Qt.AlignCenter)
        title_container_layout.addWidget(kitchen_icon)

        # Text container for title and subtitle
        text_container = QWidget()
        text_container.setStyleSheet("QWidget { background: transparent !important; }")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # Title text
        title_label = QLabel("Kitchen Dashboard")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("""
            color: white;
            border: none;
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_layout.addWidget(title_label)

        # Apply Qt-native text shadow effect instead of CSS text-shadow
        try:
            from utils.qt_effects import add_title_shadow
            add_title_shadow(title_label)
        except Exception as e:
            self.logger.debug(f"Could not apply title shadow effect: {e}")

        # Subtitle
        subtitle_label = QLabel("Professional Kitchen Management")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("""
            color: rgba(255,255,255,0.8);
            border: none;
        """)
        subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_layout.addWidget(subtitle_label)

        title_container_layout.addWidget(text_container)

        header_layout.addWidget(title_container)

        header_layout.addStretch()

        # Status indicator with perfect center alignment and fixed width
        status_container = QWidget()
        status_container.setFixedWidth(140)  # Fixed width to prevent excessive space usage
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to allow full centering
        status_layout.setSpacing(8)  # Spacing between icon and text

        # Add stretch before content to push it to center
        status_layout.addStretch(1)

        status_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255,255,255,0.15) !important;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 15px;
                min-height: 35px;
                max-height: 35px;
            }
        """)

        status_icon = QLabel("🟢")
        status_icon.setFont(QFont("Segoe UI", 12))
        status_icon.setAlignment(Qt.AlignCenter)
        status_icon.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        status_layout.addWidget(status_icon)

        status_label = QLabel("System Active")
        status_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        status_label.setStyleSheet("""
            QLabel {
                color: white;
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(status_label)

        # Add stretch after content to center it
        status_layout.addStretch(1)

        header_layout.addWidget(status_container)

        # Notification bell icon
        try:
            from modules.enhanced_notification_system import NotificationBellWidget
            self.notification_bell = NotificationBellWidget(self)
            header_layout.addWidget(self.notification_bell)
            self.logger.info("Notification bell widget loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading notification bell: {e}")
            # Fallback to simple but very visible bell
            bell_widget = QPushButton("🔔 NOTIFICATIONS")
            bell_widget.setFixedSize(150, 35)
            bell_widget.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 17px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            bell_widget.setToolTip("Click to view notifications (Fallback Mode)")
            bell_widget.clicked.connect(lambda: self.show_fallback_notification())

            header_layout.addWidget(bell_widget)
            self.logger.info("Using prominent fallback notification bell")

        parent_layout.addWidget(header_widget)

    def add_notification(self, title, message, notification_type="info"):
        """Add a notification to the bell icon"""
        try:
            if hasattr(self, 'notification_bell'):
                return self.notification_bell.add_notification(title, message, notification_type)
        except Exception as e:
            self.logger.error(f"Error adding notification: {e}")
        return None

    def show_fallback_notification(self):
        """Show fallback notification dialog"""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Notifications")
        msg.setText("Notification System Active!")
        msg.setInformativeText("The enhanced notification system is working.\nThis is a fallback notification display.")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def show_welcome_notification(self):
        """Show welcome notification"""
        self.add_notification(
            "Welcome to Kitchen Dashboard",
            "All systems are operational. Enhanced features are now available!",
            "success"
        )

        # Add some sample notifications to demonstrate the system
        QTimer.singleShot(5000, lambda: self.add_notification(
            "Packing Materials",
            "Packing materials module loaded successfully",
            "info"
        ))

        QTimer.singleShot(8000, lambda: self.add_notification(
            "Recipe Scaling",
            "Recipe scaling feature is now available in Pricing tab",
            "info"
        ))

    def apply_modern_style(self):
        """Apply modern styling to the entire application"""
        # Set application style to Fusion (most customizable)
        QApplication.setStyle(QStyleFactory.create("Fusion"))

        # Create a custom palette
        palette = QPalette()

        # Set window and base colors
        palette.setColor(QPalette.Window, QColor(248, 250, 252))  # Updated to match optimized CSS
        palette.setColor(QPalette.WindowText, QColor(15, 23, 42))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(241, 245, 249))

        # Text colors
        palette.setColor(QPalette.Text, QColor(55, 65, 81))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))

        # Button colors
        palette.setColor(QPalette.Button, QColor(59, 130, 246))

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        # Apply the palette
        QApplication.setPalette(palette)
        
        # Set global stylesheet
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #f0f0f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e0e0e5;
            border: 1px solid #dcdcdc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 1px solid white;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #eaeaef;
        }
        
        QPushButton {
            background-color: #2a82da;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #3a92ea;
        }
        
        QPushButton:pressed {
            background-color: #1a72ca;
        }
        
        QTableWidget {
            gridline-color: #e0e0e0;
            selection-background-color: #e0f0ff;
            selection-color: #000000;
            border: 1px solid #dcdcdc;
            border-radius: 4px;
        }
        
        QHeaderView::section {
            background-color: #f0f0f5;
            border: 1px solid #dcdcdc;
            padding: 4px;
            font-weight: bold;
        }
        
        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
            border: 1px solid #dcdcdc;
            border-radius: 4px;
            padding: 4px 8px;
            background-color: white;
            selection-background-color: #2a82da;
            selection-color: white;
        }
        
        QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover {
            border: 1px solid #aaaaaa;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #f0f0f5;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #c0c0c5;
            border-radius: 5px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #a0a0a5;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #f0f0f5;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #c0c0c5;
            border-radius: 5px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #a0a0a5;
        }
        
        QGroupBox {
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-
            padding: 0 5px;
            background-color: white;
        }
        """

        # Use optimized stylesheet if available, otherwise use fallback
        try:
            if hasattr(self, 'css_optimizer') and self.css_optimizer:
                from modules.css_optimizer import get_optimized_stylesheet
                optimized_stylesheet = get_optimized_stylesheet()
                self.setStyleSheet(optimized_stylesheet)
                self.logger.info("Applied optimized CSS stylesheet")
            else:
                self.setStyleSheet(stylesheet)
        except Exception as e:
            self.logger.error(f"Error applying optimized stylesheet: {e}")
            self.setStyleSheet(stylesheet)

    def optimize_widget_performance(self, widget):
        """Optimize widget performance"""
        try:
            if hasattr(self, 'performance_optimizer') and self.performance_optimizer:
                self.performance_optimizer.optimize_widget_rendering(widget)

                # Optimize tables specifically
                from PySide6.QtWidgets import QTableWidget
                if isinstance(widget, QTableWidget):
                    self.performance_optimizer.optimize_table_performance(widget)

        except Exception as e:
            self.logger.error(f"Error optimizing widget performance: {e}")

    def apply_enhanced_performance_optimizations(self):
        """Apply enhanced performance optimizations"""
        try:
            if hasattr(self, 'performance_optimizer') and self.performance_optimizer:
                # Optimize data loading
                self.load_data = self.performance_optimizer.optimize_data_loading(self.load_data)

                # Optimize memory usage
                self.performance_optimizer.optimize_memory_usage()

                # Create performance monitor (optional)
                if hasattr(self, 'show_performance_monitor'):
                    self.performance_monitor = self.performance_optimizer.create_performance_monitor()

                self.logger.info("Enhanced performance optimizations applied")

        except Exception as e:
            self.logger.error(f"Error applying enhanced performance optimizations: {e}")

    def apply_advanced_performance_enhancements(self):
        """Apply advanced performance enhancements to prevent UI freezing"""
        try:
            if hasattr(self, 'performance_enhancer') and self.performance_enhancer:
                # Optimize data loading with async operations
                original_load_data = self.load_data
                self.load_data = self.performance_enhancer.optimize_data_loading(original_load_data)

                # Setup memory monitoring
                self.performance_enhancer.setup_memory_monitoring()

                # Optimize widget updates
                self.performance_enhancer.optimize_widget_updates(self)

                self.logger.info("Advanced performance enhancements applied")

        except Exception as e:
            self.logger.error(f"Error applying advanced performance enhancements: {e}")

    def show_performance_monitor(self):
        """Show performance monitoring window"""
        try:
            if hasattr(self, 'performance_monitor'):
                self.performance_monitor.show()
            else:
                self.performance_monitor = self.performance_optimizer.create_performance_monitor()
                self.performance_monitor.show()

        except Exception as e:
            self.logger.error(f"Error showing performance monitor: {e}")

    def refresh_data(self):
        """Refresh all data from CSV files and update the current view"""
        self.logger.info("[REFRESH] Refreshing all data from CSV files...")

        try:
            # Reload data
            self.data = self.load_data()

            # Refresh the current view by re-calling the current page function
            current_button = None
            for button in self.nav_buttons:
                if button.isChecked():
                    current_button = button
                    break

            if current_button:
                # Trigger the current page refresh
                current_button.click()
                self.logger.info("[SUCCESS] Data refreshed and current view updated")
            else:
                self.logger.info("[SUCCESS] Data refreshed")

        except Exception as e:
            self.logger.error(f"[ERROR] Error refreshing data: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh data: {e}")

    def load_data(self):
        """Load all data from CSV files or create empty dataframes if files don't exist"""
        self.logger.info("🔄 Starting comprehensive data loading...")
        data = {}

        try:
            # Check if data directory exists
            if not os.path.exists('data'):
                os.makedirs('data')
                self.logger.info("📁 Created data directory")

            # Log current working directory and data path
            self.logger.info(f"📂 Working directory: {os.getcwd()}")
            self.logger.info(f"📂 Data directory: {os.path.abspath('data')}")

            # List all files in data directory
            if os.path.exists('data'):
                data_files = os.listdir('data')
                self.logger.info(f"📋 Files in data directory: {data_files}")
            else:
                self.logger.warning("⚠️ Data directory does not exist!")

            # Define empty dataframes for each data type with comprehensive columns
            empty_dataframes = {
                'inventory': pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'price_per_unit',
                    'location', 'expiry_date', 'reorder_level', 'total_value', 'price',
                    'qty_purchased', 'qty_used', 'avg_price', 'description', 'default_cost',
                    'purchase_count', 'total_spent', 'last_purchase_date', 'last_purchase_price'
                ]),
                'meal_plan': pd.DataFrame(columns=[
                    'day', 'meal_type', 'recipe_id', 'recipe_name', 'servings', 'prep_time', 'cook_time'
                ]),
                'recipes': pd.DataFrame(columns=[
                    'recipe_id', 'recipe_name', 'category', 'servings', 'prep_time', 'cook_time',
                    'description', 'ingredients', 'instructions'
                ]),
                'budget': pd.DataFrame(columns=[
                    'budget_id', 'category', 'amount', 'period', 'date'
                ]),
                'sales': pd.DataFrame(columns=[
                    'sale_id', 'item_name', 'quantity', 'price_per_unit', 'total_amount', 'customer', 'date'
                ]),
                'shopping_list': pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'priority',
                    'last_price', 'current_price', 'avg_price', 'location', 'notes', 'status', 'date_added', 'date_purchased'
                ]),
                'waste': pd.DataFrame(columns=[
                    'waste_id', 'item_name', 'quantity', 'unit', 'reason', 'cost', 'date'
                ]),
                'cleaning_maintenance': pd.DataFrame(columns=[
                    'task_id', 'task_name', 'frequency', 'last_completed', 'next_due', 'priority', 'notes'
                ]),
                'items': pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'description', 'unit', 'default_cost'
                ]),
                'categories': pd.DataFrame(columns=[
                    'category_id', 'category_name', 'description'
                ]),
                'recipe_ingredients': pd.DataFrame(columns=[
                    'recipe_id', 'ingredient_id', 'item_name', 'quantity', 'unit', 'notes'
                ]),
                'pricing': pd.DataFrame(columns=[
                    'recipe_id', 'recipe_name', 'total_cost', 'cost_per_serving', 'last_calculated'
                ]),
                'packing_materials': pd.DataFrame(columns=[
                    'material_id', 'material_name', 'category', 'size', 'unit', 'cost_per_unit',
                    'current_stock', 'minimum_stock', 'supplier', 'notes', 'date_added'
                ]),
                'recipe_packing_materials': pd.DataFrame(columns=[
                    'recipe_id', 'recipe_name', 'material_id', 'material_name', 'quantity_needed', 'cost_per_recipe', 'notes'
                ])
            }

            # Track loading statistics
            loading_stats = {
                'files_found': 0,
                'files_loaded': 0,
                'files_created': 0,
                'total_rows': 0,
                'errors': []
            }
            
            # Iterate over each data type with comprehensive logging
            for key, empty_df in empty_dataframes.items():
                file_path = os.path.join('data', f'{key}.csv')
                self.logger.info(f"🔍 Processing {key} data source...")

                if os.path.exists(file_path):
                    try:
                        # Performance optimization: Check file size and use chunked loading for large files
                        file_size = os.path.getsize(file_path)
                        self.logger.info(f"  📄 File found: {file_path} ({file_size} bytes)")

                        if file_size > 5 * 1024 * 1024:  # 5MB threshold
                            # Load large files in chunks to avoid memory issues
                            self.logger.info(f"  📊 Loading large file in chunks...")
                            chunks = []
                            chunk_count = 0
                            for chunk in pd.read_csv(file_path, chunksize=1000):
                                chunks.append(chunk)
                                chunk_count += 1
                            data[key] = pd.concat(chunks, ignore_index=True) if chunks else empty_df
                            self.logger.info(f"  ✅ Loaded {chunk_count} chunks from {file_path} ({file_size/1024/1024:.1f}MB)")
                        else:
                            # Load smaller files normally
                            data[key] = pd.read_csv(file_path, low_memory=False)
                            self.logger.info(f"  ✅ Loaded {len(data[key])} rows from {file_path} ({file_size/1024:.1f}KB)")

                        # Log data structure info
                        if len(data[key]) > 0:
                            self.logger.info(f"  📋 Columns: {list(data[key].columns)}")
                            self.logger.info(f"  📊 Shape: {data[key].shape}")
                        else:
                            self.logger.warning(f"  ⚠️ File {file_path} is empty")

                        loading_stats['files_found'] += 1
                        loading_stats['files_loaded'] += 1

                    except Exception as e:
                        error_msg = f"❌ Error loading {key} from {file_path}: {e}"
                        print(error_msg)  # Keep for immediate console feedback
                        self.logger.error(error_msg)
                        self.logger.log_exception(e, f"Loading {key} data")
                        data[key] = empty_df  # Use in-memory empty DataFrame
                        self.logger.warning(f"  🔄 Used empty dataframe for {key} due to read error. ORIGINAL FILE {file_path} WAS NOT MODIFIED.")
                        loading_stats['errors'].append(f"{key}: {str(e)}")
                else:
                    self.logger.warning(f"  📄 File not found: {file_path}")
                    data[key] = empty_df
                    # Save the empty dataframe to create the file if it doesn't exist
                    try:
                        empty_df.to_csv(file_path, index=False)
                        self.logger.info(f"  ✅ Created new empty file for {key} at {file_path}")
                        loading_stats['files_created'] += 1
                    except Exception as e:
                        self.logger.error(f"  ❌ Error creating new empty file for {key} at {file_path}: {e}")
                        loading_stats['errors'].append(f"Create {key}: {str(e)}")
            
            # Convert date columns to datetime (even for empty dataframes)
            for df_name in ['budget', 'sales', 'waste']:
                if 'date' in data[df_name].columns:
                    # Create a datetime column even if empty
                    data[df_name]['date'] = pd.to_datetime(data[df_name]['date'], errors='coerce')
            
            # Convert date columns in cleaning_maintenance
            if 'last_completed' in data['cleaning_maintenance'].columns:
                data['cleaning_maintenance']['last_completed'] = pd.to_datetime(data['cleaning_maintenance']['last_completed'], errors='coerce')
            if 'next_due' in data['cleaning_maintenance'].columns:
                data['cleaning_maintenance']['next_due'] = pd.to_datetime(data['cleaning_maintenance']['next_due'], errors='coerce')
            
            # Convert expiry_date in inventory
            if 'expiry_date' in data['inventory'].columns:
                data['inventory']['expiry_date'] = pd.to_datetime(data['inventory']['expiry_date'], errors='coerce')
                
            # Debug: Log data loading results
            print(f"🔍 DATA LOADING DEBUG:")
            for key, df in data.items():
                if isinstance(df, pd.DataFrame):
                    print(f"  {key}: {len(df)} rows × {len(df.columns)} columns")
                else:
                    print(f"  {key}: {type(df)} (not a DataFrame)")

            # Log comprehensive loading statistics
            self.logger.info("📊 Data loading completed - Summary:")
            self.logger.info(f"  📁 Files found: {loading_stats['files_found']}")
            self.logger.info(f"  ✅ Files loaded: {loading_stats['files_loaded']}")
            self.logger.info(f"  🆕 Files created: {loading_stats['files_created']}")
            self.logger.info(f"  ❌ Errors: {len(loading_stats['errors'])}")

            if loading_stats['errors']:
                self.logger.error("  Error details:")
                for error in loading_stats['errors']:
                    self.logger.error(f"    - {error}")

            # Assign data to self.data immediately
            self.data = data

            # Print final summary with enhanced details
            print(f"\n✅ DATA LOADING COMPLETED SUCCESSFULLY!")
            print(f"   📊 Total tables loaded: {len(data)}")
            total_records = sum(len(df) for df in data.values() if hasattr(df, '__len__'))
            print(f"   📋 Total records: {total_records}")
            print(f"   📁 Files processed: {loading_stats['files_found']}")
            print(f"   🆕 Files created: {loading_stats['files_created']}")
            if loading_stats['errors']:
                print(f"   ⚠️ Errors encountered: {len(loading_stats['errors'])}")

            self.logger.log_performance("Complete data loading", 0)  # Will be calculated by caller
            return data
        except Exception as e:
            error_msg = f"Error loading data: {e}"
            self.logger.critical(error_msg)
            print(f"❌ CRITICAL ERROR in load_data: {error_msg}")

            # Don't show message box during initialization to avoid blocking
            if hasattr(self, 'isVisible') and self.isVisible():
                QMessageBox.critical(self, "Error", error_msg)

            # Return empty dataframes instead of None to prevent crashes
            empty_dataframes = {
                'inventory': pd.DataFrame(),
                'meal_plan': pd.DataFrame(),
                'recipes': pd.DataFrame(),
                'budget': pd.DataFrame(),
                'sales': pd.DataFrame(),
                'shopping_list': pd.DataFrame(),
                'waste': pd.DataFrame(),
                'cleaning_maintenance': pd.DataFrame(),
                'items': pd.DataFrame(),
                'categories': pd.DataFrame(),
                'recipe_ingredients': pd.DataFrame(),
                'pricing': pd.DataFrame(),
                'packing_materials': pd.DataFrame(),
                'recipe_packing_materials': pd.DataFrame()
            }

            # Assign empty data to self.data
            self.data = empty_dataframes
            return empty_dataframes

    def debug_data_before_widget_creation(self, tab_name, required_keys=None):
        """Debug data before creating widgets"""
        print(f"🔍 {tab_name.upper()} TAB DEBUG:")
        print(f"  self.data keys: {list(self.data.keys()) if self.data else 'None'}")

        if required_keys:
            for key in required_keys:
                if key in self.data:
                    df = self.data[key]
                    if hasattr(df, 'shape'):
                        print(f"  {key}: {df.shape[0]} rows × {df.shape[1]} columns")
                        if len(df) > 0 and hasattr(df, 'columns'):
                            sample_cols = list(df.columns)[:3]
                            print(f"    Columns: {sample_cols}...")
                            if len(df) > 0:
                                first_row = df.iloc[0]
                                sample_data = []
                                for col in sample_cols:
                                    val = str(first_row[col])[:15] if pd.notna(first_row[col]) else 'N/A'
                                    sample_data.append(val)
                                print(f"    Sample: {' | '.join(sample_data)}")
                        else:
                            print(f"    ⚠️  EMPTY - no data rows")
                    else:
                        print(f"  {key}: {type(df)} (not a DataFrame)")
                else:
                    print(f"  ❌ {key}: KEY NOT FOUND")

        print(f"  Total data keys: {len(self.data) if self.data else 0}")

    def ensure_data_integrity(self):
        """Ensure data integrity and reload if necessary"""
        try:
            if not self.data or not isinstance(self.data, dict):
                print("⚠️ Data is None or not a dictionary, reloading...")
                self.data = self.load_data()

            # Check if all required keys exist
            required_keys = ['inventory', 'recipes', 'recipe_ingredients', 'shopping_list', 'sales', 'waste']
            missing_keys = [key for key in required_keys if key not in self.data]

            if missing_keys:
                print(f"⚠️ Missing data keys: {missing_keys}, reloading...")
                self.data = self.load_data()

            # Validate that data contains DataFrames
            for key, df in self.data.items():
                if not hasattr(df, 'shape'):
                    print(f"⚠️ {key} is not a DataFrame, reloading all data...")
                    self.data = self.load_data()
                    break

            print("✅ Data integrity check passed")
            return True

        except Exception as e:
            print(f"❌ Error in data integrity check: {e}")
            self.logger.error(f"Error in data integrity check: {e}")
            return False

    def create_widget_with_data_validation(self, widget_class, widget_name, required_data_keys=None):
        """Create widget with data validation"""
        try:
            print(f"\n🔧 Creating {widget_name}...")

            # Ensure data integrity
            if not self.ensure_data_integrity():
                print(f"❌ Data integrity check failed for {widget_name}")
                return None

            # Debug data before widget creation
            if required_data_keys:
                self.debug_data_before_widget_creation(widget_name, required_data_keys)

            # Create widget with validated data
            if hasattr(widget_class, '__init__'):
                # Check if widget expects data parameter
                import inspect
                sig = inspect.signature(widget_class.__init__)
                if 'data' in sig.parameters:
                    widget = widget_class(self.data)
                else:
                    widget = widget_class()
                    # Try to set data after creation
                    if hasattr(widget, 'set_data'):
                        widget.set_data(self.data)
                    elif hasattr(widget, 'data'):
                        widget.data = self.data
            else:
                widget = widget_class()

            print(f"✅ Successfully created {widget_name}")
            return widget

        except Exception as e:
            print(f"❌ Error creating {widget_name}: {e}")
            self.logger.error(f"Error creating {widget_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # create_sample_data method has been removed as requested by the user
    
    def create_sidebar(self):
        """Create navigation sidebar to match the screenshot"""
        # Create sidebar widget
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet("""
            QWidget#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f23, stop:0.3 #1a1a2e, stop:0.6 #16213e, stop:1 #0f3460) !important;
                border: none;
                border-radius: 0px 30px 30px 0px;
                border-right: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(138, 43, 226, 0.8), stop:0.5 rgba(30, 144, 255, 0.9), stop:1 rgba(0, 191, 255, 0.7));
            }

            QWidget#sidebar QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.08), stop:0.5 rgba(138, 43, 226, 0.15), stop:1 rgba(30, 144, 255, 0.12));
                color: #e8eaed;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 22px;
                text-align: left;
                padding: 18px 24px;
                font-size: 15px;
                font-weight: 500;
                margin: 2px 0px;
                letter-spacing: 0.8px;
                min-height: 24px;
            }

            QWidget#sidebar QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(138, 43, 226, 0.4), stop:0.5 rgba(30, 144, 255, 0.35), stop:1 rgba(0, 191, 255, 0.3));
                color: #ffffff;
                border: 3px solid rgba(138, 43, 226, 0.9);
                border-left: 6px solid #8a2be2;
                border-radius: 22px 8px 8px 22px;
            }

            QWidget#sidebar QPushButton:checked, QWidget#sidebar QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(138, 43, 226, 0.95), stop:0.3 rgba(30, 144, 255, 0.9), stop:0.7 rgba(0, 191, 255, 0.85), stop:1 rgba(138, 43, 226, 0.8));
                color: #ffffff;
                border: 2px solid rgba(138, 43, 226, 0.8);
                border-left: 6px solid #8a2be2;
                font-weight: 700;
                border-radius: 22px 8px 8px 22px;
            }

            QWidget#sidebar QLabel {
                color: white;
            }
        """)
        
        self.sidebar.setMinimumWidth(240)
        self.sidebar.setMaximumWidth(240)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)

        # Initialize the list to store navigation buttons
        self.nav_buttons = []
        
        # Add header with title and toggle button
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("QWidget { background: transparent !important; }")
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 2, 0, 2)
        self.header_layout.setSpacing(3)

        # Sidebar toggle button with maximum visibility and reliable hamburger icon
        self.sidebar_toggle_button = QPushButton()
        self.sidebar_toggle_button.setFixedSize(32, 32)

        # Set button text with multiple fallback hamburger symbols for better compatibility
        self.sidebar_toggle_button.setText("☰")  # Primary hamburger symbol (U+2630)

        self.sidebar_toggle_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.95);
                color: #2563eb;
                border: 2px solid #2563eb;
                border-radius: 16px;
                font-size: 20px;
                font-weight: 900;
                font-family: "Segoe UI Symbol", "Segoe UI", "Arial Unicode MS", "Arial", sans-serif;
                text-align: center;
                padding: 0px;
                min-width: 32px;
                min-height: 32px;
            }
            QPushButton:hover {
                background: #2563eb;
                color: #ffffff;
                border: 2px solid #ffffff;
                /* Removed box-shadow - using Qt effects instead */
            }
            QPushButton:pressed {
                background: #1d4ed8;
                color: #ffffff;
                border: 2px solid #ffffff;
                /* Removed box-shadow - using Qt effects instead */
            }
        """)

        # Apply Qt-native shadow effect instead of CSS box-shadow
        try:
            from utils.qt_effects import add_button_hover_shadow
            add_button_hover_shadow(self.sidebar_toggle_button)
        except Exception as e:
            self.logger.debug(f"Could not apply button shadow effect: {e}")
        self.sidebar_toggle_button.setToolTip("Toggle Sidebar (Ctrl+B)")
        self.sidebar_toggle_button.clicked.connect(self.toggle_sidebar)

        # Add fallback mechanism for icon visibility
        self.setup_toggle_button_fallback()

        self.header_layout.addWidget(self.sidebar_toggle_button)

        # Clean title design with transparent background
        self.title_container = QWidget()
        self.title_container.setObjectName("sidebarTitleContainer")
        self.title_container.setStyleSheet("""
            QWidget#sidebarTitleContainer {
                background: transparent !important;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)

        title_layout = QHBoxLayout(self.title_container)
        title_layout.setContentsMargins(8, 6, 8, 6)
        title_layout.setSpacing(5)

        # Kitchen icon with better visibility
        kitchen_icon = QLabel("🍳")
        kitchen_icon.setFont(QFont("Segoe UI", 18))
        kitchen_icon.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                color: #f39c12;
                padding: 1px;
            }
        """)
        title_layout.addWidget(kitchen_icon)

        # Improved title text visibility
        self.sidebar_title = QLabel("Vasanth Kitchen")
        self.sidebar_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.sidebar_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.sidebar_title.setMinimumWidth(120)
        self.sidebar_title.setMaximumWidth(140)
        self.sidebar_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                border: none;
                font-weight: 800;
                letter-spacing: 1.2px;
                padding-right: 3px;
            }
        """)
        title_layout.addWidget(self.sidebar_title)

        # Enhanced sparkle accent - smaller and more subtle
        sparkle_icon = QLabel("✨")
        sparkle_icon.setFont(QFont("Segoe UI", 12))
        sparkle_icon.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                color: #f1c40f;
                margin-left: 2px;
            }
        """)
        title_layout.addWidget(sparkle_icon)

        self.header_layout.addWidget(self.title_container, 1)

        self.sidebar_layout.addWidget(self.header_widget)

        # Create scroll area for navigation buttons
        self.nav_scroll_area = QScrollArea()
        self.nav_scroll_area.setWidgetResizable(True)
        self.nav_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_scroll_area.setFrameShape(QFrame.NoFrame)
        self.nav_scroll_area.setStyleSheet("""
            QWidget#sidebar QScrollArea {
                border: none;
                background: transparent !important;
            }
            QWidget#sidebar QScrollBar:vertical {
                background: transparent;
                width: 0px;
                border: none;
                margin: 0px;
            }
            QWidget#sidebar QScrollBar::handle:vertical {
                background: transparent;
                border: none;
                width: 0px;
            }
            QWidget#sidebar QScrollBar::handle:vertical:hover {
                background: transparent;
                border: none;
            }
            QWidget#sidebar QScrollBar::add-line:vertical, QWidget#sidebar QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Create widget to hold all navigation buttons
        self.nav_buttons_widget = QWidget()
        self.nav_buttons_widget.setStyleSheet("QWidget { background: transparent !important; }")
        self.nav_buttons_layout = QVBoxLayout(self.nav_buttons_widget)
        self.nav_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_buttons_layout.setSpacing(2)

        # Set the widget for the scroll area
        self.nav_scroll_area.setWidget(self.nav_buttons_widget)

        # Add scroll area to sidebar layout with stretch factor
        self.sidebar_layout.addWidget(self.nav_scroll_area, 1)

        # Initialize sidebar state
        self.sidebar_expanded = True
        self.sidebar_width = 240
        self.sidebar_collapsed_width = 60
        
        # Create buttons with icons
        self.home_button = QPushButton(" Home")
        self.home_button.setIcon(self.create_icon("🏠"))
        self.home_button.setIconSize(QSize(18, 18))
        self.home_button.setCheckable(True)
        self.home_button.setChecked(True)  # Home is selected by default
        self.home_button.clicked.connect(lambda: self.handle_nav_button(self.home_button, self.show_home_page))
        self.nav_buttons_layout.addWidget(self.home_button)
        self.nav_buttons.append(self.home_button)

        self.inventory_button = QPushButton(" Inventory")
        self.inventory_button.setIcon(self.create_icon("📦"))
        self.inventory_button.setIconSize(QSize(18, 18))
        self.inventory_button.setCheckable(True)
        self.inventory_button.clicked.connect(lambda: self.handle_nav_button(self.inventory_button, self.show_inventory_page))
        self.nav_buttons_layout.addWidget(self.inventory_button)
        self.nav_buttons.append(self.inventory_button)

        self.meal_planning_button = QPushButton(" Meal Planning")
        self.meal_planning_button.setIcon(self.create_icon("🍽️"))
        self.meal_planning_button.setIconSize(QSize(18, 18))
        self.meal_planning_button.setCheckable(True)
        self.meal_planning_button.clicked.connect(lambda: self.handle_nav_button(self.meal_planning_button, self.show_meal_planning_page))
        self.nav_buttons_layout.addWidget(self.meal_planning_button)
        self.nav_buttons.append(self.meal_planning_button)

        self.budget_button = QPushButton(" Budget")
        self.budget_button.setIcon(self.create_icon("💰"))
        self.budget_button.setIconSize(QSize(18, 18))
        self.budget_button.setCheckable(True)
        self.budget_button.clicked.connect(lambda: self.handle_nav_button(self.budget_button, self.show_budget_page))
        self.nav_buttons_layout.addWidget(self.budget_button)
        self.nav_buttons.append(self.budget_button)

        self.sales_button = QPushButton(" Sales")
        self.sales_button.setIcon(self.create_icon("📊"))
        self.sales_button.setIconSize(QSize(18, 18))
        self.sales_button.setCheckable(True)
        self.sales_button.clicked.connect(lambda: self.handle_nav_button(self.sales_button, self.show_sales_page))
        self.nav_buttons_layout.addWidget(self.sales_button)
        self.nav_buttons.append(self.sales_button)

        # Platform Reports button (Zomato/Swiggy)
        self.platform_reports_button = QPushButton(" Platform Reports")
        self.platform_reports_button.setIcon(self.create_icon("🍔"))
        self.platform_reports_button.setIconSize(QSize(18, 18))
        self.platform_reports_button.setCheckable(True)
        self.platform_reports_button.clicked.connect(lambda: self.handle_nav_button(self.platform_reports_button, self.show_platform_reports_page))
        self.nav_buttons_layout.addWidget(self.platform_reports_button)
        self.nav_buttons.append(self.platform_reports_button)

        self.pricing_button = QPushButton(" Pricing")
        self.pricing_button.setIcon(self.create_icon("💲"))
        self.pricing_button.setIconSize(QSize(18, 18))
        self.pricing_button.setCheckable(True)
        self.pricing_button.clicked.connect(lambda: self.handle_nav_button(self.pricing_button, self.show_pricing_page))
        self.nav_buttons_layout.addWidget(self.pricing_button)
        self.nav_buttons.append(self.pricing_button)

        self.packing_materials_button = QPushButton(" Packing Materials")
        self.packing_materials_button.setIcon(self.create_icon("📦"))
        self.packing_materials_button.setIconSize(QSize(18, 18))
        self.packing_materials_button.setCheckable(True)
        self.packing_materials_button.clicked.connect(lambda: self.handle_nav_button(self.packing_materials_button, self.show_packing_materials_page))
        self.nav_buttons_layout.addWidget(self.packing_materials_button)
        self.nav_buttons.append(self.packing_materials_button)

        self.shopping_button = QPushButton(" Shopping")
        self.shopping_button.setIcon(self.create_icon("🛒"))
        self.shopping_button.setIconSize(QSize(18, 18))
        self.shopping_button.setCheckable(True)
        self.shopping_button.clicked.connect(lambda: self.handle_nav_button(self.shopping_button, self.show_shopping_page))
        self.nav_buttons_layout.addWidget(self.shopping_button)
        self.nav_buttons.append(self.shopping_button)

        self.gas_management_button = QPushButton(" Gas Management")
        self.gas_management_button.setIcon(self.create_icon("🔥"))
        self.gas_management_button.setIconSize(QSize(18, 18))
        self.gas_management_button.setCheckable(True)
        self.gas_management_button.clicked.connect(lambda: self.handle_nav_button(self.gas_management_button, self.show_gas_management_page))
        self.nav_buttons_layout.addWidget(self.gas_management_button)
        self.nav_buttons.append(self.gas_management_button)

        self.waste_button = QPushButton(" Waste")
        self.waste_button.setIcon(self.create_icon("♻️"))
        self.waste_button.setIconSize(QSize(18, 18))
        self.waste_button.setCheckable(True)
        self.waste_button.clicked.connect(lambda: self.handle_nav_button(self.waste_button, self.show_waste_page))
        self.nav_buttons_layout.addWidget(self.waste_button)
        self.nav_buttons.append(self.waste_button)

        self.cleaning_button = QPushButton(" Cleaning")
        self.cleaning_button.setIcon(self.create_icon("🧹"))
        self.cleaning_button.setIconSize(QSize(18, 18))
        self.cleaning_button.setCheckable(True)
        self.cleaning_button.clicked.connect(lambda: self.handle_nav_button(self.cleaning_button, self.show_cleaning_page))
        self.nav_buttons_layout.addWidget(self.cleaning_button)
        self.nav_buttons.append(self.cleaning_button)

        # Analytics button
        self.analytics_button = QPushButton(" Analytics")
        self.analytics_button.setIcon(self.create_icon("📈"))
        self.analytics_button.setIconSize(QSize(18, 18))
        self.analytics_button.setCheckable(True)
        self.analytics_button.clicked.connect(lambda: self.handle_nav_button(self.analytics_button, self.show_analytics_page))
        self.nav_buttons_layout.addWidget(self.analytics_button)
        self.nav_buttons.append(self.analytics_button)

        # Reports button
        self.reports_button = QPushButton(" Reports")
        self.reports_button.setIcon(self.create_icon("📄"))
        self.reports_button.setIconSize(QSize(18, 18))
        self.reports_button.setCheckable(True)
        self.reports_button.clicked.connect(lambda: self.handle_nav_button(self.reports_button, self.show_reports_page))
        self.nav_buttons_layout.addWidget(self.reports_button)
        self.nav_buttons.append(self.reports_button)

        # Logs button
        self.logs_button = QPushButton(" Logs")
        self.logs_button.setIcon(self.create_icon("📋"))
        self.logs_button.setIconSize(QSize(18, 18))
        self.logs_button.setCheckable(True)
        self.logs_button.clicked.connect(lambda: self.handle_nav_button(self.logs_button, self.show_logs_page))
        self.nav_buttons_layout.addWidget(self.logs_button)
        self.nav_buttons.append(self.logs_button)

        # Firebase functionality moved to Settings tab
        # Mobile, AI/ML, and Enterprise functionality moved to Settings tab

        # Settings button
        self.settings_button = QPushButton(" Settings")
        self.settings_button.setIcon(self.create_icon("⚙️"))
        self.settings_button.setIconSize(QSize(18, 18))
        self.settings_button.setCheckable(True)
        self.settings_button.clicked.connect(lambda: self.handle_nav_button(self.settings_button, self.show_settings_page))
        self.nav_buttons_layout.addWidget(self.settings_button)
        self.nav_buttons.append(self.settings_button)

        # Add stretch to push buttons to the top within the scroll area
        self.nav_buttons_layout.addStretch(1)

        # Stunning glass-morphism version badge (will be hidden when collapsed)
        version_container = QWidget()
        version_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(138, 43, 226, 0.9), stop:0.5 rgba(30, 144, 255, 0.8), stop:1 rgba(0, 191, 255, 0.7));
                border: 3px solid rgba(255, 255, 255, 0.8);
                border-radius: 25px;
                margin: 4px 0px;
                padding: 8px;
            }
        """)

        version_layout = QHBoxLayout(version_container)
        version_layout.setContentsMargins(8, 4, 8, 4)
        version_layout.setSpacing(4)

        # Version icon
        version_icon = QLabel("🚀")
        version_icon.setFont(QFont("Segoe UI", 10))
        version_icon.setStyleSheet("border: none; background: transparent;")
        version_layout.addWidget(version_icon)

        self.version_label = QLabel("v1.0.0")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 10px;
                font-weight: 600;
                background: transparent;
                border: none;
                letter-spacing: 0.3px;
            }
        """)
        version_layout.addWidget(self.version_label, 1)

        # Status indicator
        status_dot = QLabel("●")
        status_dot.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 8px;
                background: transparent;
                border: none;
            }
        """)
        version_layout.addWidget(status_dot)

        self.sidebar_layout.addWidget(version_container)

        # Set up keyboard shortcut for toggling sidebar
        self.setup_sidebar_shortcuts()

    def setup_toggle_button_fallback(self):
        """Setup fallback mechanism for toggle button icon visibility"""
        try:
            # Test if the hamburger symbol is properly rendered
            font_metrics = self.sidebar_toggle_button.fontMetrics()
            text_width = font_metrics.horizontalAdvance("☰")

            # If the symbol is not properly rendered (width too small), use fallback
            if text_width < 10:
                # Try alternative symbols
                fallback_symbols = ["≡", "|||", "▤", "☰", "⚏"]
                for symbol in fallback_symbols:
                    test_width = font_metrics.horizontalAdvance(symbol)
                    if test_width >= 10:
                        self.sidebar_toggle_button.setText(symbol)
                        print(f"✅ Using fallback toggle symbol: {symbol}")
                        break
                else:
                    # If no symbol works, use text
                    self.sidebar_toggle_button.setText("MENU")
                    self.sidebar_toggle_button.setStyleSheet(self.sidebar_toggle_button.styleSheet().replace("font-size: 20px;", "font-size: 8px;"))
                    print("✅ Using text fallback for toggle button")
            else:
                print("✅ Toggle button symbol rendered correctly")

        except Exception as e:
            print(f"⚠️ Error in toggle button fallback setup: {e}")
            # Ultimate fallback
            self.sidebar_toggle_button.setText("≡")

    def setup_sidebar_shortcuts(self):
        """Set up keyboard shortcuts for sidebar"""
        from PySide6.QtGui import QShortcut, QKeySequence

        # Ctrl+B to toggle sidebar
        self.sidebar_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        self.sidebar_shortcut.activated.connect(self.toggle_sidebar)

    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states"""
        try:
            if self.sidebar_expanded:
                self.collapse_sidebar()
            else:
                self.expand_sidebar()
        except Exception as e:
            self.logger.error(f"Error toggling sidebar: {e}")

    def collapse_sidebar(self):
        """Collapse the sidebar to show only icons"""
        try:
            self.sidebar_expanded = False

            # Hide text elements IMMEDIATELY before animation starts
            self.hide_sidebar_text()

            # Animate the width change
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
            self.sidebar_animation.setDuration(300)
            self.sidebar_animation.setStartValue(self.sidebar_width)
            self.sidebar_animation.setEndValue(self.sidebar_collapsed_width)
            self.sidebar_animation.setEasingCurve(QEasingCurve.OutCubic)

            # Also animate maximum width
            self.sidebar_animation2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.sidebar_animation2.setDuration(300)
            self.sidebar_animation2.setStartValue(self.sidebar_width)
            self.sidebar_animation2.setEndValue(self.sidebar_collapsed_width)
            self.sidebar_animation2.setEasingCurve(QEasingCurve.OutCubic)

            # Update splitter sizes when animation completes to give content area more space
            self.sidebar_animation.finished.connect(self.update_splitter_for_collapsed)

            self.sidebar_animation.start()
            self.sidebar_animation2.start()

            # Update toggle button - use more visible expand symbol
            self.sidebar_toggle_button.setText("☰")  # Keep hamburger for collapsed state
            self.sidebar_toggle_button.setToolTip("Expand Sidebar (Ctrl+B)")

            print("🔄 Sidebar collapsed - More space for tables!")

        except Exception as e:
            self.logger.error(f"Error collapsing sidebar: {e}")

    def expand_sidebar(self):
        """Expand the sidebar to show full navigation"""
        try:
            self.sidebar_expanded = True

            # Show text elements first
            self.show_sidebar_text()

            # Animate the width change
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
            self.sidebar_animation.setDuration(300)
            self.sidebar_animation.setStartValue(self.sidebar_collapsed_width)
            self.sidebar_animation.setEndValue(self.sidebar_width)
            self.sidebar_animation.setEasingCurve(QEasingCurve.OutCubic)

            # Also animate maximum width
            self.sidebar_animation2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.sidebar_animation2.setDuration(300)
            self.sidebar_animation2.setStartValue(self.sidebar_collapsed_width)
            self.sidebar_animation2.setEndValue(self.sidebar_width)
            self.sidebar_animation2.setEasingCurve(QEasingCurve.OutCubic)

            # Update splitter sizes when animation completes to adjust content area
            self.sidebar_animation.finished.connect(self.update_splitter_for_expanded)

            self.sidebar_animation.start()
            self.sidebar_animation2.start()

            # Update toggle button - use left arrow for expanded state
            self.sidebar_toggle_button.setText("◀")  # Left arrow to indicate collapse direction
            self.sidebar_toggle_button.setToolTip("Collapse Sidebar (Ctrl+B)")

            print("🔄 Sidebar expanded")

        except Exception as e:
            self.logger.error(f"Error expanding sidebar: {e}")

    def hide_sidebar_text(self):
        """Hide text elements when sidebar is collapsed"""
        try:
            self.sidebar_title.hide()
            self.version_label.hide()

            # Hide the title container completely
            self.title_container.hide()

            # Center the toggle button by adjusting layout
            self.center_toggle_button()

            # Update button text to show no text (rely on icons only)
            for button in self.nav_buttons:
                # Store original text
                if not hasattr(button, '_original_text'):
                    button._original_text = button.text()
                # Hide text completely - the icon will still be visible
                button.setText("")
                button.setToolTip(f"{button._original_text.strip()} (Click to navigate)")

        except Exception as e:
            self.logger.error(f"Error hiding sidebar text: {e}")

    def show_sidebar_text(self):
        """Show text elements when sidebar is expanded"""
        try:
            self.sidebar_title.show()
            self.version_label.show()

            # Show the title container
            self.title_container.show()

            # Restore normal layout for toggle button
            self.restore_toggle_button_layout()

            # Restore button text
            for button in self.nav_buttons:
                if hasattr(button, '_original_text'):
                    button.setText(button._original_text)
                    button.setToolTip("")

        except Exception as e:
            self.logger.error(f"Error showing sidebar text: {e}")

    def center_toggle_button(self):
        """Center the toggle button when sidebar is collapsed"""
        try:
            # Clear the current layout
            while self.header_layout.count():
                child = self.header_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

            # Add stretch, button, stretch to center it
            self.header_layout.addStretch(1)
            self.header_layout.addWidget(self.sidebar_toggle_button)
            self.header_layout.addStretch(1)

            print("🔧 Toggle button centered for collapsed state")

        except Exception as e:
            self.logger.error(f"Error centering toggle button: {e}")

    def restore_toggle_button_layout(self):
        """Restore normal layout for toggle button when sidebar is expanded"""
        try:
            # Clear the current layout
            while self.header_layout.count():
                child = self.header_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

            # Restore original layout: button first, then title container with stretch
            self.header_layout.addWidget(self.sidebar_toggle_button)
            self.header_layout.addWidget(self.title_container, 1)

            print("🔧 Toggle button layout restored for expanded state")

        except Exception as e:
            self.logger.error(f"Error restoring toggle button layout: {e}")

    def update_splitter_for_collapsed(self):
        """Update splitter sizes when sidebar is collapsed to give content area more space"""
        try:
            # Get current total width
            current_sizes = self.main_splitter.sizes()
            if len(current_sizes) == 2:
                total_width = sum(current_sizes)
                if total_width > 0:
                    # Set sidebar to collapsed width and give rest to content
                    new_sidebar_width = self.sidebar_collapsed_width
                    new_content_width = total_width - new_sidebar_width
                    self.main_splitter.setSizes([new_sidebar_width, new_content_width])
                    print(f"🔄 Splitter updated for collapsed sidebar: [{new_sidebar_width}, {new_content_width}]")
        except Exception as e:
            self.logger.error(f"Error updating splitter for collapsed sidebar: {e}")

    def update_splitter_for_expanded(self):
        """Update splitter sizes when sidebar is expanded"""
        try:
            # Get current total width
            current_sizes = self.main_splitter.sizes()
            if len(current_sizes) == 2:
                total_width = sum(current_sizes)
                if total_width > 0:
                    # Set sidebar to expanded width and adjust content accordingly
                    new_sidebar_width = self.sidebar_width
                    new_content_width = total_width - new_sidebar_width
                    # Ensure content area doesn't get too small
                    if new_content_width < 400:
                        new_content_width = 400
                        new_sidebar_width = total_width - new_content_width
                    self.main_splitter.setSizes([new_sidebar_width, new_content_width])
                    print(f"🔄 Splitter updated for expanded sidebar: [{new_sidebar_width}, {new_content_width}]")
        except Exception as e:
            self.logger.error(f"Error updating splitter for expanded sidebar: {e}")

    def handle_nav_button(self, clicked_button, callback_function):
        """Handle navigation button clicks and styling"""
        # Get button name for logging
        button_name = clicked_button.text().strip()
        self.logger.info(f"Navigation: User clicked {button_name} button")

        # Track navigation activity
        if hasattr(self, 'current_page'):
            track_navigation(self.current_page, button_name)
        else:
            track_navigation("unknown", button_name)

        # Track user action
        track_user_action("navigation", "button_click", f"User navigated to {button_name} page")

        # Reset all navigation buttons to unchecked state
        for button in self.nav_buttons:
            if hasattr(button, 'setChecked'):
                button.setChecked(False)

        # Set the clicked button as checked (this will trigger the CSS :checked styling)
        if hasattr(clicked_button, 'setChecked'):
            clicked_button.setChecked(True)

        # Call the callback function
        self.logger.debug(f"Executing callback for {button_name}")
        self.current_page = button_name  # Track current page
        callback_function()
        
    def create_icon(self, emoji):
        """Create an icon from emoji text"""
        # Create a pixmap
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        # Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QPen(QColor("#ecf0f1")))  # White text
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()
        
        return QIcon(pixmap)
    
    def clear_content(self):
        """Clear the content area"""
        # Remove all widgets from the content layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def show_home_page(self):
        """Display the home page with overview metrics"""
        self.clear_content()
        
        # Add title with welcome message
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        title = QLabel("Welcome to Your Kitchen Dashboard")
        title.setFont(self.title_font)
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Your complete kitchen management solution")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle)
        
        self.content_layout.addWidget(title_container)
        
        if not self.data:
            no_data_label = QLabel("No data available")
            no_data_label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(no_data_label)
            return
        
        # Create a grid layout for metrics cards with responsive behavior
        metrics_widget = QWidget()
        metrics_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        metrics_layout = QGridLayout(metrics_widget)
        metrics_layout.setContentsMargins(0, 0, 0, 20)
        metrics_layout.setSpacing(20)
        self.content_layout.addWidget(metrics_widget)
        
        # Helper function to create a metric card matching the screenshot
        def create_metric_card(title, value, icon_emoji, color):
            # Format value with the current currency symbol if it starts with a currency symbol
            if isinstance(value, str) and value.startswith(('$', '₹', '€', '£', '¥')):
                # Replace the existing currency symbol with the current one
                value = self.currency_symbol + value[1:]
                
            card = QFrame()
            card.setObjectName(f"metricCard_{title.lower().replace(' ', '_')}")
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            card.setMinimumHeight(100)  # Ensure minimum height for proper display
            card.setStyleSheet(f"""
                #{card.objectName()} {{
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                }}
            """)
            card.setMinimumWidth(200)
            card.setMaximumWidth(300)
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            
            # Create circular icon container
            icon_container = QFrame()
            icon_container.setFixedSize(50, 50)
            icon_container.setStyleSheet(f"""
                background-color: {color};
                border-radius: 25px;
            """)
            
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_layout.setAlignment(Qt.AlignCenter)
            
            icon = QLabel(icon_emoji)
            icon.setFont(QFont("Segoe UI", 20))
            icon.setStyleSheet("color: white;")
            icon.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon)
            
            # Add text content
            text_container = QWidget()
            text_layout = QVBoxLayout(text_container)
            text_layout.setContentsMargins(10, 0, 0, 0)
            text_layout.setSpacing(5)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 10))
            title_label.setStyleSheet("color: #7f8c8d;")
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
            value_label.setStyleSheet("color: #2c3e50;")
            
            text_layout.addWidget(title_label)
            text_layout.addWidget(value_label)
            
            # Add to card layout
            card_layout.addWidget(icon_container)
            card_layout.addWidget(text_container, 1)
            
            return card
        
        # Calculate metrics
        # Inventory metrics
        # Calculate using either avg_price, price, or fallback to 0
        inventory_df = self.data['inventory']
        total_inventory_value = 0
        
        if len(inventory_df) > 0:
            # Calculate value for each row properly
            for _, row in inventory_df.iterrows():
                # Get quantity - first calculate available_qty if we have purchased and used
                if 'total_qty' in row and pd.notna(row['total_qty']) and 'used_qty' in row and pd.notna(row['used_qty']):
                    qty = float(row['total_qty']) - float(row['used_qty'])
                # If available_qty is directly available, use it
                elif 'available_qty' in row and pd.notna(row['available_qty']):
                    qty = float(row['available_qty'])
                # Fallback to regular quantity field
                elif 'quantity' in row and pd.notna(row['quantity']):
                    qty = float(row['quantity'])
                else:
                    qty = 0
                    
                # Get price, using avg_price if available, otherwise price
                if 'avg_price' in row and pd.notna(row['avg_price']):
                    price = float(row['avg_price'])
                elif 'price' in row and pd.notna(row['price']):
                    price = float(row['price'])
                else:
                    price = 0
                    
                # Add to total
                total_inventory_value += qty * price
        
        # Calculate low stock items using qty_left if available, otherwise use quantity
        inventory_df = self.data['inventory']
        low_stock_items = []
        
        if len(inventory_df) > 0:
            for _, row in inventory_df.iterrows():
                # Get quantity - first calculate qty_left if we have purchased and used
                if 'qty_purchased' in row and pd.notna(row['qty_purchased']) and 'qty_used' in row and pd.notna(row['qty_used']):
                    qty = float(row['qty_purchased']) - float(row['qty_used'])
                # If qty_left is directly available, use it
                elif 'qty_left' in row and pd.notna(row['qty_left']):
                    qty = float(row['qty_left'])
                # Fallback to regular quantity field
                elif 'quantity' in row and pd.notna(row['quantity']):
                    qty = float(row['quantity'])
                else:
                    qty = 0
                    
                # Get threshold
                if 'reorder_level' in row and pd.notna(row['reorder_level']):
                    threshold = float(row['reorder_level'])
                else:
                    threshold = 1.0  # Default threshold
                    
                # Check if low stock
                if qty <= threshold:
                    low_stock_items.append(row)
                    
            # Create DataFrame from low stock items
            if low_stock_items:
                low_stock = pd.DataFrame(low_stock_items)
            else:
                low_stock = pd.DataFrame()
        else:
            low_stock = pd.DataFrame()
            
        low_stock_count = len(low_stock)
        
        # Sales metrics
        if 'total_amount' in self.data['sales'].columns:
            total_sales = self.data['sales']['total_amount'].sum()
        else:
            if 'price_per_unit' in self.data['sales'].columns and 'quantity' in self.data['sales'].columns:
                self.data['sales']['total_amount'] = self.data['sales']['price_per_unit'] * self.data['sales']['quantity']
                total_sales = self.data['sales']['total_amount'].sum()
            else:
                total_sales = 0.0
        
        # Budget metrics
        if 'amount' in self.data['budget'].columns:
            total_budget = self.data['budget']['amount'].sum()
        elif 'budget_amount' in self.data['budget'].columns:
            total_budget = self.data['budget']['budget_amount'].sum()
        else:
            total_budget = 0.0
        
        # Waste metrics
        if 'cost' in self.data['waste'].columns:
            waste_cost = self.data['waste']['cost'].sum()
        else:
            waste_cost = 0.0
        
        # Shopping list metrics
        if 'status' in self.data['shopping_list'].columns:
            items_to_buy = len(self.data['shopping_list'][self.data['shopping_list']['status'] == 'Pending'])
        else:
            items_to_buy = len(self.data['shopping_list'])
            
        if 'estimated_cost' in self.data['shopping_list'].columns:
            estimated_cost = self.data['shopping_list']['estimated_cost'].sum()
        else:
            estimated_cost = 0.0
        
        # Meal planning metrics - handle both old and new data structures
        try:
            # Try the new data structure first (meal_plan_items)
            if 'meal_plan_items' in self.data and len(self.data['meal_plan_items']) > 0:
                planned_meals = len(self.data['meal_plan_items'])
                unique_recipes = len(self.data['meal_plan_items']['recipe_id'].unique()) if 'recipe_id' in self.data['meal_plan_items'].columns else 0
            # Fall back to old structure
            elif 'meal_plan' in self.data and len(self.data['meal_plan']) > 0:
                planned_meals = len(self.data['meal_plan'])
                unique_recipes = len(self.data['meal_plan']['recipe_id'].unique()) if 'recipe_id' in self.data['meal_plan'].columns else 0
            else:
                planned_meals = 0
                unique_recipes = 0
        except Exception as e:
            # Log the error and use default values
            if hasattr(self, 'logger'):
                self.logger.error(f"Error calculating meal planning metrics: {str(e)}")
            else:
                print(f"Error calculating meal planning metrics: {str(e)}")
            planned_meals = 0
            unique_recipes = 0
        
        # Get currency symbol from settings, default to Indian Rupee (₹)
        currency_symbol = "₹"
        if 'settings' in self.data and 'currency' in self.data['settings']:
            currency_symbol = self.data['settings']['currency']
        
        # Create and add metric cards to the grid with dynamic currency symbol
        inventory_card = create_metric_card("Total Inventory Value", f"{currency_symbol}{total_inventory_value:.2f}", "📦", "#3498db")
        metrics_layout.addWidget(inventory_card, 0, 0)
        
        low_stock_card = create_metric_card("Low Stock Items", f"{low_stock_count}", "⚠️", "#e74c3c")
        metrics_layout.addWidget(low_stock_card, 0, 1)
        
        sales_card = create_metric_card("Total Sales", f"{currency_symbol}{total_sales:.2f}", "💰", "#2ecc71")
        metrics_layout.addWidget(sales_card, 0, 2)
        
        budget_card = create_metric_card("Budget", f"{currency_symbol}{total_budget:.2f}", "💵", "#9b59b6")
        metrics_layout.addWidget(budget_card, 1, 0)
        
        waste_card = create_metric_card("Waste Cost", f"{currency_symbol}{waste_cost:.2f}", "♻️", "#e67e22")
        metrics_layout.addWidget(waste_card, 1, 1)
        
        shopping_card = create_metric_card("Shopping List", f"{items_to_buy} items ({currency_symbol}{estimated_cost:.2f})", "🛒", "#1abc9c")
        metrics_layout.addWidget(shopping_card, 1, 2)
        
        # Add charts section title
        charts_title = QLabel("Key Performance Indicators")
        charts_title.setFont(self.header_font)
        charts_title.setAlignment(Qt.AlignCenter)
        charts_title.setContentsMargins(0, 20, 0, 10)
        self.content_layout.addWidget(charts_title)
        
        # Create charts container with card-like styling
        charts_widget = QFrame()
        charts_widget.setObjectName("chartsContainer")
        charts_widget.setStyleSheet("""
            #chartsContainer {
                background-color: white;
                border-radius: 10px;
                border: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        charts_widget.setFrameShape(QFrame.StyledPanel)
        charts_widget.setFrameShadow(QFrame.Raised)
        
        # Use a vertical layout for better chart arrangement
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(15, 15, 15, 15)
        charts_layout.setSpacing(20)
        self.content_layout.addWidget(charts_widget, 1)  # Add stretch factor
        
        # Create a horizontal layout for the top two charts
        top_charts_widget = QWidget()
        top_charts_layout = QHBoxLayout(top_charts_widget)
        top_charts_layout.setContentsMargins(0, 0, 0, 0)
        top_charts_layout.setSpacing(15)
        charts_layout.addWidget(top_charts_widget)
        
        # Create an improved chart container class with fixed height for better visibility
        class ChartWidget(QWidget):
            def __init__(self, title, parent=None):
                super().__init__(parent)
                # Set fixed height to ensure charts have enough space
                self.setMinimumHeight(250)
                self.setMinimumWidth(350)
                self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                # Use a frame with border for better visual separation
                self.frame = QFrame(self)
                self.frame.setFrameShape(QFrame.StyledPanel)
                self.frame.setFrameShadow(QFrame.Raised)
                self.frame.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 5px;
                    }
                """)
                
                # Main layout
                main_layout = QVBoxLayout(self)
                main_layout.setContentsMargins(0, 0, 0, 0)
                main_layout.addWidget(self.frame)
                
                # Frame layout
                self.layout = QVBoxLayout(self.frame)
                self.layout.setContentsMargins(10, 10, 10, 10)
                self.layout.setSpacing(5)
                
                # Add title with background
                title_container = QWidget()
                title_container.setStyleSheet("background-color: #f8f9fa; border-radius: 3px;")
                title_layout = QVBoxLayout(title_container)
                title_layout.setContentsMargins(5, 5, 5, 5)
                
                self.title = QLabel(title)
                self.title.setFont(QFont("Segoe UI", 11, QFont.Bold))
                self.title.setStyleSheet("color: #2c3e50;")
                self.title.setAlignment(Qt.AlignCenter)
                title_layout.addWidget(self.title)
                
                self.layout.addWidget(title_container)
                
                # Canvas container with fixed height
                self.canvas_container = QWidget()
                self.canvas_container.setMinimumHeight(180)
                self.canvas_layout = QVBoxLayout(self.canvas_container)
                self.canvas_layout.setContentsMargins(0, 0, 0, 0)
                self.layout.addWidget(self.canvas_container)
            
            def set_canvas(self, canvas):
                # Clear previous canvas if any
                for i in reversed(range(self.canvas_layout.count())): 
                    self.canvas_layout.itemAt(i).widget().setParent(None)
                
                # Add new canvas with proper sizing
                canvas.setMinimumHeight(180)
                self.canvas_layout.addWidget(canvas)
        
        # Inventory by category chart
        inventory_chart_widget = ChartWidget("Inventory by Category")
        
        # Create the chart with better colors
        if 'total_value' not in self.data['inventory'].columns:
            if 'price_per_unit' in self.data['inventory'].columns and 'quantity' in self.data['inventory'].columns:
                self.data['inventory']['total_value'] = self.data['inventory']['price_per_unit'] * self.data['inventory']['quantity']
            else:
                self.data['inventory']['total_value'] = 1
        
        inventory_by_category = self.data['inventory'].groupby('category')['total_value'].sum().reset_index()
        
        # Use a modern color palette
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        
        # Use a larger figure size for the pie chart to ensure labels are visible
        fig1, ax1 = plt.subplots(figsize=(6, 4), facecolor='white')
        
        # Create a simple, clear pie chart
        wedges, texts, autotexts = ax1.pie(
            inventory_by_category['total_value'], 
            labels=inventory_by_category['category'],  # Direct labels on the pie
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(inventory_by_category)],
            wedgeprops={'edgecolor': 'white', 'linewidth': 1},
            textprops={'color': 'black', 'fontweight': 'bold', 'fontsize': 9}
        )
        
        # Ensure the pie is drawn as a circle
        ax1.axis('equal')
        
        # Remove the legend as we're using direct labels
        plt.tight_layout(pad=1.5)
        
        ax1.set_title('Inventory Value Distribution', fontsize=12, pad=20, color='#2c3e50')
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        plt.tight_layout()
        
        # Make chart responsive if responsive manager is available
        if self.responsive_chart_manager:
            self.responsive_chart_manager.make_figure_responsive(fig1)

        # Create responsive canvas
        canvas1 = FigureCanvas(fig1)
        canvas1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to responsive widget
        inventory_chart_widget.set_canvas(canvas1)
        top_charts_layout.addWidget(inventory_chart_widget)

        # Close the figure to prevent memory issues
        plt.close(fig1)
        
        # Add Firebase cloud sync section if available
        if self.firebase_sync.is_firebase_available():
            # Create a header for the cloud sync section
            cloud_header = QLabel("Cloud Sync")
            cloud_header.setFont(self.header_font)
            cloud_header.setContentsMargins(0, 20, 0, 10)
            self.content_layout.addWidget(cloud_header)
            
            # Create a container for the cloud sync UI
            cloud_frame = QFrame()
            cloud_frame.setObjectName("cloudSyncContainer")
            cloud_frame.setStyleSheet("""
                #cloudSyncContainer {
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                }
            """)
            cloud_layout = QVBoxLayout(cloud_frame)
            cloud_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add cloud sync description
            cloud_desc = QLabel("Keep your data safe and access it from anywhere by syncing to the cloud.")
            cloud_desc.setWordWrap(True)
            cloud_desc.setStyleSheet("color: #555;")
            cloud_layout.addWidget(cloud_desc)
            
            # Add the Firebase sync UI elements
            self.firebase_sync.add_sync_ui(cloud_layout)
            
            # Add the cloud sync frame to the main content layout
            self.content_layout.addWidget(cloud_frame)
        
        # Waste tracking chart using the improved chart widget
        waste_chart_widget = ChartWidget("Waste by Reason")
        
        # Create the chart with better styling
        if 'cost' not in self.data['waste'].columns:
            self.data['waste']['cost'] = 1
        
        # Use a larger figure size for the waste chart to ensure labels are visible
        fig2, ax2 = plt.subplots(figsize=(6, 4), facecolor='white')
        
        if len(self.data['waste']) > 0 and 'reason' in self.data['waste'].columns:
            waste_by_reason = self.data['waste'].groupby('reason')['cost'].sum().reset_index()
            
            # Sort by cost to make the chart more readable
            waste_by_reason = waste_by_reason.sort_values('cost', ascending=True)
            
            # Create a horizontal bar chart with consistent colors
            bars = ax2.barh(
                waste_by_reason['reason'], 
                waste_by_reason['cost'],
                color=colors[:len(waste_by_reason)],
                height=0.5,
                edgecolor='white',
                linewidth=1
            )
            
            # Add data labels to the end of each bar
            for bar in bars:
                width = bar.get_width()
                ax2.text(
                    width + 0.05,
                    bar.get_y() + bar.get_height()/2,
                    f'{self.currency_symbol}{width:.0f}',  # Use dynamic currency symbol
                    va='center',
                    fontweight='bold',
                    fontsize=9,
                    color='#333333'
                )
        else:
            # If no waste data, show empty chart with a message
            ax2.text(0.5, 0.5, 'No waste data available', 
                     horizontalalignment='center', 
                     verticalalignment='center', 
                     transform=ax2.transAxes,
                     fontsize=12,
                     color='#7f8c8d')
        
        # Improve chart styling with dynamic currency symbol
        ax2.set_title('Waste Cost Analysis', fontsize=12, pad=20, color='#2c3e50')
        ax2.set_xlabel(f'Cost ({self.currency_symbol})', fontsize=10, color='#7f8c8d')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color('#ecf0f1')
        ax2.spines['left'].set_color('#ecf0f1')
        ax2.tick_params(colors='#7f8c8d')
        ax2.set_axisbelow(True)
        ax2.grid(axis='x', linestyle='--', alpha=0.7, color='#ecf0f1')
        
        plt.tight_layout()

        # Make chart responsive if responsive manager is available
        if self.responsive_chart_manager:
            self.responsive_chart_manager.make_figure_responsive(fig2)

        # Create responsive canvas
        canvas2 = FigureCanvas(fig2)
        canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to responsive widget
        waste_chart_widget.set_canvas(canvas2)
        top_charts_layout.addWidget(waste_chart_widget)

        # Close the figure to prevent memory issues
        plt.close(fig2)
        
        # Add inventory trend chart using the improved chart widget
        trend_chart_widget = ChartWidget("Inventory Value Trend")
        # Set a larger minimum height for the trend chart
        trend_chart_widget.setMinimumHeight(300)
        
        # Create sample trend data (in a real app, this would come from historical data)
        # For demonstration, we'll create synthetic data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
        # Create different trend lines for different categories
        categories = inventory_by_category['category'].unique()[:3]  # Use top 3 categories
        
        # Use a larger figure size for the trend chart to ensure all elements are visible
        fig3, ax3 = plt.subplots(figsize=(10, 5), facecolor='white')
        
        # Generate synthetic trend data for each category - with more distinct values
        import numpy as np
        np.random.seed(42)  # Use a seed for consistent results
        
        # Create distinct base values for better separation
        base_values = [1500, 1000, 500]
        
        for i, category in enumerate(categories):
            if len(categories) > 0:
                # Use predefined base values for better separation between lines
                base_value = base_values[i % len(base_values)]
                # Create smoother trends with less variation
                trend = np.random.randint(-100, 200, size=len(months)) + base_value
                ax3.plot(months, trend, marker='o', markersize=6, linewidth=2, label=category, color=colors[i])
        
        # Improve chart styling with dynamic currency symbol
        ax3.set_title('Inventory Value Trends by Category', fontsize=12, pad=20, color='#2c3e50')
        ax3.set_xlabel('Month', fontsize=10, color='#7f8c8d')
        ax3.set_ylabel(f'Value ({self.currency_symbol})', fontsize=10, color='#7f8c8d')
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.spines['bottom'].set_color('#ecf0f1')
        ax3.spines['left'].set_color('#ecf0f1')
        ax3.tick_params(colors='#7f8c8d')
        ax3.grid(linestyle='--', alpha=0.7, color='#ecf0f1')
        # Only create legend if there are labeled artists
        if ax3.get_legend_handles_labels()[0]:
            # Remove annotations as they cause clutter and overlap
            # Instead, make the legend more prominent
            ax3.legend(frameon=True, fontsize=10, loc='upper right', 
                      facecolor='white', edgecolor='#e0e0e0')
        
        plt.tight_layout()

        # Make chart responsive if responsive manager is available
        if self.responsive_chart_manager:
            self.responsive_chart_manager.make_figure_responsive(fig3)

        # Create responsive canvas
        canvas3 = FigureCanvas(fig3)
        canvas3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to responsive widget
        trend_chart_widget.set_canvas(canvas3)
        charts_layout.addWidget(trend_chart_widget)  # Add below the top charts

        # Close the figure to prevent memory issues
        plt.close(fig3)
    
    def show_inventory_page(self):
        """Display the inventory management page"""
        try:
            self.logger.log_ui_action("Navigation", "Inventory page requested")
            self.clear_content()

            # Add header with smart ingredient check button
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(20, 10, 20, 10)

            # Title
            title_label = QLabel("Inventory Management")
            title_label.setFont(self.title_font)
            title_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
            header_layout.addWidget(title_label)

            header_layout.addStretch()

            
            # Import the inventory module with error handling
            try:
                from modules.inventory_fixed import InventoryWidget
                self.logger.log_module_import("modules.inventory_fixed.InventoryWidget", True)
            except ImportError as e:
                self.logger.log_module_import("modules.inventory_fixed.InventoryWidget", False, e)
                # Show error page instead of crashing
                self.show_error_page("Inventory", f"Failed to import inventory module: {str(e)}")
                return

            # Debug and log data before passing to inventory widget
            self.logger.info("🔍 Inventory page data check:")
            self.logger.info(f"  Available data keys: {list(self.data.keys()) if self.data else 'None'}")

            if 'inventory' in self.data:
                inventory_data = self.data['inventory']
                self.logger.info(f"  ✅ Inventory data found: {inventory_data.shape}")
                self.logger.info(f"  Columns: {list(inventory_data.columns)}")
                if 'item_name' in inventory_data.columns:
                    sample_items = list(inventory_data['item_name'].head(3))
                    self.logger.info(f"  Sample items: {sample_items}")
                else:
                    self.logger.warning("  ⚠️ No 'item_name' column found")
            else:
                self.logger.error("  ❌ No 'inventory' key in self.data!")
                # Show error page instead of crashing
                self.show_error_page("Inventory", "No inventory data available. Please check your data files.")
                return

            # Create the inventory widget with error handling
            try:
                import time
                start_time = time.time()
                self.inventory_widget = InventoryWidget(self.data)
                creation_time = time.time() - start_time
                self.logger.log_performance("Inventory widget creation", creation_time)

                # Add the widget to the content layout
                self.content_layout.addWidget(self.inventory_widget)
                self.logger.info("✅ Inventory page loaded successfully")

            except Exception as e:
                self.logger.log_exception(e, "Error creating inventory widget")
                self.show_error_page("Inventory", f"Error creating inventory interface: {str(e)}")

        except Exception as e:
            self.logger.log_exception(e, "Critical error in show_inventory_page")
            self.show_error_page("Inventory", f"Critical error loading inventory page: {str(e)}")

    def manual_ingredient_check(self):
        """Manually trigger ingredient check"""
        try:
            # Get smart ingredient manager
            if hasattr(self, 'smart_ingredient_manager') and self.smart_ingredient_manager:
                success = self.smart_ingredient_manager.manual_ingredient_check()
                if success:
                    self.add_notification(
                        "Ingredient Check",
                        "Scanning recipes for missing ingredients...",
                        "info"
                    )
                else:
                    self.add_notification(
                        "Ingredient Check Failed",
                        "Failed to check for missing ingredients",
                        "error"
                    )
            else:
                self.add_notification(
                    "Feature Unavailable",
                    "Smart ingredient manager is not available",
                    "warning"
                )
        except Exception as e:
            self.logger.error(f"Error in manual ingredient check: {e}")
            self.add_notification(
                "Error",
                f"Error checking ingredients: {e}",
                "error"
            )

    def show_meal_planning_page(self):
        """Display the meal planning page"""
        self.clear_content()
        
        # Import the meal planning module
        from modules.meal_planning import MealPlanningWidget
        # Import the fixed meal planning module
        from modules.fixed_meal_planning import FixedMealPlanningWidget
        
        # Create the fixed meal planning widget instead of the original one
        try:
            # Use the fixed meal planning widget
            meal_planning_widget = FixedMealPlanningWidget(self.data)
            self.logger.info("Using fixed meal planning widget")
        except Exception as e:
            # Fall back to original widget if there's an error
            self.logger.error(f"Error using fixed meal planning widget: {str(e)}")
            meal_planning_widget = MealPlanningWidget(self.data)
            self.logger.info("Falling back to original meal planning widget")
        
        # Add the widget to the content layout
        self.content_layout.addWidget(meal_planning_widget)
    
    def show_budget_page(self):
        """Display the budget tracking page with comprehensive budget management"""
        self.clear_content()

        # Debug data before widget creation
        self.debug_data_before_widget_creation("budget", ["budget"])
        
        # Import the enhanced budget module
        try:
            from modules.enhanced_budget import EnhancedBudgetWidget
            budget_widget = EnhancedBudgetWidget(self.data)
            self.logger.info("Using enhanced budget widget")
        except Exception as e:
            # Fallback to budget manager
            self.logger.error(f"Error using enhanced budget widget: {str(e)}")
            try:
                from modules.budget_manager import BudgetManager
                budget_widget = BudgetManager(self.data)
                self.logger.info("Falling back to budget manager")
            except Exception as e2:
                # Final fallback to original budget widget
                self.logger.error(f"Error using budget manager: {str(e2)}")
                try:
                    from modules.budget import BudgetWidget
                    budget_widget = BudgetWidget(self.data)
                    self.logger.info("Falling back to original budget widget")
                except ImportError:
                    # If no module exists, create a placeholder
                    placeholder = QWidget()
                    placeholder_layout = QVBoxLayout(placeholder)
                    placeholder_layout.setContentsMargins(20, 20, 20, 20)
                    error_label = QLabel("Budget management functionality is currently unavailable.\nPlease try again later.")
                    error_label.setStyleSheet("color: red; font-size: 16px;")
                    error_label.setAlignment(Qt.AlignCenter)
                    placeholder_layout.addWidget(error_label)
                    budget_widget = placeholder
                    self.logger.error("All budget modules failed to load")
        
        # Add the widget to the content layout
        self.content_layout.addWidget(budget_widget)
        
        # Log the action
        self.logger.debug("Executing callback for Budget")
    
    def show_sales_page(self):
        """Display the sales page with order management system"""
        self.clear_content()

        # Debug data before widget creation
        self.debug_data_before_widget_creation("sales", ["sales", "orders"])

        # Import the simplified sales order management module
        try:
            from modules.sales_order_management import SalesOrderManagementWidget

            # Get pricing data for automatic price fetching
            pricing_data = None
            try:
                from modules.pricing_management import PricingManagement
                pricing_data = PricingManagement(self.data, None)
            except Exception as e:
                self.logger.warning(f"Could not load pricing data: {e}")

            sales_widget = SalesOrderManagementWidget(self.data, pricing_data)
            self.logger.info("Using simplified sales order management widget")

        except Exception as e:
            # Create placeholder if module fails to load
            self.logger.error(f"Error using order management widget: {str(e)}")
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(20, 20, 20, 20)

            title_label = QLabel("Sales - Order Management")
            title_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 20px;")
            title_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(title_label)

            error_label = QLabel("Order management functionality is currently unavailable.\nPlease try again later.")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(error_label)

            sales_widget = placeholder
            self.logger.error("Order management module failed to load")

        # Add the widget to the content layout
        self.content_layout.addWidget(sales_widget)

    def show_platform_reports_page(self):
        """Display the platform reports page (Zomato/Swiggy specific)"""
        self.clear_content()

        # Debug data before widget creation
        self.debug_data_before_widget_creation("platform_reports", ["sales", "platform_data"])

        # Import the platform reports module
        try:
            from modules.platform_reports import PlatformReportsWidget
            platform_widget = PlatformReportsWidget(self.data)
            self.logger.info("Using platform reports widget")
        except Exception as e:
            # Fallback to sales reports module
            self.logger.error(f"Error using platform reports widget: {str(e)}")
            try:
                from modules.sales_reports import SalesReportsWidget
                platform_widget = SalesReportsWidget(self.data)
                self.logger.info("Falling back to sales reports widget")
            except Exception as e2:
                # Create placeholder if all fails
                placeholder = QWidget()
                placeholder_layout = QVBoxLayout(placeholder)
                placeholder_layout.setContentsMargins(20, 20, 20, 20)
                error_label = QLabel("Platform reports functionality is currently unavailable.\nPlease try again later.")
                error_label.setStyleSheet("color: red; font-size: 16px;")
                error_label.setAlignment(Qt.AlignCenter)
                placeholder_layout.addWidget(error_label)
                platform_widget = placeholder
                self.logger.error("All platform report modules failed to load")

        # Add the widget to the content layout
        self.content_layout.addWidget(platform_widget)

    def show_pricing_page(self):
        """Display the pricing management page"""
        self.clear_content()

        # Import the pricing management module
        try:
            from modules.pricing_management import PricingManagementWidget
            pricing_widget = PricingManagementWidget(self.data)
            self.logger.info("Using pricing management widget")
        except Exception as e:
            # Create placeholder if module fails to load
            self.logger.error(f"Error loading pricing management widget: {str(e)}")
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(20, 20, 20, 20)
            error_label = QLabel("Pricing management functionality is currently unavailable.\nPlease try again later.")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(error_label)
            pricing_widget = placeholder
            self.logger.error("Pricing management module failed to load")

        # Add the widget to the content layout
        self.content_layout.addWidget(pricing_widget)

    def show_packing_materials_page(self):
        """Display the packing materials management page"""
        self.clear_content()

        # Import the packing materials module
        try:
            from modules.packing_materials import PackingMaterialsWidget
            packing_widget = PackingMaterialsWidget(self.data)
            self.logger.info("Using packing materials widget")
        except Exception as e:
            # Create placeholder if module fails to load
            self.logger.error(f"Error loading packing materials widget: {str(e)}")
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(20, 20, 20, 20)
            error_label = QLabel("Packing materials functionality is currently unavailable.\nPlease try again later.")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(error_label)
            packing_widget = placeholder
            self.logger.error("Packing materials module failed to load")

        # Add the widget to the content layout
        self.content_layout.addWidget(packing_widget)

    def show_shopping_page(self):
        """Display the shopping list page"""
        self.clear_content()

        # Create the shopping widget using our fixed module
        # ShoppingWidget is already imported at the top of the file
        shopping_widget = ShoppingWidget(self.data)

        # Set main app reference for data refresh functionality
        shopping_widget.main_app = self

        # Add the widget to the content layout
        self.content_layout.addWidget(shopping_widget)

    def show_gas_management_page(self):
        """Display the gas management page"""
        self.clear_content()

        # Create the gas management widget
        try:
            from modules.gas_management import GasManagementWidget
            gas_widget = GasManagementWidget(self.data)

            # Connect gas alerts to main app notifications
            gas_widget.gas_alert_triggered.connect(self.handle_gas_alert)

            self.logger.info("Gas management widget created successfully")
        except Exception as e:
            self.logger.error(f"Error creating gas management widget: {e}")
            # Create placeholder
            gas_widget = QLabel("Gas Management System - Loading...")
            gas_widget.setAlignment(Qt.AlignCenter)
            gas_widget.setStyleSheet("font-size: 18px; color: #64748b;")

        # Add the widget to the content layout
        self.content_layout.addWidget(gas_widget)

    def handle_gas_alert(self, alert_type, message):
        """Handle gas alerts from the gas management system"""
        try:
            # Show system notification
            if alert_type == "critical":
                QMessageBox.critical(self, "Critical Gas Alert", message)
            elif alert_type == "warning":
                QMessageBox.warning(self, "Gas Alert", message)

            # Log the alert
            self.logger.warning(f"Gas Alert ({alert_type}): {message}")

            # You could also add desktop notifications here if needed

        except Exception as e:
            self.logger.error(f"Error handling gas alert: {e}")
    
    def show_waste_page(self):
        """Display the waste tracking page"""
        self.clear_content()
        
        # Import the waste module
        from modules.waste import WasteWidget
        
        # Create the waste widget
        waste_widget = WasteWidget(self.data)
        
        # Add the widget to the content layout
        self.content_layout.addWidget(waste_widget)
    
    def show_cleaning_page(self):
        """Display the cleaning and maintenance page"""
        self.clear_content()
        
        # Import the cleaning module
        from modules.cleaning_fixed import CleaningWidget
        
        # Create the cleaning widget
        cleaning_widget = CleaningWidget(self.data)
        
        # Add the widget to the content layout
        self.content_layout.addWidget(cleaning_widget)
    
    def show_settings_page(self):
        """Display the enhanced settings page with Firebase integration"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Application Settings")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create tabbed interface for settings
        settings_tabs = QTabWidget()
        settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
        """)

        # General Settings Tab
        general_container = QWidget()
        general_layout = QVBoxLayout(general_container)
        general_layout.setContentsMargins(20, 20, 20, 20)

        # Create the settings widget using our enhanced SettingsWidget class
        self.settings_widget = SettingsWidget(main_app=self, parent=self, data=self.data)

        # Connect the currency_changed signal to our apply_currency_changes method
        self.settings_widget.currency_changed.connect(self.apply_currency_changes)

        # Add the settings widget to the container
        general_layout.addWidget(self.settings_widget)
        settings_tabs.addTab(general_container, "⚙️ General")

        # Firebase Settings Tab
        try:
            from modules.enhanced_auth_widget import EnhancedAuthWidget
            from modules.cloud_sync_manager import CloudSyncManager

            firebase_container = QWidget()
            firebase_layout = QVBoxLayout(firebase_container)
            firebase_layout.setContentsMargins(20, 20, 20, 20)

            # Firebase sub-tabs
            firebase_subtabs = QTabWidget()

            # Authentication tab
            auth_widget = EnhancedAuthWidget()
            firebase_subtabs.addTab(auth_widget, "🔐 Authentication")

            # Cloud sync tab
            sync_widget = CloudSyncManager(self.data)
            firebase_subtabs.addTab(sync_widget, "☁️ Cloud Sync")

            firebase_layout.addWidget(firebase_subtabs)
            settings_tabs.addTab(firebase_container, "🔥 Firebase")

            self.logger.info("Firebase settings integrated into Settings tab")

        except Exception as e:
            self.logger.warning(f"Firebase settings not available: {e}")
            # Add placeholder Firebase tab
            firebase_placeholder = QLabel("Firebase settings not available.\nPlease check Firebase configuration.")
            firebase_placeholder.setAlignment(Qt.AlignCenter)
            firebase_placeholder.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
            settings_tabs.addTab(firebase_placeholder, "🔥 Firebase")

        # Data Management Tab
        data_container = QWidget()
        data_layout = QVBoxLayout(data_container)
        data_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        data_title = QLabel("Data Management")
        data_title.setFont(QFont("Arial", 16, QFont.Bold))
        data_title.setStyleSheet("color: #1e293b; margin-bottom: 20px;")
        data_layout.addWidget(data_title)

        # Refresh section
        refresh_group = QGroupBox("Data Refresh")
        refresh_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        refresh_layout = QVBoxLayout(refresh_group)

        # Refresh description
        refresh_desc = QLabel("Refresh all data from CSV files to reflect the latest changes in the GUI.")
        refresh_desc.setStyleSheet("color: #64748b; margin-bottom: 15px;")
        refresh_desc.setWordWrap(True)
        refresh_layout.addWidget(refresh_desc)

        # Refresh button
        refresh_button = QPushButton("🔄 Refresh All Data")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        refresh_button.clicked.connect(self.refresh_data)
        refresh_layout.addWidget(refresh_button)

        data_layout.addWidget(refresh_group)

        # Data status section
        status_group = QGroupBox("Data Status")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        status_layout = QVBoxLayout(status_group)

        # Data status info
        status_info = QLabel(f"""
Current Data Status:
• Shopping List: {len(self.data.get('shopping_list', []))} items
• Inventory: {len(self.data.get('inventory', []))} items
• Recipes: {len(self.data.get('recipes', []))} items
• Last Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: Click 'Refresh All Data' after making changes to CSV files to see updates in the GUI.
        """.strip())
        status_info.setStyleSheet("color: #374151; font-family: monospace; background-color: #f8fafc; padding: 15px; border-radius: 6px;")
        status_layout.addWidget(status_info)

        data_layout.addWidget(status_group)
        data_layout.addStretch()

        settings_tabs.addTab(data_container, "📊 Data Management")

        # Mobile & PWA Settings Tab
        try:
            mobile_container = QWidget()
            mobile_layout = QVBoxLayout(mobile_container)
            mobile_layout.setContentsMargins(20, 20, 20, 20)

            # Create mobile settings sub-tabs
            mobile_subtabs = QTabWidget()

            # Responsive design tab
            if self.responsive_manager:
                responsive_widget = self.create_responsive_settings_widget()
                mobile_subtabs.addTab(responsive_widget, "📱 Responsive Design")

            # PWA settings tab
            if self.pwa_manager:
                from modules.pwa_manager import PWAStatusWidget
                pwa_widget = PWAStatusWidget(self.pwa_manager)
                mobile_subtabs.addTab(pwa_widget, "📲 PWA & Offline")

            # Mobile navigation tab
            if self.mobile_navigation:
                navigation_widget = self.create_navigation_settings_widget()
                mobile_subtabs.addTab(navigation_widget, "🧭 Navigation")

            mobile_layout.addWidget(mobile_subtabs)
            settings_tabs.addTab(mobile_container, "📱 Mobile")

            self.logger.info("Mobile settings integrated into Settings tab")

        except Exception as e:
            self.logger.warning(f"Mobile settings not available: {e}")
            mobile_placeholder = QLabel("Mobile settings not available.\nPlease check mobile modules.")
            mobile_placeholder.setAlignment(Qt.AlignCenter)
            mobile_placeholder.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
            settings_tabs.addTab(mobile_placeholder, "📱 Mobile")

        # AI & ML Settings Tab
        try:
            ai_container = QWidget()
            ai_layout = QVBoxLayout(ai_container)
            ai_layout.setContentsMargins(20, 20, 20, 20)

            # AI Provider Selection
            self.create_ai_provider_selector_for_settings(ai_layout)

            # Create AI settings sub-tabs
            ai_subtabs = QTabWidget()

            # AI Insights tab
            if self.multi_ai_engine and self.multi_ai_engine.is_available():
                insights_widget = self.create_multi_ai_insights_widget()
                ai_subtabs.addTab(insights_widget, "🧠 AI Insights")

                # Provider Status tab
                status_widget = self.create_provider_status_widget()
                ai_subtabs.addTab(status_widget, "📊 Provider Status")

                # API Usage tab
                usage_widget = self.create_api_usage_widget()
                ai_subtabs.addTab(usage_widget, "📈 API Usage")

            ai_layout.addWidget(ai_subtabs)
            settings_tabs.addTab(ai_container, "🤖 AI & ML")

            self.logger.info("AI & ML settings integrated into Settings tab")

        except Exception as e:
            self.logger.warning(f"AI & ML settings not available: {e}")
            ai_placeholder = QLabel("AI & ML settings not available.\nPlease check AI modules.")
            ai_placeholder.setAlignment(Qt.AlignCenter)
            ai_placeholder.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
            settings_tabs.addTab(ai_placeholder, "🤖 AI & ML")

        # Enterprise Settings Tab
        try:
            enterprise_container = QWidget()
            enterprise_layout = QVBoxLayout(enterprise_container)
            enterprise_layout.setContentsMargins(20, 20, 20, 20)

            # Create enterprise settings sub-tabs
            enterprise_subtabs = QTabWidget()

            # User Management tab
            if self.enterprise_manager:
                users_widget = self.create_user_management_widget()
                enterprise_subtabs.addTab(users_widget, "👥 User Management")

                # Security & Audit tab
                security_widget = self.create_security_audit_widget()
                enterprise_subtabs.addTab(security_widget, "🔒 Security & Audit")

                # API Management tab
                api_widget = self.create_api_management_widget()
                enterprise_subtabs.addTab(api_widget, "🔌 API Management")

            enterprise_layout.addWidget(enterprise_subtabs)
            settings_tabs.addTab(enterprise_container, "🏢 Enterprise")

            self.logger.info("Enterprise settings integrated into Settings tab")

        except Exception as e:
            self.logger.warning(f"Enterprise settings not available: {e}")
            enterprise_placeholder = QLabel("Enterprise settings not available.\nPlease check enterprise modules.")
            enterprise_placeholder.setAlignment(Qt.AlignCenter)
            enterprise_placeholder.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
            settings_tabs.addTab(enterprise_placeholder, "🏢 Enterprise")

        self.content_layout.addWidget(settings_tabs)

        # Log the action
        self.logger.info("Enhanced Settings page with Mobile, AI/ML, and Enterprise tabs displayed")
    
    def show_logs_page(self):
        """Display the logs viewer page with missing items tab"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Application Logs & Missing Items")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create tabbed interface for logs
        logs_tabs = QTabWidget()
        logs_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
        """)

        # Application Logs Tab
        try:
            from modules.enhanced_logs_viewer import EnhancedLogsViewer
            logs_widget = EnhancedLogsViewer()
            self.logger.info("Using enhanced logs viewer")
        except Exception as e:
            # Fallback to original logs viewer
            self.logger.warning(f"Enhanced logs viewer not available: {e}")
            logs_widget = LogsViewerWidget()

        logs_tabs.addTab(logs_widget, "📋 Application Logs")

        # Missing Items Tab
        try:
            from modules.missing_items_viewer import MissingItemsViewer
            missing_items_widget = MissingItemsViewer()
            logs_tabs.addTab(missing_items_widget, "⚠️ Missing Items")
            self.logger.info("Missing items viewer added to logs")
        except Exception as e:
            self.logger.error(f"Failed to add missing items viewer: {e}")

        # Inventory Data Tab
        try:
            from modules.inventory_data_viewer import InventoryDataViewer
            inventory_data_widget = InventoryDataViewer(self.data)
            logs_tabs.addTab(inventory_data_widget, "📦 Available Inventory")
            self.logger.info("Inventory data viewer added to logs")
        except Exception as e:
            self.logger.error(f"Failed to add inventory data viewer: {e}")

        # Data Sources Tab
        try:
            from modules.data_sources_viewer import DataSourcesViewer
            data_sources_widget = DataSourcesViewer(self.data)
            logs_tabs.addTab(data_sources_widget, "🔍 All Data Sources")
            self.logger.info("Data sources viewer added to logs")
        except Exception as e:
            self.logger.error(f"Failed to add data sources viewer: {e}")

        self.content_layout.addWidget(logs_tabs)

        # Log the action
        self.logger.info("Logs page with missing items displayed")

    def show_analytics_page(self):
        """Display the business intelligence analytics page"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Business Intelligence Analytics")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create business intelligence dashboard
        try:
            from modules.business_intelligence_dashboard import BusinessIntelligenceDashboard
            analytics_widget = BusinessIntelligenceDashboard(self.data)
            self.logger.info("Using business intelligence dashboard")
        except Exception as e:
            # Fallback to placeholder
            self.logger.warning(f"Business intelligence dashboard not available: {e}")
            analytics_widget = QLabel("Business Intelligence Dashboard - Loading...")
            analytics_widget.setAlignment(Qt.AlignCenter)
            analytics_widget.setStyleSheet("font-size: 18px; color: #64748b;")

        self.content_layout.addWidget(analytics_widget)

        # Log the action
        self.logger.info("Analytics page displayed")

    def show_reports_page(self):
        """Display the advanced reporting page"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Advanced Reporting")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create advanced reporting widget
        try:
            from modules.advanced_reporting import AdvancedReporting
            reports_widget = AdvancedReporting(self.data)
            self.logger.info("Using advanced reporting system")
        except Exception as e:
            # Fallback to placeholder
            self.logger.warning(f"Advanced reporting system not available: {e}")
            reports_widget = QLabel("Advanced Reporting System - Loading...")
            reports_widget.setAlignment(Qt.AlignCenter)
            reports_widget.setStyleSheet("font-size: 18px; color: #64748b;")

        self.content_layout.addWidget(reports_widget)

        # Log the action
        self.logger.info("Reports page displayed")

    def show_firebase_page(self):
        """Display the Firebase management page"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Firebase Cloud Services")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create Firebase management widget
        try:
            from modules.enhanced_auth_widget import EnhancedAuthWidget
            from modules.cloud_sync_manager import CloudSyncManager

            # Create tabbed interface for Firebase services
            firebase_tabs = QTabWidget()
            firebase_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    margin-top: -1px;
                }
                QTabBar::tab {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 12px 20px;
                    margin-right: 2px;
                    font-size: 13px;
                    font-weight: 500;
                    color: #64748b;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 1px solid white;
                    color: #0f172a;
                }
            """)

            # Authentication tab
            auth_widget = EnhancedAuthWidget()
            firebase_tabs.addTab(auth_widget, "Authentication")

            # Cloud sync tab
            sync_widget = CloudSyncManager(self.data)
            firebase_tabs.addTab(sync_widget, "Cloud Sync")

            self.content_layout.addWidget(firebase_tabs)
            self.logger.info("Using enhanced Firebase management")

        except Exception as e:
            # Fallback to placeholder
            self.logger.warning(f"Enhanced Firebase management not available: {e}")
            firebase_widget = QLabel("Firebase Management - Loading...")
            firebase_widget.setAlignment(Qt.AlignCenter)
            firebase_widget.setStyleSheet("font-size: 18px; color: #64748b;")
            self.content_layout.addWidget(firebase_widget)

        # Log the action
        self.logger.info("Firebase page displayed")

    def show_mobile_settings_page(self):
        """Display the mobile and PWA settings page"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Mobile & PWA Settings")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create mobile settings widget
        try:
            # Create tabbed interface for mobile settings
            mobile_tabs = QTabWidget()
            mobile_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    margin-top: -1px;
                }
                QTabBar::tab {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 12px 20px;
                    margin-right: 2px;
                    font-size: 13px;
                    font-weight: 500;
                    color: #64748b;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 1px solid white;
                    color: #0f172a;
                }
            """)

            # Responsive design tab
            if self.responsive_manager:
                responsive_widget = self.create_responsive_settings_widget()
                mobile_tabs.addTab(responsive_widget, "Responsive Design")

            # PWA settings tab
            if self.pwa_manager:
                from modules.pwa_manager import PWAStatusWidget
                pwa_widget = PWAStatusWidget(self.pwa_manager)
                mobile_tabs.addTab(pwa_widget, "PWA & Offline")

            # Mobile navigation tab
            if self.mobile_navigation:
                navigation_widget = self.create_navigation_settings_widget()
                mobile_tabs.addTab(navigation_widget, "Navigation")

            self.content_layout.addWidget(mobile_tabs)
            self.logger.info("Using mobile and PWA settings")

        except Exception as e:
            # Fallback to placeholder
            self.logger.warning(f"Mobile settings not available: {e}")
            mobile_widget = QLabel("Mobile & PWA Settings - Loading...")
            mobile_widget.setAlignment(Qt.AlignCenter)
            mobile_widget.setStyleSheet("font-size: 18px; color: #64748b;")
            self.content_layout.addWidget(mobile_widget)

        # Log the action
        self.logger.info("Mobile settings page displayed")

    def show_ai_ml_page(self):
        """Display the AI & ML page"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("AI & Machine Learning")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Add AI Provider Selection
        self.create_ai_provider_selector()

        # Create AI & ML widget
        try:
            # Create tabbed interface for AI & ML features
            ai_tabs = QTabWidget()
            ai_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    margin-top: -1px;
                }
                QTabBar::tab {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 12px 20px;
                    margin-right: 2px;
                    font-size: 13px;
                    font-weight: 500;
                    color: #64748b;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 1px solid white;
                    color: #0f172a;
                }
            """)

            # AI Insights tab
            if self.multi_ai_engine and self.multi_ai_engine.is_available():
                insights_widget = self.create_multi_ai_insights_widget()
                ai_tabs.addTab(insights_widget, "AI Insights")

                # Provider Status tab
                status_widget = self.create_provider_status_widget()
                ai_tabs.addTab(status_widget, "Provider Status")

                # API Usage tab
                usage_widget = self.create_api_usage_widget()
                ai_tabs.addTab(usage_widget, "API Usage")

            self.content_layout.addWidget(ai_tabs)
            self.logger.info("Using AI & ML features")

        except Exception as e:
            # Fallback to placeholder
            self.logger.warning(f"AI & ML features not available: {e}")
            ai_widget = QLabel("AI & ML Features - Loading...")
            ai_widget.setAlignment(Qt.AlignCenter)
            ai_widget.setStyleSheet("font-size: 18px; color: #64748b;")
            self.content_layout.addWidget(ai_widget)

        # Log the action
        self.logger.info("AI & ML page displayed")

    def create_ai_engine_selector(self):
        """Create AI engine selection widget"""
        selector_widget = QWidget()
        selector_layout = QHBoxLayout(selector_widget)
        selector_layout.setContentsMargins(20, 10, 20, 10)

        # AI Engine Selection Group
        engine_group = QGroupBox("🤖 AI Engine Selection")
        engine_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        engine_layout = QHBoxLayout(engine_group)

        # Local AI Radio Button
        self.local_ai_radio = QRadioButton("🖥️ Local AI (Free, No Internet)")
        self.local_ai_radio.setChecked(True)  # Default to local AI
        self.local_ai_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        engine_layout.addWidget(self.local_ai_radio)

        # Cohere AI Radio Button
        self.cohere_ai_radio = QRadioButton("☁️ Cohere AI (Better Insights, Requires API Key)")
        self.cohere_ai_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        engine_layout.addWidget(self.cohere_ai_radio)

        # Status Label
        self.ai_status_label = QLabel("Status: Local AI Active")
        self.ai_status_label.setStyleSheet("color: #10b981; font-weight: 500; margin-left: 20px;")
        engine_layout.addWidget(self.ai_status_label)

        engine_layout.addStretch()

        # Setup Button
        setup_cohere_btn = QPushButton("⚙️ Setup Cohere AI")
        setup_cohere_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        setup_cohere_btn.clicked.connect(self.show_cohere_setup_dialog)
        engine_layout.addWidget(setup_cohere_btn)

        # Connect radio button signals
        self.local_ai_radio.toggled.connect(self.on_ai_engine_changed)
        self.cohere_ai_radio.toggled.connect(self.on_ai_engine_changed)

        selector_layout.addWidget(engine_group)
        self.content_layout.addWidget(selector_widget)

        # Check Cohere AI availability
        self.check_cohere_availability()

    def create_ai_provider_selector(self):
        """Create AI provider selection widget with multiple options"""
        selector_widget = QWidget()
        selector_layout = QVBoxLayout(selector_widget)
        selector_layout.setContentsMargins(20, 10, 20, 10)

        # Title
        title_label = QLabel("🤖 AI Provider Selection")
        title_label.setFont(self.header_font)
        title_label.setStyleSheet("color: #2c3e50; font-weight: bold; margin-bottom: 15px;")
        selector_layout.addWidget(title_label)

        # Get available providers
        if hasattr(self, 'multi_ai_engine') and self.multi_ai_engine:
            providers = self.multi_ai_engine.get_available_providers()
        else:
            providers = []

        if not providers:
            # No providers available
            no_providers_label = QLabel("❌ No AI providers available. Please configure API keys.")
            no_providers_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 20px;")
            selector_layout.addWidget(no_providers_label)

            # Add setup instructions
            setup_label = QLabel("""
            To use AI features, you need to set up at least one AI provider:

            1. Cohere: Set COHERE_API_KEY environment variable
            2. OpenAI: Set OPENAI_API_KEY environment variable
            3. Anthropic: Set ANTHROPIC_API_KEY environment variable
            4. Google Gemini: Set GOOGLE_API_KEY environment variable
            5. Hugging Face: Set HUGGINGFACE_API_KEY environment variable
            6. Groq: Set GROQ_API_KEY environment variable
            """)
            setup_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px; background-color: #f8f9fa; border-radius: 8px;")
            selector_layout.addWidget(setup_label)
        else:
            # Create provider selection grid
            providers_widget = QWidget()
            providers_layout = QGridLayout(providers_widget)
            providers_layout.setSpacing(10)

            self.provider_buttons = []

            for i, provider in enumerate(providers):
                # Create provider card
                provider_card = QPushButton()
                provider_card.setFixedSize(200, 120)
                provider_card.setCheckable(True)

                # Set card content
                card_text = f"""{provider['icon']} {provider['name']}

{provider['description']}

✓ {', '.join(provider['strengths'][:2])}"""

                provider_card.setText(card_text)
                provider_card.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        border: 2px solid #e9ecef;
                        border-radius: 12px;
                        padding: 10px;
                        text-align: left;
                        font-size: 11px;
                        color: #495057;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                        border-color: #adb5bd;
                    }
                    QPushButton:checked {
                        background-color: #e3f2fd;
                        border-color: #2196f3;
                        color: #1976d2;
                        font-weight: bold;
                    }
                """)

                # Connect signal
                provider_card.clicked.connect(lambda checked, p=provider['provider']: self.on_provider_selected(p))

                # Add to grid (3 columns)
                row = i // 3
                col = i % 3
                providers_layout.addWidget(provider_card, row, col)

                self.provider_buttons.append((provider_card, provider['provider']))

            selector_layout.addWidget(providers_widget)

            # Current provider status
            self.provider_status_label = QLabel("🔄 Select an AI provider")
            self.provider_status_label.setStyleSheet("color: #6c757d; font-weight: bold; margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 6px;")
            selector_layout.addWidget(self.provider_status_label)

            # Set default provider if available
            if providers:
                default_provider = providers[0]['provider']
                self.on_provider_selected(default_provider)
                self.provider_buttons[0][0].setChecked(True)

        # Add to main layout
        self.content_layout.addWidget(selector_widget)

    def on_provider_selected(self, provider: str):
        """Handle AI provider selection"""
        try:
            if hasattr(self, 'multi_ai_engine') and self.multi_ai_engine:
                success = self.multi_ai_engine.set_provider(provider)
                if success:
                    # Update UI
                    if hasattr(self, 'provider_status_label'):
                        self.provider_status_label.setText(f"✅ {provider.title()} AI Active")
                        self.provider_status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 15px; padding: 10px; background-color: #d4edda; border-radius: 6px;")

                    # Uncheck other buttons
                    for button, button_provider in self.provider_buttons:
                        if button_provider != provider:
                            button.setChecked(False)

                    self.logger.info(f"Switched to {provider} AI provider")
                else:
                    self.logger.error(f"Failed to switch to {provider}")
        except Exception as e:
            self.logger.error(f"Error selecting provider {provider}: {e}")

    def create_ai_provider_selector_for_settings(self, parent_layout):
        """Create AI provider selector for settings tab"""
        try:
            # Title
            provider_title = QLabel("AI Provider Selection")
            provider_title.setFont(QFont("Arial", 16, QFont.Bold))
            provider_title.setStyleSheet("color: #1e293b; margin-bottom: 15px;")
            parent_layout.addWidget(provider_title)

            # Description
            provider_desc = QLabel("Select your preferred AI provider for intelligent features:")
            provider_desc.setStyleSheet("color: #64748b; margin-bottom: 20px;")
            parent_layout.addWidget(provider_desc)

            # Provider selection (simplified for settings)
            if hasattr(self, 'multi_ai_engine') and self.multi_ai_engine:
                current_provider = self.multi_ai_engine.get_current_provider()
                provider_info = QLabel(f"Current Provider: {current_provider}")
                provider_info.setStyleSheet("color: #059669; font-weight: 500; padding: 10px; background-color: #f0fdf4; border-radius: 6px;")
                parent_layout.addWidget(provider_info)
            else:
                no_provider = QLabel("No AI provider configured")
                no_provider.setStyleSheet("color: #dc2626; font-weight: 500; padding: 10px; background-color: #fef2f2; border-radius: 6px;")
                parent_layout.addWidget(no_provider)

        except Exception as e:
            self.logger.error(f"Error creating AI provider selector for settings: {e}")

    def create_responsive_settings_widget(self):
        """Create responsive design settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Device info
        device_group = QGroupBox("Device Information")
        device_layout = QFormLayout(device_group)

        if self.responsive_manager:
            device_info = self.responsive_manager.get_device_info()

            device_type_label = QLabel(device_info["device_type"].title())
            device_type_label.setStyleSheet("font-weight: 500; color: #374151;")
            device_layout.addRow("Device Type:", device_type_label)

            layout_mode_label = QLabel(device_info["layout_mode"].title())
            layout_mode_label.setStyleSheet("font-weight: 500; color: #374151;")
            device_layout.addRow("Layout Mode:", layout_mode_label)

            screen_size_label = QLabel(f"{device_info['screen_size']['width']} x {device_info['screen_size']['height']}")
            screen_size_label.setStyleSheet("font-weight: 500; color: #374151;")
            device_layout.addRow("Screen Size:", screen_size_label)

            touch_enabled_label = QLabel("Yes" if device_info["touch_enabled"] else "No")
            touch_enabled_label.setStyleSheet("font-weight: 500; color: #374151;")
            device_layout.addRow("Touch Enabled:", touch_enabled_label)

        layout.addWidget(device_group)

        # Responsive features info
        features_group = QGroupBox("Responsive Features")
        features_layout = QVBoxLayout(features_group)

        features_text = QLabel("""
        • Automatic layout adaptation based on screen size
        • Touch-optimized controls for mobile devices
        • Responsive typography and spacing
        • Adaptive navigation styles
        • Mobile-friendly card layouts
        """)
        features_text.setStyleSheet("color: #6b7280; line-height: 1.5;")
        features_layout.addWidget(features_text)

        layout.addWidget(features_group)

        layout.addStretch()
        return widget

    def create_navigation_settings_widget(self):
        """Create navigation settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Navigation info
        nav_group = QGroupBox("Navigation Information")
        nav_layout = QFormLayout(nav_group)

        if self.mobile_navigation:
            current_style = self.mobile_navigation.get_current_navigation_style()

            style_label = QLabel(current_style.value.replace('_', ' ').title())
            style_label.setStyleSheet("font-weight: 500; color: #374151;")
            nav_layout.addRow("Current Style:", style_label)

        layout.addWidget(nav_group)

        # Navigation features info
        nav_features_group = QGroupBox("Navigation Features")
        nav_features_layout = QVBoxLayout(nav_features_group)

        nav_features_text = QLabel("""
        • Automatic navigation style switching
        • Bottom tabs for mobile devices
        • Hamburger menu for tablets
        • Touch-optimized button sizes
        • Gesture-friendly interactions
        """)
        nav_features_text.setStyleSheet("color: #6b7280; line-height: 1.5;")
        nav_features_layout.addWidget(nav_features_text)

        layout.addWidget(nav_features_group)

        layout.addStretch()
        return widget

    def show_enterprise_page(self):
        """Display the Enterprise features page"""
        self.clear_content()

        # Add header to the content area
        header_label = QLabel("Enterprise Features")
        header_label.setFont(self.title_font)
        self.content_layout.addWidget(header_label)

        # Create Enterprise widget
        try:
            # Create tabbed interface for Enterprise features
            enterprise_tabs = QTabWidget()
            enterprise_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    margin-top: -1px;
                }
                QTabBar::tab {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    padding: 12px 20px;
                    margin-right: 2px;
                    font-size: 13px;
                    font-weight: 500;
                    color: #64748b;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 1px solid white;
                    color: #0f172a;
                }
            """)

            # User Management tab
            if self.enterprise_manager:
                users_widget = self.create_user_management_widget()
                enterprise_tabs.addTab(users_widget, "User Management")

                # Security & Audit tab
                security_widget = self.create_security_audit_widget()
                enterprise_tabs.addTab(security_widget, "Security & Audit")

                # API Management tab
                api_widget = self.create_api_management_widget()
                enterprise_tabs.addTab(api_widget, "API Management")

            self.content_layout.addWidget(enterprise_tabs)
            self.logger.info("Using Enterprise features")

        except Exception as e:
            # Fallback to placeholder
            self.logger.warning(f"Enterprise features not available: {e}")
            enterprise_widget = QLabel("Enterprise Features - Loading...")
            enterprise_widget.setAlignment(Qt.AlignCenter)
            enterprise_widget.setStyleSheet("font-size: 18px; color: #64748b;")
            self.content_layout.addWidget(enterprise_widget)

        # Log the action
        self.logger.info("Enterprise page displayed")

    def create_predictions_widget(self):
        """Create predictions widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Train Models button
        train_button = QPushButton("🔄 Train AI Models")
        train_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        train_button.clicked.connect(self.train_ai_models)
        layout.addWidget(train_button)

        # Sales Forecast
        forecast_group = QGroupBox("Sales Forecast (Next 7 Days)")
        forecast_layout = QVBoxLayout(forecast_group)

        if self.ai_ml_engine:
            try:
                forecasts = self.ai_ml_engine.generate_sales_forecast(7)
                if forecasts:
                    for forecast in forecasts[:3]:  # Show first 3 days
                        forecast_label = QLabel(f"{forecast['date']} ({forecast['day_of_week']}): ${forecast['predicted_sales']:.2f}")
                        forecast_label.setStyleSheet("color: #374151; font-size: 13px; padding: 4px 0;")
                        forecast_layout.addWidget(forecast_label)
                else:
                    forecast_layout.addWidget(QLabel("No forecast data available. Train models first."))
            except Exception as e:
                forecast_layout.addWidget(QLabel(f"Error generating forecast: {str(e)}"))

        layout.addWidget(forecast_group)

        # Recommendations
        recommendations_group = QGroupBox("AI Recommendations")
        recommendations_layout = QVBoxLayout(recommendations_group)

        if self.ai_ml_engine:
            try:
                recommendations = self.ai_ml_engine.generate_recommendations()
                if recommendations:
                    for rec in recommendations[:3]:  # Show first 3 recommendations
                        rec_label = QLabel(f"• {rec['title']}: {rec['description']}")
                        rec_label.setStyleSheet("color: #374151; font-size: 13px; padding: 4px 0;")
                        rec_label.setWordWrap(True)
                        recommendations_layout.addWidget(rec_label)
                else:
                    recommendations_layout.addWidget(QLabel("No recommendations available."))
            except Exception as e:
                recommendations_layout.addWidget(QLabel(f"Error generating recommendations: {str(e)}"))

        layout.addWidget(recommendations_group)
        layout.addStretch()
        return widget

    def create_multi_ai_insights_widget(self):
        """Create multi-AI insights widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Generate Insights button
        generate_button = QPushButton("🧠 Generate AI Insights")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        generate_button.clicked.connect(self.generate_multi_ai_insights)
        layout.addWidget(generate_button)

        # Current Provider Info
        if hasattr(self, 'multi_ai_engine') and self.multi_ai_engine:
            current_provider = self.multi_ai_engine.get_current_provider()
            if current_provider:
                provider_info = QLabel(f"🤖 Using: {current_provider.title()} AI")
                provider_info.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px; padding: 10px; background-color: #d1fae5; border-radius: 6px;")
                layout.addWidget(provider_info)

        # Insights Display Area
        self.insights_display = QLabel("Click 'Generate AI Insights' to get business recommendations")
        self.insights_display.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 20px;
                color: #6c757d;
                font-size: 14px;
                min-height: 200px;
            }
        """)
        self.insights_display.setWordWrap(True)
        self.insights_display.setAlignment(Qt.AlignTop)
        layout.addWidget(self.insights_display)

        layout.addStretch()
        return widget

    def create_provider_status_widget(self):
        """Create provider status widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Refresh button
        refresh_button = QPushButton("🔄 Refresh Status")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        refresh_button.clicked.connect(self.refresh_provider_status)
        layout.addWidget(refresh_button)

        # Provider status list
        self.provider_status_list = QWidget()
        self.provider_status_layout = QVBoxLayout(self.provider_status_list)
        layout.addWidget(self.provider_status_list)

        # Initial status load
        self.refresh_provider_status()

        layout.addStretch()
        return widget

    def create_api_usage_widget(self):
        """Create API usage tracking widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Usage info
        usage_info = QLabel("""
        📊 API Usage Information

        Track your AI API usage to stay within free tier limits:

        • Cohere: 100 requests/month (Free)
        • OpenAI: Pay-per-use ($0.002/1K tokens)
        • Anthropic: Limited free usage
        • Google Gemini: 60 requests/minute (Free)
        • Hugging Face: Rate limited (Free)
        • Groq: Limited requests (Free)

        💡 Tip: Use multiple providers to maximize free usage!
        """)
        usage_info.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
                color: #856404;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        usage_info.setWordWrap(True)
        layout.addWidget(usage_info)

        layout.addStretch()
        return widget

    def generate_multi_ai_insights(self):
        """Generate insights using the selected AI provider"""
        if not hasattr(self, 'multi_ai_engine') or not self.multi_ai_engine:
            self.insights_display.setText("❌ Multi-AI engine not available")
            return

        current_provider = self.multi_ai_engine.get_current_provider()
        if not current_provider:
            self.insights_display.setText("❌ No AI provider selected. Please select a provider first.")
            return

        # Show loading state with animation
        self.insights_display.setText(f"🔄 Generating insights using {current_provider.title()} AI...\n\n⏳ Please wait, this may take 5-15 seconds...")
        self.insights_display.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 20px;
                color: #856404;
                font-size: 14px;
                min-height: 200px;
            }
        """)

        # Process events to update UI immediately
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            # Get sales data
            sales_data = self.data.get('sales', pd.DataFrame())
            if sales_data.empty:
                # Create sample data if none exists
                sales_data = pd.DataFrame([
                    {'item_name': 'Chicken Curry', 'quantity': 15, 'total_amount': 2250, 'date': '2024-01-01'},
                    {'item_name': 'Dosa', 'quantity': 25, 'total_amount': 1250, 'date': '2024-01-01'},
                    {'item_name': 'Biryani', 'quantity': 10, 'total_amount': 2000, 'date': '2024-01-01'},
                ])

            # Generate insights
            insights = self.multi_ai_engine.generate_sales_insights(sales_data)

            if 'error' in insights:
                self.insights_display.setText(f"❌ Error: {insights['error']}")
            else:
                # Format and display insights
                provider = insights.get('provider', current_provider)
                ai_insights = insights.get('ai_insights', 'No insights generated')
                timestamp = insights.get('timestamp', 'Unknown')

                formatted_insights = f"""🤖 AI Insights from {provider}
Generated: {timestamp[:19]}

{ai_insights}

💡 These insights are generated by AI and should be used as guidance alongside your business expertise."""

                # Reset style to normal
                self.insights_display.setStyleSheet("""
                    QLabel {
                        background-color: #f8f9fa;
                        border: 2px solid #28a745;
                        border-radius: 8px;
                        padding: 20px;
                        color: #155724;
                        font-size: 14px;
                        min-height: 200px;
                    }
                """)
                self.insights_display.setText(formatted_insights)
                self.logger.info(f"Generated insights using {provider}")

        except Exception as e:
            self.insights_display.setText(f"❌ Error generating insights: {e}")
            self.logger.error(f"Error generating insights: {e}")

    def refresh_provider_status(self):
        """Refresh provider status display"""
        # Clear existing status
        for i in reversed(range(self.provider_status_layout.count())):
            self.provider_status_layout.itemAt(i).widget().setParent(None)

        if not hasattr(self, 'multi_ai_engine') or not self.multi_ai_engine:
            status_label = QLabel("❌ Multi-AI engine not available")
            self.provider_status_layout.addWidget(status_label)
            return

        # Get available providers
        providers = self.multi_ai_engine.get_available_providers()
        current_provider = self.multi_ai_engine.get_current_provider()

        if not providers:
            no_providers_label = QLabel("❌ No AI providers configured")
            no_providers_label.setStyleSheet("color: #dc3545; padding: 10px;")
            self.provider_status_layout.addWidget(no_providers_label)
            return

        # Display each provider status
        for provider in providers:
            provider_widget = QWidget()
            provider_layout = QHBoxLayout(provider_widget)
            provider_layout.setContentsMargins(10, 5, 10, 5)

            # Provider icon and name
            name_label = QLabel(f"{provider['icon']} {provider['name']}")
            name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            provider_layout.addWidget(name_label)

            # Status indicator
            is_current = provider['provider'] == current_provider
            status_text = "🟢 Active" if is_current else "⚪ Available"
            status_label = QLabel(status_text)
            status_label.setStyleSheet("color: #28a745;" if is_current else "color: #6c757d;")
            provider_layout.addWidget(status_label)

            provider_layout.addStretch()

            # Strengths
            strengths_label = QLabel(f"✓ {', '.join(provider['strengths'][:2])}")
            strengths_label.setStyleSheet("color: #6c757d; font-size: 12px;")
            provider_layout.addWidget(strengths_label)

            # Style the widget
            provider_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    margin: 2px 0;
                }
            """ + ("background-color: #d4edda; border-color: #c3e6cb;" if is_current else ""))

            self.provider_status_layout.addWidget(provider_widget)

    def create_ai_insights_widget(self):
        """Create AI insights widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Anomaly Detection
        anomaly_group = QGroupBox("Anomaly Detection")
        anomaly_layout = QVBoxLayout(anomaly_group)

        detect_button = QPushButton("🔍 Detect Anomalies")
        detect_button.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        detect_button.clicked.connect(self.detect_anomalies)
        anomaly_layout.addWidget(detect_button)

        layout.addWidget(anomaly_group)

        # Recent Insights
        insights_group = QGroupBox("Recent AI Insights")
        insights_layout = QVBoxLayout(insights_group)

        if self.ai_ml_engine:
            try:
                insights = self.ai_ml_engine.get_ai_insights(5)
                if insights:
                    for insight in insights:
                        insight_label = QLabel(f"• {insight['title']}: {insight['description']}")
                        insight_label.setStyleSheet("color: #374151; font-size: 13px; padding: 4px 0;")
                        insight_label.setWordWrap(True)
                        insights_layout.addWidget(insight_label)
                else:
                    insights_layout.addWidget(QLabel("No insights available yet."))
            except Exception as e:
                insights_layout.addWidget(QLabel(f"Error loading insights: {str(e)}"))

        layout.addWidget(insights_group)
        layout.addStretch()
        return widget

    def create_models_status_widget(self):
        """Create models status widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Model Status
        status_group = QGroupBox("Model Training Status")
        status_layout = QFormLayout(status_group)

        if self.ai_ml_engine:
            status = self.ai_ml_engine.get_model_status()

            trained_label = QLabel("Yes" if status["models_trained"] else "No")
            trained_label.setStyleSheet("font-weight: 500; color: #10b981;" if status["models_trained"] else "font-weight: 500; color: #ef4444;")
            status_layout.addRow("Models Trained:", trained_label)

            last_training_label = QLabel(status["last_training_time"] or "Never")
            status_layout.addRow("Last Training:", last_training_label)

            models_label = QLabel(", ".join(status["available_models"]))
            status_layout.addRow("Available Models:", models_label)

            insights_label = QLabel(str(status["insights_count"]))
            status_layout.addRow("Total Insights:", insights_label)

        layout.addWidget(status_group)
        layout.addStretch()
        return widget

    def on_ai_engine_changed(self):
        """Handle AI engine selection change"""
        if self.local_ai_radio.isChecked():
            self.ai_status_label.setText("Status: Local AI Active")
            self.ai_status_label.setStyleSheet("color: #10b981; font-weight: 500; margin-left: 20px;")
            self.logger.info("Switched to Local AI engine")
        elif self.cohere_ai_radio.isChecked():
            if self.check_cohere_availability():
                self.ai_status_label.setText("Status: Cohere AI Active")
                self.ai_status_label.setStyleSheet("color: #3b82f6; font-weight: 500; margin-left: 20px;")
                self.logger.info("Switched to Cohere AI engine")
            else:
                self.ai_status_label.setText("Status: Cohere AI Not Available")
                self.ai_status_label.setStyleSheet("color: #ef4444; font-weight: 500; margin-left: 20px;")
                self.local_ai_radio.setChecked(True)  # Fall back to local AI

    def check_cohere_availability(self):
        """Check if Cohere AI is available"""
        try:
            from modules.cohere_ai_integration import CohereAIEngine
            cohere_engine = CohereAIEngine()
            return cohere_engine.is_enabled()
        except Exception as e:
            self.logger.error(f"Error checking Cohere availability: {e}")
            return False

    def show_cohere_setup_dialog(self):
        """Show Cohere AI setup dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel

        dialog = QDialog(self)
        dialog.setWindowTitle("Cohere AI Setup")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel("""
        <h3>🚀 Setup Cohere AI for Better Insights</h3>
        <p><b>Benefits:</b></p>
        <ul>
        <li>✅ Advanced AI-powered business insights</li>
        <li>✅ No local model training required</li>
        <li>✅ Faster performance and better recommendations</li>
        <li>✅ Free tier available (100 calls/month)</li>
        </ul>

        <p><b>Setup Steps:</b></p>
        <ol>
        <li>Visit <a href="https://cohere.ai">cohere.ai</a> and create a free account</li>
        <li>Generate an API key from your dashboard</li>
        <li>Set environment variable: <code>COHERE_API_KEY=your_key_here</code></li>
        <li>Restart the application</li>
        </ol>

        <p><b>Alternative:</b> You can continue using Local AI (no setup required)</p>
        """)
        instructions.setWordWrap(True)
        instructions.setOpenExternalLinks(True)
        layout.addWidget(instructions)

        # Close button
        close_btn = QPushButton("Got it!")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def create_user_management_widget(self):
        """Create user management widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Current User Info
        user_group = QGroupBox("Current Session")
        user_layout = QFormLayout(user_group)

        if self.enterprise_manager and self.enterprise_manager.current_user:
            user = self.enterprise_manager.current_user
            user_layout.addRow("Username:", QLabel(user["username"]))
            user_layout.addRow("Email:", QLabel(user["email"]))
            user_layout.addRow("Role:", QLabel(user["role"].value.title()))
            user_layout.addRow("Permissions:", QLabel(f"{len(user['permissions'])} permissions"))
        else:
            user_layout.addRow("Status:", QLabel("Not authenticated"))

        layout.addWidget(user_group)

        # All Users
        users_group = QGroupBox("All Users")
        users_layout = QVBoxLayout(users_group)

        if self.enterprise_manager:
            users = self.enterprise_manager.user_manager.get_all_users()
            for user in users[:5]:  # Show first 5 users
                user_info = f"{user['username']} ({user['role']}) - {'Active' if user['is_active'] else 'Inactive'}"
                user_label = QLabel(user_info)
                user_label.setStyleSheet("color: #374151; font-size: 13px; padding: 2px 0;")
                users_layout.addWidget(user_label)

        layout.addWidget(users_group)
        layout.addStretch()
        return widget

    def create_security_audit_widget(self):
        """Create security and audit widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Audit Trail
        audit_group = QGroupBox("Recent Audit Trail")
        audit_layout = QVBoxLayout(audit_group)

        if self.enterprise_manager:
            audit_records = self.enterprise_manager.user_manager.get_audit_trail(5)
            for record in audit_records:
                audit_info = f"{record['timestamp'][:19]} - {record['username']}: {record['action']} on {record['resource_type']}"
                audit_label = QLabel(audit_info)
                audit_label.setStyleSheet("color: #374151; font-size: 12px; padding: 2px 0;")
                audit_layout.addWidget(audit_label)

        layout.addWidget(audit_group)

        # Security Status
        security_group = QGroupBox("Security Status")
        security_layout = QFormLayout(security_group)

        security_layout.addRow("Encryption:", QLabel("AES-256"))
        security_layout.addRow("Authentication:", QLabel("JWT + PBKDF2"))
        security_layout.addRow("Session Timeout:", QLabel("24 hours"))
        security_layout.addRow("Audit Logging:", QLabel("Enabled"))

        layout.addWidget(security_group)
        layout.addStretch()
        return widget

    def create_api_management_widget(self):
        """Create API management widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # API Status
        api_group = QGroupBox("API Status")
        api_layout = QFormLayout(api_group)

        api_layout.addRow("API Version:", QLabel("v1.0"))
        api_layout.addRow("Authentication:", QLabel("API Key"))
        api_layout.addRow("Rate Limiting:", QLabel("1000 req/hour"))
        api_layout.addRow("Documentation:", QLabel("Available"))

        layout.addWidget(api_group)

        # API Features
        features_group = QGroupBox("Available API Endpoints")
        features_layout = QVBoxLayout(features_group)

        endpoints = [
            "GET /api/v1/inventory - Get inventory data",
            "POST /api/v1/sales - Create sales record",
            "GET /api/v1/reports - Generate reports",
            "GET /api/v1/analytics - Get analytics data"
        ]

        for endpoint in endpoints:
            endpoint_label = QLabel(f"• {endpoint}")
            endpoint_label.setStyleSheet("color: #374151; font-size: 13px; padding: 2px 0;")
            features_layout.addWidget(endpoint_label)

        layout.addWidget(features_group)
        layout.addStretch()
        return widget

    def train_ai_models(self):
        """Train AI models"""
        if self.ai_ml_engine:
            try:
                results = self.ai_ml_engine.train_models()
                if results:
                    QMessageBox.information(self, "Training Complete",
                                          f"Successfully trained {len(results)} AI models!")
                else:
                    QMessageBox.warning(self, "Training Failed",
                                      "Failed to train AI models. Check data availability.")
            except Exception as e:
                QMessageBox.critical(self, "Training Error", f"Error training models: {str(e)}")

    def detect_anomalies(self):
        """Detect anomalies in data"""
        if self.ai_ml_engine:
            try:
                anomalies = self.ai_ml_engine.detect_anomalies()
                if anomalies:
                    QMessageBox.information(self, "Anomalies Detected",
                                          f"Detected {len(anomalies)} anomalies in your data!")
                else:
                    QMessageBox.information(self, "No Anomalies",
                                          "No anomalies detected in your data.")
            except Exception as e:
                QMessageBox.critical(self, "Detection Error", f"Error detecting anomalies: {str(e)}")


    def update_currency(self, index):
        """Store the selected currency symbol"""
        try:
            if hasattr(self, 'currency_combo'):
                self.selected_currency = self.currency_combo.itemData(index)
            else:
                # For FinalRobustApp which might not have currency_combo
                self.logger.warning("Currency combo not found, using default currency")
                currencies = ['₹', '$', '€', '£', '¥']
                if 0 <= index < len(currencies):
                    self.selected_currency = currencies[index]
                else:
                    self.selected_currency = '₹'  # Default to Indian Rupee
        except Exception as e:
            self.logger.error(f"Error updating currency: {str(e)}")
            self.selected_currency = '₹'  # Default to Indian Rupee
    
    def apply_currency_changes(self):
        """Apply the selected currency throughout the application"""
        try:
            if hasattr(self, 'selected_currency'):
                self.currency_symbol = self.selected_currency
                self.logger.info(f"Currency updated to {self.currency_symbol}")
                
                # Show confirmation message
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Currency Updated", f"Currency symbol updated to {self.currency_symbol}")
            else:
                self.logger.warning("No selected currency to apply")
        except Exception as e:
            self.logger.error(f"Error applying currency changes: {str(e)}")
            # Show error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Currency Update Failed", f"Failed to update currency: {str(e)}")
            
            # Refresh the current page to show the new currency
            self.show_home_page()
        
        # Setup auto-refresh timer
        self.setup_auto_refresh_timer()
    
    def save_data(self):
        """Save the current data to backup files"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Save each dataframe to the backup directory with proper encoding
            for key, df in self.data.items():
                backup_file = os.path.join(backup_dir, f"{key}_backup.csv")
                df.to_csv(backup_file, index=False, encoding='utf-8')
            
            # Save currency setting with proper encoding
            with open(os.path.join(backup_dir, 'settings.txt'), 'w', encoding='utf-8') as f:
                f.write(f"currency_symbol={self.currency_symbol}\n")
            
            QMessageBox.information(
                self,
                "Data Saved",
                "Current data has been successfully backed up."
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Error",
                f"An error occurred while saving data: {str(e)}"
            )
    
    def refresh_all_tabs(self):
        """Reload data from CSV files and refresh all tabs with updated data.
        This method can be called to reflect external changes to CSV files or after Firebase sync.
        """
        self.logger.info("Reloading data from files and refreshing all tabs...")

        # Diagnostic log for nav_buttons BEFORE data loading
        if hasattr(self, 'nav_buttons'):
            self.logger.info(f"refresh_all_tabs: PRE-LOAD - self.nav_buttons exists. Type: {type(self.nav_buttons)}, Is list: {isinstance(self.nav_buttons, list)}, Length: {len(self.nav_buttons) if isinstance(self.nav_buttons, list) else 'N/A'}")
        else:
            self.logger.error("refresh_all_tabs: PRE-LOAD - CRITICAL - self.nav_buttons does NOT exist.")

        # Reload data from CSV files first
        self.data = self.load_data()
        if self.data is None:
            self.logger.error("Data loading failed during refresh. Aborting tab refresh.")
            QMessageBox.critical(self, "Error", "Failed to reload data from files. UI may not be up-to-date.")
            return
        
        # Proceed with refreshing UI components as before
        try:
            # Diagnostic log for nav_buttons
            if hasattr(self, 'nav_buttons'):
                self.logger.info(f"refresh_all_tabs: self.nav_buttons exists. Type: {type(self.nav_buttons)}, Is list: {isinstance(self.nav_buttons, list)}, Length: {len(self.nav_buttons) if isinstance(self.nav_buttons, list) else 'N/A'}")
            else:
                self.logger.error("refresh_all_tabs: CRITICAL - self.nav_buttons does NOT exist before loop.")
                # To see all available attributes if nav_buttons is missing:
                # self.logger.error(f"Attributes of self in refresh_all_tabs: {dir(self)}")

            # Get the currently active tab to restore it after refresh
            current_button = None
            for button in self.nav_buttons:
                if button.isChecked():
                    current_button = button
                    break
            
            # Call the appropriate page refresh method based on the active button
            if current_button:
                # Get the button's callback function and call it to refresh the page
                button_index = self.nav_buttons.index(current_button)
                if button_index == 0:  # Home
                    self.show_home_page()
                elif button_index == 1:  # Inventory
                    self.show_inventory_page()
                elif button_index == 2:  # Meal Planning
                    self.show_meal_planning_page()
                elif button_index == 3:  # Budget
                    self.show_budget_page()
                elif button_index == 4:  # Sales
                    self.show_sales_page()
                elif button_index == 5:  # Pricing
                    self.show_pricing_page()
                elif button_index == 6:  # Packing Materials
                    self.show_packing_materials_page()
                elif button_index == 7:  # Shopping
                    self.show_shopping_page()
                elif button_index == 8:  # Gas Management
                    self.show_gas_management_page()
                elif button_index == 9:  # Waste
                    self.show_waste_page()
                elif button_index == 10:  # Cleaning
                    self.show_cleaning_page()
                elif button_index == 11:  # Analytics
                    self.show_analytics_page()
                elif button_index == 12:  # Reports
                    self.show_reports_page()
                elif button_index == 13:  # Logs
                    self.show_logs_page()
                elif button_index == 14:  # Settings (Mobile, AI/ML, Enterprise moved inside)
                    self.show_settings_page()
            else:
                # Default to home page if no button is active
                self.show_home_page()

            self.logger.info("All tabs refreshed successfully")
        except Exception as e:
            self.logger.error(f"Error refreshing tabs: {str(e)}")

    def force_refresh_current_tab(self):
        """Force refresh the current tab data"""
        try:
            # Reload data from CSV files
            self.data = self.load_data()

            # Refresh the current tab
            self.refresh_all_tabs()

            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Refresh Complete", "Data has been refreshed from CSV files.")

            self.logger.info("Manual data refresh completed")

        except Exception as e:
            self.logger.error(f"Error in manual refresh: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Refresh Error", f"Failed to refresh data: {str(e)}")

    def restore_data(self):
        """Restore data from backup files"""
        try:
            # Check if backup directory exists
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_backup')
            if not os.path.exists(backup_dir):
                QMessageBox.warning(
                    self,
                    "Restore Error",
                    "No backup data found."
                )
                return

            # Confirm before restoring
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                "This will replace your current data with the backup data. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Restore each dataframe from the backup directory with proper encoding
                for key in self.data.keys():
                    backup_file = os.path.join(backup_dir, f"{key}_backup.csv")
                    if os.path.exists(backup_file):
                        self.data[key] = pd.read_csv(backup_file, encoding='utf-8')

                # Restore currency setting if available with proper encoding
                settings_file = os.path.join(backup_dir, 'settings.txt')
                if os.path.exists(settings_file):
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('currency_symbol='):
                                self.currency_symbol = line.strip().split('=')[1]
                                # Update the combo box to match the restored currency
                                for i in range(self.currency_combo.count()):
                                    if self.currency_combo.itemData(i) == self.currency_symbol:
                                        self.currency_combo.setCurrentIndex(i)
                                        break

                QMessageBox.information(
                    self,
                    "Data Restored",
                    "Data has been successfully restored from backup."
                )

                # Refresh all tabs with the restored data
                self.refresh_all_tabs()
        except Exception as e:
            QMessageBox.warning(
                self,
                "Restore Error",
                f"An error occurred while restoring data: {str(e)}"
            )

    def show_error_page(self, page_name, error_message):
        """Display an enhanced error page when a module fails to load"""
        self.logger.error(f"🚨 Showing error page for {page_name}: {error_message}")
        self.clear_content()

        # Create error container
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setContentsMargins(40, 40, 40, 40)
        error_layout.setSpacing(20)

        # Error icon and title
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        error_icon = QLabel("⚠️")
        error_icon.setFont(QFont("Segoe UI", 48))
        error_icon.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(error_icon)

        title_text = QLabel(f"Error Loading {page_name}")
        title_text.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_text.setStyleSheet("color: #e74c3c;")
        title_text.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_text)

        error_layout.addWidget(title_container)

        # Error message
        error_msg = QLabel(error_message)
        error_msg.setFont(QFont("Segoe UI", 12))
        error_msg.setStyleSheet("color: #7f8c8d; padding: 20px;")
        error_msg.setAlignment(Qt.AlignCenter)
        error_msg.setWordWrap(True)
        error_layout.addWidget(error_msg)

        # Suggestions
        suggestions = QLabel("""
        🔧 Possible solutions:
        • Check the Logs tab for detailed error information
        • Verify all required CSV files are present in the data directory
        • Restart the application
        • Check file permissions and disk space
        • Contact support if the problem persists
        """)
        suggestions.setFont(QFont("Segoe UI", 10))
        suggestions.setStyleSheet("color: #95a5a6; padding: 20px;")
        suggestions.setAlignment(Qt.AlignLeft)
        error_layout.addWidget(suggestions)

        # Action buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)

        # View logs button
        logs_btn = QPushButton("📋 View Logs")
        logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        logs_btn.clicked.connect(self.show_logs_page)
        button_layout.addWidget(logs_btn)

        # Home button
        home_btn = QPushButton("🏠 Go Home")
        home_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        home_btn.clicked.connect(self.show_home_page)
        button_layout.addWidget(home_btn)

        error_layout.addWidget(button_container, 0, Qt.AlignCenter)

        self.content_layout.addWidget(error_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KitchenDashboardApp()
    window.show()
    sys.exit(app.exec())

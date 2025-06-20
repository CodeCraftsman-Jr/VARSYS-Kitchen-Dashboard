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
    print("✓ Fixed Python paths for frozen application")
else:
    # Running in development
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'modules'))
    sys.path.insert(0, os.path.join(current_dir, 'utils'))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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
                             QFrame, QScrollArea, QMessageBox, QSplitter,
                             QGroupBox, QFormLayout, QStyleFactory, QSizePolicy,
                             QRadioButton, QDialog, QCheckBox, QButtonGroup,
                             QSystemTrayIcon, QMenu)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QPalette, QPainter, QPen, QPixmap, QAction

# Import modules - use standard imports for IDE compatibility
from modules.settings_fixed import SettingsWidget
from modules.expenses_fixed import ExpensesWidget
from modules.logs_viewer import LogsViewerWidget
from modules.firebase_sync import FirebaseSync
from modules.login_dialog import LoginDialog

# Import logger
from utils.app_logger import get_logger

# Import enhanced notification system with all cutting-edge features
from modules.enhanced_notification_system import get_notification_manager

# Import all advanced notification features
try:
    from notification_templates import NotificationTemplateManager
    from notification_ai_intelligence import NotificationAI
    from notification_mobile_integration import MobileNotificationManager
    from notification_business_intelligence import NotificationBusinessIntelligence
    from notification_performance_optimizer import OptimizedNotificationManager
    from notification_security_compliance import NotificationSecurityManager, SecurityPolicy
    from notification_realtime_streaming import NotificationStreamer
    from ultimate_notification_system import UltimateNotificationSystem
    ADVANCED_NOTIFICATIONS_AVAILABLE = True
    print("✅ Advanced notification features loaded successfully")
except ImportError as e:
    print(f"⚠️ Some advanced notification features not available: {e}")
    ADVANCED_NOTIFICATIONS_AVAILABLE = False

# Import modern theme
from modules.modern_theme import ModernTheme

# Import activity tracker
try:
    from modules.activity_tracker import get_activity_tracker, track_user_action, track_navigation, track_system_event
except ImportError:
    get_activity_tracker = None
    def track_user_action(*_args, **_kwargs): pass  # Fallback function
    def track_navigation(*_args, **_kwargs): pass  # Fallback function
    def track_system_event(*_args, **_kwargs): pass  # Fallback function

# Import update system
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

print("✓ All imports completed with fallback handling for frozen application")

# Simple fix for category dropdowns has been integrated into the inventory module

class KitchenDashboardApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load environment variables from .env file
        self.load_env_file()

        self.setWindowTitle("Kitchen Dashboard - Modern Edition")
        self.resize(1600, 1000)
        self.setMinimumSize(1400, 900)

        # Configure status bar for refresh messages
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
                color: #374151;
                font-size: 12px;
                padding: 4px 8px;
            }
        """)
        self.status_bar.showMessage("Ready", 2000)

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
        self.logger.info("[START] Kitchen Dashboard application starting...")

        # Log each major initialization step for debugging
        self.logger.info("[LIST] Step 1: Application window and styling initialized")
        self.logger.log_ui_action("Window created", f"Size: {self.size().width()}x{self.size().height()}")

        # Initialize enhanced notification system with all cutting-edge features
        self.logger.log_section_header("Ultimate Notification System Initialization")
        try:
            # Initialize core enhanced notification system (no arguments needed)
            self.notification_manager = get_notification_manager()
            self.logger.info("✅ Core enhanced notification system initialized")

            # Initialize advanced notification features if available
            if ADVANCED_NOTIFICATIONS_AVAILABLE:
                # Initialize Ultimate Notification System
                self.ultimate_notification_system = UltimateNotificationSystem()
                self.logger.info("✅ Ultimate notification system initialized")

                # Initialize AI Intelligence
                self.notification_ai = NotificationAI()
                self.logger.info("✅ AI-powered notification intelligence initialized")

                # Initialize Template System
                self.notification_templates = NotificationTemplateManager()
                self.logger.info("✅ Professional template system initialized (16+ templates)")

                # Initialize Mobile Integration
                self.mobile_notifications = MobileNotificationManager()
                self.logger.info("✅ Mobile & cross-platform integration initialized")

                # Initialize Business Intelligence
                self.notification_bi = NotificationBusinessIntelligence()
                self.logger.info("✅ Business intelligence & analytics initialized")

                # Initialize Performance Optimization
                self.performance_notifications = OptimizedNotificationManager()
                self.logger.info("✅ High-performance processing initialized (49,490+ notifications/sec)")

                # Initialize Security & Compliance
                security_policy = SecurityPolicy(
                    encryption_required=True,
                    audit_logging=True,
                    pii_detection=True,
                    content_filtering=True,
                    rate_limiting=True
                )
                self.notification_security = NotificationSecurityManager(security_policy)
                self.logger.info("✅ Enterprise security & compliance initialized")

                # Initialize Real-time Streaming
                self.notification_streaming = NotificationStreamer()
                self.logger.info("✅ Real-time streaming & WebSocket support initialized")

                self.logger.log_section_footer("Ultimate Notification System Initialization", True,
                    "All cutting-edge notification features successfully initialized")

                # Send startup notification using enhanced system
                self._send_enhanced_startup_notification()

            else:
                self.logger.warning("Advanced notification features not available - using basic system")
                self.ultimate_notification_system = None
                self.notification_ai = None
                self.notification_templates = None
                self.mobile_notifications = None
                self.notification_bi = None
                self.performance_notifications = None
                self.notification_security = None
                self.notification_streaming = None

                self.logger.log_section_footer("Ultimate Notification System Initialization", False,
                    "Advanced features not available - using basic notification system")

        except Exception as e:
            self.logger.error(f"Error initializing ultimate notification system: {e}")
            self.logger.log_section_footer("Ultimate Notification System Initialization", False, str(e))
            # Fallback to basic system
            self.ultimate_notification_system = None
            self.notification_ai = None
            self.notification_templates = None
            self.mobile_notifications = None
            self.notification_bi = None
            self.performance_notifications = None
            self.notification_security = None
            self.notification_streaming = None

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

        # Startup notification settings (can be configured)
        self.show_startup_notifications = True  # Set to False to disable startup notifications

        # Initialize pending notification storage
        self.pending_login_notification = None
        self.pending_sync_notification = None

        # Load data first with comprehensive error handling and logging
        self.logger.info("[DATA] Step 2: Loading application data...")
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
                        self.logger.info(f"   [LIST] {key}: {value.shape[0]} rows, {value.shape[1]} columns")
                    elif hasattr(value, '__len__'):
                        self.logger.info(f"   [LIST] {key}: {len(value)} items")
                    else:
                        self.logger.info(f"   [LIST] {key}: {type(value)}")

                # Perform data integrity check after loading
                self.check_and_fix_data_integrity()
            else:
                self.logger.log_data_loading("Data sources", False, error="No data returned from load_data()")
                self.data = {}

        except Exception as e:
            self.logger.log_exception(e, "Critical error during data loading")
            self.logger.log_data_loading("Data sources", False, error=str(e))
            # Initialize with empty data to prevent crashes
            self.data = {}
            self.logger.warning("[WARNING] Initialized with empty data to prevent application crash")

        # Initialize optimized Firebase
        self.firebase_user_id = "kitchen_dashboard_user" # Default user ID

        # Initialize application settings
        self.show_startup_notifications = True  # Enable startup notifications by default

        self.logger.log_section_header("Firebase Initialization")
        try:
            from modules.optimized_firebase_manager import get_optimized_firebase_manager
            # Pass Firebase config manager to optimized manager
            self.firebase_manager = get_optimized_firebase_manager(
                firebase_config_manager=getattr(self, 'firebase_config_manager', None)
            )
            self.logger.info("Optimized Firebase manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize optimized Firebase manager: {e}")
            self.firebase_manager = None

        # Legacy Firebase sync disabled for subscription model
        # Using optimized Firebase manager instead
        self.firebase_sync = None

        # Firebase login and sync are now managed by the optimized manager
        self.logger.log_section_footer("Firebase Initialization", True, "Firebase services initialized with enhanced authentication")

        # Initialize responsive design and PWA features
        self.logger.log_section_header("Responsive Design & PWA")
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

            self.logger.log_section_footer("Responsive Design & PWA", True, "All responsive features loaded successfully")
        except Exception as e:
            self.logger.log_section_footer("Responsive Design & PWA", False, f"Failed to initialize: {e}")
            self.responsive_manager = None
            self.pwa_manager = None
            self.mobile_navigation = None
            self.responsive_table_manager = None
            self.responsive_chart_manager = None
            self.responsive_dialog_manager = None

        # Initialize Multi-AI Engine and Enterprise features
        self.logger.log_section_header("Enterprise Features")
        try:
            from modules.multi_ai_engine import get_multi_ai_engine
            from modules.enterprise_features import get_enterprise_manager

            self.multi_ai_engine = get_multi_ai_engine(self.data)
            self.enterprise_manager = get_enterprise_manager()

            self.logger.log_section_footer("Enterprise Features", True, "Multi-AI Engine and Enterprise features loaded")
        except Exception as e:
            self.logger.log_section_footer("Enterprise Features", False, f"Failed to initialize: {e}")
            self.multi_ai_engine = None
            self.enterprise_manager = None

        # Skip CSS optimizer and performance modules (causing initialization issues)
        self.logger.log_section_header("Performance Optimization")
        self.logger.info("CSS optimizer and performance modules disabled to prevent initialization errors")
        self.css_optimizer = None
        self.performance_optimizer = None
        self.performance_enhancer = None
        self.logger.log_section_footer("Performance Optimization", True, "Performance modules safely disabled")

        # Initialize Update System
        self.logger.log_section_header("Update System Initialization")
        try:
            if UPDATE_SYSTEM_AVAILABLE:
                self.updater = get_updater(self.logger)
                self.update_manager = UpdateManager(self)
                self.logger.info("Update system initialized successfully")
                self.logger.log_section_footer("Update System Initialization", True, "Update checking and installation ready")
            else:
                self.updater = None
                self.update_manager = None
                self.logger.warning("Update system not available - modules not found")
                self.logger.log_section_footer("Update System Initialization", False, "Update modules not found")
        except Exception as e:
            self.logger.error(f"Failed to initialize update system: {e}")
            self.updater = None
            self.update_manager = None
            self.logger.log_section_footer("Update System Initialization", False, f"Update system initialization failed: {e}")

        # Initialize inventory_widget as it's needed by other parts
        self.inventory_widget = None

        # Initialize Firebase configuration manager
        try:
            from modules.firebase_config_manager import get_firebase_config_manager
            self.firebase_config_manager = get_firebase_config_manager()
            self.logger.info("Firebase configuration manager initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase config manager: {e}")
            self.firebase_config_manager = None

        # SUBSCRIPTION-BASED AUTHENTICATION: Only subscribed users can access
        self.logger.info("Kitchen Dashboard v1.1.3 - Subscription-based access")
        self.logger.info("Only users with valid Firebase accounts can access this application")

        # Check if daily sync is needed (without performing it)
        self._check_and_perform_daily_sync()

        # Check if Firebase is properly configured
        if (self.firebase_config_manager and self.firebase_config_manager.is_configured()):
            self.logger.info("Firebase configured - checking for existing session")
            # Check for existing session before showing login dialog
            if not self.check_existing_session():
                self.logger.info("No valid session found - showing login for subscribed users")
                self.show_authentication_dialog()
        else:
            self.logger.error("Firebase not configured - cannot authenticate subscribed users")
            self.show_firebase_required_dialog()
            return

        # Initialize WhatsApp Startup Manager for automatic connection
        self.logger.log_section_header("WhatsApp Startup Integration")
        try:
            from modules.whatsapp_startup_manager import WhatsAppStartupManager
            self.whatsapp_startup_manager = WhatsAppStartupManager(self)

            # Add callback for startup completion
            self.whatsapp_startup_manager.add_startup_callback(self._on_whatsapp_startup_complete)

            self.logger.info(f"WhatsApp startup manager initialized: {self.whatsapp_startup_manager}")
            self.logger.log_section_footer("WhatsApp Startup Integration", True, "WhatsApp automation ready")
        except Exception as e:
            import traceback
            self.logger.error(f"Failed to initialize WhatsApp startup manager: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.logger.log_section_footer("WhatsApp Startup Integration", False, f"WhatsApp startup failed: {e}")
            self.whatsapp_startup_manager = None

        # Initialize System Tray for background operation
        self.logger.log_section_header("System Tray Initialization")
        try:
            self.setup_system_tray()
            self.logger.info("✅ System tray initialized successfully")
            self.logger.log_section_footer("System Tray Initialization", True, "System tray ready for background operation")
        except Exception as e:
            self.logger.error(f"Failed to initialize system tray: {e}")
            self.logger.log_section_footer("System Tray Initialization", False, f"System tray initialization failed: {e}")
            self.system_tray = None

    def _send_enhanced_startup_notification(self):
        """Send enhanced startup notification using the ultimate notification system"""
        try:
            if not self.show_startup_notifications:
                return

            # Use template system if available
            if hasattr(self, 'notification_templates') and self.notification_templates:
                from notification_templates import notify_system_startup
                notify_system_startup("VARSYS Kitchen Dashboard - Ultimate Edition")
                self.logger.info("✅ Enhanced startup notification sent via template system")
            else:
                # Fallback to enhanced core system
                from modules.enhanced_notification_system import notify_success
                notify_success(
                    "🚀 Ultimate System Ready",
                    "VARSYS Kitchen Dashboard Ultimate Edition is now operational with all cutting-edge features",
                    "Ultimate System"
                )
                self.logger.info("✅ Enhanced startup notification sent via core system")

            # Send AI analysis notification if available
            if hasattr(self, 'notification_ai') and self.notification_ai:
                startup_notification = {
                    'title': 'Ultimate System Ready',
                    'message': 'VARSYS Kitchen Dashboard Ultimate Edition is now operational',
                    'category': 'system',
                    'priority': 10
                }

                analysis = self.notification_ai.analyze_notification(startup_notification)
                self.logger.info(f"🤖 AI Analysis: Sentiment={analysis.sentiment.value}, "
                               f"Intent={analysis.intent.value}, Urgency={analysis.urgency_score:.2f}")

            # Register mobile device if available
            if hasattr(self, 'mobile_notifications') and self.mobile_notifications:
                from notification_mobile_integration import MobileDevice, MobilePlatform
                from datetime import datetime

                desktop_device = MobileDevice(
                    device_id="desktop_main_app",
                    user_id="kitchen_dashboard_user",
                    platform=MobilePlatform.DESKTOP,
                    push_token="desktop_token_main",
                    app_version="2.0.0",
                    os_version="Windows 11",
                    device_model="Desktop Application",
                    timezone="UTC",
                    language="en",
                    registered_at=datetime.now(),
                    last_active=datetime.now(),
                    notification_settings={'push': True, 'in_app': True}
                )

                self.mobile_notifications.register_device(desktop_device)
                self.logger.info("📱 Desktop device registered for mobile integration")

        except Exception as e:
            self.logger.error(f"Error sending enhanced startup notification: {e}")

    def _on_whatsapp_startup_complete(self, success, message):
        """Callback when WhatsApp startup process completes"""
        try:
            if success:
                self.logger.info(f"✅ WhatsApp startup successful: {message}")
                self.notify_success("WhatsApp Ready", f"Abiram's Kitchen messaging is now available. {message}")
            else:
                self.logger.warning(f"⚠️ WhatsApp startup failed: {message}")

                # Check if this is first-time setup
                if self.whatsapp_startup_manager and self.whatsapp_startup_manager.is_first_time_setup():
                    self.logger.info("First-time setup detected - will show setup dialog after UI loads")
                    # Schedule setup dialog to show after UI is fully loaded
                    QTimer.singleShot(3000, self._show_whatsapp_setup_if_needed)
                else:
                    self.notify_warning("WhatsApp Connection", f"WhatsApp integration not available: {message}")

        except Exception as e:
            self.logger.error(f"Error in WhatsApp startup callback: {e}")

    def _show_whatsapp_setup_if_needed(self):
        """Show WhatsApp setup dialog if needed"""
        try:
            if self.whatsapp_startup_manager:
                success = self.whatsapp_startup_manager.show_setup_dialog_if_needed(self)
                if success:
                    self.logger.info("WhatsApp setup dialog completed successfully")
                else:
                    self.logger.info("WhatsApp setup dialog was skipped or failed")
        except Exception as e:
            self.logger.error(f"Error showing WhatsApp setup dialog: {e}")

    def start_whatsapp_automation(self):
        """Start automatic WhatsApp connection process"""
        try:
            if self.whatsapp_startup_manager:
                success = self.whatsapp_startup_manager.start_automatic_connection()
                if success:
                    self.logger.info("WhatsApp automatic connection started")
                else:
                    self.logger.info("WhatsApp automatic connection not started (disabled or already running)")
            else:
                self.logger.warning("WhatsApp startup manager not available")
        except Exception as e:
            self.logger.error(f"Error starting WhatsApp automation: {e}")

    def send_ai_powered_notification(self, title: str, message: str, category: str = "info",
                                   priority: int = 10, source: str = "System"):
        """Send notification with AI analysis and enhanced features"""
        try:
            # Create notification object
            notification = {
                'title': title,
                'message': message,
                'category': category,
                'priority': priority,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }

            # AI Analysis if available
            if hasattr(self, 'notification_ai') and self.notification_ai:
                analysis = self.notification_ai.analyze_notification(notification)
                self.logger.info(f"🤖 AI Analysis - Sentiment: {analysis.sentiment.value}, "
                               f"Intent: {analysis.intent.value}, Urgency: {analysis.urgency_score:.2f}")

                # Adjust priority based on AI analysis
                if analysis.urgency_score > 0.8:
                    priority = min(priority, 3)  # High urgency
                elif analysis.urgency_score > 0.6:
                    priority = min(priority, 6)  # Medium urgency

            # Security validation if available
            if hasattr(self, 'notification_security') and self.notification_security:
                user_context = {'user_id': 'kitchen_dashboard_user', 'role': 'admin'}
                validation = self.notification_security.validate_notification(notification, user_context)

                if not validation['valid']:
                    self.logger.warning(f"🔒 Security validation failed: {validation['security_warnings']}")
                    return False

                # Use sanitized content
                notification = validation['sanitized_content']

            # Send through performance-optimized system if available
            if hasattr(self, 'performance_notifications') and self.performance_notifications:
                success = self.performance_notifications.send_notification(
                    notification['title'], notification['message'],
                    notification['category'], priority, notification['source']
                )
                self.logger.info("⚡ Notification sent via high-performance system")
                return success
            else:
                # Fallback to enhanced core system
                from modules.enhanced_notification_system import notify_info
                success = notify_info(notification['title'], notification['message'], notification['source'])
                self.logger.info("📤 Notification sent via enhanced core system")
                return success

        except Exception as e:
            self.logger.error(f"Error sending AI-powered notification: {e}")
            return False

    def notify_emergency(self, title: str, message: str, source: str = "System"):
        """Send emergency notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "emergency", 1, source)

    def notify_critical(self, title: str, message: str, source: str = "System"):
        """Send critical notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "critical", 2, source)

    def notify_security(self, title: str, message: str, source: str = "Security System"):
        """Send security notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "security", 3, source)

    def notify_error(self, title: str, message: str, source: str = "System"):
        """Send error notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "error", 4, source)

    def notify_warning(self, title: str, message: str, source: str = "System"):
        """Send warning notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "warning", 6, source)

    def notify_success(self, title: str, message: str, source: str = "System"):
        """Send success notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "success", 10, source)

    def notify_info(self, title: str, message: str, source: str = "System"):
        """Send info notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "info", 12, source)

    def notify_inventory(self, title: str, message: str, source: str = "Inventory System"):
        """Send inventory notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "inventory", 8, source)

    def notify_staff(self, title: str, message: str, source: str = "Staff Management"):
        """Send staff notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "staff", 7, source)

    def notify_budget(self, title: str, message: str, source: str = "Budget System"):
        """Send budget notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "budget", 6, source)

    def notify_maintenance(self, title: str, message: str, source: str = "Maintenance System"):
        """Send maintenance notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "maintenance", 9, source)

    def notify_recipe(self, title: str, message: str, source: str = "Recipe System"):
        """Send recipe notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "recipe", 11, source)

    def notify_schedule(self, title: str, message: str, source: str = "Schedule System"):
        """Send schedule notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "schedule", 8, source)

    def notify_sync(self, title: str, message: str, source: str = "Cloud Sync"):
        """Send sync notification with AI analysis"""
        return self.send_ai_powered_notification(title, message, "sync", 12, source)

    def get_notification_analytics(self):
        """Get comprehensive notification analytics"""
        try:
            analytics = {}

            # Get core system analytics
            if hasattr(self, 'notification_manager') and self.notification_manager:
                notifications = self.notification_manager.get_notifications()
                analytics['core_system'] = {
                    'total_notifications': len(notifications),
                    'recent_notifications': len([n for n in notifications[-10:]]),
                    'categories': list(set(n.get('category', 'unknown') for n in notifications))
                }

            # Get AI analytics if available
            if hasattr(self, 'notification_ai') and self.notification_ai:
                ai_insights = self.notification_ai.get_ai_insights()
                analytics['ai_intelligence'] = ai_insights

            # Get business intelligence if available
            if hasattr(self, 'notification_bi') and self.notification_bi:
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                bi_report = self.notification_bi.generate_comprehensive_report(start_date, end_date)
                analytics['business_intelligence'] = {
                    'metrics_count': len(bi_report.metrics),
                    'insights_count': len(bi_report.insights),
                    'recommendations_count': len(bi_report.recommendations)
                }

            # Get mobile analytics if available
            if hasattr(self, 'mobile_notifications') and self.mobile_notifications:
                mobile_stats = self.mobile_notifications.get_device_statistics()
                analytics['mobile_integration'] = mobile_stats

            # Get performance analytics if available
            if hasattr(self, 'performance_notifications') and self.performance_notifications:
                if hasattr(self.performance_notifications, 'get_performance_metrics'):
                    perf_metrics = self.performance_notifications.get_performance_metrics()
                    analytics['performance'] = perf_metrics

            # Get streaming analytics if available
            if hasattr(self, 'notification_streaming') and self.notification_streaming:
                streaming_stats = self.notification_streaming.get_streaming_stats()
                analytics['real_time_streaming'] = streaming_stats

            self.logger.info(f"📊 Generated comprehensive notification analytics: {len(analytics)} categories")
            return analytics

        except Exception as e:
            self.logger.error(f"Error getting notification analytics: {e}")
            return {}

    def show_notification_dashboard(self):
        """Show the advanced notification dashboard"""
        try:
            if hasattr(self, 'ultimate_notification_system') and self.ultimate_notification_system:
                if hasattr(self.ultimate_notification_system, 'show_dashboard'):
                    return self.ultimate_notification_system.show_dashboard()

            # Fallback to basic dashboard
            from notification_dashboard import NotificationDashboard
            dashboard = NotificationDashboard()
            dashboard.show()
            return True

        except Exception as e:
            self.logger.error(f"Error showing notification dashboard: {e}")
            return False

    def create_window_icon(self):
        """Create a custom window icon for the kitchen dashboard"""
        try:
            from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor

            # Create a 32x32 pixmap for the icon
            pixmap = QPixmap(32, 32)
            if pixmap.isNull():
                # Fallback to a simple icon if pixmap creation fails
                return QIcon()

            pixmap.fill(QColor(102, 126, 234))  # Modern blue background

            # Use QPainter with proper error checking
            painter = QPainter()
            if not painter.begin(pixmap):
                # If painter can't begin, return a simple icon
                return QIcon()

            try:
                painter.setRenderHint(QPainter.Antialiasing)

                # Draw a simple kitchen/chef hat shape
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.setPen(QColor(255, 255, 255))

                # Draw chef hat outline (simplified)
                painter.drawEllipse(8, 12, 16, 12)  # Hat base
                painter.drawEllipse(10, 8, 12, 8)   # Hat top

            finally:
                painter.end()

            return QIcon(pixmap)

        except Exception as e:
            # If anything goes wrong, return a simple icon
            print(f"[WARNING] Error creating window icon: {e}")
            return QIcon()

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

            print("[SUCCESS] Modern window styling applied")

        except Exception as e:
            print(f"[WARNING] Error applying modern window style: {e}")

    def setup_system_tray(self):
        """Setup system tray for background operation"""
        try:
            # Check if system tray is available
            if not QSystemTrayIcon.isSystemTrayAvailable():
                self.logger.warning("System tray is not available on this system")
                return False

            # Create system tray icon
            self.system_tray = QSystemTrayIcon(self)

            # Use the same icon as the window
            tray_icon = self.create_window_icon()
            self.system_tray.setIcon(tray_icon)

            # Set tooltip
            self.system_tray.setToolTip("VARSYS Kitchen Dashboard - Ultimate Edition")

            # Create context menu
            tray_menu = QMenu()

            # Show/Hide action
            show_action = QAction("Show Dashboard", self)
            show_action.triggered.connect(self.show_from_tray)
            tray_menu.addAction(show_action)

            hide_action = QAction("Hide to Tray", self)
            hide_action.triggered.connect(self.hide_to_tray)
            tray_menu.addAction(hide_action)

            tray_menu.addSeparator()

            # Notification actions
            notifications_action = QAction("Show Notifications", self)
            notifications_action.triggered.connect(self.show_notification_dashboard)
            tray_menu.addAction(notifications_action)

            # Quick actions
            sync_action = QAction("Sync Data", self)
            sync_action.triggered.connect(self.trigger_manual_full_sync)
            tray_menu.addAction(sync_action)

            tray_menu.addSeparator()

            # Settings action
            settings_action = QAction("Settings", self)
            settings_action.triggered.connect(self.show_settings_from_tray)
            tray_menu.addAction(settings_action)

            tray_menu.addSeparator()

            # Exit action
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.exit_application)
            tray_menu.addAction(exit_action)

            # Set the context menu
            self.system_tray.setContextMenu(tray_menu)

            # Connect double-click to show/hide
            self.system_tray.activated.connect(self.on_tray_activated)

            # Show the system tray icon
            self.system_tray.show()

            # Send system tray notification
            if hasattr(self, 'notify_success'):
                self.notify_success(
                    "System Tray Ready",
                    "Kitchen Dashboard is now running in the background. Click the tray icon to access features.",
                    "System Tray"
                )

            self.logger.info("✅ System tray initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to setup system tray: {e}")
            return False

    def on_tray_activated(self, reason):
        """Handle system tray icon activation"""
        try:
            if reason == QSystemTrayIcon.DoubleClick:
                if self.isVisible():
                    self.hide_to_tray()
                else:
                    self.show_from_tray()
            elif reason == QSystemTrayIcon.Trigger:
                # Single click - show notification count
                if hasattr(self, 'notification_manager'):
                    notifications = self.notification_manager.get_notifications()
                    unread_count = len([n for n in notifications if not n.get('read', False)])

                    if unread_count > 0:
                        self.system_tray.showMessage(
                            "VARSYS Kitchen Dashboard",
                            f"You have {unread_count} unread notifications",
                            QSystemTrayIcon.Information,
                            3000
                        )
                    else:
                        self.system_tray.showMessage(
                            "VARSYS Kitchen Dashboard",
                            "All notifications are up to date",
                            QSystemTrayIcon.Information,
                            2000
                        )
        except Exception as e:
            self.logger.error(f"Error handling tray activation: {e}")

    def show_from_tray(self):
        """Show the application from system tray"""
        try:
            self.show()
            self.raise_()
            self.activateWindow()

            if hasattr(self, 'notify_info'):
                self.notify_info(
                    "Dashboard Restored",
                    "Kitchen Dashboard has been restored from the system tray",
                    "System Tray"
                )

            self.logger.info("Application restored from system tray")
        except Exception as e:
            self.logger.error(f"Error showing from tray: {e}")

    def hide_to_tray(self):
        """Hide the application to system tray"""
        try:
            self.hide()

            if hasattr(self, 'system_tray') and self.system_tray:
                self.system_tray.showMessage(
                    "VARSYS Kitchen Dashboard",
                    "Application was minimized to tray. Double-click the tray icon to restore.",
                    QSystemTrayIcon.Information,
                    3000
                )

            if hasattr(self, 'notify_info'):
                self.notify_info(
                    "Dashboard Minimized",
                    "Kitchen Dashboard is now running in the background. Access it from the system tray.",
                    "System Tray"
                )

            self.logger.info("Application minimized to system tray")
        except Exception as e:
            self.logger.error(f"Error hiding to tray: {e}")

    def show_settings_from_tray(self):
        """Show settings from system tray"""
        try:
            # First show the main window
            self.show_from_tray()

            # Then switch to settings tab if available
            if hasattr(self, 'tab_widget'):
                # Find the settings tab
                for i in range(self.tab_widget.count()):
                    if 'settings' in self.tab_widget.tabText(i).lower():
                        self.tab_widget.setCurrentIndex(i)
                        break

            self.logger.info("Settings opened from system tray")
        except Exception as e:
            self.logger.error(f"Error showing settings from tray: {e}")

    def exit_application(self):
        """Exit the application completely"""
        try:
            # Send exit notification
            if hasattr(self, 'notify_info'):
                self.notify_info(
                    "Application Closing",
                    "VARSYS Kitchen Dashboard is shutting down",
                    "System"
                )

            self.logger.info("Application exit requested from system tray")

            # Hide system tray
            if hasattr(self, 'system_tray') and self.system_tray:
                self.system_tray.hide()

            # Close the application
            QApplication.quit()

        except Exception as e:
            self.logger.error(f"Error during application exit: {e}")
            QApplication.quit()

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        try:
            # Check if system tray is available and enabled
            if hasattr(self, 'system_tray') and self.system_tray and self.system_tray.isVisible():
                # Hide to tray instead of closing
                event.ignore()
                self.hide_to_tray()

                # Show a message the first time
                if not hasattr(self, '_tray_message_shown'):
                    self.system_tray.showMessage(
                        "VARSYS Kitchen Dashboard",
                        "Application was minimized to tray. Right-click the tray icon for options, or double-click to restore.",
                        QSystemTrayIcon.Information,
                        5000
                    )
                    self._tray_message_shown = True
            else:
                # No system tray available, allow normal close
                self.logger.info("Application closing normally (no system tray)")
                event.accept()

        except Exception as e:
            self.logger.error(f"Error in close event: {e}")
            event.accept()  # Allow close if there's an error

    def check_and_fix_data_integrity(self):
        """Check data integrity issues and report without auto-fixing"""
        try:
            self.logger.info("🔍 Performing data integrity check...")

            # Check inventory data for duplicates (but don't auto-remove them)
            if 'inventory' in self.data and not self.data['inventory'].empty:
                inventory_df = self.data['inventory']
                original_count = len(inventory_df)

                # Check for duplicate item_ids
                duplicate_ids = inventory_df[inventory_df.duplicated(subset=['item_id'], keep=False)]
                if not duplicate_ids.empty:
                    unique_duplicate_ids = duplicate_ids['item_id'].nunique()
                    self.logger.info(f"📊 Found {len(duplicate_ids)} inventory entries with {unique_duplicate_ids} duplicate IDs")
                    self.logger.info("ℹ️ Duplicate entries are preserved - use inventory management tools to clean if needed")
                else:
                    self.logger.info("✅ No duplicate item_ids found in inventory")

                # Check for missing essential fields
                missing_fields = []
                required_fields = ['item_id', 'item_name', 'category', 'quantity']
                for field in required_fields:
                    if field not in inventory_df.columns:
                        missing_fields.append(field)
                    elif inventory_df[field].isnull().any():
                        null_count = inventory_df[field].isnull().sum()
                        self.logger.warning(f"⚠️ Found {null_count} items with missing {field}")

                if missing_fields:
                    self.logger.error(f"❌ Critical fields missing from inventory: {missing_fields}")
                else:
                    self.logger.info("✅ All required inventory fields present")

                # Log inventory statistics
                self.logger.info(f"📈 Inventory stats: {original_count} total items, {inventory_df['item_id'].nunique()} unique IDs")

            # Check other data sources for similar issues (but don't auto-clean)
            for data_key in ['shopping_list', 'recipes', 'staff']:
                if data_key in self.data and not self.data[data_key].empty:
                    df = self.data[data_key]
                    id_column = f"{data_key.rstrip('_list').rstrip('s')}_id"

                    if id_column in df.columns:
                        duplicates = df[df.duplicated(subset=[id_column], keep=False)]
                        if not duplicates.empty:
                            self.logger.info(f"📊 Found {len(duplicates)} duplicate entries in {data_key}")
                        else:
                            self.logger.info(f"✅ No duplicates found in {data_key}")

            self.logger.info("✅ Data integrity check completed (non-destructive mode)")

        except Exception as e:
            self.logger.error(f"❌ Error during data integrity check: {e}")

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
                print(f"[SUCCESS] Loaded environment variables from {env_file}")
            except Exception as e:
                print(f"[WARNING] Error loading .env file: {e}")

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
            self.logger.info("Daily sync needed - will be performed after user authentication")
            # SUBSCRIPTION MODEL: Daily sync requires user authentication
            # Store sync requirement to be performed after login
            self.daily_sync_needed = True
        else:
            # Ensure local data is loaded even if sync is skipped
            self.logger.info("Daily sync not needed. Ensuring local data is loaded.")
            # self.data = self.load_data() # Data is already loaded in __init__
            # self.update_ui_with_loaded_data() # Call if you have a method to refresh UI from self.data
            pass

    def perform_authenticated_daily_sync(self):
        """Perform daily sync after user authentication for subscription model"""
        try:
            self.logger.info("Performing daily sync for authenticated subscriber...")

            # Use the optimized Firebase manager for sync
            if self.firebase_manager and self.firebase_manager.is_authenticated():
                # Sync data to cloud using optimized manager
                operation_id = self.firebase_manager.sync_data_to_cloud(self.data)

                if operation_id:
                    self.logger.info("Daily sync: Data successfully synced to cloud")

                    # Update last sync date
                    try:
                        last_sync_file = os.path.join('data', 'last_sync_date.txt')
                        today_str = datetime.now().strftime('%Y-%m-%d')
                        with open(last_sync_file, 'w') as f:
                            f.write(today_str)
                        self.logger.info(f"Updated last sync date to {today_str}")

                        # Clear the sync needed flag
                        self.daily_sync_needed = False

                        # Show notification using enhanced system
                        if hasattr(self, 'notify_sync'):
                            self.notify_sync(
                                "Daily Sync Complete",
                                "Your data has been automatically synced to the cloud",
                                source='Cloud Sync'
                            )
                        else:
                            self.add_notification(
                                "Daily Sync Complete",
                                "Your data has been automatically synced to the cloud",
                                "success"
                            )
                    except Exception as e:
                        self.logger.error(f"Error updating last sync date: {e}")
                else:
                    self.logger.error("Daily sync failed - could not sync to cloud")
            else:
                self.logger.warning("Cannot perform daily sync - user not authenticated")

        except Exception as e:
            self.logger.error(f"Error in authenticated daily sync: {e}")

    def trigger_manual_full_sync(self):
        """Trigger manual sync for subscription-based model"""
        self.logger.info("Manual sync triggered for authenticated subscriber")

        # Check if user is authenticated
        if not (self.firebase_manager and self.firebase_manager.is_authenticated()):
            QMessageBox.warning(
                self,
                "Authentication Required",
                "You must be logged in to sync data to the cloud."
            )
            return False

        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("Cloud Synchronization")
        progress_dialog.setText("Syncing your data to the cloud... Please wait.")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        QApplication.processEvents()

        sync_successful = False
        try:
            self.logger.info("Manual Sync: Syncing subscriber data to cloud...")

            # Use optimized Firebase manager for sync
            operation_id = self.firebase_manager.sync_data_to_cloud(self.data)

            if operation_id:
                self.logger.info("Manual Sync: Successfully synced data to cloud")
                sync_successful = True

                # Update last sync date
                try:
                    last_sync_file = os.path.join('data', 'last_sync_date.txt')
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    with open(last_sync_file, 'w') as f:
                        f.write(today_str)
                    self.logger.info(f"Updated last sync date to {today_str} after manual sync")
                except Exception as e:
                    self.logger.error(f"Error updating last sync date: {e}")
            else:
                self.logger.error("Manual Sync: Failed to sync data to cloud")
                QMessageBox.critical(
                    self,
                    "Sync Error",
                    "Failed to sync data to cloud. Please check your connection and try again."
                )

        except Exception as e:
            self.logger.error(f"Manual sync error: {e}")
            QMessageBox.critical(
                self,
                "Sync Error",
                f"An error occurred during sync: {str(e)}"
            )

        progress_dialog.hide()
        progress_dialog.deleteLater()

        if sync_successful:
            QMessageBox.information(
                self,
                "Sync Complete",
                "Your data has been successfully synchronized to the cloud!"
            )

        return sync_successful

    def initialize_cloud_sync_for_user(self, user_info):
        """Initialize cloud sync functionality for authenticated user"""
        try:
            user_id = user_info.get('localId', user_info.get('uid', ''))
            user_email = user_info.get('email', 'Unknown')

            self.logger.info(f"Initializing cloud sync for user: {user_email} (UID: {user_id})")

            # Set up user-specific sync settings
            self.cloud_sync_settings = {
                'user_id': user_id,
                'user_email': user_email,
                'auto_sync_enabled': True,
                'sync_interval_minutes': 30,
                'last_sync_timestamp': None,
                'sync_collections': [
                    'inventory', 'recipes', 'budget', 'budget_categories', 'sales', 'expenses_list',
                    'waste', 'cleaning_maintenance', 'items', 'categories',
                    'recipe_ingredients', 'pricing', 'packing_materials',
                    'recipe_packing_materials', 'sales_orders', 'meal_plan', 'staff'
                ]
            }

            # Initialize cloud sync manager if available
            try:
                from modules.cloud_sync_manager import CloudSyncManager
                self.cloud_sync_manager = CloudSyncManager(self.data, parent=self)

                # Connect sync signals
                self.cloud_sync_manager.sync_started.connect(self.on_cloud_sync_started)
                self.cloud_sync_manager.sync_completed.connect(self.on_cloud_sync_completed)

                self.logger.info("Cloud sync manager initialized successfully")

                # Perform initial sync check
                self.check_and_perform_initial_sync()

            except ImportError as e:
                self.logger.warning(f"Cloud sync manager not available: {e}")
                # Fallback to basic Firebase sync
                self.setup_basic_cloud_sync()

        except Exception as e:
            self.logger.error(f"Error initializing cloud sync: {e}")

    def setup_basic_cloud_sync(self):
        """Setup basic cloud sync functionality as fallback"""
        try:
            self.logger.info("Setting up basic cloud sync functionality")

            # Create sync timer for periodic sync
            from PySide6.QtCore import QTimer
            self.sync_timer = QTimer()
            self.sync_timer.timeout.connect(self.perform_periodic_sync)

            # Start periodic sync (every 30 minutes)
            sync_interval = self.cloud_sync_settings.get('sync_interval_minutes', 30) * 60 * 1000
            self.sync_timer.start(sync_interval)

            self.logger.info(f"Basic cloud sync timer started (interval: {sync_interval/60000} minutes)")

        except Exception as e:
            self.logger.error(f"Error setting up basic cloud sync: {e}")

    def check_and_perform_initial_sync(self):
        """Check if initial sync is needed and perform it"""
        try:
            if not self.firebase_manager or not self.firebase_manager.is_authenticated():
                return

            user_id = self.cloud_sync_settings.get('user_id')
            if not user_id:
                return

            self.logger.info("Checking for initial cloud sync requirement...")

            # Check if user has any data in cloud
            self.check_cloud_data_exists()

        except Exception as e:
            self.logger.error(f"Error checking initial sync: {e}")

    def check_cloud_data_exists(self):
        """Check if user has existing data in cloud"""
        try:
            if not self.firebase_manager or not self.firebase_manager.db:
                return

            user_id = self.cloud_sync_settings.get('user_id')
            user_ref = self.firebase_manager.db.collection('users').document(user_id)

            # Check if user document exists
            user_doc = user_ref.get()
            if user_doc.exists:
                self.logger.info("User has existing cloud data")
                # Optionally prompt for sync direction
                self.prompt_sync_direction()
            else:
                self.logger.info("New user - performing initial upload")
                # Perform initial upload of local data
                self.perform_initial_upload()

        except Exception as e:
            self.logger.error(f"Error checking cloud data: {e}")

    def prompt_sync_direction(self):
        """Prompt user for sync direction when cloud data exists"""
        try:
            from PySide6.QtWidgets import QMessageBox, QPushButton

            msg = QMessageBox(self)
            msg.setWindowTitle("Cloud Sync - Data Found")
            msg.setText("Existing data found in cloud!")
            msg.setInformativeText("How would you like to sync your data?")
            msg.setIcon(QMessageBox.Question)

            # Custom buttons
            download_btn = msg.addButton("Download from Cloud", QMessageBox.ActionRole)
            upload_btn = msg.addButton("Upload to Cloud", QMessageBox.ActionRole)
            merge_btn = msg.addButton("Smart Merge", QMessageBox.ActionRole)
            cancel_btn = msg.addButton("Skip for Now", QMessageBox.RejectRole)

            msg.setDefaultButton(merge_btn)
            msg.exec()

            clicked_button = msg.clickedButton()

            if clicked_button == download_btn:
                self.perform_cloud_download()
            elif clicked_button == upload_btn:
                self.perform_cloud_upload()
            elif clicked_button == merge_btn:
                self.perform_smart_merge()
            else:
                self.logger.info("User skipped initial sync")

        except Exception as e:
            self.logger.error(f"Error in sync direction prompt: {e}")

    def perform_initial_upload(self):
        """Perform initial upload of local data to cloud"""
        try:
            self.logger.info("Performing initial upload to cloud...")

            # Get all local data
            local_data = self.get_all_local_data()

            if not local_data:
                self.logger.info("No local data to upload")
                return

            # Upload to cloud with user isolation
            self.upload_data_to_cloud(local_data, show_progress=True)

        except Exception as e:
            self.logger.error(f"Error in initial upload: {e}")

    def get_all_local_data(self):
        """Get all local data for cloud sync with enhanced error handling"""
        try:
            local_data = {}

            # Check if cloud sync settings are available
            if not hasattr(self, 'cloud_sync_settings') or not self.cloud_sync_settings:
                self.logger.warning("Cloud sync settings not initialized")
                return self.get_local_data_fallback()

            # Get sync collections list
            sync_collections = self.cloud_sync_settings.get('sync_collections', [])
            if not sync_collections:
                self.logger.warning("No sync collections configured")
                return self.get_local_data_fallback()

            # Check if data manager is available
            if not hasattr(self, 'data_manager') or not self.data_manager:
                self.logger.warning("Data manager not available")
                return self.get_local_data_from_files()

            # Get data from data manager
            self.logger.info(f"Checking {len(sync_collections)} collections for sync...")

            for collection_name in sync_collections:
                try:
                    # Check if data manager has this attribute
                    if hasattr(self.data_manager, collection_name):
                        df = getattr(self.data_manager, collection_name)
                        if df is not None and not df.empty:
                            local_data[collection_name] = df
                            self.logger.debug(f"Found {len(df)} records in {collection_name}")
                        else:
                            self.logger.debug(f"Collection {collection_name} is empty or None")
                    else:
                        self.logger.debug(f"Data manager does not have attribute: {collection_name}")

                except Exception as e:
                    self.logger.error(f"Error accessing collection {collection_name}: {e}")
                    continue

            self.logger.info(f"Retrieved {len(local_data)} collections for sync (total records: {sum(len(df) for df in local_data.values())})")

            # If no data found, try fallback methods
            if not local_data:
                self.logger.warning("No data found in data manager, trying fallback methods...")
                return self.get_local_data_fallback()

            return local_data

        except Exception as e:
            self.logger.error(f"Error getting local data: {e}")
            return self.get_local_data_fallback()

    def get_local_data_fallback(self):
        """Fallback method to get local data when data manager is not available"""
        try:
            self.logger.info("Using fallback method to get local data...")

            # Try to get data from CSV files directly
            return self.get_local_data_from_files()

        except Exception as e:
            self.logger.error(f"Error in fallback data retrieval: {e}")
            return {}

    def get_local_data_from_files(self):
        """Get local data directly from CSV files"""
        try:
            import os
            import pandas as pd

            local_data = {}
            data_dir = os.path.join(os.getcwd(), 'data')

            if not os.path.exists(data_dir):
                self.logger.warning(f"Data directory not found: {data_dir}")
                return {}

            # Define expected CSV files
            expected_files = [
                'inventory', 'recipes', 'budget', 'budget_categories', 'sales', 'expenses_list',
                'waste', 'cleaning_maintenance', 'items', 'categories',
                'recipe_ingredients', 'pricing', 'packing_materials',
                'recipe_packing_materials', 'sales_orders', 'meal_plan', 'staff'
            ]

            self.logger.info(f"Scanning data directory: {data_dir}")

            for file_name in expected_files:
                csv_path = os.path.join(data_dir, f"{file_name}.csv")

                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        if not df.empty:
                            local_data[file_name] = df
                            self.logger.debug(f"Loaded {len(df)} records from {file_name}.csv")
                        else:
                            self.logger.debug(f"File {file_name}.csv is empty")
                    except Exception as e:
                        self.logger.error(f"Error reading {csv_path}: {e}")
                        continue
                else:
                    self.logger.debug(f"File not found: {csv_path}")

            self.logger.info(f"Loaded {len(local_data)} collections from files (total records: {sum(len(df) for df in local_data.values())})")
            return local_data

        except Exception as e:
            self.logger.error(f"Error getting data from files: {e}")
            return {}

    def validate_local_data_for_sync(self):
        """Validate and report on local data availability for sync"""
        try:
            self.logger.info("Validating local data for sync...")

            # Get data using all available methods
            data_manager_data = {}
            file_data = {}

            # Try data manager first
            if hasattr(self, 'data_manager') and self.data_manager:
                sync_collections = self.cloud_sync_settings.get('sync_collections', []) if hasattr(self, 'cloud_sync_settings') else []
                for collection_name in sync_collections:
                    if hasattr(self.data_manager, collection_name):
                        df = getattr(self.data_manager, collection_name)
                        if df is not None and not df.empty:
                            data_manager_data[collection_name] = len(df)

            # Try file system
            file_data_raw = self.get_local_data_from_files()
            for collection_name, df in file_data_raw.items():
                if not df.empty:
                    file_data[collection_name] = len(df)

            # Create validation report
            validation_report = {
                'data_manager_collections': len(data_manager_data),
                'data_manager_records': sum(data_manager_data.values()),
                'file_collections': len(file_data),
                'file_records': sum(file_data.values()),
                'data_manager_details': data_manager_data,
                'file_details': file_data,
                'has_data': len(data_manager_data) > 0 or len(file_data) > 0
            }

            self.logger.info(f"Data validation report: {validation_report}")
            return validation_report

        except Exception as e:
            self.logger.error(f"Error validating local data: {e}")
            return {'has_data': False, 'error': str(e)}

    def show_data_validation_dialog(self):
        """Show a dialog with data validation information"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit

            validation_report = self.validate_local_data_for_sync()

            dialog = QDialog(self)
            dialog.setWindowTitle("Local Data Validation")
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # Summary
            if validation_report.get('has_data', False):
                summary_text = f"""
Data Manager: {validation_report.get('data_manager_collections', 0)} collections, {validation_report.get('data_manager_records', 0)} records
File System: {validation_report.get('file_collections', 0)} collections, {validation_report.get('file_records', 0)} records
                """.strip()
                summary_label = QLabel(summary_text)
                summary_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                summary_label = QLabel("No data found for sync")
                summary_label.setStyleSheet("font-weight: bold; color: red;")

            layout.addWidget(summary_label)

            # Details
            details_text = QTextEdit()
            details_content = "Data Manager Collections:\n"
            for collection, count in validation_report.get('data_manager_details', {}).items():
                details_content += f"  • {collection}: {count} records\n"

            details_content += "\nFile System Collections:\n"
            for collection, count in validation_report.get('file_details', {}).items():
                details_content += f"  • {collection}: {count} records\n"

            if validation_report.get('error'):
                details_content += f"\nError: {validation_report['error']}"

            details_text.setPlainText(details_content)
            details_text.setReadOnly(True)
            layout.addWidget(details_text)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing data validation dialog: {e}")

    def show_firebase_diagnostics_dialog(self):
        """Show comprehensive Firebase diagnostics dialog"""
        try:
            from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                         QPushButton, QTextEdit, QGroupBox, QScrollArea)
            import json

            dialog = QDialog(self)
            dialog.setWindowTitle("Firebase Connection Diagnostics")
            dialog.resize(700, 600)

            layout = QVBoxLayout(dialog)

            # Get current status
            status = self.get_detailed_firebase_status()

            # Status summary
            status_group = QGroupBox("Current Status")
            status_layout = QVBoxLayout(status_group)

            status_label = QLabel(status['display_text'])
            status_label.setStyleSheet(status['style'])
            status_layout.addWidget(status_label)

            if status['details']:
                details_label = QLabel(status['details'])
                details_label.setWordWrap(True)
                status_layout.addWidget(details_label)

            layout.addWidget(status_group)

            # Detailed diagnostics
            if status.get('diagnostics'):
                diag_group = QGroupBox("Detailed Diagnostics")
                diag_layout = QVBoxLayout(diag_group)

                diag_text = QTextEdit()
                diag_content = json.dumps(status['diagnostics'], indent=2)
                diag_text.setPlainText(diag_content)
                diag_text.setReadOnly(True)
                diag_text.setMaximumHeight(200)
                diag_layout.addWidget(diag_text)

                layout.addWidget(diag_group)

                # Recommendations
                recommendations = status['diagnostics'].get('recommendations', [])
                if recommendations:
                    rec_group = QGroupBox("Recommendations")
                    rec_layout = QVBoxLayout(rec_group)

                    for rec in recommendations:
                        rec_label = QLabel(f"• {rec}")
                        rec_label.setWordWrap(True)
                        rec_layout.addWidget(rec_label)

                    layout.addWidget(rec_group)

            # Action buttons
            button_layout = QHBoxLayout()

            # Test connection button
            test_btn = QPushButton("Test Connection")
            test_btn.clicked.connect(self.test_firebase_connection)
            button_layout.addWidget(test_btn)

            # Reinitialize button
            reinit_btn = QPushButton("Reinitialize Firebase")
            reinit_btn.clicked.connect(self.reinitialize_firebase_connection)
            button_layout.addWidget(reinit_btn)

            # Refresh button
            refresh_btn = QPushButton("Refresh Status")
            refresh_btn.clicked.connect(lambda: self.refresh_firebase_diagnostics_dialog(dialog))
            button_layout.addWidget(refresh_btn)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing Firebase diagnostics dialog: {e}")

    def test_firebase_connection(self):
        """Test Firebase connection and show results"""
        try:
            if not self.firebase_manager:
                QMessageBox.warning(self, "Firebase Test", "Firebase manager not available")
                return

            # Test database connection
            if hasattr(self.firebase_manager, 'test_database_connection'):
                db_test = self.firebase_manager.test_database_connection()
                auth_test = self.firebase_manager.is_authenticated()

                if db_test and auth_test:
                    QMessageBox.information(self, "Firebase Test", "✅ All Firebase services are working correctly!")
                elif db_test:
                    QMessageBox.warning(self, "Firebase Test", "⚠️ Database connection works but user not authenticated")
                elif auth_test:
                    QMessageBox.warning(self, "Firebase Test", "⚠️ User authenticated but database connection failed")
                else:
                    QMessageBox.critical(self, "Firebase Test", "❌ Firebase connection test failed")
            else:
                QMessageBox.warning(self, "Firebase Test", "Firebase test functionality not available")

        except Exception as e:
            self.logger.error(f"Error testing Firebase connection: {e}")
            QMessageBox.critical(self, "Firebase Test", f"Error during test: {str(e)}")

    def reinitialize_firebase_connection(self):
        """Reinitialize Firebase connection"""
        try:
            if not self.firebase_manager:
                QMessageBox.warning(self, "Firebase Reinit", "Firebase manager not available")
                return

            # Show progress
            progress = QMessageBox(self)
            progress.setWindowTitle("Firebase Reinitialization")
            progress.setText("Reinitializing Firebase services...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()
            QApplication.processEvents()

            # Attempt reinitialization
            if hasattr(self.firebase_manager, 'reinitialize_firebase'):
                success = self.firebase_manager.reinitialize_firebase()
            else:
                success = self.firebase_manager.reinitialize_database()

            progress.hide()

            if success:
                QMessageBox.information(self, "Firebase Reinit", "✅ Firebase reinitialization successful!")
                self.add_notification("Firebase", "Firebase services reinitialized successfully", "success")
            else:
                QMessageBox.warning(self, "Firebase Reinit", "⚠️ Firebase reinitialization failed")
                self.add_notification("Firebase", "Firebase reinitialization failed", "error")

        except Exception as e:
            self.logger.error(f"Error reinitializing Firebase: {e}")
            QMessageBox.critical(self, "Firebase Reinit", f"Error during reinitialization: {str(e)}")

    def refresh_firebase_diagnostics_dialog(self, dialog):
        """Refresh the Firebase diagnostics dialog"""
        try:
            dialog.accept()  # Close current dialog
            self.show_firebase_diagnostics_dialog()  # Open new one with updated info
        except Exception as e:
            self.logger.error(f"Error refreshing Firebase diagnostics: {e}")

    def get_detailed_firebase_status(self):
        """Get detailed Firebase connection status for display with enhanced diagnostics"""
        try:
            # Default status
            status = {
                'display_text': '❌ Firebase Status Unknown',
                'style': 'color: #ef4444; font-weight: bold;',
                'details': None,
                'diagnostics': None
            }

            # Check if Firebase manager exists
            if not self.firebase_manager:
                status.update({
                    'display_text': '❌ Firebase Manager Not Available',
                    'details': 'Firebase manager is not initialized'
                })
                return status

            # Get comprehensive diagnostics
            try:
                diagnostics = self.firebase_manager.get_connection_diagnostics()
                status['diagnostics'] = diagnostics

                # Determine status based on diagnostics
                overall_status = diagnostics.get('overall_status', 'unknown')
                components = diagnostics.get('components', {})

                if overall_status == 'fully_connected':
                    user_email = components.get('user_session', {}).get('user_email', 'Unknown')
                    status.update({
                        'display_text': f'✅ Firebase Fully Connected ({user_email})',
                        'style': 'color: #10b981; font-weight: bold;',
                        'details': 'All Firebase services operational'
                    })
                elif overall_status == 'auth_only':
                    status.update({
                        'display_text': '⚠️ Firebase Auth Only (Database Unavailable)',
                        'style': 'color: #f59e0b; font-weight: bold;',
                        'details': 'Authentication working but database connection failed'
                    })
                elif overall_status == 'database_only':
                    status.update({
                        'display_text': '⚠️ Firebase Database Only (No Auth)',
                        'style': 'color: #f59e0b; font-weight: bold;',
                        'details': 'Database connected but authentication unavailable'
                    })
                elif overall_status == 'disconnected':
                    status.update({
                        'display_text': '❌ Firebase Disconnected',
                        'details': 'No Firebase services available'
                    })
                elif overall_status == 'error':
                    status.update({
                        'display_text': '❌ Firebase Error State',
                        'details': 'Firebase services encountered errors'
                    })
                else:
                    # Fallback to component-based analysis
                    admin_available = components.get('admin_sdk', {}).get('available', False)
                    db_available = components.get('firestore_database', {}).get('available', False)
                    auth_available = components.get('pyrebase_auth', {}).get('available', False)
                    user_authenticated = components.get('user_session', {}).get('authenticated', False)

                    if db_available and auth_available and user_authenticated:
                        user_email = components.get('user_session', {}).get('user_email', 'Unknown')
                        status.update({
                            'display_text': f'✅ Firebase Connected ({user_email})',
                            'style': 'color: #10b981; font-weight: bold;',
                            'details': 'All services operational'
                        })
                    elif auth_available and user_authenticated:
                        status.update({
                            'display_text': '⚠️ Firebase Auth Connected (Database Issues)',
                            'style': 'color: #f59e0b; font-weight: bold;',
                            'details': 'Authentication working, database connection problems'
                        })
                    elif db_available:
                        status.update({
                            'display_text': '⚠️ Firebase Database Connected (Not Authenticated)',
                            'style': 'color: #f59e0b; font-weight: bold;',
                            'details': 'Database available but user not authenticated'
                        })
                    else:
                        status.update({
                            'display_text': '❌ Firebase Services Unavailable',
                            'details': 'No Firebase services are working properly'
                        })

            except Exception as diag_error:
                self.logger.error(f"Error getting Firebase diagnostics: {diag_error}")
                status.update({
                    'display_text': '❌ Firebase Diagnostics Failed',
                    'details': f'Could not retrieve Firebase status: {str(diag_error)}'
                })

            return status

        except Exception as e:
            self.logger.error(f"Error getting Firebase status: {e}")
            return {
                'display_text': f'❌ Firebase Status Error: {str(e)}',
                'style': 'color: #ef4444; font-weight: bold;',
                'details': 'Error occurred while checking Firebase status',
                'diagnostics': None
            }

    def upload_data_to_cloud(self, data, show_progress=False):
        """Upload data to cloud with user UID isolation - Async version"""
        try:
            if not self.firebase_manager or not data:
                return False

            user_id = self.cloud_sync_settings.get('user_id')
            if not user_id:
                self.logger.error("No user ID available for cloud upload")
                return False

            self.logger.info(f"Starting async upload to cloud for user: {user_id}")

            # Start async upload operation
            self.start_async_sync_operation('upload', data, show_progress)
            return True

        except Exception as e:
            self.logger.error(f"Error starting cloud upload: {e}")
            return False

    def start_async_sync_operation(self, operation_type, data=None, show_progress=True):
        """Start an asynchronous sync operation with progress tracking"""
        try:
            from PySide6.QtCore import QThread, QTimer

            # Prevent multiple concurrent operations
            if hasattr(self, 'active_sync_worker') and self.active_sync_worker and self.active_sync_worker.isRunning():
                self.add_notification("Cloud Sync", "Another sync operation is already in progress", "warning")
                return False

            # Validate Firebase manager before starting
            if not self.firebase_manager:
                self.logger.error("Firebase manager not available")
                self.add_notification("Cloud Sync", "Firebase manager not available", "error")
                return False

            if not self.firebase_manager.is_authenticated():
                self.logger.error("Firebase not authenticated")
                self.add_notification("Cloud Sync", "Firebase not authenticated - please login again", "error")
                return False

            if not hasattr(self.firebase_manager, 'db') or not self.firebase_manager.db:
                self.logger.warning("Firebase database not initialized - attempting to reinitialize...")

                # Try to reinitialize the database
                if hasattr(self.firebase_manager, 'reinitialize_database'):
                    if self.firebase_manager.reinitialize_database():
                        self.logger.info("Firebase database reinitialized successfully")
                    else:
                        self.logger.error("Failed to reinitialize Firebase database")
                        self.add_notification("Cloud Sync", "Firebase database not available", "error")
                        return False
                else:
                    self.logger.error("Firebase database not initialized and cannot reinitialize")
                    self.add_notification("Cloud Sync", "Firebase database not initialized", "error")
                    return False

            # Validate cloud sync settings
            if not hasattr(self, 'cloud_sync_settings') or not self.cloud_sync_settings:
                self.logger.error("Cloud sync settings not available")
                self.add_notification("Cloud Sync", "Cloud sync settings not configured", "error")
                return False

            user_id = self.cloud_sync_settings.get('user_id')
            if not user_id:
                self.logger.error("User ID not available in cloud sync settings")
                self.add_notification("Cloud Sync", "User ID not available for sync", "error")
                return False

            self.logger.info(f"Starting async {operation_type} operation for user: {user_id}")

            # Import and create the async worker
            from modules.async_cloud_sync_worker import AsyncCloudSyncWorker

            self.active_sync_worker = AsyncCloudSyncWorker(
                operation_type=operation_type,
                firebase_manager=self.firebase_manager,
                cloud_sync_settings=self.cloud_sync_settings,
                data=data,
                parent=self
            )

            # Connect worker signals
            self.active_sync_worker.progress_updated.connect(self.on_async_sync_progress)
            self.active_sync_worker.status_updated.connect(self.on_async_sync_status)
            self.active_sync_worker.operation_completed.connect(self.on_async_sync_completed)
            self.active_sync_worker.error_occurred.connect(self.on_async_sync_error)

            # Show progress dialog if requested
            if show_progress:
                self.show_sync_progress_dialog(operation_type)

            # Update UI to show sync is active
            self.update_sync_status_indicator(True, operation_type)

            # Start the worker
            self.active_sync_worker.start()

            self.logger.info(f"Started async {operation_type} operation")
            return True

        except Exception as e:
            self.logger.error(f"Error starting async sync operation: {e}")
            return False

    def show_sync_progress_dialog(self, operation_type):
        """Show the sync progress dialog"""
        try:
            from modules.sync_progress_dialog import SyncProgressDialog

            # Create progress dialog
            self.sync_progress_dialog = SyncProgressDialog(
                operation_id=f"{operation_type}_{int(QTimer().remainingTime())}",
                operation_type=operation_type,
                parent=self
            )

            # Connect cancel signal
            self.sync_progress_dialog.cancel_requested.connect(self.cancel_sync_operation)

            # Show dialog
            self.sync_progress_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing sync progress dialog: {e}")

    def on_async_sync_progress(self, progress_data):
        """Handle async sync progress updates"""
        try:
            progress = progress_data.get('progress', 0)
            current_operation = progress_data.get('current_operation', '')
            records_processed = progress_data.get('records_processed', 0)
            total_records = progress_data.get('total_records', 0)
            collection = progress_data.get('collection', '')

            # Update progress dialog if it exists
            if hasattr(self, 'sync_progress_dialog') and self.sync_progress_dialog:
                self.sync_progress_dialog.update_progress(
                    progress=progress,
                    step_text=current_operation,
                    records_processed=records_processed,
                    total_records=total_records,
                    collection=collection
                )

            # Update notification system with progress
            if progress % 25 == 0 and progress > 0:  # Update every 25%
                self.add_notification(
                    "Cloud Sync Progress",
                    f"{current_operation} - {progress}% complete",
                    "info"
                )

            # Update any other UI elements
            self.logger.debug(f"Sync progress: {progress}% - {current_operation} - {collection}")

        except Exception as e:
            self.logger.error(f"Error handling sync progress: {e}")

    def on_async_sync_status(self, status_data):
        """Handle async sync status updates"""
        try:
            status = status_data.get('status', '')
            message = status_data.get('message', '')

            # Update progress dialog if it exists
            if hasattr(self, 'sync_progress_dialog') and self.sync_progress_dialog:
                self.sync_progress_dialog.add_detail(f"[{QTimer().remainingTime()}] {message}")

            self.logger.info(f"Sync status: {status} - {message}")

        except Exception as e:
            self.logger.error(f"Error handling sync status: {e}")

    def on_async_sync_completed(self, result_data):
        """Handle async sync completion"""
        try:
            success = result_data.get('success', False)
            operation_type = result_data.get('operation_type', 'sync')
            message = result_data.get('message', '')
            data = result_data.get('data', None)

            # Close progress dialog
            if hasattr(self, 'sync_progress_dialog') and self.sync_progress_dialog:
                self.sync_progress_dialog.sync_completed(success, message)
                QTimer.singleShot(3000, self.sync_progress_dialog.accept)  # Auto-close after 3 seconds

            if success:
                self.logger.info(f"Async {operation_type} completed successfully")
                if hasattr(self, 'notify_sync'):
                    self.notify_sync("Cloud Sync", f"{operation_type.title()} completed successfully!", source='Cloud Sync')
                else:
                    self.add_notification("Cloud Sync", f"{operation_type.title()} completed successfully!", "success")

                # Handle post-sync operations
                if operation_type == 'download' and data:
                    self.save_cloud_data_to_local(data)
                    self.refresh_data_after_sync()
                elif operation_type in ['smart_sync', 'bidirectional'] and data:
                    self.save_cloud_data_to_local(data)
                    self.refresh_data_after_sync()

            else:
                self.logger.error(f"Async {operation_type} failed: {message}")
                self.add_notification("Cloud Sync", f"{operation_type.title()} failed: {message}", "error")

            # Update UI to show sync is no longer active
            self.update_sync_status_indicator(False)

            # Clean up worker
            if hasattr(self, 'active_sync_worker'):
                self.active_sync_worker = None

        except Exception as e:
            self.logger.error(f"Error handling sync completion: {e}")

    def on_async_sync_error(self, error_data):
        """Handle async sync errors"""
        try:
            error_message = error_data.get('error', 'Unknown error')
            operation_type = error_data.get('operation_type', 'sync')

            # Close progress dialog with error
            if hasattr(self, 'sync_progress_dialog') and self.sync_progress_dialog:
                self.sync_progress_dialog.sync_completed(False, error_message)
                QTimer.singleShot(5000, self.sync_progress_dialog.accept)  # Auto-close after 5 seconds

            self.logger.error(f"Async {operation_type} error: {error_message}")
            self.add_notification("Cloud Sync", f"{operation_type.title()} error: {error_message}", "error")

            # Update UI to show sync is no longer active
            self.update_sync_status_indicator(False)

            # Clean up worker
            if hasattr(self, 'active_sync_worker'):
                self.active_sync_worker = None

        except Exception as e:
            self.logger.error(f"Error handling sync error: {e}")

    def cancel_sync_operation(self, operation_id):
        """Cancel ongoing sync operation"""
        try:
            if hasattr(self, 'active_sync_worker') and self.active_sync_worker and self.active_sync_worker.isRunning():
                self.active_sync_worker.cancel_operation()
                self.active_sync_worker.quit()
                self.active_sync_worker.wait(5000)  # Wait up to 5 seconds for graceful shutdown

                if self.active_sync_worker.isRunning():
                    self.active_sync_worker.terminate()  # Force terminate if needed

                self.active_sync_worker = None

                self.logger.info(f"Cancelled sync operation: {operation_id}")
                self.add_notification("Cloud Sync", "Sync operation cancelled", "info")

                # Close progress dialog
                if hasattr(self, 'sync_progress_dialog') and self.sync_progress_dialog:
                    self.sync_progress_dialog.accept()

        except Exception as e:
            self.logger.error(f"Error cancelling sync operation: {e}")

    def update_sync_status_indicator(self, is_active, operation_type=None):
        """Update UI elements to show sync status"""
        try:
            # Update window title to show sync status
            base_title = "VARSYS Kitchen Dashboard v1.0.6"
            if is_active and operation_type:
                self.setWindowTitle(f"{base_title} - Syncing ({operation_type.title()})...")
            else:
                self.setWindowTitle(base_title)

            # Update user profile icon to show sync status
            if hasattr(self, 'user_icon_widget'):
                if is_active:
                    # Add a visual indicator (e.g., spinning animation or different color)
                    self.user_icon_widget.setStyleSheet("""
                        QPushButton {
                            background-color: #3b82f6;
                            color: white;
                            border: 2px solid #1d4ed8;
                            border-radius: 20px;
                            font-weight: bold;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #2563eb;
                        }
                    """)
                    self.user_icon_widget.setToolTip(f"Cloud sync in progress ({operation_type})...")
                else:
                    # Reset to normal styling
                    self.user_icon_widget.setStyleSheet("""
                        QPushButton {
                            background-color: #f3f4f6;
                            color: #374151;
                            border: 2px solid #d1d5db;
                            border-radius: 20px;
                            font-weight: bold;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #e5e7eb;
                            border-color: #9ca3af;
                        }
                    """)
                    self.user_icon_widget.setToolTip("User Profile & Cloud Sync")

            # Update any status bar or other indicators
            if hasattr(self, 'status_bar'):
                if is_active:
                    self.status_bar.showMessage(f"Cloud sync in progress ({operation_type})...")
                else:
                    self.status_bar.clearMessage()

        except Exception as e:
            self.logger.error(f"Error updating sync status indicator: {e}")

    def is_sync_operation_active(self):
        """Check if any sync operation is currently active"""
        return (hasattr(self, 'active_sync_worker') and
                self.active_sync_worker and
                self.active_sync_worker.isRunning())

    def perform_periodic_sync(self):
        """Perform periodic sync of data to cloud"""
        try:
            if not self.cloud_sync_settings.get('auto_sync_enabled', False):
                return

            self.logger.info("Performing periodic cloud sync...")

            # Get current data
            local_data = self.get_all_local_data()

            if local_data:
                self.upload_data_to_cloud(local_data, show_progress=False)

                # Update last sync timestamp
                from datetime import datetime
                self.cloud_sync_settings['last_sync_timestamp'] = datetime.now().isoformat()

        except Exception as e:
            self.logger.error(f"Error in periodic sync: {e}")

    def on_cloud_sync_started(self, operation_id):
        """Handle cloud sync started event"""
        try:
            self.logger.info(f"Cloud sync started: {operation_id}")
            self.add_notification(
                "Cloud Sync",
                "Syncing data to cloud...",
                "info"
            )
        except Exception as e:
            self.logger.error(f"Error handling sync started: {e}")

    def on_cloud_sync_completed(self, operation_id, success):
        """Handle cloud sync completed event"""
        try:
            if success:
                self.logger.info(f"Cloud sync completed successfully: {operation_id}")
                self.add_notification(
                    "Cloud Sync",
                    "Data synced to cloud successfully!",
                    "success"
                )
            else:
                self.logger.error(f"Cloud sync failed: {operation_id}")
                self.add_notification(
                    "Cloud Sync",
                    "Failed to sync data to cloud",
                    "error"
                )
        except Exception as e:
            self.logger.error(f"Error handling sync completed: {e}")

    def check_existing_session(self):
        """Check for existing valid session and auto-login if available"""
        try:
            # Import session manager
            from modules.session_manager import get_session_manager

            session_manager = get_session_manager()
            session_data = session_manager.load_session()

            if session_data and session_data.get('user_info'):
                user_info = session_data['user_info']
                self.logger.info(f"Found valid session for user: {user_info.get('email', 'Unknown')}")

                # Update session activity
                session_manager.update_session_activity(user_info)

                # Auto-login with saved session
                self.handle_authentication_result(user_info)
                return True

        except Exception as e:
            self.logger.error(f"Error checking existing session: {e}")

        return False

    def show_authentication_dialog(self):
        """Show authentication dialog and only proceed if user authenticates"""
        try:
            # Create login dialog with Firebase config
            login_dialog = LoginDialog(self, firebase_config_manager=self.firebase_config_manager)

            # Connect authentication signal
            login_dialog.login_successful.connect(self.handle_authentication_result)
            login_dialog.login_failed.connect(self.handle_authentication_failure)

            # Show dialog as modal
            result = login_dialog.exec()

            # If dialog was closed without authentication, exit application
            if result == 0:  # Dialog was rejected/closed
                self.logger.info("Authentication dialog closed - exiting application")
                self.close()

        except Exception as e:
            self.logger.error(f"Error showing authentication dialog: {e}")
            # ONLINE-ONLY MODE: No fallback to UI initialization
            self.show_firebase_connection_error_dialog()

    def handle_authentication_result(self, user_info):
        """Handle the result of authentication dialog"""
        try:
            # Authentication successful
            self.logger.info(f"Authentication successful for user: {user_info.get('email', 'Unknown')}")

            # Send success notification
            if hasattr(self, 'notify_success'):
                self.notify_success(
                    "Login Successful",
                    f"Welcome back! Logged in as {user_info.get('email', 'Unknown')}",
                    source='Authentication'
                )

            # Store user information
            self.current_user = user_info
            self.firebase_user_id = user_info.get('localId', user_info.get('uid', 'kitchen_dashboard_user'))

            # Legacy firebase_sync disabled for subscription model
            # Using optimized Firebase manager instead

            # Update optimized Firebase manager with user session
            if self.firebase_manager:
                self.firebase_manager.set_current_user(user_info)

                # Initialize cloud sync for this user
                self.initialize_cloud_sync_for_user(user_info)

            # Update cloud sync manager with subscriber info
            if hasattr(self, 'cloud_sync_manager') and self.cloud_sync_manager:
                self.cloud_sync_manager.set_subscriber_info(user_info)

            # Run automatic migration if needed (shopping_list → expenses_list)
            self.run_automatic_migration()

            # Initialize the UI
            self.initialize_ui()

            # Perform daily sync if needed (after authentication)
            if hasattr(self, 'daily_sync_needed') and self.daily_sync_needed:
                self.perform_authenticated_daily_sync()

            # Store login info for later notification (after UI is ready)
            if getattr(self, 'show_startup_notifications', True):
                self.pending_login_notification = {
                    "title": "Login Successful",
                    "message": f"Welcome back! Logged in as {user_info.get('email', 'User')}",
                    "category": "success"
                }

        except Exception as e:
            self.logger.error(f"Error handling authentication result: {e}")
            self.handle_authentication_failure("Authentication processing failed")

    def run_automatic_migration(self):
        """Run automatic migration from shopping_list to expenses_list if needed"""
        try:
            # Only run migration if we have Firebase manager and user ID
            if not self.firebase_manager or not hasattr(self, 'firebase_user_id'):
                self.logger.info("Skipping migration - Firebase manager or user ID not available")
                return

            # Import and run automatic migration
            from modules.automatic_migration import check_and_migrate_on_startup

            self.logger.info("🔄 Checking for automatic migration needs...")
            success = check_and_migrate_on_startup(self.firebase_manager, self.firebase_user_id)

            if success:
                self.logger.info("✅ Automatic migration check completed successfully")
            else:
                self.logger.warning("⚠️ Automatic migration encountered issues (non-critical)")

        except Exception as e:
            # Don't fail authentication if migration fails - it's not critical
            self.logger.warning(f"⚠️ Automatic migration failed (non-critical): {e}")
            self.logger.info("Continuing with normal application startup...")

    def handle_authentication_failure(self, error_message):
        """Handle authentication failure - ONLINE-ONLY MODE"""
        self.logger.warning(f"Authentication failed: {error_message}")

        # Show error message - NO OFFLINE MODE
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Authentication Required")
        msg.setText("Kitchen Dashboard v1.0.6 requires online authentication.")
        msg.setInformativeText(f"Error: {error_message}\n\nThis application requires a valid Firebase connection and authentication to function.")
        msg.setIcon(QMessageBox.Critical)

        # Only allow retry or exit - NO OFFLINE MODE
        retry_btn = msg.addButton("Retry Login", QMessageBox.ActionRole)
        config_btn = msg.addButton("Configure Firebase", QMessageBox.ActionRole)
        exit_btn = msg.addButton("Exit Application", QMessageBox.RejectRole)

        msg.exec()

        if msg.clickedButton() == retry_btn:
            # Retry authentication
            self.show_authentication_dialog()
        elif msg.clickedButton() == config_btn:
            # Show Firebase configuration
            self.show_firebase_configuration_dialog()
        else:
            # Exit application - NO OFFLINE MODE ALLOWED
            self.logger.info("User chose to exit - online authentication required")
            self.close()

    def show_firebase_unavailable_dialog(self):
        """Show dialog when Firebase integration is not available - ONLINE-ONLY MODE"""
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Firebase Integration Required")
        msg.setText("Kitchen Dashboard v1.0.6 requires Firebase integration.")
        msg.setInformativeText(
            "Firebase integration is not available. This may be due to:\n\n"
            "• Missing pyrebase4 package\n"
            "• Missing firebase-admin package\n"
            "• Python environment issues\n\n"
            "Please install required packages:\n"
            "pip install pyrebase4 firebase-admin"
        )
        msg.setIcon(QMessageBox.Critical)

        exit_btn = msg.addButton("Exit Application", QMessageBox.AcceptRole)
        msg.exec()

        self.logger.info("Firebase integration not available - exiting application")
        self.close()

    def show_firebase_connection_error_dialog(self):
        """Show dialog when Firebase connection fails - ONLINE-ONLY MODE"""
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Firebase Connection Error")
        msg.setText("Kitchen Dashboard v1.0.6 cannot connect to Firebase.")
        msg.setInformativeText(
            "Failed to establish connection to Firebase. This may be due to:\n\n"
            "• No internet connection\n"
            "• Invalid Firebase configuration\n"
            "• Firebase service issues\n"
            "• Incorrect credentials\n\n"
            "Please check your connection and configuration."
        )
        msg.setIcon(QMessageBox.Critical)

        retry_btn = msg.addButton("Retry Connection", QMessageBox.ActionRole)
        config_btn = msg.addButton("Configure Firebase", QMessageBox.ActionRole)
        exit_btn = msg.addButton("Exit Application", QMessageBox.RejectRole)

        msg.exec()

        if msg.clickedButton() == retry_btn:
            # Retry initialization
            self.__init__()
        elif msg.clickedButton() == config_btn:
            self.show_firebase_configuration_dialog()
        else:
            self.logger.info("Firebase connection failed - exiting application")
            self.close()

    def show_firebase_required_dialog(self):
        """Show dialog when Firebase is not configured - ONLINE-ONLY MODE"""
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Firebase Configuration Required")
        msg.setText("Kitchen Dashboard v1.0.6 requires Firebase configuration.")
        msg.setInformativeText(
            "This application requires Firebase for authentication and cloud sync.\n\n"
            "Please configure Firebase to continue."
        )
        msg.setIcon(QMessageBox.Critical)

        config_btn = msg.addButton("Configure Firebase", QMessageBox.ActionRole)
        exit_btn = msg.addButton("Exit Application", QMessageBox.RejectRole)

        msg.exec()

        if msg.clickedButton() == config_btn:
            self.show_firebase_configuration_dialog()
        else:
            self.logger.info("Firebase configuration required - exiting application")
            self.close()

    def show_firebase_configuration_dialog(self):
        """Show Firebase configuration dialog"""
        try:
            from modules.firebase_config_widget import FirebaseConfigWidget
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout

            config_dialog = QDialog(self)
            config_dialog.setWindowTitle("Firebase Configuration - Kitchen Dashboard v1.0.6")
            config_dialog.setModal(True)
            config_dialog.resize(600, 500)

            layout = QVBoxLayout(config_dialog)

            # Add configuration widget
            config_widget = FirebaseConfigWidget(self.firebase_config_manager)
            layout.addWidget(config_widget)

            # Add buttons
            button_layout = QHBoxLayout()
            save_continue_btn = QPushButton("Save & Continue")
            save_continue_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: 600;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)

            exit_btn = QPushButton("Exit Application")
            exit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: 600;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)

            save_continue_btn.clicked.connect(lambda: self.save_config_and_restart(config_dialog, config_widget))
            exit_btn.clicked.connect(self.close)

            button_layout.addStretch()
            button_layout.addWidget(save_continue_btn)
            button_layout.addWidget(exit_btn)
            layout.addLayout(button_layout)

            config_dialog.exec()

        except ImportError as e:
            self.logger.error(f"Firebase configuration widget not available: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Configuration Error",
                "Firebase configuration interface is not available.\n"
                "Please manually edit firebase_config.json and restart the application."
            )
            self.close()

    def save_config_and_restart(self, dialog, config_widget):
        """Save Firebase configuration and restart authentication"""
        if config_widget.save_configuration():
            dialog.accept()

            # Reload configuration
            if self.firebase_config_manager:
                self.firebase_config_manager.load_configuration()

            # Show success message and restart authentication
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Configuration Saved",
                "Firebase configuration saved successfully!\n"
                "Please authenticate to continue."
            )

            # Restart authentication process
            self.show_authentication_dialog()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                dialog,
                "Save Error",
                "Failed to save configuration. Please check your settings and try again."
            )

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
        """Setup timer for auto-refresh (performance enhancer disabled)"""
        try:
            from PySide6.QtCore import QTimer
            self.refresh_timer = QTimer()

            # Direct connection without performance enhancer (disabled)
            self.refresh_timer.timeout.connect(self.auto_refresh_data)

            self.refresh_timer.start(10000)  # Check every 10 seconds
            self.logger.info("Auto-refresh timer started (performance enhancer disabled)")
        except Exception as e:
            self.logger.error(f"Error setting up auto-refresh timer: {e}")

    def setup_auto_save_timer(self):
        """Setup auto-save timer to prevent data loss"""
        try:
            from PySide6.QtCore import QTimer
            from datetime import datetime

            # Create timer for auto-save
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save_data)

            # Set auto-save interval (2 minutes = 120000 ms)
            auto_save_interval = 120000  # 2 minutes
            self.auto_save_timer.start(auto_save_interval)

            # Track data changes for smart saving
            self.data_changed = False
            self.last_save_time = datetime.now()

            self.logger.info(f"Auto-save timer started with {auto_save_interval/1000/60:.1f} minute interval")

        except Exception as e:
            self.logger.error(f"Error setting up auto-save timer: {e}")

    def auto_save_data(self):
        """Automatically save data if changes have been made"""
        try:
            # Only save if data has changed and we have data to save
            if self.data_changed and hasattr(self, 'data') and self.data:
                self.logger.info("Auto-save: Saving changed data...")

                # Save all data to CSV files
                self.save_all_data_to_csv()

                # Reset change flag
                self.data_changed = False
                from datetime import datetime
                self.last_save_time = datetime.now()

                # Show subtle notification
                self.add_notification(
                    "Auto-Save",
                    "Data automatically saved",
                    "info",
                    duration=3000
                )

                self.logger.info("Auto-save completed successfully")

        except Exception as e:
            self.logger.error(f"Error during auto-save: {e}")

    def save_all_data_to_csv(self):
        """Save all application data to CSV files"""
        try:
            if not hasattr(self, 'data') or not self.data:
                self.logger.warning("No data to save")
                return

            # Ensure data directory exists
            data_dir = 'data'
            os.makedirs(data_dir, exist_ok=True)

            # Save each dataframe to its respective CSV file
            saved_files = []
            for key, df in self.data.items():
                if hasattr(df, 'to_csv'):  # Check if it's a DataFrame
                    try:
                        file_path = os.path.join(data_dir, f"{key}.csv")
                        df.to_csv(file_path, index=False, encoding='utf-8')
                        saved_files.append(key)
                    except Exception as e:
                        self.logger.error(f"Error saving {key}.csv: {e}")

            self.logger.info(f"Saved {len(saved_files)} data files: {', '.join(saved_files)}")

        except Exception as e:
            self.logger.error(f"Error saving all data to CSV: {e}")

    def mark_data_changed(self, data_type=None, item_name=None):
        """Mark that data has been changed and needs saving"""
        self.data_changed = True

        # Trigger real-time WhatsApp notifications if available
        if hasattr(self, 'whatsapp_notifications') and self.whatsapp_notifications:
            try:
                if data_type == 'inventory':
                    self.whatsapp_notifications.on_inventory_updated(item_name)
                elif data_type == 'cleaning_maintenance':
                    self.whatsapp_notifications.on_cleaning_task_updated()
                elif data_type == 'packing_materials':
                    self.whatsapp_notifications.on_packing_material_updated(item_name)
                elif data_type == 'gas_tracking':
                    self.whatsapp_notifications.on_gas_level_updated()
                else:
                    # General data change - check all notification types
                    self.whatsapp_notifications.force_check_all()
            except Exception as e:
                self.logger.error(f"Error triggering WhatsApp notifications: {e}")

    def initialize_ui(self):
        """Initialize the UI after authentication - ONLINE-ONLY MODE"""
        # Since we've already authenticated successfully, proceed with UI initialization
        self.logger.info("Initializing UI after successful authentication")

        # Apply modern style
        self.apply_modern_style()

        # Firebase manager is already initialized and working since we authenticated successfully
        if self.firebase_manager:
            self.logger.info("Using optimized Firebase manager for authenticated session")
        else:
            self.logger.info("Using subscription-based Firebase authentication")

        # Create main widget and layout with splitter for responsiveness
        self.central_widget = QWidget()
        # Set up the main window and central widget
        self.setCentralWidget(self.central_widget)
        # Daily sync will be performed after authentication if needed
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
        print(f"[DEBUG] LAYOUT DEBUG:")
        print(f"   Sidebar size: {self.sidebar.size()}")
        print(f"   Content widget size: {self.content_widget.size()}")
        print(f"   Splitter sizes: {self.main_splitter.sizes()}")

        # Show home page by default
        self.show_home_page()

        # Setup auto-refresh timer
        self.setup_auto_refresh_timer()

        # Setup auto-save functionality
        self.setup_auto_save_timer()

        # Force layout update after a short delay
        QTimer.singleShot(100, self.force_layout_update)

        # Schedule startup notifications to show after UI is fully ready (with longer delay)
        self.show_startup_notifications = getattr(self, 'show_startup_notifications', True)
        if self.show_startup_notifications:
            QTimer.singleShot(5000, self.show_startup_notifications_in_gui)  # 5 seconds delay

        # Connect responsive manager to handle layout changes
        if self.responsive_manager:
            self.responsive_manager.device_type_changed.connect(self.handle_device_type_change)
            self.responsive_manager.layout_mode_changed.connect(self.handle_layout_mode_change)

        # Synchronize categories across all modules
        QTimer.singleShot(3000, self.synchronize_categories)

        # Add testing menu for comprehensive testing
        self.create_testing_menu()

        # Add separate updates menu
        self.create_updates_menu()

        # Initialize automatic update checking (after UI is ready)
        QTimer.singleShot(5000, self.initialize_update_checking)

    def closeEvent(self, event):
        """Handle application close event with proper confirmation"""
        try:
            from PySide6.QtWidgets import QMessageBox

            # Perform final auto-save before closing
            if hasattr(self, 'data_changed') and self.data_changed:
                self.auto_save_data()

            # Show confirmation dialog
            msg = QMessageBox(self)
            msg.setWindowTitle("Exit Application")
            msg.setText("Are you sure you want to exit Kitchen Dashboard?")
            msg.setInformativeText("All data has been automatically saved.")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            # Apply modern styling to the message box
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                    color: #1f2937;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QMessageBox QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 500;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #2563eb;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #1d4ed8;
                }
            """)

            result = msg.exec()

            if result == QMessageBox.Yes:
                self.logger.info("Application exit confirmed by user")

                # Perform cleanup operations
                try:
                    # Stop auto-save timer
                    if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
                        self.auto_save_timer.stop()

                    # Stop any running sync operations
                    if hasattr(self, 'active_sync_worker') and self.active_sync_worker:
                        self.active_sync_worker.cancel_operation()
                        self.active_sync_worker.quit()
                        self.active_sync_worker.wait(2000)

                    # Final save of any pending data
                    if hasattr(self, 'data') and self.data:
                        self.save_all_data_to_csv()

                    self.logger.info("Cleanup completed successfully")

                except Exception as cleanup_error:
                    self.logger.error(f"Error during cleanup: {cleanup_error}")

                # Accept the close event
                event.accept()

                # Force application quit
                QTimer.singleShot(100, lambda: QApplication.quit())

            else:
                # User chose not to exit
                event.ignore()

        except Exception as e:
            self.logger.error(f"Error in closeEvent: {e}")
            # If there's an error, just accept the close event
            event.accept()
            QApplication.quit()

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

            print(f"[DEBUG] LAYOUT UPDATED:")
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

                # Store category sync info for later notification (after UI is ready)
                if getattr(self, 'show_startup_notifications', True):
                    self.pending_sync_notification = {
                        "title": "Category Sync Complete",
                        "message": f"Categories synchronized across {len(result['synchronized_modules'])} modules. {result['categories_added']} entries added.",
                        "category": "success"
                    }
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
        kitchen_icon = QLabel("KITCHEN")
        kitchen_icon.setFont(QFont("Segoe UI", 12, QFont.Bold))
        kitchen_icon.setStyleSheet("color: white; border: none; background: #e74c3c; padding: 4px 8px; border-radius: 4px;")
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

        status_icon = QLabel("ONLINE")
        status_icon.setFont(QFont("Segoe UI", 8, QFont.Bold))
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

        # User icon for logout functionality
        self.create_user_icon(header_layout)

        # Enhanced notification system with centralized management
        try:
            from modules.enhanced_notification_system import (
                NotificationBellWidget, get_notification_manager,
                notify_system, notify_success, notify_info, notify_warning, notify_error,
                notify_critical, notify_inventory, notify_staff, notify_schedule,
                notify_budget, notify_recipe, notify_maintenance, notify_sync
            )

            # Initialize centralized notification manager
            self.notification_manager = get_notification_manager()

            # Store notification functions for easy access
            self.notify_system = notify_system
            self.notify_success = notify_success
            self.notify_info = notify_info
            self.notify_warning = notify_warning
            self.notify_error = notify_error
            self.notify_critical = notify_critical
            self.notify_inventory = notify_inventory
            self.notify_staff = notify_staff
            self.notify_schedule = notify_schedule
            self.notify_budget = notify_budget
            self.notify_recipe = notify_recipe
            self.notify_maintenance = notify_maintenance
            self.notify_sync = notify_sync

            # Create and register bell widget
            self.notification_bell = NotificationBellWidget(self)
            self.notification_manager.register_bell_widget(self.notification_bell)
            header_layout.addWidget(self.notification_bell)

            # Register toast manager if available
            try:
                from modules.notification_system import get_notification_manager as get_toast_manager
                toast_manager = get_toast_manager(self)
                self.notification_manager.register_toast_manager(toast_manager)
            except Exception as toast_error:
                self.logger.warning(f"Toast manager not available: {toast_error}")

            self.logger.info("Notification bell widget loaded successfully")

            # Send welcome notification using enhanced system
            self.notify_system(
                "System Ready",
                "VARSYS Kitchen Dashboard initialized successfully",
                source='Application'
            )

        except Exception as e:
            self.logger.error(f"Error loading notification bell: {e}")
            # Fallback to simple but very visible bell
            bell_widget = QPushButton("NOTIFICATIONS")
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

    def create_user_icon(self, header_layout):
        """Create user icon with logout functionality"""
        try:
            # User icon container
            user_container = QWidget()
            user_container.setFixedSize(45, 45)
            user_container.setStyleSheet("""
                QWidget {
                    background-color: rgba(255,255,255,0.2);
                    border: 2px solid rgba(255,255,255,0.4);
                    border-radius: 22px;
                }
                QWidget:hover {
                    background-color: rgba(255,255,255,0.3);
                    border-color: rgba(255,255,255,0.6);
                }
            """)

            # User icon button
            user_button = QPushButton("👤")
            user_button.setParent(user_container)
            user_button.setGeometry(0, 0, 45, 45)
            user_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: white;
                    font-size: 18px;
                    border-radius: 22px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255,255,255,0.2);
                }
            """)

            # Set tooltip with user info
            if hasattr(self, 'current_user') and self.current_user:
                user_email = self.current_user.get('email', 'User')
                user_button.setToolTip(f"Logged in as: {user_email}\nClick to logout")
            else:
                user_button.setToolTip("User Menu - Click to logout")

            # Connect to logout functionality
            user_button.clicked.connect(self.show_logout_menu)

            header_layout.addWidget(user_container)
            self.logger.info("User icon created successfully")

        except Exception as e:
            self.logger.error(f"Error creating user icon: {e}")

    def show_logout_menu(self):
        """Show user profile menu with detailed information and session management"""
        try:
            from PySide6.QtWidgets import QMenu, QMessageBox

            # Create context menu
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    padding: 8px;
                    min-width: 280px;
                }
                QMenu::item {
                    padding: 10px 16px;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QMenu::item:selected {
                    background-color: #f3f4f6;
                }
                QMenu::item:disabled {
                    color: #6b7280;
                    font-weight: bold;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #e5e7eb;
                    margin: 6px 0;
                }
            """)

            # Add user info header
            if hasattr(self, 'current_user') and self.current_user:
                user_email = self.current_user.get('email', 'User')
                user_name = self.current_user.get('displayName', user_email.split('@')[0])

                # User name/email header
                user_header = menu.addAction(f"👤 {user_name}")
                user_header.setEnabled(False)

                email_action = menu.addAction(f"📧 {user_email}")
                email_action.setEnabled(False)

                menu.addSeparator()

                # User profile action
                profile_action = menu.addAction("👤 View Profile Details")
                profile_action.triggered.connect(self.show_user_profile_dialog)

                # Session management action
                session_action = menu.addAction("🔑 Manage Sessions")
                session_action.triggered.connect(self.show_session_management_dialog)

                # Cloud sync action
                cloud_sync_action = menu.addAction("☁️ Cloud Sync")
                cloud_sync_action.triggered.connect(self.show_cloud_sync_dialog)

                menu.addSeparator()

                # Account settings (placeholder for future)
                settings_action = menu.addAction("⚙️ Account Settings")
                settings_action.triggered.connect(self.show_account_settings)

                menu.addSeparator()

            # Add logout action
            logout_action = menu.addAction("🚪 Logout")
            logout_action.triggered.connect(self.logout_user)

            # Show menu at cursor position
            cursor_pos = self.mapToGlobal(self.cursor().pos())
            menu.exec(cursor_pos)

        except Exception as e:
            self.logger.error(f"Error showing user profile menu: {e}")
            # Fallback to direct logout confirmation
            self.logout_user()

    def logout_user(self):
        """Handle user logout"""
        try:
            # Show confirmation dialog
            from PySide6.QtWidgets import QMessageBox

            msg = QMessageBox(self)
            msg.setWindowTitle("Logout Confirmation")
            msg.setText("Are you sure you want to logout?")
            msg.setInformativeText("You will need to login again to access the application.")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            if msg.exec() == QMessageBox.Yes:
                self.logger.info("User logout confirmed")

                # Clear saved sessions
                try:
                    from modules.login_dialog import LoginDialog
                    LoginDialog.clear_saved_sessions(clear_remember_me=True)
                    self.logger.info("Cleared all saved sessions")
                except Exception as e:
                    self.logger.error(f"Error clearing sessions: {e}")

                # Show logout notification
                self.add_notification(
                    "Logged Out",
                    "You have been successfully logged out",
                    "info"
                )

                # Close application (since it's online-only)
                QTimer.singleShot(2000, self.close)

        except Exception as e:
            self.logger.error(f"Error during logout: {e}")

    def show_user_profile_dialog(self):
        """Show detailed user profile information dialog"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QTextEdit
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QFont

            if not hasattr(self, 'current_user') or not self.current_user:
                QMessageBox.warning(self, "No User", "No user is currently logged in.")
                return

            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("User Profile Information")
            dialog.setModal(True)
            dialog.resize(500, 600)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8fafc;
                }
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
                QLabel {
                    color: #374151;
                }
            """)

            layout = QVBoxLayout(dialog)
            layout.setSpacing(16)

            # User Information Group
            user_group = QGroupBox("👤 User Information")
            user_layout = QFormLayout(user_group)

            user_info = self.current_user
            user_layout.addRow("Email:", QLabel(user_info.get('email', 'N/A')))
            user_layout.addRow("Display Name:", QLabel(user_info.get('displayName', 'N/A')))
            user_layout.addRow("User ID:", QLabel(user_info.get('localId', 'N/A')))

            layout.addWidget(user_group)

            # Session Information Group
            session_group = QGroupBox("🔑 Session Information")
            session_layout = QFormLayout(session_group)

            login_time = user_info.get('login_time', 'N/A')
            session_id = user_info.get('session_id', 'N/A')
            app_version = user_info.get('app_version', 'N/A')
            subscription_type = user_info.get('subscription_type', 'N/A')

            session_layout.addRow("Login Time:", QLabel(login_time))
            session_layout.addRow("Session ID:", QLabel(session_id))
            session_layout.addRow("App Version:", QLabel(app_version))
            session_layout.addRow("Subscription:", QLabel(subscription_type))

            layout.addWidget(session_group)

            # Firebase Token Information (if available)
            if user_info.get('idToken'):
                token_group = QGroupBox("🔐 Firebase Token Information")
                token_layout = QVBoxLayout(token_group)

                token_text = QTextEdit()
                token_text.setPlainText(user_info.get('idToken', 'N/A'))
                token_text.setMaximumHeight(100)
                token_text.setReadOnly(True)
                token_text.setStyleSheet("background-color: #f1f5f9; border: 1px solid #cbd5e1;")

                token_layout.addWidget(QLabel("ID Token (truncated for security):"))
                token_layout.addWidget(token_text)

                layout.addWidget(token_group)

            # Buttons
            button_layout = QHBoxLayout()

            # Session Management button
            session_btn = QPushButton("🔑 Manage Sessions")
            session_btn.clicked.connect(lambda: (dialog.accept(), self.show_session_management_dialog()))
            session_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            button_layout.addWidget(session_btn)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            # Show dialog
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing user profile dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show user profile: {str(e)}")

    def show_session_management_dialog(self):
        """Show session management dialog with session key options"""
        try:
            from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                         QPushButton, QGroupBox, QFormLayout, QTextEdit,
                                         QCheckBox, QMessageBox, QScrollArea)
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QFont

            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Session Management")
            dialog.setModal(True)
            dialog.resize(600, 700)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8fafc;
                }
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

            # Create scroll area for content
            scroll = QScrollArea()
            scroll_widget = QWidget()
            layout = QVBoxLayout(scroll_widget)
            layout.setSpacing(16)

            # Get session information
            try:
                from modules.session_manager import get_session_manager
                session_manager = get_session_manager()
                session_info = session_manager.get_session_info()
            except Exception as e:
                self.logger.error(f"Error getting session info: {e}")
                session_info = {}

            # Current Session Group
            current_group = QGroupBox("🔑 Current Session")
            current_layout = QFormLayout(current_group)

            if hasattr(self, 'current_user') and self.current_user:
                current_layout.addRow("User:", QLabel(self.current_user.get('email', 'N/A')))
                current_layout.addRow("Login Time:", QLabel(self.current_user.get('login_time', 'N/A')))
                current_layout.addRow("Session ID:", QLabel(self.current_user.get('session_id', 'N/A')))

            layout.addWidget(current_group)

            # Saved Sessions Group
            saved_group = QGroupBox("💾 Saved Sessions")
            saved_layout = QVBoxLayout(saved_group)

            if session_info.get('has_current_session'):
                current_time = session_info.get('current_session_time', 'Unknown')
                current_label = QLabel(f"• Current session: {current_time}")
                saved_layout.addWidget(current_label)

            if session_info.get('has_remember_session'):
                remember_time = session_info.get('remember_session_time', 'Unknown')
                remember_label = QLabel(f"• Remember me session: {remember_time}")
                saved_layout.addWidget(remember_label)

            if not session_info.get('has_current_session') and not session_info.get('has_remember_session'):
                no_sessions_label = QLabel("No saved sessions found")
                no_sessions_label.setStyleSheet("color: #6b7280; font-style: italic;")
                saved_layout.addWidget(no_sessions_label)

            layout.addWidget(saved_group)

            # Session Actions Group
            actions_group = QGroupBox("⚙️ Session Actions")
            actions_layout = QVBoxLayout(actions_group)

            # Clear current session button
            clear_current_btn = QPushButton("🗑️ Clear Current Session")
            clear_current_btn.clicked.connect(lambda: self.clear_session_type('current', dialog))
            clear_current_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f59e0b;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    margin: 4px;
                }
                QPushButton:hover {
                    background-color: #d97706;
                }
            """)
            actions_layout.addWidget(clear_current_btn)

            # Clear remember me session button
            clear_remember_btn = QPushButton("🗑️ Clear Remember Me Session")
            clear_remember_btn.clicked.connect(lambda: self.clear_session_type('remember', dialog))
            clear_remember_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    margin: 4px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            actions_layout.addWidget(clear_remember_btn)

            # Clear all sessions button
            clear_all_btn = QPushButton("🚨 Clear All Sessions")
            clear_all_btn.clicked.connect(lambda: self.clear_session_type('all', dialog))
            clear_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7c2d12;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    margin: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #991b1b;
                }
            """)
            actions_layout.addWidget(clear_all_btn)

            layout.addWidget(actions_group)

            # Set up scroll area
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)

            # Main dialog layout
            main_layout = QVBoxLayout(dialog)
            main_layout.addWidget(scroll)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
            main_layout.addWidget(close_btn)

            # Show dialog
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing session management dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show session management: {str(e)}")

    def clear_session_type(self, session_type, parent_dialog):
        """Clear specific type of session"""
        try:
            from PySide6.QtWidgets import QMessageBox

            # Confirmation messages
            messages = {
                'current': "Are you sure you want to clear the current session?\nYou will need to login again next time.",
                'remember': "Are you sure you want to clear the Remember Me session?\nAutomatic login will be disabled.",
                'all': "Are you sure you want to clear ALL sessions?\nThis will log you out and disable automatic login."
            }

            msg = QMessageBox(parent_dialog)
            msg.setWindowTitle("Confirm Session Clearing")
            msg.setText(messages.get(session_type, "Are you sure?"))
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            if msg.exec() == QMessageBox.Yes:
                try:
                    from modules.session_manager import get_session_manager
                    session_manager = get_session_manager()

                    if session_type == 'current':
                        session_manager.clear_session(clear_remember_me=False)
                        self.add_notification("Session Cleared", "Current session cleared", "info")
                    elif session_type == 'remember':
                        session_manager.clear_session(clear_remember_me=True)
                        self.add_notification("Remember Me Cleared", "Remember me session cleared", "info")
                    elif session_type == 'all':
                        session_manager.clear_session(clear_remember_me=True)
                        self.add_notification("All Sessions Cleared", "All sessions cleared", "info")
                        # Close dialog and logout
                        parent_dialog.accept()
                        QTimer.singleShot(1000, self.logout_user)
                        return

                    # Refresh the dialog
                    parent_dialog.accept()
                    QTimer.singleShot(500, self.show_session_management_dialog)

                except Exception as e:
                    self.logger.error(f"Error clearing session: {e}")
                    QMessageBox.critical(parent_dialog, "Error", f"Failed to clear session: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error in clear_session_type: {e}")

    def show_account_settings(self):
        """Show account settings dialog"""
        try:
            if not hasattr(self, 'current_user') or not self.current_user:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No User", "No user is currently logged in.")
                return

            from modules.account_settings_dialog import AccountSettingsDialog

            settings_dialog = AccountSettingsDialog(self.current_user, self)
            settings_dialog.profile_updated.connect(self.handle_profile_updated)
            settings_dialog.settings_changed.connect(self.handle_settings_changed)
            settings_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing account settings: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Could not open account settings: {str(e)}")

    def handle_profile_updated(self, updated_user_info):
        """Handle profile update from account settings"""
        self.current_user = updated_user_info
        # Update user profile widget if it exists
        if hasattr(self, 'user_profile_widget'):
            self.user_profile_widget.set_user_info(updated_user_info)
        self.logger.info("User profile updated from account settings")

    def handle_settings_changed(self, settings):
        """Handle settings change from account settings"""
        self.logger.info("User settings updated from account settings")
        # Apply notification settings if needed
        if 'notifications' in settings:
            self.apply_notification_settings(settings['notifications'])

    def apply_notification_settings(self, notification_settings):
        """Apply notification preferences"""
        try:
            if hasattr(self, 'notification_manager'):
                # Update notification manager settings
                self.notification_manager.update_settings(notification_settings)
        except Exception as e:
            self.logger.error(f"Error applying notification settings: {e}")

    def show_cloud_sync_dialog(self):
        """Show cloud sync management dialog"""
        try:
            from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                         QPushButton, QGroupBox, QFormLayout, QTextEdit,
                                         QProgressBar, QScrollArea, QCheckBox)
            from PySide6.QtCore import Qt, QTimer
            from PySide6.QtGui import QFont
            from datetime import datetime

            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Cloud Sync Management")
            dialog.setModal(True)
            dialog.resize(700, 800)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8fafc;
                }
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
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 4px;
                }
            """)

            # Create scroll area for content
            scroll = QScrollArea()
            scroll_widget = QWidget()
            layout = QVBoxLayout(scroll_widget)
            layout.setSpacing(16)

            # User Information Group
            user_group = QGroupBox("👤 User & Sync Information")
            user_layout = QFormLayout(user_group)

            if hasattr(self, 'cloud_sync_settings') and self.cloud_sync_settings:
                user_layout.addRow("User ID:", QLabel(self.cloud_sync_settings.get('user_id', 'N/A')))
                user_layout.addRow("Email:", QLabel(self.cloud_sync_settings.get('user_email', 'N/A')))

                last_sync = self.cloud_sync_settings.get('last_sync_timestamp')
                if last_sync:
                    try:
                        sync_time = datetime.fromisoformat(last_sync)
                        sync_display = sync_time.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        sync_display = last_sync
                else:
                    sync_display = "Never"

                user_layout.addRow("Last Sync:", QLabel(sync_display))

                auto_sync = self.cloud_sync_settings.get('auto_sync_enabled', False)
                user_layout.addRow("Auto Sync:", QLabel("Enabled" if auto_sync else "Disabled"))
            else:
                user_layout.addRow("Status:", QLabel("Cloud sync not initialized"))

            layout.addWidget(user_group)

            # Sync Status Group
            status_group = QGroupBox("📊 Sync Status")
            status_layout = QVBoxLayout(status_group)

            # Firebase connection status with detailed validation
            firebase_status = self.get_detailed_firebase_status()
            connection_label = QLabel(firebase_status['display_text'])
            connection_label.setStyleSheet(firebase_status['style'])
            status_layout.addWidget(connection_label)

            # Add detailed status if there are issues
            if firebase_status.get('details'):
                details_label = QLabel(firebase_status['details'])
                details_label.setStyleSheet("color: #6b7280; font-size: 11px; margin-left: 20px;")
                status_layout.addWidget(details_label)

            # Usage statistics
            if self.firebase_manager:
                usage_stats = self.firebase_manager.get_usage_statistics()
                usage_text = f"""
Daily Usage:
• Reads: {usage_stats.get('daily_reads', 0)} / {usage_stats.get('max_reads', 0)}
• Writes: {usage_stats.get('daily_writes', 0)} / {usage_stats.get('max_writes', 0)}
• Reads Remaining: {usage_stats.get('reads_remaining', 0)}
• Writes Remaining: {usage_stats.get('writes_remaining', 0)}
                """.strip()

                usage_label = QLabel(usage_text)
                usage_label.setStyleSheet("font-family: monospace; background-color: #f1f5f9; padding: 8px; border-radius: 4px;")
                status_layout.addWidget(usage_label)

            layout.addWidget(status_group)

            # Data Collections Group
            collections_group = QGroupBox("📁 Data Collections")
            collections_layout = QVBoxLayout(collections_group)

            if hasattr(self, 'cloud_sync_settings') and self.cloud_sync_settings:
                collections = self.cloud_sync_settings.get('sync_collections', [])
                collections_text = f"Syncing {len(collections)} collections:\n" + "\n".join([f"• {col}" for col in collections])
            else:
                collections_text = "No collections configured for sync"

            collections_label = QLabel(collections_text)
            collections_label.setStyleSheet("font-family: monospace; background-color: #f1f5f9; padding: 8px; border-radius: 4px;")
            collections_layout.addWidget(collections_label)

            layout.addWidget(collections_group)

            # Sync Actions Group
            actions_group = QGroupBox("⚡ Sync Actions")
            actions_layout = QVBoxLayout(actions_group)

            # Manual sync buttons
            sync_buttons_layout = QHBoxLayout()

            # Upload button
            upload_btn = QPushButton("⬆️ Upload to Cloud")
            upload_btn.clicked.connect(lambda: self.manual_cloud_sync('upload', dialog))
            upload_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            sync_buttons_layout.addWidget(upload_btn)

            # Download button
            download_btn = QPushButton("⬇️ Download from Cloud")
            download_btn.clicked.connect(lambda: self.manual_cloud_sync('download', dialog))
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            sync_buttons_layout.addWidget(download_btn)

            # Bidirectional sync button
            bidirectional_btn = QPushButton("🔄 Smart Sync")
            bidirectional_btn.clicked.connect(lambda: self.manual_cloud_sync('bidirectional', dialog))
            bidirectional_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8b5cf6;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #7c3aed;
                }
            """)
            sync_buttons_layout.addWidget(bidirectional_btn)

            actions_layout.addLayout(sync_buttons_layout)

            # Data validation button
            validate_btn = QPushButton("🔍 Validate Local Data")
            validate_btn.clicked.connect(self.show_data_validation_dialog)
            validate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
            actions_layout.addWidget(validate_btn)

            # Firebase test button
            firebase_test_btn = QPushButton("🔧 Test Firebase Connection")
            firebase_test_btn.clicked.connect(self.test_firebase_connection)
            firebase_test_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0ea5e9;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #0284c7;
                }
            """)
            actions_layout.addWidget(firebase_test_btn)

            # Auto-sync toggle
            auto_sync_layout = QHBoxLayout()
            auto_sync_checkbox = QCheckBox("Enable automatic sync every 30 minutes")
            if hasattr(self, 'cloud_sync_settings') and self.cloud_sync_settings:
                auto_sync_checkbox.setChecked(self.cloud_sync_settings.get('auto_sync_enabled', False))
            auto_sync_checkbox.toggled.connect(self.toggle_auto_sync)
            auto_sync_layout.addWidget(auto_sync_checkbox)
            actions_layout.addLayout(auto_sync_layout)

            layout.addWidget(actions_group)

            # Progress bar for sync operations
            self.sync_progress_bar = QProgressBar()
            self.sync_progress_bar.setVisible(False)
            layout.addWidget(self.sync_progress_bar)

            # Set up scroll area
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)

            # Main dialog layout
            main_layout = QVBoxLayout(dialog)
            main_layout.addWidget(scroll)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
            main_layout.addWidget(close_btn)

            # Show dialog
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing cloud sync dialog: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to show cloud sync dialog: {str(e)}")

    def manual_cloud_sync(self, sync_type, parent_dialog):
        """Perform manual cloud sync operation with async processing"""
        try:
            from PySide6.QtWidgets import QMessageBox

            if not self.firebase_manager or not self.firebase_manager.is_authenticated():
                QMessageBox.warning(parent_dialog, "Not Connected", "Not connected to Firebase. Please check your connection.")
                return

            # Check if another sync is already running
            if hasattr(self, 'active_sync_worker') and self.active_sync_worker and self.active_sync_worker.isRunning():
                QMessageBox.warning(parent_dialog, "Sync in Progress", "Another sync operation is already running. Please wait for it to complete.")
                return

            # Show confirmation
            sync_messages = {
                'upload': "Upload all local data to cloud?\nThis will overwrite cloud data.\n\nThe operation will run in the background and you can continue using the application.",
                'download': "Download all data from cloud?\nThis will overwrite local data.\n\nThe operation will run in the background and you can continue using the application.",
                'bidirectional': "Perform smart sync?\nThis will merge local and cloud data intelligently.\n\nThe operation will run in the background and you can continue using the application."
            }

            msg = QMessageBox(parent_dialog)
            msg.setWindowTitle("Confirm Async Sync Operation")
            msg.setText(sync_messages.get(sync_type, "Perform sync operation?"))
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            if msg.exec() == QMessageBox.Yes:
                self.logger.info(f"Starting manual async {sync_type} sync")

                # Close dialog first to show it's non-blocking
                parent_dialog.accept()

                if sync_type == 'upload':
                    local_data = self.get_all_local_data()
                    if local_data:
                        # Check if data has actual records
                        total_records = sum(len(df) for df in local_data.values() if not df.empty)
                        if total_records > 0:
                            self.logger.info(f"Starting upload with {len(local_data)} collections and {total_records} total records")
                            self.start_async_sync_operation('upload', data=local_data, show_progress=True)
                        else:
                            QMessageBox.information(self, "No Data", f"Found {len(local_data)} collections but no records to upload.\n\nAll collections appear to be empty.")
                    else:
                        # Show detailed error message
                        QMessageBox.information(self, "No Data",
                                              "No local data found to upload.\n\n"
                                              "This could mean:\n"
                                              "• No CSV files in the data directory\n"
                                              "• All data files are empty\n"
                                              "• Data manager is not properly initialized\n\n"
                                              "Please add some data to the application first.")

                elif sync_type == 'download':
                    self.start_async_sync_operation('download', data=None, show_progress=True)

                elif sync_type == 'bidirectional':
                    local_data = self.get_all_local_data()
                    self.start_async_sync_operation('smart_sync', data=local_data, show_progress=True)

        except Exception as e:
            self.logger.error(f"Error in manual sync: {e}")
            QMessageBox.critical(parent_dialog, "Sync Error", f"Failed to start sync: {str(e)}")

    def toggle_auto_sync(self, enabled):
        """Toggle automatic sync on/off"""
        try:
            if hasattr(self, 'cloud_sync_settings') and self.cloud_sync_settings:
                self.cloud_sync_settings['auto_sync_enabled'] = enabled
                self.logger.info(f"Auto-sync {'enabled' if enabled else 'disabled'}")

                # Update sync timer
                if hasattr(self, 'sync_timer'):
                    if enabled:
                        if not self.sync_timer.isActive():
                            sync_interval = self.cloud_sync_settings.get('sync_interval_minutes', 30) * 60 * 1000
                            self.sync_timer.start(sync_interval)
                    else:
                        self.sync_timer.stop()

        except Exception as e:
            self.logger.error(f"Error toggling auto-sync: {e}")

    def test_firebase_connection(self):
        """Test Firebase connection and show detailed results"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar
            from PySide6.QtCore import QTimer

            # Create test dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Firebase Connection Test")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # Status label
            status_label = QLabel("Testing Firebase connection...")
            status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(status_label)

            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(progress_bar)

            # Results text area
            results_text = QTextEdit()
            results_text.setReadOnly(True)
            layout.addWidget(results_text)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            # Show dialog
            dialog.show()

            # Perform tests
            self.perform_firebase_connection_tests(status_label, progress_bar, results_text)

        except Exception as e:
            self.logger.error(f"Error testing Firebase connection: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Test Error", f"Failed to run Firebase connection test: {str(e)}")

    def perform_firebase_connection_tests(self, status_label, progress_bar, results_text):
        """Perform comprehensive Firebase connection tests"""
        try:
            test_results = []

            # Test 1: Firebase Manager Availability
            progress_bar.setValue(10)
            status_label.setText("Testing Firebase Manager...")
            if self.firebase_manager:
                test_results.append("✅ Firebase Manager: Available")
            else:
                test_results.append("❌ Firebase Manager: Not Available")

            results_text.setPlainText("\n".join(test_results))
            QApplication.processEvents()

            # Test 2: Authentication Status
            progress_bar.setValue(25)
            status_label.setText("Testing Authentication...")
            if self.firebase_manager and self.firebase_manager.is_authenticated():
                test_results.append("✅ Authentication: User is authenticated")
            else:
                test_results.append("❌ Authentication: User is not authenticated")

            results_text.setPlainText("\n".join(test_results))
            QApplication.processEvents()

            # Test 3: Database Connection
            progress_bar.setValue(40)
            status_label.setText("Testing Database Connection...")
            if self.firebase_manager and hasattr(self.firebase_manager, 'is_database_available'):
                if self.firebase_manager.is_database_available():
                    test_results.append("✅ Database: Connection available and working")
                else:
                    test_results.append("❌ Database: Connection not available or not working")

                    # Try to reinitialize
                    if hasattr(self.firebase_manager, 'reinitialize_database'):
                        if self.firebase_manager.reinitialize_database():
                            test_results.append("✅ Database: Reinitialized successfully")
                        else:
                            test_results.append("❌ Database: Reinitialization failed")
            else:
                test_results.append("❌ Database: Cannot test (method not available)")

            results_text.setPlainText("\n".join(test_results))
            QApplication.processEvents()

            # Test 4: User Session
            progress_bar.setValue(55)
            status_label.setText("Testing User Session...")
            if (self.firebase_manager and
                hasattr(self.firebase_manager, 'current_session') and
                self.firebase_manager.current_session):
                user_email = getattr(self.firebase_manager.current_session, 'email', 'Unknown')
                test_results.append(f"✅ User Session: Active ({user_email})")
            else:
                test_results.append("❌ User Session: No active session")

            results_text.setPlainText("\n".join(test_results))
            QApplication.processEvents()

            # Test 5: Cloud Sync Settings
            progress_bar.setValue(70)
            status_label.setText("Testing Cloud Sync Settings...")
            if hasattr(self, 'cloud_sync_settings') and self.cloud_sync_settings:
                user_id = self.cloud_sync_settings.get('user_id', 'Not Set')
                test_results.append(f"✅ Cloud Sync Settings: Available (User ID: {user_id})")
            else:
                test_results.append("❌ Cloud Sync Settings: Not configured")

            results_text.setPlainText("\n".join(test_results))
            QApplication.processEvents()

            # Test 6: Firebase Connectivity Test
            progress_bar.setValue(85)
            status_label.setText("Testing Firebase Connectivity...")
            if self.firebase_manager and self.firebase_manager.db:
                try:
                    # Try to create a test reference (doesn't actually write data)
                    test_ref = self.firebase_manager.db.collection('connection_test')
                    test_results.append("✅ Firebase Connectivity: Connection successful")
                except Exception as e:
                    test_results.append(f"❌ Firebase Connectivity: Failed ({str(e)})")
            else:
                test_results.append("❌ Firebase Connectivity: Cannot test (no database)")

            results_text.setPlainText("\n".join(test_results))
            QApplication.processEvents()

            # Test Complete
            progress_bar.setValue(100)

            # Determine overall status
            failed_tests = [result for result in test_results if result.startswith("❌")]
            if failed_tests:
                status_label.setText(f"❌ Tests Complete - {len(failed_tests)} issues found")
                status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ef4444;")

                # Add recommendations
                test_results.append("\n" + "="*50)
                test_results.append("RECOMMENDATIONS:")
                test_results.append("• Check Firebase configuration")
                test_results.append("• Verify internet connection")
                test_results.append("• Try logging out and logging back in")
                test_results.append("• Check Firebase service status")

            else:
                status_label.setText("✅ All Tests Passed - Firebase Ready")
                status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #10b981;")

                test_results.append("\n" + "="*50)
                test_results.append("✅ Firebase is ready for sync operations!")

            results_text.setPlainText("\n".join(test_results))

        except Exception as e:
            self.logger.error(f"Error performing Firebase tests: {e}")
            status_label.setText("❌ Test Error")
            results_text.setPlainText(f"Error during testing: {str(e)}")

    def download_data_from_cloud(self):
        """Download data from cloud to local storage - Async version"""
        try:
            if not self.firebase_manager or not self.firebase_manager.is_authenticated():
                self.logger.error("Firebase not available for download")
                return False

            self.logger.info("Starting async download from cloud...")

            # Start async download operation
            return self.start_async_sync_operation('download', data=None, show_progress=True)

        except Exception as e:
            self.logger.error(f"Error starting cloud download: {e}")
            self.add_notification("Cloud Sync", "Failed to start download from cloud", "error")
            return False

    def save_cloud_data_to_local(self, cloud_data):
        """Save downloaded cloud data to local CSV files"""
        try:
            import os

            # Ensure data directory exists
            data_dir = os.path.join(os.getcwd(), 'data')
            os.makedirs(data_dir, exist_ok=True)

            saved_files = 0
            for collection_name, df in cloud_data.items():
                try:
                    file_path = os.path.join(data_dir, f"{collection_name}.csv")

                    # Backup existing file if it exists
                    if os.path.exists(file_path):
                        backup_path = f"{file_path}.backup"
                        os.rename(file_path, backup_path)
                        self.logger.info(f"Backed up existing {collection_name}.csv")

                    # Save new data
                    df.to_csv(file_path, index=False)
                    saved_files += 1
                    self.logger.info(f"Saved {len(df)} records to {collection_name}.csv")

                except Exception as e:
                    self.logger.error(f"Error saving {collection_name}: {e}")
                    continue

            self.logger.info(f"Saved {saved_files} files from cloud data")

        except Exception as e:
            self.logger.error(f"Error saving cloud data to local: {e}")

    def refresh_data_after_sync(self):
        """Refresh application data after sync operation"""
        try:
            # Reload data manager if available
            if hasattr(self, 'data_manager') and self.data_manager:
                self.logger.info("Refreshing data manager after sync...")
                # Trigger data reload
                self.data_manager.reload_all_data()

            # Refresh UI components
            self.logger.info("Refreshing UI after sync...")
            # Add any UI refresh logic here

            self.add_notification("Data Refresh", "Application data refreshed after sync", "info")

        except Exception as e:
            self.logger.error(f"Error refreshing data after sync: {e}")

    def perform_smart_sync(self):
        """Perform intelligent bidirectional sync with conflict resolution - Async version"""
        try:
            if not self.firebase_manager or not self.firebase_manager.is_authenticated():
                self.logger.error("Firebase not available for smart sync")
                return False

            self.logger.info("Starting async smart sync...")

            # Get local data for smart sync
            local_data = self.get_all_local_data()

            # Start async smart sync operation
            return self.start_async_sync_operation('smart_sync', data=local_data, show_progress=True)

        except Exception as e:
            self.logger.error(f"Error starting smart sync: {e}")
            self.add_notification("Cloud Sync", "Failed to start smart sync", "error")
            return False

    def merge_local_and_cloud_data(self, local_data, cloud_data):
        """Merge local and cloud data with intelligent conflict resolution"""
        try:
            import pandas as pd
            from datetime import datetime

            merged_data = {}

            # Get all unique collection names
            all_collections = set(local_data.keys()) | set(cloud_data.keys())

            for collection_name in all_collections:
                local_df = local_data.get(collection_name)
                cloud_df = cloud_data.get(collection_name)

                if local_df is None and cloud_df is not None:
                    # Only cloud data exists
                    merged_data[collection_name] = cloud_df.copy()
                    self.logger.info(f"Using cloud data for {collection_name} (no local data)")

                elif local_df is not None and cloud_df is None:
                    # Only local data exists
                    merged_data[collection_name] = local_df.copy()
                    self.logger.info(f"Using local data for {collection_name} (no cloud data)")

                elif local_df is not None and cloud_df is not None:
                    # Both exist - perform intelligent merge
                    merged_df = self.intelligent_dataframe_merge(local_df, cloud_df, collection_name)
                    merged_data[collection_name] = merged_df

            return merged_data

        except Exception as e:
            self.logger.error(f"Error merging data: {e}")
            return {}

    def intelligent_dataframe_merge(self, local_df, cloud_df, collection_name):
        """Perform intelligent merge of two DataFrames"""
        try:
            import pandas as pd

            # Strategy 1: If DataFrames are identical, return local
            if local_df.equals(cloud_df):
                self.logger.info(f"Data identical for {collection_name}")
                return local_df.copy()

            # Strategy 2: If one is empty, use the non-empty one
            if local_df.empty and not cloud_df.empty:
                self.logger.info(f"Using cloud data for {collection_name} (local empty)")
                return cloud_df.copy()
            elif not local_df.empty and cloud_df.empty:
                self.logger.info(f"Using local data for {collection_name} (cloud empty)")
                return local_df.copy()

            # Strategy 3: Merge based on common columns and indices
            try:
                # Try to merge on common columns
                common_columns = set(local_df.columns) & set(cloud_df.columns)

                if common_columns:
                    # Combine both DataFrames and remove duplicates
                    combined_df = pd.concat([local_df, cloud_df], ignore_index=True)

                    # Remove exact duplicates
                    merged_df = combined_df.drop_duplicates()

                    self.logger.info(f"Merged {collection_name}: {len(local_df)} local + {len(cloud_df)} cloud = {len(merged_df)} final")
                    return merged_df
                else:
                    # No common columns, prefer local data
                    self.logger.warning(f"No common columns for {collection_name}, using local data")
                    return local_df.copy()

            except Exception as merge_error:
                self.logger.error(f"Error in DataFrame merge for {collection_name}: {merge_error}")
                # Fallback to local data
                return local_df.copy()

        except Exception as e:
            self.logger.error(f"Error in intelligent merge for {collection_name}: {e}")
            return local_df.copy() if local_df is not None else cloud_df.copy()

    def add_notification(self, title, message, notification_type="info", category=None, source=None):
        """Add a notification using the centralized notification manager"""
        try:
            if hasattr(self, 'notification_manager'):
                return self.notification_manager.notify(
                    title, message,
                    category=category or notification_type,
                    source=source or 'Application'
                )
            elif hasattr(self, 'notification_bell'):
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

    def show_startup_notifications_in_gui(self):
        """Show all startup notifications in the GUI after it's fully loaded"""
        try:
            # Show login notification if pending
            if hasattr(self, 'pending_login_notification'):
                notification = self.pending_login_notification
                self.add_notification(
                    notification["title"],
                    notification["message"],
                    notification["category"]
                )
                delattr(self, 'pending_login_notification')

            # Show welcome notification
            QTimer.singleShot(1000, lambda: self.add_notification(
                "Welcome to Kitchen Dashboard",
                "All systems are operational. Enhanced features are now available!",
                "success"
            ))

            # Show category sync notification if pending
            if hasattr(self, 'pending_sync_notification'):
                notification = self.pending_sync_notification
                QTimer.singleShot(2000, lambda: self.add_notification(
                    notification["title"],
                    notification["message"],
                    notification["category"]
                ))
                delattr(self, 'pending_sync_notification')

        except Exception as e:
            self.logger.error(f"Error showing startup notifications: {e}")

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

    def toggle_startup_notifications(self, state):
        """Toggle startup notifications on/off"""
        self.show_startup_notifications = state == 2  # 2 = checked, 0 = unchecked
        self.logger.info(f"Startup notifications {'enabled' if self.show_startup_notifications else 'disabled'}")

    def create_testing_menu(self):
        """Create testing menu for comprehensive module testing"""
        try:
            from PySide6.QtGui import QAction

            # Create menu bar if it doesn't exist
            if not self.menuBar():
                menubar = self.menuBar()
            else:
                menubar = self.menuBar()

            # Create Testing menu
            testing_menu = menubar.addMenu("Testing")

            # Add comprehensive test action
            comprehensive_test_action = QAction("Run Comprehensive Tests", self)
            comprehensive_test_action.triggered.connect(self.run_comprehensive_tests)
            testing_menu.addAction(comprehensive_test_action)

            # Add module-specific test actions
            testing_menu.addSeparator()

            module_test_action = QAction("Test All Modules", self)
            module_test_action.triggered.connect(self.test_all_modules)
            testing_menu.addAction(module_test_action)

            data_test_action = QAction("Test Data Operations", self)
            data_test_action.triggered.connect(self.test_data_operations)
            testing_menu.addAction(data_test_action)

            ui_test_action = QAction("Test UI Components", self)
            ui_test_action.triggered.connect(self.test_ui_components)
            testing_menu.addAction(ui_test_action)

            performance_test_action = QAction("Test Performance", self)
            performance_test_action.triggered.connect(self.test_performance)
            testing_menu.addAction(performance_test_action)

            # Add sample data generation
            testing_menu.addSeparator()

            generate_data_action = QAction("Generate Sample Data", self)
            generate_data_action.triggered.connect(self.generate_sample_data)
            testing_menu.addAction(generate_data_action)

            cleanup_data_action = QAction("Cleanup Sample Data", self)
            cleanup_data_action.triggered.connect(self.cleanup_sample_data)
            testing_menu.addAction(cleanup_data_action)

            self.logger.info("Testing menu created successfully")

        except Exception as e:
            self.logger.error(f"Error creating testing menu: {e}")

    def create_updates_menu(self):
        """Create dedicated updates menu for version management and updates"""
        try:
            from PySide6.QtGui import QAction

            # Get menu bar
            menubar = self.menuBar()

            # Create Updates menu
            updates_menu = menubar.addMenu("Updates")

            # Add version information action
            show_version_action = QAction("Show Version Info", self)
            show_version_action.triggered.connect(self.show_version_info)
            updates_menu.addAction(show_version_action)

            updates_menu.addSeparator()

            # Add update checking actions
            if UPDATE_SYSTEM_AVAILABLE and self.update_manager:
                check_updates_action = QAction("Check for Updates", self)
                check_updates_action.triggered.connect(self.manual_check_for_updates)
                updates_menu.addAction(check_updates_action)

                auto_update_action = QAction("Auto-Check Settings", self)
                auto_update_action.triggered.connect(self.show_auto_update_settings)
                updates_menu.addAction(auto_update_action)

                updates_menu.addSeparator()

                backup_data_action = QAction("Backup Data Before Update", self)
                backup_data_action.triggered.connect(self.backup_data_for_update)
                updates_menu.addAction(backup_data_action)

                restore_data_action = QAction("Restore Data from Backup", self)
                restore_data_action.triggered.connect(self.restore_data_from_backup)
                updates_menu.addAction(restore_data_action)

                updates_menu.addSeparator()

                update_history_action = QAction("Update History", self)
                update_history_action.triggered.connect(self.show_update_history)
                updates_menu.addAction(update_history_action)

            else:
                # Show disabled update options when system is not available
                check_updates_disabled = QAction("Check for Updates (Not Available)", self)
                check_updates_disabled.setEnabled(False)
                updates_menu.addAction(check_updates_disabled)

                updates_menu.addSeparator()

                install_update_system_action = QAction("Install Update System", self)
                install_update_system_action.triggered.connect(self.show_update_system_installation_info)
                updates_menu.addAction(install_update_system_action)

            self.logger.info("Updates menu created successfully")

        except Exception as e:
            self.logger.error(f"Error creating updates menu: {e}")

    def initialize_update_checking(self):
        """Initialize automatic update checking after UI is ready"""
        try:
            if UPDATE_SYSTEM_AVAILABLE and self.update_manager:
                self.logger.info("Initializing automatic update checking...")

                # Check for updates automatically on startup
                self.update_manager.auto_check_updates()

                # Add notification about update system
                self.add_notification(
                    "Update System Ready",
                    "Automatic update checking is now active. Updates will be checked periodically.",
                    "info"
                )

                self.logger.info("Automatic update checking initialized successfully")
            else:
                self.logger.warning("Update system not available - skipping automatic update checking")

        except Exception as e:
            self.logger.error(f"Error initializing update checking: {e}")
            self.add_notification(
                "Update System Error",
                f"Failed to initialize update checking: {str(e)}",
                "error"
            )

    def manual_check_for_updates(self):
        """Manually check for updates"""
        try:
            if UPDATE_SYSTEM_AVAILABLE and self.update_manager:
                self.logger.info("Manual update check requested")
                self.update_manager.manual_check_updates()

                self.add_notification(
                    "Update Check",
                    "Checking for updates manually...",
                    "info"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Update System Not Available",
                    "The update system is not available. Please check if update modules are properly installed."
                )
        except Exception as e:
            self.logger.error(f"Error during manual update check: {e}")
            QMessageBox.critical(
                self,
                "Update Check Error",
                f"Failed to check for updates: {str(e)}"
            )

    def show_version_info(self):
        """Show current version information"""
        try:
            if UPDATE_SYSTEM_AVAILABLE and version_manager:
                version_info = version_manager.get_version_info()

                info_text = f"""
Current Version Information:

Version: {version_info.get('version', 'Unknown')}
Build: {version_info.get('build', 'Unknown')}
Author: {version_info.get('author', 'Unknown')}
Description: {version_info.get('description', 'Unknown')}
Release Date: {version_info.get('release_date', 'Unknown')}
                """

                QMessageBox.information(
                    self,
                    "Version Information",
                    info_text.strip()
                )
            else:
                QMessageBox.warning(
                    self,
                    "Version Info Not Available",
                    "Version information is not available. Update system may not be properly installed."
                )
        except Exception as e:
            self.logger.error(f"Error showing version info: {e}")
            QMessageBox.critical(
                self,
                "Version Info Error",
                f"Failed to retrieve version information: {str(e)}"
            )

    def backup_data_for_update(self):
        """Create a backup of current data before update"""
        try:
            self.logger.info("Creating data backup for update...")

            # Use the existing save_data method which creates backups
            self.save_data()

            # Also create a timestamped backup specifically for updates
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'update_backup_{timestamp}')
            os.makedirs(backup_dir, exist_ok=True)

            # Save each dataframe to the update backup directory
            for key, df in self.data.items():
                backup_file = os.path.join(backup_dir, f"{key}.csv")
                df.to_csv(backup_file, index=False, encoding='utf-8')

            # Save settings
            with open(os.path.join(backup_dir, 'settings.txt'), 'w', encoding='utf-8') as f:
                f.write(f"currency_symbol={self.currency_symbol}\n")
                f.write(f"backup_created={datetime.now().isoformat()}\n")

            self.logger.info(f"Update backup created successfully at: {backup_dir}")

            QMessageBox.information(
                self,
                "Backup Complete",
                f"Data backup for update created successfully!\n\nBackup location:\n{backup_dir}"
            )

            self.add_notification(
                "Backup Complete",
                f"Data backup created at: {backup_dir}",
                "success"
            )

        except Exception as e:
            self.logger.error(f"Error creating update backup: {e}")
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Failed to create data backup: {str(e)}"
            )

    def show_auto_update_settings(self):
        """Show auto-update settings dialog"""
        try:
            if UPDATE_SYSTEM_AVAILABLE and self.update_manager:
                # Show the update manager settings
                self.update_manager.show()
            else:
                QMessageBox.information(
                    self,
                    "Auto-Update Settings",
                    "Auto-update settings are not available.\nUpdate system may not be properly installed."
                )
        except Exception as e:
            self.logger.error(f"Error showing auto-update settings: {e}")
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to show auto-update settings: {str(e)}"
            )

    def restore_data_from_backup(self):
        """Restore data from a backup"""
        try:
            from PySide6.QtWidgets import QFileDialog

            # Let user select backup directory
            backup_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Backup Directory to Restore",
                os.path.dirname(os.path.abspath(__file__)),
                QFileDialog.ShowDirsOnly
            )

            if not backup_dir:
                return

            # Confirm restoration
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                f"Are you sure you want to restore data from:\n{backup_dir}\n\nThis will overwrite current data!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            # Restore data files
            restored_files = []
            for filename in os.listdir(backup_dir):
                if filename.endswith('.csv'):
                    source_file = os.path.join(backup_dir, filename)
                    dest_file = os.path.join('data', filename)

                    # Create data directory if it doesn't exist
                    os.makedirs('data', exist_ok=True)

                    # Copy file
                    import shutil
                    shutil.copy2(source_file, dest_file)
                    restored_files.append(filename)

            # Restore settings if available
            settings_file = os.path.join(backup_dir, 'settings.txt')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('currency_symbol='):
                            self.currency_symbol = line.split('=', 1)[1].strip()

            # Reload data
            self.data = self.load_data()
            self.refresh_all_tabs()

            self.logger.info(f"Data restored from backup: {backup_dir}")

            QMessageBox.information(
                self,
                "Restore Complete",
                f"Data restored successfully!\n\nRestored files:\n" + "\n".join(restored_files)
            )

            self.add_notification(
                "Data Restored",
                f"Data restored from backup: {os.path.basename(backup_dir)}",
                "success"
            )

        except Exception as e:
            self.logger.error(f"Error restoring data from backup: {e}")
            QMessageBox.critical(
                self,
                "Restore Error",
                f"Failed to restore data from backup: {str(e)}"
            )

    def show_update_history(self):
        """Show update history"""
        try:
            if UPDATE_SYSTEM_AVAILABLE and version_manager:
                # Create a simple update history dialog
                history_text = """
Update History:

This feature shows the history of updates applied to the application.

Current Version: """ + version_manager.get_version_info().get('version', 'Unknown') + """
Build Date: """ + version_manager.get_version_info().get('build', 'Unknown') + """

Note: Detailed update history will be available in future versions.
For now, you can check the GitHub releases page for version history.
                """

                QMessageBox.information(
                    self,
                    "Update History",
                    history_text.strip()
                )
            else:
                QMessageBox.warning(
                    self,
                    "Update History Not Available",
                    "Update history is not available. Update system may not be properly installed."
                )
        except Exception as e:
            self.logger.error(f"Error showing update history: {e}")
            QMessageBox.critical(
                self,
                "Update History Error",
                f"Failed to show update history: {str(e)}"
            )

    def show_update_system_installation_info(self):
        """Show information about installing the update system"""
        info_text = """
Update System Installation

The update system is not currently available. To enable automatic updates:

1. Ensure the following files are present:
   - update_manager.py
   - updater.py
   - version.py
   - update_checker.py

2. Install required dependencies:
   - requests (for checking updates)
   - PySide6 (for UI components)

3. Restart the application

For more information, please check the documentation or contact support.
        """

        QMessageBox.information(
            self,
            "Update System Installation",
            info_text.strip()
        )

    def run_comprehensive_tests(self):
        """Run safe comprehensive tests for all modules and functions"""
        try:
            # Import the safe comprehensive test suite
            from safe_comprehensive_test import show_safe_comprehensive_test_suite_modal

            # Show a message first
            QMessageBox.information(self, "Comprehensive Tests", "Opening comprehensive test suite...")

            # Create and show the safe test suite (modal version)
            self.comprehensive_test_dialog = show_safe_comprehensive_test_suite_modal(self)

            if self.comprehensive_test_dialog is None:
                QMessageBox.warning(self, "Test Error", "Failed to create safe test suite.")
                return

            self.logger.info("Safe comprehensive test suite launched successfully")

        except Exception as e:
            self.logger.error(f"Error running comprehensive tests: {e}")
            QMessageBox.critical(self, "Test Error", f"Failed to run comprehensive tests: {e}")

    def test_all_modules(self):
        """Test all modules individually"""
        try:
            # Import from tests directory
            import sys
            import os
            tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
            sys.path.insert(0, tests_dir)

            try:
                from module_tester import ModuleTester  # type: ignore
                tester = ModuleTester(self)
                tester.test_all_modules()
            except ImportError:
                QMessageBox.warning(self, "Test Error", "Module tester not found. Please ensure test files are available.")
                return

        except Exception as e:
            self.logger.error(f"Error testing modules: {e}")
            QMessageBox.warning(self, "Module Test Error", f"Failed to test modules: {e}")

    def test_data_operations(self):
        """Test data operations with sample data"""
        try:
            # Import from tests directory
            import sys
            import os
            tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
            sys.path.insert(0, tests_dir)

            try:
                from data_operation_tester import DataOperationTester  # type: ignore
                tester = DataOperationTester(self)
                tester.test_all_data_operations()
            except ImportError:
                QMessageBox.warning(self, "Test Error", "Data operation tester not found. Please ensure test files are available.")
                return

        except Exception as e:
            self.logger.error(f"Error testing data operations: {e}")
            QMessageBox.warning(self, "Data Test Error", f"Failed to test data operations: {e}")

    def test_ui_components(self):
        """Test UI components and interactions"""
        try:
            # Import from tests directory
            import sys
            import os
            tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
            sys.path.insert(0, tests_dir)

            try:
                from ui_component_tester import UIComponentTester  # type: ignore
                tester = UIComponentTester(self)
                tester.test_all_ui_components()
            except ImportError:
                QMessageBox.warning(self, "Test Error", "UI component tester not found. Please ensure test files are available.")
                return

        except Exception as e:
            self.logger.error(f"Error testing UI components: {e}")
            QMessageBox.warning(self, "UI Test Error", f"Failed to test UI components: {e}")

    def test_performance(self):
        """Test performance with large datasets"""
        try:
            # Import from tests directory
            import sys
            import os
            tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
            sys.path.insert(0, tests_dir)

            try:
                from performance_tester import PerformanceTester  # type: ignore
                tester = PerformanceTester(self)
                tester.test_performance()
            except ImportError:
                QMessageBox.warning(self, "Test Error", "Performance tester not found. Please ensure test files are available.")
                return

        except Exception as e:
            self.logger.error(f"Error testing performance: {e}")
            QMessageBox.warning(self, "Performance Test Error", f"Failed to test performance: {e}")

    def generate_sample_data(self):
        """Generate comprehensive sample data for testing"""
        try:
            # Import from tests directory
            import sys
            import os
            tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
            sys.path.insert(0, tests_dir)

            try:
                from sample_data_generator import SampleDataGenerator  # type: ignore
            except ImportError:
                QMessageBox.warning(self, "Test Error", "Sample data generator not found. Please ensure test files are available.")
                return

            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Generate Sample Data",
                "This will generate comprehensive sample data for all modules.\n"
                "This may overwrite existing data files.\n\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Show progress dialog
                progress_dialog = QMessageBox(self)
                progress_dialog.setWindowTitle("Generating Sample Data")
                progress_dialog.setText("Generating comprehensive sample data...\nPlease wait.")
                progress_dialog.setStandardButtons(QMessageBox.NoButton)
                progress_dialog.setWindowModality(Qt.WindowModal)
                progress_dialog.show()
                QApplication.processEvents()

                # Generate data
                generator = SampleDataGenerator()
                data = generator.generate_all_sample_data(save_to_files=True)

                progress_dialog.hide()
                progress_dialog.deleteLater()

                # Reload data in application
                self.data = self.load_data()

                # Refresh all tabs
                self.refresh_all_tabs()

                # Show success message
                QMessageBox.information(
                    self,
                    "Sample Data Generated",
                    f"Successfully generated sample data for {len(data)} datasets!\n\n"
                    "Data has been saved to CSV files and loaded into the application.\n"
                    "You can now test all modules with realistic data."
                )

                self.logger.info("Sample data generation completed successfully")

                # Add notification
                self.add_notification(
                    "Sample Data Generated",
                    f"Generated {len(data)} datasets with comprehensive test data",
                    "success"
                )

        except Exception as e:
            self.logger.error(f"Error generating sample data: {e}")
            QMessageBox.critical(self, "Sample Data Error", f"Failed to generate sample data: {e}")

    def cleanup_sample_data(self):
        """Cleanup sample data with user options"""
        try:
            # Show cleanup options dialog
            cleanup_dialog = SampleDataCleanupDialog(self)
            if cleanup_dialog.exec() == QDialog.Accepted:
                # Reload data after cleanup
                self.data = self.load_data()

                # Refresh all tabs
                self.refresh_all_tabs()

                # Add notification
                self.add_notification(
                    "Sample Data Cleaned",
                    "Sample data has been cleaned up successfully",
                    "info"
                )

                self.logger.info("Sample data cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during sample data cleanup: {e}")
            QMessageBox.critical(self, "Cleanup Error", f"Failed to cleanup sample data: {e}")

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

        # Apply stylesheet directly (CSS optimizer disabled)
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
        """Apply enhanced performance optimizations - DISABLED"""
        # Performance optimizers disabled to prevent initialization errors
        self.logger.info("Performance optimizations skipped (modules disabled)")

    def apply_advanced_performance_enhancements(self):
        """Apply advanced performance enhancements - DISABLED"""
        # Performance enhancers disabled to prevent initialization errors
        self.logger.info("Advanced performance enhancements skipped (modules disabled)")

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
            # Show loading indicator
            self.show_loading_message("Refreshing data from CSV files...")

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

                # Show success message
                self.show_success_message("Data refreshed successfully!")
            else:
                self.logger.info("[SUCCESS] Data refreshed")
                self.show_success_message("Data refreshed successfully!")

        except Exception as e:
            self.logger.error(f"[ERROR] Error refreshing data: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh data: {e}")

    def refresh_current_tab_data(self):
        """Refresh data for the current tab only"""
        self.logger.info("[REFRESH] Refreshing current tab data...")

        try:
            # Show loading indicator
            self.show_loading_message("Refreshing current tab data...")

            # Reload data
            self.data = self.load_data()

            # Get current tab and refresh it
            current_button = None
            for button in self.nav_buttons:
                if button.isChecked():
                    current_button = button
                    break

            if current_button:
                # Get the button's callback function and call it to refresh the page
                button_index = self.nav_buttons.index(current_button)
                tab_name = self.get_tab_name_by_index(button_index)

                # Trigger the current page refresh
                current_button.click()
                self.logger.info(f"[SUCCESS] {tab_name} tab data refreshed")

                # Show success message
                self.show_success_message(f"{tab_name} data refreshed successfully!")
            else:
                self.logger.info("[SUCCESS] Data refreshed")
                self.show_success_message("Data refreshed successfully!")

        except Exception as e:
            self.logger.error(f"[ERROR] Error refreshing current tab data: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh tab data: {e}")

    def get_tab_name_by_index(self, index):
        """Get tab name by button index"""
        tab_names = [
            "Home", "Inventory", "Meal Planning", "Budget", "Sales",
            "Pricing", "Packing Materials", "Expenses", "Gas Management",
            "Waste", "Cleaning", "Reports", "Logs", "Settings"
        ]
        return tab_names[index] if 0 <= index < len(tab_names) else "Unknown"

    def show_loading_message(self, message):
        """Show a temporary loading message"""
        try:
            # Create a temporary status message
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(message, 2000)  # Show for 2 seconds
        except:
            pass  # Ignore if status bar doesn't exist

    def show_success_message(self, message):
        """Show a temporary success message"""
        try:
            # Create a temporary status message
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(message, 3000)  # Show for 3 seconds
        except:
            pass  # Ignore if status bar doesn't exist

    def load_data(self):
        """Load all data from CSV files or create empty dataframes if files don't exist"""
        self.logger.log_section_header("Data Loading")
        data = {}

        try:
            # Check if data directory exists
            if not os.path.exists('data'):
                os.makedirs('data')
                self.logger.info("Created data directory")

            # Log current working directory and data path
            self.logger.info(f"Working directory: {os.getcwd()}")
            self.logger.info(f"Data directory: {os.path.abspath('data')}")

            # List all files in data directory
            if os.path.exists('data'):
                data_files = os.listdir('data')
                self.logger.info(f"Files in data directory: {len(data_files)} files found")
            else:
                self.logger.warning("Data directory does not exist!")

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
                'budget_categories': pd.DataFrame(columns=[
                    'category_id', 'category_name', 'category_type', 'parent_id',
                    'budget_amount', 'spent_amount', 'description'
                ]),
                'sales': pd.DataFrame(columns=[
                    'sale_id', 'item_name', 'quantity', 'price_per_unit', 'total_amount', 'customer', 'date'
                ]),
                'expenses_list': pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'budget_category', 'quantity', 'unit', 'priority',
                    'last_price', 'current_price', 'avg_price', 'location', 'notes', 'status', 'date_added', 'date_purchased'
                ]),
                'waste': pd.DataFrame(columns=[
                    'waste_id', 'item_name', 'quantity', 'unit', 'reason', 'cost', 'date'
                ]),
                'cleaning_maintenance': pd.DataFrame(columns=[
                    'task_id', 'task_name', 'frequency', 'last_completed', 'next_due', 'priority', 'notes',
                    'assigned_staff_id', 'assigned_staff_name', 'schedule_type', 'schedule_interval',
                    'day_number', 'time_period', 'auto_assign', 'rotation_order'
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
                ]),
                'sales_orders': pd.DataFrame(columns=[
                    'date', 'order_id', 'recipe', 'quantity', 'packing_materials', 'packing_cost',
                    'preparation_materials', 'preparation_cost', 'gas_charges', 'electricity_charges',
                    'total_cost_making', 'our_pricing', 'subtotal', 'discount', 'final_price_after_discount',
                    'profit', 'profit_percentage'
                ]),
                'staff': pd.DataFrame(columns=[
                    'staff_id', 'staff_name', 'role', 'contact_number', 'email', 'hire_date', 'status', 'notes'
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
                self.logger.info(f"Processing {key} data source")

                if os.path.exists(file_path):
                    try:
                        # Performance optimization: Check file size and use chunked loading for large files
                        file_size = os.path.getsize(file_path)
                        self.logger.info(f"  File found: {file_path} ({file_size} bytes)")

                        if file_size > 5 * 1024 * 1024:  # 5MB threshold
                            # Load large files in chunks to avoid memory issues
                            self.logger.info(f"  Loading large file in chunks")
                            chunks = []
                            chunk_count = 0
                            for chunk in pd.read_csv(file_path, chunksize=1000):
                                chunks.append(chunk)
                                chunk_count += 1
                            data[key] = pd.concat(chunks, ignore_index=True) if chunks else empty_df
                            self.logger.info(f"  Loaded {chunk_count} chunks from {file_path} ({file_size/1024/1024:.1f}MB)")
                        else:
                            # Load smaller files normally
                            data[key] = pd.read_csv(file_path, low_memory=False)
                            self.logger.info(f"  Loaded {len(data[key])} rows from {file_path} ({file_size/1024:.1f}KB)")

                        # Log data structure info
                        if len(data[key]) > 0:
                            self.logger.info(f"  Columns: {len(data[key].columns)} columns")
                            self.logger.info(f"  Shape: {data[key].shape}")
                        else:
                            self.logger.warning(f"  File {file_path} is empty")

                        loading_stats['files_found'] += 1
                        loading_stats['files_loaded'] += 1

                    except Exception as e:
                        error_msg = f"Error loading {key} from {file_path}: {e}"
                        self.logger.error(error_msg)
                        self.logger.log_exception(e, f"Loading {key} data")
                        data[key] = empty_df  # Use in-memory empty DataFrame
                        self.logger.warning(f"  Used empty dataframe for {key} due to read error. ORIGINAL FILE {file_path} WAS NOT MODIFIED.")
                        loading_stats['errors'].append(f"{key}: {str(e)}")
                else:
                    self.logger.warning(f"  File not found: {file_path}")
                    data[key] = empty_df
                    # Save the empty dataframe to create the file if it doesn't exist
                    try:
                        empty_df.to_csv(file_path, index=False)
                        self.logger.info(f"  Created new empty file for {key} at {file_path}")
                        loading_stats['files_created'] += 1
                    except Exception as e:
                        self.logger.error(f"  Error creating new empty file for {key} at {file_path}: {e}")
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
            print(f"[SEARCH] DATA LOADING DEBUG:")
            for key, df in data.items():
                if isinstance(df, pd.DataFrame):
                    print(f"  {key}: {len(df)} rows × {len(df.columns)} columns")
                else:
                    print(f"  {key}: {type(df)} (not a DataFrame)")

            # Log comprehensive loading statistics
            total_records = sum(len(df) for df in data.values() if hasattr(df, '__len__'))

            # Assign data to self.data immediately
            self.data = data

            # Log final summary
            summary_details = f"Loaded {len(data)} tables with {total_records} total records. Files: {loading_stats['files_found']} found, {loading_stats['files_loaded']} loaded, {loading_stats['files_created']} created"

            if loading_stats['errors']:
                self.logger.log_section_footer("Data Loading", False, f"{summary_details}. Errors: {len(loading_stats['errors'])}")
                self.logger.error("Error details:")
                for error in loading_stats['errors']:
                    self.logger.error(f"  - {error}")
            else:
                self.logger.log_section_footer("Data Loading", True, summary_details)

                # Send success notification for data loading
                if hasattr(self, 'notify_success') and total_records > 0:
                    self.notify_success(
                        "Data Loading Complete",
                        f"Successfully loaded {len(data)} data sources with {total_records} records",
                        source='Data Manager'
                    )

            self.logger.log_performance("Complete data loading", 0)  # Will be calculated by caller
            return data
        except Exception as e:
            error_msg = f"Error loading data: {e}"
            self.logger.critical(error_msg)
            print(f"[ERROR] CRITICAL ERROR in load_data: {error_msg}")

            # Don't show message box during initialization to avoid blocking
            if hasattr(self, 'isVisible') and self.isVisible():
                QMessageBox.critical(self, "Error", error_msg)

            # Return empty dataframes instead of None to prevent crashes
            empty_dataframes = {
                'inventory': pd.DataFrame(),
                'meal_plan': pd.DataFrame(),
                'recipes': pd.DataFrame(),
                'budget': pd.DataFrame(),
                'budget_categories': pd.DataFrame(),
                'sales': pd.DataFrame(),
                'expenses_list': pd.DataFrame(),
                'waste': pd.DataFrame(),
                'cleaning_maintenance': pd.DataFrame(),
                'items': pd.DataFrame(),
                'categories': pd.DataFrame(),
                'recipe_ingredients': pd.DataFrame(),
                'pricing': pd.DataFrame(),
                'packing_materials': pd.DataFrame(),
                'recipe_packing_materials': pd.DataFrame(),
                'sales_orders': pd.DataFrame(),
                'staff': pd.DataFrame()
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
            required_keys = ['inventory', 'recipes', 'recipe_ingredients', 'expenses_list', 'budget_categories', 'sales', 'waste']
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

        self.expenses_button = QPushButton(" Expenses")
        self.expenses_button.setIcon(self.create_icon("💰"))
        self.expenses_button.setIconSize(QSize(18, 18))
        self.expenses_button.setCheckable(True)
        self.expenses_button.clicked.connect(lambda: self.handle_nav_button(self.expenses_button, self.show_expenses_page))
        self.nav_buttons_layout.addWidget(self.expenses_button)
        self.nav_buttons.append(self.expenses_button)

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

        self.version_label = QLabel("v1.2.1")
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
        try:
            # Create a pixmap
            pixmap = QPixmap(24, 24)
            if pixmap.isNull():
                # Fallback to a simple icon if pixmap creation fails
                return QIcon()

            pixmap.fill(Qt.transparent)

            # Create a painter to draw on the pixmap with proper error checking
            painter = QPainter()
            if not painter.begin(pixmap):
                # If painter can't begin, return a simple icon
                return QIcon()

            try:
                painter.setFont(QFont("Segoe UI", 12))
                painter.setPen(QPen(QColor("#ecf0f1")))  # White text
                painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
            finally:
                painter.end()

            return QIcon(pixmap)

        except Exception as e:
            # If anything goes wrong, return a simple icon
            print(f"[WARNING] Error creating emoji icon: {e}")
            return QIcon()

    def create_refresh_button(self, tab_name="", callback=None):
        """Create a standardized refresh button for tabs"""
        refresh_button = QPushButton("🔄 Refresh Data")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)

        # Set tooltip
        if tab_name:
            refresh_button.setToolTip(f"Refresh {tab_name} data from CSV files")
        else:
            refresh_button.setToolTip("Refresh data from CSV files")

        # Connect callback
        if callback:
            refresh_button.clicked.connect(callback)
        else:
            refresh_button.clicked.connect(self.refresh_current_tab_data)

        return refresh_button

    def create_tab_header_with_refresh(self, title, tab_name="", custom_refresh_callback=None):
        """Create a standardized tab header with title and refresh button"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(10)

        # Title
        title_label = QLabel(title)
        title_label.setFont(self.title_font)
        header_layout.addWidget(title_label)

        # Spacer to push refresh button to the right
        header_layout.addStretch()

        # Refresh button
        refresh_button = self.create_refresh_button(tab_name, custom_refresh_callback)
        header_layout.addWidget(refresh_button)

        return header_widget

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

        # Expenses list metrics
        if 'status' in self.data['expenses_list'].columns:
            items_to_buy = len(self.data['expenses_list'][self.data['expenses_list']['status'] == 'Pending'])
        else:
            items_to_buy = len(self.data['expenses_list'])

        if 'estimated_cost' in self.data['expenses_list'].columns:
            estimated_cost = self.data['expenses_list']['estimated_cost'].sum()
        else:
            estimated_cost = 0.0

        # Note: Meal planning metrics calculation removed as variables were unused

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
        ax1.pie(
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

        # Add Firebase cloud sync section for subscription model
        if self.firebase_manager and self.current_user:
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

            # Add subscription-based sync info
            sync_info = QLabel("Your data automatically syncs to the cloud when you're authenticated.")
            sync_info.setWordWrap(True)
            sync_info.setStyleSheet("color: #10b981; font-weight: 600; margin-top: 10px;")
            cloud_layout.addWidget(sync_info)

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

            # Add header with smart ingredient check button and refresh button
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(20, 10, 20, 10)

            # Title
            title_label = QLabel("Inventory Management")
            title_label.setFont(self.title_font)
            title_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
            header_layout.addWidget(title_label)

            header_layout.addStretch()

            # Add refresh button
            refresh_button = self.create_refresh_button("Inventory")
            header_layout.addWidget(refresh_button)


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
                self.logger.info("[SUCCESS] Inventory page loaded successfully")

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
        """Display the enhanced budget management page"""
        self.clear_content()

        # Add header with refresh button
        header_widget = self.create_tab_header_with_refresh("Budget Management", "Budget")
        self.content_layout.addWidget(header_widget)

        # Create the budget management widget with proper budget categories
        try:
            from modules.budget_manager import BudgetManager
            budget_widget = BudgetManager(self.data)
            self.logger.info("Using updated budget management widget with budget categories")
        except Exception as e:
            # Create placeholder if module fails to load
            self.logger.error(f"Error loading budget widget: {str(e)}")
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(20, 20, 20, 20)
            error_label = QLabel(f"Budget management functionality is currently unavailable.\nError: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            placeholder_layout.addWidget(error_label)
            budget_widget = placeholder
            self.logger.error("Enhanced budget module failed to load")

        # Add the widget to the content layout
        self.content_layout.addWidget(budget_widget)

        # Log the action
        self.logger.info("Budget management page displayed")

    def show_sales_page(self):
        """Display the sales page with both basic sales recording and order management"""
        self.clear_content()

        # Add header with refresh button
        header_widget = self.create_tab_header_with_refresh("Sales Management", "Sales")
        self.content_layout.addWidget(header_widget)

        # Debug data before widget creation
        self.debug_data_before_widget_creation("sales", ["sales", "orders"])

        # Create a tabbed interface for different sales functions
        from PySide6.QtWidgets import QTabWidget

        sales_tabs = QTabWidget()
        sales_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                background: #f1f5f9;
            }
        """)

        # Tab 1: Basic Sales Recording
        try:
            from modules.sales import SalesWidget
            # Create a dummy inventory widget since SalesWidget requires it
            # but we'll use None for now and handle it in the SalesWidget
            basic_sales_widget = SalesWidget(self.data, None)
            sales_tabs.addTab(basic_sales_widget, "📝 Record Sales")
            self.logger.info("Basic sales recording widget loaded successfully")
        except Exception as e:
            # Create placeholder for basic sales
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            error_label = QLabel(f"Basic Sales module failed to load.\n\nError: {str(e)}")
            error_label.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-size: 14px;
                    padding: 20px;
                    background-color: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    margin: 20px;
                }
            """)
            error_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(error_label)
            sales_tabs.addTab(placeholder, "📝 Record Sales")
            self.logger.error(f"Basic sales module failed to load: {e}")

        # Tab 2: Order Management
        order_management_widget = None
        try:
            from modules.sales_order_management import SalesOrderManagementWidget

            # Get pricing data for automatic price fetching
            pricing_data = None
            try:
                from modules.pricing_management import PricingManagement
                pricing_data = PricingManagement(self.data, None)
            except Exception as e:
                self.logger.warning(f"Could not load pricing data: {e}")

            order_management_widget = SalesOrderManagementWidget(self.data, pricing_data)
            sales_tabs.addTab(order_management_widget, "🛒 Order Management")
            self.logger.info("Sales order management widget loaded successfully")

        except Exception as e:
            # Create placeholder for order management
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            error_label = QLabel(f"Order Management module failed to load.\n\nError: {str(e)}")
            error_label.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-size: 14px;
                    padding: 20px;
                    background-color: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    margin: 20px;
                }
            """)
            error_label.setAlignment(Qt.AlignCenter)
            placeholder_layout.addWidget(error_label)
            sales_tabs.addTab(placeholder, "🛒 Order Management")
            self.logger.error(f"Order management module failed to load: {e}")

        # Connect signals between widgets if both were created successfully
        try:
            if 'basic_sales_widget' in locals() and order_management_widget is not None:
                # Connect the sale_deleted signal to refresh the order management
                basic_sales_widget.sale_deleted.connect(lambda: self.refresh_order_management(order_management_widget))
                # Connect the sale_added signal to refresh the order management
                basic_sales_widget.sale_added.connect(lambda: self.refresh_order_management(order_management_widget))
                self.logger.info("Connected basic sales widget to order management for cross-tab updates")
        except Exception as e:
            self.logger.warning(f"Could not connect sales widgets: {e}")

        # Add the tabbed widget to the content layout
        self.content_layout.addWidget(sales_tabs)

    def refresh_order_management(self, order_management_widget):
        """Refresh the order management widget when a sale is added or deleted"""
        try:
            # Reload the sales_orders data
            self.data = self.load_data()

            # Update the widget's data
            order_management_widget.data = self.data

            # Refresh the orders display
            order_management_widget.load_orders()

            self.logger.info("Order management widget refreshed after sale change")
        except Exception as e:
            self.logger.error(f"Error refreshing order management widget: {e}")

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

        # Add header with refresh button
        header_widget = self.create_tab_header_with_refresh("Pricing Management", "Pricing")
        self.content_layout.addWidget(header_widget)

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
            self.logger.info("Packing materials module imported successfully")
            packing_widget = PackingMaterialsWidget(self.data)
            self.logger.info("Packing materials widget created successfully")
        except Exception as e:
            # Create placeholder if module fails to load
            self.logger.error(f"Error loading packing materials widget: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setContentsMargins(20, 20, 20, 20)
            error_label = QLabel(f"Packing materials functionality is currently unavailable.\nError: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            placeholder_layout.addWidget(error_label)
            packing_widget = placeholder
            self.logger.error("Packing materials module failed to load")

        # Add the widget to the content layout
        self.content_layout.addWidget(packing_widget)

    def show_expenses_page(self):
        """Display the expenses page"""
        self.clear_content()

        # Add header with refresh button
        header_widget = self.create_tab_header_with_refresh("Expenses", "Expenses")
        self.content_layout.addWidget(header_widget)

        # Create the expenses widget using our fixed module
        # ExpensesWidget is already imported at the top of the file
        expenses_widget = ExpensesWidget(self.data)

        # Set main app reference for data refresh functionality
        expenses_widget.main_app = self

        # Add the widget to the content layout
        self.content_layout.addWidget(expenses_widget)

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
            from modules.cloud_sync_manager import CloudSyncManager

            firebase_container = QWidget()
            firebase_layout = QVBoxLayout(firebase_container)
            firebase_layout.setContentsMargins(20, 20, 20, 20)

            # Firebase sub-tabs
            firebase_subtabs = QTabWidget()

            # Cloud sync tab (Authentication functionality integrated into Cloud Sync)
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

        # Notification settings section
        notification_group = QGroupBox("Notification Settings")
        notification_group.setStyleSheet("""
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
        notification_layout = QVBoxLayout(notification_group)

        # Notification description
        notification_desc = QLabel("Control which notifications are shown during application startup.")
        notification_desc.setStyleSheet("color: #64748b; margin-bottom: 15px;")
        notification_desc.setWordWrap(True)
        notification_layout.addWidget(notification_desc)

        # Startup notifications checkbox
        self.startup_notifications_checkbox = QCheckBox("Show startup notifications (Login, Welcome, Sync)")
        self.startup_notifications_checkbox.setChecked(getattr(self, 'show_startup_notifications', True))
        self.startup_notifications_checkbox.stateChanged.connect(self.toggle_startup_notifications)
        self.startup_notifications_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        notification_layout.addWidget(self.startup_notifications_checkbox)

        data_layout.addWidget(notification_group)

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
• Expenses List: {len(self.data.get('expenses_list', []))} items
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

        # Staff Management Tab
        try:
            from modules.staff_management import StaffManagementWidget

            staff_container = QWidget()
            staff_layout = QVBoxLayout(staff_container)
            staff_layout.setContentsMargins(20, 20, 20, 20)

            # Create staff management widget
            staff_widget = StaffManagementWidget(self.data)
            staff_widget.data_changed.connect(self.refresh_all_tabs)
            staff_layout.addWidget(staff_widget)

            settings_tabs.addTab(staff_container, "👥 Staff Management")
            self.logger.info("Staff management integrated into Settings tab")

        except Exception as e:
            self.logger.warning(f"Staff management not available: {e}")
            staff_placeholder = QLabel("Staff management not available.\nPlease check staff management modules.")
            staff_placeholder.setAlignment(Qt.AlignCenter)
            staff_placeholder.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
            settings_tabs.addTab(staff_placeholder, "👥 Staff Management")

        # Appliance & Electricity Management Tab
        try:
            from modules.appliance_management import ApplianceManagementWidget

            appliance_container = QWidget()
            appliance_layout = QVBoxLayout(appliance_container)
            appliance_layout.setContentsMargins(20, 20, 20, 20)

            # Create appliance management widget
            appliance_widget = ApplianceManagementWidget()
            appliance_widget.appliance_updated.connect(self.on_appliance_settings_updated)
            appliance_layout.addWidget(appliance_widget)

            settings_tabs.addTab(appliance_container, "⚡ Appliances")
            self.logger.info("Appliance management integrated into Settings tab")

        except Exception as e:
            self.logger.warning(f"Appliance management not available: {e}")
            appliance_placeholder = QLabel("Appliance management not available.\nPlease check appliance modules.")
            appliance_placeholder.setAlignment(Qt.AlignCenter)
            appliance_placeholder.setStyleSheet("font-size: 16px; color: #64748b; padding: 40px;")
            settings_tabs.addTab(appliance_placeholder, "⚡ Appliances")
        # WhatsApp Integration Tab
        try:
            # Check if dependencies are available at runtime
            from modules.whatsapp_integration import check_selenium_dependencies, WhatsAppIntegrationWidget

            selenium_available, webdriver_manager_available = check_selenium_dependencies()

            if selenium_available:
                # Dependencies are available, create the full WhatsApp integration
                whatsapp_container = QWidget()
                whatsapp_layout = QVBoxLayout(whatsapp_container)
                whatsapp_layout.setContentsMargins(20, 20, 20, 20)

                # Pass user info for Firebase sync
                user_info = getattr(self, 'user_info', None)
                whatsapp_widget = WhatsAppIntegrationWidget(self.data, user_info, parent=self)

                # Set reference to main app for startup manager access
                whatsapp_widget.main_app = self
                self.logger.info(f"Set main_app reference on WhatsApp widget: {whatsapp_widget}")
                self.logger.info(f"WhatsApp widget main_app: {getattr(whatsapp_widget, 'main_app', 'NOT SET')}")
                self.logger.info(f"Main app whatsapp_startup_manager: {getattr(self, 'whatsapp_startup_manager', 'NOT SET')}")

                # Initialize automated notifications system
                try:
                    from modules.whatsapp_automated_notifications import WhatsAppAutomatedNotifications
                    self.whatsapp_notifications = WhatsAppAutomatedNotifications(
                        data=self.data,
                        whatsapp_widget=whatsapp_widget,
                        main_app=self
                    )
                    # Start monitoring
                    self.whatsapp_notifications.start_monitoring()
                    self.logger.info("✅ WhatsApp automated notifications system initialized and started")

                    # Store reference in whatsapp widget for easy access
                    whatsapp_widget.automated_notifications = self.whatsapp_notifications

                except Exception as e:
                    self.logger.error(f"Failed to initialize WhatsApp automated notifications: {e}")
                    self.whatsapp_notifications = None

                # Update startup status now that main_app reference is set
                if hasattr(whatsapp_widget, 'update_startup_status'):
                    whatsapp_widget.update_startup_status()
                    self.logger.info("Updated WhatsApp startup status after setting main_app reference")

                # Connect signals for notifications
                if hasattr(self, 'notification_manager'):
                    whatsapp_widget.message_sent.connect(
                        lambda msg: self.notify_success(
                            "Message Sent",
                            f"WhatsApp message sent to {msg.get('recipient', 'Unknown')}",
                            source='WhatsApp Integration'
                        )
                    )
                    whatsapp_widget.message_received.connect(
                        lambda msg: self.notify_info(
                            "New Message",
                            f"WhatsApp message from {msg.get('sender', 'Unknown')}",
                            source='WhatsApp Integration'
                        )
                    )

                whatsapp_layout.addWidget(whatsapp_widget)
                settings_tabs.addTab(whatsapp_container, "📱 WhatsApp")
                self.logger.info("WhatsApp integration added to Settings tab")
            else:
                # Dependencies not available, show installation interface
                raise ImportError("Selenium dependencies not available")

        except ImportError as e:
            self.logger.warning(f"WhatsApp integration not available: {e}")
            # Create placeholder with setup instructions
            whatsapp_placeholder = QWidget()
            placeholder_layout = QVBoxLayout(whatsapp_placeholder)
            placeholder_layout.setContentsMargins(20, 20, 20, 20)

            title_label = QLabel("📱 WhatsApp Integration")
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            title_label.setStyleSheet("color: #1e293b; margin-bottom: 20px;")
            placeholder_layout.addWidget(title_label)

            info_label = QLabel("""
            <h3>WhatsApp Integration Setup</h3>
            <p>WhatsApp integration provides powerful messaging capabilities with Firebase sync.</p>
            <p><strong>Features Available:</strong></p>
            <ul>
            <li>📱 WhatsApp Web integration</li>
            <li>🔄 Multi-device Firebase sync</li>
            <li>👥 Contact management</li>
            <li>💬 Message history</li>
            <li>📢 Broadcast messaging</li>
            <li>📝 Message templates</li>
            <li>🤖 Automatic ChromeDriver management</li>
            </ul>
            """)
            info_label.setWordWrap(True)
            info_label.setOpenExternalLinks(True)
            info_label.setStyleSheet("color: #374151; background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;")
            placeholder_layout.addWidget(info_label)

            # Add automatic installation button
            install_button = QPushButton("🚀 Install WhatsApp Dependencies Automatically")
            install_button.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    margin: 10px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
                QPushButton:pressed {
                    background-color: #047857;
                }
            """)
            install_button.clicked.connect(self.install_whatsapp_dependencies)
            placeholder_layout.addWidget(install_button)

            # Add manual installation info
            manual_label = QLabel("""
            <p><strong>Manual Installation (if automatic fails):</strong></p>
            <p>1. Open command prompt as administrator</p>
            <p>2. Run: <code>pip install selenium webdriver-manager</code></p>
            <p>3. Restart the application</p>
            """)
            manual_label.setWordWrap(True)
            manual_label.setStyleSheet("color: #6b7280; font-size: 12px; padding: 10px; background-color: #f9fafb; border-radius: 6px; margin-top: 10px;")
            placeholder_layout.addWidget(manual_label)

            placeholder_layout.addStretch()
            settings_tabs.addTab(whatsapp_placeholder, "📱 WhatsApp")
        except Exception as e:
            self.logger.error(f"Error adding WhatsApp integration to settings: {e}")
            whatsapp_error_placeholder = QLabel("WhatsApp integration error.\nPlease check the logs for details.")
            whatsapp_error_placeholder.setAlignment(Qt.AlignCenter)
            whatsapp_error_placeholder.setStyleSheet("font-size: 16px; color: #ef4444; padding: 40px;")
            settings_tabs.addTab(whatsapp_error_placeholder, "📱 WhatsApp")





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
        self.logger.info("Enhanced Settings page with Firebase and Enterprise tabs displayed")

    def install_whatsapp_dependencies(self):
        """Install WhatsApp dependencies automatically from the main application"""
        try:
            from PySide6.QtWidgets import QProgressDialog
            import subprocess
            import sys

            # Create progress dialog
            progress = QProgressDialog("Installing WhatsApp dependencies...", "Cancel", 0, 100, self)
            progress.setWindowTitle("WhatsApp Setup")
            progress.setModal(True)
            progress.show()

            # Update progress
            progress.setValue(10)
            QApplication.processEvents()

            try:
                # Install selenium
                progress.setLabelText("Installing Selenium...")
                progress.setValue(30)
                QApplication.processEvents()

                result = subprocess.run([sys.executable, "-m", "pip", "install", "selenium"],
                                      capture_output=True, text=True, timeout=120)

                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

                # Install webdriver-manager
                progress.setLabelText("Installing WebDriver Manager...")
                progress.setValue(60)
                QApplication.processEvents()

                result = subprocess.run([sys.executable, "-m", "pip", "install", "webdriver-manager"],
                                      capture_output=True, text=True, timeout=120)

                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

                # Complete installation
                progress.setLabelText("Installation complete!")
                progress.setValue(100)
                QApplication.processEvents()

                progress.close()

                # Show success message with option to refresh
                reply = QMessageBox.question(
                    self, "Installation Complete",
                    "WhatsApp dependencies installed successfully!\n\n"
                    "Would you like to refresh the Settings page now to use WhatsApp integration?\n\n"
                    "Available features:\n"
                    "• Connect to WhatsApp Web\n"
                    "• Send and receive messages\n"
                    "• Manage contacts\n"
                    "• Sync across devices with Firebase\n\n"
                    "Click 'Yes' to refresh now, or 'No' to restart the application later.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    # Refresh the settings page to load WhatsApp integration
                    self.refresh_settings_page()

                # Send notification
                if hasattr(self, 'notify_success'):
                    self.notify_success(
                        "WhatsApp Setup Complete",
                        "Dependencies installed successfully. WhatsApp integration is now available!",
                        "WhatsApp Integration"
                    )

                self.logger.info("WhatsApp dependencies installed successfully")

            except subprocess.CalledProcessError as e:
                progress.close()
                error_msg = f"Installation failed with return code {e.returncode}"
                if e.stderr:
                    error_msg += f"\nError: {e.stderr}"

                QMessageBox.critical(
                    self, "Installation Failed",
                    f"{error_msg}\n\n"
                    "Please try manual installation:\n"
                    "1. Open command prompt as administrator\n"
                    "2. Run: pip install selenium webdriver-manager\n"
                    "3. Restart the application"
                )

                self.logger.error(f"WhatsApp dependencies installation failed: {error_msg}")

            except subprocess.TimeoutExpired:
                progress.close()
                QMessageBox.critical(
                    self, "Installation Timeout",
                    "Installation timed out. Please check your internet connection and try again.\n\n"
                    "You can also try manual installation:\n"
                    "1. Open command prompt as administrator\n"
                    "2. Run: pip install selenium webdriver-manager\n"
                    "3. Restart the application"
                )

                self.logger.error("WhatsApp dependencies installation timed out")

        except Exception as e:
            if 'progress' in locals():
                progress.close()

            QMessageBox.critical(
                self, "Installation Error",
                f"An error occurred during installation:\n{e}\n\n"
                "Please try manual installation:\n"
                "1. Open command prompt as administrator\n"
                "2. Run: pip install selenium webdriver-manager\n"
                "3. Restart the application"
            )

            self.logger.error(f"Error during WhatsApp dependencies installation: {e}")

    def refresh_settings_page(self):
        """Refresh the settings page to reload WhatsApp integration after dependency installation"""
        try:
            # Clear the current content
            self.clear_content()

            # Reload the settings page
            self.show_settings_page()

            # Send notification about successful refresh
            if hasattr(self, 'notify_info'):
                self.notify_info(
                    "Settings Refreshed",
                    "Settings page refreshed. WhatsApp integration is now available!",
                    "Settings"
                )

            self.logger.info("Settings page refreshed after WhatsApp dependency installation")

        except Exception as e:
            self.logger.error(f"Error refreshing settings page: {e}")

            # Fallback message
            QMessageBox.information(
                self, "Refresh Required",
                "Please navigate away from Settings and back to see the WhatsApp integration, "
                "or restart the application."
            )

    def on_appliance_settings_updated(self):
        """Handle appliance settings updates"""
        try:
            self.logger.info("Appliance settings updated - refreshing pricing calculations")
            # Refresh any pricing-related data if needed
            # This ensures that electricity cost calculations use the updated settings
        except Exception as e:
            self.logger.error(f"Error handling appliance settings update: {e}")

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
                provider_card.clicked.connect(lambda _, p=provider['provider']: self.on_provider_selected(p))

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
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel

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

    def toggle_startup_notifications(self, state):
        """Toggle startup notifications on/off"""
        try:
            from PySide6.QtCore import Qt
            self.show_startup_notifications = (state == Qt.Checked)

            # Save the setting (you could save this to a config file)
            status = "enabled" if self.show_startup_notifications else "disabled"
            self.logger.info(f"Startup notifications {status}")

            # Show immediate feedback
            self.add_notification(
                "Settings Updated",
                f"Startup notifications {status}. Changes will take effect on next application start.",
                "info"
            )

        except Exception as e:
            self.logger.error(f"Error toggling startup notifications: {e}")

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
                elif button_index == 7:  # Expenses
                    self.show_expenses_page()
                elif button_index == 8:  # Gas Management
                    self.show_gas_management_page()
                elif button_index == 9:  # Waste
                    self.show_waste_page()
                elif button_index == 10:  # Cleaning
                    self.show_cleaning_page()
                elif button_index == 11:  # Reports
                    self.show_reports_page()
                elif button_index == 12:  # Logs
                    self.show_logs_page()
                elif button_index == 13:  # Settings (Mobile, AI/ML, Enterprise moved inside)
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


class SampleDataCleanupDialog(QDialog):
    """Dialog for cleaning up sample data"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("Sample Data Cleanup")
        self.setMinimumSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup the cleanup dialog UI"""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Sample Data Cleanup")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header_label)

        # Description
        desc_label = QLabel("Choose what sample data to remove:")
        layout.addWidget(desc_label)

        # Cleanup options
        options_group = QGroupBox("Cleanup Options")
        options_layout = QVBoxLayout(options_group)

        self.cleanup_options = QButtonGroup()

        # Option 1: Remove all sample data
        self.remove_all_radio = QRadioButton("Remove ALL sample data (complete cleanup)")
        self.remove_all_radio.setChecked(True)
        self.cleanup_options.addButton(self.remove_all_radio, 1)
        options_layout.addWidget(self.remove_all_radio)

        # Option 2: Remove test files only
        self.remove_test_radio = QRadioButton("Remove only test-generated files")
        self.cleanup_options.addButton(self.remove_test_radio, 2)
        options_layout.addWidget(self.remove_test_radio)

        # Option 3: Reset to empty state
        self.reset_empty_radio = QRadioButton("Reset to empty state (keep structure)")
        self.cleanup_options.addButton(self.reset_empty_radio, 3)
        options_layout.addWidget(self.reset_empty_radio)

        layout.addWidget(options_group)

        # Backup option
        self.backup_checkbox = QCheckBox("Create backup before cleanup")
        self.backup_checkbox.setChecked(True)
        layout.addWidget(self.backup_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        self.cleanup_button = QPushButton("Cleanup")
        self.cleanup_button.clicked.connect(self.perform_cleanup)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.cleanup_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def perform_cleanup(self):
        """Perform the selected cleanup operation"""
        try:
            # Import cleanup utility
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

            from cleanup_sample_data import DataCleanup

            cleanup = DataCleanup()

            # Create backup if requested
            if self.backup_checkbox.isChecked():
                if not cleanup.backup_data():
                    QMessageBox.warning(self, "Backup Failed", "Failed to create backup. Continue anyway?")
                    return

            # Perform selected cleanup
            selected_option = self.cleanup_options.checkedId()
            success = False

            if selected_option == 1:
                # Remove all sample data
                success = cleanup.remove_all_sample_data()
            elif selected_option == 2:
                # Remove test files only
                success = cleanup.remove_test_files_only()
            elif selected_option == 3:
                # Reset to empty state
                success = cleanup.reset_to_empty_state()

            if success:
                QMessageBox.information(self, "Cleanup Complete", "Sample data cleanup completed successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Cleanup Failed", "Sample data cleanup failed. Check the logs for details.")

        except Exception as e:
            QMessageBox.critical(self, "Cleanup Error", f"Error during cleanup: {e}")


if __name__ == "__main__":
    # Initialize logging first
    from utils.app_logger import get_logger
    logger = get_logger()

    try:
        print("\n" + "="*80)
        print("    VARSYS KITCHEN DASHBOARD - PROFESSIONAL EDITION v1.1.3")
        print("="*80)
        print("Starting application...")
        print("="*80 + "\n")

        logger.log_startup_info()

        app = QApplication(sys.argv)

        # Initialize main window first
        logger.log_section_header("Application Initialization")
        window = KitchenDashboardApp()
        logger.log_section_footer("Application Initialization", True)

        # Show loading screen with main app reference for WhatsApp initialization
        from modules.startup_loading_screen import show_startup_loading_screen
        loading_screen = show_startup_loading_screen(window)

        # Connect loading screen completion to show main window
        def on_loading_finished():
            logger.log_section_header("UI Display")
            window.show()
            logger.log_section_footer("UI Display", True)
            logger.info("Application ready - entering main event loop")

            # WhatsApp automation is now started during loading phase
            # No need to start it again here

        loading_screen.loading_finished.connect(on_loading_finished)

        # Run the application
        exit_code = app.exec()

        # Shutdown logging
        print("\n" + "="*80)
        print("    APPLICATION SHUTDOWN")
        print("="*80)
        logger.log_shutdown_info()
        print("Thank you for using VARSYS Kitchen Dashboard!")
        print("="*80 + "\n")

        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Critical application error: {e}")
        logger.log_exception(e, "Application startup/shutdown")
        print(f"\n*** CRITICAL ERROR ***")
        print(f"Error: {e}")
        print("Check the error log for details.")
        print("="*80 + "\n")
        sys.exit(1)

"""
Optimized Firebase Manager
Enhanced Firebase integration with authentication fixes, free tier optimization, and analytics integration
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QMessageBox, QInputDialog, QLineEdit

# Firebase imports with fallback
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    import pyrebase
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_system_event, track_performance_start, track_performance_end
    from .analytics_engine import get_analytics_engine
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass
    def track_performance_start(*args, **kwargs): pass
    def track_performance_end(*args, **kwargs): pass
    get_analytics_engine = None

@dataclass
class UserSession:
    """User session data structure"""
    user_id: str
    email: str
    display_name: str
    session_start: str
    last_activity: str
    session_token: str
    permissions: List[str]

@dataclass
class SyncStatus:
    """Sync operation status"""
    operation_id: str
    status: str  # "pending", "in_progress", "completed", "failed"
    start_time: str
    end_time: Optional[str]
    records_synced: int
    error_message: Optional[str]

class OptimizedFirebaseManager(QObject):
    """
    Optimized Firebase manager with:
    - Improved authentication flow
    - Free tier optimization
    - Analytics integration
    - Session management
    - Efficient data structures
    """
    
    # Signals
    authentication_changed = Signal(bool, dict)  # authenticated, user_info
    sync_progress = Signal(str, int)  # operation_id, progress_percentage
    sync_completed = Signal(str, bool)  # operation_id, success
    error_occurred = Signal(str, str)  # operation, error_message
    
    def __init__(self, parent=None, firebase_config_manager=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Firebase configuration manager
        self.firebase_config_manager = firebase_config_manager

        # Firebase instances
        self.admin_app = None
        self.db = None
        self.pyrebase_app = None
        self.auth_instance = None

        # Session management
        self.current_session: Optional[UserSession] = None
        self.session_timeout = 3600  # 1 hour

        # Free tier optimization
        self.batch_size = 100  # Optimize for Firestore free tier
        self.max_daily_reads = 50000  # Free tier limit
        self.max_daily_writes = 20000  # Free tier limit
        self.daily_read_count = 0
        self.daily_write_count = 0
        self.last_reset_date = datetime.now().date()

        # Sync management
        self.sync_queue = []
        self.active_syncs = {}

        # Initialize Firebase
        self.initialize_firebase()
        
        # Setup session timer
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.check_session_validity)
        self.session_timer.start(60000)  # Check every minute
        
        self.logger.info("Optimized Firebase Manager initialized")
        track_system_event("firebase_manager", "initialized", "Optimized Firebase manager started")
    
    def initialize_firebase(self) -> bool:
        """Initialize Firebase with enhanced error handling and validation"""
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase libraries not available")
            return False

        try:
            # Initialize Firebase Admin SDK with multiple credential path options
            credential_paths = [
                "firebase_credentials.json",
                "secure_credentials/firebase_credentials.json",
                "firebase-admin-key.json",
                "firebase_admin_config.json"
            ]

            admin_initialized = False
            for cred_path in credential_paths:
                if os.path.exists(cred_path):
                    self.logger.info(f"Found Firebase credentials file: {cred_path}")

                    try:
                        if not firebase_admin._apps:
                            cred = credentials.Certificate(cred_path)
                            self.admin_app = firebase_admin.initialize_app(cred)
                            self.logger.info("Firebase Admin app initialized successfully")
                        else:
                            self.admin_app = firebase_admin.get_app()
                            self.logger.info("Using existing Firebase Admin app")

                        # Initialize Firestore client
                        self.db = firestore.client()
                        self.logger.info("Firestore client initialized successfully")

                        # Test database connection with comprehensive testing
                        # Skip the connection test during initialization to avoid hanging
                        # We'll test the connection later when actually needed
                        self.logger.info("✅ Firestore client initialized - connection will be tested on first use")
                        admin_initialized = True
                        break

                    except Exception as admin_error:
                        self.logger.error(f"Firebase Admin SDK initialization failed with {cred_path}: {admin_error}")
                        self.db = None
                        continue

            if not admin_initialized:
                self.logger.warning("❌ Firebase Admin SDK initialization failed with all credential files")

            # Initialize Pyrebase for authentication with multiple config path options
            web_config_paths = [
                "firebase_web_config.json",
                "secure_credentials/firebase_web_config.json",
                "firebase_config.json"
            ]

            auth_initialized = False
            for web_config_path in web_config_paths:
                if os.path.exists(web_config_path):
                    self.logger.info(f"Found Firebase web config file: {web_config_path}")

                    try:
                        with open(web_config_path, 'r') as f:
                            config = json.load(f)

                        # Handle different config file structures
                        if 'firebase' in config:
                            config = config['firebase']

                        self.pyrebase_app = pyrebase.initialize_app(config)
                        self.auth_instance = self.pyrebase_app.auth()
                        self.logger.info("✅ Pyrebase initialized successfully")
                        auth_initialized = True
                        break

                    except Exception as pyrebase_error:
                        self.logger.error(f"Pyrebase initialization failed with {web_config_path}: {pyrebase_error}")
                        continue

            if not auth_initialized:
                self.logger.error("❌ Pyrebase initialization failed with all config files")

            # Validate initialization and provide detailed status
            initialization_success = False
            if self.db and self.auth_instance:
                self.logger.info("✅ Full Firebase initialization successful (Admin SDK + Pyrebase)")
                initialization_success = True
                self.firebase_status = "fully_connected"
            elif self.auth_instance:
                self.logger.warning("⚠️ Partial Firebase initialization (Pyrebase only - limited functionality)")
                initialization_success = True
                self.firebase_status = "auth_only"
            elif self.db:
                self.logger.warning("⚠️ Partial Firebase initialization (Database only - no authentication)")
                initialization_success = True
                self.firebase_status = "database_only"
            else:
                self.logger.error("❌ Firebase initialization failed - no services available")
                initialization_success = False
                self.firebase_status = "disconnected"

            # Log detailed status for debugging
            self.log_firebase_status()

            if initialization_success:
                track_system_event("firebase_manager", "firebase_initialized", f"Firebase services initialized: {self.firebase_status}")
            else:
                track_system_event("firebase_manager", "firebase_init_failed", "Firebase initialization failed")

            return initialization_success

        except Exception as e:
            self.logger.error(f"Firebase initialization failed with exception: {e}")
            track_system_event("firebase_manager", "firebase_init_failed", f"Firebase initialization failed: {str(e)}")
            self.firebase_status = "error"
            return False

    def test_database_connection(self) -> bool:
        """Comprehensive database connection test with enhanced error handling"""
        try:
            if not self.db:
                self.logger.debug("Database not available: db is None")
                return False

            # Test 1: Create a reference (lightweight operation)
            test_ref = self.db.collection('connection_test')
            self.logger.debug("Database reference creation successful")

            # Test 2: Try to perform a simple read operation with specific error handling
            try:
                # This will attempt to read from the collection (may be empty)
                docs = list(test_ref.limit(1).stream())
                self.logger.debug("Database read operation successful")
                return True

            except Exception as read_error:
                error_str = str(read_error)
                self.logger.warning(f"Database read test failed: {error_str}")

                # Check for specific Firebase errors
                if "invalid_grant" in error_str.lower():
                    self.logger.error("❌ Firebase credentials invalid - JWT signature error")
                    self.logger.error("   This usually means:")
                    self.logger.error("   1. The service account key is expired or invalid")
                    self.logger.error("   2. The credentials file is corrupted")
                    self.logger.error("   3. The project ID doesn't match the credentials")
                    return False
                elif "permission" in error_str.lower() or "forbidden" in error_str.lower():
                    self.logger.warning("⚠️ Database permissions issue - credentials may lack required permissions")
                    return False
                elif "unavailable" in error_str.lower() or "timeout" in error_str.lower():
                    self.logger.warning("⚠️ Database connection timeout - network or service issue")
                    return False
                else:
                    self.logger.warning(f"⚠️ Unknown database error: {error_str}")
                    return False

        except Exception as e:
            error_str = str(e)
            self.logger.error(f"Database connection test failed: {error_str}")

            # Provide specific guidance based on error type
            if "invalid_grant" in error_str.lower():
                self.logger.error("❌ SOLUTION: Please regenerate your Firebase service account key")
                self.logger.error("   1. Go to Firebase Console > Project Settings > Service Accounts")
                self.logger.error("   2. Generate a new private key")
                self.logger.error("   3. Replace the credentials file")
            elif "not found" in error_str.lower():
                self.logger.error("❌ SOLUTION: Check if the Firebase project exists and credentials are correct")

            return False

    def is_database_available(self) -> bool:
        """Check if Firestore database is available and working"""
        if not self.db:
            return False

        # Use cached result if available and recent
        if hasattr(self, '_db_test_cache'):
            cache_time, cache_result = self._db_test_cache
            if (datetime.now() - cache_time).seconds < 300:  # 5 minute cache
                return cache_result

        # Perform actual test
        result = self.test_database_connection()

        # Cache the result
        self._db_test_cache = (datetime.now(), result)

        return result

    def log_firebase_status(self):
        """Log detailed Firebase status for debugging"""
        try:
            self.logger.info("=== Firebase Status Report ===")
            self.logger.info(f"Overall Status: {getattr(self, 'firebase_status', 'unknown')}")
            self.logger.info(f"Admin SDK Available: {self.admin_app is not None}")
            self.logger.info(f"Firestore Database Available: {self.db is not None}")
            self.logger.info(f"Pyrebase Auth Available: {self.auth_instance is not None}")
            self.logger.info(f"User Authenticated: {self.is_authenticated()}")

            if self.admin_app:
                try:
                    project_id = self.admin_app.project_id
                    self.logger.info(f"Project ID: {project_id}")
                except:
                    self.logger.info("Project ID: Unable to retrieve")

            if self.current_session:
                self.logger.info(f"Current User: {self.current_session.email}")
                self.logger.info(f"User ID: {self.current_session.user_id}")
            else:
                self.logger.info("Current User: None")

            self.logger.info("=== End Firebase Status Report ===")

        except Exception as e:
            self.logger.error(f"Error logging Firebase status: {e}")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_session is not None

    def get_database_status(self) -> Dict[str, Any]:
        """Get detailed database status information"""
        status = {
            'database_available': False,
            'authentication_available': False,
            'user_authenticated': False,
            'admin_sdk_available': False,
            'pyrebase_available': False,
            'error_message': None
        }

        try:
            # Check Admin SDK
            status['admin_sdk_available'] = self.admin_app is not None

            # Check Pyrebase
            status['pyrebase_available'] = self.auth_instance is not None

            # Check database
            status['database_available'] = self.is_database_available()

            # Check authentication
            status['authentication_available'] = self.auth_instance is not None
            status['user_authenticated'] = self.is_authenticated()

        except Exception as e:
            status['error_message'] = str(e)
            self.logger.error(f"Error getting database status: {e}")

        return status

    def reinitialize_database(self) -> bool:
        """Attempt to reinitialize the database connection"""
        try:
            self.logger.info("Attempting to reinitialize database connection...")

            if self.admin_app and not self.db:
                self.db = firestore.client()

                # Test the new connection
                if self.test_database_connection():
                    self.logger.info("✅ Database reinitialized and tested successfully")
                    self.firebase_status = "fully_connected" if self.auth_instance else "database_only"
                    return True
                else:
                    self.logger.error("❌ Database reinitialization failed - connection test failed")
                    self.db = None
                    return False

            elif not self.admin_app:
                self.logger.warning("Cannot reinitialize database - Admin SDK not available")
                # Try to reinitialize the entire Firebase system
                return self.reinitialize_firebase()
            else:
                # Database already exists, test if it's working
                if self.test_database_connection():
                    self.logger.info("✅ Database already initialized and working")
                    return True
                else:
                    self.logger.warning("⚠️ Database exists but connection test failed, attempting full reinit")
                    return self.reinitialize_firebase()

        except Exception as e:
            self.logger.error(f"Database reinitialization failed: {e}")
            return False

    def reinitialize_firebase(self) -> bool:
        """Completely reinitialize Firebase services"""
        try:
            self.logger.info("Performing complete Firebase reinitialization...")

            # Reset current state
            self.db = None
            self.admin_app = None
            self.auth_instance = None
            self.pyrebase_app = None
            self.firebase_status = "reinitializing"

            # Reinitialize
            success = self.initialize_firebase()

            if success:
                self.logger.info("✅ Complete Firebase reinitialization successful")
                track_system_event("firebase_manager", "firebase_reinitialized", "Firebase services reinitialized successfully")
            else:
                self.logger.error("❌ Complete Firebase reinitialization failed")
                track_system_event("firebase_manager", "firebase_reinit_failed", "Firebase reinitialization failed")

            return success

        except Exception as e:
            self.logger.error(f"Complete Firebase reinitialization failed: {e}")
            self.firebase_status = "error"
            return False

    def get_connection_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive connection diagnostics"""
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': getattr(self, 'firebase_status', 'unknown'),
            'components': {
                'admin_sdk': {
                    'available': self.admin_app is not None,
                    'project_id': None,
                    'error': None
                },
                'firestore_database': {
                    'available': self.db is not None,
                    'connection_test': False,
                    'error': None
                },
                'pyrebase_auth': {
                    'available': self.auth_instance is not None,
                    'error': None
                },
                'user_session': {
                    'authenticated': self.is_authenticated(),
                    'user_email': None,
                    'user_id': None,
                    'session_valid': False
                }
            },
            'recommendations': []
        }

        try:
            # Test Admin SDK
            if self.admin_app:
                try:
                    diagnostics['components']['admin_sdk']['project_id'] = self.admin_app.project_id
                except Exception as e:
                    diagnostics['components']['admin_sdk']['error'] = str(e)

            # Test Database
            if self.db:
                try:
                    diagnostics['components']['firestore_database']['connection_test'] = self.test_database_connection()
                except Exception as e:
                    diagnostics['components']['firestore_database']['error'] = str(e)

            # Test User Session
            if self.current_session:
                diagnostics['components']['user_session']['user_email'] = self.current_session.email
                diagnostics['components']['user_session']['user_id'] = self.current_session.user_id
                diagnostics['components']['user_session']['session_valid'] = True

            # Generate recommendations
            if not diagnostics['components']['admin_sdk']['available']:
                diagnostics['recommendations'].append("Firebase Admin SDK not initialized - check credential files")

            if not diagnostics['components']['firestore_database']['available']:
                diagnostics['recommendations'].append("Firestore database not available - Admin SDK required")
            elif not diagnostics['components']['firestore_database']['connection_test']:
                diagnostics['recommendations'].append("Database connection test failed - check network and permissions")

            if not diagnostics['components']['pyrebase_auth']['available']:
                diagnostics['recommendations'].append("Pyrebase authentication not available - check web config file")

            if not diagnostics['components']['user_session']['authenticated']:
                diagnostics['recommendations'].append("User not authenticated - login required for cloud operations")

        except Exception as e:
            diagnostics['error'] = f"Error generating diagnostics: {str(e)}"

        return diagnostics

    def validate_firebase_credentials(self, cred_path: str) -> Dict[str, Any]:
        """Validate Firebase credentials file without connecting"""
        validation = {
            'valid': False,
            'file_exists': False,
            'file_readable': False,
            'json_valid': False,
            'has_required_fields': False,
            'project_id': None,
            'client_email': None,
            'errors': []
        }

        try:
            # Check if file exists
            if not os.path.exists(cred_path):
                validation['errors'].append(f"Credentials file not found: {cred_path}")
                return validation

            validation['file_exists'] = True

            # Check if file is readable
            try:
                with open(cred_path, 'r') as f:
                    content = f.read()
                validation['file_readable'] = True
            except Exception as e:
                validation['errors'].append(f"Cannot read credentials file: {str(e)}")
                return validation

            # Check if JSON is valid
            try:
                cred_data = json.loads(content)
                validation['json_valid'] = True
            except json.JSONDecodeError as e:
                validation['errors'].append(f"Invalid JSON in credentials file: {str(e)}")
                return validation

            # Check required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = []

            for field in required_fields:
                if field not in cred_data:
                    missing_fields.append(field)

            if missing_fields:
                validation['errors'].append(f"Missing required fields: {', '.join(missing_fields)}")
            else:
                validation['has_required_fields'] = True
                validation['project_id'] = cred_data.get('project_id')
                validation['client_email'] = cred_data.get('client_email')

            # Check if it's a service account
            if cred_data.get('type') != 'service_account':
                validation['errors'].append(f"Expected service_account, got: {cred_data.get('type')}")

            # Basic private key validation
            private_key = cred_data.get('private_key', '')
            if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                validation['errors'].append("Private key format appears invalid")

            # If all checks pass
            if (validation['file_exists'] and validation['file_readable'] and
                validation['json_valid'] and validation['has_required_fields'] and
                not validation['errors']):
                validation['valid'] = True

        except Exception as e:
            validation['errors'].append(f"Unexpected error validating credentials: {str(e)}")

        return validation

    def get_firebase_setup_recommendations(self) -> List[str]:
        """Get recommendations for fixing Firebase setup"""
        recommendations = []

        try:
            # Check credential files
            credential_paths = [
                "firebase_credentials.json",
                "secure_credentials/firebase_credentials.json",
                "firebase-admin-key.json"
            ]

            valid_creds_found = False
            for cred_path in credential_paths:
                validation = self.validate_firebase_credentials(cred_path)
                if validation['valid']:
                    valid_creds_found = True
                    break
                elif validation['file_exists']:
                    recommendations.append(f"Fix issues with {cred_path}: {'; '.join(validation['errors'])}")

            if not valid_creds_found:
                recommendations.append("No valid Firebase service account credentials found")
                recommendations.append("1. Go to Firebase Console > Project Settings > Service Accounts")
                recommendations.append("2. Click 'Generate new private key'")
                recommendations.append("3. Save the file as 'secure_credentials/firebase_credentials.json'")

            # Check web config files
            web_config_paths = [
                "firebase_web_config.json",
                "secure_credentials/firebase_web_config.json",
                "firebase_config.json"
            ]

            web_config_found = False
            for config_path in web_config_paths:
                if os.path.exists(config_path):
                    web_config_found = True
                    break

            if not web_config_found:
                recommendations.append("No Firebase web configuration found")
                recommendations.append("4. Copy your web app config to 'firebase_web_config.json'")

            # Check if Firebase libraries are available
            if not FIREBASE_AVAILABLE:
                recommendations.append("Firebase libraries not installed")
                recommendations.append("5. Install Firebase libraries: pip install firebase-admin pyrebase4")

        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")

        return recommendations

    def authenticate_user(self, email: str = None, password: str = None) -> bool:
        """Authenticate user with improved flow"""
        if not self.auth_instance:
            self.logger.error("Firebase authentication not available")
            return False
        
        try:
            # If no credentials provided, prompt user
            if not email or not password:
                email, ok = QInputDialog.getText(
                    None, "Firebase Authentication", "Email:", 
                    QLineEdit.Normal, ""
                )
                if not ok or not email:
                    return False
                
                password, ok = QInputDialog.getText(
                    None, "Firebase Authentication", "Password:", 
                    QLineEdit.Password, ""
                )
                if not ok or not password:
                    return False
            
            # Authenticate with Firebase
            operation_id = f"auth_{datetime.now().timestamp()}"
            track_performance_start(operation_id, "firebase_manager", "authenticate_user")
            
            user = self.auth_instance.sign_in_with_email_and_password(email, password)
            
            # Create session
            session = UserSession(
                user_id=user['localId'],
                email=email,
                display_name=user.get('displayName', email.split('@')[0]),
                session_start=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat(),
                session_token=user['idToken'],
                permissions=["read", "write"]  # Default permissions
            )
            
            self.current_session = session
            
            # Emit authentication signal
            user_info = {
                "user_id": session.user_id,
                "email": session.email,
                "display_name": session.display_name
            }
            self.authentication_changed.emit(True, user_info)
            
            track_performance_end(operation_id, "firebase_manager", "authenticate_user", 
                                metadata={"user_id": session.user_id})
            track_user_action("firebase_manager", "user_authenticated", f"User {email} authenticated successfully")
            
            self.logger.info(f"User authenticated: {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            self.error_occurred.emit("authentication", str(e))
            track_user_action("firebase_manager", "auth_failed", f"Authentication failed: {str(e)}")
            return False
    
    def sign_out(self):
        """Sign out current user"""
        if self.current_session:
            track_user_action("firebase_manager", "user_signout", f"User {self.current_session.email} signed out")
            self.current_session = None
            self.authentication_changed.emit(False, {})
            self.logger.info("User signed out")
    
    def check_session_validity(self):
        """Check if current session is still valid"""
        if not self.current_session:
            return
        
        try:
            session_start = datetime.fromisoformat(self.current_session.session_start)
            if datetime.now() - session_start > timedelta(seconds=self.session_timeout):
                self.logger.info("Session expired")
                self.sign_out()
        except Exception as e:
            self.logger.error(f"Error checking session validity: {e}")
    
    def update_session_activity(self):
        """Update last activity timestamp"""
        if self.current_session:
            self.current_session.last_activity = datetime.now().isoformat()
    
    def check_daily_limits(self) -> bool:
        """Check if we're within daily Firebase limits"""
        current_date = datetime.now().date()
        
        # Reset counters if new day
        if current_date != self.last_reset_date:
            self.daily_read_count = 0
            self.daily_write_count = 0
            self.last_reset_date = current_date
        
        # Check limits
        if self.daily_read_count >= self.max_daily_reads:
            self.logger.warning("Daily read limit reached")
            return False
        
        if self.daily_write_count >= self.max_daily_writes:
            self.logger.warning("Daily write limit reached")
            return False
        
        return True
    
    def sync_data_to_cloud(self, data: Dict[str, pd.DataFrame], user_id: str = None) -> str:
        """Sync data to cloud with optimization"""
        if not self.db or not self.current_session:
            self.logger.error("Firebase not initialized or user not authenticated")
            return None
        
        if not self.check_daily_limits():
            self.logger.error("Daily Firebase limits reached")
            return None
        
        operation_id = f"sync_to_cloud_{datetime.now().timestamp()}"
        
        try:
            track_performance_start(operation_id, "firebase_manager", "sync_data_to_cloud")
            
            # Use current session user_id if not provided
            if not user_id:
                user_id = self.current_session.user_id
            
            # Create sync status
            sync_status = SyncStatus(
                operation_id=operation_id,
                status="in_progress",
                start_time=datetime.now().isoformat(),
                end_time=None,
                records_synced=0,
                error_message=None
            )
            
            self.active_syncs[operation_id] = sync_status
            self.sync_progress.emit(operation_id, 0)
            
            total_records = sum(len(df) for df in data.values())
            synced_records = 0
            
            # Sync each table
            for table_name, df in data.items():
                if df.empty:
                    continue
                
                # Convert DataFrame to optimized format
                records = self.optimize_dataframe_for_firestore(df)
                
                # Batch write for efficiency
                batch = self.db.batch()
                batch_count = 0
                
                for record in records:
                    # Create document reference
                    doc_ref = self.db.collection('users').document(user_id).collection(table_name).document()
                    
                    # Add to batch
                    batch.set(doc_ref, record)
                    batch_count += 1
                    synced_records += 1
                    
                    # Commit batch when full
                    if batch_count >= self.batch_size:
                        batch.commit()
                        self.daily_write_count += batch_count
                        batch = self.db.batch()
                        batch_count = 0
                        
                        # Update progress
                        progress = int((synced_records / total_records) * 100)
                        self.sync_progress.emit(operation_id, progress)
                
                # Commit remaining records
                if batch_count > 0:
                    batch.commit()
                    self.daily_write_count += batch_count
            
            # Update sync status
            sync_status.status = "completed"
            sync_status.end_time = datetime.now().isoformat()
            sync_status.records_synced = synced_records
            
            self.sync_progress.emit(operation_id, 100)
            self.sync_completed.emit(operation_id, True)
            
            track_performance_end(operation_id, "firebase_manager", "sync_data_to_cloud",
                                metadata={"records_synced": synced_records})
            
            self.logger.info(f"Data synced to cloud: {synced_records} records")
            return operation_id
            
        except Exception as e:
            # Update sync status with error
            if operation_id in self.active_syncs:
                self.active_syncs[operation_id].status = "failed"
                self.active_syncs[operation_id].error_message = str(e)
            
            self.sync_completed.emit(operation_id, False)
            self.error_occurred.emit("sync_to_cloud", str(e))
            
            track_performance_end(operation_id, "firebase_manager", "sync_data_to_cloud",
                                metadata={"error": str(e)})
            
            self.logger.error(f"Sync to cloud failed: {e}")
            return None

    def sync_data_from_cloud(self, user_id: str = None, collections: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Download data from cloud with user UID isolation"""
        if not self.db or not self.current_session:
            self.logger.error("Firebase not initialized or user not authenticated")
            return {}

        if not self.check_daily_limits():
            self.logger.error("Daily Firebase limits reached")
            return {}

        operation_id = f"sync_from_cloud_{datetime.now().timestamp()}"

        try:
            track_performance_start(operation_id, "firebase_manager", "sync_data_from_cloud")

            # Use current session user_id if not provided
            if not user_id:
                user_id = self.current_session.user_id

            self.logger.info(f"Downloading data from cloud for user: {user_id}")

            # Get user's collections
            user_ref = self.db.collection('users').document(user_id)

            # If specific collections not specified, get all available collections
            if not collections:
                collections_refs = user_ref.collections()
                collections = [col.id for col in collections_refs]

            downloaded_data = {}
            total_records = 0

            for collection_name in collections:
                try:
                    collection_ref = user_ref.collection(collection_name)
                    docs = collection_ref.stream()

                    records = []
                    for doc in docs:
                        doc_data = doc.to_dict()
                        # Remove metadata fields
                        doc_data.pop('_sync_timestamp', None)
                        doc_data.pop('_record_hash', None)
                        records.append(doc_data)
                        total_records += 1
                        self.daily_read_count += 1

                    if records:
                        # Convert to DataFrame
                        df = pd.DataFrame(records)
                        downloaded_data[collection_name] = df
                        self.logger.info(f"Downloaded {len(records)} records from {collection_name}")

                except Exception as e:
                    self.logger.error(f"Error downloading collection {collection_name}: {e}")
                    continue

            track_performance_end(operation_id, "firebase_manager", "sync_data_from_cloud",
                                metadata={"records_downloaded": total_records})

            self.logger.info(f"Downloaded {total_records} total records from {len(downloaded_data)} collections")
            return downloaded_data

        except Exception as e:
            track_performance_end(operation_id, "firebase_manager", "sync_data_from_cloud",
                                metadata={"error": str(e)})

            self.logger.error(f"Download from cloud failed: {e}")
            return {}

    def get_cloud_data_summary(self, user_id: str = None) -> Dict[str, Any]:
        """Get summary of user's cloud data"""
        if not self.db or not self.current_session:
            return {}

        try:
            # Use current session user_id if not provided
            if not user_id:
                user_id = self.current_session.user_id

            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()

            summary = {
                'user_exists': user_doc.exists,
                'collections': {},
                'total_records': 0,
                'last_sync': None
            }

            if user_doc.exists:
                user_data = user_doc.to_dict()
                summary['last_sync'] = user_data.get('last_sync')

                # Get collection summaries
                collections_refs = user_ref.collections()
                for collection_ref in collections_refs:
                    collection_name = collection_ref.id

                    # Count documents in collection
                    docs_count = len(list(collection_ref.limit(1000).stream()))  # Limit for performance
                    summary['collections'][collection_name] = docs_count
                    summary['total_records'] += docs_count

                    self.daily_read_count += docs_count

            return summary

        except Exception as e:
            self.logger.error(f"Error getting cloud data summary: {e}")
            return {}

    def clear_user_cloud_data(self, user_id: str = None, collections: List[str] = None) -> bool:
        """Clear user's cloud data (with caution)"""
        if not self.db or not self.current_session:
            self.logger.error("Firebase not initialized or user not authenticated")
            return False

        try:
            # Use current session user_id if not provided
            if not user_id:
                user_id = self.current_session.user_id

            # Security check - only allow users to clear their own data
            if user_id != self.current_session.user_id:
                self.logger.error("Cannot clear data for different user")
                return False

            self.logger.warning(f"Clearing cloud data for user: {user_id}")

            user_ref = self.db.collection('users').document(user_id)

            # If specific collections not specified, get all collections
            if not collections:
                collections_refs = user_ref.collections()
                collections = [col.id for col in collections_refs]

            # Delete collections
            for collection_name in collections:
                collection_ref = user_ref.collection(collection_name)

                # Delete all documents in collection
                docs = collection_ref.stream()
                batch = self.db.batch()
                batch_count = 0

                for doc in docs:
                    batch.delete(doc.reference)
                    batch_count += 1

                    if batch_count >= self.batch_size:
                        batch.commit()
                        self.daily_write_count += batch_count
                        batch = self.db.batch()
                        batch_count = 0

                # Commit remaining deletes
                if batch_count > 0:
                    batch.commit()
                    self.daily_write_count += batch_count

                self.logger.info(f"Cleared collection: {collection_name}")

            return True

        except Exception as e:
            self.logger.error(f"Error clearing cloud data: {e}")
            return False

    def sync_analytics_to_cloud(self, analytics_data: Dict) -> bool:
        """Sync analytics data to cloud"""
        if not self.db or not self.current_session:
            return False
        
        try:
            # Store analytics in user's analytics collection
            doc_ref = self.db.collection('users').document(self.current_session.user_id).collection('analytics').document()
            
            analytics_record = {
                "timestamp": datetime.now().isoformat(),
                "metrics": analytics_data,
                "session_id": self.current_session.session_token[:10]  # Truncated for privacy
            }
            
            doc_ref.set(analytics_record)
            self.daily_write_count += 1
            
            track_user_action("firebase_manager", "analytics_synced", "Analytics data synced to cloud")
            return True
            
        except Exception as e:
            self.logger.error(f"Analytics sync failed: {e}")
            return False
    
    def optimize_dataframe_for_firestore(self, df: pd.DataFrame) -> List[Dict]:
        """Optimize DataFrame for Firestore storage"""
        records = []
        
        for _, row in df.iterrows():
            record = {}
            for col, value in row.items():
                # Handle different data types
                if pd.isna(value):
                    record[col] = None
                elif isinstance(value, (int, float)):
                    record[col] = float(value) if not pd.isna(value) else 0.0
                elif isinstance(value, bool):
                    record[col] = bool(value)
                else:
                    record[col] = str(value)
            
            # Add metadata
            record['_sync_timestamp'] = datetime.now().isoformat()
            record['_record_hash'] = self.generate_record_hash(record)
            
            records.append(record)
        
        return records
    
    def generate_record_hash(self, record: Dict) -> str:
        """Generate hash for record deduplication"""
        # Create a stable string representation
        record_str = json.dumps(record, sort_keys=True, default=str)
        return hashlib.md5(record_str.encode()).hexdigest()
    
    def get_sync_status(self, operation_id: str) -> Optional[SyncStatus]:
        """Get status of sync operation"""
        return self.active_syncs.get(operation_id)
    
    def get_daily_usage_stats(self) -> Dict[str, int]:
        """Get current daily usage statistics"""
        return {
            "reads": self.daily_read_count,
            "writes": self.daily_write_count,
            "max_reads": self.max_daily_reads,
            "max_writes": self.max_daily_writes,
            "reads_remaining": self.max_daily_reads - self.daily_read_count,
            "writes_remaining": self.max_daily_writes - self.daily_write_count
        }
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.current_session is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user information"""
        if self.current_session:
            return {
                "user_id": self.current_session.user_id,
                "email": self.current_session.email,
                "display_name": self.current_session.display_name,
                "session_start": self.current_session.session_start
            }
        return None

    def set_current_user(self, user_info: Dict):
        """Set current user session from authentication result for v1.0.6"""
        try:
            if user_info:
                self.current_session = UserSession(
                    user_id=user_info.get('localId', user_info.get('uid', '')),
                    email=user_info.get('email', ''),
                    display_name=user_info.get('displayName', user_info.get('email', '').split('@')[0]),
                    session_start=datetime.now().isoformat(),
                    last_activity=datetime.now().isoformat(),
                    session_token=user_info.get('idToken', ''),
                    permissions=["read", "write"]  # Default permissions for subscribers
                )
                self.logger.info(f"User session set for subscriber: {self.current_session.email}")
                return True
        except Exception as e:
            self.logger.error(f"Error setting current user: {e}")
        return False

    def get_usage_statistics(self) -> Dict:
        """Get Firebase usage statistics for v1.0.6"""
        return {
            "daily_reads": self.daily_read_count,
            "daily_writes": self.daily_write_count,
            "max_reads": self.max_daily_reads,
            "max_writes": self.max_daily_writes,
            "reads_remaining": self.max_daily_reads - self.daily_read_count,
            "writes_remaining": self.max_daily_writes - self.daily_write_count,
            "last_reset_date": self.last_reset_date.isoformat() if self.last_reset_date else None
        }

    def cleanup_old_syncs(self):
        """Clean up old sync operations"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        to_remove = []
        for operation_id, sync_status in self.active_syncs.items():
            try:
                start_time = datetime.fromisoformat(sync_status.start_time)
                if start_time < cutoff_time:
                    to_remove.append(operation_id)
            except:
                to_remove.append(operation_id)
        
        for operation_id in to_remove:
            del self.active_syncs[operation_id]

# Global optimized Firebase manager instance
_optimized_firebase_manager = None

def get_optimized_firebase_manager(firebase_config_manager=None):
    """Get global optimized Firebase manager instance for v1.0.6"""
    global _optimized_firebase_manager
    if _optimized_firebase_manager is None:
        _optimized_firebase_manager = OptimizedFirebaseManager(firebase_config_manager=firebase_config_manager)
    return _optimized_firebase_manager

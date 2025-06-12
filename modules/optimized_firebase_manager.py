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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
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
        """Initialize Firebase with error handling"""
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase libraries not available")
            return False
        
        try:
            # Initialize Firebase Admin SDK
            cred_path = "firebase_credentials.json"
            if os.path.exists(cred_path):
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    self.admin_app = firebase_admin.initialize_app(cred)
                else:
                    self.admin_app = firebase_admin.get_app()
                
                self.db = firestore.client()
                self.logger.info("Firebase Admin SDK initialized")
            
            # Initialize Pyrebase for authentication
            web_config_path = "firebase_web_config.json"
            if os.path.exists(web_config_path):
                with open(web_config_path, 'r') as f:
                    config = json.load(f)
                
                self.pyrebase_app = pyrebase.initialize_app(config)
                self.auth_instance = self.pyrebase_app.auth()
                self.logger.info("Pyrebase initialized")
            
            track_system_event("firebase_manager", "firebase_initialized", "Firebase services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Firebase initialization failed: {e}")
            track_system_event("firebase_manager", "firebase_init_failed", f"Firebase initialization failed: {str(e)}")
            return False
    
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

def get_optimized_firebase_manager():
    """Get global optimized Firebase manager instance"""
    global _optimized_firebase_manager
    if _optimized_firebase_manager is None:
        _optimized_firebase_manager = OptimizedFirebaseManager()
    return _optimized_firebase_manager

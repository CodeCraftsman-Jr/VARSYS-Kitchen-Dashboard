"""
Enterprise Features Manager
Multi-user support, security, API integration, and compliance features
"""

import os
import json
import logging
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import pandas as pd
from PySide6.QtCore import QObject, Signal
import jwt

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_system_event, track_performance_start, track_performance_end
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass
    def track_performance_start(*args, **kwargs): pass
    def track_performance_end(*args, **kwargs): pass

class UserRole(Enum):
    """User roles with different permission levels"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

class Permission(Enum):
    """System permissions"""
    READ_ALL = "read_all"
    WRITE_ALL = "write_all"
    DELETE_ALL = "delete_all"
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    MANAGE_INVENTORY = "manage_inventory"
    MANAGE_SALES = "manage_sales"
    MANAGE_BUDGET = "manage_budget"

class AuditAction(Enum):
    """Audit trail actions"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    IMPORT = "import"
    SETTINGS_CHANGE = "settings_change"

class SecurityLevel(Enum):
    """Security levels for data classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class UserManager:
    """Manages user accounts, roles, and permissions"""
    
    def __init__(self, db_path: str = "enterprise.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.secret_key = self.get_or_create_secret_key()
        self.init_database()
        
        # Role permissions mapping
        self.role_permissions = {
            UserRole.SUPER_ADMIN: list(Permission),
            UserRole.ADMIN: [
                Permission.READ_ALL, Permission.WRITE_ALL, Permission.DELETE_ALL,
                Permission.MANAGE_SETTINGS, Permission.VIEW_REPORTS, Permission.EXPORT_DATA,
                Permission.MANAGE_INVENTORY, Permission.MANAGE_SALES, Permission.MANAGE_BUDGET
            ],
            UserRole.MANAGER: [
                Permission.READ_ALL, Permission.WRITE_ALL, Permission.VIEW_REPORTS,
                Permission.EXPORT_DATA, Permission.MANAGE_INVENTORY, Permission.MANAGE_SALES,
                Permission.MANAGE_BUDGET
            ],
            UserRole.STAFF: [
                Permission.READ_ALL, Permission.MANAGE_INVENTORY, Permission.MANAGE_SALES
            ],
            UserRole.VIEWER: [
                Permission.READ_ALL, Permission.VIEW_REPORTS
            ]
        }
        
        self.logger.info("User Manager initialized")
    
    def get_or_create_secret_key(self) -> str:
        """Get or create JWT secret key"""
        key_file = "jwt_secret.key"
        try:
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    return f.read().strip()
            else:
                # Generate new secret key
                secret = secrets.token_urlsafe(32)
                with open(key_file, 'w') as f:
                    f.write(secret)
                return secret
        except Exception as e:
            self.logger.error(f"Error handling secret key: {e}")
            return secrets.token_urlsafe(32)
    
    def init_database(self):
        """Initialize enterprise database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        role TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        last_login TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER,
                        FOREIGN KEY (created_by) REFERENCES users (id)
                    )
                """)
                
                # Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_token TEXT UNIQUE NOT NULL,
                        expires_at TEXT NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Audit trail table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_trail (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT NOT NULL,
                        resource_type TEXT,
                        resource_id TEXT,
                        old_values TEXT,
                        new_values TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # API keys table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key_name TEXT NOT NULL,
                        api_key TEXT UNIQUE NOT NULL,
                        user_id INTEGER NOT NULL,
                        permissions TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        expires_at TEXT,
                        last_used TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                conn.commit()
                
                # Create default admin user if no users exist
                self.create_default_admin()
                
                self.logger.info("Enterprise database initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing enterprise database: {e}")
    
    def create_default_admin(self):
        """Create default admin user if no users exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                if user_count == 0:
                    # Create default admin
                    # Generate secure default password
                    import secrets
                    import string
                    default_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

                    self.create_user(
                        username="admin",
                        email="admin@kitchendashboard.com",
                        password=default_password,
                        role=UserRole.SUPER_ADMIN
                    )

                    # Log the generated password securely (only in debug mode)
                    if os.getenv('DEBUG_MODE') == 'true':
                        self.logger.info(f"Default admin password: {default_password}")
                    else:
                        self.logger.info("Default admin user created with secure password")
                    self.logger.info("Default admin user created")
                    
        except Exception as e:
            self.logger.error(f"Error creating default admin: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return password_hash.hex(), salt
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole, created_by: int = None) -> Optional[int]:
        """Create a new user"""
        try:
            password_hash, salt = self.hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, salt, role, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, email, password_hash, salt, role.value, created_by))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                # Log audit trail
                self.log_audit_action(
                    created_by, AuditAction.CREATE, "user", str(user_id),
                    None, {"username": username, "email": email, "role": role.value}
                )
                
                self.logger.info(f"User created: {username}")
                track_user_action("user_manager", "user_created", f"Created user: {username}")
                
                return user_id
                
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, email, password_hash, salt, role, is_active
                    FROM users
                    WHERE username = ? AND is_active = 1
                """, (username,))
                
                user_data = cursor.fetchone()
                
                if user_data:
                    user_id, username, email, stored_hash, salt, role, is_active = user_data
                    
                    # Verify password
                    password_hash, _ = self.hash_password(password, salt)
                    
                    if password_hash == stored_hash:
                        # Update last login
                        cursor.execute("""
                            UPDATE users SET last_login = ? WHERE id = ?
                        """, (datetime.now().isoformat(), user_id))
                        conn.commit()
                        
                        # Log audit trail
                        self.log_audit_action(user_id, AuditAction.LOGIN, "system", None)
                        
                        user_info = {
                            "id": user_id,
                            "username": username,
                            "email": email,
                            "role": UserRole(role),
                            "permissions": self.role_permissions.get(UserRole(role), [])
                        }
                        
                        track_user_action("user_manager", "user_authenticated", f"User logged in: {username}")
                        return user_info
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            return None
    
    def create_session_token(self, user_id: int, ip_address: str = None, 
                           user_agent: str = None) -> Optional[str]:
        """Create JWT session token"""
        try:
            # Token expires in 24 hours
            expires_at = datetime.now() + timedelta(hours=24)
            
            payload = {
                "user_id": user_id,
                "exp": expires_at.timestamp(),
                "iat": datetime.now().timestamp()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            
            # Store session in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, token, expires_at.isoformat(), ip_address, user_agent))
                
                conn.commit()
            
            return token
            
        except Exception as e:
            self.logger.error(f"Error creating session token: {e}")
            return None
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT session token"""
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload["user_id"]
            
            # Check if session exists and is valid
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT s.expires_at, u.id, u.username, u.email, u.role, u.is_active
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = 1
                """, (token, datetime.now().isoformat()))
                
                session_data = cursor.fetchone()
                
                if session_data:
                    expires_at, user_id, username, email, role, is_active = session_data
                    
                    return {
                        "id": user_id,
                        "username": username,
                        "email": email,
                        "role": UserRole(role),
                        "permissions": self.role_permissions.get(UserRole(role), [])
                    }
                
                return None
                
        except jwt.ExpiredSignatureError:
            self.logger.warning("Session token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid session token")
            return None
        except Exception as e:
            self.logger.error(f"Error validating session token: {e}")
            return None
    
    def log_audit_action(self, user_id: Optional[int], action: AuditAction, 
                        resource_type: str, resource_id: str = None,
                        old_values: Any = None, new_values: Any = None,
                        ip_address: str = None, user_agent: str = None):
        """Log action to audit trail"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_trail (user_id, action, resource_type, resource_id,
                                           old_values, new_values, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, action.value, resource_type, resource_id,
                    json.dumps(old_values) if old_values else None,
                    json.dumps(new_values) if new_values else None,
                    ip_address, user_agent
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error logging audit action: {e}")
    
    def get_audit_trail(self, limit: int = 100, user_id: int = None) -> List[Dict[str, Any]]:
        """Get audit trail records"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT a.id, a.user_id, u.username, a.action, a.resource_type,
                           a.resource_id, a.timestamp, a.ip_address
                    FROM audit_trail a
                    LEFT JOIN users u ON a.user_id = u.id
                """
                params = []
                
                if user_id:
                    query += " WHERE a.user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY a.timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                audit_records = []
                for row in cursor.fetchall():
                    audit_records.append({
                        "id": row[0],
                        "user_id": row[1],
                        "username": row[2] or "System",
                        "action": row[3],
                        "resource_type": row[4],
                        "resource_id": row[5],
                        "timestamp": row[6],
                        "ip_address": row[7]
                    })
                
                return audit_records
                
        except Exception as e:
            self.logger.error(f"Error getting audit trail: {e}")
            return []
    
    def has_permission(self, user: Dict[str, Any], permission: Permission) -> bool:
        """Check if user has specific permission"""
        user_permissions = user.get("permissions", [])
        return permission in user_permissions
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, email, role, is_active, last_login, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "role": row[3],
                        "is_active": bool(row[4]),
                        "last_login": row[5],
                        "created_at": row[6]
                    })
                
                return users
                
        except Exception as e:
            self.logger.error(f"Error getting all users: {e}")
            return []

class APIManager:
    """Manages API keys and external integrations"""
    
    def __init__(self, user_manager: UserManager):
        self.logger = logging.getLogger(__name__)
        self.user_manager = user_manager
        
        self.logger.info("API Manager initialized")
    
    def create_api_key(self, user_id: int, key_name: str, 
                      permissions: List[Permission] = None,
                      expires_days: int = 365) -> Optional[str]:
        """Create new API key"""
        try:
            api_key = f"kd_{secrets.token_urlsafe(32)}"
            expires_at = datetime.now() + timedelta(days=expires_days)
            
            with sqlite3.connect(self.user_manager.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO api_keys (key_name, api_key, user_id, permissions, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    key_name, api_key, user_id,
                    json.dumps([p.value for p in permissions]) if permissions else None,
                    expires_at.isoformat()
                ))
                
                conn.commit()
            
            # Log audit trail
            self.user_manager.log_audit_action(
                user_id, AuditAction.CREATE, "api_key", key_name
            )
            
            track_user_action("api_manager", "api_key_created", f"Created API key: {key_name}")
            return api_key
            
        except Exception as e:
            self.logger.error(f"Error creating API key: {e}")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key"""
        try:
            with sqlite3.connect(self.user_manager.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT k.id, k.key_name, k.user_id, k.permissions, u.username, u.role
                    FROM api_keys k
                    JOIN users u ON k.user_id = u.id
                    WHERE k.api_key = ? AND k.is_active = 1 
                    AND (k.expires_at IS NULL OR k.expires_at > ?)
                """, (api_key, datetime.now().isoformat()))
                
                key_data = cursor.fetchone()
                
                if key_data:
                    # Update last used
                    cursor.execute("""
                        UPDATE api_keys SET last_used = ? WHERE id = ?
                    """, (datetime.now().isoformat(), key_data[0]))
                    conn.commit()
                    
                    permissions = json.loads(key_data[3]) if key_data[3] else []
                    
                    return {
                        "key_id": key_data[0],
                        "key_name": key_data[1],
                        "user_id": key_data[2],
                        "permissions": [Permission(p) for p in permissions],
                        "username": key_data[4],
                        "role": UserRole(key_data[5])
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error validating API key: {e}")
            return None

class ComplianceManager:
    """Manages compliance features and data protection"""
    
    def __init__(self, user_manager: UserManager):
        self.logger = logging.getLogger(__name__)
        self.user_manager = user_manager
        
        # Data retention policies (in days)
        self.retention_policies = {
            "audit_trail": 2555,  # 7 years
            "user_sessions": 30,   # 30 days
            "api_logs": 365,      # 1 year
            "sales_data": 2555,   # 7 years
            "inventory_data": 1095 # 3 years
        }
        
        self.logger.info("Compliance Manager initialized")
    
    def classify_data_sensitivity(self, data_type: str) -> SecurityLevel:
        """Classify data sensitivity level"""
        sensitive_data = {
            "user_credentials": SecurityLevel.RESTRICTED,
            "financial_data": SecurityLevel.CONFIDENTIAL,
            "customer_data": SecurityLevel.CONFIDENTIAL,
            "sales_data": SecurityLevel.INTERNAL,
            "inventory_data": SecurityLevel.INTERNAL,
            "reports": SecurityLevel.INTERNAL,
            "system_logs": SecurityLevel.PUBLIC
        }
        
        return sensitive_data.get(data_type, SecurityLevel.INTERNAL)
    
    def apply_data_retention(self):
        """Apply data retention policies"""
        try:
            with sqlite3.connect(self.user_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean old audit trail records
                cutoff_date = (datetime.now() - timedelta(days=self.retention_policies["audit_trail"])).isoformat()
                cursor.execute("DELETE FROM audit_trail WHERE timestamp < ?", (cutoff_date,))
                
                # Clean old sessions
                cutoff_date = (datetime.now() - timedelta(days=self.retention_policies["user_sessions"])).isoformat()
                cursor.execute("DELETE FROM user_sessions WHERE created_at < ?", (cutoff_date,))
                
                conn.commit()
                
                self.logger.info("Data retention policies applied")
                
        except Exception as e:
            self.logger.error(f"Error applying data retention: {e}")
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            with sqlite3.connect(self.user_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # User statistics
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                active_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
                inactive_users = cursor.fetchone()[0]
                
                # Audit trail statistics
                cursor.execute("SELECT COUNT(*) FROM audit_trail WHERE timestamp > ?", 
                             ((datetime.now() - timedelta(days=30)).isoformat(),))
                recent_audit_records = cursor.fetchone()[0]
                
                # API key statistics
                cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
                active_api_keys = cursor.fetchone()[0]
                
                return {
                    "report_date": datetime.now().isoformat(),
                    "user_statistics": {
                        "active_users": active_users,
                        "inactive_users": inactive_users,
                        "total_users": active_users + inactive_users
                    },
                    "audit_statistics": {
                        "recent_audit_records": recent_audit_records
                    },
                    "api_statistics": {
                        "active_api_keys": active_api_keys
                    },
                    "retention_policies": self.retention_policies,
                    "compliance_status": "compliant"
                }
                
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {e}")
            return {"error": str(e)}

class EnterpriseManager(QObject):
    """
    Main enterprise features manager that coordinates:
    - User management and authentication
    - Role-based access control
    - API key management
    - Audit trails and compliance
    - Security features
    """
    
    user_authenticated = Signal(dict)  # user_info
    user_logged_out = Signal(int)      # user_id
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.user_manager = UserManager()
        self.api_manager = APIManager(self.user_manager)
        self.compliance_manager = ComplianceManager(self.user_manager)
        
        # Current session
        self.current_user = None
        self.current_session_token = None
        
        self.logger.info("Enterprise Manager initialized")
        track_system_event("enterprise_manager", "initialized", "Enterprise features manager started")
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user and create session"""
        user_info = self.user_manager.authenticate_user(username, password)
        
        if user_info:
            # Create session token
            session_token = self.user_manager.create_session_token(user_info["id"])
            
            if session_token:
                self.current_user = user_info
                self.current_session_token = session_token
                self.user_authenticated.emit(user_info)
                return True
        
        return False
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            user_id = self.current_user["id"]
            
            # Log audit trail
            self.user_manager.log_audit_action(user_id, AuditAction.LOGOUT, "system", None)
            
            self.user_logged_out.emit(user_id)
            self.current_user = None
            self.current_session_token = None
            
            track_user_action("enterprise_manager", "user_logged_out", f"User logged out: {user_id}")
    
    def check_permission(self, permission: Permission) -> bool:
        """Check if current user has permission"""
        if not self.current_user:
            return False
        
        return self.user_manager.has_permission(self.current_user, permission)
    
    def get_enterprise_status(self) -> Dict[str, Any]:
        """Get enterprise features status"""
        return {
            "user_authenticated": self.current_user is not None,
            "current_user": self.current_user,
            "total_users": len(self.user_manager.get_all_users()),
            "compliance_status": "active",
            "security_level": "high"
        }

# Global enterprise manager instance
_enterprise_manager = None

def get_enterprise_manager():
    """Get global enterprise manager instance"""
    global _enterprise_manager
    if _enterprise_manager is None:
        _enterprise_manager = EnterpriseManager()
    return _enterprise_manager

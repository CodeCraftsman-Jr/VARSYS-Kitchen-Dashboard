"""
Progressive Web App (PWA) Manager
Offline functionality, service worker management, and app-like experience
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import pandas as pd
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_system_event, track_performance_start, track_performance_end
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass
    def track_performance_start(*args, **kwargs): pass
    def track_performance_end(*args, **kwargs): pass

class ConnectionStatus(Enum):
    """Network connection status"""
    ONLINE = "online"
    OFFLINE = "offline"
    LIMITED = "limited"

class SyncStatus(Enum):
    """Data synchronization status"""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    ERROR = "error"

class OfflineDataManager:
    """Manages offline data storage and synchronization"""
    
    def __init__(self, db_path: str = "offline_data.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize offline database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tables for offline data
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS offline_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        table_name TEXT NOT NULL,
                        record_id TEXT,
                        data TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        sync_status TEXT DEFAULT 'pending',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sync_metadata (
                        table_name TEXT PRIMARY KEY,
                        last_sync TEXT,
                        sync_status TEXT,
                        record_count INTEGER DEFAULT 0
                    )
                """)
                
                conn.commit()
                self.logger.info("Offline database initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing offline database: {e}")
    
    def store_offline_operation(self, table_name: str, operation: str, data: Dict, record_id: str = None):
        """Store an operation for later synchronization"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO offline_data (table_name, record_id, data, operation, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (table_name, record_id, json.dumps(data), operation, datetime.now().isoformat()))
                
                conn.commit()
                self.logger.info(f"Stored offline operation: {operation} on {table_name}")
                
        except Exception as e:
            self.logger.error(f"Error storing offline operation: {e}")
    
    def get_pending_operations(self) -> List[Dict]:
        """Get all pending synchronization operations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, table_name, record_id, data, operation, timestamp
                    FROM offline_data
                    WHERE sync_status = 'pending'
                    ORDER BY timestamp ASC
                """)
                
                operations = []
                for row in cursor.fetchall():
                    operations.append({
                        "id": row[0],
                        "table_name": row[1],
                        "record_id": row[2],
                        "data": json.loads(row[3]),
                        "operation": row[4],
                        "timestamp": row[5]
                    })
                
                return operations
                
        except Exception as e:
            self.logger.error(f"Error getting pending operations: {e}")
            return []
    
    def mark_operation_synced(self, operation_id: int):
        """Mark an operation as successfully synced"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE offline_data
                    SET sync_status = 'synced'
                    WHERE id = ?
                """, (operation_id,))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error marking operation as synced: {e}")
    
    def get_offline_stats(self) -> Dict[str, int]:
        """Get offline data statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM offline_data WHERE sync_status = 'pending'")
                pending_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM offline_data WHERE sync_status = 'synced'")
                synced_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM offline_data WHERE sync_status = 'error'")
                error_count = cursor.fetchone()[0]
                
                return {
                    "pending": pending_count,
                    "synced": synced_count,
                    "errors": error_count,
                    "total": pending_count + synced_count + error_count
                }
                
        except Exception as e:
            self.logger.error(f"Error getting offline stats: {e}")
            return {"pending": 0, "synced": 0, "errors": 0, "total": 0}

class PWAManager(QObject):
    """
    Progressive Web App manager that provides:
    - Offline functionality
    - Background sync
    - App-like experience
    - Installation prompts
    - Push notifications
    """
    
    # Signals
    connection_status_changed = Signal(ConnectionStatus)
    sync_progress = Signal(int, str)  # progress, status
    offline_data_available = Signal(int)  # count of pending operations
    
    def __init__(self, data: Dict[str, pd.DataFrame], parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data = data
        
        # Connection status
        self.connection_status = ConnectionStatus.ONLINE
        self.last_online_time = datetime.now()
        
        # Offline data manager
        self.offline_manager = OfflineDataManager()
        
        # Sync settings
        self.auto_sync_enabled = True
        self.sync_interval = 30  # seconds
        self.max_offline_operations = 1000
        
        # Setup timers
        self.connection_check_timer = QTimer()
        self.connection_check_timer.timeout.connect(self.check_connection_status)
        self.connection_check_timer.start(5000)  # Check every 5 seconds
        
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_offline_data)
        self.sync_timer.start(self.sync_interval * 1000)
        
        # Initialize
        self.check_connection_status()
        self.create_pwa_manifest()
        
        self.logger.info("PWA Manager initialized")
        track_system_event("pwa_manager", "initialized", "Progressive Web App manager started")
    
    def check_connection_status(self):
        """Check current connection status"""
        try:
            # Simple connection check - in a real app, you might ping a server
            # For now, we'll simulate connection status
            import socket
            
            # Try to connect to a reliable server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            new_status = ConnectionStatus.ONLINE
            
        except (socket.error, OSError):
            new_status = ConnectionStatus.OFFLINE
        
        if new_status != self.connection_status:
            old_status = self.connection_status
            self.connection_status = new_status
            
            if new_status == ConnectionStatus.ONLINE:
                self.last_online_time = datetime.now()
                self.logger.info("Connection restored - going online")
                track_system_event("pwa_manager", "connection_restored", "Internet connection restored")
                
                # Trigger sync when coming back online
                if old_status == ConnectionStatus.OFFLINE:
                    self.sync_offline_data()
            else:
                self.logger.info("Connection lost - going offline")
                track_system_event("pwa_manager", "connection_lost", "Internet connection lost")
            
            self.connection_status_changed.emit(new_status)
    
    def is_online(self) -> bool:
        """Check if currently online"""
        return self.connection_status == ConnectionStatus.ONLINE
    
    def store_operation_offline(self, table_name: str, operation: str, data: Dict, record_id: str = None):
        """Store an operation for offline execution"""
        if not self.is_online():
            self.offline_manager.store_offline_operation(table_name, operation, data, record_id)
            
            # Emit signal about pending operations
            stats = self.offline_manager.get_offline_stats()
            self.offline_data_available.emit(stats["pending"])
            
            track_user_action("pwa_manager", "operation_stored_offline", f"Stored {operation} operation for {table_name}")
    
    def sync_offline_data(self):
        """Synchronize offline data when connection is available"""
        if not self.is_online():
            return
        
        operation_id = f"offline_sync_{datetime.now().timestamp()}"
        track_performance_start(operation_id, "pwa_manager", "sync_offline_data")
        
        try:
            pending_operations = self.offline_manager.get_pending_operations()
            
            if not pending_operations:
                return
            
            self.logger.info(f"Syncing {len(pending_operations)} offline operations")
            self.sync_progress.emit(0, f"Syncing {len(pending_operations)} operations...")
            
            synced_count = 0
            for i, operation in enumerate(pending_operations):
                try:
                    # Apply the operation to the main data
                    success = self.apply_offline_operation(operation)
                    
                    if success:
                        self.offline_manager.mark_operation_synced(operation["id"])
                        synced_count += 1
                    
                    # Update progress
                    progress = int(((i + 1) / len(pending_operations)) * 100)
                    self.sync_progress.emit(progress, f"Synced {synced_count}/{len(pending_operations)} operations")
                    
                except Exception as e:
                    self.logger.error(f"Error syncing operation {operation['id']}: {e}")
            
            self.sync_progress.emit(100, f"Sync complete: {synced_count} operations synced")
            
            # Update offline data count
            stats = self.offline_manager.get_offline_stats()
            self.offline_data_available.emit(stats["pending"])
            
            track_performance_end(operation_id, "pwa_manager", "sync_offline_data",
                                metadata={"operations_synced": synced_count})
            
        except Exception as e:
            self.logger.error(f"Error during offline sync: {e}")
            self.sync_progress.emit(0, f"Sync failed: {str(e)}")
            track_performance_end(operation_id, "pwa_manager", "sync_offline_data",
                                metadata={"error": str(e)})
    
    def apply_offline_operation(self, operation: Dict) -> bool:
        """Apply an offline operation to the main data"""
        try:
            table_name = operation["table_name"]
            op_type = operation["operation"]
            data = operation["data"]
            
            if table_name not in self.data:
                self.logger.warning(f"Table {table_name} not found in data")
                return False
            
            df = self.data[table_name]
            
            if op_type == "insert":
                # Add new row
                new_row = pd.DataFrame([data])
                self.data[table_name] = pd.concat([df, new_row], ignore_index=True)
                
            elif op_type == "update":
                # Update existing row
                record_id = operation.get("record_id")
                if record_id and "id" in df.columns:
                    mask = df["id"] == record_id
                    for key, value in data.items():
                        if key in df.columns:
                            df.loc[mask, key] = value
                
            elif op_type == "delete":
                # Delete row
                record_id = operation.get("record_id")
                if record_id and "id" in df.columns:
                    self.data[table_name] = df[df["id"] != record_id]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying offline operation: {e}")
            return False
    
    def create_pwa_manifest(self):
        """Create PWA manifest file"""
        try:
            manifest = {
                "name": "Kitchen Dashboard",
                "short_name": "KitchenApp",
                "description": "Professional Kitchen Management Dashboard",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#3b82f6",
                "orientation": "portrait-primary",
                "icons": [
                    {
                        "src": "icon-192.png",
                        "sizes": "192x192",
                        "type": "image/png"
                    },
                    {
                        "src": "icon-512.png",
                        "sizes": "512x512",
                        "type": "image/png"
                    }
                ],
                "categories": ["business", "productivity", "food"],
                "lang": "en",
                "scope": "/",
                "prefer_related_applications": False
            }
            
            # Save manifest file
            with open("manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info("PWA manifest created")
            
        except Exception as e:
            self.logger.error(f"Error creating PWA manifest: {e}")
    
    def get_offline_stats(self) -> Dict[str, Any]:
        """Get offline functionality statistics"""
        stats = self.offline_manager.get_offline_stats()
        
        return {
            "connection_status": self.connection_status.value,
            "last_online": self.last_online_time.isoformat(),
            "offline_operations": stats,
            "auto_sync_enabled": self.auto_sync_enabled,
            "sync_interval": self.sync_interval,
            "time_offline": (datetime.now() - self.last_online_time).total_seconds() if self.connection_status == ConnectionStatus.OFFLINE else 0
        }
    
    def enable_offline_mode(self):
        """Enable offline mode features"""
        self.auto_sync_enabled = True
        self.logger.info("Offline mode enabled")
        track_user_action("pwa_manager", "offline_mode_enabled", "Offline functionality enabled")
    
    def disable_offline_mode(self):
        """Disable offline mode features"""
        self.auto_sync_enabled = False
        self.logger.info("Offline mode disabled")
        track_user_action("pwa_manager", "offline_mode_disabled", "Offline functionality disabled")

class PWAStatusWidget(QWidget):
    """Widget to display PWA status and controls"""
    
    def __init__(self, pwa_manager: PWAManager, parent=None):
        super().__init__(parent)
        self.pwa_manager = pwa_manager
        self.init_ui()
        
        # Connect signals
        self.pwa_manager.connection_status_changed.connect(self.update_connection_status)
        self.pwa_manager.sync_progress.connect(self.update_sync_progress)
        self.pwa_manager.offline_data_available.connect(self.update_offline_count)
        
        # Initial update
        self.update_connection_status(self.pwa_manager.connection_status)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Connection status
        self.connection_label = QLabel("🔄 Checking connection...")
        self.connection_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        layout.addWidget(self.connection_label)
        
        # Offline operations count
        self.offline_count_label = QLabel("📱 No offline operations")
        self.offline_count_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        layout.addWidget(self.offline_count_label)
        
        # Sync progress
        self.sync_progress_bar = QProgressBar()
        self.sync_progress_bar.setVisible(False)
        self.sync_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.sync_progress_bar)
        
        self.sync_status_label = QLabel("")
        self.sync_status_label.setStyleSheet("font-size: 11px; color: #9ca3af;")
        layout.addWidget(self.sync_status_label)
        
        # Manual sync button
        self.sync_button = QPushButton("🔄 Sync Now")
        self.sync_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.sync_button.clicked.connect(self.manual_sync)
        layout.addWidget(self.sync_button)
    
    def update_connection_status(self, status: ConnectionStatus):
        """Update connection status display"""
        if status == ConnectionStatus.ONLINE:
            self.connection_label.setText("🟢 Online")
            self.connection_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #10b981;")
            self.sync_button.setEnabled(True)
        elif status == ConnectionStatus.OFFLINE:
            self.connection_label.setText("🔴 Offline")
            self.connection_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #ef4444;")
            self.sync_button.setEnabled(False)
        else:
            self.connection_label.setText("🟡 Limited Connection")
            self.connection_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #f59e0b;")
            self.sync_button.setEnabled(True)
    
    def update_sync_progress(self, progress: int, status: str):
        """Update sync progress display"""
        if progress > 0:
            self.sync_progress_bar.setVisible(True)
            self.sync_progress_bar.setValue(progress)
            self.sync_status_label.setText(status)
        else:
            self.sync_progress_bar.setVisible(False)
            self.sync_status_label.setText("")
    
    def update_offline_count(self, count: int):
        """Update offline operations count"""
        if count > 0:
            self.offline_count_label.setText(f"📱 {count} operations pending sync")
            self.offline_count_label.setStyleSheet("font-size: 12px; color: #f59e0b; font-weight: 500;")
        else:
            self.offline_count_label.setText("📱 All data synced")
            self.offline_count_label.setStyleSheet("font-size: 12px; color: #10b981;")
    
    def manual_sync(self):
        """Trigger manual sync"""
        if self.pwa_manager.is_online():
            self.pwa_manager.sync_offline_data()
        else:
            QMessageBox.warning(self, "Sync Failed", "Cannot sync while offline. Please check your internet connection.")

# Global PWA manager instance
_pwa_manager = None

def get_pwa_manager(data: Dict[str, pd.DataFrame] = None):
    """Get global PWA manager instance"""
    global _pwa_manager
    if _pwa_manager is None and data is not None:
        _pwa_manager = PWAManager(data)
    return _pwa_manager

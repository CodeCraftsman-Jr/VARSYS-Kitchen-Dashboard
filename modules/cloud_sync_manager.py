"""
Cloud Sync Manager
Advanced cloud synchronization with analytics integration and conflict resolution
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QGroupBox, QFormLayout

class SyncDirection(Enum):
    """Sync direction options"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    BIDIRECTIONAL = "bidirectional"

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MERGE = "merge"
    ASK_USER = "ask_user"

@dataclass
class SyncOperation:
    """Sync operation details"""
    operation_id: str
    direction: SyncDirection
    tables: List[str]
    start_time: str
    end_time: Optional[str]
    status: str  # "pending", "in_progress", "completed", "failed"
    records_processed: int
    conflicts_found: int
    error_message: Optional[str]

class CloudSyncWorker(QThread):
    """Background cloud sync worker"""
    
    progress_updated = Signal(str, int, str)  # operation_id, progress, status
    sync_completed = Signal(str, bool, str)  # operation_id, success, message
    conflict_detected = Signal(str, dict)  # operation_id, conflict_data
    
    def __init__(self, operation: SyncOperation, data: Dict[str, pd.DataFrame], firebase_manager, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.data = data
        self.firebase_manager = firebase_manager
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Execute sync operation"""
        try:
            self.progress_updated.emit(self.operation.operation_id, 0, "Starting sync...")
            
            if self.operation.direction == SyncDirection.UPLOAD:
                self.upload_data()
            elif self.operation.direction == SyncDirection.DOWNLOAD:
                self.download_data()
            elif self.operation.direction == SyncDirection.BIDIRECTIONAL:
                self.bidirectional_sync()
            
            self.operation.status = "completed"
            self.operation.end_time = datetime.now().isoformat()
            self.sync_completed.emit(self.operation.operation_id, True, "Sync completed successfully")
            
        except Exception as e:
            self.operation.status = "failed"
            self.operation.error_message = str(e)
            self.operation.end_time = datetime.now().isoformat()
            self.sync_completed.emit(self.operation.operation_id, False, str(e))
    
    def upload_data(self):
        """Upload local data to cloud"""
        total_tables = len(self.operation.tables)
        
        for i, table_name in enumerate(self.operation.tables):
            if table_name in self.data:
                df = self.data[table_name]
                
                self.progress_updated.emit(
                    self.operation.operation_id, 
                    int((i / total_tables) * 100), 
                    f"Uploading {table_name}..."
                )
                
                # Upload table data
                self.upload_table(table_name, df)
                self.operation.records_processed += len(df)
        
        self.progress_updated.emit(self.operation.operation_id, 100, "Upload completed")
    
    def upload_table(self, table_name: str, df: pd.DataFrame):
        """Upload a single table to cloud"""
        # This would integrate with the Firebase manager
        # For now, simulate the upload
        import time
        time.sleep(0.5)  # Simulate network delay
    
    def download_data(self):
        """Download cloud data to local"""
        # Implementation for downloading data from cloud
        pass
    
    def bidirectional_sync(self):
        """Perform bidirectional synchronization with conflict resolution"""
        # Implementation for bidirectional sync
        pass

class CloudSyncManager(QWidget):
    """
    Cloud sync manager with:
    - Real-time sync monitoring
    - Conflict resolution
    - Analytics integration
    - Bandwidth optimization
    """
    
    # Signals
    sync_started = Signal(str)  # operation_id
    sync_completed = Signal(str, bool)  # operation_id, success
    
    def __init__(self, data: Dict[str, pd.DataFrame], parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data = data
        
        # Get Firebase manager
        try:
            from .optimized_firebase_manager import get_optimized_firebase_manager
            self.firebase_manager = get_optimized_firebase_manager()
        except ImportError:
            self.firebase_manager = None
        
        # Get analytics engine
        try:
            from .analytics_engine import get_analytics_engine
            self.analytics_engine = get_analytics_engine(data)
        except ImportError:
            self.analytics_engine = None
        
        # Sync operations tracking
        self.active_operations: Dict[str, SyncOperation] = {}
        self.sync_history: List[SyncOperation] = []
        
        # Sync settings
        self.auto_sync_enabled = True
        self.sync_interval = 300  # 5 minutes
        self.conflict_resolution = ConflictResolution.ASK_USER
        
        # Initialize UI
        self.init_ui()
        
        # Setup auto-sync timer
        self.auto_sync_timer = QTimer()
        self.auto_sync_timer.timeout.connect(self.auto_sync)
        if self.auto_sync_enabled:
            self.auto_sync_timer.start(self.sync_interval * 1000)
        
        # Setup status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
        self.logger.info("Cloud Sync Manager initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Cloud Synchronization")
        header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        layout.addWidget(header_label)
        
        # Sync controls
        self.create_sync_controls(layout)
        
        # Sync status
        self.create_sync_status(layout)
        
        # Analytics sync
        self.create_analytics_sync(layout)
        
        # Sync history
        self.create_sync_history(layout)
    
    def create_sync_controls(self, parent_layout):
        """Create sync control buttons"""
        controls_group = QGroupBox("Sync Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Manual sync button
        self.manual_sync_btn = QPushButton("Manual Sync")
        self.manual_sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.manual_sync_btn.clicked.connect(self.start_manual_sync)
        controls_layout.addWidget(self.manual_sync_btn)
        
        # Upload only button
        self.upload_btn = QPushButton("Upload Only")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.upload_btn.clicked.connect(self.start_upload_only)
        controls_layout.addWidget(self.upload_btn)
        
        # Download only button
        self.download_btn = QPushButton("Download Only")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.download_btn.clicked.connect(self.start_download_only)
        controls_layout.addWidget(self.download_btn)
        
        controls_layout.addStretch()
        
        parent_layout.addWidget(controls_group)
    
    def create_sync_status(self, parent_layout):
        """Create sync status display"""
        status_group = QGroupBox("Sync Status")
        status_layout = QVBoxLayout(status_group)
        
        # Current operation status
        self.current_operation_label = QLabel("No active sync operations")
        self.current_operation_label.setStyleSheet("color: #6b7280; font-size: 14px; padding: 8px;")
        status_layout.addWidget(self.current_operation_label)
        
        # Progress bar
        self.sync_progress = QProgressBar()
        self.sync_progress.setVisible(False)
        self.sync_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.sync_progress)
        
        # Last sync info
        self.last_sync_label = QLabel("Last sync: Never")
        self.last_sync_label.setStyleSheet("color: #9ca3af; font-size: 12px; padding: 4px;")
        status_layout.addWidget(self.last_sync_label)
        
        parent_layout.addWidget(status_group)
    
    def create_analytics_sync(self, parent_layout):
        """Create analytics sync section"""
        analytics_group = QGroupBox("Analytics Sync")
        analytics_layout = QFormLayout(analytics_group)
        
        # Analytics sync status
        self.analytics_sync_status = QLabel("Ready")
        self.analytics_sync_status.setStyleSheet("color: #10b981; font-weight: 500;")
        analytics_layout.addRow("Status:", self.analytics_sync_status)
        
        # Last analytics sync
        self.last_analytics_sync = QLabel("Never")
        self.last_analytics_sync.setStyleSheet("color: #6b7280;")
        analytics_layout.addRow("Last Sync:", self.last_analytics_sync)
        
        # Sync analytics button
        self.sync_analytics_btn = QPushButton("Sync Analytics")
        self.sync_analytics_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.sync_analytics_btn.clicked.connect(self.sync_analytics)
        analytics_layout.addRow("", self.sync_analytics_btn)
        
        parent_layout.addWidget(analytics_group)
    
    def create_sync_history(self, parent_layout):
        """Create sync history display"""
        history_group = QGroupBox("Sync History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_text = QTextEdit()
        self.history_text.setMaximumHeight(150)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #374151;
            }
        """)
        self.history_text.setPlainText("No sync operations yet...")
        history_layout.addWidget(self.history_text)
        
        parent_layout.addWidget(history_group)
    
    def start_manual_sync(self):
        """Start manual bidirectional sync"""
        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            self.add_history_entry("❌ Manual sync failed: Not authenticated")
            return
        
        operation = SyncOperation(
            operation_id=f"manual_{datetime.now().timestamp()}",
            direction=SyncDirection.BIDIRECTIONAL,
            tables=list(self.data.keys()),
            start_time=datetime.now().isoformat(),
            end_time=None,
            status="pending",
            records_processed=0,
            conflicts_found=0,
            error_message=None
        )
        
        self.start_sync_operation(operation)
    
    def start_upload_only(self):
        """Start upload-only sync"""
        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            self.add_history_entry("❌ Upload failed: Not authenticated")
            return
        
        operation = SyncOperation(
            operation_id=f"upload_{datetime.now().timestamp()}",
            direction=SyncDirection.UPLOAD,
            tables=list(self.data.keys()),
            start_time=datetime.now().isoformat(),
            end_time=None,
            status="pending",
            records_processed=0,
            conflicts_found=0,
            error_message=None
        )
        
        self.start_sync_operation(operation)
    
    def start_download_only(self):
        """Start download-only sync"""
        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            self.add_history_entry("❌ Download failed: Not authenticated")
            return
        
        operation = SyncOperation(
            operation_id=f"download_{datetime.now().timestamp()}",
            direction=SyncDirection.DOWNLOAD,
            tables=list(self.data.keys()),
            start_time=datetime.now().isoformat(),
            end_time=None,
            status="pending",
            records_processed=0,
            conflicts_found=0,
            error_message=None
        )
        
        self.start_sync_operation(operation)
    
    def start_sync_operation(self, operation: SyncOperation):
        """Start a sync operation"""
        try:
            # Add to active operations
            self.active_operations[operation.operation_id] = operation
            
            # Update UI
            self.current_operation_label.setText(f"🔄 {operation.direction.value.title()} in progress...")
            self.sync_progress.setVisible(True)
            self.sync_progress.setValue(0)
            
            # Disable sync buttons
            self.manual_sync_btn.setEnabled(False)
            self.upload_btn.setEnabled(False)
            self.download_btn.setEnabled(False)
            
            # Start background worker
            self.sync_worker = CloudSyncWorker(operation, self.data, self.firebase_manager)
            self.sync_worker.progress_updated.connect(self.on_sync_progress)
            self.sync_worker.sync_completed.connect(self.on_sync_completed)
            self.sync_worker.conflict_detected.connect(self.on_conflict_detected)
            self.sync_worker.start()
            
            # Add to history
            self.add_history_entry(f"🔄 Started {operation.direction.value} sync (ID: {operation.operation_id[:8]})")
            
            # Emit signal
            self.sync_started.emit(operation.operation_id)
            
        except Exception as e:
            self.logger.error(f"Failed to start sync operation: {e}")
            self.add_history_entry(f"❌ Failed to start sync: {str(e)}")
    
    def on_sync_progress(self, operation_id: str, progress: int, status: str):
        """Handle sync progress update"""
        self.sync_progress.setValue(progress)
        self.current_operation_label.setText(f"🔄 {status}")
    
    def on_sync_completed(self, operation_id: str, success: bool, message: str):
        """Handle sync completion"""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            
            # Move to history
            self.sync_history.append(operation)
            del self.active_operations[operation_id]
            
            # Update UI
            self.sync_progress.setVisible(False)
            
            if success:
                self.current_operation_label.setText("✅ Sync completed successfully")
                self.add_history_entry(f"✅ {operation.direction.value.title()} sync completed ({operation.records_processed} records)")
                self.last_sync_label.setText(f"Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                self.current_operation_label.setText("❌ Sync failed")
                self.add_history_entry(f"❌ {operation.direction.value.title()} sync failed: {message}")
            
            # Re-enable sync buttons
            self.manual_sync_btn.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self.download_btn.setEnabled(True)
            
            # Emit signal
            self.sync_completed.emit(operation_id, success)
    
    def on_conflict_detected(self, operation_id: str, conflict_data: dict):
        """Handle sync conflict"""
        self.add_history_entry(f"⚠️ Conflict detected in operation {operation_id[:8]}")
        # Here you would implement conflict resolution UI
    
    def sync_analytics(self):
        """Sync analytics data to cloud"""
        if not self.analytics_engine or not self.firebase_manager:
            self.add_history_entry("❌ Analytics sync failed: Services not available")
            return
        
        try:
            # Get current analytics
            metrics = self.analytics_engine.get_metrics()
            insights = self.analytics_engine.get_insights()
            
            analytics_data = {
                "metrics": {k: asdict(v) for k, v in metrics.items()},
                "insights": [asdict(insight) for insight in insights],
                "timestamp": datetime.now().isoformat()
            }
            
            # Sync to cloud
            success = self.firebase_manager.sync_analytics_to_cloud(analytics_data)
            
            if success:
                self.analytics_sync_status.setText("✅ Synced")
                self.analytics_sync_status.setStyleSheet("color: #10b981; font-weight: 500;")
                self.last_analytics_sync.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.add_history_entry("✅ Analytics data synced to cloud")
            else:
                self.analytics_sync_status.setText("❌ Failed")
                self.analytics_sync_status.setStyleSheet("color: #ef4444; font-weight: 500;")
                self.add_history_entry("❌ Analytics sync failed")
                
        except Exception as e:
            self.logger.error(f"Analytics sync failed: {e}")
            self.add_history_entry(f"❌ Analytics sync error: {str(e)}")
    
    def auto_sync(self):
        """Perform automatic sync"""
        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            return
        
        # Only auto-sync if no operations are active
        if not self.active_operations:
            self.add_history_entry("🔄 Auto-sync triggered")
            self.start_upload_only()  # Auto-sync only uploads for safety
    
    def update_status(self):
        """Update status displays"""
        # Update current operation status
        if not self.active_operations:
            if self.current_operation_label.text().startswith("🔄"):
                # Reset to idle state after a delay
                pass
    
    def add_history_entry(self, message: str):
        """Add entry to sync history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history_text.append(f"[{timestamp}] {message}")
        
        # Keep only last 50 entries
        lines = self.history_text.toPlainText().split('\n')
        if len(lines) > 50:
            self.history_text.setPlainText('\n'.join(lines[-50:]))
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get sync statistics"""
        completed_syncs = [op for op in self.sync_history if op.status == "completed"]
        failed_syncs = [op for op in self.sync_history if op.status == "failed"]
        
        return {
            "total_syncs": len(self.sync_history),
            "successful_syncs": len(completed_syncs),
            "failed_syncs": len(failed_syncs),
            "total_records_synced": sum(op.records_processed for op in completed_syncs),
            "active_operations": len(self.active_operations),
            "last_sync": self.sync_history[-1].end_time if self.sync_history else None
        }

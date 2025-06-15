"""
Intelligent Cloud Synchronization Manager for Kitchen Dashboard
Provides efficient, incremental sync with Firebase free tier optimization
"""

import os
import json
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal, QThread, QTimer
from PySide6.QtWidgets import QApplication
import logging

@dataclass
class SyncMetadata:
    """Metadata for tracking sync state"""
    last_sync_timestamp: str
    data_checksum: str
    record_count: int
    file_size: int
    sync_direction: str  # 'upload', 'download', 'bidirectional'
    
@dataclass
class ChangeDetectionResult:
    """Result of change detection"""
    has_local_changes: bool
    has_remote_changes: bool
    local_modified_time: Optional[str]
    remote_modified_time: Optional[str]
    change_summary: str

@dataclass
class SyncOperation:
    """Represents a sync operation"""
    operation_id: str
    operation_type: str  # 'upload', 'download', 'check_changes'
    data_types: List[str]
    start_time: str
    end_time: Optional[str] = None
    status: str = 'pending'  # 'pending', 'running', 'completed', 'failed'
    progress: int = 0
    current_step: str = ''
    total_operations: int = 0
    completed_operations: int = 0
    error_message: Optional[str] = None

class IntelligentSyncManager(QObject):
    """Intelligent synchronization manager with change detection and Firebase optimization"""
    
    # Signals
    sync_started = Signal(str)  # operation_id
    sync_progress = Signal(str, int, str)  # operation_id, progress, status
    sync_completed = Signal(str, bool, str)  # operation_id, success, message
    changes_detected = Signal(str, dict)  # data_type, change_info
    daily_limit_warning = Signal(str, int, int)  # operation_type, current_count, limit
    
    def __init__(self, firebase_manager=None, data_directory="data"):
        super().__init__()
        self.firebase_manager = firebase_manager
        self.data_directory = data_directory
        self.logger = logging.getLogger(__name__)
        
        # Sync metadata storage
        self.metadata_file = os.path.join(data_directory, ".sync_metadata.json")
        self.sync_metadata: Dict[str, SyncMetadata] = {}
        
        # Operation tracking
        self.active_operations: Dict[str, SyncOperation] = {}
        self.operation_history: List[SyncOperation] = []
        
        # Firebase free tier limits
        self.daily_read_limit = 50000
        self.daily_write_limit = 20000
        self.operation_counts = {'reads': 0, 'writes': 0}
        self.last_reset_date = datetime.now().date()
        
        # Load existing metadata
        self.load_sync_metadata()
        
        # Setup periodic change detection
        self.change_detection_timer = QTimer()
        self.change_detection_timer.timeout.connect(self.check_for_remote_changes)
        self.change_detection_timer.start(300000)  # Check every 5 minutes
        
    def load_sync_metadata(self):
        """Load sync metadata from file"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.sync_metadata = {
                        k: SyncMetadata(**v) for k, v in data.get('metadata', {}).items()
                    }
                    self.operation_counts = data.get('operation_counts', {'reads': 0, 'writes': 0})
                    last_reset = data.get('last_reset_date')
                    if last_reset:
                        self.last_reset_date = datetime.fromisoformat(last_reset).date()
                        
                self.logger.info(f"Loaded sync metadata for {len(self.sync_metadata)} data types")
            else:
                self.logger.info("No existing sync metadata found")
                
        except Exception as e:
            self.logger.error(f"Error loading sync metadata: {e}")
            self.sync_metadata = {}
    
    def save_sync_metadata(self):
        """Save sync metadata to file"""
        try:
            os.makedirs(self.data_directory, exist_ok=True)
            
            data = {
                'metadata': {k: asdict(v) for k, v in self.sync_metadata.items()},
                'operation_counts': self.operation_counts,
                'last_reset_date': self.last_reset_date.isoformat()
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving sync metadata: {e}")
    
    def reset_daily_counts_if_needed(self):
        """Reset daily operation counts if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.operation_counts = {'reads': 0, 'writes': 0}
            self.last_reset_date = current_date
            self.save_sync_metadata()
            self.logger.info("Daily operation counts reset")
    
    def check_daily_limits(self, operation_type: str, required_operations: int = 1) -> bool:
        """Check if operation would exceed daily limits"""
        self.reset_daily_counts_if_needed()
        
        if operation_type == 'read':
            remaining = self.daily_read_limit - self.operation_counts['reads']
            if required_operations > remaining:
                self.daily_limit_warning.emit('read', self.operation_counts['reads'], self.daily_read_limit)
                return False
        elif operation_type == 'write':
            remaining = self.daily_write_limit - self.operation_counts['writes']
            if required_operations > remaining:
                self.daily_limit_warning.emit('write', self.operation_counts['writes'], self.daily_write_limit)
                return False
        
        return True
    
    def increment_operation_count(self, operation_type: str, count: int = 1):
        """Increment operation count and save metadata"""
        self.operation_counts[operation_type + 's'] += count
        self.save_sync_metadata()
    
    def calculate_data_checksum(self, data: pd.DataFrame) -> str:
        """Calculate checksum for data to detect changes"""
        try:
            # Convert DataFrame to string and calculate hash
            data_string = data.to_csv(index=False)
            return hashlib.md5(data_string.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def get_local_file_info(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Get local file information for change detection"""
        try:
            file_path = os.path.join(self.data_directory, f"{data_type}.csv")
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Read data and calculate checksum
            df = pd.read_csv(file_path)
            checksum = self.calculate_data_checksum(df)
            
            return {
                'modified_time': modified_time.isoformat(),
                'checksum': checksum,
                'record_count': len(df),
                'file_size': stat.st_size
            }
            
        except Exception as e:
            self.logger.error(f"Error getting local file info for {data_type}: {e}")
            return None
    
    def detect_local_changes(self, data_type: str) -> bool:
        """Detect if local data has changed since last sync"""
        try:
            current_info = self.get_local_file_info(data_type)
            if not current_info:
                return False
            
            # Check against stored metadata
            if data_type not in self.sync_metadata:
                return True  # No previous sync, consider as changed
            
            stored_metadata = self.sync_metadata[data_type]
            
            # Compare checksums
            if current_info['checksum'] != stored_metadata.data_checksum:
                self.logger.info(f"Local changes detected for {data_type} (checksum mismatch)")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting local changes for {data_type}: {e}")
            return False
    
    def detect_remote_changes(self, data_type: str) -> Tuple[bool, Optional[str]]:
        """Detect if remote data has changed since last sync"""
        try:
            if not self.firebase_manager or not self.firebase_manager.is_authenticated():
                return False, "Firebase not available"
            
            # Check if we can perform read operations
            if not self.check_daily_limits('read', 1):
                return False, "Daily read limit reached"
            
            # Get remote metadata (this would be a Firebase read operation)
            # Implementation depends on your Firebase structure
            # For now, return False to avoid Firebase calls during development
            
            self.increment_operation_count('read', 1)
            return False, None
            
        except Exception as e:
            self.logger.error(f"Error detecting remote changes for {data_type}: {e}")
            return False, str(e)
    
    def check_for_remote_changes(self):
        """Periodic check for remote changes"""
        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            return
        
        # Check for changes in all known data types
        for data_type in self.sync_metadata.keys():
            has_changes, error = self.detect_remote_changes(data_type)
            if has_changes:
                change_info = {
                    'data_type': data_type,
                    'has_remote_changes': True,
                    'detected_at': datetime.now().isoformat()
                }
                self.changes_detected.emit(data_type, change_info)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and statistics"""
        self.reset_daily_counts_if_needed()
        
        return {
            'firebase_available': self.firebase_manager is not None,
            'authenticated': self.firebase_manager.is_authenticated() if self.firebase_manager else False,
            'active_operations': len(self.active_operations),
            'daily_reads': self.operation_counts['reads'],
            'daily_writes': self.operation_counts['writes'],
            'read_limit': self.daily_read_limit,
            'write_limit': self.daily_write_limit,
            'last_sync_times': {
                data_type: metadata.last_sync_timestamp
                for data_type, metadata in self.sync_metadata.items()
            },
            'data_types_tracked': list(self.sync_metadata.keys())
        }

    def start_upload_sync(self, data_types: List[str] = None) -> str:
        """Start upload sync operation"""
        operation_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            self.logger.error("Firebase not available or not authenticated")
            return None

        # Determine data types to sync
        if data_types is None:
            data_types = self._get_available_data_types()

        # Filter to only data types with local changes
        changed_data_types = [dt for dt in data_types if self.detect_local_changes(dt)]

        if not changed_data_types:
            self.logger.info("No local changes detected, skipping upload sync")
            return None

        # Create operation
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type='upload',
            data_types=changed_data_types,
            start_time=datetime.now().isoformat(),
            total_operations=len(changed_data_types)
        )

        self.active_operations[operation_id] = operation
        self.sync_started.emit(operation_id)

        # Start sync worker
        worker = SyncWorker(operation, self)
        worker.progress_updated.connect(self._on_sync_progress)
        worker.sync_completed.connect(self._on_sync_completed)
        worker.start()

        return operation_id

    def start_download_sync(self, data_types: List[str] = None) -> str:
        """Start download sync operation"""
        operation_id = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if not self.firebase_manager or not self.firebase_manager.is_authenticated():
            self.logger.error("Firebase not available or not authenticated")
            return None

        # Determine data types to sync
        if data_types is None:
            data_types = list(self.sync_metadata.keys())

        # Create operation
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type='download',
            data_types=data_types,
            start_time=datetime.now().isoformat(),
            total_operations=len(data_types)
        )

        self.active_operations[operation_id] = operation
        self.sync_started.emit(operation_id)

        # Start sync worker
        worker = SyncWorker(operation, self)
        worker.progress_updated.connect(self._on_sync_progress)
        worker.sync_completed.connect(self._on_sync_completed)
        worker.start()

        return operation_id

    def check_for_changes(self, data_types: List[str] = None) -> str:
        """Check for changes without syncing"""
        operation_id = f"check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Determine data types to check
        if data_types is None:
            data_types = self._get_available_data_types()

        # Create operation
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type='check_changes',
            data_types=data_types,
            start_time=datetime.now().isoformat(),
            total_operations=len(data_types)
        )

        self.active_operations[operation_id] = operation
        self.sync_started.emit(operation_id)

        # Start check worker
        worker = ChangeCheckWorker(operation, self)
        worker.progress_updated.connect(self._on_sync_progress)
        worker.sync_completed.connect(self._on_sync_completed)
        worker.start()

        return operation_id

    def _get_available_data_types(self) -> List[str]:
        """Get list of available data types from local files"""
        data_types = []
        try:
            if os.path.exists(self.data_directory):
                for filename in os.listdir(self.data_directory):
                    if filename.endswith('.csv') and not filename.startswith('.'):
                        data_type = filename[:-4]  # Remove .csv extension
                        data_types.append(data_type)
        except Exception as e:
            self.logger.error(f"Error getting available data types: {e}")

        return data_types

    def _on_sync_progress(self, operation_id: str, progress: int, status: str):
        """Handle sync progress updates"""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation.progress = progress
            operation.current_step = status
            self.sync_progress.emit(operation_id, progress, status)

    def _on_sync_completed(self, operation_id: str, success: bool, message: str):
        """Handle sync completion"""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation.status = 'completed' if success else 'failed'
            operation.end_time = datetime.now().isoformat()
            operation.error_message = message if not success else None

            # Move to history
            self.operation_history.append(operation)
            del self.active_operations[operation_id]

            self.sync_completed.emit(operation_id, success, message)

    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an active operation"""
        if operation_id in self.active_operations:
            # Implementation would depend on worker thread cancellation
            operation = self.active_operations[operation_id]
            operation.status = 'cancelled'
            operation.end_time = datetime.now().isoformat()

            # Move to history
            self.operation_history.append(operation)
            del self.active_operations[operation_id]

            return True
        return False


class SyncWorker(QThread):
    """Worker thread for sync operations"""

    progress_updated = Signal(str, int, str)  # operation_id, progress, status
    sync_completed = Signal(str, bool, str)   # operation_id, success, message

    def __init__(self, operation: SyncOperation, sync_manager: IntelligentSyncManager):
        super().__init__()
        self.operation = operation
        self.sync_manager = sync_manager
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Execute sync operation"""
        try:
            self.operation.status = 'running'

            if self.operation.operation_type == 'upload':
                self._perform_upload()
            elif self.operation.operation_type == 'download':
                self._perform_download()

            self.operation.status = 'completed'
            self.sync_completed.emit(self.operation.operation_id, True, "Sync completed successfully")

        except Exception as e:
            self.operation.status = 'failed'
            error_msg = f"Sync failed: {str(e)}"
            self.logger.error(error_msg)
            self.sync_completed.emit(self.operation.operation_id, False, error_msg)

    def _perform_upload(self):
        """Perform upload sync"""
        total_types = len(self.operation.data_types)

        for i, data_type in enumerate(self.operation.data_types):
            # Update progress
            progress = int((i / total_types) * 100)
            status = f"Uploading {data_type}..."
            self.progress_updated.emit(self.operation.operation_id, progress, status)

            # Check daily limits
            if not self.sync_manager.check_daily_limits('write', 10):  # Estimate 10 writes per data type
                raise Exception("Daily write limit would be exceeded")

            # Load local data
            file_path = os.path.join(self.sync_manager.data_directory, f"{data_type}.csv")
            if not os.path.exists(file_path):
                continue

            df = pd.read_csv(file_path)

            # Upload to Firebase (simplified - actual implementation would use firebase_manager)
            if self.sync_manager.firebase_manager:
                # This would call the actual Firebase upload method
                success = self._upload_data_to_firebase(data_type, df)
                if success:
                    # Update metadata
                    checksum = self.sync_manager.calculate_data_checksum(df)
                    self.sync_manager.sync_metadata[data_type] = SyncMetadata(
                        last_sync_timestamp=datetime.now().isoformat(),
                        data_checksum=checksum,
                        record_count=len(df),
                        file_size=os.path.getsize(file_path),
                        sync_direction='upload'
                    )
                    self.sync_manager.increment_operation_count('write', 10)  # Estimate

            self.operation.completed_operations += 1

        # Final progress
        self.progress_updated.emit(self.operation.operation_id, 100, "Upload completed")
        self.sync_manager.save_sync_metadata()

    def _perform_download(self):
        """Perform download sync"""
        total_types = len(self.operation.data_types)

        for i, data_type in enumerate(self.operation.data_types):
            # Update progress
            progress = int((i / total_types) * 100)
            status = f"Downloading {data_type}..."
            self.progress_updated.emit(self.operation.operation_id, progress, status)

            # Check daily limits
            if not self.sync_manager.check_daily_limits('read', 5):  # Estimate 5 reads per data type
                raise Exception("Daily read limit would be exceeded")

            # Download from Firebase (simplified)
            if self.sync_manager.firebase_manager:
                df = self._download_data_from_firebase(data_type)
                if df is not None:
                    # Save to local file
                    file_path = os.path.join(self.sync_manager.data_directory, f"{data_type}.csv")
                    os.makedirs(self.sync_manager.data_directory, exist_ok=True)
                    df.to_csv(file_path, index=False)

                    # Update metadata
                    checksum = self.sync_manager.calculate_data_checksum(df)
                    self.sync_manager.sync_metadata[data_type] = SyncMetadata(
                        last_sync_timestamp=datetime.now().isoformat(),
                        data_checksum=checksum,
                        record_count=len(df),
                        file_size=os.path.getsize(file_path),
                        sync_direction='download'
                    )
                    self.sync_manager.increment_operation_count('read', 5)  # Estimate

            self.operation.completed_operations += 1

        # Final progress
        self.progress_updated.emit(self.operation.operation_id, 100, "Download completed")
        self.sync_manager.save_sync_metadata()

    def _upload_data_to_firebase(self, data_type: str, df: pd.DataFrame) -> bool:
        """Upload data to Firebase (placeholder implementation)"""
        try:
            # This would use the actual Firebase manager to upload data
            # For now, just simulate the operation
            QApplication.processEvents()  # Allow UI updates
            self.msleep(100)  # Simulate network delay
            return True
        except Exception as e:
            self.logger.error(f"Error uploading {data_type}: {e}")
            return False

    def _download_data_from_firebase(self, data_type: str) -> Optional[pd.DataFrame]:
        """Download data from Firebase (placeholder implementation)"""
        try:
            # This would use the actual Firebase manager to download data
            # For now, just simulate the operation
            QApplication.processEvents()  # Allow UI updates
            self.msleep(100)  # Simulate network delay

            # Return empty DataFrame as placeholder
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error downloading {data_type}: {e}")
            return None


class ChangeCheckWorker(QThread):
    """Worker thread for checking changes"""

    progress_updated = Signal(str, int, str)  # operation_id, progress, status
    sync_completed = Signal(str, bool, str)   # operation_id, success, message

    def __init__(self, operation: SyncOperation, sync_manager: IntelligentSyncManager):
        super().__init__()
        self.operation = operation
        self.sync_manager = sync_manager
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Execute change check operation"""
        try:
            self.operation.status = 'running'

            total_types = len(self.operation.data_types)
            changes_found = []

            for i, data_type in enumerate(self.operation.data_types):
                # Update progress
                progress = int((i / total_types) * 100)
                status = f"Checking {data_type}..."
                self.progress_updated.emit(self.operation.operation_id, progress, status)

                # Check for local changes
                has_local_changes = self.sync_manager.detect_local_changes(data_type)

                # Check for remote changes (if within limits)
                has_remote_changes = False
                if self.sync_manager.check_daily_limits('read', 1):
                    has_remote_changes, _ = self.sync_manager.detect_remote_changes(data_type)

                if has_local_changes or has_remote_changes:
                    changes_found.append({
                        'data_type': data_type,
                        'local_changes': has_local_changes,
                        'remote_changes': has_remote_changes
                    })

                self.operation.completed_operations += 1
                QApplication.processEvents()  # Allow UI updates

            # Final progress
            self.progress_updated.emit(self.operation.operation_id, 100, "Change check completed")

            # Emit changes detected signals
            for change in changes_found:
                self.sync_manager.changes_detected.emit(change['data_type'], change)

            self.operation.status = 'completed'
            message = f"Found changes in {len(changes_found)} data types" if changes_found else "No changes detected"
            self.sync_completed.emit(self.operation.operation_id, True, message)

        except Exception as e:
            self.operation.status = 'failed'
            error_msg = f"Change check failed: {str(e)}"
            self.logger.error(error_msg)
            self.sync_completed.emit(self.operation.operation_id, False, error_msg)

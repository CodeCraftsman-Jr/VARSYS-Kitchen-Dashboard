"""
Asynchronous Cloud Sync Worker for Kitchen Dashboard v1.0.6
Handles background cloud sync operations with progress tracking and UI responsiveness
"""

import logging
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from PySide6.QtWidgets import QApplication


class AsyncCloudSyncWorker(QThread):
    """
    Asynchronous worker for cloud sync operations
    Prevents UI blocking during Firebase data transfers
    """
    
    # Signals for communication with main thread
    progress_updated = Signal(dict)  # progress_data
    status_updated = Signal(dict)    # status_data
    operation_completed = Signal(dict)  # result_data
    error_occurred = Signal(dict)    # error_data
    
    def __init__(self, operation_type, firebase_manager, cloud_sync_settings, data=None, parent=None):
        super().__init__(parent)
        self.operation_type = operation_type
        self.firebase_manager = firebase_manager
        self.cloud_sync_settings = cloud_sync_settings
        self.data = data
        self.logger = logging.getLogger(__name__)

        # Thread control
        self._cancelled = False
        self._mutex = QMutex()

        # Progress tracking
        self.total_records = 0
        self.processed_records = 0
        self.current_collection = ""
        self.start_time = None

        # Validate Firebase manager on initialization
        self.firebase_available = self.validate_firebase_manager()

    def validate_firebase_manager(self):
        """Validate that Firebase manager is properly initialized and available"""
        try:
            if not self.firebase_manager:
                self.logger.error("Firebase manager is None")
                return False

            # Check database availability using the new method
            if hasattr(self.firebase_manager, 'is_database_available'):
                if not self.firebase_manager.is_database_available():
                    self.logger.error("Firebase database is not available")

                    # Try to reinitialize database
                    if hasattr(self.firebase_manager, 'reinitialize_database'):
                        self.logger.info("Attempting to reinitialize Firebase database...")
                        if self.firebase_manager.reinitialize_database():
                            self.logger.info("Database reinitialized successfully")
                        else:
                            self.logger.error("Database reinitialization failed")
                            return False
                    else:
                        return False
            else:
                # Fallback to old method
                if not hasattr(self.firebase_manager, 'db') or not self.firebase_manager.db:
                    self.logger.error("Firebase manager database is not initialized")
                    return False

            if not hasattr(self.firebase_manager, 'is_authenticated') or not self.firebase_manager.is_authenticated():
                self.logger.error("Firebase manager is not authenticated")
                return False

            # Test basic Firebase connectivity
            try:
                # Try to access a simple collection to test connectivity
                test_ref = self.firebase_manager.db.collection('test')
                # This doesn't actually read data, just creates a reference
                self.logger.info("Firebase manager validation successful")
                return True

            except Exception as e:
                self.logger.error(f"Firebase connectivity test failed: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Error validating Firebase manager: {e}")
            return False

    def run(self):
        """Main worker thread execution"""
        try:
            self.start_time = datetime.now()
            self._cancelled = False

            self.emit_status("starting", f"Starting {self.operation_type} operation...")

            # Validate Firebase availability before starting
            if not self.firebase_available:
                self.logger.error("Firebase not available - re-validating...")
                self.firebase_available = self.validate_firebase_manager()

                if not self.firebase_available:
                    raise ValueError("Firebase not available for sync operation")

            # Perform the requested operation
            if self.operation_type == 'upload':
                self.perform_upload()
            elif self.operation_type == 'download':
                self.perform_download()
            elif self.operation_type in ['smart_sync', 'bidirectional']:
                self.perform_smart_sync()
            else:
                raise ValueError(f"Unknown operation type: {self.operation_type}")

        except Exception as e:
            self.logger.error(f"Error in async sync worker: {e}")
            self.error_occurred.emit({
                'error': str(e),
                'operation_type': self.operation_type
            })
    
    def perform_upload(self):
        """Perform asynchronous upload operation"""
        try:
            if not self.data:
                raise ValueError("No data provided for upload")

            # Check if data is empty
            if not any(not df.empty for df in self.data.values()):
                self.logger.warning("All data collections are empty")
                self.operation_completed.emit({
                    'success': False,
                    'operation_type': 'upload',
                    'message': "No data to upload - all collections are empty",
                    'data': None
                })
                return

            user_id = self.cloud_sync_settings.get('user_id')
            if not user_id:
                raise ValueError("No user ID available")

            # Calculate total records (only non-empty DataFrames)
            self.total_records = sum(len(df) for df in self.data.values() if not df.empty)
            self.processed_records = 0

            if self.total_records == 0:
                self.logger.warning("No records found to upload")
                self.operation_completed.emit({
                    'success': False,
                    'operation_type': 'upload',
                    'message': "No records found to upload",
                    'data': None
                })
                return

            self.emit_status("uploading", f"Uploading {len(self.data)} collections ({self.total_records} records) to cloud...")
            self.emit_progress(0, "Preparing upload...", 0, self.total_records)
            
            # Upload each collection
            for i, (collection_name, df) in enumerate(self.data.items()):
                if self.is_cancelled():
                    return
                
                if df.empty:
                    continue
                
                self.current_collection = collection_name
                self.emit_status("uploading", f"Uploading {collection_name}...")
                
                # Upload collection with progress tracking
                self.upload_collection(collection_name, df, user_id)
                
                # Update overall progress
                collection_progress = int(((i + 1) / len(self.data)) * 100)
                self.emit_progress(collection_progress, f"Uploaded {collection_name}", 
                                 self.processed_records, self.total_records)
            
            # Complete upload
            self.emit_progress(100, "Upload completed", self.total_records, self.total_records)
            self.operation_completed.emit({
                'success': True,
                'operation_type': 'upload',
                'message': f"Successfully uploaded {self.processed_records} records",
                'data': None
            })
            
        except Exception as e:
            self.logger.error(f"Upload error: {e}")
            self.error_occurred.emit({
                'error': str(e),
                'operation_type': 'upload'
            })
    
    def upload_collection(self, collection_name, df, user_id):
        """Upload a single collection with batch processing"""
        try:
            if not self.firebase_manager or not self.firebase_manager.db:
                raise ValueError("Firebase not available")
            
            # Convert DataFrame to optimized format
            records = self.optimize_dataframe_for_firestore(df)
            batch_size = 100  # Firestore batch limit
            
            # Process in batches
            for i in range(0, len(records), batch_size):
                if self.is_cancelled():
                    return
                
                batch_records = records[i:i + batch_size]
                
                # Create Firestore batch
                batch = self.firebase_manager.db.batch()
                
                for record in batch_records:
                    doc_ref = (self.firebase_manager.db
                              .collection('users')
                              .document(user_id)
                              .collection(collection_name)
                              .document())
                    batch.set(doc_ref, record)
                
                # Commit batch
                batch.commit()
                self.processed_records += len(batch_records)
                
                # Update progress within collection
                collection_progress = int((i + len(batch_records)) / len(records) * 100)
                self.emit_status("uploading", 
                               f"Uploading {collection_name}: {self.processed_records}/{self.total_records} records")
                
                # Small delay to prevent overwhelming Firebase
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error uploading collection {collection_name}: {e}")
            raise
    
    def perform_download(self):
        """Perform asynchronous download operation"""
        try:
            user_id = self.cloud_sync_settings.get('user_id')
            collections = self.cloud_sync_settings.get('sync_collections', [])
            
            if not user_id:
                raise ValueError("No user ID available")
            
            self.emit_status("downloading", "Starting download from cloud...")
            self.emit_progress(0, "Connecting to cloud...", 0, len(collections))
            
            downloaded_data = {}
            
            for i, collection_name in enumerate(collections):
                if self.is_cancelled():
                    return
                
                self.current_collection = collection_name
                self.emit_status("downloading", f"Downloading {collection_name}...")
                
                # Download collection
                collection_data = self.download_collection(collection_name, user_id)
                
                if collection_data is not None and not collection_data.empty:
                    downloaded_data[collection_name] = collection_data
                
                # Update progress
                progress = int(((i + 1) / len(collections)) * 100)
                self.emit_progress(progress, f"Downloaded {collection_name}", i + 1, len(collections))
                
                time.sleep(0.1)  # Prevent overwhelming Firebase
            
            # Complete download
            self.emit_progress(100, "Download completed", len(collections), len(collections))
            self.operation_completed.emit({
                'success': True,
                'operation_type': 'download',
                'message': f"Successfully downloaded {len(downloaded_data)} collections",
                'data': downloaded_data
            })
            
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            self.error_occurred.emit({
                'error': str(e),
                'operation_type': 'download'
            })
    
    def download_collection(self, collection_name, user_id):
        """Download a single collection from Firebase"""
        try:
            if not self.firebase_manager or not self.firebase_manager.db:
                raise ValueError("Firebase not available")
            
            collection_ref = (self.firebase_manager.db
                            .collection('users')
                            .document(user_id)
                            .collection(collection_name))
            
            docs = collection_ref.stream()
            records = []
            
            for doc in docs:
                if self.is_cancelled():
                    return None
                
                doc_data = doc.to_dict()
                # Remove metadata fields
                doc_data.pop('_sync_timestamp', None)
                doc_data.pop('_record_hash', None)
                records.append(doc_data)
            
            if records:
                return pd.DataFrame(records)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error downloading collection {collection_name}: {e}")
            return None
    
    def perform_smart_sync(self):
        """Perform asynchronous smart sync operation"""
        try:
            self.emit_status("smart_sync", "Starting smart sync...")
            
            # Step 1: Download cloud data
            self.emit_progress(10, "Downloading cloud data...", 0, 100)
            cloud_data = self.get_cloud_data()
            
            if self.is_cancelled():
                return
            
            # Step 2: Get local data
            self.emit_progress(30, "Processing local data...", 0, 100)
            local_data = self.data or {}
            
            # Step 3: Merge data
            self.emit_progress(50, "Merging data...", 0, 100)
            merged_data = self.merge_data(local_data, cloud_data)
            
            if self.is_cancelled():
                return
            
            # Step 4: Upload merged data
            self.emit_progress(70, "Uploading merged data...", 0, 100)
            self.data = merged_data
            self.perform_upload()
            
            if self.is_cancelled():
                return
            
            # Complete smart sync
            self.emit_progress(100, "Smart sync completed", 100, 100)
            self.operation_completed.emit({
                'success': True,
                'operation_type': 'smart_sync',
                'message': f"Smart sync completed with {len(merged_data)} collections",
                'data': merged_data
            })
            
        except Exception as e:
            self.logger.error(f"Smart sync error: {e}")
            self.error_occurred.emit({
                'error': str(e),
                'operation_type': 'smart_sync'
            })
    
    def get_cloud_data(self):
        """Get cloud data for smart sync"""
        try:
            user_id = self.cloud_sync_settings.get('user_id')
            collections = self.cloud_sync_settings.get('sync_collections', [])
            
            cloud_data = {}
            for collection_name in collections:
                if self.is_cancelled():
                    return {}
                
                collection_data = self.download_collection(collection_name, user_id)
                if collection_data is not None and not collection_data.empty:
                    cloud_data[collection_name] = collection_data
            
            return cloud_data
            
        except Exception as e:
            self.logger.error(f"Error getting cloud data: {e}")
            return {}
    
    def merge_data(self, local_data, cloud_data):
        """Merge local and cloud data intelligently"""
        try:
            merged_data = {}
            all_collections = set(local_data.keys()) | set(cloud_data.keys())
            
            for collection_name in all_collections:
                if self.is_cancelled():
                    return {}
                
                local_df = local_data.get(collection_name)
                cloud_df = cloud_data.get(collection_name)
                
                if local_df is None and cloud_df is not None:
                    merged_data[collection_name] = cloud_df.copy()
                elif local_df is not None and cloud_df is None:
                    merged_data[collection_name] = local_df.copy()
                elif local_df is not None and cloud_df is not None:
                    # Merge both DataFrames
                    combined_df = pd.concat([local_df, cloud_df], ignore_index=True)
                    merged_data[collection_name] = combined_df.drop_duplicates()
                
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Error merging data: {e}")
            return local_data or {}
    
    def optimize_dataframe_for_firestore(self, df):
        """Optimize DataFrame for Firestore storage"""
        records = []
        for _, row in df.iterrows():
            record = {}
            for col, value in row.items():
                if pd.isna(value):
                    record[col] = None
                elif isinstance(value, (int, float)):
                    record[col] = float(value) if not pd.isna(value) else 0.0
                elif isinstance(value, bool):
                    record[col] = bool(value)
                else:
                    record[col] = str(value)
            
            record['_sync_timestamp'] = datetime.now().isoformat()
            records.append(record)
        
        return records
    
    def emit_progress(self, progress, message, processed, total):
        """Emit progress update signal"""
        self.progress_updated.emit({
            'progress': progress,
            'current_operation': message,
            'records_processed': processed,
            'total_records': total,
            'collection': self.current_collection
        })
    
    def emit_status(self, status, message):
        """Emit status update signal"""
        self.status_updated.emit({
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def cancel_operation(self):
        """Cancel the current operation"""
        with QMutexLocker(self._mutex):
            self._cancelled = True
        self.logger.info(f"Cancellation requested for {self.operation_type} operation")
    
    def is_cancelled(self):
        """Check if operation has been cancelled"""
        with QMutexLocker(self._mutex):
            return self._cancelled

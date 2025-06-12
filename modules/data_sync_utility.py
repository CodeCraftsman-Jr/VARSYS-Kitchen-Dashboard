"""
Data Synchronization Utility
============================

Provides utilities for keeping CSV files and application data in sync.
"""

import os
import pandas as pd
from datetime import datetime

class DataSyncManager:
    """Manages synchronization between CSV files and application data"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.last_sync = {}
        
    def save_dataframe_to_csv(self, df, filename, backup=True):
        """Save dataframe to CSV with proper error handling"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            
            # Create backup if requested
            if backup and os.path.exists(filepath):
                backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                df_existing = pd.read_csv(filepath)
                df_existing.to_csv(backup_path, index=False)
            
            # Ensure directory exists
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Save with proper encoding
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            # Update sync timestamp
            self.last_sync[filename] = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def load_dataframe_from_csv(self, filename, default_columns=None):
        """Load dataframe from CSV with error handling"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, encoding='utf-8')
                return df
            else:
                # Create empty dataframe with default columns
                if default_columns:
                    df = pd.DataFrame(columns=default_columns)
                    self.save_dataframe_to_csv(df, filename, backup=False)
                    return df
                else:
                    return pd.DataFrame()
                    
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            if default_columns:
                return pd.DataFrame(columns=default_columns)
            return pd.DataFrame()
    
    def sync_data_to_application(self, app_data_dict):
        """Sync CSV files to application data dictionary"""
        try:
            files_synced = 0
            
            for key, df in app_data_dict.items():
                filename = f"{key}.csv"
                filepath = os.path.join(self.data_dir, filename)
                
                if os.path.exists(filepath):
                    # Check if file was modified since last sync
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    last_sync_time = self.last_sync.get(filename, datetime.min)
                    
                    if file_mtime > last_sync_time:
                        # File was modified, reload it
                        new_df = pd.read_csv(filepath, encoding='utf-8')
                        app_data_dict[key] = new_df
                        self.last_sync[filename] = datetime.now()
                        files_synced += 1
            
            return files_synced
            
        except Exception as e:
            print(f"Error syncing data to application: {e}")
            return 0
    
    def force_sync_all(self, app_data_dict):
        """Force sync all data regardless of timestamps"""
        try:
            for key, df in app_data_dict.items():
                filename = f"{key}.csv"
                new_df = self.load_dataframe_from_csv(filename)
                if not new_df.empty or key in app_data_dict:
                    app_data_dict[key] = new_df
            
            return True
            
        except Exception as e:
            print(f"Error in force sync: {e}")
            return False

# Global instance
_sync_manager = None

def get_sync_manager():
    """Get the global sync manager instance"""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = DataSyncManager()
    return _sync_manager

def save_and_sync(data_dict, key, dataframe):
    """Save dataframe and sync with application data"""
    sync_manager = get_sync_manager()
    filename = f"{key}.csv"
    
    if sync_manager.save_dataframe_to_csv(dataframe, filename):
        data_dict[key] = dataframe
        return True
    return False

def refresh_from_csv(data_dict, key):
    """Refresh specific data from CSV file"""
    sync_manager = get_sync_manager()
    filename = f"{key}.csv"
    
    new_df = sync_manager.load_dataframe_from_csv(filename)
    if not new_df.empty or key in data_dict:
        data_dict[key] = new_df
        return True
    return False

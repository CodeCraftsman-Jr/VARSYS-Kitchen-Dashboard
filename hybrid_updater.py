#!/usr/bin/env python3
"""
Hybrid Auto-Updater for VARSYS Kitchen Dashboard
Combines Git-based and HTTP-based update methods for optimal performance
"""

import os
import sys
import json
import tempfile
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Callable, Tuple
import threading

# Import both update methods
try:
    from git_updater import get_git_repository_manager, GIT_AVAILABLE
except ImportError:
    GIT_AVAILABLE = False
    get_git_repository_manager = None

try:
    from enhanced_updater import get_enhanced_updater
    HTTP_UPDATER_AVAILABLE = True
except ImportError:
    try:
        from updater import get_updater as get_enhanced_updater
        HTTP_UPDATER_AVAILABLE = True
    except ImportError:
        HTTP_UPDATER_AVAILABLE = False
        get_enhanced_updater = None

from __version__ import __version__, is_newer_version


class HybridUpdater:
    """Hybrid updater that tries Git first, falls back to HTTP"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.current_version = __version__
        self.git_manager = None
        self.http_updater = None
        self.last_check_file = "last_update_check.json"
        self.update_check_interval = 24  # hours
        
        # Initialize available updaters
        self._initialize_updaters()
        
    def log(self, message, level="info"):
        """Log message"""
        if self.logger:
            getattr(self.logger, level)(f"[Hybrid Updater] {message}")
        else:
            print(f"[{level.upper()}] {message}")
    
    def _initialize_updaters(self):
        """Initialize available update methods"""
        # Initialize Git updater if available
        if GIT_AVAILABLE and get_git_repository_manager:
            try:
                self.git_manager = get_git_repository_manager(self.logger)
                self.log("Git updater initialized")
            except Exception as e:
                self.log(f"Failed to initialize Git updater: {e}", "warning")
                self.git_manager = None
        
        # Initialize HTTP updater if available
        if HTTP_UPDATER_AVAILABLE and get_enhanced_updater:
            try:
                self.http_updater = get_enhanced_updater(self.logger)
                self.log("HTTP updater initialized")
            except Exception as e:
                self.log(f"Failed to initialize HTTP updater: {e}", "warning")
                self.http_updater = None
        
        # Log available methods
        methods = []
        if self.git_manager and self.git_manager.is_git_available():
            methods.append("Git")
        if self.http_updater:
            methods.append("HTTP")
        
        if methods:
            self.log(f"Available update methods: {', '.join(methods)}")
        else:
            self.log("No update methods available", "error")
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on interval"""
        try:
            if not os.path.exists(self.last_check_file):
                return True
                
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                
            last_check = datetime.fromisoformat(data.get('last_check', '2000-01-01'))
            return datetime.now() - last_check > timedelta(hours=self.update_check_interval)
            
        except Exception as e:
            self.log(f"Error checking update interval: {e}", "warning")
            return True
    
    def save_last_check_time(self, method_used: str = "unknown"):
        """Save the last update check time"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'current_version': self.current_version,
                'method_used': method_used
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.log(f"Error saving last check time: {e}", "warning")
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check for updates using the best available method"""
        self.log("Checking for updates...")
        
        # Try Git method first (faster, more reliable)
        if self.git_manager and self.git_manager.is_git_available():
            self.log("Trying Git method...")
            try:
                update_info = self.git_manager.get_latest_version_info()
                if update_info is not None:
                    self.save_last_check_time("git")
                    update_info['download_method'] = 'git'
                    self.log(f"Git method successful - Update available: {update_info.get('version', 'unknown')}")
                    return update_info
                else:
                    self.log("Git method: No update available")
                    self.save_last_check_time("git")
                    return None
            except Exception as e:
                self.log(f"Git method failed: {e}", "warning")
        
        # Fallback to HTTP method
        if self.http_updater:
            self.log("Trying HTTP method...")
            try:
                update_info = self.http_updater.check_for_updates()
                if update_info is not None:
                    self.save_last_check_time("http")
                    update_info['download_method'] = 'http'
                    self.log(f"HTTP method successful - Update available: {update_info.get('version', 'unknown')}")
                    return update_info
                else:
                    self.log("HTTP method: No update available")
                    self.save_last_check_time("http")
                    return None
            except Exception as e:
                self.log(f"HTTP method failed: {e}", "error")
        
        self.log("All update methods failed", "error")
        return None
    
    def download_update(self, update_info: Dict, 
                       progress_callback: Optional[Callable[[int], None]] = None) -> Optional[str]:
        """Download update using the specified method"""
        download_method = update_info.get('download_method', 'http')
        
        self.log(f"Downloading update using {download_method} method...")
        
        if download_method == 'git' and self.git_manager:
            try:
                return self._download_with_git(update_info, progress_callback)
            except Exception as e:
                self.log(f"Git download failed: {e}", "warning")
                # Try HTTP fallback
                if self.http_updater:
                    self.log("Falling back to HTTP download...")
                    return self._download_with_http(update_info, progress_callback)
        
        elif download_method == 'http' and self.http_updater:
            return self._download_with_http(update_info, progress_callback)
        
        self.log("No suitable download method available", "error")
        return None
    
    def _download_with_git(self, update_info: Dict, 
                          progress_callback: Optional[Callable[[int], None]] = None) -> Optional[str]:
        """Download update using Git method"""
        if not self.git_manager:
            raise Exception("Git manager not available")
        
        # Initialize repository with progress
        def git_progress(percent):
            if progress_callback:
                # Git operations take about 70% of total time
                progress_callback(int(percent * 0.7))
        
        if not self.git_manager.initialize_repository(git_progress):
            raise Exception("Failed to initialize Git repository")
        
        # Download files
        def download_progress(percent):
            if progress_callback:
                # Download takes remaining 30%
                progress_callback(70 + int(percent * 0.3))
        
        update_files_dir = self.git_manager.download_update_files(update_info, download_progress)
        
        if not update_files_dir:
            raise Exception("Failed to download update files")
        
        # Look for executable in downloaded files
        exe_path = os.path.join(update_files_dir, 'VARSYS_Kitchen_Dashboard.exe')
        if os.path.exists(exe_path):
            return exe_path
        
        # If no executable, return the directory for building
        return update_files_dir
    
    def _download_with_http(self, update_info: Dict, 
                           progress_callback: Optional[Callable[[int], None]] = None) -> Optional[str]:
        """Download update using HTTP method"""
        if not self.http_updater:
            raise Exception("HTTP updater not available")
        
        return self.http_updater.download_update(update_info, progress_callback)
    
    def install_update(self, update_file_path: str) -> bool:
        """Install the downloaded update"""
        try:
            self.log(f"Installing update from: {update_file_path}")
            
            # If it's a directory (from Git), look for executable or build script
            if os.path.isdir(update_file_path):
                return self._install_from_directory(update_file_path)
            
            # If it's a file, use HTTP updater's install method
            elif self.http_updater:
                return self.http_updater.install_update(update_file_path)
            
            else:
                self.log("No suitable installation method available", "error")
                return False
                
        except Exception as e:
            self.log(f"Error installing update: {e}", "error")
            return False
    
    def _install_from_directory(self, update_dir: str) -> bool:
        """Install update from a directory (Git download)"""
        try:
            # Look for pre-built executable
            exe_path = os.path.join(update_dir, 'VARSYS_Kitchen_Dashboard.exe')
            
            if os.path.exists(exe_path):
                # Use HTTP updater's install method for the executable
                if self.http_updater:
                    return self.http_updater.install_update(exe_path)
                else:
                    self.log("No installer available for executable", "error")
                    return False
            
            # Look for build script
            build_script = os.path.join(update_dir, 'build_cx_freeze.py')
            if os.path.exists(build_script):
                self.log("Building update from source...")
                # This would require implementing a build process
                # For now, return False and suggest manual installation
                self.log("Source-based installation not yet implemented", "warning")
                return False
            
            self.log("No installable files found in update directory", "error")
            return False
            
        except Exception as e:
            self.log(f"Error installing from directory: {e}", "error")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary files from both methods"""
        try:
            if self.git_manager:
                self.git_manager.cleanup_repository()
            
            if self.http_updater:
                self.http_updater.cleanup_temp_files()
                
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "warning")
    
    def get_update_statistics(self) -> Dict:
        """Get statistics about update methods"""
        stats = {
            'git_available': bool(self.git_manager and self.git_manager.is_git_available()),
            'http_available': bool(self.http_updater),
            'preferred_method': 'git' if self.git_manager and self.git_manager.is_git_available() else 'http'
        }
        
        # Add last check info
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, 'r') as f:
                    data = json.load(f)
                stats.update({
                    'last_check': data.get('last_check'),
                    'last_method_used': data.get('method_used', 'unknown')
                })
        except Exception:
            pass
        
        return stats


# Global hybrid updater instance
_hybrid_updater = None

def get_hybrid_updater(logger=None):
    """Get global hybrid updater instance"""
    global _hybrid_updater
    if _hybrid_updater is None:
        _hybrid_updater = HybridUpdater(logger)
    return _hybrid_updater

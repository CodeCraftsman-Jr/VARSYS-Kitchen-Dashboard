#!/usr/bin/env python3
"""
Enhanced Auto-Updater for VARSYS Kitchen Dashboard
Fixes the update installation process to properly replace the application
"""

import os
import sys
import json
import hashlib
import tempfile
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError
import ssl
import zipfile

from __version__ import (
    __version__, UPDATE_CHECK_URL, DOWNLOAD_BASE_URL, 
    is_newer_version, get_version_info
)

class EnhancedUpdater:
    """Enhanced auto-updater with proper installation process"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.current_version = __version__
        self.update_check_interval = 24  # hours
        self.last_check_file = "last_update_check.json"
        self.temp_dir = tempfile.gettempdir()
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_exe = "VARSYS_Kitchen_Dashboard.exe"
        
    def log(self, message, level="info"):
        """Log message"""
        if self.logger:
            getattr(self.logger, level)(f"[Enhanced Updater] {message}")
        else:
            print(f"[{level.upper()}] {message}")

    def should_check_for_updates(self):
        """Check if we should check for updates based on interval"""
        try:
            if not os.path.exists(self.last_check_file):
                return True
                
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                
            last_check = datetime.fromisoformat(data.get('last_check', '2000-01-01'))
            next_check = last_check + timedelta(hours=self.update_check_interval)
            
            return datetime.now() >= next_check
            
        except Exception as e:
            self.log(f"Error checking update interval: {e}", "warning")
            return True

    def save_last_check_time(self):
        """Save the last update check time"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'current_version': self.current_version
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.log(f"Error saving last check time: {e}", "warning")
    
    def check_for_updates(self):
        """Check for updates using GitHub public API"""
        try:
            self.log("Checking for updates...")
            
            # Create SSL context for secure connection
            context = ssl.create_default_context()
            
            # Make request to GitHub API
            with urlopen(UPDATE_CHECK_URL, context=context, timeout=10) as response:
                if response.status != 200:
                    self.log(f"Update check failed: HTTP {response.status}", "error")
                    return None
                    
                data = json.loads(response.read().decode())
            
            # Extract version from tag name
            tag_name = data.get('tag_name', '')
            remote_version = tag_name.lstrip('v')
            
            if not remote_version:
                self.log("No version found in release data", "warning")
                return None
            
            self.log(f"Current version: {self.current_version}, Remote version: {remote_version}")
            
            # Check if update is available
            if is_newer_version(remote_version):
                self.log(f"Update available: {remote_version}")
                
                # Save check time
                self.save_last_check_time()
                
                return {
                    'version': remote_version,
                    'tag_name': tag_name,
                    'name': data.get('name', f'Version {remote_version}'),
                    'body': data.get('body', 'No release notes available'),
                    'published_at': data.get('published_at', ''),
                    'assets': data.get('assets', []),
                    'html_url': data.get('html_url', ''),
                    'download_url': self.find_download_asset(data.get('assets', []))
                }
            else:
                self.log("No update available")
                self.save_last_check_time()
                return None
                
        except (URLError, HTTPError, json.JSONDecodeError, ssl.SSLError) as e:
            self.log(f"Update check failed: {e}", "error")
            return None
        except Exception as e:
            self.log(f"Unexpected error during update check: {e}", "error")
            return None

    def find_download_asset(self, assets):
        """Find the appropriate download asset for Windows"""
        for asset in assets:
            name = asset.get('name', '').lower()
            # Look for Windows installer or executable
            if any(ext in name for ext in ['.msi', '.exe', '_windows', '_win', '_installer']):
                return asset.get('browser_download_url')
        
        # Fallback: return first asset if no specific match
        if assets:
            return assets[0].get('browser_download_url')
        
        return None

    def verify_download(self, file_path):
        """Verify downloaded file integrity"""
        try:
            if not os.path.exists(file_path):
                self.log("Downloaded file not found", "error")
                return False
            
            # Check file size (should be reasonable for an application)
            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:  # Less than 1MB is suspicious
                self.log(f"Downloaded file too small: {file_size} bytes", "error")
                return False
            
            if file_size > 500 * 1024 * 1024:  # More than 500MB is suspicious
                self.log(f"Downloaded file too large: {file_size} bytes", "error")
                return False
            
            self.log(f"Download verification passed: {file_size} bytes")
            return True
            
        except Exception as e:
            self.log(f"Error verifying download: {e}", "error")
            return False
    
    def download_update(self, update_info, progress_callback=None):
        """Download update file securely"""
        try:
            download_url = update_info.get('download_url')
            
            if not download_url:
                self.log("No download URL found", "error")
                return None
            
            self.log(f"Downloading update from: {download_url}")
            
            # Create secure temp file
            temp_file = os.path.join(self.temp_dir, f"kitchen_dashboard_update_{update_info['version']}.exe")
            
            # Download with progress tracking
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    progress_callback(percent)
            
            urlretrieve(download_url, temp_file, reporthook=report_progress)
            
            # Verify download
            if not self.verify_download(temp_file):
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return None
            
            self.log(f"Update downloaded successfully: {temp_file}")
            return temp_file
            
        except Exception as e:
            self.log(f"Error downloading update: {e}", "error")
            return None

    def create_update_script(self, new_exe_path):
        """Create a batch script to handle the update process"""
        try:
            current_exe = os.path.join(self.app_dir, self.app_exe)
            backup_exe = os.path.join(self.app_dir, f"{self.app_exe}.backup")
            
            # Create update script
            script_content = f'''@echo off
echo Starting VARSYS Kitchen Dashboard update...

REM Wait for main application to close
timeout /t 3 /nobreak >nul

REM Backup current executable
if exist "{current_exe}" (
    echo Backing up current version...
    copy "{current_exe}" "{backup_exe}" >nul
    if errorlevel 1 (
        echo ERROR: Failed to backup current version
        pause
        exit /b 1
    )
)

REM Copy new executable
echo Installing new version...
copy "{new_exe_path}" "{current_exe}" >nul
if errorlevel 1 (
    echo ERROR: Failed to install new version
    if exist "{backup_exe}" (
        echo Restoring backup...
        copy "{backup_exe}" "{current_exe}" >nul
    )
    pause
    exit /b 1
)

REM Clean up
if exist "{backup_exe}" del "{backup_exe}" >nul
if exist "{new_exe_path}" del "{new_exe_path}" >nul

echo Update completed successfully!
echo Starting updated application...

REM Start the updated application
start "" "{current_exe}"

REM Clean up this script
del "%~f0" >nul 2>&1
'''
            
            script_path = os.path.join(self.temp_dir, "kitchen_dashboard_update.bat")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            return script_path
            
        except Exception as e:
            self.log(f"Error creating update script: {e}", "error")
            return None

    def install_update(self, update_file_path):
        """Install the downloaded update using a separate process"""
        try:
            if not os.path.exists(update_file_path):
                self.log("Update file not found", "error")
                return False
            
            self.log("Installing update...")
            
            # Check if this is an installer or just an executable
            if update_file_path.endswith('.msi'):
                # MSI installer
                subprocess.Popen([
                    'msiexec', '/i', update_file_path, '/quiet', '/norestart'
                ], shell=True)
                self.log("MSI installer started")
                return True
                
            elif update_file_path.endswith('.exe'):
                # Check if it's an installer or just the application executable
                file_size = os.path.getsize(update_file_path)
                
                # If file is large, it's likely an installer
                if file_size > 50 * 1024 * 1024:  # > 50MB
                    # Run as installer
                    subprocess.Popen([update_file_path, '/S'], shell=True)
                    self.log("Installer started")
                    return True
                else:
                    # It's just the application executable - use our update script
                    script_path = self.create_update_script(update_file_path)
                    if script_path:
                        subprocess.Popen([script_path], shell=True)
                        self.log("Update script started")
                        # Exit the current application to allow update
                        sys.exit(0)
                    else:
                        return False
            
            return False
            
        except Exception as e:
            self.log(f"Error installing update: {e}", "error")
            return False

    def cleanup_temp_files(self):
        """Clean up temporary update files"""
        try:
            temp_pattern = "kitchen_dashboard_update_"
            for file in os.listdir(self.temp_dir):
                if file.startswith(temp_pattern):
                    temp_file = os.path.join(self.temp_dir, file)
                    try:
                        os.remove(temp_file)
                        self.log(f"Cleaned up temp file: {file}")
                    except Exception as e:
                        self.log(f"Error cleaning temp file {file}: {e}", "warning")
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "warning")

# Global enhanced updater instance
_enhanced_updater_instance = None

def get_enhanced_updater(logger=None):
    """Get global enhanced updater instance"""
    global _enhanced_updater_instance
    if _enhanced_updater_instance is None:
        _enhanced_updater_instance = EnhancedUpdater(logger)
    return _enhanced_updater_instance

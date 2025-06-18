"""
VARSYS Solutions - Kitchen Dashboard
Auto-Update System

Secure update system following GitHub best practices
No API keys stored in code - uses public GitHub API
"""

import os
import sys
import json
import hashlib
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError
import ssl
import zipfile
import shutil

from __version__ import (
    __version__, UPDATE_CHECK_URL, DOWNLOAD_BASE_URL, 
    is_newer_version, get_version_info
)

class SecureUpdater:
    """Secure auto-updater following GitHub security best practices"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.current_version = __version__
        self.update_check_interval = 24  # hours
        self.last_check_file = "last_update_check.json"
        self.temp_dir = tempfile.gettempdir()
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
    def log(self, message, level="info"):
        """Log message"""
        if self.logger:
            getattr(self.logger, level)(f"[Updater] {message}")
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
            return datetime.now() - last_check > timedelta(hours=self.update_check_interval)
            
        except Exception as e:
            self.log(f"Error checking update interval: {e}", "warning")
            return True
    
    def update_last_check_time(self):
        """Update the last check time"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'current_version': self.current_version
            }
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.log(f"Error updating last check time: {e}", "warning")
    
    def check_for_updates(self):
        """Check for updates using GitHub public API (no authentication required)"""
        try:
            self.log("Checking for updates...")
            
            # Create SSL context for secure connection
            context = ssl.create_default_context()
            
            # Make request to GitHub API (public, no auth required)
            with urlopen(UPDATE_CHECK_URL, context=context, timeout=10) as response:
                if response.status != 200:
                    self.log(f"Update check failed: HTTP {response.status}", "error")
                    return None
                    
                data = json.loads(response.read().decode())
            
            # Extract version from tag name (assuming format: v1.0.0)
            tag_name = data.get('tag_name', '')
            remote_version = tag_name.lstrip('v')
            
            if not remote_version:
                self.log("No version found in release data", "warning")
                return None
            
            self.log(f"Current version: {self.current_version}")
            self.log(f"Remote version: {remote_version}")
            
            # Update last check time
            self.update_last_check_time()
            
            if is_newer_version(remote_version):
                return {
                    'version': remote_version,
                    'tag_name': tag_name,
                    'name': data.get('name', f'Version {remote_version}'),
                    'body': data.get('body', 'No release notes available'),
                    'published_at': data.get('published_at'),
                    'assets': data.get('assets', []),
                    'download_url': None  # Will be set based on assets
                }
            else:
                self.log("No updates available")
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
            # Look for Windows executable or installer
            if any(ext in name for ext in ['.exe', '.msi', '_windows', '_win']):
                return asset.get('browser_download_url')
        
        # Fallback: return first asset if no specific match
        if assets:
            return assets[0].get('browser_download_url')
        
        return None
    
    def verify_download(self, file_path, expected_size=None):
        """Verify downloaded file integrity"""
        try:
            if not os.path.exists(file_path):
                return False
                
            # Check file size if provided
            if expected_size:
                actual_size = os.path.getsize(file_path)
                if actual_size != expected_size:
                    self.log(f"File size mismatch: expected {expected_size}, got {actual_size}", "error")
                    return False
            
            # Basic file validation
            if os.path.getsize(file_path) < 1024:  # Less than 1KB is suspicious
                self.log("Downloaded file is too small", "error")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"Error verifying download: {e}", "error")
            return False
    
    def download_update(self, update_info, progress_callback=None):
        """Download update file securely"""
        try:
            # Find appropriate download asset
            download_url = self.find_download_asset(update_info.get('assets', []))
            
            if not download_url:
                self.log("No suitable download found", "error")
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
    
    def install_update(self, update_file_path):
        """Install the downloaded update with enhanced process"""
        try:
            if not os.path.exists(update_file_path):
                self.log("Update file not found", "error")
                return False

            self.log("Installing update...")

            # Check file size to determine if it's an installer or just the executable
            file_size = os.path.getsize(update_file_path)

            if update_file_path.endswith('.msi'):
                # MSI installer
                subprocess.Popen([
                    'msiexec', '/i', update_file_path, '/quiet', '/norestart'
                ], shell=True)
                self.log("MSI installer started")
                return True

            elif update_file_path.endswith('.exe'):
                # If file is large (>50MB), it's likely an installer
                if file_size > 50 * 1024 * 1024:
                    # Run as installer with silent flag
                    subprocess.Popen([update_file_path, '/SILENT'], shell=True)
                    self.log("Installer started in silent mode")
                    return True
                else:
                    # It's just the application executable - use update script
                    return self._install_executable_update(update_file_path)

            return False

        except Exception as e:
            self.log(f"Error installing update: {e}", "error")
            return False

    def _install_executable_update(self, new_exe_path):
        """Install update when the download is just the executable"""
        try:
            current_exe = os.path.join(self.app_dir, "VARSYS_Kitchen_Dashboard.exe")
            backup_exe = os.path.join(self.app_dir, "VARSYS_Kitchen_Dashboard.exe.backup")

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

            # Run the update script
            subprocess.Popen([script_path], shell=True)
            self.log("Update script started - application will restart")

            # Exit current application to allow update
            import sys
            sys.exit(0)

        except Exception as e:
            self.log(f"Error creating update script: {e}", "error")
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

# Global updater instance
_updater_instance = None

def get_updater(logger=None):
    """Get global updater instance with hybrid Git/HTTP functionality"""
    global _updater_instance
    if _updater_instance is None:
        # Try to use hybrid updater first (Git + HTTP), then enhanced, then basic
        try:
            from hybrid_updater import get_hybrid_updater
            _updater_instance = get_hybrid_updater(logger)
            if logger:
                logger.info("Using hybrid Git/HTTP updater")
        except ImportError:
            try:
                from enhanced_updater import get_enhanced_updater
                _updater_instance = get_enhanced_updater(logger)
                if logger:
                    logger.info("Using enhanced HTTP updater")
            except ImportError:
                _updater_instance = SecureUpdater(logger)
                if logger:
                    logger.info("Using basic HTTP updater")
    return _updater_instance

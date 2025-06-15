#!/usr/bin/env python3
"""
Version management for VARSYS Kitchen Dashboard
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple

# Current version information
__version__ = "1.0.6"
__build__ = "2025.01.15"
__author__ = "VARSYS"
__description__ = "Professional Kitchen Management Dashboard with Firebase Login & Cloud Sync"

# GitHub repository information
GITHUB_REPO = "VARSYS-Kitchen-Dashboard"
GITHUB_OWNER = "your-username"  # Replace with actual GitHub username
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
GITHUB_RELEASES_URL = f"{GITHUB_API_URL}/releases/latest"
GITHUB_DOWNLOAD_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest/download"

class VersionManager:
    """Handles version checking and updates"""
    
    def __init__(self):
        self.current_version = __version__
        self.current_build = __build__
        
    def get_version_info(self) -> Dict[str, str]:
        """Get current version information"""
        return {
            "version": self.current_version,
            "build": self.current_build,
            "author": __author__,
            "description": __description__,
            "release_date": self.current_build
        }
    
    def check_for_updates(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check if a newer version is available on GitHub
        Returns: (has_update, release_info)
        """
        try:
            response = requests.get(GITHUB_RELEASES_URL, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get("tag_name", "").lstrip("v")
                
                if self._is_newer_version(latest_version, self.current_version):
                    return True, {
                        "version": latest_version,
                        "name": release_data.get("name", ""),
                        "body": release_data.get("body", ""),
                        "download_url": f"{GITHUB_DOWNLOAD_URL}/VARSYS_Kitchen_Dashboard.exe",
                        "published_at": release_data.get("published_at", ""),
                        "html_url": release_data.get("html_url", "")
                    }
                else:
                    return False, None
            else:
                print(f"Failed to check for updates: HTTP {response.status_code}")
                return False, None
                
        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")
            return False, None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False, None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings (semantic versioning)"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except ValueError:
            # If version parsing fails, assume no update
            return False
    
    def download_update(self, download_url: str, save_path: str = "VARSYS_Kitchen_Dashboard_Update.exe") -> bool:
        """Download the latest version"""
        try:
            print(f"Downloading update from: {download_url}")
            response = requests.get(download_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\rDownload progress: {progress:.1f}%", end="", flush=True)
                
                print(f"\nUpdate downloaded successfully: {save_path}")
                return True
            else:
                print(f"Failed to download update: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading update: {e}")
            return False
    
    def save_version_info(self, file_path: str = "version_info.json"):
        """Save version information to file"""
        version_info = self.get_version_info()
        version_info["last_check"] = datetime.now().isoformat()
        
        try:
            with open(file_path, 'w') as f:
                json.dump(version_info, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving version info: {e}")
            return False
    
    def load_version_info(self, file_path: str = "version_info.json") -> Optional[Dict]:
        """Load version information from file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading version info: {e}")
        return None

# Global version manager instance
version_manager = VersionManager()

def get_version() -> str:
    """Get current version string"""
    return __version__

def get_build() -> str:
    """Get current build string"""
    return __build__

def get_full_version() -> str:
    """Get full version string"""
    return f"{__version__} (Build {__build__})"

if __name__ == "__main__":
    # Test version checking
    vm = VersionManager()
    print(f"Current version: {vm.get_version_info()}")
    
    print("Checking for updates...")
    has_update, release_info = vm.check_for_updates()
    
    if has_update:
        print(f"Update available: {release_info['version']}")
        print(f"Release notes: {release_info['body']}")
    else:
        print("No updates available")

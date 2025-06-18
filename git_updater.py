#!/usr/bin/env python3
"""
Git-based Auto-Updater for VARSYS Kitchen Dashboard
Provides faster downloads and incremental updates using Git
"""

import os
import sys
import json
import tempfile
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Callable, List
import threading

# Git integration imports (optional)
try:
    import git
    from git import Repo, GitCommandError, RemoteProgress
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from __version__ import __version__, is_newer_version


class GitProgressReporter(RemoteProgress):
    """Progress reporter for Git operations"""
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]] = None):
        super().__init__()
        self.progress_callback = progress_callback
        self.last_percent = 0
    
    def update(self, op_code, cur_count, max_count=None, message=''):
        """Update progress during Git operations"""
        if self.progress_callback and max_count:
            percent = min(100, int((cur_count / max_count) * 100))
            if percent != self.last_percent:
                self.progress_callback(percent)
                self.last_percent = percent


class GitRepositoryManager:
    """Manages Git repository operations for auto-updates"""

    def __init__(self, logger=None, repo_url=None, auth_token=None):
        self.logger = logger
        self.current_version = __version__
        self.temp_dir = tempfile.gettempdir()
        self.app_dir = os.path.dirname(os.path.abspath(__file__))

        # Repository configuration
        self.repo_url = repo_url or "https://github.com/VARSYS-Kitchen-Dashboard/VARSYS-Kitchen-Dashboard.git"
        self.auth_token = auth_token
        self.local_repo_path = os.path.join(self.temp_dir, "varsys_kitchen_dashboard_repo")
        self.repo = None

        # Configure authentication if provided
        self._configure_authentication()
        
    def log(self, message, level="info"):
        """Log message"""
        if self.logger:
            getattr(self.logger, level)(f"[Git Updater] {message}")
        else:
            print(f"[{level.upper()}] {message}")

    def _configure_authentication(self):
        """Configure Git authentication if credentials are provided"""
        if not self.auth_token:
            return

        try:
            # For GitHub, use token authentication in URL
            if "github.com" in self.repo_url and self.auth_token:
                # Convert HTTPS URL to use token authentication
                if self.repo_url.startswith("https://github.com/"):
                    repo_path = self.repo_url.replace("https://github.com/", "")
                    self.repo_url = f"https://{self.auth_token}@github.com/{repo_path}"
                    self.log("Configured GitHub token authentication")

        except Exception as e:
            self.log(f"Error configuring authentication: {e}", "warning")

    def set_auth_token(self, token: str):
        """Set authentication token for private repositories"""
        self.auth_token = token
        self._configure_authentication()
        self.log("Authentication token updated")
    
    def is_git_available(self) -> bool:
        """Check if Git is available"""
        if not GIT_AVAILABLE:
            self.log("GitPython not available", "warning")
            return False
        
        try:
            # Check if git command is available
            subprocess.run(['git', '--version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.log("Git command not available", "warning")
            return False
    
    def initialize_repository(self, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """Initialize or update local repository"""
        try:
            if not self.is_git_available():
                return False
            
            progress_reporter = GitProgressReporter(progress_callback)
            
            if os.path.exists(self.local_repo_path):
                # Repository exists, try to update it
                self.log("Updating existing repository...")
                try:
                    self.repo = Repo(self.local_repo_path)
                    
                    # Fetch latest changes
                    origin = self.repo.remotes.origin
                    origin.fetch(progress=progress_reporter)
                    
                    # Reset to latest origin/main
                    self.repo.git.reset('--hard', 'origin/main')
                    
                    self.log("Repository updated successfully")
                    return True
                    
                except GitCommandError as e:
                    self.log(f"Failed to update repository: {e}", "warning")
                    # Remove corrupted repo and try fresh clone
                    shutil.rmtree(self.local_repo_path, ignore_errors=True)
            
            # Clone fresh repository
            self.log("Cloning repository...")
            self.repo = Repo.clone_from(
                self.repo_url,
                self.local_repo_path,
                progress=progress_reporter,
                depth=1,  # Shallow clone for speed
                single_branch=True,
                branch='main'
            )
            
            self.log("Repository cloned successfully")
            return True
            
        except Exception as e:
            self.log(f"Error initializing repository: {e}", "error")
            return False
    
    def get_latest_version_info(self) -> Optional[Dict]:
        """Get latest version information from Git repository"""
        try:
            if not self.repo:
                if not self.initialize_repository():
                    return None
            
            # Get latest tag
            tags = sorted(self.repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
            
            if not tags:
                self.log("No tags found in repository", "warning")
                return None
            
            latest_tag = tags[0]
            remote_version = latest_tag.name.lstrip('v')
            
            self.log(f"Current version: {self.current_version}, Remote version: {remote_version}")
            
            if is_newer_version(remote_version):
                # Get commit information
                commit = latest_tag.commit
                
                return {
                    'version': remote_version,
                    'tag_name': latest_tag.name,
                    'name': f'Version {remote_version}',
                    'body': commit.message,
                    'published_at': commit.committed_datetime.isoformat(),
                    'commit_sha': commit.hexsha,
                    'download_method': 'git'
                }
            else:
                self.log("No update available")
                return None
                
        except Exception as e:
            self.log(f"Error getting version info: {e}", "error")
            return None
    
    def download_update_files(self, version_info: Dict, 
                            progress_callback: Optional[Callable[[int], None]] = None) -> Optional[str]:
        """Download update files using Git"""
        try:
            if not self.repo:
                self.log("Repository not initialized", "error")
                return None
            
            # Checkout specific version
            tag_name = version_info.get('tag_name')
            if tag_name:
                self.log(f"Checking out version {tag_name}")
                self.repo.git.checkout(tag_name)
            
            # Find built executable or build files
            update_files_dir = os.path.join(self.temp_dir, f"varsys_update_{version_info['version']}")
            
            if os.path.exists(update_files_dir):
                shutil.rmtree(update_files_dir)
            
            os.makedirs(update_files_dir)
            
            # Look for pre-built executables in releases or dist folder
            possible_exe_paths = [
                os.path.join(self.local_repo_path, 'dist', 'VARSYS_Kitchen_Dashboard.exe'),
                os.path.join(self.local_repo_path, 'build', 'VARSYS_Kitchen_Dashboard.exe'),
                os.path.join(self.local_repo_path, 'releases', 'VARSYS_Kitchen_Dashboard.exe'),
                os.path.join(self.local_repo_path, 'VARSYS_Kitchen_Dashboard.exe')
            ]
            
            exe_found = False
            for exe_path in possible_exe_paths:
                if os.path.exists(exe_path):
                    self.log(f"Found executable: {exe_path}")
                    dest_path = os.path.join(update_files_dir, 'VARSYS_Kitchen_Dashboard.exe')
                    shutil.copy2(exe_path, dest_path)
                    exe_found = True
                    break
            
            if not exe_found:
                # Copy source files for building
                self.log("No pre-built executable found, copying source files")
                
                # Copy essential files
                essential_files = [
                    'kitchen_app.py',
                    'version.py',
                    '__version__.py',
                    'requirements.txt',
                    'build_cx_freeze.py'
                ]
                
                for file_name in essential_files:
                    src_path = os.path.join(self.local_repo_path, file_name)
                    if os.path.exists(src_path):
                        dest_path = os.path.join(update_files_dir, file_name)
                        shutil.copy2(src_path, dest_path)
                
                # Copy directories
                essential_dirs = ['modules', 'widgets', 'data', 'assets']
                for dir_name in essential_dirs:
                    src_dir = os.path.join(self.local_repo_path, dir_name)
                    if os.path.exists(src_dir):
                        dest_dir = os.path.join(update_files_dir, dir_name)
                        shutil.copytree(src_dir, dest_dir, ignore_errors=True)
            
            if progress_callback:
                progress_callback(100)
            
            self.log(f"Update files prepared in: {update_files_dir}")
            return update_files_dir
            
        except Exception as e:
            self.log(f"Error downloading update files: {e}", "error")
            return None
    
    def cleanup_repository(self):
        """Clean up temporary repository files"""
        try:
            if os.path.exists(self.local_repo_path):
                shutil.rmtree(self.local_repo_path, ignore_errors=True)
                self.log("Repository cleanup completed")
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "warning")


# Global Git repository manager instance
_git_repo_manager = None

def get_git_repository_manager(logger=None):
    """Get global Git repository manager instance"""
    global _git_repo_manager
    if _git_repo_manager is None:
        _git_repo_manager = GitRepositoryManager(logger)
    return _git_repo_manager

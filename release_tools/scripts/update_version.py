#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VARSYS Kitchen Dashboard - Version Update Script
Automates version updates and release preparation
"""

import os
import sys
import re
import datetime
import subprocess
import json
from pathlib import Path

class VersionUpdater:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent  # Go up two levels from release_tools/scripts
        self.version_file = self.base_dir / "__version__.py"
        self.setup_file = self.base_dir / "setup_cx_freeze.py"
        self.manifest_file = self.base_dir / "manifest.json"
        
    def get_current_version(self):
        """Get current version from __version__.py"""
        try:
            with open(self.version_file, 'r') as f:
                content = f.read()
                
            # Extract version components
            version_match = re.search(r'__version__ = "([^"]+)"', content)
            build_match = re.search(r'__build__ = "([^"]+)"', content)
            
            if version_match:
                return version_match.group(1), build_match.group(1) if build_match else None
            return None, None
        except Exception as e:
            print(f"Error reading version file: {e}")
            return None, None
    
    def update_version(self, new_version, release_type="stable"):
        """Update version in all relevant files"""
        current_version, current_build = self.get_current_version()
        new_build = datetime.datetime.now().strftime("%Y%m%d")
        
        print(f"Updating version from {current_version} to {new_version}")
        print(f"Build: {current_build} -> {new_build}")
        
        # Update __version__.py
        self._update_version_file(new_version, new_build, release_type)
        
        # Update setup_cx_freeze.py
        self._update_setup_file(new_version)
        
        # Update manifest.json
        self._update_manifest_file(new_version)
        
        print(f"SUCCESS: Version updated successfully to {new_version}")
        
    def _update_version_file(self, new_version, new_build, release_type):
        """Update __version__.py file"""
        try:
            with open(self.version_file, 'r') as f:
                content = f.read()
            
            # Parse version components
            major, minor, patch = map(int, new_version.split('.'))
            
            # Update version strings
            content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
            content = re.sub(r'__build__ = "[^"]+"', f'__build__ = "{new_build}"', content)
            
            # Update version components
            content = re.sub(r'VERSION_MAJOR = \d+', f'VERSION_MAJOR = {major}', content)
            content = re.sub(r'VERSION_MINOR = \d+', f'VERSION_MINOR = {minor}', content)
            content = re.sub(r'VERSION_PATCH = \d+', f'VERSION_PATCH = {patch}', content)
            content = re.sub(r'VERSION_BUILD = \d+', f'VERSION_BUILD = {new_build}', content)
            
            # Update release type
            content = re.sub(r'RELEASE_TYPE = "[^"]+"', f'RELEASE_TYPE = "{release_type}"', content)
            
            with open(self.version_file, 'w') as f:
                f.write(content)
                
            print(f"SUCCESS: Updated {self.version_file}")

        except Exception as e:
            print(f"ERROR: Error updating version file: {e}")
    
    def _update_setup_file(self, new_version):
        """Update setup_cx_freeze.py file"""
        try:
            if not self.setup_file.exists():
                print(f"⚠️ Setup file not found: {self.setup_file}")
                return
                
            with open(self.setup_file, 'r') as f:
                content = f.read()
            
            # Update version in setup file
            content = re.sub(r'version\s*=\s*["\'][^"\']+["\']', f'version="{new_version}"', content)
            content = re.sub(r'"version":\s*"[^"]+"', f'"version": "{new_version}"', content)
            
            with open(self.setup_file, 'w') as f:
                f.write(content)
                
            print(f"SUCCESS: Updated {self.setup_file}")

        except Exception as e:
            print(f"ERROR: Error updating setup file: {e}")
    
    def _update_manifest_file(self, new_version):
        """Update manifest.json file"""
        try:
            if not self.manifest_file.exists():
                print(f"⚠️ Manifest file not found: {self.manifest_file}")
                return
                
            with open(self.manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Update version in manifest
            manifest["version"] = new_version
            manifest["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
                
            print(f"SUCCESS: Updated {self.manifest_file}")

        except Exception as e:
            print(f"ERROR: Error updating manifest file: {e}")
    
    def increment_version(self, increment_type="patch"):
        """Automatically increment version"""
        current_version, _ = self.get_current_version()
        if not current_version:
            print("ERROR: Could not read current version")
            return
        
        major, minor, patch = map(int, current_version.split('.'))
        
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        elif increment_type == "patch":
            patch += 1
        else:
            print(f"ERROR: Invalid increment type: {increment_type}")
            return
        
        new_version = f"{major}.{minor}.{patch}"
        self.update_version(new_version)
        return new_version
    
    def create_release_notes(self, version, changes=None):
        """Create release notes file"""
        release_notes_file = self.base_dir / f"RELEASE_NOTES_v{version}.md"
        
        template = f"""# VARSYS Kitchen Dashboard v{version}

## Release Date
{datetime.datetime.now().strftime("%B %d, %Y")}

## What's New

### New Features
- [Add new features here]

### Bug Fixes
- [Add bug fixes here]

### Improvements
- [Add improvements here]

### Technical Changes
- [Add technical changes here]

## Installation
1. Download the latest release from GitHub
2. Extract the ZIP file
3. Run VARSYS_Kitchen_Dashboard.exe

## System Requirements
- Windows 10 or Windows 11
- 4GB RAM minimum
- 500MB disk space

## Support
For support, please visit: https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard

---
© 2025 VARSYS Solutions. All rights reserved.
"""
        
        if changes:
            # Replace placeholders with actual changes
            for category, items in changes.items():
                if items:
                    section = f"### {category}\n" + "\n".join(f"- {item}" for item in items) + "\n"
                    template = template.replace(f"### {category}\n- [Add {category.lower()} here]", section)
        
        with open(release_notes_file, 'w') as f:
            f.write(template)
        
        print(f"SUCCESS: Created release notes: {release_notes_file}")
        return release_notes_file

def main():
    updater = VersionUpdater()
    
    if len(sys.argv) < 2:
        print("VARSYS Kitchen Dashboard - Version Update Script")
        print("\nUsage:")
        print("  python update_version.py <command> [options]")
        print("\nCommands:")
        print("  current                    - Show current version")
        print("  set <version>             - Set specific version (e.g., 1.2.0)")
        print("  increment <type>          - Increment version (major/minor/patch)")
        print("  release <version>         - Prepare release with notes")
        print("\nExamples:")
        print("  python update_version.py current")
        print("  python update_version.py set 1.1.0")
        print("  python update_version.py increment patch")
        print("  python update_version.py release 1.1.0")
        return
    
    command = sys.argv[1].lower()
    
    if command == "current":
        version, build = updater.get_current_version()
        print(f"Current version: {version}")
        print(f"Current build: {build}")
        
    elif command == "set" and len(sys.argv) >= 3:
        new_version = sys.argv[2]
        release_type = sys.argv[3] if len(sys.argv) >= 4 else "stable"
        updater.update_version(new_version, release_type)
        
    elif command == "increment" and len(sys.argv) >= 3:
        increment_type = sys.argv[2]
        new_version = updater.increment_version(increment_type)
        if new_version:
            print(f"Version incremented to: {new_version}")
            
    elif command == "release" and len(sys.argv) >= 3:
        new_version = sys.argv[2]
        updater.update_version(new_version)
        updater.create_release_notes(new_version)
        print(f"\n🎉 Release {new_version} prepared!")
        print("Next steps:")
        print("1. Edit the release notes file")
        print("2. Build the application: python setup_cx_freeze.py build")
        print("3. Test the executable")
        print("4. Commit and push to GitHub")
        print("5. Create GitHub release")
        
    else:
        print("ERROR: Invalid command or missing arguments")
        print("Use 'python update_version.py' for help")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
VARSYS Kitchen Dashboard - Main Release Launcher
Launches the release tools from the release_tools folder
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher that calls the release tools"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    release_tools_dir = script_dir / "release_tools"
    
    # Check if release_tools directory exists
    if not release_tools_dir.exists():
        print("❌ Error: release_tools directory not found")
        print(f"Expected location: {release_tools_dir}")
        print("Please make sure the release tools are properly installed.")
        return 1
    
    # Check if release_manager.py exists in scripts folder
    release_manager_path = release_tools_dir / "scripts" / "release_manager.py"
    if not release_manager_path.exists():
        print("❌ Error: release_manager.py not found in release_tools/scripts directory")
        print(f"Expected location: {release_manager_path}")
        return 1

    # Change to release_tools directory and run the release manager
    try:
        # Change working directory to release_tools
        original_cwd = os.getcwd()
        os.chdir(release_tools_dir)

        # Run the release manager with all arguments passed through
        cmd = [sys.executable, "scripts/release_manager.py"] + sys.argv[1:]
        result = subprocess.run(cmd)
        
        # Restore original working directory
        os.chdir(original_cwd)
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running release manager: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

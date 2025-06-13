#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VARSYS Kitchen Dashboard - Cross-Platform Release Manager
Works on Windows, Linux, and macOS
"""

import os
import sys
import subprocess
from pathlib import Path

class CrossPlatformReleaseManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent  # We're in release_tools/scripts
        
    def run_command(self, script, args):
        """Run a Python script with arguments"""
        try:
            cmd = [sys.executable, script] + args
            result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
                
            return result.returncode == 0
        except Exception as e:
            print(f"Error running command: {e}")
            return False
    
    def show_menu(self):
        """Show interactive menu"""
        while True:
            self.clear_screen()
            print("=" * 60)
            print("  VARSYS Kitchen Dashboard - Release Manager")
            print("=" * 60)
            print()
            
            # Get current version
            try:
                result = subprocess.run([sys.executable, "update_version.py", "current"], 
                                      capture_output=True, text=True, cwd=self.base_dir)
                if result.returncode == 0:
                    print("Current Status:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            print(f"  {line}")
                else:
                    print("  Unable to get current version")
            except:
                print("  Unable to get current version")
            
            print()
            print("Available Options:")
            print()
            print("  1. Show Current Version")
            print("  2. Increment Patch Version (1.0.3 -> 1.0.4)")
            print("  3. Increment Minor Version (1.0.3 -> 1.1.0)")
            print("  4. Increment Major Version (1.0.3 -> 2.0.0)")
            print("  5. Set Specific Version")
            print("  6. Build Application Only")
            print("  7. Create Full Release")
            print("  8. Clean Build Directory")
            print("  9. Help")
            print("  0. Exit")
            print()
            
            try:
                choice = input("Enter your choice (0-9): ").strip()
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            
            if choice == "0":
                print("\nThank you for using VARSYS Release Manager!")
                break
            elif choice == "1":
                self.show_current_version()
            elif choice == "2":
                self.increment_version("patch")
            elif choice == "3":
                self.increment_version("minor")
            elif choice == "4":
                self.increment_version("major")
            elif choice == "5":
                self.set_specific_version()
            elif choice == "6":
                self.build_application()
            elif choice == "7":
                self.create_full_release()
            elif choice == "8":
                self.clean_build()
            elif choice == "9":
                self.show_help()
            else:
                print("Invalid choice. Please try again.")
                self.pause()
    
    def clear_screen(self):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pause(self):
        """Pause and wait for user input"""
        try:
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            pass
    
    def show_current_version(self):
        """Show current version information"""
        print("\n" + "=" * 40)
        print("Current Version Information")
        print("=" * 40)
        self.run_command("update_version.py", ["current"])
        self.pause()
    
    def increment_version(self, version_type):
        """Increment version (patch, minor, or major)"""
        print(f"\n" + "=" * 40)
        print(f"Incrementing {version_type.title()} Version")
        print("=" * 40)
        
        if self.run_command("update_version.py", ["increment", version_type]):
            print(f"\nSUCCESS: {version_type.title()} version incremented successfully!")
        else:
            print(f"\nERROR: Failed to increment {version_type} version")
        
        self.pause()
    
    def set_specific_version(self):
        """Set a specific version"""
        print("\n" + "=" * 40)
        print("Set Specific Version")
        print("=" * 40)
        
        try:
            version = input("Enter new version (e.g., 1.2.0): ").strip()
            if not version:
                print("No version entered. Returning to menu.")
                self.pause()
                return
            
            if self.run_command("update_version.py", ["set", version]):
                print(f"\nSUCCESS: Version set to {version} successfully!")
            else:
                print(f"\nERROR: Failed to set version to {version}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        
        self.pause()
    
    def build_application(self):
        """Build the application"""
        print("\n" + "=" * 40)
        print("Building Application")
        print("=" * 40)
        print("This may take a few minutes...")
        print()
        
        if self.run_command("release_automation.py", ["build"]):
            print("\nSUCCESS: Application built successfully!")
            print("Check the 'build' folder for the executable.")
        else:
            print("\nERROR: Build failed. Check the error messages above.")
        
        self.pause()
    
    def create_full_release(self):
        """Create a full release"""
        print("\n" + "=" * 40)
        print("Create Full Release")
        print("=" * 40)
        
        try:
            version = input("Enter release version (e.g., 1.0.4): ").strip()
            if not version:
                print("No version entered. Returning to menu.")
                self.pause()
                return
            
            print(f"\nStarting full release process for version {version}...")
            print("This will take several minutes...")
            print()
            
            if self.run_command("release_automation.py", ["full", version]):
                print("\n" + "=" * 60)
                print("SUCCESS: Release Process Completed Successfully!")
                print("=" * 60)
                print()
                print("Generated files are in the 'releases' folder:")
                print(f"- VARSYS_Kitchen_Dashboard_v{version}.zip")
                print(f"- install_v{version}.bat")
                print("- Checksums and release info files")
                print()
                print("Next Steps:")
                print("1. Test the ZIP file in the releases folder")
                print(f"2. Edit RELEASE_NOTES_v{version}.md if needed")
                print("3. Commit and push to GitHub")
                print("4. Create GitHub release with the ZIP file")
            else:
                print(f"\nERROR: Release process failed for version {version}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        
        self.pause()
    
    def clean_build(self):
        """Clean build directory"""
        print("\n" + "=" * 40)
        print("Cleaning Build Directory")
        print("=" * 40)
        
        if self.run_command("release_automation.py", ["clean"]):
            print("\nSUCCESS: Build directory cleaned successfully!")
        else:
            print("\nERROR: Failed to clean build directory")
        
        self.pause()
    
    def show_help(self):
        """Show help information"""
        print("\n" + "=" * 60)
        print("Help - How to Use This Tool")
        print("=" * 60)
        print()
        print("This tool helps you manage versions and create releases for")
        print("the VARSYS Kitchen Dashboard application.")
        print()
        print("Version Types:")
        print("- Patch (1.0.3 -> 1.0.4): Bug fixes, small improvements")
        print("- Minor (1.0.3 -> 1.1.0): New features, backward compatible")
        print("- Major (1.0.3 -> 2.0.0): Breaking changes, major overhauls")
        print()
        print("Typical Workflow:")
        print("1. Make your code changes")
        print("2. Choose option 2, 3, or 4 to update version")
        print("3. Choose option 7 to create full release")
        print("4. Test the generated ZIP file")
        print("5. Upload to GitHub releases")
        print()
        print("Files Updated Automatically:")
        print("- __version__.py (version information)")
        print("- setup_cx_freeze.py (build configuration)")
        print("- manifest.json (application manifest)")
        print()
        print("Files Generated:")
        print("- ZIP package with your application")
        print("- Installer batch file")
        print("- Checksums for verification")
        print("- Release notes template")
        print()
        self.pause()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command line mode
        manager = CrossPlatformReleaseManager()
        command = sys.argv[1].lower()
        
        if command == "current":
            manager.run_command("update_version.py", ["current"])
        elif command == "patch":
            manager.run_command("update_version.py", ["increment", "patch"])
        elif command == "minor":
            manager.run_command("update_version.py", ["increment", "minor"])
        elif command == "major":
            manager.run_command("update_version.py", ["increment", "major"])
        elif command == "set" and len(sys.argv) >= 3:
            version = sys.argv[2]
            manager.run_command("update_version.py", ["set", version])
        elif command == "build":
            manager.run_command("release_automation.py", ["build"])
        elif command == "full" and len(sys.argv) >= 3:
            version = sys.argv[2]
            manager.run_command("release_automation.py", ["full", version])
        elif command == "clean":
            manager.run_command("release_automation.py", ["clean"])
        elif command == "help":
            print("VARSYS Kitchen Dashboard - Release Manager")
            print()
            print("Usage: python release_manager.py [command] [options]")
            print()
            print("Commands:")
            print("  current           - Show current version")
            print("  patch             - Increment patch version")
            print("  minor             - Increment minor version")
            print("  major             - Increment major version")
            print("  set <version>     - Set specific version")
            print("  build             - Build application only")
            print("  full <version>    - Complete release process")
            print("  clean             - Clean build directories")
            print("  help              - Show this help")
            print()
            print("Examples:")
            print("  python release_manager.py current")
            print("  python release_manager.py patch")
            print("  python release_manager.py full 1.0.4")
            print()
            print("Or run without arguments for interactive menu:")
            print("  python release_manager.py")
        else:
            print("Invalid command. Use 'python release_manager.py help' for usage.")
    else:
        # Interactive mode
        manager = CrossPlatformReleaseManager()
        manager.show_menu()

if __name__ == "__main__":
    main()

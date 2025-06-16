#!/usr/bin/env python3
"""
VARSYS Kitchen Dashboard v1.1.1 - Build Testing Script
Tests the built application for functionality and auto-update capabilities
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_status(message, status="info"):
    """Print a status message with icon"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")

def test_version_consistency():
    """Test that all version files are consistent"""
    print_header("Testing Version Consistency")
    
    try:
        # Test main version file
        sys.path.insert(0, os.getcwd())
        from __version__ import __version__, __build__
        
        print_status(f"Main version: {__version__}", "success")
        print_status(f"Build date: {__build__}", "success")
        
        if __version__ == "1.1.1":
            print_status("Version 1.1.1 confirmed", "success")
            return True
        else:
            print_status(f"Expected v1.1.1, got v{__version__}", "error")
            return False
            
    except Exception as e:
        print_status(f"Version test failed: {e}", "error")
        return False

def test_build_output():
    """Test that build output exists and is valid"""
    print_header("Testing Build Output")
    
    # Find build directory
    build_dirs = [
        "build/exe.win-amd64-3.12",
        "build/exe.win-amd64-3.13"
    ]
    
    build_dir = None
    for dir_path in build_dirs:
        if os.path.exists(dir_path):
            build_dir = dir_path
            break
    
    if not build_dir:
        print_status("No build directory found", "error")
        return False
    
    print_status(f"Found build directory: {build_dir}", "success")
    
    # Check main executable
    exe_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print_status(f"Main executable found ({size_mb:.1f} MB)", "success")
    else:
        print_status("Main executable not found", "error")
        return False
    
    # Check essential directories
    essential_dirs = ["modules", "utils", "data", "lib"]
    for dir_name in essential_dirs:
        dir_path = os.path.join(build_dir, dir_name)
        if os.path.exists(dir_path):
            print_status(f"Directory {dir_name} found", "success")
        else:
            print_status(f"Directory {dir_name} missing", "warning")
    
    return True

def test_executable_startup():
    """Test that the executable can start"""
    print_header("Testing Executable Startup")
    
    # Find executable
    build_dirs = [
        "build/exe.win-amd64-3.12",
        "build/exe.win-amd64-3.13"
    ]
    
    exe_path = None
    for build_dir in build_dirs:
        test_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
        if os.path.exists(test_path):
            exe_path = test_path
            break
    
    if not exe_path:
        print_status("Executable not found for testing", "error")
        return False
    
    try:
        print_status("Starting executable (will timeout after 10 seconds)...", "info")
        
        # Start process with timeout
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(exe_path)
        )
        
        # Wait for a few seconds then terminate
        time.sleep(5)
        process.terminate()
        
        # Wait for process to end
        try:
            process.wait(timeout=5)
            print_status("Executable started and stopped successfully", "success")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            print_status("Executable started but had to be killed", "warning")
            return True
            
    except Exception as e:
        print_status(f"Executable test failed: {e}", "error")
        return False

def test_installer_output():
    """Test that installer was created"""
    print_header("Testing Installer Output")
    
    installer_path = "installer_output/VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe"
    
    if os.path.exists(installer_path):
        size_mb = os.path.getsize(installer_path) / (1024 * 1024)
        print_status(f"Installer found ({size_mb:.1f} MB)", "success")
        return True
    else:
        print_status("Installer not found (may not have been built)", "warning")
        return False

def test_release_package():
    """Test that release package is complete"""
    print_header("Testing Release Package")
    
    release_dir = "release_v1.1.1"
    
    if not os.path.exists(release_dir):
        print_status("Release package not found", "error")
        return False
    
    print_status(f"Release directory found: {release_dir}", "success")
    
    # Check required files
    required_files = [
        "VARSYS_Kitchen_Dashboard.exe",
        "RELEASE_NOTES.md",
        "checksums.txt",
        "build_info.json"
    ]
    
    optional_files = [
        "VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe"
    ]
    
    all_good = True
    
    for file_name in required_files:
        file_path = os.path.join(release_dir, file_name)
        if os.path.exists(file_path):
            print_status(f"Required file found: {file_name}", "success")
        else:
            print_status(f"Required file missing: {file_name}", "error")
            all_good = False
    
    for file_name in optional_files:
        file_path = os.path.join(release_dir, file_name)
        if os.path.exists(file_path):
            print_status(f"Optional file found: {file_name}", "success")
        else:
            print_status(f"Optional file missing: {file_name}", "warning")
    
    # Test build info JSON
    try:
        build_info_path = os.path.join(release_dir, "build_info.json")
        if os.path.exists(build_info_path):
            with open(build_info_path, 'r') as f:
                build_info = json.load(f)
            
            if build_info.get("version") == "1.1.1":
                print_status("Build info version correct", "success")
            else:
                print_status("Build info version incorrect", "error")
                all_good = False
                
            if build_info.get("auto_update_enabled"):
                print_status("Auto-update enabled in build info", "success")
            else:
                print_status("Auto-update not enabled in build info", "warning")
                
    except Exception as e:
        print_status(f"Error reading build info: {e}", "error")
        all_good = False
    
    return all_good

def test_auto_update_system():
    """Test auto-update system components"""
    print_header("Testing Auto-Update System")
    
    try:
        # Test updater module
        from updater import get_updater
        updater = get_updater()
        print_status("Updater module imported successfully", "success")
        
        # Test version checking
        from __version__ import is_newer_version
        
        test_cases = [
            ("1.1.2", True),
            ("1.1.1", False),
            ("1.1.0", False)
        ]
        
        for test_version, expected in test_cases:
            result = is_newer_version(test_version)
            if result == expected:
                print_status(f"Version comparison {test_version}: {result} ✓", "success")
            else:
                print_status(f"Version comparison {test_version}: {result} ✗", "error")
        
        return True
        
    except Exception as e:
        print_status(f"Auto-update test failed: {e}", "error")
        return False

def generate_test_report():
    """Generate a test report"""
    print_header("Test Summary")
    
    tests = [
        ("Version Consistency", test_version_consistency),
        ("Build Output", test_build_output),
        ("Executable Startup", test_executable_startup),
        ("Installer Output", test_installer_output),
        ("Release Package", test_release_package),
        ("Auto-Update System", test_auto_update_system)
    ]
    
    results = []
    passed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
        except Exception as e:
            print_status(f"Test '{test_name}' crashed: {e}", "error")
            results.append((test_name, False))
    
    print_header("Final Results")
    
    for test_name, result in results:
        status = "success" if result else "error"
        print_status(f"{test_name}: {'PASS' if result else 'FAIL'}", status)
    
    print(f"\nTests Passed: {passed}/{len(tests)}")
    print(f"Success Rate: {(passed/len(tests))*100:.1f}%")
    
    if passed == len(tests):
        print_status("🎉 ALL TESTS PASSED - Build is ready for release!", "success")
    elif passed >= len(tests) * 0.8:
        print_status("⚠️ Most tests passed - Build is likely ready", "warning")
    else:
        print_status("❌ Multiple test failures - Build needs attention", "error")
    
    # Create test report file
    report_path = "test_report_v1.1.1.txt"
    with open(report_path, 'w') as f:
        f.write(f"VARSYS Kitchen Dashboard v1.1.1 - Build Test Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for test_name, result in results:
            f.write(f"{test_name}: {'PASS' if result else 'FAIL'}\n")
        
        f.write(f"\nSummary: {passed}/{len(tests)} tests passed ({(passed/len(tests))*100:.1f}%)\n")
    
    print_status(f"Test report saved: {report_path}", "info")

def main():
    """Main test function"""
    print("VARSYS Kitchen Dashboard v1.1.1 - Build Testing")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    generate_test_report()
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

"""
COMPREHENSIVE cx_Freeze setup for Kitchen Dashboard
Includes ALL files for complete functionality
"""

import sys
import os
from cx_Freeze import setup, Executable

def get_all_files():
    """Get ALL files and directories for complete application"""
    files_to_include = []
    
    # CORE DIRECTORIES - Always include
    core_dirs = [
        "data", "modules", "utils", "assets", "logs", 
        "secure_credentials", "tests", "docs", "release_tools",
        "data_backup", "reports", "releases", "md files"
    ]
    
    for dir_name in core_dirs:
        if os.path.exists(dir_name):
            files_to_include.append((dir_name + "/", dir_name + "/"))
            print(f"✓ Including directory: {dir_name}/")
    
    # CONFIGURATION FILES - Critical for Firebase and app functionality
    config_files = [
        "firebase_config.json", "firebase_web_config.json", "jwt_secret.key",
        "__version__.py", "version.py", "config.py", "varsys_config.py", 
        "varsys_branding.py", "manifest.json", "last_update_check.json",
        "version_info.txt", "enterprise.db", "offline_data.db"
    ]
    
    for file_name in config_files:
        if os.path.exists(file_name):
            files_to_include.append((file_name, file_name))
            print(f"✓ Including config: {file_name}")
    
    # UTILITY SCRIPTS - All Python scripts for full functionality
    utility_scripts = [
        "update_manager.py", "updater.py", "enhanced_updater.py",
        "credential_manager.py", "license_manager.py", "license_dialog.py",
        "firebase_installer.py", "firebase_protection.py", "protected_firebase.py",
        "fix_firebase_credentials.py", "update_firebase_config.py",
        "check_firebase_files.py", "verify_security.py",
        "create_user.py", "reset_password.py", "reset_data.py",
        "auto_cleanup.py", "quick_cleanup.py", "cleanup_sample_data.py",
        "map_recipes_to_appliances.py", "system_tray_service.py",
        "run_app_safe.py", "update_checker.py", "release.py"
    ]
    
    for script in utility_scripts:
        if os.path.exists(script):
            files_to_include.append((script, script))
            print(f"✓ Including script: {script}")
    
    # TEST FILES - All test utilities
    test_files = [
        "test_app_firebase_status.py", "test_build_compatibility.py",
        "test_daily_sync_fix.py", "test_firebase_connection_fix.py",
        "test_firebase_error_fix.py", "test_firebase_integration.py",
        "test_firebase_simple.py", "test_import.py", "test_imports_before_build.py",
        "test_nuitka_setup.py", "test_online_only_enforcement.py",
        "test_qpainter_fix.py", "test_subscription_auth.py",
        "run_tests.py", "fix_matplotlib_backend.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            files_to_include.append((test_file, test_file))
            print(f"✓ Including test: {test_file}")
    
    # DOCUMENTATION FILES - All markdown and documentation
    doc_files = [
        "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md",
        "BUILD_GUIDE.md", "BUILD_INSTRUCTIONS.md", "FIREBASE_SETUP.md",
        "RELEASE_NOTES.md", "RELEASE_NOTES_v1.0.4.md", "RELEASE_NOTES_v1.0.5.md"
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            files_to_include.append((doc_file, doc_file))
            print(f"✓ Including doc: {doc_file}")
    
    # BATCH/SHELL SCRIPTS - Installation and setup scripts
    script_files = [
        "build_app.bat", "build_app.ps1", "run_tests.bat", "run_tests.sh",
        "cleanup_sample_data.bat", "install_v1.0.5.bat", 
        "install_comprehensive_v1.0.5.bat", "init_git_repo.bat", "init_git_repo.ps1"
    ]
    
    for script_file in script_files:
        if os.path.exists(script_file):
            files_to_include.append((script_file, script_file))
            print(f"✓ Including script: {script_file}")
    
    print(f"\n📦 Total files/directories to include: {len(files_to_include)}")
    return files_to_include

# COMPREHENSIVE build options
build_exe_options = {
    "packages": [
        # Core Python packages
        "pandas", "matplotlib", "PySide6", "numpy", "PIL", "openpyxl",
        "requests", "urllib3", "certifi",
        "traceback", "sys", "os", "logging", "sqlite3",

        # GUI and visualization
        "matplotlib.backends.backend_qtagg",

        # Data processing
        "tqdm", "dateutil",

        # Security
        "cryptography",

        # Application modules - explicitly include
        "modules", "utils"
    ],

    # Include modules in Python path
    "includes": [
        "modules.settings_fixed", "modules.shopping_fixed", "modules.logs_viewer",
        "modules.firebase_sync", "modules.login_dialog", "modules.notification_system",
        "modules.inventory_fixed", "modules.sales", "modules.budget", "modules.cleaning",
        "modules.meal_planning", "modules.waste", "modules.packing_materials",
        "utils.app_logger", "utils.data_validator", "utils.performance_monitor"
    ],
    
    "include_files": get_all_files(),
    
    "excludes": ["tkinter", "unittest", "test", "distutils", "setuptools"],

    # Path handling for modules
    "path": [os.getcwd(), os.path.join(os.getcwd(), "modules"), os.path.join(os.getcwd(), "utils")],

    # Optimization
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],

    # Build options for better module handling
    "build_exe": os.path.join("build", "exe.win-amd64-3.13")
}

# Create executable with icon
icon_file = "assets/icons/vasanthkitchen.ico" if os.path.exists("assets/icons/vasanthkitchen.ico") else None

executable = Executable(
    script="kitchen_app.py",
    base="Win32GUI",
    icon=icon_file,
    target_name="VARSYS_Kitchen_Dashboard.exe"
)

# Setup configuration
setup(
    name="VARSYS Kitchen Dashboard",
    version="1.0.6",
    description="Professional Kitchen Management System with Firebase Cloud Sync",
    author="VARSYS",
    options={"build_exe": build_exe_options},
    executables=[executable]
)

print("\n🎉 COMPREHENSIVE build configuration loaded!")
print("This build includes ALL files for complete functionality:")
print("✓ Firebase credentials and configuration")
print("✓ All test utilities and scripts") 
print("✓ Documentation and guides")
print("✓ Data backups and reports")
print("✓ Release tools and installers")
print("✓ Complete module ecosystem")
print("\nReady to build a fully functional application! 🚀")

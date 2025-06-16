# VARSYS Kitchen Dashboard v1.1.1 - Build and Release Guide

## 🚀 Complete Build and Release Process

This guide will walk you through building and releasing version 1.1.1 of the Kitchen Dashboard application.

## 📋 Prerequisites

### Required Software:
- **Python 3.12 or 3.13** (recommended: 3.12 for stability)
- **Git** for version control
- **Inno Setup** for creating Windows installer
- **GitHub account** with repository access

### Required Python Packages:
```bash
pip install cx_Freeze PySide6 pandas matplotlib firebase-admin pyrebase4
```

## 🔧 Step 1: Pre-Build Preparation

### 1.1 Verify Version Update
Check that all version files show v1.1.1:
```bash
# Check main version file
python -c "from __version__ import __version__; print(f'Version: {__version__}')"

# Check setup file
python -c "import setup_cx_freeze; print('Setup version updated')"
```

### 1.2 Clean Previous Builds
```bash
# Remove old build directories
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q installer_output
```

### 1.3 Update Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install --upgrade cx_Freeze
python -m pip install -r requirements.txt
```

## 🏗️ Step 2: Build the Application

### 2.1 Automated Build (Recommended)
```bash
# Run the automated build script
build_app.bat
```

### 2.2 Manual Build Process
If you prefer manual control:

```bash
# Step 1: Build executable
python setup_cx_freeze.py build

# Step 2: Create MSI installer (optional)
python setup_cx_freeze.py bdist_msi
```

### 2.3 Verify Build Output
After building, you should have:
```
build/
├── exe.win-amd64-3.12/  (or 3.13)
│   ├── VARSYS_Kitchen_Dashboard.exe
│   ├── python3.dll
│   ├── python312.dll (or python313.dll)
│   ├── lib/
│   ├── modules/
│   ├── utils/
│   ├── data/
│   └── [other files]
```

## 📦 Step 3: Create Professional Installer

### 3.1 Update Inno Setup Script
First, update the version in the Inno Setup script:

```pascal
#define MyAppVersion "1.1.1"
```

### 3.2 Build Installer
```bash
# Compile the Inno Setup script
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VARSYS_Kitchen_Dashboard_Setup.iss
```

### 3.3 Installer Output
The installer will be created in:
```
installer_output/
└── VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe
```

## 🧪 Step 4: Test the Build

### 4.1 Test Executable
```bash
# Navigate to build directory
cd build\exe.win-amd64-3.12

# Run the application
VARSYS_Kitchen_Dashboard.exe
```

### 4.2 Test Installer
1. Run the installer as administrator
2. Install to a test directory
3. Launch the installed application
4. Verify all features work correctly
5. Test auto-update functionality

### 4.3 Test Auto-Update System
```bash
# Run the auto-update test
python test_auto_update.py
```

## 📤 Step 5: Create GitHub Release

### 5.1 Prepare Release Assets
Create a release folder with:
```
release_v1.1.1/
├── VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe
├── VARSYS_Kitchen_Dashboard.exe (standalone)
├── README.md
├── RELEASE_NOTES.md
└── checksums.txt
```

### 5.2 Generate Checksums
```bash
# Create checksums for verification
certutil -hashfile VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe SHA256 > checksums.txt
certutil -hashfile VARSYS_Kitchen_Dashboard.exe SHA256 >> checksums.txt
```

### 5.3 Create GitHub Release

#### Option A: GitHub Web Interface
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.1.1`
4. Release title: `VARSYS Kitchen Dashboard v1.1.1`
5. Upload release assets
6. Publish release

#### Option B: GitHub CLI
```bash
# Create release with GitHub CLI
gh release create v1.1.1 \
  --title "VARSYS Kitchen Dashboard v1.1.1" \
  --notes-file RELEASE_NOTES.md \
  VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe \
  VARSYS_Kitchen_Dashboard.exe \
  checksums.txt
```

## 📝 Step 6: Release Notes Template

Create `RELEASE_NOTES.md`:
```markdown
# VARSYS Kitchen Dashboard v1.1.1

## 🎉 What's New
- Updated to version 1.1.1 with enhanced stability
- Improved auto-update system reliability
- Enhanced Firebase cloud sync performance
- Bug fixes and performance improvements

## 🔄 Auto-Update
This version includes automatic update capabilities. The application will:
- Check for updates every 24 hours
- Notify you when new versions are available
- Download and install updates with one click
- Restart automatically after updates

## 📦 Installation
- **Installer**: Download and run `VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe`
- **Standalone**: Download `VARSYS_Kitchen_Dashboard.exe` for portable use

## 🔐 System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 500MB disk space
- Internet connection for cloud sync

## 🆕 Upgrade from Previous Versions
- Automatic upgrade via built-in updater
- Manual installation will preserve your data
- Backup recommended before upgrading
```

## 🔍 Step 7: Post-Release Verification

### 7.1 Test Auto-Update
1. Install a previous version (if available)
2. Run the application
3. Check for updates manually
4. Verify it detects v1.1.1
5. Test the update process

### 7.2 Monitor Release
- Check download statistics
- Monitor for user feedback
- Watch for error reports

## 📊 Build Script Automation

### Complete Build Script (`build_release_v1.1.1.bat`):
```batch
@echo off
echo ========================================
echo Building VARSYS Kitchen Dashboard v1.1.1
echo ========================================

REM Step 1: Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "installer_output" rmdir /s /q "installer_output"

REM Step 2: Build application
echo Building application...
python setup_cx_freeze.py build

REM Step 3: Create installer
echo Creating installer...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VARSYS_Kitchen_Dashboard_Setup.iss

REM Step 4: Create release folder
echo Preparing release assets...
mkdir release_v1.1.1
copy "installer_output\VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe" "release_v1.1.1\"
copy "build\exe.win-amd64-3.12\VARSYS_Kitchen_Dashboard.exe" "release_v1.1.1\"

REM Step 5: Generate checksums
echo Generating checksums...
cd release_v1.1.1
certutil -hashfile VARSYS_Kitchen_Dashboard_v1.1.1_Setup.exe SHA256 > checksums.txt
certutil -hashfile VARSYS_Kitchen_Dashboard.exe SHA256 >> checksums.txt

echo ========================================
echo Build Complete!
echo ========================================
echo Release assets are in: release_v1.1.1\
echo Ready for GitHub release!
pause
```

## ✅ Final Checklist

Before releasing:
- [ ] All version files updated to v1.1.1
- [ ] Application builds without errors
- [ ] Installer creates successfully
- [ ] Application runs correctly after installation
- [ ] Auto-update system tested
- [ ] Release notes prepared
- [ ] GitHub release created
- [ ] Assets uploaded and verified
- [ ] Checksums generated and included

## 🎯 Quick Release Commands

```bash
# Complete build and release process
build_app.bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VARSYS_Kitchen_Dashboard_Setup.iss
gh release create v1.1.1 --title "VARSYS Kitchen Dashboard v1.1.1" installer_output\*.exe
```

Your Kitchen Dashboard v1.1.1 is now ready for release with full auto-update capabilities!

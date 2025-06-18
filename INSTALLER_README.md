# VARSYS Kitchen Dashboard - Professional Windows Installer

This directory contains the Inno Setup configuration and build scripts to create a professional Windows installer for the Kitchen Dashboard application.

## 📋 Prerequisites

### 1. Inno Setup 6
Download and install Inno Setup 6 from: https://jrsoftware.org/isinfo.php

**Default Installation Path:** `C:\Program Files (x86)\Inno Setup 6\`

### 2. Completed cx_Freeze Build
Ensure you have successfully built the application using cx_Freeze:
```bash
python setup_fixed.py build
```

This should create the `build/exe.win-amd64-3.13/` directory with all application files.

## 🚀 Building the Installer

### Method 1: Using Batch Script (Windows)
```cmd
build_installer.bat
```

### Method 2: Using PowerShell Script (Recommended)
```powershell
.\build_installer.ps1
```

### Method 3: Manual Inno Setup Compilation
1. Open Inno Setup Compiler
2. Open `VARSYS_Kitchen_Dashboard_Setup.iss`
3. Click "Build" or press F9

## 📁 Output

The installer will be created in the `installer_output/` directory:
- **Filename:** `VARSYS_Kitchen_Dashboard_v1.0.5_Setup.exe`
- **Size:** Approximately 200-300 MB (includes all dependencies)

## 🎯 Installer Features

### Installation Options
- ✅ **Desktop Icon** - Creates desktop shortcut (optional)
- ✅ **Quick Launch Icon** - Adds to quick launch bar (optional)
- ✅ **Windows Startup** - Auto-start with Windows (optional)
- ✅ **Start Menu Group** - Creates program group in Start Menu

### What Gets Installed
- **Main Application** - VARSYS_Kitchen_Dashboard.exe
- **Python Runtime** - All required Python DLLs and libraries
- **Application Modules** - All custom modules and utilities
- **Data Directories** - Sample data, backups, logs, reports
- **Assets** - Icons, themes, and resources
- **Configuration Files** - Firebase config, settings, credentials
- **Documentation** - README, LICENSE, setup guides
- **Utilities** - Helper scripts and tools

### System Integration
- **File Associations** - Associates .kitchen files with the application
- **Registry Entries** - Proper Windows integration
- **Uninstaller** - Clean removal of all components
- **User Data Protection** - Preserves user data during uninstall

## 🔧 Customization

### Modifying the Installer

Edit `VARSYS_Kitchen_Dashboard_Setup.iss` to customize:

#### Application Information
```pascal
#define MyAppName "VARSYS Kitchen Dashboard"
#define MyAppVersion "1.0.5"
#define MyAppPublisher "VARSYS Technologies"
```

#### Installation Paths
```pascal
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
```

#### Additional Files
Add new files in the `[Files]` section:
```pascal
Source: "path\to\new\file"; DestDir: "{app}"; Flags: ignoreversion
```

#### Registry Entries
Add custom registry entries in the `[Registry]` section:
```pascal
Root: HKCU; Subkey: "SOFTWARE\MyApp"; ValueType: string; ValueName: "Setting"; ValueData: "Value"
```

### Build Script Paths

If Inno Setup is installed in a different location, update the path in the build scripts:

**build_installer.bat:**
```batch
set "INNO_SETUP_PATH=C:\Your\Custom\Path\ISCC.exe"
```

**build_installer.ps1:**
```powershell
$InnoSetupPath = "C:\Your\Custom\Path\ISCC.exe"
```

## 🛠️ Troubleshooting

### Common Issues

#### "Inno Setup not found"
- Install Inno Setup 6 from the official website
- Update the path in build scripts if installed elsewhere

#### "Build directory not found"
- Run `python setup_fixed.py build` first
- Ensure the build completed successfully

#### "Main executable not found"
- Check that `build/exe.win-amd64-3.13/VARSYS_Kitchen_Dashboard.exe` exists
- Verify the cx_Freeze build didn't have errors

#### "Access denied" during build
- Run the build script as Administrator
- Check that the output directory is writable

### Build Verification

After building, verify the installer:
1. **Size Check** - Should be 200-300 MB
2. **Test Installation** - Install on a clean system
3. **Functionality Test** - Ensure the app runs correctly
4. **Uninstall Test** - Verify clean removal

## 📦 Distribution

### Installer Properties
- **Digitally Signed** - Consider code signing for production
- **Virus Scanning** - Scan with antivirus before distribution
- **Compression** - Uses LZMA compression for smaller size
- **64-bit Only** - Requires 64-bit Windows 10 or later

### Deployment Options
- **Direct Download** - Host on website or file sharing
- **Package Managers** - Consider Chocolatey or Winget
- **Enterprise Deployment** - Use Group Policy or SCCM
- **Auto-Updates** - Implement update checking in the application

## 🔐 Security Considerations

### Code Signing (Recommended for Production)
```pascal
; Add to [Setup] section
SignTool=signtool
SignedUninstaller=yes
```

### Antivirus Compatibility
- The installer includes many Python libraries that may trigger false positives
- Consider submitting to antivirus vendors for whitelisting
- Use reputable code signing certificate

## 📋 Checklist

Before building the installer:
- [ ] cx_Freeze build completed successfully
- [ ] All required files are in build directory
- [ ] Inno Setup 6 is installed
- [ ] Version number is updated in .iss file
- [ ] License and README files are current
- [ ] Icon files exist in assets directory
- [ ] Firebase configuration is properly set up

After building the installer:
- [ ] Installer file is created in installer_output/
- [ ] File size is reasonable (200-300 MB)
- [ ] Test installation on clean system
- [ ] Verify all features work correctly
- [ ] Test uninstallation process
- [ ] Scan for viruses/malware

## 🎉 Success!

Once built successfully, you'll have a professional Windows installer that:
- Installs the complete Kitchen Dashboard application
- Integrates properly with Windows
- Provides a clean uninstall experience
- Includes all necessary dependencies
- Offers user-friendly installation options

The installer is ready for distribution to end users!

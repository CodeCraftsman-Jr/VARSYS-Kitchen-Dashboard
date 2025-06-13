# VARSYS Kitchen Dashboard - Version Update and Release Guide

## Overview

This guide explains how to update source files and release new versions of the VARSYS Kitchen Dashboard application efficiently and consistently.

## Quick Start

### For Simple Updates (Recommended)

```bash
# Check current version
release.bat current

# Increment patch version (1.0.0 -> 1.0.1)
release.bat patch

# Build and test
release.bat build

# Create full release
release.bat full 1.0.1
```

## Version Management System

### Version Format
- **Format**: `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- **MAJOR**: Breaking changes or major new features
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, small improvements

### Build Numbers
- **Format**: `YYYYMMDD` (e.g., 20250612)
- **Auto-generated**: Based on release date

## Available Tools

### 1. Batch Script (Easiest)
```bash
release.bat [command] [options]
```

**Commands:**
- `current` - Show current version
- `patch` - Increment patch version
- `minor` - Increment minor version  
- `major` - Increment major version
- `set 1.2.0` - Set specific version
- `build` - Build application only
- `release 1.2.0` - Prepare release with notes
- `full 1.2.0` - Complete release process

### 2. Python Scripts (Advanced)

#### Version Updater
```bash
python update_version.py [command] [options]
```

#### Release Automation
```bash
python release_automation.py [command] [options]
```

## Step-by-Step Release Process

### Method 1: Automated (Recommended)

1. **Update and Release in One Step**
   ```bash
   release.bat full 1.1.0
   ```

2. **Test the Release**
   - Navigate to `releases/` folder
   - Extract and test the ZIP package
   - Verify all features work correctly

3. **Commit to GitHub**
   ```bash
   git add .
   git commit -m "Release v1.1.0"
   git push origin main
   ```

4. **Create GitHub Release**
   - Go to GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag: `v1.1.0`
   - Upload the ZIP package from `releases/` folder

### Method 2: Manual Steps

1. **Update Version**
   ```bash
   release.bat set 1.1.0
   ```

2. **Build Application**
   ```bash
   release.bat build
   ```

3. **Create Package**
   ```bash
   python release_automation.py package 1.1.0
   ```

4. **Test and Release** (same as Method 1)

## File Structure After Release

```
VARSYS_COOKSUITE/
├── releases/
│   ├── VARSYS_Kitchen_Dashboard_v1.1.0.zip
│   ├── VARSYS_Kitchen_Dashboard_v1.1.0.checksums.txt
│   ├── install_v1.1.0.bat
│   └── release_info_v1.1.0.json
├── build/
│   └── exe.win-amd64-3.10/
├── RELEASE_NOTES_v1.1.0.md
└── [source files with updated versions]
```

## Files Updated Automatically

### Version Information
- `__version__.py` - Main version file
- `setup_cx_freeze.py` - Build configuration
- `manifest.json` - Application manifest

### Release Documentation
- `RELEASE_NOTES_v[version].md` - Generated release notes template
- `release_info_v[version].json` - Technical release information

## Customizing Release Notes

After running the release command, edit the generated release notes:

```markdown
# VARSYS Kitchen Dashboard v1.1.0

## What's New

### 🚀 New Features
- Added comprehensive logging system
- Enhanced error handling and recovery
- Improved debugging capabilities

### 🐛 Bug Fixes
- Fixed data loading issues in executable mode
- Resolved memory leaks in chart rendering

### 🔧 Improvements
- Better performance monitoring
- Enhanced user interface responsiveness
```

## GitHub Integration

### Setting Up Automatic Updates

1. **Update GitHub Repository URL** in `__version__.py`:
   ```python
   UPDATE_CHECK_URL = "https://api.github.com/repos/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/releases/latest"
   ```

2. **Configure Download URLs**:
   ```python
   DOWNLOAD_BASE_URL = "https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/releases/download"
   ```

### Creating GitHub Releases

1. **Tag Format**: `v1.1.0`
2. **Release Title**: `VARSYS Kitchen Dashboard v1.1.0`
3. **Upload Files**:
   - Main ZIP package
   - Installer batch file
   - Checksums file

## Testing Checklist

Before releasing, verify:

- [ ] Application starts without errors
- [ ] All main features work correctly
- [ ] Data loading functions properly
- [ ] Charts and visualizations display correctly
- [ ] Error handling works as expected
- [ ] Logs are generated properly
- [ ] Version information is correct in About dialog

## Troubleshooting

### Common Issues

1. **Build Fails**
   ```bash
   # Clean and retry
   python release_automation.py clean
   python release_automation.py build
   ```

2. **Version Not Updated**
   - Check `__version__.py` manually
   - Verify file permissions
   - Run version update again

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Getting Help

- Check the console output for detailed error messages
- Review log files in the `logs/` directory
- Verify all required files are present

## Best Practices

1. **Always test before releasing**
2. **Use semantic versioning consistently**
3. **Write meaningful release notes**
4. **Keep backup of working versions**
5. **Test on clean Windows systems**
6. **Verify checksums after upload**

## Advanced Configuration

### Custom Build Settings

Edit `setup_cx_freeze.py` for:
- Additional files to include
- Icon and metadata changes
- Optimization settings

### Version Flags

In `__version__.py`, configure:
- `RELEASE_TYPE` - alpha, beta, rc, stable
- `FIREBASE_ENABLED` - Enable/disable Firebase features
- `SUBSCRIPTION_REQUIRED` - Future subscription model

## Support

For issues with the release process:
1. Check this guide first
2. Review console error messages
3. Test individual steps manually
4. Contact development team if needed

---

© 2025 VARSYS Solutions. All rights reserved.

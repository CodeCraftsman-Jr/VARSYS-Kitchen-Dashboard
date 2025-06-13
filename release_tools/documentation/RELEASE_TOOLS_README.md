# VARSYS Kitchen Dashboard - Release Tools

## Overview

This directory contains comprehensive tools for managing versions and creating releases of the VARSYS Kitchen Dashboard application. All tools are cross-platform and work on Windows, Linux, and macOS.

## Available Tools

### 1. Cross-Platform Python Manager (Recommended)
**File**: `release_manager.py`
- ✅ Works on all operating systems
- ✅ Interactive menu interface
- ✅ Command-line interface
- ✅ No additional dependencies

### 2. Shell Script (Unix/Linux/macOS/Git Bash)
**File**: `release.sh`
- ✅ Works on Unix-like systems
- ✅ Works in Git Bash on Windows
- ✅ Simple command-line interface

### 3. Windows Batch Files
**Files**: `release.bat`, `release_menu.bat`, `🚀 Release Manager.bat`
- ✅ Works on Windows Command Prompt
- ✅ Interactive menu interface
- ⚠️ Windows only

### 4. PowerShell Script
**File**: `release.ps1`
- ✅ Works on Windows PowerShell
- ✅ Enhanced Windows integration
- ⚠️ Windows only

## Quick Start Guide

### Method 1: Interactive Menu (Easiest)

#### On Any System:
```bash
python release_manager.py
```

#### On Unix/Linux/macOS/Git Bash:
```bash
./release.sh menu
```

#### On Windows (Double-click):
- `🚀 Release Manager.bat`
- `release_menu.bat`

### Method 2: Command Line

#### Check Current Version:
```bash
# Python (works everywhere)
python release_manager.py current

# Shell script (Unix/Git Bash)
./release.sh current

# Windows batch
release.bat current

# PowerShell
.\release.ps1 current
```

#### Create a New Release:
```bash
# Python (works everywhere)
python release_manager.py full 1.0.4

# Shell script (Unix/Git Bash)
./release.sh full 1.0.4

# Windows batch
release.bat full 1.0.4

# PowerShell
.\release.ps1 full 1.0.4
```

## Complete Command Reference

### Version Management
| Action | Python | Shell | Batch | PowerShell |
|--------|--------|-------|-------|------------|
| Show current version | `python release_manager.py current` | `./release.sh current` | `release.bat current` | `.\release.ps1 current` |
| Increment patch (1.0.3→1.0.4) | `python release_manager.py patch` | `./release.sh patch` | `release.bat patch` | `.\release.ps1 patch` |
| Increment minor (1.0.3→1.1.0) | `python release_manager.py minor` | `./release.sh minor` | `release.bat minor` | `.\release.ps1 minor` |
| Increment major (1.0.3→2.0.0) | `python release_manager.py major` | `./release.sh major` | `release.bat major` | `.\release.ps1 major` |
| Set specific version | `python release_manager.py set 1.2.0` | `./release.sh set 1.2.0` | `release.bat set 1.2.0` | `.\release.ps1 set 1.2.0` |

### Build and Release
| Action | Python | Shell | Batch | PowerShell |
|--------|--------|-------|-------|------------|
| Build only | `python release_manager.py build` | `./release.sh build` | `release.bat build` | `.\release.ps1 build` |
| Full release | `python release_manager.py full 1.0.4` | `./release.sh full 1.0.4` | `release.bat full 1.0.4` | `.\release.ps1 full 1.0.4` |
| Clean build | `python release_manager.py clean` | `./release.sh clean` | `release.bat clean` | `.\release.ps1 clean` |

### Interactive Menu
| Action | Python | Shell | Batch | PowerShell |
|--------|--------|-------|-------|------------|
| Show menu | `python release_manager.py` | `./release.sh menu` | Double-click `🚀 Release Manager.bat` | `.\release.ps1` |

## Step-by-Step Release Process

### For Your Next Release (Version 1.0.4):

1. **Choose Your Tool**:
   - **Recommended**: `python release_manager.py` (works everywhere)
   - **Git Bash**: `./release.sh`
   - **Windows**: Double-click `🚀 Release Manager.bat`

2. **Run Full Release**:
   ```bash
   python release_manager.py full 1.0.4
   ```

3. **What Happens**:
   - Updates version in all files
   - Builds the executable
   - Creates ZIP package
   - Generates checksums
   - Creates release notes template

4. **Test the Release**:
   - Go to `releases/` folder
   - Extract `VARSYS_Kitchen_Dashboard_v1.0.4.zip`
   - Test the executable

5. **Upload to GitHub**:
   - Commit and push changes
   - Create GitHub release
   - Upload the ZIP file

## File Structure After Release

```
VARSYS_COOKSUITE/
├── releases/                                    ← Generated release files
│   ├── VARSYS_Kitchen_Dashboard_v1.0.4.zip    ← Main release package
│   ├── install_v1.0.4.bat                     ← Windows installer
│   ├── VARSYS_Kitchen_Dashboard_v1.0.4.checksums.txt
│   └── release_info_v1.0.4.json
├── build/                                       ← Build artifacts
│   └── exe.win-amd64-3.10/
├── RELEASE_NOTES_v1.0.4.md                    ← Edit this file
├── __version__.py                              ← Updated automatically
├── setup_cx_freeze.py                         ← Updated automatically
├── manifest.json                              ← Updated automatically
└── [release tools]
```

## Troubleshooting

### Problem: "Command not found" or "File not found"
**Solution**: Make sure you're in the right directory
```bash
cd "path/to/DashboardV4/VARSYS_COOKSUITE"
```

### Problem: "Python not found"
**Solution**: Install Python 3.x and make sure it's in your PATH
```bash
python --version  # Should show Python 3.x.x
```

### Problem: Permission denied (Unix/Linux)
**Solution**: Make the shell script executable
```bash
chmod +x release.sh
```

### Problem: Build fails
**Solution**: Clean and try again
```bash
python release_manager.py clean
python release_manager.py build
```

### Problem: Want to undo version change
**Solution**: Set back to previous version
```bash
python release_manager.py set 1.0.3
```

## Which Tool Should I Use?

### For Beginners:
- **Windows**: Double-click `🚀 Release Manager.bat`
- **Mac/Linux**: `python release_manager.py`

### For Command Line Users:
- **Any System**: `python release_manager.py [command]`
- **Git Bash/Unix**: `./release.sh [command]`

### For Windows Power Users:
- **Command Prompt**: `release.bat [command]`
- **PowerShell**: `.\release.ps1 [command]`

## Examples

### Example 1: Quick Bug Fix Release
```bash
# Make your code changes first, then:
python release_manager.py patch        # 1.0.3 → 1.0.4
python release_manager.py build        # Build and test
python release_manager.py full 1.0.4   # Create full release
```

### Example 2: New Feature Release
```bash
# Make your code changes first, then:
python release_manager.py minor        # 1.0.3 → 1.1.0
python release_manager.py full 1.1.0   # Create full release
```

### Example 3: Interactive Release
```bash
python release_manager.py              # Shows interactive menu
# Choose option 7 (Create Full Release)
# Enter version: 1.0.4
# Wait for completion
```

## Support

If you encounter any issues:
1. Check this README first
2. Try the interactive menu: `python release_manager.py`
3. Check the console output for error messages
4. Make sure all required files are present
5. Verify Python is installed and accessible

---

All tools are designed to be simple and reliable. Choose the one that works best for your environment!

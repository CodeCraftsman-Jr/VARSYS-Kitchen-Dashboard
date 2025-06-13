# VARSYS Kitchen Dashboard - Release Tools

## 📁 Organized File Structure

The release tools are now organized by category for better maintainability:

```
release_tools/
├── scripts/                    # Core Python scripts
│   ├── update_version.py      # Version management
│   ├── release_automation.py  # Build and packaging automation
│   └── release_manager.py     # Cross-platform interactive manager
├── windows/                   # Windows-specific tools
│   ├── release.bat           # Windows batch script
│   ├── release.ps1           # PowerShell script
│   ├── release_menu.bat      # Interactive menu for Windows
│   └── Release_Manager.bat   # Windows launcher
├── unix/                     # Unix/Linux/macOS tools
│   └── release.sh           # Shell script for Unix systems
├── documentation/           # Documentation files
│   ├── VERSION_UPDATE_GUIDE.md
│   └── RELEASE_TOOLS_README.md
└── README.md               # This file
```

## 🚀 Quick Start

### From Main Directory (Recommended)

```bash
# From VARSYS_COOKSUITE directory:

# Cross-platform Python launcher
python release.py current
python release.py patch
python release.py full 1.0.4

# Interactive menu
python release.py

# Unix/Linux/macOS
./release.sh current
./release.sh full 1.0.4
```

### Direct Access to Tools

#### Python Scripts (Cross-Platform)
```bash
cd release_tools
python scripts/release_manager.py current
python scripts/release_manager.py full 1.0.4
python scripts/release_manager.py  # Interactive menu
```

#### Windows Tools
```cmd
cd release_tools\windows
release.bat current
release.bat full 1.0.4

# Or double-click Release_Manager.bat for interactive menu
```

#### Unix/Linux/macOS Tools
```bash
cd release_tools/unix
./release.sh current
./release.sh full 1.0.4
```

## 📋 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `current` | Show current version | `python release.py current` |
| `patch` | Increment patch version (1.0.3→1.0.4) | `python release.py patch` |
| `minor` | Increment minor version (1.0.3→1.1.0) | `python release.py minor` |
| `major` | Increment major version (1.0.3→2.0.0) | `python release.py major` |
| `set X.Y.Z` | Set specific version | `python release.py set 1.2.0` |
| `build` | Build application only | `python release.py build` |
| `full X.Y.Z` | Complete release process | `python release.py full 1.0.4` |
| `clean` | Clean build directories | `python release.py clean` |
| `help` | Show help information | `python release.py help` |

## 🔧 Core Scripts Description

### scripts/update_version.py
- Updates version numbers in all project files
- Manages `__version__.py`, `setup_cx_freeze.py`, `manifest.json`
- Handles semantic versioning (major.minor.patch)
- Generates build numbers based on date

### scripts/release_automation.py
- Automates the complete build process
- Creates executable using cx_Freeze
- Packages application into ZIP files
- Generates checksums and release information
- Creates installer scripts

### scripts/release_manager.py
- Cross-platform interactive interface
- Provides both command-line and menu-driven interfaces
- Coordinates between update_version.py and release_automation.py
- Works on Windows, Linux, and macOS

## 🖥️ Platform-Specific Tools

### Windows Tools (windows/)
- **release.bat**: Command-line interface for Windows
- **release.ps1**: PowerShell version with enhanced features
- **release_menu.bat**: Interactive menu system
- **Release_Manager.bat**: Double-click launcher

### Unix Tools (unix/)
- **release.sh**: Shell script for Linux/macOS/Git Bash
- Works with bash, zsh, and other POSIX shells
- Includes error checking and colored output

## 📚 Documentation (documentation/)
- **VERSION_UPDATE_GUIDE.md**: Comprehensive version management guide
- **RELEASE_TOOLS_README.md**: Detailed tool usage instructions

## 🎯 Typical Workflow

### For Bug Fixes (Patch Release)
```bash
# 1. Make your code changes
# 2. Update version and create release
python release.py patch
python release.py full 1.0.4

# 3. Test the generated ZIP file
# 4. Upload to GitHub releases
```

### For New Features (Minor Release)
```bash
# 1. Make your code changes
# 2. Update version and create release
python release.py minor
python release.py full 1.1.0

# 3. Test and release
```

### For Major Updates
```bash
# 1. Make your code changes
# 2. Update version and create release
python release.py major
python release.py full 2.0.0

# 3. Test and release
```

## 🔍 What Gets Updated Automatically

When you run version updates, these files are automatically modified:
- `__version__.py` - Main version information
- `setup_cx_freeze.py` - Build configuration
- `manifest.json` - Application manifest
- Generated release notes template

## 📦 What Gets Generated

When you run a full release, these files are created:
- `releases/VARSYS_Kitchen_Dashboard_vX.Y.Z.zip` - Main release package
- `releases/install_vX.Y.Z.bat` - Windows installer
- `releases/VARSYS_Kitchen_Dashboard_vX.Y.Z.checksums.txt` - File verification
- `releases/release_info_vX.Y.Z.json` - Technical release information
- `RELEASE_NOTES_vX.Y.Z.md` - Release notes template

## 🛠️ Troubleshooting

### Common Issues
1. **"Python not found"**: Install Python 3.x and add to PATH
2. **"Scripts not found"**: Make sure you're in the correct directory
3. **"Permission denied"**: On Unix systems, run `chmod +x release.sh`
4. **Build fails**: Run `python release.py clean` then try again

### Getting Help
- Run `python release.py help` for command-line help
- Run `python release.py` for interactive menu
- Check the documentation folder for detailed guides

## 🎉 Benefits of This Organization

- **Clear separation** of platform-specific tools
- **Easy maintenance** with categorized files
- **Better documentation** organization
- **Simplified access** through main launchers
- **Cross-platform compatibility** maintained

---

Choose the tool that works best for your platform and workflow!

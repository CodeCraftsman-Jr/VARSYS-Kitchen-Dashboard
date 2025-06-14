# 🧹 Sample Data Cleanup Guide

This guide explains how to remove sample data that was generated during testing of the Kitchen Dashboard application.

## 📋 Available Cleanup Options

### 1. 🚀 Quick Automated Cleanup (Recommended)
**File:** `auto_cleanup.py`
```bash
python auto_cleanup.py
```
**What it removes:**
- Test data directory (`tests/data/`)
- Test report files (`test_report_*.txt`)
- Backup directories (`data_backup_*`)
- Temporary test files (`*.tmp`)

**Safe to use:** ✅ Only removes test-generated files

---

### 2. 🎯 Interactive Cleanup
**File:** `quick_cleanup.py`
```bash
python quick_cleanup.py
```
**What it does:**
- Removes test data automatically
- Asks before removing main data files
- Gives you control over what to clean

**Safe to use:** ✅ Asks for confirmation before removing main data

---

### 3. 🔧 Comprehensive Cleanup
**File:** `cleanup_sample_data.py`
```bash
python cleanup_sample_data.py
```
**Features:**
- Interactive menu with multiple options
- Backup creation before cleanup
- Selective category cleanup
- Complete data reset options

**Options available:**
1. Remove ALL sample data (complete cleanup)
2. Remove specific data categories
3. Show current data files
4. Backup data before cleanup
5. Remove only test-generated files
6. Reset to empty state (keep structure)

---

### 4. 🔄 Complete Data Reset
**File:** `reset_data.py`
```bash
python reset_data.py
```
**What it does:**
- ⚠️ **WARNING:** Removes ALL your data
- Creates backup before reset
- Resets all CSV files to empty state with headers
- Resets JSON configuration files

**Use when:** You want to start completely fresh

---

### 5. 🖱️ GUI Cleanup (In Application)
**Location:** Testing Menu → "Cleanup Sample Data"

**Features:**
- User-friendly dialog interface
- Radio button options for cleanup type
- Backup checkbox option
- Integrated with application

---

### 6. 💻 Windows Batch File
**File:** `cleanup_sample_data.bat`
```cmd
cleanup_sample_data.bat
```
**What it does:**
- Windows-friendly cleanup script
- Checks for Python installation
- Runs the quick cleanup utility

---

## 🎯 Recommended Cleanup Workflow

### For Regular Testing Cleanup:
```bash
# Quick and safe - removes only test files
python auto_cleanup.py
```

### For Selective Cleanup:
```bash
# Interactive menu with options
python cleanup_sample_data.py
```

### For Complete Fresh Start:
```bash
# Complete reset (creates backup first)
python reset_data.py
```

## 📁 What Gets Cleaned Up

### Test Files (Safe to Remove):
- `tests/data/` - Test data directory
- `test_report_*.txt` - Test execution reports
- `data_backup_*` - Old backup directories
- `*.tmp` - Temporary files

### Sample Data Files (Main Data):
- `inventory.csv` - Sample inventory items
- `recipes.csv` - Sample recipes
- `sales.csv` - Sample sales data
- `shopping_list.csv` - Sample shopping items
- `meal_plan.csv` - Sample meal plans
- And other CSV data files...

### Configuration Files:
- `notifications.json` - Sample notifications
- `activities.json` - Sample activity logs
- `gas_cost_config.json` - Gas cost settings

## 🛡️ Safety Features

### Automatic Backups:
- Most scripts offer backup creation
- Backups are timestamped
- Located in `data_backup_YYYYMMDD_HHMMSS/`

### Confirmation Prompts:
- Scripts ask for confirmation before major changes
- Type 'YES' for destructive operations
- 'y/N' prompts default to No for safety

### Selective Cleanup:
- Choose specific categories to clean
- Preview what will be removed
- Cancel at any time

## 🚨 Important Notes

1. **Always backup important data** before running cleanup scripts
2. **Test files are safe to remove** - they don't affect your real data
3. **Main data cleanup is irreversible** without backups
4. **The application will recreate empty files** when needed
5. **Configuration files will be reset** to defaults

## 🔧 Troubleshooting

### Python Not Found:
```bash
# Check Python installation
python --version

# Or try
python3 --version
```

### Permission Errors:
- Run as administrator on Windows
- Check file permissions on Linux/Mac
- Close the Kitchen Dashboard app before cleanup

### Backup Failures:
- Check available disk space
- Ensure write permissions in project directory
- Close any open files in the data directory

## 📞 Need Help?

If you encounter issues:
1. Check the console output for error messages
2. Ensure the Kitchen Dashboard app is closed
3. Try running as administrator
4. Check file permissions and disk space

---

**Happy Cleaning! 🧹✨**

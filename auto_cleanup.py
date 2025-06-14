#!/usr/bin/env python3
"""
Automated Sample Data Cleanup
Automatically removes test-generated sample data
"""

import os
import shutil
import glob

def auto_cleanup():
    """Automatically cleanup test data"""
    print("🧹 Automated Sample Data Cleanup")
    print("=" * 40)
    
    removed_count = 0
    
    # 1. Remove test data directory
    tests_data_dir = os.path.join('tests', 'data')
    if os.path.exists(tests_data_dir):
        try:
            shutil.rmtree(tests_data_dir)
            print(f"✅ Removed: {tests_data_dir}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {tests_data_dir}: {e}")
    
    # 2. Remove test report files
    test_reports = glob.glob('test_report_*.txt')
    for report in test_reports:
        try:
            os.remove(report)
            print(f"✅ Removed: {report}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {report}: {e}")
    
    # 3. Remove backup directories
    backup_dirs = glob.glob('data_backup_*')
    for backup_dir in backup_dirs:
        try:
            if os.path.isdir(backup_dir):
                shutil.rmtree(backup_dir)
                print(f"✅ Removed: {backup_dir}")
                removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {backup_dir}: {e}")
    
    # 4. Remove temporary test files
    temp_files = glob.glob('test_*.tmp') + glob.glob('*.tmp')
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            print(f"✅ Removed: {temp_file}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {temp_file}: {e}")
    
    print(f"\n📊 Cleanup Summary: {removed_count} items removed")
    
    if removed_count > 0:
        print("✅ Test data cleanup completed!")
    else:
        print("ℹ️  No test data found to clean up")
    
    return removed_count

if __name__ == "__main__":
    auto_cleanup()

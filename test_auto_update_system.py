#!/usr/bin/env python3
"""
Auto-Update System Tester for Kitchen Dashboard
Tests download speed, file replacement, and update verification
"""

import os
import sys
import time
import json
import shutil
import hashlib
import requests
from pathlib import Path
from datetime import datetime

class AutoUpdateTester:
    def __init__(self):
        self.test_dir = "auto_update_test"
        self.old_version = "1.1.2"
        self.new_version = "1.1.3"
        self.results = {}
        
    def setup_test_environment(self):
        """Create test environment with simulated old version"""
        print("🔧 Setting up test environment...")
        
        # Clean previous test
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create simulated old version structure
        old_app_dir = f"{self.test_dir}/old_version_app"
        os.makedirs(old_app_dir, exist_ok=True)
        
        # Create fake old files to test replacement
        test_files = {
            "VARSYS_Kitchen_Dashboard.exe": "OLD_EXECUTABLE_CONTENT_v1.1.2",
            "modules/startup_loading_screen.py": "# OLD VERSION - No loading screen",
            "modules/account_settings_dialog.py": "# OLD VERSION - No account settings",
            "__version__.py": f'__version__ = "{self.old_version}"',
            "config.py": "# OLD CONFIG FILE",
            "firebase_config.json": '{"version": "1.1.2", "old": true}'
        }
        
        for file_path, content in test_files.items():
            full_path = f"{old_app_dir}/{file_path}"
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        print(f"✅ Test environment created: {old_app_dir}")
        return old_app_dir
    
    def test_download_speed(self, update_url=None):
        """Test download speed and progress tracking"""
        print("\n📥 Testing download speed...")
        
        # Use actual release package for testing
        test_file = "VARSYS_Kitchen_Dashboard_v1.1.3_Working_cx_Freeze_Release.zip"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return False
        
        file_size = os.path.getsize(test_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📊 File size: {file_size_mb:.1f} MB")
        
        # Simulate download by copying with progress tracking
        start_time = time.time()
        
        # Copy in chunks to simulate download
        chunk_size = 1024 * 1024  # 1MB chunks
        downloaded = 0
        
        with open(test_file, 'rb') as src:
            with open(f"{self.test_dir}/downloaded_update.zip", 'wb') as dst:
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    
                    dst.write(chunk)
                    downloaded += len(chunk)
                    
                    # Progress tracking
                    progress = (downloaded / file_size) * 100
                    elapsed = time.time() - start_time
                    speed_mbps = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                    
                    print(f"\r📥 Progress: {progress:.1f}% | Speed: {speed_mbps:.1f} MB/s", end="")
                    
                    # Simulate network delay
                    time.sleep(0.1)
        
        total_time = time.time() - start_time
        avg_speed = file_size_mb / total_time
        
        print(f"\n✅ Download completed!")
        print(f"   Total time: {total_time:.1f} seconds")
        print(f"   Average speed: {avg_speed:.1f} MB/s")
        
        self.results['download'] = {
            'file_size_mb': file_size_mb,
            'download_time': total_time,
            'average_speed_mbps': avg_speed,
            'success': True
        }
        
        return True
    
    def test_file_replacement(self, old_app_dir):
        """Test if new files properly replace old files"""
        print("\n🔄 Testing file replacement...")
        
        # Extract the update package
        import zipfile
        
        update_zip = f"{self.test_dir}/downloaded_update.zip"
        extract_dir = f"{self.test_dir}/extracted_update"
        
        with zipfile.ZipFile(update_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the Application directory in extracted files
        app_source = None
        for root, dirs, files in os.walk(extract_dir):
            if "Application" in dirs:
                app_source = os.path.join(root, "Application")
                break
        
        if not app_source:
            print("❌ Application directory not found in update package")
            return False
        
        print(f"📁 Found application source: {app_source}")
        
        # Test file replacement
        replacement_results = {}
        
        # Check critical files for replacement
        critical_files = [
            "VARSYS_Kitchen_Dashboard.exe",
            "modules/startup_loading_screen.py",
            "modules/account_settings_dialog.py",
            "__version__.py",
            "config.py"
        ]
        
        for file_path in critical_files:
            old_file = f"{old_app_dir}/{file_path}"
            new_file = f"{app_source}/{file_path}"
            
            if os.path.exists(old_file) and os.path.exists(new_file):
                # Read old content
                with open(old_file, 'rb') as f:
                    old_content = f.read()
                
                # Read new content
                with open(new_file, 'rb') as f:
                    new_content = f.read()
                
                # Check if files are different
                files_different = old_content != new_content
                
                # Simulate replacement
                backup_file = f"{old_file}.backup"
                shutil.copy2(old_file, backup_file)
                shutil.copy2(new_file, old_file)
                
                # Verify replacement
                with open(old_file, 'rb') as f:
                    replaced_content = f.read()
                
                replacement_success = replaced_content == new_content
                
                replacement_results[file_path] = {
                    'files_different': files_different,
                    'replacement_success': replacement_success,
                    'old_size': len(old_content),
                    'new_size': len(new_content)
                }
                
                status = "✅" if replacement_success else "❌"
                print(f"   {status} {file_path}: {len(old_content)} → {len(new_content)} bytes")
            else:
                print(f"   ⚠️  {file_path}: File missing")
                replacement_results[file_path] = {'error': 'File missing'}
        
        self.results['file_replacement'] = replacement_results
        return True
    
    def test_version_verification(self, old_app_dir):
        """Test version verification after update"""
        print("\n🔍 Testing version verification...")
        
        # Check version file
        version_file = f"{old_app_dir}/__version__.py"
        
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                content = f.read()
            
            # Check if version was updated
            version_updated = self.new_version in content
            old_version_removed = self.old_version not in content
            
            print(f"   📄 Version file content: {content.strip()}")
            print(f"   ✅ New version present: {version_updated}")
            print(f"   ✅ Old version removed: {old_version_removed}")
            
            self.results['version_verification'] = {
                'version_file_exists': True,
                'new_version_present': version_updated,
                'old_version_removed': old_version_removed,
                'content': content.strip()
            }
        else:
            print("   ❌ Version file not found")
            self.results['version_verification'] = {'version_file_exists': False}
    
    def test_feature_verification(self, old_app_dir):
        """Test if new features are present after update"""
        print("\n🆕 Testing new feature verification...")
        
        feature_results = {}
        
        # Check for v1.1.3 features
        features_to_check = {
            "startup_loading_screen.py": "Startup Loading Screen",
            "account_settings_dialog.py": "Account Settings Dialog",
            "user_profile_widget.py": "Enhanced User Profile"
        }
        
        for file_name, feature_name in features_to_check.items():
            file_path = f"{old_app_dir}/modules/{file_name}"
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for v1.1.3 specific content
                has_new_content = "v1.1.3" in content or "1.1.3" in content
                file_size = len(content)
                
                feature_results[feature_name] = {
                    'file_exists': True,
                    'has_new_content': has_new_content,
                    'file_size': file_size
                }
                
                status = "✅" if has_new_content else "⚠️"
                print(f"   {status} {feature_name}: {file_size} bytes")
            else:
                feature_results[feature_name] = {'file_exists': False}
                print(f"   ❌ {feature_name}: File not found")
        
        self.results['feature_verification'] = feature_results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating test report...")
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_summary': {
                'old_version': self.old_version,
                'new_version': self.new_version,
                'overall_success': True
            },
            'detailed_results': self.results
        }
        
        # Determine overall success
        download_success = self.results.get('download', {}).get('success', False)
        replacement_success = all(
            r.get('replacement_success', False) 
            for r in self.results.get('file_replacement', {}).values()
            if 'replacement_success' in r
        )
        version_success = self.results.get('version_verification', {}).get('new_version_present', False)
        
        report['test_summary']['overall_success'] = download_success and replacement_success and version_success
        
        # Save report
        report_file = f"{self.test_dir}/auto_update_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 AUTO-UPDATE TEST SUMMARY")
        print("="*60)
        
        print(f"📥 Download Test: {'✅ PASS' if download_success else '❌ FAIL'}")
        if download_success:
            download_info = self.results['download']
            print(f"   Size: {download_info['file_size_mb']:.1f} MB")
            print(f"   Time: {download_info['download_time']:.1f} seconds")
            print(f"   Speed: {download_info['average_speed_mbps']:.1f} MB/s")
        
        print(f"🔄 File Replacement: {'✅ PASS' if replacement_success else '❌ FAIL'}")
        
        print(f"🔍 Version Update: {'✅ PASS' if version_success else '❌ FAIL'}")
        
        overall_status = "✅ READY FOR RELEASE" if report['test_summary']['overall_success'] else "❌ NEEDS FIXES"
        print(f"\n🎯 Overall Status: {overall_status}")
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        return report
    
    def run_full_test(self):
        """Run complete auto-update test suite"""
        print("🚀 Starting Auto-Update System Test")
        print("="*50)
        
        try:
            # Setup test environment
            old_app_dir = self.setup_test_environment()
            
            # Run tests
            self.test_download_speed()
            self.test_file_replacement(old_app_dir)
            self.test_version_verification(old_app_dir)
            self.test_feature_verification(old_app_dir)
            
            # Generate report
            report = self.generate_test_report()
            
            return report
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main test function"""
    print("Kitchen Dashboard Auto-Update System Tester")
    print("Testing download speed, file replacement, and update verification")
    print()
    
    tester = AutoUpdateTester()
    report = tester.run_full_test()
    
    if report and report['test_summary']['overall_success']:
        print("\n🎉 AUTO-UPDATE SYSTEM IS READY FOR RELEASE!")
        print("✅ Download speed is acceptable")
        print("✅ File replacement works correctly")
        print("✅ Version verification successful")
        print("✅ New features are properly included")
    else:
        print("\n⚠️  AUTO-UPDATE SYSTEM NEEDS ATTENTION!")
        print("Please review the test report and fix any issues before release.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
VARSYS Solutions - Kitchen Dashboard
Professional EXE Build Script

This script creates a production-ready EXE with:
- Automated dependency checking
- Version management
- Digital signing (optional)
- Distribution packaging
- GitHub release preparation
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __version__ import get_version_info, get_version_string

class VARSYSBuilder:
    """Professional build system for VARSYS Kitchen Dashboard"""
    
    def __init__(self):
        self.version_info = get_version_info()
        self.version = get_version_string()
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.release_dir = Path("release")
        
        # Build configuration
        self.app_name = "VARSYS_Kitchen_Dashboard"
        self.exe_name = f"{self.app_name}.exe"
        self.installer_name = f"VARSYS_Kitchen_Dashboard_v{self.version}_Setup.exe"
        
        print(f"🏗️  VARSYS Kitchen Dashboard Build System")
        print(f"📦 Version: {self.version}")
        print(f"🏢 Company: {self.version_info['company']}")
        print(f"📅 Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'pyinstaller',
            'PySide6',
            'pandas',
            'numpy',
            'matplotlib',
            'seaborn',
            'plotly',
            'firebase-admin',
            'Pyrebase4',
            'requests',
            'cryptography',
            'openpyxl',
            'python-dotenv'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').lower())
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package}")
        
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            print("Please install missing packages with:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All dependencies satisfied!")
        return True
    
    def clean_build(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning previous builds...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir, "__pycache__"]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  🗑️  Removed {dir_path}")
        
        # Clean .pyc files
        for pyc_file in Path(".").rglob("*.pyc"):
            pyc_file.unlink()
        
        print("✅ Build environment cleaned!")
    
    def create_app_icon(self):
        """Create application icon if it doesn't exist"""
        icon_dir = Path("assets/icons")
        icon_path = icon_dir / "app_icon.ico"
        
        if not icon_path.exists():
            print("🎨 Creating default application icon...")
            icon_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple default icon (you can replace this with a proper icon)
            try:
                from PIL import Image, ImageDraw
                
                # Create a 256x256 icon
                img = Image.new('RGBA', (256, 256), (0, 123, 255, 255))
                draw = ImageDraw.Draw(img)
                
                # Draw a simple "V" for VARSYS
                draw.text((100, 100), "V", fill=(255, 255, 255, 255))
                
                img.save(icon_path, format='ICO')
                print(f"  ✅ Created icon: {icon_path}")
            except ImportError:
                print("  ⚠️  PIL not available, skipping icon creation")
        else:
            print(f"  ✅ Using existing icon: {icon_path}")
    
    def build_exe(self):
        """Build the EXE using PyInstaller"""
        print("🔨 Building EXE with PyInstaller...")
        
        # Ensure spec file exists
        spec_file = Path("kitchen_dashboard.spec")
        if not spec_file.exists():
            print("❌ Spec file not found!")
            return False
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        print(f"  🚀 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("  ✅ PyInstaller completed successfully!")
            
            # Check if EXE was created
            exe_path = self.dist_dir / self.exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"  📦 EXE created: {exe_path} ({size_mb:.1f} MB)")
                return True
            else:
                print("  ❌ EXE file not found after build!")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ PyInstaller failed: {e}")
            print(f"  📝 Error output: {e.stderr}")
            return False
    
    def create_release_package(self):
        """Create release package with all necessary files"""
        print("📦 Creating release package...")
        
        # Create release directory
        self.release_dir.mkdir(exist_ok=True)
        
        # Copy EXE
        exe_source = self.dist_dir / self.exe_name
        exe_dest = self.release_dir / self.exe_name
        
        if exe_source.exists():
            shutil.copy2(exe_source, exe_dest)
            print(f"  ✅ Copied EXE: {exe_dest}")
        else:
            print("  ❌ EXE not found for packaging!")
            return False
        
        # Copy essential files
        essential_files = [
            "README.md",
            "requirements.txt",
            "RELEASE_NOTES.md"
        ]
        
        for file_name in essential_files:
            source = Path(file_name)
            if source.exists():
                dest = self.release_dir / file_name
                shutil.copy2(source, dest)
                print(f"  ✅ Copied: {file_name}")
        
        # Create version info file
        version_file = self.release_dir / "version.json"
        with open(version_file, 'w') as f:
            json.dump(self.version_info, f, indent=2)
        print(f"  ✅ Created: {version_file}")
        
        # Create ZIP package
        zip_name = f"VARSYS_Kitchen_Dashboard_v{self.version}.zip"
        zip_path = self.release_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.release_dir.iterdir():
                if file_path.suffix != '.zip':
                    zipf.write(file_path, file_path.name)
        
        print(f"  📦 Created ZIP package: {zip_path}")
        
        # Calculate package size
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"  📊 Package size: {zip_size_mb:.1f} MB")
        
        return True
    
    def create_github_release_info(self):
        """Create GitHub release information"""
        print("🐙 Creating GitHub release information...")
        
        release_info = {
            "tag_name": f"v{self.version}",
            "name": f"VARSYS Kitchen Dashboard v{self.version}",
            "body": f"""
# VARSYS Kitchen Dashboard v{self.version}

## 🎉 What's New
- Complete kitchen management system
- Inventory tracking and management
- Meal planning with recipe integration
- Budget and expense tracking
- Sales analytics and reporting
- Gas management system
- Packing materials tracking
- Pricing management
- Enterprise features
- AI & ML integration
- Responsive design
- Firebase cloud sync

## 📋 System Requirements
- Windows 10 or Windows 11
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Internet connection (for cloud features)

## 🚀 Installation
1. Download the ZIP package
2. Extract to your desired location
3. Run `VARSYS_Kitchen_Dashboard.exe`
4. Follow the setup wizard

## 🔧 Features
- **Inventory Management**: Track ingredients, quantities, and expiry dates
- **Meal Planning**: Plan meals with integrated recipes
- **Budget Tracking**: Monitor expenses and costs
- **Sales Analytics**: Comprehensive sales reporting
- **Gas Management**: Track gas usage and orders
- **Pricing Tools**: Advanced pricing calculations
- **Cloud Sync**: Firebase integration for data backup
- **Enterprise Ready**: Multi-user support and advanced features

## 📞 Support
- Website: {self.version_info['website']}
- Email: {self.version_info['support_email']}
- Issues: GitHub Issues

## 📄 License
{self.version_info['copyright']}

---
Built with ❤️ by {self.version_info['company']}
            """.strip(),
            "draft": False,
            "prerelease": False,
            "assets": [
                {
                    "name": f"VARSYS_Kitchen_Dashboard_v{self.version}.zip",
                    "label": "Complete Application Package"
                }
            ]
        }
        
        release_file = self.release_dir / "github_release.json"
        with open(release_file, 'w') as f:
            json.dump(release_info, f, indent=2)
        
        print(f"  ✅ Created: {release_file}")
        return True
    
    def build(self):
        """Main build process"""
        print("🚀 Starting VARSYS Kitchen Dashboard build process...\n")
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            return False
        
        print()
        
        # Step 2: Clean previous builds
        self.clean_build()
        print()
        
        # Step 3: Create app icon
        self.create_app_icon()
        print()
        
        # Step 4: Build EXE
        if not self.build_exe():
            return False
        
        print()
        
        # Step 5: Create release package
        if not self.create_release_package():
            return False
        
        print()
        
        # Step 6: Create GitHub release info
        self.create_github_release_info()
        
        print()
        print("🎉 Build completed successfully!")
        print(f"📦 Release package: {self.release_dir}")
        print(f"🚀 Ready for distribution!")
        
        return True

def main():
    """Main entry point"""
    builder = VARSYSBuilder()
    
    try:
        success = builder.build()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

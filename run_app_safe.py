#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe launcher for VARSYS Kitchen Dashboard
Handles Unicode encoding issues on Windows
"""

import os
import sys
import locale

def setup_unicode_environment():
    """Setup proper Unicode environment for Windows"""
    try:
        # Set UTF-8 encoding for stdout/stderr
        if sys.platform.startswith('win'):
            # Try to set console to UTF-8
            try:
                os.system('chcp 65001 >nul 2>&1')
            except:
                pass
            
            # Set environment variables for UTF-8
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['PYTHONUTF8'] = '1'
            
            # Try to set locale
            try:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            except:
                try:
                    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                except:
                    pass
        
        print("Unicode environment setup completed")
        return True
        
    except Exception as e:
        print(f"Warning: Could not setup Unicode environment: {e}")
        return False

def main():
    """Main launcher function"""
    print("VARSYS Kitchen Dashboard - Safe Launcher")
    print("=" * 50)
    
    # Setup Unicode environment
    setup_unicode_environment()
    
    try:
        # Import and run the main application
        print("Starting Kitchen Dashboard...")

        # Import the main application
        from kitchen_app import KitchenDashboardApp
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt

        # Set Qt attributes before QApplication creation to avoid warnings
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create and show the main window
        window = KitchenDashboardApp()
        window.show()
        
        # Run the application
        sys.exit(app.exec())
        
    except UnicodeEncodeError as e:
        print(f"Unicode encoding error: {e}")
        print("This is a Windows terminal encoding issue.")
        print("The application should still work normally in the GUI.")
        
        # Try to continue anyway
        try:
            from kitchen_app import KitchenDashboardApp
            from PySide6.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            window = KitchenDashboardApp()
            window.show()
            sys.exit(app.exec())
        except Exception as e2:
            print(f"Failed to start application: {e2}")
            return 1
            
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

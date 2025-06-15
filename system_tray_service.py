#!/usr/bin/env python3
"""
VARSYS Kitchen Dashboard System Tray Service
Provides background operation, auto-startup, and system tray integration
"""

import sys
import os
import subprocess
import winreg
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PySide6.QtGui import QIcon, QAction

class KitchenDashboardService:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set up system tray
        self.setup_system_tray()
        
        # Set up auto-startup
        self.setup_auto_startup()
        
        # Main application process
        self.main_app_process = None
        
        # Timer for checking main app status
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_main_app)
        self.check_timer.start(5000)  # Check every 5 seconds

    def setup_system_tray(self):
        """Set up the system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            sys.exit(1)

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        
        # Set icon
        icon_path = Path("assets/icons/vasanthkitchen.ico")
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # Fallback icon
            self.tray_icon.setIcon(self.app.style().standardIcon(
                self.app.style().SP_ComputerIcon))

        # Create context menu
        self.create_tray_menu()
        
        # Set tooltip
        self.tray_icon.setToolTip("VARSYS Kitchen Dashboard")
        
        # Connect double-click to show main app
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()

    def create_tray_menu(self):
        """Create the system tray context menu"""
        menu = QMenu()
        
        # Open Kitchen Dashboard
        open_action = QAction("Open Kitchen Dashboard", None)
        open_action.triggered.connect(self.show_main_app)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings", None)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # Auto-startup toggle
        self.auto_startup_action = QAction("Auto-startup", None)
        self.auto_startup_action.setCheckable(True)
        self.auto_startup_action.setChecked(self.is_auto_startup_enabled())
        self.auto_startup_action.triggered.connect(self.toggle_auto_startup)
        menu.addAction(self.auto_startup_action)
        
        menu.addSeparator()
        
        # About
        about_action = QAction("About", None)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        # Exit
        exit_action = QAction("Exit", None)
        exit_action.triggered.connect(self.exit_application)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)

    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_app()

    def show_main_app(self):
        """Launch or show the main Kitchen Dashboard application"""
        if self.main_app_process is None or self.main_app_process.poll() is not None:
            # Launch main application
            exe_path = Path("VARSYS_Kitchen_Dashboard.exe")
            if exe_path.exists():
                try:
                    self.main_app_process = subprocess.Popen([str(exe_path)])
                    self.tray_icon.showMessage(
                        "Kitchen Dashboard",
                        "Application started successfully",
                        QSystemTrayIcon.Information,
                        3000
                    )
                except Exception as e:
                    QMessageBox.critical(None, "Error", 
                                       f"Failed to start Kitchen Dashboard: {e}")
            else:
                QMessageBox.critical(None, "Error", 
                                   "Kitchen Dashboard executable not found!")

    def check_main_app(self):
        """Check if main application is still running"""
        if self.main_app_process and self.main_app_process.poll() is not None:
            # Main app has closed
            self.main_app_process = None

    def setup_auto_startup(self):
        """Set up Windows auto-startup registry entry"""
        try:
            service_path = Path(sys.executable).resolve()
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            
            # Try to open the registry key
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                                   winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "VARSYS_Kitchen_Service", 0, 
                                winreg.REG_SZ, str(service_path))
                winreg.CloseKey(key)
            except Exception:
                pass  # Silently fail if we can't set auto-startup
                
        except Exception:
            pass  # Silently fail

    def is_auto_startup_enabled(self):
        """Check if auto-startup is enabled"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                               winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "VARSYS_Kitchen_Service")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False

    def toggle_auto_startup(self):
        """Toggle auto-startup setting"""
        if self.auto_startup_action.isChecked():
            self.setup_auto_startup()
        else:
            self.remove_auto_startup()

    def remove_auto_startup(self):
        """Remove auto-startup registry entry"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                               winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "VARSYS_Kitchen_Service")
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(None, "Settings", 
                              "Settings will be available in the main application.")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(None, "About VARSYS Kitchen Dashboard",
                         "VARSYS Kitchen Dashboard v1.0.6\n"
                         "Professional Kitchen Management System\n\n"
                         "Copyright (C) 2025 VARSYS Solutions\n"
                         "All rights reserved.")

    def exit_application(self):
        """Exit the service and main application"""
        if self.main_app_process and self.main_app_process.poll() is None:
            self.main_app_process.terminate()
        
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        """Run the service"""
        return self.app.exec()

def main():
    """Main entry point"""
    service = KitchenDashboardService()
    return service.run()

if __name__ == "__main__":
    sys.exit(main())

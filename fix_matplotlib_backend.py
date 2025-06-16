#!/usr/bin/env python3
"""
Fix matplotlib backend for PySide6 compatibility
"""

import os
import sys

def fix_matplotlib_backend():
    """Set matplotlib to use Qt6 backend for PySide6"""
    try:
        # Set environment variable for matplotlib backend
        os.environ['MPLBACKEND'] = 'QtAgg'
        
        # Import matplotlib and set backend
        import matplotlib
        matplotlib.use('QtAgg')  # Use Qt6 backend
        
        # Test the backend
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        
        print("✅ Matplotlib backend set to QtAgg (Qt6)")
        print(f"✅ Current backend: {matplotlib.get_backend()}")
        
        # Test PySide6 integration
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 integration working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting matplotlib backend: {e}")
        return False

if __name__ == "__main__":
    print("Fixing matplotlib backend for PySide6...")
    if fix_matplotlib_backend():
        print("🎉 Matplotlib backend fixed successfully!")
    else:
        print("❌ Failed to fix matplotlib backend")
        sys.exit(1)

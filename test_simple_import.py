#!/usr/bin/env python3
"""
Simple test to check if comprehensive test suite can be imported
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'tests'))

def test_import():
    """Test simple import"""
    print("🧪 Testing Simple Import")
    print("=" * 30)
    
    try:
        print("📦 Importing comprehensive test suite...")
        from comprehensive_test_suite import ComprehensiveTestSuite
        print("✅ Import successful!")
        
        print("📋 Checking class...")
        print(f"   Class: {ComprehensiveTestSuite}")
        print(f"   Methods: {[m for m in dir(ComprehensiveTestSuite) if not m.startswith('_')]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_import()
    if success:
        print("\n✅ Import test passed!")
    else:
        print("\n❌ Import test failed!")

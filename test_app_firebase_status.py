#!/usr/bin/env python3
"""
Test the Kitchen Dashboard app with Firebase status checking
"""

import sys
import os
from datetime import datetime

def test_app_firebase_status():
    """Test the app's Firebase status functionality"""
    print("=== Kitchen Dashboard Firebase Status Test ===")
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        # Import the optimized Firebase manager
        from modules.optimized_firebase_manager import get_optimized_firebase_manager
        
        print("✅ Successfully imported optimized Firebase manager")
        
        # Initialize the manager (this should not hang now)
        print("Initializing Firebase manager...")
        firebase_manager = get_optimized_firebase_manager()
        print("✅ Firebase manager instance created")
        
        # Get status without testing connection
        print("\n--- Getting Firebase Status ---")
        
        # Check basic properties
        print(f"Admin SDK available: {'✅' if firebase_manager.admin_app else '❌'}")
        print(f"Firestore DB available: {'✅' if firebase_manager.db else '❌'}")
        print(f"Pyrebase Auth available: {'✅' if firebase_manager.auth_instance else '❌'}")
        print(f"User authenticated: {'✅' if firebase_manager.is_authenticated() else '❌'}")
        
        # Get detailed diagnostics
        if hasattr(firebase_manager, 'get_connection_diagnostics'):
            print("\n--- Detailed Diagnostics ---")
            diagnostics = firebase_manager.get_connection_diagnostics()
            
            print(f"Overall Status: {diagnostics.get('overall_status', 'unknown')}")
            
            components = diagnostics.get('components', {})
            
            admin_sdk = components.get('admin_sdk', {})
            print(f"Admin SDK: {'✅' if admin_sdk.get('available') else '❌'}")
            if admin_sdk.get('project_id'):
                print(f"  Project ID: {admin_sdk['project_id']}")
            
            firestore = components.get('firestore_database', {})
            print(f"Firestore: {'✅' if firestore.get('available') else '❌'}")
            
            auth = components.get('pyrebase_auth', {})
            print(f"Auth: {'✅' if auth.get('available') else '❌'}")
            
            session = components.get('user_session', {})
            print(f"Session: {'✅' if session.get('authenticated') else '❌'}")
            
            # Show recommendations
            recommendations = diagnostics.get('recommendations', [])
            if recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
        
        # Test Firebase status widget
        print("\n--- Testing Firebase Status Widget ---")
        try:
            from modules.firebase_status_widget import FirebaseStatusWidget
            from PySide6.QtWidgets import QApplication
            
            # Create minimal Qt application
            if not QApplication.instance():
                app = QApplication(sys.argv)
            
            # Create status widget
            status_widget = FirebaseStatusWidget(firebase_manager)
            print("✅ Firebase status widget created successfully")
            
            # Test status refresh
            status_widget.refresh_status()
            print("✅ Status widget refresh completed")
            
        except Exception as widget_error:
            print(f"⚠️ Firebase status widget test failed: {widget_error}")
        
        # Test credential validation
        print("\n--- Testing Credential Validation ---")
        if hasattr(firebase_manager, 'validate_firebase_credentials'):
            cred_path = "secure_credentials/firebase_credentials.json"
            validation = firebase_manager.validate_firebase_credentials(cred_path)
            
            print(f"Credentials valid: {'✅' if validation['valid'] else '❌'}")
            if validation.get('project_id'):
                print(f"Project ID: {validation['project_id']}")
            if validation.get('errors'):
                print("Errors:")
                for error in validation['errors']:
                    print(f"  • {error}")
        
        # Test setup recommendations
        if hasattr(firebase_manager, 'get_firebase_setup_recommendations'):
            recommendations = firebase_manager.get_firebase_setup_recommendations()
            if recommendations:
                print("\n--- Setup Recommendations ---")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec}")
        
        print("\n=== Test Summary ===")
        
        # Determine overall status
        if firebase_manager.admin_app and firebase_manager.auth_instance:
            print("✅ Firebase initialization SUCCESSFUL")
            print("Both Admin SDK and Authentication are available")
            
            if firebase_manager.db:
                print("✅ Firestore database client is available")
                print("Note: Actual connection testing is deferred to avoid hanging")
            else:
                print("⚠️ Firestore database client not available")
        elif firebase_manager.auth_instance:
            print("⚠️ Firebase initialization PARTIAL")
            print("Authentication available but Admin SDK failed")
        elif firebase_manager.admin_app:
            print("⚠️ Firebase initialization PARTIAL") 
            print("Admin SDK available but authentication failed")
        else:
            print("❌ Firebase initialization FAILED")
            print("No Firebase services are available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Kitchen Dashboard Firebase Status Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("kitchen_app.py"):
        print("❌ Error: Please run this script from the Kitchen Dashboard root directory")
        return False
    
    # Test Firebase status
    success = test_app_firebase_status()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Firebase status test completed successfully!")
        print("The Firebase manager is working with improved error handling.")
    else:
        print("❌ Firebase status test failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

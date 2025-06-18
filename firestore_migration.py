#!/usr/bin/env python3
"""
Firestore Data Migration Script
Migrates 'shopping_list' collection to 'expenses_list' collection in Firestore

This script:
1. Connects to Firestore
2. Reads data from 'shopping_list' collection
3. Migrates data to 'expenses_list' collection with new schema
4. Optionally removes old 'shopping_list' collection
5. Updates budget categories if needed
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FirestoreMigration:
    """Handles Firestore data migration from shopping_list to expenses_list"""
    
    def __init__(self):
        self.firebase_manager = None
        self.user_id = None
        self.migration_log = []
        
    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            from modules.optimized_firebase_manager import get_optimized_firebase_manager
            self.firebase_manager = get_optimized_firebase_manager()
            
            if not self.firebase_manager:
                raise Exception("Firebase manager not available")
                
            logger.info("✅ Firebase manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            return False
    
    def authenticate_user(self, email, password):
        """Authenticate user for migration"""
        try:
            success = self.firebase_manager.authenticate_user(email, password)
            if success and hasattr(self.firebase_manager, 'current_session'):
                self.user_id = self.firebase_manager.current_session.user_id
                logger.info(f"✅ User authenticated: {email}")
                return True
            else:
                logger.error("❌ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def check_collections_exist(self):
        """Check which collections exist in Firestore"""
        try:
            collections_status = {}
            
            # Check shopping_list collection
            shopping_data = self.firebase_manager.get_collection_data('shopping_list', self.user_id)
            collections_status['shopping_list'] = {
                'exists': shopping_data is not None and len(shopping_data) > 0,
                'count': len(shopping_data) if shopping_data else 0
            }
            
            # Check expenses_list collection
            expenses_data = self.firebase_manager.get_collection_data('expenses_list', self.user_id)
            collections_status['expenses_list'] = {
                'exists': expenses_data is not None and len(expenses_data) > 0,
                'count': len(expenses_data) if expenses_data else 0
            }
            
            # Check budget_categories collection
            budget_categories_data = self.firebase_manager.get_collection_data('budget_categories', self.user_id)
            collections_status['budget_categories'] = {
                'exists': budget_categories_data is not None and len(budget_categories_data) > 0,
                'count': len(budget_categories_data) if budget_categories_data else 0
            }
            
            return collections_status
            
        except Exception as e:
            logger.error(f"❌ Error checking collections: {e}")
            return {}
    
    def migrate_shopping_to_expenses(self):
        """Migrate shopping_list data to expenses_list format"""
        try:
            # Get shopping_list data
            shopping_data = self.firebase_manager.get_collection_data('shopping_list', self.user_id)
            
            if not shopping_data or len(shopping_data) == 0:
                logger.info("ℹ️ No shopping_list data found to migrate")
                return True
            
            logger.info(f"📦 Found {len(shopping_data)} items in shopping_list collection")
            
            # Convert to DataFrame for easier manipulation
            shopping_df = pd.DataFrame(shopping_data)
            
            # Add budget_category column if it doesn't exist
            if 'budget_category' not in shopping_df.columns:
                shopping_df['budget_category'] = 'Kitchen Essentials'  # Default budget category
                logger.info("➕ Added default budget_category column")
            
            # Ensure all required columns exist
            required_columns = [
                'item_id', 'item_name', 'category', 'budget_category', 'quantity', 'unit', 
                'priority', 'last_price', 'current_price', 'avg_price', 'location', 
                'notes', 'status', 'date_added', 'date_purchased'
            ]
            
            for col in required_columns:
                if col not in shopping_df.columns:
                    if col in ['last_price', 'current_price', 'avg_price']:
                        shopping_df[col] = 0.0
                    elif col in ['date_added', 'date_purchased']:
                        shopping_df[col] = datetime.now().isoformat()
                    else:
                        shopping_df[col] = ''
            
            # Convert back to list of dictionaries
            expenses_data = shopping_df.to_dict('records')
            
            # Upload to expenses_list collection
            success = self.firebase_manager.upload_collection_data('expenses_list', expenses_data, self.user_id)
            
            if success:
                logger.info(f"✅ Successfully migrated {len(expenses_data)} items to expenses_list")
                self.migration_log.append(f"Migrated {len(expenses_data)} items from shopping_list to expenses_list")
                return True
            else:
                logger.error("❌ Failed to upload expenses_list data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Migration error: {e}")
            return False
    
    def create_default_budget_categories(self):
        """Create default budget categories if they don't exist"""
        try:
            # Check if budget_categories already exist
            existing_data = self.firebase_manager.get_collection_data('budget_categories', self.user_id)
            
            if existing_data and len(existing_data) > 0:
                logger.info(f"ℹ️ Budget categories already exist ({len(existing_data)} categories)")
                return True
            
            # Create default budget categories with no budget allocations (user will set their own)
            default_categories = [
                {
                    'category_id': 1,
                    'category_name': 'Kitchen Essentials',
                    'category_type': 'Parent',
                    'parent_id': '',
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Default parent category for kitchen-related expenses - set your own budget allocation'
                },
                {
                    'category_id': 2,
                    'category_name': 'Groceries',
                    'category_type': 'Child',
                    'parent_id': 1,
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Food and grocery items - set your own budget allocation'
                },
                {
                    'category_id': 3,
                    'category_name': 'Cooking Equipment',
                    'category_type': 'Child',
                    'parent_id': 1,
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Kitchen tools and equipment - set your own budget allocation'
                },
                {
                    'category_id': 4,
                    'category_name': 'Utilities',
                    'category_type': 'Parent',
                    'parent_id': '',
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Utility expenses - set your own budget allocation'
                },
                {
                    'category_id': 5,
                    'category_name': 'Maintenance',
                    'category_type': 'Parent',
                    'parent_id': '',
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Maintenance and repairs - set your own budget allocation'
                }
            ]
            
            # Upload budget categories
            success = self.firebase_manager.upload_collection_data('budget_categories', default_categories, self.user_id)
            
            if success:
                logger.info(f"✅ Created {len(default_categories)} default budget categories")
                self.migration_log.append(f"Created {len(default_categories)} default budget categories")
                return True
            else:
                logger.error("❌ Failed to create budget categories")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating budget categories: {e}")
            return False
    
    def remove_old_shopping_collection(self, confirm=False):
        """Remove old shopping_list collection (with confirmation)"""
        try:
            if not confirm:
                logger.info("⚠️ Skipping removal of shopping_list collection (confirm=False)")
                return True
            
            # This would require admin privileges or a specific delete method
            # For now, we'll just log that it should be done manually
            logger.info("⚠️ Manual action required: Remove 'shopping_list' collection from Firestore console")
            self.migration_log.append("Manual action required: Remove 'shopping_list' collection")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing shopping collection: {e}")
            return False
    
    def run_migration(self, email, password, remove_old=False):
        """Run the complete migration process"""
        logger.info("🚀 Starting Firestore migration...")
        logger.info("=" * 60)
        
        # Step 1: Initialize Firebase
        if not self.initialize_firebase():
            return False
        
        # Step 2: Authenticate
        if not self.authenticate_user(email, password):
            return False
        
        # Step 3: Check current collections
        logger.info("📋 Checking current collections...")
        collections_status = self.check_collections_exist()
        
        for collection, status in collections_status.items():
            if status['exists']:
                logger.info(f"  ✅ {collection}: {status['count']} items")
            else:
                logger.info(f"  ❌ {collection}: Not found")
        
        # Step 4: Migrate shopping_list to expenses_list
        if collections_status.get('shopping_list', {}).get('exists', False):
            logger.info("🔄 Migrating shopping_list to expenses_list...")
            if not self.migrate_shopping_to_expenses():
                return False
        else:
            logger.info("ℹ️ No shopping_list data to migrate")
        
        # Step 5: Create budget categories
        logger.info("📊 Setting up budget categories...")
        if not self.create_default_budget_categories():
            return False
        
        # Step 6: Remove old collection (optional)
        if remove_old:
            logger.info("🗑️ Removing old shopping_list collection...")
            self.remove_old_shopping_collection(confirm=True)
        
        # Step 7: Summary
        logger.info("=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("📝 Migration Summary:")
        for log_entry in self.migration_log:
            logger.info(f"  • {log_entry}")
        
        return True

def main():
    """Main migration function"""
    print("🔥 Firestore Data Migration Tool")
    print("=" * 50)
    print("This tool migrates 'shopping_list' to 'expenses_list' in Firestore")
    print()
    
    # Get user credentials
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required")
        return False
    
    # Confirm migration
    print("\n⚠️ This will migrate your Firestore data:")
    print("  • shopping_list → expenses_list")
    print("  • Create default budget categories")
    print("  • Optionally remove old shopping_list collection")
    
    confirm = input("\nProceed with migration? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Migration cancelled")
        return False
    
    # Ask about removing old collection
    remove_old = input("Remove old shopping_list collection after migration? (yes/no): ").strip().lower() in ['yes', 'y']
    
    # Run migration
    migration = FirestoreMigration()
    success = migration.run_migration(email, password, remove_old)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Your Firestore data has been updated to use the new expenses system.")
    else:
        print("\n❌ Migration failed. Please check the logs above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

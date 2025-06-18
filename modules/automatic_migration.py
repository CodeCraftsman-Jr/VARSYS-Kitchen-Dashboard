"""
Automatic Firestore Migration Module

This module handles automatic migration of old 'shopping_list' data to 'expenses_list'
during normal application startup. It runs transparently in the background.
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class AutomaticMigration:
    """Handles automatic migration of Firestore data during app startup"""
    
    def __init__(self, firebase_manager, user_id: str):
        self.firebase_manager = firebase_manager
        self.user_id = user_id
        self.migration_performed = False
        
    def check_migration_needed(self) -> bool:
        """Check if migration is needed"""
        try:
            # Check if shopping_list collection exists
            shopping_data = self.firebase_manager.get_collection_data('shopping_list', self.user_id)
            has_shopping_data = shopping_data is not None and len(shopping_data) > 0
            
            # Check if expenses_list collection exists
            expenses_data = self.firebase_manager.get_collection_data('expenses_list', self.user_id)
            has_expenses_data = expenses_data is not None and len(expenses_data) > 0
            
            # Migration needed if we have shopping data but no expenses data
            migration_needed = has_shopping_data and not has_expenses_data
            
            if migration_needed:
                logger.info(f"🔄 Migration needed: shopping_list ({len(shopping_data)} items) → expenses_list")
            elif has_shopping_data and has_expenses_data:
                logger.info("ℹ️ Both shopping_list and expenses_list exist - manual cleanup may be needed")
            else:
                logger.info("✅ No migration needed")
            
            return migration_needed
            
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return False
    
    def migrate_shopping_to_expenses(self) -> bool:
        """Migrate shopping_list data to expenses_list"""
        try:
            # Get shopping_list data
            shopping_data = self.firebase_manager.get_collection_data('shopping_list', self.user_id)
            
            if not shopping_data or len(shopping_data) == 0:
                logger.info("No shopping_list data to migrate")
                return True
            
            logger.info(f"Migrating {len(shopping_data)} items from shopping_list to expenses_list")
            
            # Convert to DataFrame for easier manipulation
            shopping_df = pd.DataFrame(shopping_data)
            
            # Add budget_category column if missing
            if 'budget_category' not in shopping_df.columns:
                shopping_df['budget_category'] = 'Kitchen Essentials'
            
            # Ensure required columns exist with defaults
            column_defaults = {
                'item_id': lambda: range(1, len(shopping_df) + 1),
                'item_name': '',
                'category': 'Uncategorized',
                'budget_category': 'Kitchen Essentials',
                'quantity': 1,
                'unit': 'piece',
                'priority': 'Medium',
                'last_price': 0.0,
                'current_price': 0.0,
                'avg_price': 0.0,
                'location': '',
                'notes': '',
                'status': 'Pending',
                'date_added': datetime.now().isoformat(),
                'date_purchased': ''
            }
            
            for col, default_value in column_defaults.items():
                if col not in shopping_df.columns:
                    if callable(default_value):
                        shopping_df[col] = list(default_value())
                    else:
                        shopping_df[col] = default_value
            
            # Convert to records for upload
            expenses_data = shopping_df.to_dict('records')
            
            # Upload to expenses_list collection
            success = self.firebase_manager.upload_collection_data('expenses_list', expenses_data, self.user_id)
            
            if success:
                logger.info(f"✅ Successfully migrated {len(expenses_data)} items to expenses_list")
                self.migration_performed = True
                return True
            else:
                logger.error("❌ Failed to upload migrated data to expenses_list")
                return False
                
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return False
    
    def create_budget_categories_if_missing(self) -> bool:
        """Create default budget categories if they don't exist"""
        try:
            # Check if budget_categories exist
            existing_categories = self.firebase_manager.get_collection_data('budget_categories', self.user_id)
            
            if existing_categories and len(existing_categories) > 0:
                logger.info(f"Budget categories already exist ({len(existing_categories)} categories)")
                return True
            
            # Create default categories with no budget allocations (user will set their own)
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
                    'category_name': 'Utilities',
                    'category_type': 'Parent',
                    'parent_id': '',
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Utility expenses - set your own budget allocation'
                },
                {
                    'category_id': 4,
                    'category_name': 'Maintenance',
                    'category_type': 'Parent',
                    'parent_id': '',
                    'budget_amount': 0.0,
                    'spent_amount': 0.0,
                    'description': 'Maintenance and repairs - set your own budget allocation'
                }
            ]
            
            success = self.firebase_manager.upload_collection_data('budget_categories', default_categories, self.user_id)
            
            if success:
                logger.info(f"✅ Created {len(default_categories)} default budget categories")
                return True
            else:
                logger.error("❌ Failed to create default budget categories")
                return False
                
        except Exception as e:
            logger.error(f"Error creating budget categories: {e}")
            return False
    
    def run_automatic_migration(self) -> Dict[str, Any]:
        """Run automatic migration if needed"""
        result = {
            'migration_performed': False,
            'budget_categories_created': False,
            'success': True,
            'message': 'No migration needed'
        }
        
        try:
            # Check if migration is needed
            if not self.check_migration_needed():
                result['message'] = 'No migration needed - data is up to date'
                return result
            
            logger.info("🔄 Starting automatic migration...")
            
            # Perform migration
            if self.migrate_shopping_to_expenses():
                result['migration_performed'] = True
                result['message'] = 'Successfully migrated shopping_list to expenses_list'
            else:
                result['success'] = False
                result['message'] = 'Failed to migrate shopping_list data'
                return result
            
            # Create budget categories if needed
            if self.create_budget_categories_if_missing():
                result['budget_categories_created'] = True
            
            logger.info("✅ Automatic migration completed successfully")
            result['message'] = 'Migration completed successfully'
            
        except Exception as e:
            logger.error(f"Error during automatic migration: {e}")
            result['success'] = False
            result['message'] = f'Migration failed: {str(e)}'
        
        return result

def run_migration_if_needed(firebase_manager, user_id: str) -> Dict[str, Any]:
    """
    Convenience function to run migration if needed
    
    Args:
        firebase_manager: Firebase manager instance
        user_id: User ID for the migration
        
    Returns:
        Dict with migration results
    """
    migration = AutomaticMigration(firebase_manager, user_id)
    return migration.run_automatic_migration()

def check_and_migrate_on_startup(firebase_manager, user_id: str) -> bool:
    """
    Check and perform migration during app startup
    
    Args:
        firebase_manager: Firebase manager instance
        user_id: User ID for the migration
        
    Returns:
        bool: True if successful or no migration needed, False if failed
    """
    try:
        result = run_migration_if_needed(firebase_manager, user_id)
        
        if result['success']:
            if result['migration_performed']:
                logger.info("🎉 Automatic migration completed during startup")
            return True
        else:
            logger.error(f"Migration failed during startup: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"Error during startup migration: {e}")
        return False

"""
Shopping List Management Module

This module provides functionality to:
- Mark items as purchased with today's date
- Update inventory when items are purchased
- Manage shopping list status and dates
- Provide proper integration between shopping and inventory
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from shopping_inventory_sync import ShoppingInventorySync

class ShoppingListManager:
    """Manages shopping list operations and inventory integration"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.shopping_file = os.path.join(data_dir, "shopping_list.csv")
        self.sync_manager = ShoppingInventorySync(data_dir)
        
    def mark_items_as_purchased(self, item_ids: List[int], purchase_date: Optional[str] = None) -> Dict[str, int]:
        """
        Mark shopping list items as purchased and sync to inventory
        
        Args:
            item_ids: List of item IDs to mark as purchased
            purchase_date: Date of purchase (defaults to today)
            
        Returns:
            Dict with operation results
        """
        if purchase_date is None:
            purchase_date = datetime.now().strftime('%Y-%m-%d')
            
        results = {
            'marked_purchased': 0,
            'synced_to_inventory': 0,
            'errors': 0,
            'error_items': []
        }
        
        try:
            # Read shopping list
            shopping_df = pd.read_csv(self.shopping_file)
            
            # Process each item
            for item_id in item_ids:
                try:
                    # Find the item
                    item_idx = shopping_df[shopping_df['item_id'] == item_id].index
                    if len(item_idx) == 0:
                        results['errors'] += 1
                        results['error_items'].append(f"Item ID {item_id} not found")
                        continue
                    
                    idx = item_idx[0]
                    item_name = shopping_df.loc[idx, 'item_name']
                    
                    # Update status and date
                    shopping_df.loc[idx, 'status'] = 'Purchased'
                    shopping_df.loc[idx, 'date_purchased'] = purchase_date
                    
                    # Update current price if not set
                    if pd.isna(shopping_df.loc[idx, 'current_price']) or shopping_df.loc[idx, 'current_price'] == 0:
                        shopping_df.loc[idx, 'current_price'] = shopping_df.loc[idx, 'last_price']
                    
                    results['marked_purchased'] += 1
                    print(f"[SUCCESS] Marked as purchased: {item_name} on {purchase_date}")
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_items'].append(f"Error processing item {item_id}: {e}")
                    print(f"❌ Error processing item {item_id}: {e}")
            
            # Save updated shopping list
            if results['marked_purchased'] > 0:
                shopping_df.to_csv(self.shopping_file, index=False)
                print(f"💾 Updated shopping list with {results['marked_purchased']} purchased items")
                
                # Sync to inventory
                sync_results = self.sync_manager.sync_purchased_items()
                results['synced_to_inventory'] = sync_results['updated_inventory'] + sync_results['new_inventory_items']
                
                if sync_results['errors'] > 0:
                    results['errors'] += sync_results['errors']
                    results['error_items'].append(f"Sync errors: {sync_results['errors']}")
                
        except Exception as e:
            results['errors'] += 1
            results['error_items'].append(f"General error: {e}")
            print(f"❌ General error in mark_items_as_purchased: {e}")
        
        return results
    
    def mark_item_as_pending(self, item_id: int) -> bool:
        """Mark an item as pending (not purchased)"""
        try:
            shopping_df = pd.read_csv(self.shopping_file)
            
            item_idx = shopping_df[shopping_df['item_id'] == item_id].index
            if len(item_idx) == 0:
                return False
            
            idx = item_idx[0]
            shopping_df.loc[idx, 'status'] = 'Pending'
            shopping_df.loc[idx, 'date_purchased'] = ''
            shopping_df.loc[idx, 'current_price'] = 0.0
            
            shopping_df.to_csv(self.shopping_file, index=False)
            
            item_name = shopping_df.loc[idx, 'item_name']
            print(f"[SUCCESS] Marked as pending: {item_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error marking item as pending: {e}")
            return False
    
    def update_item_dates_to_today(self, item_ids: List[int]) -> Dict[str, int]:
        """Update date_added for specified items to today"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        results = {
            'updated': 0,
            'errors': 0,
            'error_items': []
        }
        
        try:
            shopping_df = pd.read_csv(self.shopping_file)
            
            for item_id in item_ids:
                try:
                    item_idx = shopping_df[shopping_df['item_id'] == item_id].index
                    if len(item_idx) == 0:
                        results['errors'] += 1
                        results['error_items'].append(f"Item ID {item_id} not found")
                        continue
                    
                    idx = item_idx[0]
                    item_name = shopping_df.loc[idx, 'item_name']
                    
                    # Update date_added to today
                    shopping_df.loc[idx, 'date_added'] = today
                    
                    # If item is pending, clear purchase date
                    if shopping_df.loc[idx, 'status'].lower() == 'pending':
                        shopping_df.loc[idx, 'date_purchased'] = ''
                    
                    results['updated'] += 1
                    print(f"[SUCCESS] Updated date for: {item_name} to {today}")
                    
                except Exception as e:
                    results['errors'] += 1
                    results['error_items'].append(f"Error updating item {item_id}: {e}")
            
            # Save updated shopping list
            if results['updated'] > 0:
                shopping_df.to_csv(self.shopping_file, index=False)
                print(f"💾 Updated {results['updated']} item dates to {today}")
        
        except Exception as e:
            results['errors'] += 1
            results['error_items'].append(f"General error: {e}")
            print(f"❌ Error updating dates: {e}")
        
        return results
    
    def get_shopping_list_summary(self) -> Dict[str, any]:
        """Get summary of shopping list status"""
        try:
            shopping_df = pd.read_csv(self.shopping_file)
            
            total_items = len(shopping_df)
            purchased_items = len(shopping_df[shopping_df['status'].str.lower() == 'purchased'])
            pending_items = len(shopping_df[shopping_df['status'].str.lower() == 'pending'])
            
            # Get items by date
            today = datetime.now().strftime('%Y-%m-%d')
            items_added_today = len(shopping_df[shopping_df['date_added'] == today])
            items_purchased_today = len(shopping_df[shopping_df['date_purchased'] == today])
            
            return {
                'total_items': total_items,
                'purchased_items': purchased_items,
                'pending_items': pending_items,
                'items_added_today': items_added_today,
                'items_purchased_today': items_purchased_today,
                'current_date': today
            }
            
        except Exception as e:
            print(f"Error getting shopping list summary: {e}")
            return {
                'total_items': 0,
                'purchased_items': 0,
                'pending_items': 0,
                'items_added_today': 0,
                'items_purchased_today': 0,
                'current_date': datetime.now().strftime('%Y-%m-%d')
            }

def main():
    """Test the shopping list management functionality"""
    manager = ShoppingListManager()
    
    print("🛒 Shopping List Management Test")
    print("=" * 50)
    
    # Get current summary
    summary = manager.get_shopping_list_summary()
    print(f"📊 Current Summary:")
    print(f"   Total items: {summary['total_items']}")
    print(f"   Purchased: {summary['purchased_items']}")
    print(f"   Pending: {summary['pending_items']}")
    print(f"   Added today: {summary['items_added_today']}")
    print(f"   Purchased today: {summary['items_purchased_today']}")
    print(f"   Current date: {summary['current_date']}")
    
    # Update recent items to today's date
    recent_item_ids = [64, 65, 66, 67, 68, 69]  # The 6 items we updated earlier
    print(f"\n🔄 Updating dates for items {recent_item_ids} to today...")
    
    date_results = manager.update_item_dates_to_today(recent_item_ids)
    print(f"[SUCCESS] Date update results:")
    print(f"   Updated: {date_results['updated']}")
    print(f"   Errors: {date_results['errors']}")
    
    # Get updated summary
    summary = manager.get_shopping_list_summary()
    print(f"\n📊 Updated Summary:")
    print(f"   Items added today: {summary['items_added_today']}")
    print(f"   Items purchased today: {summary['items_purchased_today']}")

if __name__ == "__main__":
    main()

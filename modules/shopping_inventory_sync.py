"""
Shopping List to Inventory Synchronization Module

This module handles the integration between shopping list and inventory:
- When items are marked as "Purchased" in shopping list, update inventory
- Sync quantities, prices, and dates between systems
- Maintain data consistency across modules
"""

import os
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class ShoppingInventorySync:
    """Handles synchronization between shopping list and inventory"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.shopping_file = os.path.join(data_dir, "shopping_list.csv")
        self.inventory_file = os.path.join(data_dir, "inventory.csv")
        
    def sync_purchased_items(self) -> Dict[str, int]:
        """
        Sync items marked as 'Purchased' in shopping list to inventory
        Returns: Dict with sync results
        """
        results = {
            'updated_inventory': 0,
            'new_inventory_items': 0,
            'updated_shopping_dates': 0,
            'errors': 0
        }
        
        try:
            # Read shopping list
            shopping_df = pd.read_csv(self.shopping_file)
            
            # Read inventory
            if os.path.exists(self.inventory_file):
                inventory_df = pd.read_csv(self.inventory_file)
            else:
                # Create empty inventory if it doesn't exist
                inventory_df = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit',
                    'price_per_unit', 'location', 'expiry_date', 'reorder_level',
                    'total_value', 'price', 'qty_purchased', 'qty_used', 'avg_price',
                    'description', 'default_cost', 'purchase_count', 'total_spent',
                    'last_purchase_date', 'last_purchase_price'
                ])
            
            # Find purchased items that need syncing
            purchased_items = shopping_df[
                (shopping_df['status'].str.lower() == 'purchased') &
                (shopping_df['date_purchased'].notna()) &
                (shopping_df['date_purchased'] != '')
            ].copy()
            
            print(f"Found {len(purchased_items)} purchased items to sync")
            
            # Process each purchased item
            for _, item in purchased_items.iterrows():
                try:
                    result = self._sync_single_item(item, inventory_df)
                    if result['action'] == 'updated':
                        results['updated_inventory'] += 1
                    elif result['action'] == 'created':
                        results['new_inventory_items'] += 1
                        
                except Exception as e:
                    print(f"Error syncing item {item.get('item_name', 'Unknown')}: {e}")
                    results['errors'] += 1
            
            # Save updated inventory
            if results['updated_inventory'] > 0 or results['new_inventory_items'] > 0:
                inventory_df.to_csv(self.inventory_file, index=False)
                print(f"[SUCCESS] Inventory updated: {results['updated_inventory']} items updated, {results['new_inventory_items']} new items")
            
            return results
            
        except Exception as e:
            print(f"Error in sync_purchased_items: {e}")
            results['errors'] += 1
            return results
    
    def _sync_single_item(self, shopping_item: pd.Series, inventory_df: pd.DataFrame) -> Dict[str, str]:
        """Sync a single shopping item to inventory"""
        
        item_name = str(shopping_item.get('item_name', '')).strip()
        quantity = float(shopping_item.get('quantity', 0))
        unit = str(shopping_item.get('unit', 'units'))
        price_per_unit = float(shopping_item.get('current_price', 0)) / max(quantity, 1)
        total_cost = float(shopping_item.get('current_price', 0))
        purchase_date = shopping_item.get('date_purchased', datetime.now().strftime('%Y-%m-%d'))
        category = shopping_item.get('category', 'General')
        
        # Check if item exists in inventory
        existing_item_idx = inventory_df[
            inventory_df['item_name'].str.lower().str.strip() == item_name.lower()
        ].index
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        if len(existing_item_idx) > 0:
            # Update existing inventory item
            idx = existing_item_idx[0]
            current_qty = float(inventory_df.loc[idx, 'quantity'] or 0)
            new_qty = current_qty + quantity

            inventory_df.loc[idx, 'quantity'] = new_qty
            inventory_df.loc[idx, 'price_per_unit'] = price_per_unit
            inventory_df.loc[idx, 'total_value'] = float(inventory_df.loc[idx, 'total_value'] or 0) + total_cost
            inventory_df.loc[idx, 'last_purchase_date'] = purchase_date
            inventory_df.loc[idx, 'last_purchase_price'] = price_per_unit
            inventory_df.loc[idx, 'qty_purchased'] = float(inventory_df.loc[idx, 'qty_purchased'] or 0) + quantity
            inventory_df.loc[idx, 'total_spent'] = float(inventory_df.loc[idx, 'total_spent'] or 0) + total_cost
            inventory_df.loc[idx, 'purchase_count'] = int(inventory_df.loc[idx, 'purchase_count'] or 0) + 1

            print(f"Updated inventory: {item_name} ({current_qty} + {quantity} = {new_qty} {unit})")
            return {'action': 'updated', 'item': item_name}
            
        else:
            # Create new inventory item
            next_id = inventory_df['item_id'].max() + 1 if len(inventory_df) > 0 else 1

            new_item = {
                'item_id': next_id,
                'item_name': item_name,
                'category': category,
                'quantity': quantity,
                'unit': unit,
                'price_per_unit': price_per_unit,
                'location': shopping_item.get('location', 'Local Market'),
                'expiry_date': '',
                'reorder_level': max(quantity * 0.2, 1),  # 20% of purchased quantity
                'total_value': total_cost,
                'price': price_per_unit,
                'qty_purchased': quantity,
                'qty_used': 0,
                'avg_price': price_per_unit,
                'description': f'Added from shopping list on {current_date}',
                'default_cost': price_per_unit,
                'purchase_count': 1,
                'total_spent': total_cost,
                'last_purchase_date': purchase_date,
                'last_purchase_price': price_per_unit
            }

            inventory_df = pd.concat([inventory_df, pd.DataFrame([new_item])], ignore_index=True)

            print(f"Created new inventory item: {item_name} ({quantity} {unit})")
            return {'action': 'created', 'item': item_name}
    
    def mark_shopping_item_as_synced(self, item_id: int) -> bool:
        """Mark a shopping list item as synced to inventory"""
        try:
            # Read shopping list
            shopping_df = pd.read_csv(self.shopping_file)
            
            # Find and update the item
            item_idx = shopping_df[shopping_df['item_id'] == item_id].index
            if len(item_idx) > 0:
                idx = item_idx[0]
                shopping_df.loc[idx, 'notes'] = str(shopping_df.loc[idx, 'notes']) + ' [Synced to Inventory]'
                shopping_df.loc[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
                
                # Save updated shopping list
                shopping_df.to_csv(self.shopping_file, index=False)
                return True
                
        except Exception as e:
            print(f"Error marking item as synced: {e}")
            
        return False
    
    def get_sync_status(self) -> Dict[str, int]:
        """Get current synchronization status"""
        try:
            shopping_df = pd.read_csv(self.shopping_file)
            
            total_items = len(shopping_df)
            purchased_items = len(shopping_df[shopping_df['status'].str.lower() == 'purchased'])
            pending_items = len(shopping_df[shopping_df['status'].str.lower() == 'pending'])
            synced_items = len(shopping_df[shopping_df['notes'].str.contains('Synced to Inventory', na=False)])
            
            return {
                'total_shopping_items': total_items,
                'purchased_items': purchased_items,
                'pending_items': pending_items,
                'synced_items': synced_items,
                'unsynced_purchased': purchased_items - synced_items
            }
            
        except Exception as e:
            print(f"Error getting sync status: {e}")
            return {
                'total_shopping_items': 0,
                'purchased_items': 0,
                'pending_items': 0,
                'synced_items': 0,
                'unsynced_purchased': 0
            }

def main():
    """Test the synchronization functionality"""
    sync = ShoppingInventorySync()
    
    print("🔄 Starting Shopping List to Inventory Sync...")
    
    # Get current status
    status = sync.get_sync_status()
    print(f"📊 Current Status:")
    print(f"   Total shopping items: {status['total_shopping_items']}")
    print(f"   Purchased items: {status['purchased_items']}")
    print(f"   Pending items: {status['pending_items']}")
    print(f"   Already synced: {status['synced_items']}")
    print(f"   Need syncing: {status['unsynced_purchased']}")
    
    # Perform sync
    results = sync.sync_purchased_items()
    print(f"\n[SUCCESS] Sync Results:")
    print(f"   Inventory items updated: {results['updated_inventory']}")
    print(f"   New inventory items created: {results['new_inventory_items']}")
    print(f"   Errors: {results['errors']}")

if __name__ == "__main__":
    main()

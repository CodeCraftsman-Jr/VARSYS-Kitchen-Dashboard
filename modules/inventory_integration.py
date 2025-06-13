"""
Inventory Integration Module
Handles automatic inventory reduction when sales are completed,
gas usage tracking, and packing materials consumption.
"""

import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class InventoryIntegration:
    """Manages inventory integration with sales, gas, and packing materials"""
    
    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(__name__)
        
    def process_sale_completion(self, sale_data: Dict) -> Dict[str, any]:
        """
        Process sale completion and update all related inventories
        
        Args:
            sale_data: Dictionary containing sale information
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'success': False,
            'inventory_updated': False,
            'gas_updated': False,
            'packing_updated': False,
            'budget_updated': False,
            'errors': []
        }
        
        try:
            # 1. Update ingredient inventory
            inventory_result = self.update_ingredient_inventory(sale_data)
            results['inventory_updated'] = inventory_result['success']
            if not inventory_result['success']:
                results['errors'].extend(inventory_result['errors'])
            
            # 2. Update gas usage
            gas_result = self.update_gas_usage(sale_data)
            results['gas_updated'] = gas_result['success']
            if not gas_result['success']:
                results['errors'].extend(gas_result['errors'])
            
            # 3. Update packing materials
            packing_result = self.update_packing_materials(sale_data)
            results['packing_updated'] = packing_result['success']
            if not packing_result['success']:
                results['errors'].extend(packing_result['errors'])
            
            # 4. Update budget tracking
            budget_result = self.update_budget_tracking(sale_data)
            results['budget_updated'] = budget_result['success']
            if not budget_result['success']:
                results['errors'].extend(budget_result['errors'])
            
            # Overall success if at least inventory was updated
            results['success'] = results['inventory_updated']
            
            self.logger.info(f"Sale completion processed: {results}")
            
        except Exception as e:
            self.logger.error(f"Error processing sale completion: {e}")
            results['errors'].append(str(e))
            
        return results
    
    def update_ingredient_inventory(self, sale_data: Dict) -> Dict[str, any]:
        """Update ingredient inventory based on recipe requirements"""
        result = {'success': False, 'errors': [], 'updated_items': []}
        
        try:
            recipe_name = sale_data.get('recipe_name') or sale_data.get('item_name')
            quantity_sold = sale_data.get('quantity', 1)
            
            if not recipe_name:
                result['errors'].append("No recipe name found in sale data")
                return result
            
            # Find recipe ingredients
            if 'recipe_ingredients' not in self.data or self.data['recipe_ingredients'].empty:
                result['errors'].append("No recipe ingredients data available")
                return result
            
            # Get recipe ID
            recipe_id = self.get_recipe_id(recipe_name)
            if not recipe_id:
                result['errors'].append(f"Recipe '{recipe_name}' not found")
                return result
            
            # Get ingredients for this recipe
            recipe_ingredients = self.data['recipe_ingredients'][
                self.data['recipe_ingredients']['recipe_id'] == recipe_id
            ]
            
            if recipe_ingredients.empty:
                result['errors'].append(f"No ingredients found for recipe '{recipe_name}'")
                return result
            
            # Update inventory for each ingredient
            for _, ingredient in recipe_ingredients.iterrows():
                item_name = ingredient.get('item_name', '')
                ingredient_qty = float(ingredient.get('quantity', 0))
                ingredient_unit = ingredient.get('unit', 'g')
                
                total_qty_needed = ingredient_qty * quantity_sold
                
                # Deduct from inventory
                deduction_result = self.deduct_from_inventory(
                    item_name, total_qty_needed, ingredient_unit
                )
                
                if deduction_result['success']:
                    result['updated_items'].append({
                        'item': item_name,
                        'deducted': total_qty_needed,
                        'unit': ingredient_unit
                    })
                else:
                    result['errors'].extend(deduction_result['errors'])
            
            # Save updated inventory
            if result['updated_items']:
                self.save_inventory()
                result['success'] = True
                
        except Exception as e:
            self.logger.error(f"Error updating ingredient inventory: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def deduct_from_inventory(self, item_name: str, quantity: float, unit: str) -> Dict[str, any]:
        """Deduct quantity from inventory item"""
        result = {'success': False, 'errors': []}
        
        try:
            if 'inventory' not in self.data:
                result['errors'].append("No inventory data available")
                return result
            
            inventory_df = self.data['inventory']
            
            # Find the item
            item_mask = inventory_df['item_name'].str.lower() == item_name.lower()
            matching_items = inventory_df[item_mask]
            
            if matching_items.empty:
                # Create new item with negative quantity (indicates shortage)
                new_item = pd.DataFrame({
                    'item_id': [len(inventory_df) + 1],
                    'item_name': [item_name],
                    'category': ['Auto-Added'],
                    'quantity': [-quantity],
                    'unit': [unit],
                    'price': [0],
                    'location': ['Unknown'],
                    'notes': [f'Auto-created due to sale. Shortage: {quantity} {unit}']
                })
                
                self.data['inventory'] = pd.concat([inventory_df, new_item], ignore_index=True)
                result['success'] = True
                self.logger.warning(f"Created new inventory item '{item_name}' with shortage")
                
            else:
                # Update existing item
                item_idx = matching_items.index[0]
                current_qty = float(inventory_df.loc[item_idx, 'quantity'])
                new_qty = current_qty - quantity
                
                inventory_df.loc[item_idx, 'quantity'] = new_qty
                
                # Update used quantity if column exists
                if 'qty_used' in inventory_df.columns:
                    current_used = float(inventory_df.loc[item_idx, 'qty_used']) if pd.notna(inventory_df.loc[item_idx, 'qty_used']) else 0
                    inventory_df.loc[item_idx, 'qty_used'] = current_used + quantity
                
                result['success'] = True
                
                if new_qty < 0:
                    self.logger.warning(f"Item '{item_name}' now has negative quantity: {new_qty}")
                
        except Exception as e:
            self.logger.error(f"Error deducting from inventory: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def update_gas_usage(self, sale_data: Dict) -> Dict[str, any]:
        """Update gas usage based on cooking time"""
        result = {'success': False, 'errors': []}
        
        try:
            recipe_name = sale_data.get('recipe_name') or sale_data.get('item_name')
            quantity_sold = sale_data.get('quantity', 1)
            
            # Get cooking time from recipe
            cooking_time = self.get_recipe_cooking_time(recipe_name)
            if not cooking_time:
                cooking_time = 30  # Default 30 minutes
            
            # Calculate gas usage (0.2 kg per hour of cooking)
            gas_usage_per_hour = 0.2
            total_cooking_time = cooking_time * quantity_sold  # Total minutes
            gas_usage = (total_cooking_time / 60.0) * gas_usage_per_hour  # Convert to hours and calculate usage
            
            # Add to gas usage data
            if 'gas_usage' not in self.data:
                self.data['gas_usage'] = pd.DataFrame(columns=[
                    'usage_id', 'date', 'usage_kg', 'purpose', 'type', 'notes'
                ])
            
            new_usage = pd.DataFrame({
                'usage_id': [len(self.data['gas_usage']) + 1],
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'usage_kg': [gas_usage],
                'purpose': [f"Cooking: {recipe_name} (x{quantity_sold})"],
                'type': ['Cooking'],
                'notes': [f"Auto-calculated from sale. Cooking time: {total_cooking_time} minutes"]
            })
            
            self.data['gas_usage'] = pd.concat([self.data['gas_usage'], new_usage], ignore_index=True)
            
            # Save gas usage data
            gas_file = os.path.join('data', 'gas_usage.csv')
            self.data['gas_usage'].to_csv(gas_file, index=False)
            
            result['success'] = True
            self.logger.info(f"Gas usage updated: {gas_usage:.3f} kg for {recipe_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating gas usage: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def update_packing_materials(self, sale_data: Dict) -> Dict[str, any]:
        """Update packing materials inventory"""
        result = {'success': False, 'errors': []}
        
        try:
            quantity_sold = sale_data.get('quantity', 1)
            
            # Standard packing materials per order
            packing_items = [
                {'name': 'Food Container', 'qty_per_order': 1},
                {'name': 'Plastic Bag', 'qty_per_order': 1},
                {'name': 'Napkins', 'qty_per_order': 2}
            ]
            
            if 'packing_materials' not in self.data:
                result['errors'].append("No packing materials data available")
                return result
            
            packing_df = self.data['packing_materials']
            updated_items = []
            
            for item in packing_items:
                item_name = item['name']
                qty_needed = item['qty_per_order'] * quantity_sold
                
                # Find and update packing material
                item_mask = packing_df['material_name'].str.lower() == item_name.lower()
                matching_items = packing_df[item_mask]
                
                if not matching_items.empty:
                    item_idx = matching_items.index[0]
                    current_stock = float(packing_df.loc[item_idx, 'current_stock'])
                    new_stock = current_stock - qty_needed
                    
                    packing_df.loc[item_idx, 'current_stock'] = max(0, new_stock)  # Don't go below 0
                    updated_items.append(f"{item_name}: {qty_needed} used")
                    
                    if new_stock < 0:
                        self.logger.warning(f"Packing material '{item_name}' is out of stock")
            
            if updated_items:
                # Save packing materials data
                packing_file = os.path.join('data', 'packing_materials.csv')
                packing_df.to_csv(packing_file, index=False)
                result['success'] = True
                self.logger.info(f"Packing materials updated: {', '.join(updated_items)}")
            
        except Exception as e:
            self.logger.error(f"Error updating packing materials: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def update_budget_tracking(self, sale_data: Dict) -> Dict[str, any]:
        """Update budget tracking with sale revenue"""
        result = {'success': False, 'errors': []}
        
        try:
            total_amount = sale_data.get('total_amount', 0)
            
            if total_amount <= 0:
                result['errors'].append("No valid sale amount found")
                return result
            
            # Add to revenue tracking (could be part of budget)
            if 'budget' in self.data and not self.data['budget'].empty:
                # Find revenue category or create it
                budget_df = self.data['budget']
                revenue_mask = budget_df['category'] == 'Revenue'
                
                if revenue_mask.any():
                    # Update existing revenue
                    idx = budget_df[revenue_mask].index[0]
                    current_actual = float(budget_df.loc[idx, 'actual_amount']) if 'actual_amount' in budget_df.columns else 0
                    budget_df.loc[idx, 'actual_amount'] = current_actual + total_amount
                else:
                    # Create new revenue category
                    new_revenue = pd.DataFrame({
                        'budget_id': [len(budget_df) + 1],
                        'category': ['Revenue'],
                        'budget_amount': [0],  # No budget limit for revenue
                        'actual_amount': [total_amount],
                        'period': ['Monthly'],
                        'notes': ['Auto-tracked from sales']
                    })
                    
                    self.data['budget'] = pd.concat([budget_df, new_revenue], ignore_index=True)
                
                # Save budget data
                budget_file = os.path.join('data', 'budget.csv')
                self.data['budget'].to_csv(budget_file, index=False)
                result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error updating budget tracking: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def get_recipe_id(self, recipe_name: str) -> Optional[str]:
        """Get recipe ID from recipe name"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return None
            
            recipes_df = self.data['recipes']
            recipe_mask = recipes_df['recipe_name'].str.lower() == recipe_name.lower()
            matching_recipes = recipes_df[recipe_mask]
            
            if not matching_recipes.empty:
                return matching_recipes.iloc[0]['recipe_id']
                
        except Exception as e:
            self.logger.error(f"Error getting recipe ID: {e}")
            
        return None
    
    def get_recipe_cooking_time(self, recipe_name: str) -> Optional[int]:
        """Get cooking time for recipe"""
        try:
            if 'recipes' not in self.data or self.data['recipes'].empty:
                return None
            
            recipes_df = self.data['recipes']
            recipe_mask = recipes_df['recipe_name'].str.lower() == recipe_name.lower()
            matching_recipes = recipes_df[recipe_mask]
            
            if not matching_recipes.empty:
                return int(matching_recipes.iloc[0].get('cook_time', 30))
                
        except Exception as e:
            self.logger.error(f"Error getting recipe cooking time: {e}")
            
        return 30  # Default
    
    def save_inventory(self):
        """Save inventory data to CSV"""
        try:
            inventory_file = os.path.join('data', 'inventory.csv')
            self.data['inventory'].to_csv(inventory_file, index=False)
        except Exception as e:
            self.logger.error(f"Error saving inventory: {e}")

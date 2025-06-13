"""
Category Manager Module
Manages unified category system across inventory, shopping, and budget tabs
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Set, Optional

class CategoryManager:
    """Manages unified categories across all modules"""
    
    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(__name__)
        
        # Standard categories that should exist across all modules
        self.standard_categories = {
            'Vegetables',
            'Fruits', 
            'Grains & Cereals',
            'Dairy Products',
            'Meat & Poultry',
            'Seafood',
            'Spices & Herbs',
            'Oils & Fats',
            'Beverages',
            'Snacks',
            'Frozen Foods',
            'Canned Goods',
            'Bakery Items',
            'Condiments',
            'Cleaning Supplies',
            'Packing Materials',
            'Gas',
            'Utilities',
            'Equipment',
            'Maintenance'
        }
    
    def get_unified_categories(self) -> Set[str]:
        """Get unified set of categories from all modules"""
        all_categories = set(self.standard_categories)
        
        try:
            # Get categories from inventory
            if 'inventory' in self.data and not self.data['inventory'].empty:
                if 'category' in self.data['inventory'].columns:
                    inventory_cats = set(self.data['inventory']['category'].dropna().unique())
                    all_categories.update(inventory_cats)
            
            # Get categories from shopping list
            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                if 'category' in self.data['shopping_list'].columns:
                    shopping_cats = set(self.data['shopping_list']['category'].dropna().unique())
                    all_categories.update(shopping_cats)
            
            # Get categories from budget
            if 'budget' in self.data and not self.data['budget'].empty:
                if 'category' in self.data['budget'].columns:
                    budget_cats = set(self.data['budget']['category'].dropna().unique())
                    all_categories.update(budget_cats)
            
            # Get categories from manual expenses
            if 'manual_expenses' in self.data and not self.data['manual_expenses'].empty:
                if 'category' in self.data['manual_expenses'].columns:
                    expense_cats = set(self.data['manual_expenses']['category'].dropna().unique())
                    all_categories.update(expense_cats)
            
            # Remove empty strings and None values
            all_categories = {cat for cat in all_categories if cat and str(cat).strip()}
            
        except Exception as e:
            self.logger.error(f"Error getting unified categories: {e}")
        
        return all_categories
    
    def synchronize_categories(self) -> Dict[str, any]:
        """Synchronize categories across all modules"""
        result = {
            'success': False,
            'synchronized_modules': [],
            'errors': [],
            'categories_added': 0
        }
        
        try:
            unified_categories = self.get_unified_categories()
            
            # Synchronize inventory categories
            inventory_result = self.sync_inventory_categories(unified_categories)
            if inventory_result['success']:
                result['synchronized_modules'].append('inventory')
                result['categories_added'] += inventory_result['categories_added']
            else:
                result['errors'].extend(inventory_result['errors'])
            
            # Synchronize shopping categories
            shopping_result = self.sync_shopping_categories(unified_categories)
            if shopping_result['success']:
                result['synchronized_modules'].append('shopping')
                result['categories_added'] += shopping_result['categories_added']
            else:
                result['errors'].extend(shopping_result['errors'])
            
            # Synchronize budget categories
            budget_result = self.sync_budget_categories(unified_categories)
            if budget_result['success']:
                result['synchronized_modules'].append('budget')
                result['categories_added'] += budget_result['categories_added']
            else:
                result['errors'].extend(budget_result['errors'])
            
            result['success'] = len(result['synchronized_modules']) > 0
            
            self.logger.info(f"Category synchronization completed: {result}")
            
        except Exception as e:
            self.logger.error(f"Error synchronizing categories: {e}")
            result['errors'].append(str(e))
        
        return result
    
    def sync_inventory_categories(self, unified_categories: Set[str]) -> Dict[str, any]:
        """Synchronize inventory categories"""
        result = {'success': False, 'categories_added': 0, 'errors': []}
        
        try:
            if 'inventory' not in self.data:
                self.data['inventory'] = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'price', 'location', 'notes'
                ])
            
            inventory_df = self.data['inventory']
            
            # Ensure category column exists
            if 'category' not in inventory_df.columns:
                inventory_df['category'] = 'General'
            
            # Update items with missing or invalid categories
            missing_category_mask = inventory_df['category'].isna() | (inventory_df['category'] == '')
            if missing_category_mask.any():
                inventory_df.loc[missing_category_mask, 'category'] = 'General'
                result['categories_added'] += missing_category_mask.sum()
            
            # Save updated inventory
            inventory_file = os.path.join('data', 'inventory.csv')
            inventory_df.to_csv(inventory_file, index=False)
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error syncing inventory categories: {e}")
            result['errors'].append(str(e))
        
        return result
    
    def sync_shopping_categories(self, unified_categories: Set[str]) -> Dict[str, any]:
        """Synchronize shopping list categories"""
        result = {'success': False, 'categories_added': 0, 'errors': []}
        
        try:
            if 'shopping_list' not in self.data:
                self.data['shopping_list'] = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 'priority',
                    'last_price', 'current_price', 'avg_price', 'location', 'notes', 'status', 'date_added'
                ])
            
            shopping_df = self.data['shopping_list']
            
            # Ensure category column exists
            if 'category' not in shopping_df.columns:
                shopping_df['category'] = 'General'
            
            # Update items with missing or invalid categories
            missing_category_mask = shopping_df['category'].isna() | (shopping_df['category'] == '')
            if missing_category_mask.any():
                shopping_df.loc[missing_category_mask, 'category'] = 'General'
                result['categories_added'] += missing_category_mask.sum()
            
            # Save updated shopping list
            shopping_file = os.path.join('data', 'shopping_list.csv')
            shopping_df.to_csv(shopping_file, index=False)
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error syncing shopping categories: {e}")
            result['errors'].append(str(e))
        
        return result
    
    def sync_budget_categories(self, unified_categories: Set[str]) -> Dict[str, any]:
        """Synchronize budget categories"""
        result = {'success': False, 'categories_added': 0, 'errors': []}
        
        try:
            if 'budget' not in self.data:
                self.data['budget'] = pd.DataFrame(columns=[
                    'budget_id', 'category', 'budget_amount', 'actual_amount', 'period', 'notes'
                ])
            
            budget_df = self.data['budget']
            existing_budget_categories = set(budget_df['category'].dropna().unique()) if not budget_df.empty else set()
            
            # Add missing budget categories from other modules
            categories_to_add = unified_categories - existing_budget_categories
            
            for category in categories_to_add:
                # Skip revenue category as it's handled separately
                if category.lower() == 'revenue':
                    continue
                
                # Determine default budget amount based on category
                default_budget = self.get_default_budget_amount(category)
                
                new_budget = pd.DataFrame({
                    'budget_id': [len(budget_df) + 1],
                    'category': [category],
                    'budget_amount': [default_budget],
                    'actual_amount': [0.0],
                    'period': ['Monthly'],
                    'notes': ['Auto-created for category synchronization']
                })
                
                budget_df = pd.concat([budget_df, new_budget], ignore_index=True)
                result['categories_added'] += 1
            
            # Update data
            self.data['budget'] = budget_df
            
            # Save updated budget
            budget_file = os.path.join('data', 'budget.csv')
            budget_df.to_csv(budget_file, index=False)
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error syncing budget categories: {e}")
            result['errors'].append(str(e))
        
        return result
    
    def get_default_budget_amount(self, category: str) -> float:
        """Get default budget amount for a category"""
        category_budgets = {
            'Vegetables': 2000.0,
            'Fruits': 1500.0,
            'Grains & Cereals': 3000.0,
            'Dairy Products': 2500.0,
            'Meat & Poultry': 4000.0,
            'Seafood': 3000.0,
            'Spices & Herbs': 1000.0,
            'Oils & Fats': 800.0,
            'Beverages': 1200.0,
            'Gas': 2000.0,
            'Packing Materials': 1500.0,
            'Utilities': 3000.0,
            'Equipment': 5000.0,
            'Maintenance': 2000.0,
            'Cleaning Supplies': 800.0
        }
        
        return category_budgets.get(category, 1000.0)  # Default 1000 if not found
    
    def get_category_mapping(self) -> Dict[str, str]:
        """Get mapping between different category systems"""
        # This can be used to map categories between different naming conventions
        mapping = {
            'Food': 'General',
            'Grocery': 'General',
            'Kitchen': 'Equipment',
            'Household': 'Cleaning Supplies'
        }
        
        return mapping
    
    def validate_categories(self) -> Dict[str, any]:
        """Validate category consistency across modules"""
        result = {
            'valid': True,
            'issues': [],
            'recommendations': []
        }
        
        try:
            unified_categories = self.get_unified_categories()
            
            # Check for orphaned categories (categories that exist in only one module)
            inventory_cats = set()
            shopping_cats = set()
            budget_cats = set()
            
            if 'inventory' in self.data and not self.data['inventory'].empty:
                if 'category' in self.data['inventory'].columns:
                    inventory_cats = set(self.data['inventory']['category'].dropna().unique())
            
            if 'shopping_list' in self.data and not self.data['shopping_list'].empty:
                if 'category' in self.data['shopping_list'].columns:
                    shopping_cats = set(self.data['shopping_list']['category'].dropna().unique())
            
            if 'budget' in self.data and not self.data['budget'].empty:
                if 'category' in self.data['budget'].columns:
                    budget_cats = set(self.data['budget']['category'].dropna().unique())
            
            # Find orphaned categories
            inventory_only = inventory_cats - shopping_cats - budget_cats
            shopping_only = shopping_cats - inventory_cats - budget_cats
            budget_only = budget_cats - inventory_cats - shopping_cats
            
            if inventory_only:
                result['issues'].append(f"Categories only in inventory: {', '.join(inventory_only)}")
                result['recommendations'].append("Consider adding these categories to shopping and budget")
            
            if shopping_only:
                result['issues'].append(f"Categories only in shopping: {', '.join(shopping_only)}")
                result['recommendations'].append("Consider adding these categories to inventory and budget")
            
            if budget_only:
                result['issues'].append(f"Categories only in budget: {', '.join(budget_only)}")
                result['recommendations'].append("Consider adding these categories to inventory and shopping")
            
            result['valid'] = len(result['issues']) == 0
            
        except Exception as e:
            self.logger.error(f"Error validating categories: {e}")
            result['issues'].append(str(e))
            result['valid'] = False
        
        return result

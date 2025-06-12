"""
Smart Ingredient Manager
Automatically detects missing ingredients and adds them to inventory with intelligent categorization
"""

import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QMessageBox

# Import activity tracker
try:
    from .activity_tracker import track_user_action, track_data_change, track_system_event
except ImportError:
    def track_user_action(*args, **kwargs): pass
    def track_data_change(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

# Import notification system
try:
    from .notification_system import notify_info, notify_success, notify_warning, notify_error
except ImportError:
    def notify_info(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_success(title, message, **kwargs): logging.info(f"{title}: {message}")
    def notify_warning(title, message, **kwargs): logging.warning(f"{title}: {message}")
    def notify_error(title, message, **kwargs): logging.error(f"{title}: {message}")

class SmartIngredientManager(QObject):
    """
    Intelligent ingredient management system that:
    1. Detects missing ingredients when planning meals
    2. Automatically adds them to inventory with smart categorization
    3. Provides notifications for all ingredient additions
    4. Maintains ingredient database with learning capabilities
    """
    
    ingredient_added = Signal(str, str, float)  # ingredient_name, category, quantity
    missing_ingredients_detected = Signal(list)  # list of missing ingredients
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data = data_manager
        self.logger = logging.getLogger(__name__)

        # Reference to main app for bell notifications
        self.main_app = None

        # Initialize ingredient knowledge base
        self.ingredient_categories = self.load_ingredient_categories()
        self.ingredient_units = self.load_ingredient_units()
        self.ingredient_costs = self.load_ingredient_costs()

        # Auto-check timer (disabled by default - use manual button instead)
        self.auto_check_timer = QTimer()
        self.auto_check_timer.timeout.connect(self.check_missing_ingredients)
        # self.auto_check_timer.start(30000)  # Disabled - use manual button instead

        self.logger.info("Smart Ingredient Manager initialized")

    def enable_auto_check(self, enabled=True):
        """Enable or disable automatic ingredient checking"""
        if enabled:
            if not self.auto_check_timer.isActive():
                self.auto_check_timer.start(30000)  # Check every 30 seconds
                self.logger.info("Auto ingredient checking enabled")
        else:
            if self.auto_check_timer.isActive():
                self.auto_check_timer.stop()
                self.logger.info("Auto ingredient checking disabled")

    def manual_ingredient_check(self):
        """Manually trigger ingredient check and add missing ones"""
        try:
            self.logger.info("Manual ingredient check triggered")

            # Show notification that check is starting
            self.send_bell_notification(
                "Ingredient Check",
                "Scanning recipes for missing ingredients...",
                "info"
            )

            # Perform the check
            self.check_missing_ingredients()

            return True
        except Exception as e:
            self.logger.error(f"Error in manual ingredient check: {e}")
            self.send_bell_notification(
                "Ingredient Check Error",
                f"Failed to check ingredients: {e}",
                "error"
            )
            return False

    def set_main_app(self, main_app):
        """Set reference to main app for bell notifications"""
        self.main_app = main_app
        self.logger.info("Connected to main app notification system")

    def send_bell_notification(self, title, message, notification_type="info"):
        """Send notification to bell icon if available"""
        if self.main_app and hasattr(self.main_app, 'add_notification'):
            try:
                self.main_app.add_notification(title, message, notification_type)
                return True
            except Exception as e:
                self.logger.error(f"Error sending bell notification: {e}")
        return False
    
    def load_ingredient_categories(self) -> Dict[str, str]:
        """Load ingredient categorization knowledge base"""
        categories = {
            # Spices and Seasonings
            'salt': 'Spices', 'pepper': 'Spices', 'turmeric': 'Spices', 'cumin': 'Spices',
            'coriander': 'Spices', 'garam masala': 'Spices', 'red chili powder': 'Spices',
            'black pepper': 'Spices', 'cardamom': 'Spices', 'cinnamon': 'Spices',
            'cloves': 'Spices', 'bay leaves': 'Spices', 'mustard seeds': 'Spices',
            'fenugreek': 'Spices', 'asafoetida': 'Spices', 'ginger': 'Spices',
            'garlic': 'Spices', 'green chili': 'Spices', 'curry leaves': 'Spices',
            
            # Oils and Fats
            'oil': 'Oils', 'olive oil': 'Oils', 'coconut oil': 'Oils', 'ghee': 'Oils',
            'butter': 'Dairy', 'sunflower oil': 'Oils', 'sesame oil': 'Oils',
            
            # Grains and Cereals
            'rice': 'Grains', 'wheat': 'Grains', 'flour': 'Grains', 'wheat flour': 'Grains',
            'rice flour': 'Grains', 'semolina': 'Grains', 'oats': 'Grains',
            'quinoa': 'Grains', 'barley': 'Grains', 'millet': 'Grains',
            
            # Legumes and Pulses
            'dal': 'Legumes', 'lentils': 'Legumes', 'chickpeas': 'Legumes',
            'black beans': 'Legumes', 'kidney beans': 'Legumes', 'green peas': 'Legumes',
            'black gram': 'Legumes', 'pigeon peas': 'Legumes',
            
            # Vegetables
            'onion': 'Vegetables', 'tomato': 'Vegetables', 'potato': 'Vegetables',
            'carrot': 'Vegetables', 'cabbage': 'Vegetables', 'cauliflower': 'Vegetables',
            'broccoli': 'Vegetables', 'spinach': 'Vegetables', 'lettuce': 'Vegetables',
            'bell pepper': 'Vegetables', 'cucumber': 'Vegetables', 'eggplant': 'Vegetables',
            
            # Fruits
            'apple': 'Fruits', 'banana': 'Fruits', 'orange': 'Fruits', 'mango': 'Fruits',
            'grapes': 'Fruits', 'strawberry': 'Fruits', 'lemon': 'Fruits', 'lime': 'Fruits',
            
            # Dairy
            'milk': 'Dairy', 'yogurt': 'Dairy', 'cheese': 'Dairy', 'paneer': 'Dairy',
            'cream': 'Dairy', 'buttermilk': 'Dairy',
            
            # Meat and Poultry
            'chicken': 'Meat', 'beef': 'Meat', 'pork': 'Meat', 'lamb': 'Meat',
            'fish': 'Seafood', 'shrimp': 'Seafood', 'crab': 'Seafood',
            
            # Eggs
            'eggs': 'Dairy', 'egg': 'Dairy',
            
            # Baking
            'sugar': 'Baking', 'brown sugar': 'Baking', 'baking powder': 'Baking',
            'baking soda': 'Baking', 'vanilla': 'Baking', 'yeast': 'Baking',
            
            # Nuts and Seeds
            'almonds': 'Nuts', 'cashews': 'Nuts', 'peanuts': 'Nuts', 'walnuts': 'Nuts',
            'sesame seeds': 'Seeds', 'sunflower seeds': 'Seeds',
            
            # Prepared Items
            'dosa batter': 'Prepared', 'idli batter': 'Prepared', 'sambhar': 'Prepared',
            'coconut chutni': 'Prepared', 'tomato chutni': 'Prepared', 'chicken gravy': 'Prepared',
            'fish kolambu': 'Prepared'
        }
        return categories
    
    def load_ingredient_units(self) -> Dict[str, str]:
        """Load ingredient unit knowledge base"""
        units = {
            # Liquids
            'oil': 'ml', 'milk': 'ml', 'water': 'ml', 'coconut oil': 'ml',
            'ghee': 'ml', 'sambhar': 'ml', 'coconut chutni': 'ml', 'tomato chutni': 'ml',
            'chicken gravy': 'ml', 'fish kolambu': 'ml',

            # Solids by weight
            'rice': 'grams', 'flour': 'grams', 'sugar': 'grams', 'salt': 'grams', 'turmeric': 'grams',
            'chicken': 'grams', 'beef': 'grams', 'fish': 'grams', 'paneer': 'grams',
            'onion': 'grams', 'tomato': 'grams', 'potato': 'grams', 'ginger': 'grams', 'garlic': 'grams',
            'dosa batter': 'grams', 'idli batter': 'grams',

            # Count-based
            'eggs': 'units', 'egg': 'units', 'green chili': 'units',
            'bay leaves': 'units', 'cardamom': 'units', 'cloves': 'units'
        }
        return units
    
    def load_ingredient_costs(self) -> Dict[str, float]:
        """Load ingredient cost knowledge base (per unit)"""
        costs = {
            # Common ingredients with estimated costs per unit
            'oil': 0.15,  # per ml
            'rice': 0.08,  # per g
            'flour': 0.05,  # per g
            'onion': 0.04,  # per g
            'tomato': 0.06,  # per g
            'potato': 0.03,  # per g
            'chicken': 0.25,  # per g
            'eggs': 8.0,   # per unit
            'milk': 0.06,  # per ml
            'sugar': 0.04,  # per g
            'salt': 0.02,  # per g
            'turmeric': 0.50,  # per g
            'ginger': 0.15,  # per g
            'garlic': 0.20,  # per g
            'ghee': 0.80,  # per ml
            'paneer': 0.40,  # per g
            'dosa batter': 0.08,  # per g
            'sambhar': 0.12,  # per ml
            'coconut chutni': 0.10,  # per ml
            'tomato chutni': 0.08,  # per ml
            'chicken gravy': 0.20,  # per ml
            'fish kolambu': 0.25   # per ml
        }
        return costs
    
    def categorize_ingredient(self, ingredient_name: str) -> str:
        """Intelligently categorize an ingredient"""
        ingredient_lower = ingredient_name.lower().strip()
        
        # Direct match
        if ingredient_lower in self.ingredient_categories:
            return self.ingredient_categories[ingredient_lower]
        
        # Partial match
        for known_ingredient, category in self.ingredient_categories.items():
            if known_ingredient in ingredient_lower or ingredient_lower in known_ingredient:
                return category
        
        # Keyword-based categorization
        if any(word in ingredient_lower for word in ['oil', 'ghee']):
            return 'Oils'
        elif any(word in ingredient_lower for word in ['powder', 'masala', 'spice']):
            return 'Spices'
        elif any(word in ingredient_lower for word in ['flour', 'rice', 'wheat']):
            return 'Grains'
        elif any(word in ingredient_lower for word in ['dal', 'lentil', 'bean']):
            return 'Legumes'
        elif any(word in ingredient_lower for word in ['chicken', 'beef', 'meat', 'fish']):
            return 'Meat'
        elif any(word in ingredient_lower for word in ['milk', 'cheese', 'yogurt', 'paneer']):
            return 'Dairy'
        elif any(word in ingredient_lower for word in ['chutni', 'gravy', 'kolambu', 'sambhar', 'batter']):
            return 'Prepared'
        
        return 'Unknown'
    
    def get_ingredient_unit(self, ingredient_name: str) -> str:
        """Get appropriate unit for an ingredient"""
        ingredient_lower = ingredient_name.lower().strip()
        
        # Direct match
        if ingredient_lower in self.ingredient_units:
            return self.ingredient_units[ingredient_lower]
        
        # Partial match
        for known_ingredient, unit in self.ingredient_units.items():
            if known_ingredient in ingredient_lower:
                return unit
        
        # Default based on category
        category = self.categorize_ingredient(ingredient_name)
        if category in ['Oils', 'Prepared']:
            return 'ml'
        elif category in ['Dairy'] and 'egg' in ingredient_lower:
            return 'units'
        else:
            return 'grams'
    
    def get_ingredient_cost(self, ingredient_name: str) -> float:
        """Get estimated cost for an ingredient"""
        ingredient_lower = ingredient_name.lower().strip()
        
        # Direct match
        if ingredient_lower in self.ingredient_costs:
            return self.ingredient_costs[ingredient_lower]
        
        # Partial match
        for known_ingredient, cost in self.ingredient_costs.items():
            if known_ingredient in ingredient_lower:
                return cost
        
        # Default based on category
        category = self.categorize_ingredient(ingredient_name)
        defaults = {
            'Spices': 0.30,
            'Oils': 0.15,
            'Grains': 0.06,
            'Legumes': 0.08,
            'Vegetables': 0.05,
            'Fruits': 0.08,
            'Dairy': 0.10,
            'Meat': 0.25,
            'Seafood': 0.30,
            'Baking': 0.05,
            'Nuts': 0.50,
            'Seeds': 0.40,
            'Prepared': 0.15,
            'Unknown': 0.10
        }
        return defaults.get(category, 0.10)
    
    def check_missing_ingredients(self):
        """Check for missing ingredients in current meal plans"""
        try:
            if 'meal_plan' not in self.data or 'recipe_ingredients' not in self.data:
                return
            
            meal_plan = self.data['meal_plan']
            recipe_ingredients = self.data['recipe_ingredients']
            inventory = self.data.get('inventory', pd.DataFrame())
            
            if meal_plan.empty or recipe_ingredients.empty:
                return
            
            # Get all required ingredients from current meal plans
            required_ingredients = set()
            
            for _, meal in meal_plan.iterrows():
                recipe_id = meal.get('recipe_id')
                if pd.notna(recipe_id):
                    recipe_items = recipe_ingredients[recipe_ingredients['recipe_id'] == recipe_id]
                    for _, item in recipe_items.iterrows():
                        ingredient_name = item.get('item_name', '').strip()
                        if ingredient_name:
                            required_ingredients.add(ingredient_name.lower())
            
            # Check which ingredients are missing from inventory
            if not inventory.empty:
                available_ingredients = set(inventory['item_name'].str.lower().tolist())
            else:
                available_ingredients = set()
            
            missing_ingredients = required_ingredients - available_ingredients
            
            if missing_ingredients:
                self.auto_add_missing_ingredients(list(missing_ingredients))
                self.missing_ingredients_detected.emit(list(missing_ingredients))
                
        except Exception as e:
            self.logger.error(f"Error checking missing ingredients: {e}")
    
    def auto_add_missing_ingredients(self, missing_ingredients: List[str]):
        """Automatically add missing ingredients to inventory"""
        try:
            if 'inventory' not in self.data:
                self.data['inventory'] = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'quantity', 'unit', 
                    'price', 'location', 'expiry_date', 'reorder_level',
                    'qty_purchased', 'qty_used', 'avg_price'
                ])
            
            inventory = self.data['inventory']
            added_count = 0
            
            for ingredient_name in missing_ingredients:
                # Check if already exists (case-insensitive)
                existing = inventory[inventory['item_name'].str.lower() == ingredient_name.lower()]
                if not existing.empty:
                    continue
                
                # Generate new item ID
                if not inventory.empty:
                    max_id = inventory['item_id'].max()
                    new_id = max_id + 1 if pd.notna(max_id) else 1
                else:
                    new_id = 1
                
                # Get intelligent categorization
                category = self.categorize_ingredient(ingredient_name)
                unit = self.get_ingredient_unit(ingredient_name)
                cost = self.get_ingredient_cost(ingredient_name)
                
                # Create new inventory entry
                new_item = {
                    'item_id': new_id,
                    'item_name': ingredient_name.title(),
                    'category': category,
                    'quantity': 0.0,  # Start with 0 quantity
                    'unit': unit,
                    'price': cost,
                    'location': 'Unknown',
                    'expiry_date': '',
                    'reorder_level': 1.0,
                    'qty_purchased': 0.0,
                    'qty_used': 0.0,
                    'avg_price': cost
                }
                
                # Add to inventory
                new_row = pd.DataFrame([new_item])
                self.data['inventory'] = pd.concat([inventory, new_row], ignore_index=True)
                
                # Also add to items if it doesn't exist
                if 'items' in self.data:
                    items = self.data['items']
                    existing_item = items[items['item_name'].str.lower() == ingredient_name.lower()]
                    if existing_item.empty:
                        new_item_entry = {
                            'item_id': new_id,
                            'item_name': ingredient_name.title(),
                            'category': category,
                            'description': f'Auto-added {category.lower()} ingredient',
                            'unit': unit,
                            'default_cost': cost
                        }
                        new_item_row = pd.DataFrame([new_item_entry])
                        self.data['items'] = pd.concat([items, new_item_row], ignore_index=True)
                
                added_count += 1
                
                # Emit signal
                self.ingredient_added.emit(ingredient_name.title(), category, 0.0)

                # Track the activity
                track_data_change(
                    "smart_ingredient_manager",
                    "auto_add_ingredient",
                    f"Auto-added ingredient '{ingredient_name.title()}' with category '{category}'",
                    data_before={"ingredient_count": len(self.data['inventory']) - 1},
                    data_after={"ingredient_count": len(self.data['inventory'])},
                    metadata={
                        "ingredient_name": ingredient_name.title(),
                        "category": category,
                        "auto_detected": True
                    }
                )

                # Show notification in bell icon
                self.send_bell_notification(
                    "Ingredient Added",
                    f"'{ingredient_name.title()}' added to inventory with category '{category}'",
                    "success"
                )

                # Also show traditional notification as fallback
                notify_success(
                    "Ingredient Added",
                    f"'{ingredient_name.title()}' added to inventory with category '{category}'",
                    duration=5000
                )
                
                self.logger.info(f"Auto-added ingredient: {ingredient_name.title()} (Category: {category})")
            
            if added_count > 0:
                # Save data
                self.save_inventory_data()
                
                # Summary notification in bell icon
                self.send_bell_notification(
                    "Smart Ingredient Detection",
                    f"Added {added_count} missing ingredients to inventory",
                    "info"
                )

                # Also show traditional notification as fallback
                notify_info(
                    "Smart Ingredient Detection",
                    f"Added {added_count} missing ingredients to inventory",
                    duration=7000
                )
                
                self.logger.info(f"Auto-added {added_count} missing ingredients to inventory")
                
        except Exception as e:
            self.logger.error(f"Error auto-adding missing ingredients: {e}")
            notify_error(
                "Error",
                f"Failed to add missing ingredients: {str(e)}",
                duration=10000
            )
    
    def save_inventory_data(self):
        """Save inventory data to CSV"""
        try:
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            if 'inventory' in self.data:
                inventory_file = os.path.join(data_dir, 'inventory.csv')
                self.data['inventory'].to_csv(inventory_file, index=False)
            
            if 'items' in self.data:
                items_file = os.path.join(data_dir, 'items.csv')
                self.data['items'].to_csv(items_file, index=False)
                
        except Exception as e:
            self.logger.error(f"Error saving inventory data: {e}")
    
    def manually_add_ingredient(self, ingredient_name: str, category: str = None, 
                              quantity: float = 0.0, unit: str = None, cost: float = None):
        """Manually add an ingredient with specified parameters"""
        try:
            # Use intelligent defaults if not specified
            if category is None:
                category = self.categorize_ingredient(ingredient_name)
            if unit is None:
                unit = self.get_ingredient_unit(ingredient_name)
            if cost is None:
                cost = self.get_ingredient_cost(ingredient_name)
            
            # Add to missing ingredients list to trigger auto-add
            self.auto_add_missing_ingredients([ingredient_name])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error manually adding ingredient: {e}")
            return False

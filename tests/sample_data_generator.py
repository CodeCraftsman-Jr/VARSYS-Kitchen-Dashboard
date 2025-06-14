"""
Sample Data Generator
Generates comprehensive sample data for testing all modules
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class SampleDataGenerator:
    """Generates realistic sample data for testing"""

    def __init__(self):
        self.categories = [
            'Vegetables', 'Fruits', 'Grains & Cereals', 'Dairy Products',
            'Meat & Poultry', 'Seafood', 'Spices & Herbs', 'Oils & Fats',
            'Beverages', 'Snacks', 'Frozen Foods', 'Canned Goods',
            'Bakery Items', 'Condiments', 'Cleaning Supplies', 'Packing Materials'
        ]

        self.units = ['kg', 'grams', 'liters', 'ml', 'pieces', 'packs', 'bottles', 'cans']
        self.locations = ['Fridge', 'Pantry', 'Freezer', 'Storage Room', 'Dry Storage']
        self.priorities = ['High', 'Medium', 'Low']
        self.meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Realistic item names by category
        self.items_by_category = {
            'Vegetables': ['Tomatoes', 'Onions', 'Potatoes', 'Carrots', 'Bell Peppers', 'Spinach', 'Lettuce', 'Broccoli', 'Cauliflower', 'Cabbage'],
            'Fruits': ['Apples', 'Bananas', 'Oranges', 'Grapes', 'Strawberries', 'Mangoes', 'Pineapple', 'Watermelon', 'Lemons', 'Limes'],
            'Grains & Cereals': ['Rice', 'Wheat Flour', 'Oats', 'Quinoa', 'Barley', 'Pasta', 'Bread', 'Cornflakes', 'Muesli', 'Noodles'],
            'Dairy Products': ['Milk', 'Cheese', 'Yogurt', 'Butter', 'Cream', 'Cottage Cheese', 'Sour Cream', 'Ice Cream', 'Condensed Milk', 'Paneer'],
            'Meat & Poultry': ['Chicken Breast', 'Ground Beef', 'Pork Chops', 'Lamb', 'Turkey', 'Bacon', 'Sausages', 'Ham', 'Chicken Thighs', 'Beef Steak'],
            'Seafood': ['Salmon', 'Tuna', 'Shrimp', 'Cod', 'Crab', 'Lobster', 'Sardines', 'Mackerel', 'Prawns', 'Fish Fillets'],
            'Spices & Herbs': ['Salt', 'Black Pepper', 'Turmeric', 'Cumin', 'Coriander', 'Garam Masala', 'Basil', 'Oregano', 'Thyme', 'Garlic Powder'],
            'Oils & Fats': ['Olive Oil', 'Vegetable Oil', 'Coconut Oil', 'Sunflower Oil', 'Ghee', 'Sesame Oil', 'Avocado Oil', 'Canola Oil', 'Palm Oil', 'Mustard Oil'],
            'Beverages': ['Water', 'Juice', 'Soda', 'Tea', 'Coffee', 'Energy Drinks', 'Sports Drinks', 'Coconut Water', 'Milk Shakes', 'Smoothies'],
            'Cleaning Supplies': ['Dish Soap', 'All-Purpose Cleaner', 'Bleach', 'Sponges', 'Paper Towels', 'Trash Bags', 'Disinfectant', 'Floor Cleaner', 'Glass Cleaner', 'Scrub Brushes'],
            'Packing Materials': ['Small Boxes', 'Medium Boxes', 'Large Boxes', 'Bubble Wrap', 'Packing Tape', 'Food Containers', 'Plastic Bags', 'Paper Bags', 'Aluminum Foil', 'Cling Wrap']
        }

    def generate_all_sample_data(self, save_to_files=True):
        """Generate all sample data"""
        data = {}

        # Generate each dataset
        data['inventory'] = self.generate_inventory_data()
        data['shopping_list'] = self.generate_shopping_data()
        data['recipes'] = self.generate_recipe_data()
        data['recipe_ingredients'] = self.generate_recipe_ingredients_data(data['recipes'])
        data['meal_plan'] = self.generate_meal_plan_data(data['recipes'])
        data['sales'] = self.generate_sales_data(data['recipes'])
        data['budget'] = self.generate_budget_data()
        data['waste'] = self.generate_waste_data()
        data['cleaning_maintenance'] = self.generate_cleaning_data()
        data['items'] = self.generate_items_data()
        data['categories'] = self.generate_categories_data()
        data['pricing'] = self.generate_pricing_data(data['recipes'])
        data['packing_materials'] = self.generate_packing_materials_data()
        data['recipe_packing_materials'] = self.generate_recipe_packing_data(data['recipes'], data['packing_materials'])
        data['sales_orders'] = self.generate_sales_orders_data(data['recipes'])

        if save_to_files:
            self.save_data_to_files(data)

        return data

    def generate_inventory_data(self, num_items=200):
        """Generate realistic inventory data"""
        items = []
        item_id = 1

        for category in self.categories:
            if category in self.items_by_category:
                category_items = self.items_by_category[category]
                for item_name in category_items:
                    items.append({
                        'item_id': item_id,
                        'item_name': item_name,
                        'category': category,
                        'quantity': random.randint(1, 100),
                        'unit': random.choice(self.units),
                        'price_per_unit': round(random.uniform(10, 500), 2),
                        'location': random.choice(self.locations),
                        'expiry_date': (datetime.now() + timedelta(days=random.randint(1, 365))).date(),
                        'reorder_level': random.randint(1, 20),
                        'total_value': 0,  # Will be calculated
                        'price': 0,  # Will be calculated
                        'qty_purchased': random.randint(50, 500),
                        'qty_used': random.randint(10, 200),
                        'avg_price': round(random.uniform(10, 500), 2),
                        'description': f'High quality {item_name.lower()}',
                        'default_cost': round(random.uniform(10, 500), 2),
                        'purchase_count': random.randint(1, 50),
                        'total_spent': round(random.uniform(100, 5000), 2),
                        'last_purchase_date': (datetime.now() - timedelta(days=random.randint(1, 90))).date(),
                        'last_purchase_price': round(random.uniform(10, 500), 2)
                    })
                    item_id += 1

        df = pd.DataFrame(items)

        # Calculate derived fields
        df['total_value'] = df['quantity'] * df['price_per_unit']
        df['price'] = df['price_per_unit']

        return df

    def generate_shopping_data(self, num_items=100):
        """Generate shopping list data"""
        items = []
        item_id = 1

        for i in range(num_items):
            category = random.choice(self.categories)
            if category in self.items_by_category:
                item_name = random.choice(self.items_by_category[category])
            else:
                item_name = f'Item_{i}'

            items.append({
                'item_id': item_id,
                'item_name': item_name,
                'category': category,
                'quantity': random.randint(1, 20),
                'unit': random.choice(self.units),
                'priority': random.choice(self.priorities),
                'last_price': round(random.uniform(10, 200), 2),
                'current_price': round(random.uniform(10, 200), 2),
                'avg_price': round(random.uniform(10, 200), 2),
                'location': random.choice(['Market A', 'Market B', 'Supermarket', 'Online']),
                'notes': f'Notes for {item_name}',
                'status': random.choice(['Pending', 'Purchased', 'Cancelled']),
                'date_added': (datetime.now() - timedelta(days=random.randint(0, 30))).date(),
                'date_purchased': (datetime.now() - timedelta(days=random.randint(0, 7))).date() if random.choice([True, False]) else None
            })
            item_id += 1

        return pd.DataFrame(items)

    def generate_recipe_data(self, num_recipes=50):
        """Generate recipe data"""
        recipe_names = [
            'Pasta Marinara', 'Chicken Curry', 'Vegetable Stir Fry', 'Caesar Salad', 'Tomato Soup',
            'Grilled Salmon', 'Beef Tacos', 'Mushroom Risotto', 'Greek Salad', 'Chicken Sandwich',
            'Vegetable Biryani', 'Fish and Chips', 'Pancakes', 'French Toast', 'Omelette',
            'Fried Rice', 'Spaghetti Carbonara', 'Chicken Tikka', 'Vegetable Curry', 'Beef Stew',
            'Chocolate Cake', 'Vanilla Ice Cream', 'Apple Pie', 'Banana Bread', 'Cookies',
            'Pizza Margherita', 'Burger', 'Hot Dog', 'Sandwich', 'Wrap',
            'Smoothie Bowl', 'Protein Shake', 'Green Salad', 'Fruit Salad', 'Soup',
            'Grilled Chicken', 'Baked Fish', 'Roast Beef', 'Lamb Curry', 'Pork Chops',
            'Vegetable Soup', 'Lentil Dal', 'Chickpea Curry', 'Spinach Curry', 'Potato Curry',
            'Fried Chicken', 'BBQ Ribs', 'Grilled Vegetables', 'Stuffed Peppers', 'Lasagna'
        ]

        recipe_categories = ['Main Course', 'Appetizer', 'Dessert', 'Soup', 'Salad', 'Breakfast', 'Snack', 'Beverage']

        recipes = []
        for i in range(min(num_recipes, len(recipe_names))):
            recipes.append({
                'recipe_id': i + 1,
                'recipe_name': recipe_names[i],
                'category': random.choice(recipe_categories),
                'servings': random.randint(1, 8),
                'prep_time': random.randint(5, 60),
                'cook_time': random.randint(0, 120),
                'description': f'Delicious {recipe_names[i].lower()} recipe',
                'ingredients': f'Ingredients for {recipe_names[i]}',
                'instructions': f'Instructions for making {recipe_names[i]}'
            })

        return pd.DataFrame(recipes)

    def generate_recipe_ingredients_data(self, recipes_df):
        """Generate recipe ingredients data"""
        ingredients = []

        for _, recipe in recipes_df.iterrows():
            # Each recipe has 3-8 ingredients
            num_ingredients = random.randint(3, 8)

            for i in range(num_ingredients):
                # Pick random category and item
                category = random.choice(list(self.items_by_category.keys()))
                item_name = random.choice(self.items_by_category[category])

                ingredients.append({
                    'recipe_id': recipe['recipe_id'],
                    'ingredient_id': len(ingredients) + 1,
                    'item_name': item_name,
                    'quantity': random.randint(50, 500),
                    'unit': random.choice(['g', 'ml', 'pieces', 'cups', 'tbsp', 'tsp']),
                    'notes': f'Fresh {item_name.lower()}'
                })

        return pd.DataFrame(ingredients)

    def generate_meal_plan_data(self, recipes_df):
        """Generate meal plan data"""
        meal_plans = []

        for day in self.days:
            for meal_type in self.meal_types:
                if random.choice([True, False, True]):  # 66% chance of having a meal planned
                    recipe = recipes_df.sample(1).iloc[0]
                    meal_plans.append({
                        'day': day,
                        'meal_type': meal_type,
                        'recipe_id': recipe['recipe_id'],
                        'recipe_name': recipe['recipe_name'],
                        'servings': random.randint(1, 6),
                        'prep_time': recipe['prep_time'],
                        'cook_time': recipe['cook_time']
                    })

        return pd.DataFrame(meal_plans)

    def generate_sales_data(self, recipes_df, num_sales=500):
        """Generate sales data"""
        sales = []

        for i in range(num_sales):
            recipe = recipes_df.sample(1).iloc[0]
            quantity = random.randint(1, 10)
            price_per_unit = round(random.uniform(50, 500), 2)

            sales.append({
                'sale_id': i + 1,
                'item_name': recipe['recipe_name'],
                'quantity': quantity,
                'price_per_unit': price_per_unit,
                'total_amount': quantity * price_per_unit,
                'customer': f'Customer_{random.randint(1, 100)}',
                'date': (datetime.now() - timedelta(days=random.randint(0, 365))).date()
            })

        return pd.DataFrame(sales)

    def generate_budget_data(self):
        """Generate budget data"""
        budgets = []

        for i, category in enumerate(self.categories):
            budgets.append({
                'budget_id': i + 1,
                'category': category,
                'amount': round(random.uniform(1000, 10000), 2),
                'period': random.choice(['Weekly', 'Monthly', 'Quarterly']),
                'date': datetime.now().date()
            })

        return pd.DataFrame(budgets)

    def generate_waste_data(self, num_waste=100):
        """Generate waste data"""
        waste_reasons = ['Expired', 'Spoiled', 'Burnt', 'Overripe', 'Contaminated', 'Damaged', 'Excess']
        waste_items = []

        for i in range(num_waste):
            category = random.choice(list(self.items_by_category.keys()))
            item_name = random.choice(self.items_by_category[category])

            waste_items.append({
                'waste_id': i + 1,
                'item_name': item_name,
                'quantity': round(random.uniform(0.1, 10), 2),
                'unit': random.choice(self.units),
                'reason': random.choice(waste_reasons),
                'cost': round(random.uniform(10, 500), 2),
                'date': (datetime.now() - timedelta(days=random.randint(0, 90))).date()
            })

        return pd.DataFrame(waste_items)

    def generate_cleaning_data(self):
        """Generate cleaning and maintenance data"""
        cleaning_tasks = [
            'Clean Kitchen Counters', 'Sanitize Equipment', 'Mop Floors', 'Clean Refrigerator',
            'Wash Dishes', 'Clean Stove', 'Sanitize Cutting Boards', 'Clean Sink',
            'Empty Trash', 'Wipe Tables', 'Clean Windows', 'Organize Pantry',
            'Deep Clean Oven', 'Descale Coffee Machine', 'Clean Exhaust Fan'
        ]

        frequencies = ['Daily', 'Weekly', 'Monthly', 'Quarterly']

        tasks = []
        for i, task_name in enumerate(cleaning_tasks):
            frequency = random.choice(frequencies)
            last_completed = datetime.now() - timedelta(days=random.randint(0, 30))

            # Calculate next due date based on frequency
            if frequency == 'Daily':
                next_due = last_completed + timedelta(days=1)
            elif frequency == 'Weekly':
                next_due = last_completed + timedelta(weeks=1)
            elif frequency == 'Monthly':
                next_due = last_completed + timedelta(days=30)
            else:  # Quarterly
                next_due = last_completed + timedelta(days=90)

            tasks.append({
                'task_id': i + 1,
                'task_name': task_name,
                'frequency': frequency,
                'last_completed': last_completed.date(),
                'next_due': next_due.date(),
                'priority': random.choice(self.priorities),
                'notes': f'Notes for {task_name}'
            })

        return pd.DataFrame(tasks)

    def generate_items_data(self):
        """Generate items master data"""
        items = []
        item_id = 1

        for category in self.categories:
            if category in self.items_by_category:
                for item_name in self.items_by_category[category]:
                    items.append({
                        'item_id': item_id,
                        'item_name': item_name,
                        'category': category,
                        'description': f'High quality {item_name.lower()}',
                        'unit': random.choice(self.units),
                        'default_cost': round(random.uniform(10, 500), 2)
                    })
                    item_id += 1

        return pd.DataFrame(items)

    def generate_categories_data(self):
        """Generate categories data"""
        categories = []

        for i, category_name in enumerate(self.categories):
            categories.append({
                'category_id': i + 1,
                'category_name': category_name,
                'description': f'Category for {category_name.lower()}'
            })

        return pd.DataFrame(categories)

    def generate_pricing_data(self, recipes_df):
        """Generate pricing data"""
        pricing = []

        for _, recipe in recipes_df.iterrows():
            total_cost = round(random.uniform(50, 300), 2)
            cost_per_serving = round(total_cost / recipe['servings'], 2)

            pricing.append({
                'recipe_id': recipe['recipe_id'],
                'recipe_name': recipe['recipe_name'],
                'total_cost': total_cost,
                'cost_per_serving': cost_per_serving,
                'last_calculated': datetime.now().date()
            })

        return pd.DataFrame(pricing)

    def generate_packing_materials_data(self):
        """Generate packing materials data"""
        materials = [
            {'name': 'Small Box', 'category': 'Boxes', 'size': 'Small', 'cost': 5.0},
            {'name': 'Medium Box', 'category': 'Boxes', 'size': 'Medium', 'cost': 8.0},
            {'name': 'Large Box', 'category': 'Boxes', 'size': 'Large', 'cost': 12.0},
            {'name': 'Bubble Wrap', 'category': 'Protection', 'size': 'Roll', 'cost': 2.0},
            {'name': 'Packing Tape', 'category': 'Adhesive', 'size': 'Roll', 'cost': 1.5},
            {'name': 'Food Containers', 'category': 'Containers', 'size': 'Various', 'cost': 15.0},
            {'name': 'Plastic Bags', 'category': 'Bags', 'size': 'Small', 'cost': 0.5},
            {'name': 'Paper Bags', 'category': 'Bags', 'size': 'Medium', 'cost': 1.0},
            {'name': 'Aluminum Foil', 'category': 'Wrapping', 'size': 'Roll', 'cost': 3.0},
            {'name': 'Cling Wrap', 'category': 'Wrapping', 'size': 'Roll', 'cost': 2.5}
        ]

        packing_data = []
        for i, material in enumerate(materials):
            packing_data.append({
                'material_id': i + 1,
                'material_name': material['name'],
                'category': material['category'],
                'size': material['size'],
                'unit': 'piece' if material['category'] in ['Boxes', 'Containers'] else 'meter',
                'cost_per_unit': material['cost'],
                'current_stock': random.randint(50, 500),
                'minimum_stock': random.randint(10, 50),
                'supplier': random.choice(['Supplier A', 'Supplier B', 'Supplier C']),
                'notes': f'Notes for {material["name"]}',
                'date_added': datetime.now().date()
            })

        return pd.DataFrame(packing_data)

    def generate_recipe_packing_data(self, recipes_df, packing_df):
        """Generate recipe packing materials data"""
        recipe_packing = []

        for _, recipe in recipes_df.iterrows():
            # Each recipe uses 1-3 packing materials
            num_materials = random.randint(1, 3)
            selected_materials = packing_df.sample(num_materials)

            for _, material in selected_materials.iterrows():
                quantity_needed = random.randint(1, 5)
                cost_per_recipe = quantity_needed * material['cost_per_unit']

                recipe_packing.append({
                    'recipe_id': recipe['recipe_id'],
                    'recipe_name': recipe['recipe_name'],
                    'material_id': material['material_id'],
                    'material_name': material['material_name'],
                    'quantity_needed': quantity_needed,
                    'cost_per_recipe': cost_per_recipe,
                    'notes': f'Packing for {recipe["recipe_name"]}'
                })

        return pd.DataFrame(recipe_packing)

    def generate_sales_orders_data(self, recipes_df, num_orders=200):
        """Generate sales orders data"""
        orders = []

        for i in range(num_orders):
            recipe = recipes_df.sample(1).iloc[0]
            quantity = random.randint(1, 10)

            # Calculate costs
            packing_cost = round(random.uniform(5, 25), 2)
            preparation_cost = round(random.uniform(20, 100), 2)
            gas_charges = round(random.uniform(5, 20), 2)
            electricity_charges = round(random.uniform(3, 15), 2)
            total_cost_making = packing_cost + preparation_cost + gas_charges + electricity_charges

            our_pricing = round(total_cost_making * random.uniform(1.3, 2.0), 2)  # 30-100% markup
            subtotal = our_pricing * quantity
            discount = round(subtotal * random.uniform(0, 0.2), 2)  # 0-20% discount
            final_price = subtotal - discount
            profit = final_price - (total_cost_making * quantity)
            profit_percentage = (profit / final_price * 100) if final_price > 0 else 0

            orders.append({
                'date': (datetime.now() - timedelta(days=random.randint(0, 90))).date(),
                'order_id': f'ORD_{i+1:04d}',
                'recipe': recipe['recipe_name'],
                'quantity': quantity,
                'packing_materials': 'Standard Packing',
                'packing_cost': packing_cost,
                'preparation_materials': 'Standard Ingredients',
                'preparation_cost': preparation_cost,
                'gas_charges': gas_charges,
                'electricity_charges': electricity_charges,
                'total_cost_making': total_cost_making,
                'our_pricing': our_pricing,
                'subtotal': subtotal,
                'discount': discount,
                'final_price_after_discount': final_price,
                'profit': profit,
                'profit_percentage': round(profit_percentage, 2)
            })

        return pd.DataFrame(orders)

    def save_data_to_files(self, data):
        """Save all data to CSV files"""
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        for name, df in data.items():
            filename = f'data/{name}.csv'
            df.to_csv(filename, index=False)
            print(f"Saved {len(df)} records to {filename}")

        print(f"Sample data generation completed! Generated {len(data)} datasets.")


def generate_sample_data():
    """Convenience function to generate sample data"""
    generator = SampleDataGenerator()
    return generator.generate_all_sample_data()


if __name__ == "__main__":
    # Generate sample data when run directly
    generate_sample_data()
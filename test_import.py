#!/usr/bin/env python3
"""
Test import of packing materials module
"""

import pandas as pd
import os

try:
    print("Testing packing materials import...")
    from modules.packing_materials import PackingMaterialsWidget
    print("SUCCESS: Import worked")

    print("Testing widget creation...")

    # Create test data structure
    data = {}

    # Load actual data
    if os.path.exists('data/packing_materials.csv'):
        data['packing_materials'] = pd.read_csv('data/packing_materials.csv')
        print(f"Loaded {len(data['packing_materials'])} packing materials")
    else:
        data['packing_materials'] = pd.DataFrame()
        print("No packing materials data found")

    if os.path.exists('data/recipe_packing_materials.csv'):
        data['recipe_packing_materials'] = pd.read_csv('data/recipe_packing_materials.csv')
        print(f"Loaded {len(data['recipe_packing_materials'])} recipe materials")
    else:
        data['recipe_packing_materials'] = pd.DataFrame()
        print("No recipe materials data found")

    if os.path.exists('data/recipes.csv'):
        data['recipes'] = pd.read_csv('data/recipes.csv')
        print(f"Loaded {len(data['recipes'])} recipes")
    else:
        data['recipes'] = pd.DataFrame()
        print("No recipes data found")

    print("SUCCESS: Data loaded, widget creation test complete")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

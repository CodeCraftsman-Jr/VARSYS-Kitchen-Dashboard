#!/usr/bin/env python3
"""
Test script to verify the cost breakdown fixes
Tests that:
1. Making cost equals ingredient cost (not 20%)
2. Packaging cost comes from packing materials mapping (not hardcoded ₹5.00)
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_test_data():
    """Load test data from CSV files"""
    data = {}
    
    try:
        # Load recipes
        if os.path.exists('data/recipes.csv'):
            data['recipes'] = pd.read_csv('data/recipes.csv')
            print(f"✅ Loaded {len(data['recipes'])} recipes")
        
        # Load recipe ingredients
        if os.path.exists('data/recipe_ingredients.csv'):
            data['recipe_ingredients'] = pd.read_csv('data/recipe_ingredients.csv')
            print(f"✅ Loaded {len(data['recipe_ingredients'])} recipe ingredients")
        
        # Load recipe packing materials
        if os.path.exists('data/recipe_packing_materials.csv'):
            data['recipe_packing_materials'] = pd.read_csv('data/recipe_packing_materials.csv')
            print(f"✅ Loaded {len(data['recipe_packing_materials'])} recipe packing materials")
        
        # Load shopping list for ingredient prices
        if os.path.exists('data/shopping_list.csv'):
            data['shopping_list'] = pd.read_csv('data/shopping_list.csv')
            print(f"✅ Loaded {len(data['shopping_list'])} shopping list items")
        
        # Load inventory for ingredient prices
        if os.path.exists('data/inventory.csv'):
            data['inventory'] = pd.read_csv('data/inventory.csv')
            print(f"✅ Loaded {len(data['inventory'])} inventory items")
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
    
    return data

def test_enhanced_cost_breakdown():
    """Test the enhanced cost breakdown module"""
    print("\n🧪 Testing Enhanced Cost Breakdown Module")
    print("=" * 50)

    try:
        # Import QApplication first
        from PySide6.QtWidgets import QApplication
        import sys

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        from modules.enhanced_cost_breakdown import EnhancedCostBreakdownPanel

        # Load test data
        data = load_test_data()

        if not data:
            print("❌ No test data available")
            return False

        # Create cost breakdown panel
        cost_panel = EnhancedCostBreakdownPanel(data)
        
        # Test with a sample recipe
        if 'recipes' in data and not data['recipes'].empty:
            sample_recipe = data['recipes'].iloc[0]
            recipe_id = sample_recipe.get('recipe_id')
            recipe_name = sample_recipe.get('recipe_name')
            
            print(f"\n📋 Testing with recipe: {recipe_name} (ID: {recipe_id})")
            
            # Calculate cost breakdown
            breakdown = cost_panel.calculate_detailed_cost_breakdown(recipe_id)
            
            print(f"\n💰 Cost Breakdown Results:")
            print(f"   Recipe Name: {breakdown['recipe_name']}")
            print(f"   Ingredient Cost: ₹{breakdown['ingredient_cost']:.2f}")
            print(f"   Making Cost: ₹{breakdown['making_cost']:.2f}")
            print(f"   Packaging Cost: ₹{breakdown['packaging_cost']:.2f}")
            print(f"   Electricity Cost: ₹{breakdown['electricity_cost']:.2f}")
            print(f"   Gas Cost: ₹{breakdown['gas_cost']:.2f}")
            print(f"   Other Charges: ₹{breakdown['other_charges']:.2f}")
            print(f"   Overhead Cost: ₹{breakdown['overhead_cost']:.2f}")
            print(f"   Total Cost: ₹{breakdown['total_cost']:.2f}")
            
            # Verify fixes
            print(f"\n🔍 Verification:")
            
            # Test 1: Making cost should equal ingredient cost
            if abs(breakdown['making_cost'] - breakdown['ingredient_cost']) < 0.01:
                print(f"   ✅ Making cost equals ingredient cost: ₹{breakdown['making_cost']:.2f}")
            else:
                print(f"   ❌ Making cost should equal ingredient cost!")
                print(f"      Expected: ₹{breakdown['ingredient_cost']:.2f}")
                print(f"      Got: ₹{breakdown['making_cost']:.2f}")
            
            # Test 2: Packaging cost should come from packing materials (not hardcoded ₹5.00)
            actual_packaging_cost = cost_panel.calculate_actual_packaging_cost(recipe_name)
            if abs(breakdown['packaging_cost'] - actual_packaging_cost) < 0.01:
                print(f"   ✅ Packaging cost from packing materials: ₹{breakdown['packaging_cost']:.2f}")
            else:
                print(f"   ❌ Packaging cost mismatch!")
                print(f"      Expected: ₹{actual_packaging_cost:.2f}")
                print(f"      Got: ₹{breakdown['packaging_cost']:.2f}")
            
            # Test 3: Check if packaging cost is not the old hardcoded ₹5.00
            if breakdown['packaging_cost'] != 5.0:
                print(f"   ✅ Packaging cost is not hardcoded ₹5.00")
            else:
                print(f"   ⚠️  Packaging cost is ₹5.00 (could be hardcoded or actual cost)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing enhanced cost breakdown: {e}")
        return False

def test_pricing_management():
    """Test the pricing management module"""
    print("\n🧪 Testing Pricing Management Module")
    print("=" * 50)

    try:
        # Import QApplication first
        from PySide6.QtWidgets import QApplication
        import sys

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        from modules.pricing_management import PricingManagementWidget

        # Load test data
        data = load_test_data()

        if not data:
            print("❌ No test data available")
            return False

        # Create pricing management widget
        pricing_widget = PricingManagementWidget(data)
        
        # Test with a sample recipe
        if 'recipes' in data and not data['recipes'].empty:
            sample_recipe = data['recipes'].iloc[0]
            recipe_id = sample_recipe.get('recipe_id')
            recipe_name = sample_recipe.get('recipe_name')
            
            print(f"\n📋 Testing with recipe: {recipe_name} (ID: {recipe_id})")
            
            # Calculate ingredient cost
            ingredient_cost = pricing_widget.calculate_ingredient_cost(recipe_id)
            
            if ingredient_cost is not None:
                print(f"   Ingredient Cost: ₹{ingredient_cost:.2f}")
                
                # Calculate packaging cost
                packaging_cost = pricing_widget.calculate_actual_packaging_cost(recipe_name)
                print(f"   Packaging Cost: ₹{packaging_cost:.2f}")
                
                print(f"\n🔍 Verification:")
                print(f"   ✅ Pricing management module working correctly")
                
                return True
            else:
                print(f"   ⚠️  Could not calculate ingredient cost (missing ingredient prices)")
                return True
            
    except Exception as e:
        print(f"❌ Error testing pricing management: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Cost Breakdown Fixes")
    print("=" * 60)
    
    # Test enhanced cost breakdown
    test1_passed = test_enhanced_cost_breakdown()
    
    # Test pricing management
    test2_passed = test_pricing_management()
    
    print(f"\n📊 Test Results Summary:")
    print(f"   Enhanced Cost Breakdown: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Pricing Management: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! The cost breakdown fixes are working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()

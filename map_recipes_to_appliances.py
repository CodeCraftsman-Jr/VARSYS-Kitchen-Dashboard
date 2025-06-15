#!/usr/bin/env python3
"""
Recipe to Appliance Mapping Tool
Tool to map recipes from database to electric appliances with CSV storage
"""

import json
import os
import pandas as pd
import csv

def load_config():
    """Load electricity configuration"""
    config_path = os.path.join('data', 'electricity_cost_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def save_config(config):
    """Save electricity configuration"""
    config_path = os.path.join('data', 'electricity_cost_config.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def load_recipes_from_database():
    """Load recipes from the recipes.csv database"""
    recipes_path = os.path.join('data', 'recipes.csv')
    try:
        if os.path.exists(recipes_path):
            df = pd.read_csv(recipes_path)
            if 'recipe_name' in df.columns:
                recipes = df['recipe_name'].dropna().unique().tolist()
                return sorted(recipes)
            else:
                print("Warning: 'recipe_name' column not found in recipes.csv")
                return []
        else:
            print("Warning: recipes.csv not found in data folder")
            return []
    except Exception as e:
        print(f"Error loading recipes from database: {e}")
        return []

def load_recipe_appliance_mappings_csv():
    """Load recipe-appliance mappings from CSV file"""
    csv_path = os.path.join('data', 'recipe_appliance_mappings.csv')
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            mappings = {}
            for _, row in df.iterrows():
                mappings[row['recipe_name']] = row['appliance_name']
            return mappings
        else:
            return {}
    except Exception as e:
        print(f"Error loading CSV mappings: {e}")
        return {}

def save_recipe_appliance_mappings_csv(mappings):
    """Save recipe-appliance mappings to CSV file (only electric appliances, not basic charges)"""
    csv_path = os.path.join('data', 'recipe_appliance_mappings.csv')
    try:
        # Filter out metadata entries and basic kitchen lighting
        clean_mappings = {k: v for k, v in mappings.items()
                         if not k.startswith('_') and v != 'Basic Kitchen Lighting'}

        # Create DataFrame
        data = []
        for recipe, appliance in clean_mappings.items():
            data.append({
                'recipe_name': recipe,
                'appliance_name': appliance,
                'created_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        if data:
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
            print(f"✅ {len(data)} electric appliance mappings saved to {csv_path}")
            print(f"   (Basic charge recipes not included in CSV)")
        else:
            # Create empty CSV with headers if no electric appliance mappings
            df = pd.DataFrame(columns=['recipe_name', 'appliance_name', 'created_date'])
            df.to_csv(csv_path, index=False)
            print(f"✅ Empty mappings file created at {csv_path}")
            print(f"   (No recipes mapped to electric appliances yet)")

        return True
    except Exception as e:
        print(f"Error saving CSV mappings: {e}")
        return False

def sync_csv_to_json_config(config):
    """Sync CSV mappings to JSON config"""
    csv_mappings = load_recipe_appliance_mappings_csv()

    # Update JSON config with CSV data
    if 'recipe_appliance_mapping' not in config:
        config['recipe_appliance_mapping'] = {}

    # Keep metadata entries
    metadata = {k: v for k, v in config['recipe_appliance_mapping'].items() if k.startswith('_')}

    # Replace with CSV data
    config['recipe_appliance_mapping'] = metadata
    config['recipe_appliance_mapping'].update(csv_mappings)

    return config

def show_current_mappings(config):
    """Show current recipe mappings (only electric appliances)"""
    print("\n=== Current Recipe Mappings (Electric Appliances Only) ===")

    recipe_mapping = config.get('recipe_appliance_mapping', {})
    appliances = config.get('appliances', {})
    basic_charge = config.get('electricity_settings', {}).get('minimum_cost_inr', 0.50)
    rate = config.get('electricity_settings', {}).get('electricity_rate_per_kwh_inr', 7.50)

    # Filter out metadata and basic kitchen lighting
    electric_mappings = {k: v for k, v in recipe_mapping.items()
                        if not k.startswith('_') and v != 'Basic Kitchen Lighting'}

    if not electric_mappings:
        print("No recipes are currently mapped to electric appliances.")
        print("All recipes use basic ₹0.50 charge (tubelight only).")
        print("\nNote: Only electric appliance mappings are shown here.")
        print("Basic charge recipes are not tracked in CSV.")
        return

    print("Recipe Name        | Appliance              | Cost (15 min)")
    print("-" * 60)

    for recipe, appliance in electric_mappings.items():
        appliance_data = appliances.get(appliance, {})
        power_kw = appliance_data.get('power_consumption_kw', 0.0)

        cost = max(power_kw * (15/60) * rate, basic_charge)
        print(f"{recipe:<18} | {appliance:<22} | ₹{cost:.2f}")

    print(f"\nTotal electric appliance mappings: {len(electric_mappings)}")
    print("Note: Recipes not listed here use basic ₹0.50 charge")

def show_available_appliances(config):
    """Show available appliances"""
    print("\n=== Available Appliances ===")

    appliances = config.get('appliances', {})
    rate = config.get('electricity_settings', {}).get('electricity_rate_per_kwh_inr', 7.50)

    print("ID | Appliance Name           | Power (kW) | Cost (15 min)")
    print("-" * 65)

    for i, (name, data) in enumerate(appliances.items(), 1):
        power = data.get('power_consumption_kw', 0.0)
        cost_15_min = power * (15/60) * rate if power > 0 else 0.50
        print(f"{i:2d} | {name:<24} | {power:8.1f}  | ₹{cost_15_min:.2f}")

def show_recipes_from_database():
    """Show recipes from database"""
    print("\n=== Recipes from Database ===")

    recipes = load_recipes_from_database()
    if not recipes:
        print("No recipes found in database.")
        return

    print(f"Total recipes found: {len(recipes)}")
    print("\nRecipe List:")
    print("-" * 40)

    for i, recipe in enumerate(recipes, 1):
        print(f"{i:3d}. {recipe}")

    if len(recipes) > 20:
        print(f"\n... and {len(recipes) - 20} more recipes")
        print("(Use option 4 to select from full list when mapping)")

def add_recipe_mapping(config):
    """Add a new recipe mapping"""
    print("\n=== Add Recipe Mapping ===")

    # Load recipes from database
    recipes = load_recipes_from_database()
    if not recipes:
        print("No recipes found in database. Please add recipes first.")
        return False

    # Show available recipes
    print(f"\nAvailable Recipes ({len(recipes)} total):")
    print("ID  | Recipe Name")
    print("-" * 40)

    for i, recipe in enumerate(recipes, 1):
        print(f"{i:2d}  | {recipe}")

    # Get recipe selection
    try:
        choice = int(input(f"\nSelect recipe (1-{len(recipes)}): "))
        if 1 <= choice <= len(recipes):
            recipe_name = recipes[choice - 1]
        else:
            print("Invalid selection.")
            return False
    except ValueError:
        print("Please enter a valid number.")
        return False
    
    # Show available appliances
    show_available_appliances(config)
    
    # Get appliance selection
    appliances = list(config.get('appliances', {}).keys())
    try:
        choice = int(input(f"\nSelect appliance (1-{len(appliances)}): "))
        if 1 <= choice <= len(appliances):
            selected_appliance = appliances[choice - 1]
        else:
            print("Invalid selection.")
            return False
    except ValueError:
        print("Please enter a valid number.")
        return False
    
    # Update mapping
    if 'recipe_appliance_mapping' not in config:
        config['recipe_appliance_mapping'] = {}

    # Handle basic kitchen lighting differently
    if selected_appliance == 'Basic Kitchen Lighting':
        # Remove from mapping (will use default basic charge)
        if recipe_name in config['recipe_appliance_mapping']:
            del config['recipe_appliance_mapping'][recipe_name]
        print(f"\n✅ '{recipe_name}' set to use basic charge (₹0.50)")
        print(f"   Will not appear in CSV (only electric appliances are tracked)")
    else:
        # Add to mapping for electric appliances
        config['recipe_appliance_mapping'][recipe_name] = selected_appliance

        # Show cost calculation
        appliance_data = config['appliances'][selected_appliance]
        power_kw = appliance_data.get('power_consumption_kw', 0.0)
        rate = config.get('electricity_settings', {}).get('electricity_rate_per_kwh_inr', 7.50)
        basic_charge = config.get('electricity_settings', {}).get('minimum_cost_inr', 0.50)

        cost = max(power_kw * (15/60) * rate, basic_charge)
        print(f"\n✅ '{recipe_name}' mapped to '{selected_appliance}'")
        print(f"   Power: {power_kw} kW")
        print(f"   Cost for 15 minutes: ₹{cost:.2f}")
        print(f"   Will be saved to CSV for tracking")

    return True

def remove_recipe_mapping(config):
    """Remove a recipe mapping"""
    print("\n=== Remove Recipe Mapping ===")
    
    recipe_mapping = config.get('recipe_appliance_mapping', {})
    if not recipe_mapping:
        print("No recipe mappings to remove.")
        return False
    
    print("Current mappings:")
    recipes = list(recipe_mapping.keys())
    for i, recipe in enumerate(recipes, 1):
        appliance = recipe_mapping[recipe]
        print(f"{i:2d}. {recipe} → {appliance}")
    
    try:
        choice = int(input(f"\nSelect recipe to remove mapping (1-{len(recipes)}): "))
        if 1 <= choice <= len(recipes):
            recipe_to_remove = recipes[choice - 1]
            del config['recipe_appliance_mapping'][recipe_to_remove]
            print(f"✅ Removed mapping for '{recipe_to_remove}' (will now use basic ₹0.50 charge)")
            return True
        else:
            print("Invalid selection.")
            return False
    except ValueError:
        print("Please enter a valid number.")
        return False

def main():
    """Main function"""
    print("🔌 Recipe to Appliance Mapping Tool")
    print("Database Integration + CSV Storage")
    print("=" * 50)

    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Please check if data/electricity_cost_config.json exists.")
        return

    # Sync CSV data to JSON config on startup
    config = sync_csv_to_json_config(config)
    
    while True:
        print("\nOptions:")
        print("1. Show current mappings")
        print("2. Show available appliances")
        print("3. Show recipes from database")
        print("4. Add recipe mapping (from database)")
        print("5. Remove recipe mapping")
        print("6. Save to CSV and JSON")
        print("7. Exit without saving")
        
        try:
            choice = input("\nSelect option (1-7): ").strip()

            if choice == '1':
                show_current_mappings(config)

            elif choice == '2':
                show_available_appliances(config)

            elif choice == '3':
                show_recipes_from_database()

            elif choice == '4':
                if add_recipe_mapping(config):
                    print("\nMapping added successfully!")

            elif choice == '5':
                if remove_recipe_mapping(config):
                    print("\nMapping removed successfully!")

            elif choice == '6':
                # Save to both CSV and JSON
                csv_mappings = {k: v for k, v in config.get('recipe_appliance_mapping', {}).items() if not k.startswith('_')}
                if save_recipe_appliance_mappings_csv(csv_mappings):
                    if save_config(config):
                        print("\n✅ Configuration saved to both CSV and JSON!")
                        print("📁 CSV file: data/recipe_appliance_mappings.csv")
                        print("📁 JSON file: data/electricity_cost_config.json")
                        print("Changes will take effect in the kitchen app.")
                        break
                    else:
                        print("\n❌ Failed to save JSON configuration.")
                else:
                    print("\n❌ Failed to save CSV mappings.")

            elif choice == '7':
                print("\nExiting without saving changes.")
                break

            else:
                print("Invalid option. Please select 1-7.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()

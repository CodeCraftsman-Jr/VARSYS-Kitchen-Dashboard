"""
Data Validation Utility
=======================

Validates and cleans data before saving to CSV files.
"""

import pandas as pd
import os
from datetime import datetime

class DataValidator:
    """Validates and cleans data for the Kitchen Dashboard"""
    
    @staticmethod
    def validate_packing_materials(df):
        """Validate packing materials data"""
        try:
            # Ensure required columns exist
            required_columns = [
                'material_id', 'material_name', 'category', 'unit', 
                'cost_per_unit', 'current_stock', 'minimum_stock', 
                'supplier', 'notes'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Clean and validate data types
            df['material_id'] = pd.to_numeric(df['material_id'], errors='coerce').fillna(0).astype(int)
            df['material_name'] = df['material_name'].astype(str).fillna('')
            df['category'] = df['category'].astype(str).fillna('General')
            df['unit'] = df['unit'].astype(str).fillna('piece')
            df['cost_per_unit'] = pd.to_numeric(df['cost_per_unit'], errors='coerce').fillna(0.0)
            df['current_stock'] = pd.to_numeric(df['current_stock'], errors='coerce').fillna(0.0)
            df['minimum_stock'] = pd.to_numeric(df['minimum_stock'], errors='coerce').fillna(0.0)
            df['supplier'] = df['supplier'].astype(str).fillna('')
            df['notes'] = df['notes'].astype(str).fillna('')
            
            # Ensure unique material IDs
            if df['material_id'].duplicated().any():
                df['material_id'] = range(1, len(df) + 1)
            
            return df
            
        except Exception as e:
            print(f"Error validating packing materials: {e}")
            return df
    
    @staticmethod
    def safe_save_csv(df, filepath, validator_func=None):
        """Safely save dataframe to CSV with validation"""
        try:
            # Apply validation if provided
            if validator_func:
                df = validator_func(df)
            
            # Create backup
            if os.path.exists(filepath):
                backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(filepath, backup_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save with proper encoding
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print(f"Error saving CSV {filepath}: {e}")
            return False
    
    @staticmethod
    def validate_and_save_packing_materials(df, filepath="data/packing_materials.csv"):
        """Validate and save packing materials data"""
        return DataValidator.safe_save_csv(
            df, filepath, DataValidator.validate_packing_materials
        )

# Convenience functions
def save_packing_materials(df):
    """Save packing materials with validation"""
    return DataValidator.validate_and_save_packing_materials(df)

def validate_data(df, data_type):
    """Validate data based on type"""
    if data_type == 'packing_materials':
        return DataValidator.validate_packing_materials(df)
    return df

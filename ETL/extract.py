"""
Extract Module: Read raw data from CSV files and validate schema
This module handles the E in ETL - extracting raw transactional data
"""

import pandas as pd
import os
from pathlib import Path

class DataExtractor:
    """Extract raw data from CSV files with validation"""
    
    def __init__(self, data_path: str):
        """
        Initialize the extractor with the path to raw data
        
        Args:
            data_path: Path to the raw data directory
        """
        self.data_path = data_path
        self.extracted_data = {}
        
    def extract_products(self) -> pd.DataFrame:
        """Extract products table from CSV"""
        file_path = os.path.join(self.data_path, 'products.csv')
        df = pd.read_csv(file_path)
        
        # Validate schema
        expected_columns = ['product_id', 'name', 'category', 'brand', 'unit_price', 'unit_cost']
        self._validate_schema(df, expected_columns, 'products')
        
        print(f"✓ Extracted {len(df)} products")
        self.extracted_data['products'] = df
        return df
    
    def extract_customers(self) -> pd.DataFrame:
        """Extract customers table from CSV"""
        file_path = os.path.join(self.data_path, 'customers.csv')
        df = pd.read_csv(file_path)
        
        # Validate schema
        expected_columns = ['customer_id', 'name', 'city', 'country', 'age']
        self._validate_schema(df, expected_columns, 'customers')
        
        print(f"✓ Extracted {len(df)} customers")
        self.extracted_data['customers'] = df
        return df
    
    def extract_sales(self) -> pd.DataFrame:
        """Extract sales table from CSV"""
        file_path = os.path.join(self.data_path, 'sales.csv')
        df = pd.read_csv(file_path)
        
        # Validate schema
        expected_columns = ['sale_id', 'sale_date', 'product_id', 'customer_id', 
                          'channel_id', 'quantity', 'unit_price_sale']
        self._validate_schema(df, expected_columns, 'sales')
        
        print(f"✓ Extracted {len(df)} sales records")
        self.extracted_data['sales'] = df
        return df
    
    def extract_channels(self) -> pd.DataFrame:
        """Extract channels table from CSV"""
        file_path = os.path.join(self.data_path, '..', 'channels.csv')
        df = pd.read_csv(file_path)
        
        # Validate schema
        expected_columns = ['channel_id', 'channel']
        self._validate_schema(df, expected_columns, 'channels')
        
        print(f"✓ Extracted {len(df)} channels")
        self.extracted_data['channels'] = df
        return df
    
    def extract_all(self) -> dict:
        """Extract all tables and return as dictionary"""
        print("\n=== EXTRACT PHASE ===")
        self.extract_products()
        self.extract_customers()
        self.extract_sales()
        self.extract_channels()
        
        print(f"\n✓ All data extracted successfully!")
        return self.extracted_data
    
    @staticmethod
    def _validate_schema(df: pd.DataFrame, expected_columns: list, table_name: str):
        """Validate that DataFrame has expected columns"""
        if not all(col in df.columns for col in expected_columns):
            raise ValueError(f"Schema validation failed for {table_name}. "
                           f"Expected columns: {expected_columns}, "
                           f"Got: {list(df.columns)}")
        
        if df.empty:
            raise ValueError(f"Table {table_name} is empty!")


def extract(data_path: str) -> dict:
    """
    Main extraction function
    
    Args:
        data_path: Path to raw data directory
        
    Returns:
        Dictionary with extracted DataFrames
    """
    extractor = DataExtractor(data_path)
    return extractor.extract_all()


if __name__ == "__main__":
    # Usage example
    raw_data_path = r"c:\Users\LENOVO\OneDrive\Documentos\ETL\3 Lab\ETL-lab-3\data\raw"
    
    if os.path.exists(raw_data_path):
        extracted = extract(raw_data_path)
        print("\nExtracted data shapes:")
        for table_name, df in extracted.items():
            print(f"  {table_name}: {df.shape}")
    else:
        print(f"Error: Data path not found: {raw_data_path}")

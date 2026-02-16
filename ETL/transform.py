"""
Transform Module: Clean and transform raw data for the data warehouse
This module handles the T in ETL - transforming and preparing data
"""

import pandas as pd
import numpy as np
from datetime import datetime

class DataTransformer:
    """Transform raw data into dimensional format"""
    
    def __init__(self, extracted_data: dict):
        """
        Initialize transformer with extracted data
        
        Args:
            extracted_data: Dictionary with raw DataFrames from extract phase
        """
        self.extracted_data = extracted_data
        self.transformed_data = {}
        self.surrogate_key_counter = {}
        
    def transform_all(self) -> dict:
        """Execute all transformations"""
        print("\n=== TRANSFORM PHASE ===")
        
        self.transform_date_dimension()
        self.transform_product_dimension()
        self.transform_customer_dimension()
        self.transform_channel_dimension()
        self.transform_sales_fact()
        
        print("\n[OK] All data transformed successfully!")
        return self.transformed_data
    
    def transform_date_dimension(self) -> pd.DataFrame:
        """Create date dimension table"""
        print("\nTransforming Date Dimension...")
        
        # Get date range from sales
        sales_df = self.extracted_data['sales'].copy()
        sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
        
        date_range = pd.date_range(
            start=sales_df['sale_date'].min(),
            end=sales_df['sale_date'].max(),
            freq='D'
        )
        
        # Create date dimension
        dim_date = pd.DataFrame({
            'date_id': range(1, len(date_range) + 1),
            'date': date_range,
            'day': date_range.day,
            'month': date_range.month,
            'quarter': date_range.quarter,
            'year': date_range.year,
            'day_of_week': date_range.day_name(),
            'month_name': date_range.strftime('%B')
        })
        
        print(f"  [OK] Created date dimension with {len(dim_date)} records")
        self.transformed_data['dim_date'] = dim_date
        return dim_date
    
    def transform_product_dimension(self) -> pd.DataFrame:
        """Create product dimension table"""
        print("Transforming Product Dimension...")
        
        products_df = self.extracted_data['products'].copy()
        
        # Clean and standardize data
        products_df['name'] = products_df['name'].str.strip()
        products_df['category'] = products_df['category'].str.strip().str.upper()
        products_df['brand'] = products_df['brand'].str.strip().str.upper()
        
        # Convert prices to numeric
        products_df['unit_price'] = pd.to_numeric(products_df['unit_price'], errors='coerce')
        products_df['unit_cost'] = pd.to_numeric(products_df['unit_cost'], errors='coerce')
        
        # Create surrogate key
        dim_product = products_df.copy()
        dim_product = dim_product.rename(columns={'product_id': 'product_key'})
        dim_product['product_key'] = range(1, len(dim_product) + 1)
        dim_product.insert(0, 'product_key', dim_product.pop('product_key'))
        
        # Calculate margin
        dim_product['margin_percent'] = (
            (dim_product['unit_price'] - dim_product['unit_cost']) / 
            dim_product['unit_price'] * 100
        ).round(2)
        
        print(f"  [OK] Created product dimension with {len(dim_product)} records")
        print(f"    Brands: {dim_product['brand'].nunique()}, Categories: {dim_product['category'].nunique()}")
        
        self.transformed_data['dim_product'] = dim_product
        return dim_product
    
    def transform_customer_dimension(self) -> pd.DataFrame:
        """Create customer dimension table"""
        print("Transforming Customer Dimension...")
        
        customers_df = self.extracted_data['customers'].copy()
        
        # Clean and standardize data
        customers_df['name'] = customers_df['name'].str.strip()
        customers_df['city'] = customers_df['city'].str.strip().str.upper()
        customers_df['country'] = customers_df['country'].str.strip().str.upper()
        customers_df['age'] = pd.to_numeric(customers_df['age'], errors='coerce').astype('Int64')
        
        # Create surrogate key
        dim_customer = customers_df.copy()
        dim_customer = dim_customer.rename(columns={'customer_id': 'customer_key'})
        dim_customer['customer_key'] = range(1, len(dim_customer) + 1)
        dim_customer.insert(0, 'customer_key', dim_customer.pop('customer_key'))
        
        # Store mapping for fact table
        self.customer_mapping = dict(zip(customers_df['customer_id'], dim_customer['customer_key']))
        self.product_mapping = None  # Will be set later
        
        print(f"  [OK] Created customer dimension with {len(dim_customer)} records")
        print(f"    Countries: {dim_customer['country'].nunique()}")
        
        self.transformed_data['dim_customer'] = dim_customer
        return dim_customer
    
    def transform_channel_dimension(self) -> pd.DataFrame:
        """Create channel dimension table"""
        print("Transforming Channel Dimension...")
        
        channels_df = self.extracted_data['channels'].copy()
        
        # Clean and standardize data
        channels_df['channel'] = channels_df['channel'].str.strip()
        
        # Create surrogate key
        dim_channel = channels_df.copy()
        dim_channel = dim_channel.rename(columns={'channel_id': 'channel_key'})
        dim_channel['channel_key'] = range(1, len(dim_channel) + 1)
        dim_channel.insert(0, 'channel_key', dim_channel.pop('channel_key'))
        
        # Store mapping for fact table
        self.channel_mapping = dict(zip(channels_df['channel_id'], dim_channel['channel_key']))
        
        print(f"  [OK] Created channel dimension with {len(dim_channel)} records")
        
        self.transformed_data['dim_channel'] = dim_channel
        return dim_channel
    
    def transform_sales_fact(self) -> pd.DataFrame:
        """Create sales fact table"""
        print("Transforming Sales Fact Table...")
        
        sales_df = self.extracted_data['sales'].copy()
        products_df = self.extracted_data['products'].copy()
        
        # Clean data
        sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
        sales_df['quantity'] = pd.to_numeric(sales_df['quantity'], errors='coerce').astype('Int64')
        sales_df['unit_price_sale'] = pd.to_numeric(sales_df['unit_price_sale'], errors='coerce')
        
        # Merge with products to get cost
        sales_with_cost = sales_df.merge(
            products_df[['product_id', 'unit_cost']], 
            on='product_id', 
            how='left'
        )
        
        # Calculate measures
        sales_with_cost['total_sales_amount'] = (
            sales_with_cost['quantity'] * sales_with_cost['unit_price_sale']
        ).round(2)
        
        sales_with_cost['total_cost'] = (
            sales_with_cost['quantity'] * sales_with_cost['unit_cost']
        ).round(2)
        
        sales_with_cost['profit'] = (
            sales_with_cost['total_sales_amount'] - sales_with_cost['total_cost']
        ).round(2)
        
        sales_with_cost['profit_margin'] = (
            (sales_with_cost['profit'] / sales_with_cost['total_sales_amount'] * 100)
        ).round(2)
        
        # Build fact table with mapped surrogate keys
        dim_date = self.transformed_data['dim_date']
        dim_product = self.transformed_data['dim_product']
        
        # Create mappings
        date_mapping = dict(zip(dim_date['date'], dim_date['date_id']))
        product_mapping = dict(zip(
            self.extracted_data['products']['product_id'], 
            range(1, len(self.transformed_data['dim_product']) + 1)
        ))
        
        # Map original product_id to surrogate key
        products_orig = self.extracted_data['products'].reset_index(drop=True)
        product_key_mapping = dict(zip(
            products_orig['product_id'],
            range(1, len(products_orig) + 1)
        ))
        
        fact_sales = pd.DataFrame({
            'sales_key': range(1, len(sales_with_cost) + 1),
            'sale_id': sales_with_cost['sale_id'],
            'date_id': sales_with_cost['sale_date'].map(date_mapping),
            'product_key': sales_with_cost['product_id'].map(product_key_mapping),
            'customer_key': sales_with_cost['customer_id'].map(self.customer_mapping),
            'channel_key': sales_with_cost['channel_id'].map(self.channel_mapping),
            'quantity': sales_with_cost['quantity'],
            'unit_price_sale': sales_with_cost['unit_price_sale'],
            'total_sales_amount': sales_with_cost['total_sales_amount'],
            'total_cost': sales_with_cost['total_cost'],
            'profit': sales_with_cost['profit'],
            'profit_margin': sales_with_cost['profit_margin']
        })
        
        # Remove rows with null keys
        initial_rows = len(fact_sales)
        fact_sales = fact_sales.dropna(subset=['date_id', 'product_key', 'customer_key', 'channel_key'])
        dropped_rows = initial_rows - len(fact_sales)
        
        print(f"  [OK] Created Sales Fact Table with {len(fact_sales)} records")
        if dropped_rows > 0:
            print(f"    (Dropped {dropped_rows} rows with missing references)")
        
        self.transformed_data['fact_sales'] = fact_sales
        return fact_sales


def transform(extracted_data: dict) -> dict:
    """
    Main transformation function
    
    Args:
        extracted_data: Dictionary with raw DataFrames from extract phase
        
    Returns:
        Dictionary with transformed DataFrames
    """
    transformer = DataTransformer(extracted_data)
    return transformer.transform_all()


if __name__ == "__main__":
    # This will be tested in the notebook or after extract
    print("Transform module loaded. Use with extract.py and load.py")

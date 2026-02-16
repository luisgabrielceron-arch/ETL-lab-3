"""
Load Module: Load transformed data into a Data Warehouse (SQLite database)
This module handles the L in ETL - loading data into the dimensional model
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

class DataWarehouseLoader:
    """Load transformed data into Data Warehouse"""
    
    def __init__(self, db_path: str):
        """
        Initialize the loader with database path
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        print(f"[OK] Connected to database: {self.db_path}")
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            self.connection.close()
            print("[OK] Disconnected from database")
    
    def create_schema(self):
        """Create the data warehouse schema"""
        print("\n=== LOAD PHASE - Creating Schema ===")
        
        try:
            # Drop existing tables (for fresh load)
            tables = ['fact_sales', 'dim_date', 'dim_product', 'dim_customer', 'dim_channel']
            for table in tables:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            # Create Date Dimension
            self.cursor.execute("""
                CREATE TABLE dim_date (
                    date_id INTEGER PRIMARY KEY,
                    date DATE NOT NULL UNIQUE,
                    day INTEGER,
                    month INTEGER,
                    quarter INTEGER,
                    year INTEGER,
                    day_of_week TEXT,
                    month_name TEXT
                )
            """)
            
            # Create Product Dimension
            self.cursor.execute("""
                CREATE TABLE dim_product (
                    product_key INTEGER PRIMARY KEY,
                    product_id INTEGER,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    unit_price REAL,
                    unit_cost REAL,
                    margin_percent REAL
                )
            """)
            
            # Create Customer Dimension
            self.cursor.execute("""
                CREATE TABLE dim_customer (
                    customer_key INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    name TEXT NOT NULL,
                    city TEXT,
                    country TEXT,
                    age INTEGER
                )
            """)
            
            # Create Channel Dimension
            self.cursor.execute("""
                CREATE TABLE dim_channel (
                    channel_key INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    channel TEXT NOT NULL
                )
            """)
            
            # Create Sales Fact Table
            self.cursor.execute("""
                CREATE TABLE fact_sales (
                    sales_key INTEGER PRIMARY KEY,
                    sale_id INTEGER,
                    date_id INTEGER NOT NULL,
                    product_key INTEGER NOT NULL,
                    customer_key INTEGER NOT NULL,
                    channel_key INTEGER NOT NULL,
                    quantity INTEGER,
                    unit_price_sale REAL,
                    total_sales_amount REAL,
                    total_cost REAL,
                    profit REAL,
                    profit_margin REAL,
                    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
                    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
                    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
                    FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key)
                )
            """)
            
            self.connection.commit()
            print("[OK] Schema created successfully")
            
        except sqlite3.Error as e:
            print(f"[ERROR] Error creating schema: {e}")
            raise
    
    def load_dimensions(self, transformed_data: dict):
        """Load dimension tables in correct order"""
        print("\nLoading Dimension Tables...")
        
        try:
            # Load Date Dimension
            dim_date = transformed_data['dim_date']
            dim_date.to_sql('dim_date', self.connection, if_exists='append', index=False)
            print(f"  [OK] Loaded {len(dim_date)} date records")
            
            # Load Product Dimension
            dim_product = transformed_data['dim_product']
            dim_product.to_sql('dim_product', self.connection, if_exists='append', index=False)
            print(f"  [OK] Loaded {len(dim_product)} product records")
            
            # Load Customer Dimension
            dim_customer = transformed_data['dim_customer']
            dim_customer.to_sql('dim_customer', self.connection, if_exists='append', index=False)
            print(f"  [OK] Loaded {len(dim_customer)} customer records")
            
            # Load Channel Dimension
            dim_channel = transformed_data['dim_channel']
            dim_channel.to_sql('dim_channel', self.connection, if_exists='append', index=False)
            print(f"  [OK] Loaded {len(dim_channel)} channel records")
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"[ERROR] Error loading dimensions: {e}")
            raise
    
    def load_fact_table(self, transformed_data: dict):
        """Load fact table after all dimensions are loaded"""
        print("\nLoading Fact Table...")
        
        try:
            fact_sales = transformed_data['fact_sales']
            fact_sales.to_sql('fact_sales', self.connection, if_exists='append', index=False)
            print(f"  [OK] Loaded {len(fact_sales)} sales records")
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"[ERROR] Error loading fact table: {e}")
            raise
    
    def verify_data_warehouse(self):
        """Verify the data warehouse was loaded correctly"""
        print("\n=== Data Warehouse Verification ===")
        
        try:
            tables = {
                'dim_date': 'Date Dimension',
                'dim_product': 'Product Dimension',
                'dim_customer': 'Customer Dimension',
                'dim_channel': 'Channel Dimension',
                'fact_sales': 'Sales Fact Table'
            }
            
            for table, description in tables.items():
                result = self.cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                count = result[0] if result else 0
                print(f"  [OK] {description}: {count} records")
            
            # Check referential integrity
            print("\nReferential Integrity Checks:")
            
            # Check for orphaned product keys
            orphan_products = self.cursor.execute("""
                SELECT COUNT(*) FROM fact_sales f 
                WHERE f.product_key NOT IN (SELECT product_key FROM dim_product)
            """).fetchone()[0]
            print(f"  [OK] Orphaned product keys: {orphan_products}")
            
            # Check for orphaned customer keys
            orphan_customers = self.cursor.execute("""
                SELECT COUNT(*) FROM fact_sales f 
                WHERE f.customer_key NOT IN (SELECT customer_key FROM dim_customer)
            """).fetchone()[0]
            print(f"  [OK] Orphaned customer keys: {orphan_customers}")
            
            # Check for orphaned channel keys
            orphan_channels = self.cursor.execute("""
                SELECT COUNT(*) FROM fact_sales f 
                WHERE f.channel_key NOT IN (SELECT channel_key FROM dim_channel)
            """).fetchone()[0]
            print(f"  [OK] Orphaned channel keys: {orphan_channels}")
            
            print("\n[OK] Data Warehouse is ready for analysis!")
            
        except sqlite3.Error as e:
            print(f"[ERROR] Error verifying data warehouse: {e}")
    
    def load_all(self, transformed_data: dict):
        """Execute complete load process"""
        try:
            self.connect()
            self.create_schema()
            self.load_dimensions(transformed_data)
            self.load_fact_table(transformed_data)
            self.verify_data_warehouse()
            self.disconnect()
        except Exception as e:
            print(f"[ERROR] Load process failed: {e}")
            if self.connection:
                self.disconnect()
            raise


def load(transformed_data: dict, db_path: str):
    """
    Main load function
    
    Args:
        transformed_data: Dictionary with transformed DataFrames
        db_path: Path to the SQLite database file
    """
    loader = DataWarehouseLoader(db_path)
    loader.load_all(transformed_data)


if __name__ == "__main__":
    print("Load module loaded. Use with extract.py and transform.py")

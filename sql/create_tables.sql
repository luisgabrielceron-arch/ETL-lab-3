-- =============================================================================
-- DATA WAREHOUSE SCHEMA CREATION
-- Technology Retail Analytics Data Warehouse
-- Database: SQLite
-- Created: February 2026
-- =============================================================================

-- Drop existing tables (if needed for refresh)
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_channel;

-- =============================================================================
-- DIMENSION TABLE: dim_date
-- Purpose: Temporal dimension for date-based analysis
-- Grain: One row per day
-- =============================================================================
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    month_name TEXT NOT NULL
);

-- Create index on date for faster lookups
CREATE INDEX idx_dim_date_date ON dim_date(date);

-- =============================================================================
-- DIMENSION TABLE: dim_product
-- Purpose: Product master data with profitability metrics
-- Grain: One row per product
-- =============================================================================
CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT NOT NULL,
    unit_price REAL NOT NULL,
    unit_cost REAL NOT NULL,
    margin_percent REAL
);

-- Create indexes for common queries
CREATE INDEX idx_dim_product_product_id ON dim_product(product_id);
CREATE INDEX idx_dim_product_category ON dim_product(category);
CREATE INDEX idx_dim_product_brand ON dim_product(brand);

-- =============================================================================
-- DIMENSION TABLE: dim_customer
-- Purpose: Customer master data with demographics
-- Grain: One row per customer
-- =============================================================================
CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    age INTEGER
);

-- Create indexes for common queries
CREATE INDEX idx_dim_customer_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_dim_customer_country ON dim_customer(country);
CREATE INDEX idx_dim_customer_city ON dim_customer(city);

-- =============================================================================
-- DIMENSION TABLE: dim_channel
-- Purpose: Sales channel information
-- Grain: One row per channel
-- Types: Physical Store (Cali), Physical Store (Bogota), Online Store
-- =============================================================================
CREATE TABLE dim_channel (
    channel_key INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL UNIQUE,
    channel TEXT NOT NULL
);

-- Create index for lookups
CREATE INDEX idx_dim_channel_channel_id ON dim_channel(channel_id);

-- =============================================================================
-- FACT TABLE: fact_sales
-- Purpose: Core fact table containing all sales transactions
-- Grain: ONE ROW PER TRANSACTION
--        One product sold to one customer through one channel on one date
-- Measures: Quantity, revenue, cost, profit
-- =============================================================================
CREATE TABLE fact_sales (
    sales_key INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL UNIQUE,
    
    -- Foreign keys to dimensions
    date_id INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    channel_key INTEGER NOT NULL,
    
    -- Measures (additive - can be summed)
    quantity INTEGER NOT NULL,
    unit_price_sale REAL NOT NULL,
    total_sales_amount REAL NOT NULL,
    total_cost REAL NOT NULL,
    profit REAL NOT NULL,
    profit_margin REAL,
    
    -- Foreign key constraints for referential integrity
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key)
);

-- Create indexes for foreign keys and common queries
CREATE INDEX idx_fact_sales_date_id ON fact_sales(date_id);
CREATE INDEX idx_fact_sales_product_key ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_customer_key ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_channel_key ON fact_sales(channel_key);

-- Composite index for common query patterns
CREATE INDEX idx_fact_sales_date_channel ON fact_sales(date_id, channel_key);
CREATE INDEX idx_fact_sales_product_category ON fact_sales(product_key, date_id);

-- =============================================================================
-- SCHEMA VERIFICATION QUERIES
-- Run these to verify the schema is correctly created
-- =============================================================================

-- Check all tables exist
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Check fact table structure
-- PRAGMA table_info(fact_sales);

-- Check for orphaned keys (data quality verification)
-- SELECT COUNT(*) FROM fact_sales f WHERE f.date_id NOT IN (SELECT date_id FROM dim_date);
-- SELECT COUNT(*) FROM fact_sales f WHERE f.product_key NOT IN (SELECT product_key FROM dim_product);
-- SELECT COUNT(*) FROM fact_sales f WHERE f.customer_key NOT IN (SELECT customer_key FROM dim_customer);
-- SELECT COUNT(*) FROM fact_sales f WHERE f.channel_key NOT IN (SELECT channel_key FROM dim_channel);

-- =============================================================================
-- SCHEMA STATISTICS
-- =============================================================================
-- Dimension Tables:
--   dim_date:     ~120 rows (4 months of daily data)
--   dim_product:  ~40 rows (technology products)
--   dim_customer: ~25 rows (customers from 3 countries)
--   dim_channel:  ~3 rows (2 physical stores + 1 online)
--
-- Fact Table:
--   fact_sales:   ~240 rows (sales transactions)
--
-- Total Cardinality: ~450-500 rows
-- Database Size: ~1-2 MB (SQLite)
-- =============================================================================

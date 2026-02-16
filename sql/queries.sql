-- =============================================================================
-- KPI QUERIES FOR DATA WAREHOUSE ANALYSIS
-- Technology Retail Analytics
-- All queries to be executed against the Data Warehouse (OLAP)
-- =============================================================================

-- =============================================================================
-- KPI 1: SALES VOLUME AND REVENUE BY PRODUCT CATEGORY
-- Business Question: What is the sales volume and revenue per product category?
-- =============================================================================
SELECT 
    p.category,
    COUNT(f.sales_key) as num_transactions,
    SUM(f.quantity) as total_quantity,
    ROUND(SUM(f.total_sales_amount), 2) as total_revenue,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND(AVG(f.profit_margin), 2) as avg_profit_margin,
    ROUND(100 * SUM(f.profit) / SUM(f.total_sales_amount), 2) as revenue_profit_margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;

-- =============================================================================
-- KPI 2: REVENUE BY SALES CHANNEL (PHYSICAL vs ONLINE)
-- Business Question: Which sales channels (physical store vs online) generate 
--                    the highest revenue?
-- =============================================================================
SELECT 
    c.channel,
    COUNT(f.sales_key) as num_transactions,
    SUM(f.quantity) as total_quantity,
    ROUND(SUM(f.total_sales_amount), 2) as total_revenue,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND(100 * SUM(f.total_sales_amount) / 
        (SELECT SUM(total_sales_amount) FROM fact_sales), 2) as revenue_percentage,
    ROUND(AVG(f.total_sales_amount), 2) as avg_transaction_value
FROM fact_sales f
JOIN dim_channel c ON f.channel_key = c.channel_key
GROUP BY c.channel
ORDER BY total_revenue DESC;

-- =============================================================================
-- KPI 3: MONTHLY SALES TRENDS
-- Business Question: How do sales evolve over time (monthly trends)?
-- Shows month-over-month performance and growth indicators
-- =============================================================================
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(f.sales_key) as num_transactions,
    SUM(f.quantity) as total_units,
    ROUND(SUM(f.total_sales_amount), 2) as monthly_revenue,
    ROUND(SUM(f.profit), 2) as monthly_profit,
    ROUND(AVG(f.total_sales_amount), 2) as avg_transaction_value,
    ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as profit_margin_percent
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- =============================================================================
-- KPI 4: BRAND PROFITABILITY RANKING
-- Business Question: Which brands are the most profitable?
-- Includes profit, volume, and margin analysis
-- =============================================================================
SELECT 
    p.brand,
    COUNT(f.sales_key) as num_transactions,
    SUM(f.quantity) as total_units_sold,
    ROUND(SUM(f.total_sales_amount), 2) as brand_revenue,
    ROUND(SUM(f.profit), 2) as brand_profit,
    ROUND(AVG(f.profit_margin), 2) as avg_profit_margin_percent,
    ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as revenue_profit_margin,
    ROUND(AVG(p.margin_percent), 2) as product_margin_percent
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.brand
ORDER BY brand_profit DESC;

-- =============================================================================
-- KPI 5: CUSTOMER GEOGRAPHIC DISTRIBUTION
-- Business Question: Market penetration by geography
-- Shows revenue, volume, and customer count by country
-- =============================================================================
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_key) as unique_customers,
    COUNT(f.sales_key) as total_transactions,
    SUM(f.quantity) as total_units,
    ROUND(SUM(f.total_sales_amount), 2) as country_revenue,
    ROUND(SUM(f.profit), 2) as country_profit,
    ROUND(AVG(f.total_sales_amount), 2) as avg_transaction_value,
    ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as profit_margin_percent
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
ORDER BY country_revenue DESC;

-- =============================================================================
-- KPI 6: PRODUCT CATEGORY PROFITABILITY INDEX
-- Business Question: Which categories are most profitable per unit?
-- Combines revenue volume with profitability metrics
-- =============================================================================
SELECT 
    p.category,
    COUNT(DISTINCT p.product_key) as num_products,
    SUM(f.quantity) as total_units,
    ROUND(SUM(f.total_sales_amount), 2) as total_revenue,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as profit_margin_percent,
    ROUND(SUM(f.profit) / SUM(f.quantity), 2) as profit_per_unit,
    ROUND(AVG(p.margin_percent), 2) as avg_product_margin_percent
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY profit_margin_percent DESC;

-- =============================================================================
-- BONUS ANALYSIS QUERIES
-- =============================================================================

-- Top 10 Most Profitable Products
SELECT 
    p.product_id,
    p.name,
    p.brand,
    p.category,
    COUNT(f.sales_key) as times_sold,
    ROUND(SUM(f.total_sales_amount), 2) as product_revenue,
    ROUND(SUM(f.profit), 2) as product_profit,
    ROUND(AVG(f.profit_margin), 2) as profit_margin_percent
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.name, p.brand, p.category
HAVING times_sold > 0
ORDER BY product_profit DESC
LIMIT 10;

-- Channel Performance by Product Category
SELECT 
    c.channel,
    p.category,
    COUNT(f.sales_key) as transactions,
    ROUND(SUM(f.total_sales_amount), 2) as revenue,
    ROUND(SUM(f.profit), 2) as profit,
    ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as profit_margin
FROM fact_sales f
JOIN dim_channel c ON f.channel_key = c.channel_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY c.channel, p.category
ORDER BY c.channel, revenue DESC;

-- Customer Lifetime Value Analysis
SELECT 
    c.customer_id,
    c.name,
    c.country,
    c.age,
    COUNT(f.sales_key) as purchase_frequency,
    ROUND(SUM(f.total_sales_amount), 2) as total_spent,
    ROUND(SUM(f.profit), 2) as total_profit_generated,
    ROUND(AVG(f.total_sales_amount), 2) as avg_transaction_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.name, c.country, c.age
ORDER BY total_spent DESC;

-- Overall Data Warehouse Summary
SELECT 
    COUNT(DISTINCT f.sales_key) as total_transactions,
    COUNT(DISTINCT f.customer_key) as unique_customers,
    COUNT(DISTINCT f.product_key) as products_sold,
    COUNT(DISTINCT f.date_id) as days_active,
    COUNT(DISTINCT f.channel_key) as channels,
    SUM(f.quantity) as total_units,
    ROUND(SUM(f.total_sales_amount), 2) as total_revenue,
    ROUND(SUM(f.total_cost), 2) as total_cost,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND(100 * SUM(f.profit) / SUM(f.total_sales_amount), 2) as overall_profit_margin
FROM fact_sales f;

-- =============================================================================
-- QUERY PERFORMANCE NOTES
-- =============================================================================
-- * All queries use foreign key joins (surrogate keys are integers - fast)
-- * Indexes on fact_sales FK columns enable fast dimension lookups
-- * GROUP BY on dimension keys is efficient
-- * ROUND() function applied to financial metrics for precision
-- * All queries return in < 1 second on SQLite (even with 240 rows)
-- * Production systems would benefit from materialized views for complex queries
-- =============================================================================

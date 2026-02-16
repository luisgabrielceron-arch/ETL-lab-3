# KPI DEFINITIONS & FORMULAS
## Technology Retail Analytics - Data Warehouse KPIs

---

## Table of Contents
1. [KPI 1: Sales Volume & Revenue by Category](#kpi-1)
2. [KPI 2: Revenue by Sales Channel](#kpi-2)
3. [KPI 3: Monthly Sales Trends](#kpi-3)
4. [KPI 4: Brand Profitability Ranking](#kpi-4)
5. [KPI 5: Customer Geographic Distribution](#kpi-5)
6. [KPI 6: Product Category Profitability Index](#kpi-6)

---

## KPI 1: Sales Volume & Revenue by Product Category {#kpi-1}

### Business Question
**What is the sales volume and revenue per product category?**

### Purpose
Understand which product categories drive the most sales volume and revenue. Essential for inventory planning, marketing budget allocation, and product mix optimization.

### Formula
```
Total Quantity = SUM(quantity) BY category
Total Revenue = SUM(total_sales_amount) BY category
Total Profit = SUM(profit) BY category
Avg Profit Margin = AVG(profit_margin) BY category
```

### Calculation
```sql
SELECT 
    p.category,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_sales_amount) as total_revenue,
    SUM(f.profit) as total_profit,
    (SUM(f.profit) / SUM(f.total_sales_amount)) * 100 as profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
```

### Required Tables
- **Fact Table:** `fact_sales` (quantity, total_sales_amount, profit)
- **Dimension:** `dim_product` (category)

### Visualization Type
**Horizontal Stacked Bar Chart** or **Bullet Chart**
- X-axis: Revenue ($)
- Y-axis: Product Category
- Color-coded by profit margin

### Business Value
- ✅ Identifies top-performing categories
- ✅ Guides product portfolio decisions
- ✅ Reveals profitability gaps
- ✅ Supports pricing strategy

### Sample Output
| Category | Units | Revenue | Profit | Margin % |
|----------|-------|---------|--------|----------|
| Smartphones | 45 | $28,500 | $8,550 | 30% |
| Networking | 62 | $24,100 | $5,700 | 24% |
| Audio | 38 | $18,200 | $5,460 | 30% |
| Accessories | 96 | $15,600 | $4,680 | 30% |

---

## KPI 2: Revenue by Sales Channel {#kpi-2}

### Business Question
**Which sales channels (physical store vs online) generate the highest revenue?**

### Purpose
Optimize channel strategy (physical vs digital), allocate resources, and understand customer preferences by channel. Critical for omnichannel retail decisions.

### Formula
```
Channel Revenue = SUM(total_sales_amount) BY channel
Channel Market Share = (Channel Revenue / Total Revenue) * 100
Channel Profit = SUM(profit) BY channel
Avg Transaction Value = AVG(total_sales_amount) BY channel
```

### Calculation
```sql
SELECT 
    c.channel,
    SUM(f.total_sales_amount) as channel_revenue,
    SUM(f.profit) as channel_profit,
    COUNT(f.sales_key) as num_transactions,
    (SUM(f.total_sales_amount) / 
        (SELECT SUM(total_sales_amount) FROM fact_sales)) * 100 as revenue_pct
FROM fact_sales f
JOIN dim_channel c ON f.channel_key = c.channel_key
GROUP BY c.channel
```

### Required Tables
- **Fact Table:** `fact_sales` (total_sales_amount, profit)
- **Dimension:** `dim_channel` (channel name)

### Visualization Type
**Pie Chart** (revenue distribution) + **Bar Chart** (profit by channel)

### Business Value
- ✅ Shows channel performance split
- ✅ Identifies growth opportunities (e.g., online expansion)
- ✅ Validates digital transformation investments
- ✅ Informs resource allocation

### Sample Output
| Channel | Revenue | % of Total | Profit | Transactions |
|---------|---------|-----------|--------|--------------|
| Physical Store - Cali | $37,200 | 42% | $11,160 | 85 |
| Physical Store - Bogotá | $26,100 | 30% | $7,830 | 68 |
| Online Store | $23,100 | 28% | $6,930 | 88 |

### Strategic Implications
- **Online** has highest transaction count but lower avg ticket
- **Physical stores** have higher margins (service, upsell)
- Opportunity to increase online channel efficiency

---

## KPI 3: Monthly Sales Trends {#kpi-3}

### Business Question
**How do sales evolve over time (monthly trends)?**

### Purpose
Identify seasonal patterns, growth trends, and forecast future demand. Essential for planning inventory, promotions, and cash flow.

### Formula
```
Monthly Revenue = SUM(total_sales_amount) BY month
Monthly Profit = SUM(profit) BY month
Month-over-Month Growth = ((Current Revenue - Previous Revenue) / Previous Revenue) * 100
Profit Margin Trend = (Monthly Profit / Monthly Revenue) * 100
```

### Calculation
```sql
SELECT 
    d.year,
    d.month,
    d.month_name,
    SUM(f.total_sales_amount) as monthly_revenue,
    SUM(f.profit) as monthly_profit,
    COUNT(f.sales_key) as num_transactions,
    (SUM(f.profit) / SUM(f.total_sales_amount)) * 100 as margin_pct
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month
```

### Required Tables
- **Fact Table:** `fact_sales` (total_sales_amount, profit)
- **Dimension:** `dim_date` (month, year, month_name)

### Visualization Type
**Line Chart with Trend Line + Area Fill**
- X-axis: Month (Jan - Apr 2026)
- Y-axis: Revenue ($)
- Secondary axis: Profit Margin (%)
- Trend line showing growth direction

### Business Value
- ✅ Reveals seasonal patterns
- ✅ Identifies peak and low periods
- ✅ Enables demand forecasting
- ✅ Guides promotional planning

### Sample Output
| Month | Revenue | Profit | Margin % | Growth % |
|-------|---------|--------|----------|----------|
| Jan 2026 | $27,000 | $8,100 | 30.0% | — |
| Feb 2026 | $28,500 | $8,550 | 30.0% | +5.6% |
| Mar 2026 | $32,400 | $9,720 | 30.0% | +13.6% |
| Apr 2026 | $30,500 | $9,150 | 30.0% | -5.9% |

### Insights
- Consistent profit margins across months (30%)
- Peak sales in March (end-of-quarter push?)
- Slight decline in April (typical after fiscal quarter)

---

## KPI 4: Brand Profitability Ranking {#kpi-4}

### Business Question
**Which brands are the most profitable?**

### Purpose
Evaluate brand performance, guide vendor partnerships, and optimize brand portfolio. Support trade and slotting decisions with retailers.

### Formula
```
Brand Revenue = SUM(total_sales_amount) BY brand
Brand Profit = SUM(profit) BY brand
Brand Units = SUM(quantity) BY brand
Profit per Unit = Brand Profit / Brand Units
Brand Margin % = (Brand Profit / Brand Revenue) * 100
```

### Calculation
```sql
SELECT 
    p.brand,
    SUM(f.quantity) as total_units,
    SUM(f.total_sales_amount) as brand_revenue,
    SUM(f.profit) as brand_profit,
    (SUM(f.profit) / SUM(f.total_sales_amount)) * 100 as profit_margin_pct,
    ROUND(SUM(f.profit) / SUM(f.quantity), 2) as profit_per_unit
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.brand
ORDER BY brand_profit DESC
```

### Required Tables
- **Fact Table:** `fact_sales` (quantity, total_sales_amount, profit)
- **Dimension:** `dim_product` (brand)

### Visualization Type
**Horizontal Bar Chart (Top 10 Brands)**
- Primary: Revenue (stacked)
- Secondary: Profit Margin % (data labels)

### Business Value
- ✅ Identifies profitable vs unprofitable brands
- ✅ Supports vendor negotiation (rebates, terms)
- ✅ Guides assortment decisions
- ✅ Enables margin optimization

### Sample Output
| Brand | Revenue | Profit | Units | Margin % | Profit/Unit |
|-------|---------|--------|-------|----------|-------------|
| Samsung | $18,500 | $5,550 | 28 | 30% | $198.21 |
| Apple | $16,200 | $4,860 | 22 | 30% | $220.91 |
| HP | $14,800 | $4,440 | 35 | 30% | $126.86 |
| Lenovo | $12,300 | $3,690 | 31 | 30% | $119.03 |
| Sony | $10,100 | $3,030 | 18 | 30% | $168.33 |

### Strategic Insights
- **Premium brands** (Apple) = Higher profit per unit
- **Volume brands** (HP) = Consistent margins but lower per-unit profit
- **Underperformers** = Candidates for discontinuation

---

## KPI 5: Customer Geographic Distribution {#kpi-5}

### Business Question
**Market penetration by geography - which geographic markets are most valuable?**

### Purpose
Understand market strength by country, prioritize geographic expansion, and allocate marketing budgets. Support localization strategies.

### Formula
```
Country Revenue = SUM(total_sales_amount) BY country
Country Customers = COUNT(DISTINCT customer_id) BY country
Transactions per Customer = COUNT(sales) / COUNT(customers) BY country
Revenue per Customer = Country Revenue / Country Customers
Profit by Country = SUM(profit) BY country
```

### Calculation
```sql
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_key) as unique_customers,
    COUNT(f.sales_key) as total_transactions,
    SUM(f.total_sales_amount) as country_revenue,
    SUM(f.profit) as country_profit,
    ROUND(SUM(f.total_sales_amount) / COUNT(DISTINCT c.customer_key), 2) as revenue_per_customer
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
```

### Required Tables
- **Fact Table:** `fact_sales` (total_sales_amount, profit)
- **Dimension:** `dim_customer` (country)

### Visualization Type
**Map Chart** (if geography available) or **Grouped Bar Chart**
- Countries on X-axis
- Revenue + Customer Count (dual axes)

### Business Value
- ✅ Identifies high-value markets
- ✅ Shows market penetration (customers vs revenue)
- ✅ Guides localization investment
- ✅ Supports go-to-market strategy

### Sample Output
| Country | Customers | Transactions | Revenue | Revenue/Customer |
|---------|-----------|--------------|---------|------------------|
| Mexico | 9 | 62 | $38,200 | $4,244 |
| Colombia | 10 | 58 | $32,100 | $3,210 |
| Chile | 6 | 23 | $15,900 | $2,650 |

### Market Insights
- **Mexico**: Highest penetration (9 customers = 36% of base)
- **Colombia**: Second highest (10 customers = 40% of base)  
- **Chile**: Emerging market (6 customers = 24% of base)
- Opportunity: Expand Chile market (lowest revenue per customer)

---

## KPI 6: Product Category Profitability Index {#kpi-6}

### Business Question
**Which product categories are most profitable relative to revenue? (Profitability Index)**

### Purpose
Identify margin-rich vs margin-thin categories for pricing strategy, product development focus, and assortment planning.

### Formula
```
Category Revenue = SUM(total_sales_amount) BY category
Category Profit = SUM(profit) BY category
Profitability Index = (Category Profit / Category Revenue) * 100
Profit per Unit = Category Profit / SUM(quantity) BY category
```

### Calculation
```sql
SELECT 
    p.category,
    SUM(f.quantity) as total_units,
    SUM(f.total_sales_amount) as total_revenue,
    SUM(f.profit) as total_profit,
    (SUM(f.profit) / SUM(f.total_sales_amount)) * 100 as profit_margin_pct,
    ROUND(SUM(f.profit) / SUM(f.quantity), 2) as profit_per_unit
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY profit_margin_pct DESC
```

### Required Tables
- **Fact Table:** `fact_sales` (quantity, total_sales_amount, profit)
- **Dimension:** `dim_product` (category)

### Visualization Type
**Combo Chart**
- Column: Revenue (primary Y-axis)
- Line: Profit Margin % (secondary Y-axis)

### Business Value
- ✅ Compares profitability across categories
- ✅ Guides promotional strategy (protect high-margin items)
- ✅ Identifies opportunities for productivity
- ✅ Supports pricing decisions

### Sample Output
| Category | Units | Revenue | Profit | Margin % | Profit/Unit |
|----------|-------|---------|--------|----------|-------------|
| Audio | 38 | $18,200 | $5,460 | 30% | $143.68 |
| Smartphones | 45 | $28,500 | $8,550 | 30% | $190.00 |
| Accessories | 96 | $15,600 | $4,680 | 30% | $48.75 |
| Networking | 62 | $24,100 | $7,230 | 30% | $116.61 |

---

## Summary Table: All KPIs

| KPI # | Name | Key Metric | Business Impact |
|-------|------|-----------|-----------------|
| 1 | Category Analysis | Revenue by category | Product portfolio strategy |
| 2 | Channel Performance | Revenue by channel | Omnichannel strategy |
| 3 | Trend Analysis | Monthly revenue growth | Demand forecasting |
| 4 | Brand Value | Profitability by brand | Vendor management |
| 5 | Geographic Mix | Revenue by country | Market expansion |
| 6 | Margin Management | Profit margin by category | Pricing strategy |

---

## Implementation Notes

### Data Quality Requirements
- ✅ All FK relationships must be valid (no orphaned records)
- ✅ Prices must be positive (unit_price, unit_cost)
- ✅ Quantity must be >= 1
- ✅ Profit margins must be between 0-100%

### Performance Characteristics
- All queries execute in < 1 second on SQLite
- Fact table has proper indexes on all FK columns
- Dimension tables are small enough for efficient joins
- No complex aggregations requiring materialized views

### Refresh Frequency
- Recommended: Daily (end-of-business)
- Or: Real-time if integrated with POS system

---

**Last Updated:** February 2026

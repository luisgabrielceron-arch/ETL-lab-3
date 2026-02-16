# DIMENSIONAL MODEL DESIGN DOCUMENTATION
## Technology Retail Analytics Data Warehouse

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Star Schema Design](#star-schema)
3. [Dimensional Model](#dimensional-model)
4. [Fact Table Design](#fact-table)
5. [Dimension Tables](#dimensions)
6. [Design Decisions](#design-decisions)
7. [Data Lineage](#data-lineage)

---

## Executive Summary {#executive-summary}

### What is Dimensional Modeling?

Dimensional modeling is a database design technique specifically optimized for **analytical queries** (OLAP). It organizes data into:
- **Fact Tables**: Store measurable events (transactions, sales)
- **Dimension Tables**: Provide context (who, what, when, where, why)

### Why Not Use Transactional Database?

| Aspect | OLTP (Source) | OLAP (Data Warehouse) |
|--------|---------------|----------------------|
| Purpose | Fast writes | Fast reads/analysis |
| Structure | 3NF (normalized) | Denormalized star |
| Query Type | Simple, indexed | Complex, aggregations |
| Performance | ~100ms | ~1 second |
| Data Volume | Operational | Historical |

---

## Star Schema Design {#star-schema}

### Visual Representation

```
                        ╔═══════════════╗
                        ║   DIM_DATE    ║
                        ║─────────────── ║
                        ║  date_id (PK) ║
                        ║  date          ║
                        ║  month         ║
                        ║  quarter       ║
                        ║  year          ║
                        ╚═══════════════╝
                               ▲
                               │
                      ╔════════╩════════╗
                      │                 │
        ╔═════════════════════╗  ╔═════════════════════╗
        ║  DIM_PRODUCT        ║  ║  FACT_SALES         ║  ─────────────► ╔═════════════════════╗
        ║─────────────────────║  ║─────────────────────║                 ║  DIM_CUSTOMER       ║
        ║ product_key (PK)    ║◄─║ product_key (FK)    ║                 ║─────────────────────║
        ║ product_id          ║  ║ date_id (FK)        ║                 ║ customer_key (PK)   ║
        ║ name                ║  ║ customer_key (FK)   ║                 ║ customer_id         ║
        ║ category            ║  ║ channel_key (FK)    ║                 ║ name                ║
        ║ brand               ║  ║ quantity (MEASURE)  ║                 ║ country             ║
        ║ unit_price          ║  ║ revenue (MEASURE)   ║                 ║ city                ║
        ║ unit_cost           ║  ║ cost (MEASURE)      ║                 ║ age                 ║
        ║ margin_percent      ║  ║ profit (MEASURE)    ║                 ╚═════════════════════╝
        ╚═════════════════════╝  ╚─────────────────────║
                                          │
                                         │
                                ╔════════╩══════════╗
                                │                    │
                        ╔══════════════════╗
                        ║  DIM_CHANNEL     ║
                        ║──────────────────║
                        ║ channel_key (PK)║
                        ║ channel_id       ║
                        ║ channel          ║
                        ╚══════════════════╝
```

### Why Star Schema?

✅ **Fast Joins**: Integer FK lookups are very fast  
✅ **Simple Queries**: Easy to write GROUP BY statements  
✅ **Aggregation**: Measures naturally sum across dimensions  
✅ **Maintainability**: Clear structure, easy to understand  
✅ **Flexibility**: Add new dimensions without changing fact table  

---

## Dimensional Model {#dimensional-model}

### Fact Table Overview

**Name:** `fact_sales`

**Grain (Atomic Level):**  
*One row in the fact table represents **one product sold to one customer through one channel on one specific date***

**Cardinality:** ~240 rows (for 4-month period)

**Measures (Additive Numeric Values):**
- `quantity`: Units sold (integer)
- `unit_price_sale`: Sale price per unit (decimal)
- `total_sales_amount`: Quantity × UnitPrice (decimal)
- `total_cost`: Quantity × UnitCost (decimal)
- `profit`: Revenue - Cost (decimal)
- `profit_margin`: Profit % (decimal 0-100)

### Why This Grain?

The chosen grain (transaction-level) allows us to:
- Analyze sales at granular level
- Drill down from company-wide to specific transactions
- Group flexibly by any dimension combination
- Support any analytical question

---

## Fact Table {#fact-table}

### Physical Design

```sql
CREATE TABLE fact_sales (
    sales_key INTEGER PRIMARY KEY,       -- Surrogate key
    sale_id INTEGER NOT NULL UNIQUE,     -- Business key
    
    -- Dimension foreign keys
    date_id INTEGER NOT NULL FK,         -- References dim_date
    product_key INTEGER NOT NULL FK,     -- References dim_product
    customer_key INTEGER NOT NULL FK,    -- References dim_customer
    channel_key INTEGER NOT NULL FK,     -- References dim_channel
    
    -- Measures (facts)
    quantity INTEGER NOT NULL,
    unit_price_sale REAL NOT NULL,
    total_sales_amount REAL NOT NULL,
    total_cost REAL NOT NULL,
    profit REAL NOT NULL,
    profit_margin REAL
);
```

### Indexing Strategy

| Index Name | Columns | Purpose |
|------------|---------|---------|
| PK | sales_key | Quick row lookup |
| FK_date | date_id | Join with dim_date |
| FK_product | product_key | Join with dim_product |
| FK_customer | customer_key | Join with dim_customer |
| FK_channel | channel_key | Join with dim_channel |
| Composite | date_id, channel_key | Category-channel analysis |

### Loading Order

1. **Load Dimensions First** (no FK dependencies)
   - dim_date
   - dim_product
   - dim_customer
   - dim_channel

2. **Load Fact Table Last** (all FKs already exist)
   - fact_sales

---

## Dimension Tables {#dimensions}

### DIM_DATE (Time Dimension)

**Purpose:** Enables all temporal analysis

```
date_id   | date       | day | month | quarter | year | day_of_week | month_name
---------|------------|-----|-------|---------|------|-------------|----------
1        | 2026-01-01 | 1   | 1     | 1       | 2026 | Thursday    | January
2        | 2026-01-02 | 2   | 1     | 1       | 2026 | Friday      | January
...
120      | 2026-04-30 | 30  | 4     | 2       | 2026 | Thursday    | April
```

**Key Design Decisions:**
- ✅ Surrogate key (`date_id`) for fast joins
- ✅ Business date column for reference
- ✅ Pre-calculated temporal attributes (no runtime calculations)
- ✅ Support for any time-based analysis

**Cardinality:** ~120 rows (4 months × 30 days avg)

---

### DIM_PRODUCT (Product Master Dimension)

**Purpose:** Product context and profitability tracking

```
product_key | product_id | name                    | category      | brand
------------|------------|------------------------|---------------|----------
1           | 1001       | Lenovo Fast Charger    | ACCESSORIES   | LENOVO
2           | 1002       | Apple Laptop Backpack  | ACCESSORIES   | APPLE
3           | 1003       | Sony Wi-Fi Router      | NETWORKING    | SONY
...
40          | 1040       | HP Soundbar            | AUDIO         | HP
```

**Key Design Decisions:**
- ✅ Surrogate key (`product_key`) for DW management
- ✅ Keep original `product_id` for auditability
- ✅ Standardized category/brand (UPPERCASE)
- ✅ Calculated `margin_percent` = (price - cost) / price

**Cardinality:** ~40 rows

**Attributes:**
- product_id (business key from source)
- name (product description)
- category (standardized classification)
- brand (manufacturer)
- unit_price (list price in USD)
- unit_cost (acquisition cost)
- margin_percent (profitability metric)

---

### DIM_CUSTOMER (Customer Master Dimension)

**Purpose:** Customer context and geographic analysis

```
customer_key | customer_id | name              | city        | country  | age
------------|-------------|-------------------|-------------|----------|-----
1           | 5001        | Laura Rodríguez   | CALI        | COLOMBIA | 64
2           | 5002        | Carlos García     | CDMX        | MEXICO   | 47
...
25          | 5025        | Ana Pérez         | SANTIAGO    | CHILE    | 35
```

**Key Design Decisions:**
- ✅ Surrogate key for consistency
- ✅ Preserve original `customer_id` for reference
- ✅ Standardized city/country to UPPERCASE
- ✅ Include age for demographic analysis

**Cardinality:** ~25 rows (from 3 countries)

**Attributes:**
- customer_id (source identifier)
- name (customer name)
- city (geographic detail)
- country (market segment)
- age (demographic profiling)

---

### DIM_CHANNEL (Sales Channel Dimension)

**Purpose:** Channel performance analysis

```
channel_key | channel_id | channel
------------|------------|-------------------------
1           | 1          | Physical Store - Cali
2           | 2          | Physical Store - Bogotá
3           | 3          | Online Store
```

**Key Design Decisions:**
- ✅ Small dimension (only 3 channels)
- ✅ Descriptive naming for clarity
- ✅ Differentiates physical locations

**Cardinality:** 3 rows

**Attributes:**
- channel_id (source identifier)
- channel (descriptive name)

---

## Design Decisions {#design-decisions}

### 1. Surrogate Keys vs Business Keys

**Decision:** Use SURROGATE keys (integers) as primary keys

**Rationale:**
| Aspect | Surrogate | Business |
|--------|-----------|----------|
| Size | 4 bytes | Variable |
| Stability | Never changes | Can change (SCD) |
| Join speed | Fast (int) | Slower |
| Meaning | None (artificial) | Domain knowledge |

**Implementation:**
- `date_id` is surrogate (auto-increment)
- `product_id` is business key (kept as reference)
- Fact table joins on surrogate, preserves business key for audit

### 2. Grain Selection (Atomic Transaction Level)

**Decision:** One row = One product sold in one transaction

**Why Not Higher Grain?**
- Cannot drill down further
- Loss of detail for customer analysis
- Prevents exception reporting

**Why Not Lower Grain?**
- Would require exploding dimensions (not applicable here)
- Increases storage unnecessarily

### 3. Slowly Changing Dimensions (Not Implemented)

**Current Approach:** Type 0 (No change tracking)
- Overwrites dimension attributes
- Suitable for stable dimensions (products, channels)

**Could Add (Type 2)** for Customer dimension:
```
customer_key | customer_id | name | city | effective_date | end_date
```
This tracks when customer moved cities (SCD Type 2)

### 4. Conformed Dimensions

All dimensions are **conformed** - they share common attributes:
- `*_key`: Surrogate primary key
- `*_id`: Business key from source
- Standardized naming conventions

### 5. Degenerate Dimensions

**None included.** Could add later:
- `sale_id` in fact table (already present for audit)
- `order_number` for line-level grouping

---

## Data Lineage {#data-lineage}

### From Source (OLTP) to Warehouse (OLAP)

```
SOURCE SYSTEMS (Raw Data)
│
├─ products.csv
│  └─ product_id, name, category, brand, unit_price, unit_cost
│     │
│     └─ [EXTRACT] → pandas DataFrame
│        │
│        └─ [TRANSFORM] → Standardize categories/brands, calculate margins
│           │
│           └─ [LOAD] → dim_product table
│
├─ customers.csv
│  └─ customer_id, name, city, country, age
│     │
│     └─ [EXTRACT] → pandas DataFrame
│        │
│        └─ [TRANSFORM] → Standardize city/country to UPPERCASE
│           │
│           └─ [LOAD] → dim_customer table
│
├─ sales.csv
│  └─ sale_id, sale_date, product_id, customer_id, channel_id, quantity, unit_price_sale
│     │
│     └─ [EXTRACT] → pandas DataFrame
│        │
│        └─ [TRANSFORM] → Map to surrogate keys, calculate measures
│           │
│           └─ [LOAD] → fact_sales table (after dimensions loaded)
│
└─ channels.csv
   └─ channel_id, channel
      │
      └─ [EXTRACT] → pandas DataFrame
         │
         └─ [TRANSFORM] → Minimal cleanup
            │
            └─ [LOAD] → dim_channel table
```

### Referential Integrity

All foreign keys are enforced at database level:
```sql
-- Fact table → dim_date
FOREIGN KEY (date_id) REFERENCES dim_date(date_id)

-- Fact table → dim_product
FOREIGN KEY (product_key) REFERENCES dim_product(product_key)

-- Fact table → dim_customer
FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)

-- Fact table → dim_channel
FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key)
```

---

## Summary

### Model Characteristics

| Aspect | Value |
|--------|-------|
| Schema Type | Star Schema |
| Fact Tables | 1 (fact_sales) |
| Dimension Tables | 4 (date, product, customer, channel) |
| Fact Table Grain | Transaction level |
| Total Rows | ~370 (240 facts + 130 dimensions) |
| Surrogate Keys | Yes (all dimensions) |
| SCDs Tracked | None (Type 0) |
| Conformed? | Yes |
| Referential Integrity | Enforced |

### Design Quality

✅ **Appropriate for analytical queries**  
✅ **Supports all required KPIs**  
✅ **Extensible for future metrics**  
✅ **Maintains data integrity**  
✅ **Performance optimized for joins**  

---

**Last Updated:** February 2026  
**Status:** Complete and Validated

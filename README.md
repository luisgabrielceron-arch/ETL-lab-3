# ETL Data Warehouse Project - Technology Retail Analytics

## 📊 Project Overview

This project implements a complete **ETL (Extract, Transform, Load) pipeline** to build a **dimensional Data Warehouse** for a retail technology company. The system enables strategic decision-making through KPI calculations and visual analytics.

### Business Context
A technology retail company (selling gadgets and IT products) requested a Business Intelligence system to analyze sales performance across:
- **Product Categories** (Smartphones, Networking, Audio, Accessories)
- **Sales Channels** (2 Physical Stores + 1 Online Channel)
- **Geographic Markets** (Colombia, Mexico, Chile)
- **Time Periods** (4 consecutive months: Jan-Apr 2026)

---

## 🎯 Learning Objectives

Upon completing this project, students understand:
- ✅ Dimensional modeling and star schema design
- ✅ Complete ETL pipeline implementation
- ✅ Data quality and referential integrity
- ✅ KPI calculation from fact/dimension tables
- ✅ Business intelligence visualization
- ✅ Difference between OLTP (transactional) and OLAP (analytical) systems

---

## 📁 Project Structure

```
ETL-lab-3/
│
├── data/
│   ├── raw/                          # Source transactional data (OLTP)
│   │   ├── products.csv              # 40+ products
│   │   ├── customers.csv             # 25 customers from 3 countries
│   │   ├── sales.csv                 # 241 sales transactions
│   │   └── channels.csv              # 3 sales channels
│   │
│   └── warehouse/
│       └── datawarehouse.db          # SQLite Data Warehouse (OLAP)
│
├── ETL/
│   ├── extract.py                    # E phase: Read & validate raw data
│   ├── transform.py                  # T phase: Create dimensional model
│   ├── load.py                       # L phase: Load into warehouse
│   └── proto.ipynb                   # Educational tutorial notebook
│
├── sql/
│   ├── create_tables.sql             # Data Warehouse DDL
│   └── queries.sql                   # KPI SQL queries
│
├── visualization/
│   └── kpi_dashboard.py              # Dashboard generation script
│
├── docs/
│   ├── DIMENSIONAL_MODEL.md          # Star schema documentation
│   ├── KPI_DEFINITIONS.md            # 6 KPI definitions & formulas
│   └── BUSINESS_INSIGHTS.md          # Analysis & strategies
│
└── README.md                          # This file
```

---

## 🔄 ETL Pipeline Stages

### **EXTRACT Phase** (`extract.py`)
- Reads CSV files from `/data/raw/`
- Validates schema and data types
- Checks for empty tables and missing columns
- Returns extracted data as Pandas DataFrames

**Input:** Raw CSV files (OLTP structure)  
**Output:** Dictionary of DataFrames

### **TRANSFORM Phase** (`transform.py`)
- Creates **4 Dimension Tables:**
  - `dim_date`: Date attributes (day, month, quarter, year)
  - `dim_product`: Product details with calculated margins
  - `dim_customer`: Customer demographics
  - `dim_channel`: Sales channel information

- Creates **1 Fact Table:**
  - `fact_sales`: Transactions with measures (revenue, cost, profit, margin)

- Implements **Surrogate Keys** (sequential integer IDs)
- Cleans and standardizes all data
- Calculates business metrics

**Input:** Extracted DataFrames  
**Output:** Dimensional model ready for loading

### **LOAD Phase** (`load.py`)
- Creates SQLite database schema
- Loads dimensions FIRST (no dependencies)
- Loads fact table LAST (with foreign key constraints)
- Verifies referential integrity
- Checks for orphaned keys

**Input:** Transformed dimensional data  
**Output:** SQLite Data Warehouse (OLAP)

---

## 📊 Star Schema Design

```
                        DIM_DATE
                          │
           DIM_PRODUCT ─ FACT_SALES ─ DIM_CUSTOMER
                          │
                      DIM_CHANNEL
```

### Schema Details

| Table | Type | Key Concept |
|-------|------|------------|
| `dim_date` | Dimension | Temporal analysis (trends, seasonality) |
| `dim_product` | Dimension | Product profitability & mix analysis |
| `dim_customer` | Dimension | Customer segmentation & geography |
| `dim_channel` | Dimension | Channel performance comparison |
| `fact_sales` | Fact | Transactional measures (quantity, revenue, profit) |

**Grain of Fact Table:**  
*One row = One product sold to one customer through one channel on one specific date*

---

## 🎯 Key Performance Indicators (KPIs)

### Required KPIs (from Management)

1. **KPI1: Sales Volume & Revenue by Product Category**
   - Formula: `SUM(quantity)`, `SUM(revenue)` grouped by category
   - Tables: `fact_sales` + `dim_product`
   - Visualization: Horizontal bar chart

2. **KPI2: Revenue by Sales Channel**
   - Formula: `SUM(revenue)` by channel + percentage distribution
   - Tables: `fact_sales` + `dim_channel`
   - Visualization: Pie chart

3. **KPI3: Monthly Sales Trends**
   - Formula: `SUM(revenue)` by month with trend analysis
   - Tables: `fact_sales` + `dim_date`
   - Visualization: Line chart with trend

4. **KPI4: Brand Profitability Ranking**
   - Formula: `SUM(profit)` by brand + profit margin %
   - Tables: `fact_sales` + `dim_product`
   - Visualization: Horizontal bar chart (Top 10)

### Additional KPIs (Strategic Value)

5. **KPI5: Customer Geographic Distribution**
   - Formula: Revenue, transactions, and ATV by country
   - Tables: `fact_sales` + `dim_customer`
   - Visualization: Bar/map chart

6. **KPI6: Product Category Profitability Index**
   - Formula: `(SUM(profit) / SUM(revenue)) * 100` by category
   - Tables: `fact_sales` + `dim_product`
   - Visualization: Combo chart (revenue + margin%)

---

## 🚀 How to Run

### 1. **Execute ETL Pipeline** (from notebook)
```python
from extract import extract
from transform import transform
from load import load

# Extract
extracted = extract(raw_data_path)

# Transform
transformed = transform(extracted)

# Load
load(transformed, db_path)
```

### 2. **Query Data Warehouse**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/warehouse/datawarehouse.db')
query = "SELECT * FROM fact_sales LIMIT 5"
df = pd.read_sql_query(query, conn)
```

### 3. **Generate Dashboard**
```bash
python visualization/kpi_dashboard.py
```

---

## 💾 Dataset Characteristics

| Property | Value |
|----------|-------|
| Sales Records | 241 transactions |
| Customers | 25 from 3 countries |
| Products | 40+ SKUs |
| Product Categories | 4+ (Smartphones, Networking, Audio, Accessories) |
| Brands | 10+ (Samsung, Apple, HP, Lenovo, Sony, etc.) |
| Sales Channels | 3 (Physical Store Cali, Physical Store Bogotá, Online) |
| Time Period | 4 months (Jan-Apr 2026) |
| Countries | 3 (Colombia, Mexico, Chile) |

---

## 📈 Business Insights Generated

The Data Warehouse enables:
- ✅ Quick trend analysis without slow transactional queries
- ✅ Product mix optimization across channels
- ✅ Geographic market performance comparison
- ✅ Brand rationalization decisions
- ✅ Channel strategy optimization
- ✅ Time-based sales forecasting

---

## 🛠️ Technologies Used

| Component | Technology |
|-----------|-----------|
| **Extract** | Python, Pandas |
| **Transform** | Python, NumPy, Pandas |
| **Load** | SQLite, SQL |
| **Warehouse** | SQLite (local OLAP database) |
| **Visualization** | Matplotlib, Seaborn |
| **Documentation** | Jupyter Notebook |

---

## 📚 Educational Value

This project demonstrates:
1. **Data Engineering**: ETL pipeline design & implementation
2. **Database Design**: Dimensional modeling (star schema)
3. **SQL Mastery**: Complex queries, joins, aggregations
4. **Business Analytics**: KPI definition, interpretation
5. **Python**: OOP, data processing, error handling
6. **Data Quality**: Validation, referential integrity

---

## 📋 Deliverables Checklist

- [x] Extract module with schema validation
- [x] Transform module with dimensional model
- [x] Load module with data warehouse
- [x] Educational Jupyter notebook (10 parts, 34 cells)
- [x] 5 working SQL queries
- [x] 4x2 KPI visualization dashboard
- [x] Star schema design documentation
- [x] Business insights & recommendations
- [x] Complete README documentation

---

## 👨‍💼 Project Roles

- **Product Owner**: Define customer requirements & KPIs
- **Data Engineer**: Design & build ETL pipeline
- **BI Analyst**: Create dashboards & interpret insights

---

## 📞 Questions?

Refer to:
- `docs/DIMENSIONAL_MODEL.md` - Schema details
- `docs/KPI_DEFINITIONS.md` - KPI formulas
- `docs/BUSINESS_INSIGHTS.md` - Strategic analysis
- `ETL/proto.ipynb` - Step-by-step tutorial

---

**Created:** February 2026  
**Lab:** ETL Lab 3 - Data Warehouse Implementation  
**Business Scenario:** Technology Retail Store Analytics

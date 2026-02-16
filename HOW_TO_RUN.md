# How to Run the ETL Pipeline

This document explains how to execute the complete ETL pipeline and generate the Data Warehouse.

## Project Structure Summary

```
data/
├── raw/                              # SOURCE DATA (OLTP - Read Only)
│   ├── products.csv
│   ├── customers.csv
│   ├── sales.csv
│   └── channels.csv
│
└── warehouse/                        # DATA WAREHOUSE (OLAP - Created by ETL)
    └── datawarehouse.db             # SQLite database (created after running ETL)

ETL/
├── extract.py                       # Phase 1: Read & validate raw data
├── transform.py                     # Phase 2: Create dimensional model
├── load.py                          # Phase 3: Load into warehouse
└── proto.ipynb                      # Interactive tutorial notebook

sql/
├── create_tables.sql               # DDL for data warehouse schema
└── queries.sql                     # KPI queries

visualization/
└── kpi_dashboard.py                # Generate KPI visualizations

run_etl.py                          # Main ETL execution script
```

## Key Directories

| Directory | Purpose | Content |
|-----------|---------|---------|
| `data/raw/` | **SOURCE LAYER** - Original transactional data (OLTP) | 4 CSV files with 240 sales + customers + products + channels |
| `data/warehouse/` | **WAREHOUSE LAYER** - Dimensional model (OLAP) | SQLite database with star schema (1 fact + 4 dimensions) |

---

## How to Execute the ETL Pipeline

### Option 1: Run Complete ETL Script (Recommended)

```bash
python run_etl.py
```

This will:
1. Extract raw data from `data/raw/`
2. Transform into dimensional model
3. Create `data/warehouse/datawarehouse.db`
4. Load data with referential integrity checks
5. Display summary of tables created

**Output:**
```
[1/3] EXTRACT PHASE: Reading raw transactional data...
[2/3] TRANSFORM PHASE: Creating dimensional model...
[3/3] LOAD PHASE: Loading into Data Warehouse...

ETL PIPELINE COMPLETED SUCCESSFULLY

Data Warehouse Location: .../data/warehouse/datawarehouse.db
```

### Option 2: Interactive Notebook Tutorial

```bash
jupyter notebook ETL/proto.ipynb
```

This notebook walks through:
- Concepts of OLTP vs OLAP
- Each ETL phase with code + output
- SQL queries for KPIs
- Visualizations and analysis

---

## After ETL Execution

### 1. Query the Data Warehouse

```bash
sqlite3 data/warehouse/datawarehouse.db
```

Run queries from `sql/queries.sql`:
- KPI 1: Revenue by Category
- KPI 2: Revenue by Channel
- KPI 3: Monthly Trends
- KPI 4: Brand Profitability
- KPI 5: Geographic Distribution
- KPI 6: Category Profitability Index

### 2. Generate KPI Visualizations

```bash
python visualization/kpi_dashboard.py
```

Creates:
- 4 individual KPI charts
- 1 comprehensive dashboard
- PNG files in `visualization/output/`

### 3. Data Verification

The data warehouse contains:

**Dimensions (Lookup Tables):**
- `dim_date` - 120 rows (dates from Jan-Apr 2026)
- `dim_product` - 40 rows (products with costs and margins)
- `dim_customer` - 24 rows (customers from 3 countries)
- `dim_channel` - 3 rows (physical stores + online)

**Facts (Transaction Table):**
- `fact_sales` - 240 rows (one per product-customer-channel-date combination)
  - Measures: quantity, revenue, cost, profit, margin%
  - Foreign keys to all dimensions

---

## Database Architecture

### Star Schema Design

```
                        DIM_DATE
                           ▲
                           │
                           │
    DIM_PRODUCT ◄─┐    ┌───┴────┬─ FACT_SALES
                  └────┤         │
                  ┌────┤         ├─► DIM_CUSTOMER
    DIM_CHANNEL ◄─┘    └─────────┘
```

### Data Lineage

```
CSV FILES (OLTP)
   ↓
[EXTRACT] → DataFrames (Staging)
   ↓
[TRANSFORM] → Dimensional Model (Keys, Calculations)
   ↓
[LOAD] → SQLite Data Warehouse (OLAP)
   ↓
[QUERY] → KPIs & Analytics
```

---

## Important Notes

### Data Warehouse Location
- **Why separate?** The `data/raw/` folder contains the original transactional source (OLTP). The `data/warehouse/` folder contains the cleaned, structured dimensional model (OLAP).
- **Why SQLite?** Lightweight, file-based, no server required - perfect for learning and small deployments.
- **Can I reset?** Yes, simply delete `data/warehouse/datawarehouse.db` and run `python run_etl.py` again.

### Raw Data Protection
- The CSV files in `data/raw/` are **read-only** in the ETL process
- They are never modified or deleted
- You can safely rebuild the warehouse without affecting source data

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'extract'` | Run from project root directory |
| `FileNotFoundError: data/raw/*.csv` | Verify you're in the correct directory |
| `Database is locked` | Close other connections to `data/warehouse/datawarehouse.db` |
| `Permission denied` | Ensure write access to `data/warehouse/` folder |

---

## Summary

1. **Raw Data**: `data/raw/` - Original CSV files (OLTP)
2. **Execute ETL**: Run `python run_etl.py`
3. **Data Warehouse**: `data/warehouse/datawarehouse.db` - Dimensional model (OLAP)
4. **Query**: Use `sql/queries.sql` for KPI analysis
5. **Visualize**: Run `visualization/kpi_dashboard.py`

**The warehouse layer is now ready for Business Intelligence!** 📊

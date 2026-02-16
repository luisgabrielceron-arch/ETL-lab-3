# QUICKSTART - ETL Data Warehouse Project

## 🚀 Execute Complete Pipeline (30 seconds)

```bash
python run.py
```

**That's it!** The script will:
1. ✅ Verify all source files exist
2. ✅ Extract data from CSV
3. ✅ Transform to dimensional model
4. ✅ Load into SQLite warehouse
5. ✅ Generate visualizations
6. ✅ Display summary

---

## 📋 Command Options

| Command | Effect |
|---------|--------|
| `python run.py` | Full pipeline (E→T→L→VIZ) |
| `python run.py --skip-viz` | Skip visualization generation |
| `python run.py --skip-gen` | Skip data generation |
| `python run.py --rebuild` | Delete warehouse and rebuild |
| `python run.py --quiet` | Silent mode (less output) |
| `python run.py --help` | Show help menu |

---

## 📁 Project Structure (Final)

```
etl_lab_3/
│
├── data/
│   ├── raw/                    # SOURCE DATA (CSV files)
│   │   ├── products.csv        # 40 products
│   │   ├── customers.csv       # 24 customers
│   │   ├── sales.csv           # 240 transactions
│   │   └── channels.csv        # 3 channels
│   │
│   └── warehouse/              # OUTPUT DATA (SQLite)
│       └── datawarehouse.db    # Created by run.py
│
├── ETL/
│   ├── extract.py              # Phase 1: Extract
│   ├── transform.py            # Phase 2: Transform  
│   ├── load.py                 # Phase 3: Load
│   └── proto.ipynb             # Educational notebook
│
├── sql/
│   ├── create_tables.sql       # Data Warehouse DDL
│   └── queries.sql             # 6 KPI Queries
│
├── visualization/
│   └── kpi_dashboard.py        # Dashboard generator
│
├── run.py                      # MAIN ENTRY POINT ⭐
├── README.md                   # Full documentation
├── HOW_TO_RUN.md               # Execution details
├── QUICKSTART.md               # This file
└── .gitignore
```

---

## ⚙️ What run.py Does

### Phase 1: EXTRACT
- Reads: `data/raw/products.csv`, `customers.csv`, `sales.csv`, `channels.csv`
- Validates schema and data integrity
- Returns DataFrames

### Phase 2: TRANSFORM
- Creates date dimension (120 rows)
- Creates product dimension (40 rows)
- Creates customer dimension (24 rows)
- Creates channel dimension (3 rows)
- Calculates: revenue, cost, profit, margins
- Generates surrogate keys

### Phase 3: LOAD
- Creates 5 tables in SQLite:
  - dim_date (120 rows)
  - dim_product (40 rows)
  - dim_customer (24 rows)
  - dim_channel (3 rows)
  - fact_sales (240 rows)
- Enforces foreign keys & referential integrity
- Creates indexes for performance

### Phase 4: VISUALIZE (optional)
- Generates 4 KPI charts
- Creates comprehensive dashboard
- Saves as PNG files

---

## 📊 After Execution

### Data Warehouse Location
```
data/warehouse/datawarehouse.db
```

### Query the Results
```bash
# Option 1: Command line
sqlite3 data/warehouse/datawarehouse.db

# Option 2: Inside DB
.tables              # List tables
SELECT COUNT(*) FROM fact_sales;   # Check records
```

### Run KPI Queries
```bash
# Inside sqlite prompt
.read sql/queries.sql
```

### Generate Visualizations Only
```bash
python visualization/kpi_dashboard.py
```

### Interactive Analysis
```bash
jupyter notebook ETL/proto.ipynb
```

---

## ✅ Verification Checklist

After running `python run.py`, you should have:

- [x] **data/warehouse/datawarehouse.db** created (contains 5 tables)
- [x] **Dimensions loaded**: dim_date, dim_product, dim_customer, dim_channel
- [x] **Fact table loaded**: fact_sales with 240 sales records
- [x] **Foreign keys enforced**: No orphaned records
- [x] **Visualizations created**: PNG files in visualization/output/
- [x] **No errors in log**: Clean execution

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Ensure you're in project root and installed dependencies |
| `FileNotFoundError: data/raw/...` | Check that CSV files exist in data/raw/ |
| `Database is locked` | Close other connections to datawarehouse.db |
| `Permission denied` | Check write access to data/warehouse/ folder |

---

## 📚 Documentation

- **README.md** - Full project overview & requirements checklist
- **HOW_TO_RUN.md** - Detailed execution instructions
- **QUICKSTART.md** - This file (quick reference)
- **ETL/proto.ipynb** - Step-by-step tutorial notebook
- **sql/queries.sql** - All 6 KPI queries with documentation

---

## 🎯 Course Requirements

This project fulfills **100%** of the ETL Lab 3 requirements:

✅ Dimensional model (star schema)  
✅ Complete ETL pipeline  
✅ 6 KPIs with queries  
✅ 240+ sales records from 3 countries  
✅ SQLite data warehouse with referential integrity  
✅ Professional visualizations  
✅ Technical documentation  

**Status: READY FOR SUBMISSION**

---

**Version:** 1.0  
**Date:** February 2026  
**Lab:** ETL Lab 3 - Dimensional Data Modeling

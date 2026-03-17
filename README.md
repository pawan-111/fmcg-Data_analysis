# FMCG Post-Merger Data Consolidation & Analytics

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Cleaning-green)
![SQL](https://img.shields.io/badge/SQL-Star%20Schema-orange)
![PowerBI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## Problem Statement

When **GlobalFMCG Corp** (Parent Company) acquired **RegionalFresh Ltd** (Regional Brand), the combined entity faced a critical data challenge:

- Both companies operated **separate data systems** with different schemas
- **Duplicate customer records** existed across both databases
- **Inconsistent naming** for cities, categories, and products made unified reporting impossible
- Leadership needed a single dashboard showing **combined revenue, customer health, and product performance**

This project builds the complete data pipeline — from raw fragmented data to a unified analytics-ready master dataset and Power BI dashboard.

---

## Solution Overview

```
Company A Data          Company B Data
(HUL-like FMCG)       (ITC-like Regional)
      |                       |
      v                       v
  Schema Mapping         Schema Mapping
  Date Standardization   Date Standardization
  Category Normalization Category Normalization
      |                       |
      +----------+------------+
                 |
         Fuzzy Customer
           Deduplication
                 |
         Merged Master
            Dataset
                 |
        +--------+---------+
        |                  |
      SQL              Python RFM
  Star Schema          Analysis
  (Fact + Dims)     (Customer Segments)
        |                  |
        +--------+---------+
                 |
          Power BI Dashboard
```

---

## Project Structure

```
fmcg_merger_project/
│
├── data/
│   ├── company_a_sales.csv        ← GlobalFMCG raw sales data
│   ├── company_b_sales.csv        ← RegionalFresh raw sales data
│   ├── merged_sales_master.csv    ← Final unified dataset (generated)
│   └── rfm_segments.csv           ← RFM output (generated)
│
├── notebooks/
│   └── 01_data_cleaning_merging.ipynb  ← Full EDA + cleaning + merging + RFM
│
├── sql/
│   └── analysis_queries.sql       ← Star Schema DDL + 8 business queries
│
├── dashboard/
│   ├── powerbi_setup_guide.md     ← Step-by-step Power BI instructions
│   └── *.png                      ← Chart exports (generated on run)
│
└── README.md
```

---

## Key Data Challenges Solved

| Challenge | Company A | Company B | Solution |
|---|---|---|---|
| Column Names | `transaction_id` | `sale_id` | Rename mapping |
| Date Format | `YYYY-MM-DD` | `DD-MM-YYYY` | `pd.to_datetime()` with format |
| City Names | `Delhi` | `New Delhi` | Dictionary replace |
| Category Names | `Personal Care` | `Health Care` | Category normalization map |
| Customer IDs | `CA101` | `CB201` | Fuzzy match + confirmed overlap map |
| Customer Schema | `customer_name` | `cust_fullname` | Rename mapping |

---

## Business Insights Derived

- **Combined Revenue**: Merged dataset shows full P&L picture across both entities
- **Mumbai** — highest revenue city; both companies have overlapping presence
- **3 customers** identified across both systems via fuzzy name matching; deduplicated to single unified ID
- **Personal Care** is the highest revenue category post-merger
- **Company B brings new categories** (Tobacco, Staples) not present in Company A — expansion opportunity
- **RFM Analysis** segments the combined customer base into High Value, Loyal, At-Risk, and Dormant

---

## How to Run

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn fuzzywuzzy python-Levenshtein
```

### Run Notebook
```bash
cd notebooks/
jupyter notebook 01_data_cleaning_merging.ipynb
```

### Run SQL (SQLite)
```bash
# Load merged_sales_master.csv into SQLite, then:
sqlite3 fmcg.db < sql/analysis_queries.sql
```

### Power BI Dashboard
See `dashboard/powerbi_setup_guide.md` for step-by-step instructions.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10 | Data cleaning, transformation, EDA |
| Pandas | DataFrame operations, merging, date parsing |
| FuzzyWuzzy | Customer deduplication via fuzzy name matching |
| Matplotlib / Seaborn | Visualizations |
| SQL (SQLite) | Star Schema design, business queries |
| Jupyter Notebook | Analysis documentation |
| Power BI | Interactive dashboard |

---

## Skills Demonstrated

- Real-world **schema mismatch resolution** (the core challenge in any merger/acquisition)
- **Fuzzy string matching** for entity resolution
- **Star Schema** design with Fact + Dimension tables
- **RFM Customer Segmentation** using both Python and SQL
- **Power BI DAX measures** for KPI reporting
- End-to-end **data pipeline** thinking

---

## Author

**Pawan Vishwakarma**  
B.Tech Computer Science (Data Science)  
GitHub: [github.com/pawan-111](https://github.com/pawan-111)

---

> *This project simulates a real post-merger data consolidation scenario common in the FMCG industry (similar to HUL acquiring brands or ITC expanding portfolio).*

# Power BI Dashboard Setup Guide
## FMCG Post-Merger Analytics Dashboard

---

## Files to Load into Power BI

| File | Use |
|---|---|
| `data/merged_sales_master.csv` | Main fact table |
| `data/rfm_segments.csv` | Customer segments |

---

## Step 1: Load Data

1. Open Power BI Desktop
2. Click **Get Data → Text/CSV**
3. Load `merged_sales_master.csv` → name it `Sales`
4. Load `rfm_segments.csv` → name it `RFM`

---

## Step 2: Create Relationships

In **Model View**:
- `Sales[customer_id]` → `RFM[customer_id]` (Many to One)

---

## Step 3: DAX Measures

Paste these in a new table called `_Measures`:

```dax
-- Total Revenue
Total Revenue = SUM(Sales[total_amount])

-- Total Orders
Total Orders = COUNTROWS(Sales)

-- Average Order Value
Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

-- Company A Revenue
GlobalFMCG Revenue = 
    CALCULATE([Total Revenue], Sales[source_company] = "GlobalFMCG")

-- Company B Revenue
RegionalFresh Revenue = 
    CALCULATE([Total Revenue], Sales[source_company] = "RegionalFresh")

-- Revenue Share %
Revenue Share % = 
    DIVIDE([Total Revenue],
           CALCULATE([Total Revenue], ALL(Sales)),
           0) * 100

-- MoM Revenue Growth
MoM Growth % = 
VAR CurrentMonth = [Total Revenue]
VAR PrevMonth = CALCULATE([Total Revenue], DATEADD(Sales[transaction_date], -1, MONTH))
RETURN DIVIDE(CurrentMonth - PrevMonth, PrevMonth, 0) * 100

-- Customer Count
Unique Customers = DISTINCTCOUNT(Sales[customer_id])

-- Overlap Customers (bought from both)
Overlap Customers = 
COUNTROWS(
    FILTER(
        VALUES(Sales[customer_id]),
        CALCULATE(DISTINCTCOUNT(Sales[source_company])) > 1
    )
)
```

---

## Step 4: Dashboard Pages

### Page 1 — Executive Summary
- KPI Cards: Total Revenue | Total Orders | Avg Order Value | Unique Customers
- Donut Chart: Revenue split by Company (GlobalFMCG vs RegionalFresh)
- Bar Chart: Revenue by Category
- Line Chart: Monthly Revenue Trend

### Page 2 — Geographic Analysis
- Map Visual: Revenue by City (bubble size = revenue)
- Matrix: City × Company revenue comparison
- Bar: Top 5 cities by combined revenue

### Page 3 — Customer Segments
- Pie Chart: RFM Segment distribution
- Bar: Revenue by Segment
- Table: Top 10 customers with Segment, Recency, Frequency, Monetary
- KPI: Overlap Customer count

### Page 4 — Product Analysis
- Bar: Top 10 products by revenue
- Matrix: Product × Company presence (shows duplicates)
- Treemap: Revenue by Category → Product

---

## Step 5: Slicers to Add

Add these slicers to every page:
- `Sales[source_company]` — GlobalFMCG / RegionalFresh / Both
- `Sales[store_city]`
- `Sales[transaction_date]` — date range picker
- `Sales[category]`

---

## Key Insights to Highlight (for interviews)

1. **Mumbai** generates highest combined revenue (both companies present)
2. **3 customers** appear in both systems → deduplicated using fuzzy matching
3. **Personal Care** is the overlapping category with possible SKU rationalization opportunity
4. **20% of customers** = High Value segment driving majority of revenue
5. Company B brings **Tobacco & Staples** categories not present in Company A

---

*Dashboard screenshots → save in `/dashboard/` folder for GitHub README*

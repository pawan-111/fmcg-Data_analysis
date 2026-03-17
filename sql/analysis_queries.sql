-- ============================================================
-- FMCG Post-Merger SQL Analysis
-- Database: SQLite / PostgreSQL compatible
-- Dataset: merged_sales_master.csv (loaded as 'sales' table)
-- ============================================================

-- ============================================================
-- STEP 1: Create the Star Schema
-- ============================================================

-- Dimension: Customers
CREATE TABLE dim_customer (
    customer_id     TEXT PRIMARY KEY,
    customer_name   TEXT NOT NULL
);

-- Dimension: Products
CREATE TABLE dim_product (
    product_code    TEXT PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    source_company  TEXT NOT NULL
);

-- Dimension: Stores
CREATE TABLE dim_store (
    store_id        TEXT PRIMARY KEY,
    store_city      TEXT NOT NULL,
    source_company  TEXT NOT NULL
);

-- Dimension: Date
CREATE TABLE dim_date (
    date_key        TEXT PRIMARY KEY,   -- YYYY-MM-DD
    year            INTEGER,
    month           INTEGER,
    month_name      TEXT,
    quarter         TEXT
);

-- Fact Table: Sales
CREATE TABLE fact_sales (
    transaction_id  TEXT PRIMARY KEY,
    customer_id     TEXT REFERENCES dim_customer(customer_id),
    product_code    TEXT REFERENCES dim_product(product_code),
    store_id        TEXT REFERENCES dim_store(store_id),
    date_key        TEXT REFERENCES dim_date(date_key),
    quantity        INTEGER,
    unit_price      DECIMAL(10,2),
    total_amount    DECIMAL(10,2),
    source_company  TEXT
);


-- ============================================================
-- STEP 2: Business Analysis Queries
-- ============================================================

-- Query 1: Total Combined Revenue by Company
-- WHAT: Shows each company's contribution to combined revenue
-- WHY: First check post-merger — understand relative scale
SELECT
    source_company,
    COUNT(transaction_id)           AS total_transactions,
    SUM(total_amount)               AS total_revenue,
    ROUND(AVG(total_amount), 2)     AS avg_order_value
FROM fact_sales
GROUP BY source_company
ORDER BY total_revenue DESC;


-- Query 2: Revenue by Category (Combined View)
-- WHAT: Revenue breakdown per product category
-- WHY: Identifies which categories dominate post-merger and where gaps exist
SELECT
    p.category,
    SUM(f.total_amount)     AS total_revenue,
    COUNT(f.transaction_id) AS total_orders,
    ROUND(
        SUM(f.total_amount) * 100.0 /
        (SELECT SUM(total_amount) FROM fact_sales), 2
    )                       AS revenue_share_pct
FROM fact_sales f
JOIN dim_product p ON f.product_code = p.product_code
GROUP BY p.category
ORDER BY total_revenue DESC;


-- Query 3: City-wise Revenue — Where are both companies present?
-- WHAT: Revenue per city, split by company
-- WHY: Identifies overlapping markets and exclusive territories
SELECT
    s.store_city,
    SUM(CASE WHEN f.source_company = 'GlobalFMCG'    THEN f.total_amount ELSE 0 END) AS company_a_revenue,
    SUM(CASE WHEN f.source_company = 'RegionalFresh' THEN f.total_amount ELSE 0 END) AS company_b_revenue,
    SUM(f.total_amount) AS combined_revenue
FROM fact_sales f
JOIN dim_store s ON f.store_id = s.store_id
GROUP BY s.store_city
ORDER BY combined_revenue DESC;


-- Query 4: Identify Overlapping Customers
-- WHAT: Customers who bought from BOTH companies
-- WHY: These are highest-value targets — already trust both brands
SELECT
    f.customer_id,
    c.customer_name,
    COUNT(DISTINCT f.source_company)    AS companies_shopped,
    SUM(f.total_amount)                 AS total_spend,
    COUNT(f.transaction_id)             AS total_transactions
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY f.customer_id, c.customer_name
HAVING COUNT(DISTINCT f.source_company) > 1
ORDER BY total_spend DESC;


-- Query 5: Monthly Revenue Trend
-- WHAT: Month-over-month revenue for each company
-- WHY: Detects seasonality and growth trends
SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(CASE WHEN f.source_company = 'GlobalFMCG'    THEN f.total_amount ELSE 0 END) AS global_fmcg_revenue,
    SUM(CASE WHEN f.source_company = 'RegionalFresh' THEN f.total_amount ELSE 0 END) AS regional_fresh_revenue,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- Query 6: Top 10 Products by Combined Revenue
-- WHAT: Best performing SKUs across both companies
-- WHY: Post-merger catalog rationalization — which SKUs to keep/promote
SELECT
    p.product_code,
    p.product_name,
    p.category,
    p.source_company,
    SUM(f.quantity)        AS total_units_sold,
    SUM(f.total_amount)    AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_code = p.product_code
GROUP BY p.product_code, p.product_name, p.category, p.source_company
ORDER BY total_revenue DESC
LIMIT 10;


-- Query 7: RFM Segmentation using SQL
-- WHAT: Recency, Frequency, Monetary scoring in pure SQL
-- WHY: Can be run directly in the DB without Python
WITH rfm_raw AS (
    SELECT
        customer_id,
        JULIANDAY('2023-04-01') - JULIANDAY(MAX(date_key)) AS recency_days,
        COUNT(transaction_id)                               AS frequency,
        SUM(total_amount)                                   AS monetary
    FROM fact_sales
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT *,
        CASE
            WHEN recency_days <= 10  THEN 4
            WHEN recency_days <= 20  THEN 3
            WHEN recency_days <= 40  THEN 2
            ELSE 1
        END AS r_score,
        CASE
            WHEN frequency >= 5 THEN 4
            WHEN frequency >= 3 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END AS f_score,
        CASE
            WHEN monetary >= 1000 THEN 4
            WHEN monetary >= 500  THEN 3
            WHEN monetary >= 200  THEN 2
            ELSE 1
        END AS m_score
    FROM rfm_raw
)
SELECT
    customer_id,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 10 THEN 'High Value'
        WHEN (r_score + f_score + m_score) >= 7  THEN 'Loyal'
        WHEN (r_score + f_score + m_score) >= 5  THEN 'At-Risk'
        ELSE 'Dormant'
    END AS customer_segment
FROM rfm_scored
ORDER BY rfm_total DESC;


-- Query 8: Duplicate SKU Detection
-- WHAT: Products with similar names across both companies
-- WHY: Detects catalog overlap — avoid running two similar products post-merger
SELECT
    a.product_code  AS company_a_code,
    a.product_name  AS company_a_product,
    b.product_code  AS company_b_code,
    b.product_name  AS company_b_product,
    a.category
FROM dim_product a
JOIN dim_product b
    ON a.category = b.category
    AND a.source_company = 'GlobalFMCG'
    AND b.source_company = 'RegionalFresh'
ORDER BY a.category;

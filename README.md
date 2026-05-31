# FMCG AI Merger Intelligence Copilot

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Executive%20App-red)
![LangChain](https://img.shields.io/badge/LangChain-AI%20Analyst-green)
![SQL](https://img.shields.io/badge/SQL-Star%20Schema-orange)
![PowerBI](https://img.shields.io/badge/Power%20BI-Ready-yellow)

An end-to-end **AI + Data Analyst portfolio project** that simulates a post-merger FMCG integration. It turns fragmented company sales data into a clean analytics layer, customer intelligence model, executive dashboard, and LangChain-ready natural-language analyst.

The project is designed to show the skills companies currently screen for in analyst roles: messy-data cleaning, business KPI thinking, SQL modeling, BI storytelling, customer segmentation, and applied AI that helps leaders make decisions.

---

## Business Problem

**GlobalFMCG Corp** acquired **RegionalFresh Ltd**. Leadership needed one trusted view of the combined business, but the two companies had:

- different sales schemas and transaction IDs
- different date formats
- inconsistent city and category naming
- duplicate customer records across systems
- no single dashboard for revenue, customer health, product performance, and merger synergy

This project builds the post-merger data product from raw CSVs to an AI-assisted executive cockpit.

---

## What Makes This Project Stand Out

- **AI analyst copilot:** Ask natural-language business questions about revenue, categories, customers, markets, products, and merger synergy.
- **LangChain integration:** Uses a LangChain pandas dataframe agent when `OPENAI_API_KEY` is available.
- **Demo-safe fallback:** If no API key exists, the app still answers with a deterministic local analyst engine.
- **Executive dashboard:** Streamlit app with KPIs, filters, Plotly charts, RFM intelligence, cross-sell readiness, and downloadable data.
- **Business recommendations:** Converts analysis into retention, cross-sell, SKU rationalization, and city-level integration actions.
- **Classic analyst foundation:** Python cleaning, fuzzy matching, RFM segmentation, SQL star schema, and Power BI setup.

---

## Live App Features

### Project Story
- case-study narrative explaining the merger problem, data pipeline, AI layer, and business impact
- visual pipeline from raw CSVs to AI-assisted dashboard
- resume-ready bullets and interview demo flow

### Executive Cockpit
- merged revenue, orders, customers, average order value, and overlap customers
- company revenue split
- category revenue mix
- monthly revenue trend

### AI Analyst
- natural-language Q&A over the merged dataset
- LangChain + OpenAI path for real AI analysis
- local fallback engine for offline demos
- supported local questions for revenue, product count, company comparison, city targeting, RFM customers, recommendations, and architecture
- AI-prioritized insight cards with recommended actions

### Customer Intelligence
- RFM customer segmentation
- revenue by segment
- top customers by spend and order activity

### Merger Synergy
- top integration markets
- product portfolio heatmap
- cross-company customer overlap
- cross-sell readiness score

### Data Product
- filtered master data preview
- downloadable CSV
- explanation of the pipeline and modeling layer

---

## Project Structure

```text
fmcg_merger_project/
├── app.py                              # Streamlit AI merger intelligence app
├── src/
│   ├── __init__.py
│   └── ai_merger_analyst.py            # Metrics, insights, local AI fallback, LangChain agent
├── data/
│   ├── company_a_sales.csv             # GlobalFMCG raw sales data
│   ├── company_b_sales.csv             # RegionalFresh raw sales data
│   ├── merged_sales_master.csv         # Unified analytics-ready dataset
│   └── rfm_segments.csv                # Customer segmentation output
├── notebooks/
│   └── 01_data_cleaning_merging.ipynb  # Cleaning, merging, EDA, RFM workflow
├── sql/
│   └── analysis_queries.sql            # Star schema DDL and business queries
├── dashboard/
│   ├── powerbi_setup_guide.md
│   └── *.png                           # Static dashboard chart exports
├── requirements.txt
└── README.md
```

---

## Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the AI dashboard

```bash
streamlit run app.py
```

The app works without an API key using the built-in local analyst engine.

### 3. Validate the project

```bash
python validate_project.py
```

This checks required files, required data columns, core metrics, product counts, and the local AI fallback answer.

### 4. Optional: enable LangChain + OpenAI

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

When the key is configured, the AI Analyst tab uses LangChain to reason over the sales dataframe. Without the key, it automatically falls back to deterministic business-answer logic.

---

## Demo Flow for Interviews

1. Open **Executive Cockpit** and explain the merger problem in 20 seconds.
2. Point to KPIs: merged revenue, orders, customers, overlap customers, and product count.
3. Open **AI Analyst** and ask: `give total number of product in both company`.
4. Explain local engine vs LangChain + OpenAI API key.
5. Open **Customer Intelligence** and explain RFM segmentation.
6. Open **Merger Synergy** and discuss city/category/customer cross-sell opportunities.
7. Open **Project Story** to show architecture, resume bullets, and production thinking.

---

## Resume Highlights

- Built an AI-assisted FMCG post-merger analytics dashboard using Streamlit, Pandas, Plotly, LangChain, and SQL.
- Consolidated two mismatched company sales schemas into a unified analytics-ready master dataset.
- Implemented RFM customer segmentation for retention, win-back, and high-value customer targeting.
- Added a local AI analyst fallback plus optional LangChain + OpenAI dataframe agent.
- Designed executive KPI views for revenue, products, categories, cities, customers, and merger synergy.

---

## Data Challenges Solved

| Challenge | Company A | Company B | Solution |
|---|---|---|---|
| Transaction ID | `transaction_id` | `sale_id` | schema mapping |
| Customer ID | `customer_id` | `cust_code` | unified customer model |
| Customer name | `customer_name` | `cust_fullname` | normalized naming |
| Date format | `YYYY-MM-DD` | `DD-MM-YYYY` | typed date parsing |
| City names | `Delhi` | `New Delhi` | city standardization |
| Category names | `Personal Care` | `Health Care` | category normalization |
| Duplicate customers | `CA101` | `CB201` style IDs | fuzzy match + confirmed overlap map |

---

## Key Business Insights

- **Personal Care** is the strongest overlapping category and should be reviewed for joint promotions and SKU rationalization.
- **Mumbai** is the highest-value integration market, making it a strong pilot city for cross-sell campaigns.
- **Overlap customers** are the highest-signal audience because they already buy from both companies.
- **RFM segmentation** separates high-value, loyal, at-risk, and dormant customers for targeted retention and win-back campaigns.
- **RegionalFresh adds new category breadth** such as Tobacco and Staples, creating post-merger expansion opportunities.
- **16 unique products** are present across both companies: 10 from GlobalFMCG and 6 from RegionalFresh.

---

## SQL + BI Layer

The SQL file includes:

- `dim_customer`
- `dim_product`
- `dim_store`
- `dim_date`
- `fact_sales`
- business queries for revenue, categories, cities, overlap customers, monthly trend, top products, RFM, and duplicate SKU detection

Power BI setup instructions are available in `dashboard/powerbi_setup_guide.md`.

---

## Skills Demonstrated

- AI-assisted analytics with LangChain
- Streamlit product dashboard development
- Pandas data cleaning and transformation
- fuzzy customer/entity matching
- RFM customer segmentation
- SQL star schema modeling
- executive KPI design
- BI storytelling and decision recommendations
- merger/acquisition analytics framing

---

## Author

**Pawan Vishwakarma**  
B.Tech Computer Science (Data Science)  
GitHub: [github.com/pawan-111](https://github.com/pawan-111)

---

This is a simulated FMCG post-merger analytics project created for portfolio and interview demonstration.

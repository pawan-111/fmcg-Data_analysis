from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.ai_merger_analyst import (
    ai_mode_label,
    ask_ai_analyst,
    business_recommendations,
    category_performance,
    city_performance,
    company_performance,
    cross_company_overlap,
    executive_metrics,
    find_matching_insights,
    format_money,
    generate_insights,
    load_rfm,
    load_sales,
    monthly_trend,
    product_counts,
    project_architecture_summary,
    rfm_revenue_view,
    supported_questions,
    top_products,
)


st.set_page_config(
    page_title="FMCG AI Merger Intelligence",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


THEME = {
    "ink": "#18212f",
    "muted": "#5f6c7b",
    "line": "#dde5ee",
    "blue": "#1f77b4",
    "green": "#1f9d6a",
    "amber": "#f2a541",
    "red": "#df5b57",
}


st.markdown(
    """
    <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
        [data-testid="stMetricValue"] {font-size: 1.6rem;}
        [data-testid="stSidebar"] {background: #f7f9fc;}
        .hero {
            border-bottom: 1px solid #dde5ee;
            padding: 0.3rem 0 1.1rem 0;
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2.2rem;
            line-height: 1.12;
            margin-bottom: 0.35rem;
            color: #18212f;
        }
        .hero p {color: #5f6c7b; max-width: 980px; font-size: 1rem;}
        .insight-card {
            border: 1px solid #dde5ee;
            border-radius: 8px;
            padding: 1rem;
            height: 100%;
            background: #ffffff;
        }
        .priority {
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0;
            border-radius: 999px;
            padding: 0.15rem 0.55rem;
            background: #eef5ff;
            color: #1f77b4;
        }
        .small-muted {color: #5f6c7b; font-size: 0.88rem;}
        .signal-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.8rem 0 1rem 0;
        }
        .signal {
            border: 1px solid #dde5ee;
            border-radius: 8px;
            padding: 0.85rem;
            background: #ffffff;
        }
        .signal b {
            display: block;
            color: #18212f;
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
        }
        .signal span {color: #5f6c7b; font-size: 0.88rem;}
        .analyst-note {
            border: 1px solid #cfe0f5;
            border-left: 4px solid #1f77b4;
            border-radius: 8px;
            padding: 1rem;
            background: #f7fbff;
            margin-top: 0.8rem;
        }
        .pipeline {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.6rem 0 1rem 0;
        }
        .pipe-step {
            border: 1px solid #dde5ee;
            border-radius: 8px;
            padding: 0.8rem;
            background: #ffffff;
            min-height: 96px;
        }
        .pipe-step small {
            color: #1f77b4;
            font-weight: 700;
        }
        .pipe-step b {
            display: block;
            margin: 0.2rem 0;
            color: #18212f;
        }
        .pipe-step span {
            color: #5f6c7b;
            font-size: 0.86rem;
        }
        @media (max-width: 900px) {
            .signal-row, .pipeline {grid-template-columns: 1fr 1fr;}
        }
        @media (max-width: 640px) {
            .signal-row, .pipeline {grid-template-columns: 1fr;}
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def cached_data():
    sales_df = load_sales()
    rfm_df = load_rfm()
    return sales_df, rfm_df


sales, rfm = cached_data()

with st.sidebar:
    st.header("Control Room")
    st.caption(f"AI mode: {ai_mode_label()}")
    companies = sorted(sales["source_company"].unique())
    cities = sorted(sales["store_city"].unique())
    categories = sorted(sales["category"].unique())

    company_filter = st.multiselect("Company", companies, default=companies)
    city_filter = st.multiselect("City", cities, default=cities)
    category_filter = st.multiselect("Category", categories, default=categories)

    min_date = sales["transaction_date"].min().date()
    max_date = sales["transaction_date"].max().date()
    date_filter = st.date_input("Transaction window", (min_date, max_date))

filtered = sales[
    sales["source_company"].isin(company_filter)
    & sales["store_city"].isin(city_filter)
    & sales["category"].isin(category_filter)
].copy()

if isinstance(date_filter, tuple) and len(date_filter) == 2:
    start_date, end_date = date_filter
    filtered = filtered[
        (filtered["transaction_date"].dt.date >= start_date)
        & (filtered["transaction_date"].dt.date <= end_date)
    ]

if filtered.empty:
    st.warning("No records match the current filters. Adjust the control room selections.")
    st.stop()

metrics = executive_metrics(filtered, rfm)
insights = generate_insights(filtered, rfm)
total_products = int(filtered["product_code"].nunique())
top_category_row = category_performance(filtered).iloc[0]
top_city_row = city_performance(filtered).iloc[0]

st.markdown(
    """
    <div class="hero">
        <h1>FMCG AI Merger Intelligence Copilot</h1>
        <p>
            A portfolio-ready analytics product for post-acquisition sales consolidation:
            schema harmonization, customer deduplication, RFM segmentation, executive KPIs,
            synergy recommendations, and a LangChain-ready natural-language analyst.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Merged Revenue", format_money(metrics["total_revenue"]))
kpi2.metric("Orders", f"{metrics['total_orders']:,}")
kpi3.metric("Customers", f"{metrics['customers']:,}")
kpi4.metric("Avg Order Value", format_money(metrics["avg_order_value"]))
kpi5.metric("Overlap Customers", f"{metrics['overlap_customers']:,}")
kpi6.metric("Products", f"{total_products:,}")

tabs = st.tabs(
    [
        "Executive Cockpit",
        "AI Analyst",
        "Customer Intelligence",
        "Merger Synergy",
        "Project Story",
        "Data Product",
    ]
)

with tabs[0]:
    st.markdown(
        f"""
        <div class="signal-row">
            <div class="signal"><b>Top category</b><span>{top_category_row['category']} at {format_money(float(top_category_row['revenue']))}</span></div>
            <div class="signal"><b>Best city</b><span>{top_city_row['store_city']} at {format_money(float(top_city_row['combined_revenue']))}</span></div>
            <div class="signal"><b>Product portfolio</b><span>{total_products} SKUs across {int(filtered['category'].nunique())} categories</span></div>
            <div class="signal"><b>AI readiness</b><span>{ai_mode_label()}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.05, 0.95])
    with left:
        company_df = company_performance(filtered)
        fig = px.bar(
            company_df,
            x="source_company",
            y="revenue",
            color="source_company",
            text_auto=".2s",
            title="Revenue Contribution by Company",
            color_discrete_sequence=[THEME["blue"], THEME["green"], THEME["amber"]],
        )
        fig.update_layout(showlegend=False, yaxis_title="Revenue", xaxis_title="")
        st.plotly_chart(fig, width="stretch")

    with right:
        cat_df = category_performance(filtered)
        fig = px.bar(
            cat_df,
            x="revenue",
            y="category",
            orientation="h",
            color="revenue_share",
            text="revenue_share",
            title="Category Revenue Mix",
            color_continuous_scale="Blues",
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_layout(yaxis_title="", xaxis_title="Revenue", coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")

    trend = monthly_trend(filtered)
    fig = px.line(
        trend,
        x="month_start",
        y="revenue",
        color="source_company",
        markers=True,
        title="Monthly Revenue Trend",
        color_discrete_sequence=[THEME["blue"], THEME["green"], THEME["amber"]],
    )
    fig.update_layout(xaxis_title="", yaxis_title="Revenue")
    st.plotly_chart(fig, width="stretch")

with tabs[1]:
    st.subheader("Natural-Language Merger Analyst")
    st.caption("The dropdown fills an example. Replace the text box with your own business question.")

    engine_col, mode_col = st.columns([0.65, 0.35])
    with engine_col:
        st.info(
            "Local engine is a coded fallback for demo-safe questions. Add `OPENAI_API_KEY` to switch to LangChain + OpenAI for more flexible free-form analysis."
        )
    with mode_col:
        st.metric("Current AI Mode", ai_mode_label())

    sample_questions = supported_questions()
    selected_prompt = st.selectbox("Example prompt", sample_questions)
    question = st.text_area(
        "Ask your own business question",
        value=selected_prompt,
        height=110,
        help="The dropdown only fills an example. You can replace it with any question about the dataset.",
    )

    if st.button("Analyze", type="primary", width="content"):
        answer, engine = ask_ai_analyst(question, filtered, rfm)
        st.markdown(
            f"""
            <div class="analyst-note">
                <b>Engine: {engine}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(answer)

    st.subheader("Questions this demo can answer well")
    q_cols = st.columns(2)
    for idx, prompt in enumerate(sample_questions):
        q_cols[idx % 2].markdown(f"- `{prompt}`")

    st.divider()
    st.subheader("AI-Prioritized Insight Cards")
    insight_query = st.text_input("Filter insight cards", placeholder="Try: city, customer, category, retention")
    visible_insights = find_matching_insights(insight_query, insights)

    for row_start in range(0, len(visible_insights), 3):
        cols = st.columns(3)
        for col, insight in zip(cols, visible_insights[row_start : row_start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <span class="priority">{insight.priority} priority</span>
                        <h4>{insight.title}</h4>
                        <h3>{insight.metric}</h3>
                        <p>{insight.detail}</p>
                        <p class="small-muted"><b>Action:</b> {insight.recommendation}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

with tabs[2]:
    customer_view = rfm_revenue_view(filtered, rfm)
    left, right = st.columns([0.9, 1.1])
    with left:
        fig = px.pie(
            customer_view,
            names="Segment",
            values="customers",
            hole=0.48,
            title="Customer Segment Distribution",
            color_discrete_sequence=[THEME["green"], THEME["blue"], THEME["amber"], THEME["red"]],
        )
        st.plotly_chart(fig, width="stretch")

    with right:
        fig = px.bar(
            customer_view,
            x="Segment",
            y="revenue",
            color="Segment",
            text_auto=".2s",
            title="Revenue by RFM Segment",
            color_discrete_sequence=[THEME["green"], THEME["blue"], THEME["amber"], THEME["red"]],
        )
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Revenue")
        st.plotly_chart(fig, width="stretch")

    enriched = filtered.merge(rfm, on="customer_id", how="left")
    top_customers = (
        enriched.groupby(["customer_id", "customer_name", "Segment"], as_index=False)
        .agg(revenue=("total_amount", "sum"), orders=("transaction_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(12)
    )
    st.dataframe(top_customers, width="stretch", hide_index=True)

with tabs[3]:
    left, right = st.columns(2)
    with left:
        cities_df = city_performance(filtered)
        fig = px.bar(
            cities_df.head(8),
            x="store_city",
            y="combined_revenue",
            text_auto=".2s",
            title="Top Markets for Integration",
            color="combined_revenue",
            color_continuous_scale="Teal",
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="Revenue")
        st.plotly_chart(fig, width="stretch")

    with right:
        product_df = top_products(filtered)
        fig = px.treemap(
            product_df,
            path=["category", "product_name"],
            values="revenue",
            color="source_company",
            title="Product Portfolio Heatmap",
            color_discrete_sequence=[THEME["blue"], THEME["green"], THEME["amber"]],
        )
        st.plotly_chart(fig, width="stretch")

    overlap = cross_company_overlap(filtered)
    overlap_customers = (
        overlap.groupby(["customer_key", "customer_name"], as_index=False)
        .agg(
            revenue=("total_amount", "sum"),
            companies=("source_company", "nunique"),
            customer_ids=("customer_id", lambda values: ", ".join(sorted(set(values)))),
            orders=("transaction_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
        .drop(columns=["customer_key"])
    )

    gauge_value = min(metrics["overlap_customers"] * 25, 100)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=gauge_value,
            title={"text": "Cross-Sell Readiness Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": THEME["green"]},
                "steps": [
                    {"range": [0, 40], "color": "#f6d8d6"},
                    {"range": [40, 70], "color": "#fff0c9"},
                    {"range": [70, 100], "color": "#d8f1e5"},
                ],
            },
        )
    )
    st.plotly_chart(fig, width="stretch")
    st.dataframe(overlap_customers, width="stretch", hide_index=True)

with tabs[4]:
    st.subheader("Project Case Study")
    st.markdown(
        """
        This project simulates a real FMCG merger where leadership needs a single trusted view after acquiring another company. The key challenge is not only dashboarding; it is turning mismatched raw systems into a clean, explainable, decision-ready data product.
        """
    )

    st.markdown(
        """
        <div class="pipeline">
            <div class="pipe-step"><small>01</small><b>Raw sources</b><span>Company A and Company B sales files with different schemas.</span></div>
            <div class="pipe-step"><small>02</small><b>Cleaning</b><span>Column mapping, date parsing, city and category normalization.</span></div>
            <div class="pipe-step"><small>03</small><b>Entity resolution</b><span>Customer overlap detection using normalized names.</span></div>
            <div class="pipe-step"><small>04</small><b>Master data</b><span>Unified sales master for analytics and BI.</span></div>
            <div class="pipe-step"><small>05</small><b>Customer analytics</b><span>RFM segmentation for retention and win-back use cases.</span></div>
            <div class="pipe-step"><small>06</small><b>SQL model</b><span>Fact and dimension thinking for BI readiness.</span></div>
            <div class="pipe-step"><small>07</small><b>Executive app</b><span>KPIs, filters, charts, and downloadable data.</span></div>
            <div class="pipe-step"><small>08</small><b>AI analyst</b><span>Local fallback plus optional LangChain + OpenAI agent.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Architecture")
        st.write(project_architecture_summary())
        st.subheader("Resume bullets")
        st.markdown(
            """
            - Built an AI-assisted FMCG merger analytics dashboard using Streamlit, Pandas, Plotly, LangChain, and SQL.
            - Consolidated mismatched company sales schemas into a unified analytics-ready master dataset.
            - Implemented RFM segmentation and business Q&A for customer retention and merger synergy analysis.
            - Designed executive KPIs, category/city/product analysis, and cross-sell recommendations.
            """
        )
    with right:
        st.subheader("Business recommendations")
        for item in business_recommendations(filtered, rfm)[:4]:
            st.markdown(f"- {item}")

    st.subheader("Interview demo flow")
    st.markdown(
        """
        1. Start with the merger problem and Executive Cockpit KPIs.
        2. Ask AI Analyst: `give total number of product in both company`.
        3. Show Customer Intelligence and explain RFM segmentation.
        4. Show Merger Synergy and discuss cross-sell readiness.
        5. End with production improvements: data warehouse, tests, scheduled ETL, and LLM guardrails.
        """
    )

with tabs[5]:
    st.subheader("Why this is more than a dashboard")
    st.markdown(
        """
        - **Data engineering:** normalizes mismatched schemas, dates, city names, category names, and customer identifiers.
        - **Analytics modeling:** produces a clean sales master, RFM table, star-schema SQL, and BI-ready outputs.
        - **AI layer:** wraps the merged dataset with a LangChain dataframe agent when an API key is available.
        - **Business actionability:** converts metrics into retention, cross-sell, SKU rationalization, and market-entry recommendations.
        """
    )

    st.subheader("Filtered Data Preview")
    st.dataframe(filtered.sort_values("transaction_date"), width="stretch", hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered sales master",
        data=csv,
        file_name="filtered_fmcg_sales_master.csv",
        mime="text/csv",
    )

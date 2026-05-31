from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class Insight:
    title: str
    metric: str
    detail: str
    recommendation: str
    priority: str = "Medium"


def load_sales(path: str = "data/merged_sales_master.csv") -> pd.DataFrame:
    """Load the unified sales master with typed dates."""
    df = pd.read_csv(path)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    return df


def load_rfm(path: str = "data/rfm_segments.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def format_money(value: float) -> str:
    return f"Rs {value:,.0f}"


def normalized_customer_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(name).lower()).strip()


def cross_company_overlap(sales: pd.DataFrame) -> pd.DataFrame:
    """Return rows for customers whose normalized names appear in both companies."""
    keyed = sales.assign(customer_key=sales["customer_name"].map(normalized_customer_name))
    overlap_keys = (
        keyed.groupby("customer_key")["source_company"]
        .nunique()
        .loc[lambda series: series > 1]
        .index
    )
    return keyed[keyed["customer_key"].isin(overlap_keys)].copy()


def executive_metrics(sales: pd.DataFrame, rfm: pd.DataFrame) -> dict[str, float | int | str]:
    total_revenue = float(sales["total_amount"].sum())
    total_orders = int(sales["transaction_id"].nunique())
    customers = int(sales["customer_id"].nunique())
    avg_order_value = total_revenue / total_orders if total_orders else 0
    high_value_customers = int((rfm["Segment"] == "High Value").sum())
    overlap_customers = int(cross_company_overlap(sales)["customer_key"].nunique())

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "customers": customers,
        "avg_order_value": avg_order_value,
        "high_value_customers": high_value_customers,
        "overlap_customers": overlap_customers,
    }


def company_performance(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.groupby("source_company", as_index=False)
        .agg(
            revenue=("total_amount", "sum"),
            orders=("transaction_id", "nunique"),
            customers=("customer_id", "nunique"),
            avg_order_value=("total_amount", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )


def category_performance(sales: pd.DataFrame) -> pd.DataFrame:
    category = (
        sales.groupby("category", as_index=False)
        .agg(
            revenue=("total_amount", "sum"),
            orders=("transaction_id", "nunique"),
            units=("quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )
    category["revenue_share"] = category["revenue"] / category["revenue"].sum()
    return category


def city_performance(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.pivot_table(
            index="store_city",
            columns="source_company",
            values="total_amount",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .assign(combined_revenue=lambda df: df.drop(columns=["store_city"]).sum(axis=1))
        .sort_values("combined_revenue", ascending=False)
    )


def monthly_trend(sales: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        sales.assign(month_start=sales["transaction_date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month_start", "source_company"], as_index=False)["total_amount"]
        .sum()
        .rename(columns={"total_amount": "revenue"})
    )
    return monthly.sort_values("month_start")


def rfm_revenue_view(sales: pd.DataFrame, rfm: pd.DataFrame) -> pd.DataFrame:
    merged = sales.merge(rfm[["customer_id", "Segment", "RFM_Score"]], on="customer_id", how="left")
    return (
        merged.groupby("Segment", as_index=False)
        .agg(
            revenue=("total_amount", "sum"),
            customers=("customer_id", "nunique"),
            orders=("transaction_id", "nunique"),
            avg_rfm=("RFM_Score", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )


def top_products(sales: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    return (
        sales.groupby(["product_name", "category", "source_company"], as_index=False)
        .agg(revenue=("total_amount", "sum"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
        .head(limit)
    )


def product_counts(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.groupby("source_company", as_index=False)
        .agg(
            unique_products=("product_code", "nunique"),
            categories=("category", "nunique"),
            orders=("transaction_id", "nunique"),
        )
        .sort_values("unique_products", ascending=False)
    )


def customer_segment_counts(rfm: pd.DataFrame) -> pd.DataFrame:
    return (
        rfm.groupby("Segment", as_index=False)
        .agg(customers=("customer_id", "nunique"), avg_score=("RFM_Score", "mean"))
        .sort_values(["customers", "avg_score"], ascending=[False, False])
    )


def ai_mode_label() -> str:
    if os.getenv("OPENAI_API_KEY"):
        return "LangChain + OpenAI enabled"
    return "Local analyst fallback"


def supported_questions() -> list[str]:
    return [
        "Give total number of products in both company.",
        "Compare both companies by revenue and customers.",
        "Which category has highest revenue?",
        "Which city should we target first?",
        "How many high value customers are there?",
        "Give me 3 business recommendations.",
        "What is the strongest merger synergy opportunity?",
        "Show revenue split by company.",
        "Which products are top performers?",
        "Explain this project architecture.",
    ]


def project_architecture_summary() -> str:
    return (
        "Raw Company A and Company B CSVs -> schema mapping -> date, city, and category "
        "standardization -> customer entity resolution -> merged sales master -> RFM segmentation "
        "-> SQL star schema -> Streamlit executive dashboard -> AI Analyst layer."
    )


def business_recommendations(sales: pd.DataFrame, rfm: pd.DataFrame) -> list[str]:
    top_city = city_performance(sales).iloc[0]
    top_category = category_performance(sales).iloc[0]
    segment_view = rfm_revenue_view(sales, rfm)
    top_segment = segment_view.iloc[0] if not segment_view.empty else None
    overlap_count = int(cross_company_overlap(sales)["customer_key"].nunique())

    recommendations = [
        (
            f"Pilot cross-sell campaigns in {top_city['store_city']} because it is the strongest "
            f"combined market at {format_money(float(top_city['combined_revenue']))}."
        ),
        (
            f"Prioritize {top_category['category']} for SKU rationalization and bundled offers "
            f"because it contributes {top_category['revenue_share']:.1%} of revenue."
        ),
        (
            f"Create a retention list for {overlap_count} cross-company customers because they "
            "already show trust in both businesses."
        ),
    ]
    if top_segment is not None:
        recommendations.append(
            f"Protect the {top_segment['Segment']} segment first because it leads segment revenue "
            f"at {format_money(float(top_segment['revenue']))}."
        )
    return recommendations


def compare_companies(sales: pd.DataFrame) -> str:
    companies = company_performance(sales)
    products = product_counts(sales).set_index("source_company")
    lines = ["Company comparison:"]
    for row in companies.itertuples(index=False):
        product_count = int(products.loc[row.source_company, "unique_products"])
        lines.append(
            f"- {row.source_company}: {format_money(row.revenue)} revenue, "
            f"{row.orders} orders, {row.customers} customers, {product_count} products, "
            f"{format_money(row.avg_order_value)} average order value"
        )
    leader = companies.iloc[0]
    lines.append(
        f"Business read: {leader['source_company']} is the current revenue leader, "
        "so its go-to-market pattern should be studied before scaling merger campaigns."
    )
    return "\n".join(lines)


def generate_insights(sales: pd.DataFrame, rfm: pd.DataFrame) -> list[Insight]:
    metrics = executive_metrics(sales, rfm)
    companies = company_performance(sales)
    categories = category_performance(sales)
    cities = city_performance(sales)
    rfm_view = rfm_revenue_view(sales, rfm)

    top_company = companies.iloc[0]
    top_category = categories.iloc[0]
    top_city = cities.iloc[0]
    top_segment = rfm_view.iloc[0]

    overlap = cross_company_overlap(sales)
    overlap_revenue = float(overlap["total_amount"].sum())
    overlap_share = overlap_revenue / metrics["total_revenue"] if metrics["total_revenue"] else 0

    return [
        Insight(
            title="Executive revenue base",
            metric=format_money(metrics["total_revenue"]),
            detail=(
                f"{metrics['total_orders']} unified transactions across "
                f"{metrics['customers']} deduplicated customers."
            ),
            recommendation="Use this as the single post-merger source of truth for sales reporting.",
            priority="High",
        ),
        Insight(
            title="Dominant revenue engine",
            metric=f"{top_company['source_company']} leads",
            detail=(
                f"{top_company['source_company']} contributes "
                f"{format_money(float(top_company['revenue']))} in revenue."
            ),
            recommendation="Benchmark RegionalFresh performance against GlobalFMCG's strongest stores and categories.",
            priority="High",
        ),
        Insight(
            title="Category rationalization",
            metric=f"{top_category['category']} is #{1}",
            detail=(
                f"{top_category['category']} contributes "
                f"{top_category['revenue_share']:.1%} of total revenue."
            ),
            recommendation="Prioritize joint promotions and SKU overlap review in the highest-share category.",
            priority="High",
        ),
        Insight(
            title="Geographic synergy",
            metric=str(top_city["store_city"]),
            detail=f"{top_city['store_city']} is the strongest city at {format_money(float(top_city['combined_revenue']))}.",
            recommendation="Treat this as the pilot city for cross-sell campaigns and distributor consolidation.",
            priority="Medium",
        ),
        Insight(
            title="Cross-company loyalty pool",
            metric=f"{metrics['overlap_customers']} overlap customers",
            detail=f"Overlap customers generate {format_money(overlap_revenue)} ({overlap_share:.1%} of revenue).",
            recommendation="Build a retention list for customers already buying from both companies.",
            priority="High",
        ),
        Insight(
            title="Customer segment focus",
            metric=str(top_segment["Segment"]),
            detail=(
                f"{top_segment['Segment']} customers lead revenue at "
                f"{format_money(float(top_segment['revenue']))}."
            ),
            recommendation="Use RFM scores to target high-value retention and at-risk win-back journeys.",
            priority="Medium",
        ),
    ]


def answer_with_local_analyst(question: str, sales: pd.DataFrame, rfm: pd.DataFrame) -> str:
    """Deterministic analyst fallback for demos without an LLM key."""
    q = question.lower().strip()
    metrics = executive_metrics(sales, rfm)

    if not q:
        return "Ask about revenue, categories, products, customers, cities, company comparison, recommendations, architecture, or merger synergy."

    if any(word in q for word in ["architecture", "pipeline", "workflow", "flow", "how project"]):
        return (
            "Project architecture:\n"
            f"{project_architecture_summary()}\n"
            "Business value: this turns fragmented post-merger sales data into an executive-ready analytics and AI decision-support product."
        )

    if any(word in q for word in ["recommend", "recommendation", "action", "suggest", "next step"]):
        lines = ["Recommended business actions:"]
        lines.extend(f"- {item}" for item in business_recommendations(sales, rfm)[:3])
        return "\n".join(lines)

    if any(word in q for word in ["compare", "comparison", "versus", "vs", "better company"]):
        return compare_companies(sales)

    if any(word in q for word in ["revenue", "sales", "turnover"]):
        companies = company_performance(sales)
        lines = [
            f"Total merged revenue is {format_money(metrics['total_revenue'])}.",
            "Company split:",
        ]
        for row in companies.itertuples(index=False):
            lines.append(f"- {row.source_company}: {format_money(row.revenue)} from {row.orders} orders")
        return "\n".join(lines)

    if any(word in q for word in ["category", "categories", "sku"]):
        category = category_performance(sales).head(5)
        top = category.iloc[0]
        if any(word in q for word in ["highest", "top", "best", "maximum", "max"]):
            return (
                f"{top['category']} has the highest revenue at {format_money(float(top['revenue']))}, "
                f"which is {top['revenue_share']:.1%} of filtered revenue.\n"
                "Recommendation: use it for joint promotions and SKU rationalization first."
            )
        lines = ["Top categories by revenue:"]
        lines.extend(
            f"- {row.category}: {format_money(row.revenue)} ({row.revenue_share:.1%} share)"
            for row in category.itertuples(index=False)
        )
        lines.append("Recommendation: start SKU rationalization and bundled offers in the highest-share categories.")
        return "\n".join(lines)

    if any(word in q for word in ["city", "cities", "location", "market"]):
        cities = city_performance(sales).head(5)
        if any(word in q for word in ["target", "first", "best", "highest", "pilot"]):
            top = cities.iloc[0]
            return (
                f"Target {top['store_city']} first. It has the highest combined revenue at "
                f"{format_money(float(top['combined_revenue']))}.\n"
                "Recommendation: use it as the pilot city for cross-sell and distributor integration."
            )
        lines = ["Best city markets by combined revenue:"]
        lines.extend(
            f"- {row.store_city}: {format_money(row.combined_revenue)}"
            for row in cities.itertuples(index=False)
        )
        lines.append("Recommendation: use the top overlap city as the merger pilot market.")
        return "\n".join(lines)

    if any(word in q for word in ["customer", "segment", "rfm", "loyal", "retention", "dormant", "at-risk", "high value"]):
        if any(term in q for term in ["how many", "count", "number", "total"]) and "high" in q:
            high_value = int((rfm["Segment"] == "High Value").sum())
            return (
                f"There are {high_value} High Value customers in the RFM output.\n"
                "Recommendation: prioritize them for retention, premium offers, and cross-sell campaigns."
            )
        rfm_view = rfm_revenue_view(sales, rfm)
        lines = ["Customer segment view:"]
        lines.extend(
            f"- {row.Segment}: {row.customers} customers, {format_money(row.revenue)} revenue"
            for row in rfm_view.itertuples(index=False)
        )
        lines.append("Recommendation: protect High Value customers and run win-back campaigns for At-Risk/Dormant groups.")
        return "\n".join(lines)

    if any(word in q for word in ["product", "products", "item"]):
        if any(word in q for word in ["count", "number", "total", "many", "how many"]):
            counts = product_counts(sales)
            total_products = int(sales["product_code"].nunique())
            total_categories = int(sales["category"].nunique())
            lines = [
                f"There are {total_products} unique products across both companies.",
                f"These products are spread across {total_categories} categories.",
                "Company-wise product count:",
            ]
            lines.extend(
                f"- {row.source_company}: {row.unique_products} unique products across {row.categories} categories"
                for row in counts.itertuples(index=False)
            )
            return "\n".join(lines)

        products = top_products(sales, 5)
        lines = ["Top products by revenue:"]
        lines.extend(
            f"- {row.product_name} ({row.source_company}): {format_money(row.revenue)}"
            for row in products.itertuples(index=False)
        )
        return "\n".join(lines)

    if any(word in q for word in ["synergy", "merger", "acquisition", "overlap"]):
        overlap_count = int(cross_company_overlap(sales)["customer_key"].nunique())
        top_city = city_performance(sales).iloc[0]
        top_category = category_performance(sales).iloc[0]
        return (
            f"The strongest synergy signal is {overlap_count} cross-company customers, "
            f"plus {top_city['store_city']} as the highest combined market and "
            f"{top_category['category']} as the strongest category. "
            "Recommended next step: pilot a cross-sell campaign in the top city and measure uplift by customer segment."
        )

    insights = generate_insights(sales, rfm)[:3]
    lines = [
        "I could not map that question to a precise local rule, so here are the strongest available insights:",
    ]
    lines.extend(f"- {item.title}: {item.metric}. {item.recommendation}" for item in insights)
    lines.append("Tip: use OpenAI API mode for more flexible free-form questions.")
    return "\n".join(lines)


def build_langchain_agent(sales: pd.DataFrame):
    """Create a LangChain dataframe agent when optional AI dependencies and a key exist."""
    if not os.getenv("OPENAI_API_KEY"):
        return None

    try:
        from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.1)
    prefix = (
        "You are an AI merger data analyst. Answer like a sharp business analyst: "
        "show the metric, explain the business meaning, and end with one recommended action. "
        "The dataframe is a unified FMCG post-merger sales master."
    )
    return create_pandas_dataframe_agent(
        llm,
        sales,
        prefix=prefix,
        verbose=False,
        allow_dangerous_code=True,
        agent_executor_kwargs={"handle_parsing_errors": True},
    )


def ask_ai_analyst(question: str, sales: pd.DataFrame, rfm: pd.DataFrame) -> tuple[str, str]:
    agent = build_langchain_agent(sales)
    if agent is None:
        return answer_with_local_analyst(question, sales, rfm), "Local analyst engine"

    try:
        response = agent.invoke({"input": question})
        return str(response.get("output", response)), "LangChain + OpenAI"
    except Exception as exc:  # pragma: no cover - defensive UI fallback
        fallback = answer_with_local_analyst(question, sales, rfm)
        return f"{fallback}\n\nAI service fallback note: {exc}", "Local fallback after AI error"


def find_matching_insights(query: str, insights: Iterable[Insight]) -> list[Insight]:
    tokens = set(re.findall(r"[a-zA-Z]+", query.lower()))
    if not tokens:
        return list(insights)

    matched = []
    for insight in insights:
        haystack = f"{insight.title} {insight.detail} {insight.recommendation}".lower()
        if any(token in haystack for token in tokens):
            matched.append(insight)
    return matched or list(insights)

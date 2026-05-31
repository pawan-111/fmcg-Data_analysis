from __future__ import annotations

from pathlib import Path

from src.ai_merger_analyst import (
    answer_with_local_analyst,
    executive_metrics,
    load_rfm,
    load_sales,
    product_counts,
)


ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "data/company_a_sales.csv",
        "data/company_b_sales.csv",
        "data/merged_sales_master.csv",
        "data/rfm_segments.csv",
        "sql/analysis_queries.sql",
        "src/ai_merger_analyst.py",
    ]
    for file_name in required_files:
        require((ROOT / file_name).exists(), f"Missing required file: {file_name}")

    sales = load_sales(ROOT / "data" / "merged_sales_master.csv")
    rfm = load_rfm(ROOT / "data" / "rfm_segments.csv")

    expected_sales_columns = {
        "transaction_id",
        "customer_id",
        "customer_name",
        "product_code",
        "product_name",
        "category",
        "quantity",
        "unit_price",
        "total_amount",
        "store_city",
        "transaction_date",
        "source_company",
    }
    require(expected_sales_columns.issubset(sales.columns), "Sales master is missing required columns.")
    require({"customer_id", "Segment", "RFM_Score"}.issubset(rfm.columns), "RFM file is missing required columns.")

    metrics = executive_metrics(sales, rfm)
    require(metrics["total_revenue"] == 21340.0, "Unexpected total revenue.")
    require(metrics["total_orders"] == 60, "Unexpected order count.")
    require(metrics["customers"] == 32, "Unexpected customer count.")

    products = product_counts(sales).set_index("source_company")
    require(int(sales["product_code"].nunique()) == 16, "Unexpected total product count.")
    require(int(products.loc["GlobalFMCG", "unique_products"]) == 10, "Unexpected GlobalFMCG product count.")
    require(int(products.loc["RegionalFresh", "unique_products"]) == 6, "Unexpected RegionalFresh product count.")

    answer = answer_with_local_analyst("give total number of product in both company", sales, rfm)
    require("16 unique products" in answer, "Local analyst product-count answer failed.")
    require("GlobalFMCG: 10" in answer, "Local analyst GlobalFMCG product count failed.")
    require("RegionalFresh: 6" in answer, "Local analyst RegionalFresh product count failed.")

    print("Project validation passed.")
    print(f"Revenue: Rs {metrics['total_revenue']:,.0f}")
    print(f"Orders: {metrics['total_orders']}")
    print("Products: 16 total, GlobalFMCG 10, RegionalFresh 6")


if __name__ == "__main__":
    main()

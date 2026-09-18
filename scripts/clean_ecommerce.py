"""
Clean the e-commerce sales dataset.
Approach: flag data-quality issues in dedicated columns rather than dropping rows,
so revenue totals stay auditable and the dashboard can surface what was caught.
"""
import json
import pandas as pd

RAW_PATH = "../data/raw/ecommerce_raw.csv"
OUT_CSV = "../data/processed/ecommerce_clean.csv"
OUT_REPORT = "../data/processed/ecommerce_quality_report.json"

df = pd.read_csv(RAW_PATH, parse_dates=["OrderDate", "SignupDate"])
n_start = len(df)

quality_report = {"dataset": "ecommerce_clean_final_data", "rows_in": n_start, "issues": []}

# --- Issue 1: negative Quantity / Sales on orders still marked Completed ---
df["flag_negative_value"] = (df["Quantity"] < 0) | (df["Sales"] < 0)
n_negative = int(df["flag_negative_value"].sum())
n_negative_completed = int(((df["flag_negative_value"]) & (df["Status"] == "Completed")).sum())
quality_report["issues"].append({
    "issue": "negative Quantity/Sales on orders (many still marked Completed)",
    "rows_affected": n_negative,
    "of_which_status_completed": n_negative_completed,
    "action": "flagged (flag_negative_value column), not dropped -- excluded from revenue KPIs downstream but visible in the dashboard's data-quality panel",
})

# --- Issue 2: zero-quantity orders (also implausible) ---
df["flag_zero_quantity"] = df["Quantity"] == 0
n_zero = int(df["flag_zero_quantity"].sum())
quality_report["issues"].append({
    "issue": "zero-quantity orders",
    "rows_affected": n_zero,
    "action": "flagged (flag_zero_quantity column), not dropped",
})

quality_report["nulls_found"] = int(df.isnull().sum().sum())
quality_report["duplicates_found"] = int(df.duplicated().sum())
quality_report["clean_revenue_row_count"] = int((~df["flag_negative_value"] & ~df["flag_zero_quantity"]).sum())

# --- Feature engineering for the story ---
df["OrderMonth"] = df["OrderDate"].dt.to_period("M").astype(str)
df["AgeGroup"] = pd.cut(df["Age"], bins=[0, 25, 35, 45, 55, 100],
                         labels=["<25", "25-34", "35-44", "45-54", "55+"])

df.to_csv(OUT_CSV, index=False)

# --- Aggregates for the dashboard (computed on the *clean* subset only) ---
clean = df[~df["flag_negative_value"] & ~df["flag_zero_quantity"]]

summary = {
    "total_orders": len(df),
    "clean_orders_used_for_kpis": len(clean),
    "flagged_orders_excluded_from_kpis": n_negative + n_zero,
    "total_revenue": round(float(clean["Sales"].sum()), 2),
    "status_breakdown": df["Status"].value_counts().to_dict(),
    "category_revenue": clean.groupby("Category")["Sales"].sum().round(2).sort_values(ascending=False).to_dict(),
    "revenue_by_month": clean.groupby("OrderMonth")["Sales"].sum().round(2).to_dict(),
    "segment_breakdown": df["CustomerSegment"].value_counts().to_dict(),
    "payment_method_breakdown": df["PaymentMethod"].value_counts().to_dict(),
    "top_cities": df["City"].value_counts().head(10).to_dict(),
}
quality_report["dashboard_summary"] = summary

with open(OUT_REPORT, "w") as f:
    json.dump(quality_report, f, indent=2, default=str)

print(f"Cleaned {n_start} -> {len(df)} rows (all rows kept; {n_negative + n_zero} flagged)")
print("Wrote:", OUT_CSV, "and", OUT_REPORT)

"""Build the small JSON files the static dashboard reads directly."""
import json
import pandas as pd

# ---------- E-commerce ----------
with open("../data/processed/ecommerce_quality_report.json") as f:
    eco_report = json.load(f)

eco_out = {
    "total_revenue": eco_report["dashboard_summary"]["total_revenue"],
    "total_orders": eco_report["dashboard_summary"]["total_orders"],
    "flagged_orders": eco_report["dashboard_summary"]["flagged_orders_excluded_from_kpis"],
    "status_breakdown": eco_report["dashboard_summary"]["status_breakdown"],
    "category_revenue": eco_report["dashboard_summary"]["category_revenue"],
    "revenue_by_month": eco_report["dashboard_summary"]["revenue_by_month"],
    "segment_breakdown": eco_report["dashboard_summary"]["segment_breakdown"],
    "payment_method_breakdown": eco_report["dashboard_summary"]["payment_method_breakdown"],
    "top_cities": eco_report["dashboard_summary"]["top_cities"],
}
with open("../dashboard/data/ecommerce.json", "w") as f:
    json.dump(eco_out, f, indent=2)

# ---------- Drug ----------
df = pd.read_csv("../data/processed/drug_clean.csv")

drug_out = {
    "n_rows": len(df),
    "casing_fixed_rows": int(df["drug_label_was_inconsistent"].sum()),
    "drug_distribution": df["Drug"].value_counts().to_dict(),
    "na_to_k_median_by_drug": df.groupby("Drug")["Na_to_K"].median().round(2).to_dict(),
    "scatter_points": [
        {"age": int(r.Age), "na_to_k": float(r.Na_to_K), "drug": r.Drug}
        for r in df.itertuples()
    ],
}
with open("../dashboard/data/drug.json", "w") as f:
    json.dump(drug_out, f, indent=2)

print("Exported ecommerce.json and drug.json")

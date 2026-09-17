"""
Clean the drug classification dataset.
Approach: flag data-quality issues in dedicated columns rather than dropping rows,
so nothing is silently lost and the dashboard can surface what was fixed.
"""
import json
import pandas as pd

RAW_PATH = "../data/raw/drug200_raw.csv"
OUT_CSV = "../data/processed/drug_clean.csv"
OUT_REPORT = "../data/processed/drug_quality_report.json"

df = pd.read_csv(RAW_PATH)
n_start = len(df)

quality_report = {"dataset": "drug200", "rows_in": n_start, "issues": []}

# --- Issue 1: inconsistent casing in Drug labels (DrugY vs drugA/B/C/X) ---
raw_labels = sorted(df["Drug"].unique().tolist())
canonical_map = {label: "Drug" + label[-1].upper() for label in raw_labels}
df["drug_label_was_inconsistent"] = df["Drug"] != df["Drug"].map(canonical_map)
n_fixed_casing = df["drug_label_was_inconsistent"].sum()
df["Drug"] = df["Drug"].map(canonical_map)
quality_report["issues"].append({
    "issue": "inconsistent capitalization in Drug column",
    "example_raw_values": raw_labels,
    "standardized_to": sorted(set(canonical_map.values())),
    "rows_affected": int(n_fixed_casing),
})

# --- Sanity checks (no fixes needed, but documented) ---
quality_report["nulls_found"] = int(df.isnull().sum().sum())
quality_report["duplicates_found"] = int(df.duplicated().sum())

# --- Feature engineering for the story ---
df["AgeGroup"] = pd.cut(
    df["Age"], bins=[0, 30, 45, 60, 100],
    labels=["<30", "30-45", "46-60", "60+"]
)
# The headline pattern: Na_to_K above ~15 is an almost perfect predictor of Drug Y
df["NaK_Band"] = pd.cut(
    df["Na_to_K"], bins=[0, 15, 100],
    labels=["<=15 (typical range)", ">15 (high)"]
)

df.to_csv(OUT_CSV, index=False)

# --- Extra summary stats for the dashboard ---
quality_report["rows_out"] = len(df)
quality_report["drug_distribution"] = df["Drug"].value_counts().to_dict()
quality_report["na_to_k_median_by_drug"] = df.groupby("Drug")["Na_to_K"].median().round(2).to_dict()
quality_report["age_median_by_drug"] = df.groupby("Drug")["Age"].median().to_dict()
quality_report["nak_band_vs_drug"] = (
    df.groupby(["NaK_Band", "Drug"], observed=True).size().unstack(fill_value=0).to_dict()
)

with open(OUT_REPORT, "w") as f:
    json.dump(quality_report, f, indent=2, default=str)

print(f"Cleaned {n_start} -> {len(df)} rows")
print(f"Fixed casing on {n_fixed_casing} rows")
print("Wrote:", OUT_CSV, "and", OUT_REPORT)

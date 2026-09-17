# Raw Data → Visual Story

MLH Hack Week exercise: clean, analyze, and visualize two unrelated datasets, then tell the story as a static dashboard.

**Live story, two chapters:**
1. **Retail** — an e-commerce transactions dataset (~49K orders)
2. **Clinical** — a drug-prescription dataset (200 patients)

## The headline findings

- **Retail**: $3.45M in clean revenue, Electronics-led. 24 orders were flagged (negative or zero quantity) rather than deleted, and order volume drops ~35% from Feb 2026 — flagged as an open question, not a conclusion, since the data alone can't say whether that's a real slowdown or incomplete collection.
- **Clinical**: a sodium-to-potassium ratio above 15 predicts a Drug Y prescription with 100% accuracy in this dataset (91/91). The source file also had inconsistent capitalization in the `Drug` column (`DrugY` vs `drugA`/`drugB`/`drugC`/`drugX`) affecting 109 of 200 rows — fixed before any aggregation.

## Repo structure

```
data/
  raw/                    # untouched originals
  processed/              # cleaned CSVs + JSON quality reports
scripts/
  clean_ecommerce.py      # profiling + flag-don't-drop cleaning
  clean_drug.py
  export_dashboard_data.py  # builds the small JSON files the dashboard reads
dashboard/
  index.html / style.css / script.js   # static site, Plotly.js via CDN
  data/*.json             # pre-computed chart data (no backend needed)
```

## Methodology: flag, don't drop

Every cleaning step keeps every row. Instead of deleting anything that looks wrong,
we add a boolean flag column and exclude flagged rows only from the specific KPI
they'd distort (e.g. revenue totals) — so nothing disappears silently, and the
flagged rows stay auditable in `data/processed/*.csv`.

## Running it locally

```bash
pip install -r requirements.txt
cd scripts
python clean_drug.py
python clean_ecommerce.py
python export_dashboard_data.py

# serve the dashboard (fetch() needs http, not file://)
cd ../dashboard
python -m http.server 8000
# open http://localhost:8000
```

## Deploying

**Vercel**: `vercel --prod` from inside `dashboard/` (it's a static site, zero config needed).

**GitHub Pages**: push this repo, then in Settings → Pages, set the source to the
`dashboard/` folder on your default branch (or copy `dashboard/`'s contents to
a `docs/` folder or `gh-pages` branch, depending on your preference).

## Data sources

- E-commerce: [E-Commerce Sales Data Analysis & EDA](https://www.kaggle.com/datasets/erfan4524/e-commerce-sales-data-analysis-and-eda) (Kaggle)
- Drug classification: [Drug Classification](https://www.kaggle.com/datasets/prathamtripathi/drug-classification) (Kaggle)

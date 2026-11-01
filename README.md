# BlinkIT Grocery Sales Analysis

A reproducible student project exploring product, category, outlet, and location performance with Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter, Streamlit, and Altair. The project follows the four objectives in the supplied Sapphire IQ brief: understand performance, assess data reliability, identify drivers, and recommend practical actions.

## Open the interactive dashboard

**[Launch the dashboard](https://drviper59.github.io/blinkit-grocery-sales-analysis/)** · [View the GitHub project](https://github.com/drviper59/blinkit-grocery-sales-analysis)

The hosted dashboard offers filters for product, outlet, location, size, and fat content, plus Overview, Products, and Outlets & Signals views. GitHub Pages must be enabled for this repository before the hosted link becomes available. The same Streamlit app is available locally with `streamlit run app.py`.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook notebooks/blinkit_grocery_sales_analysis.ipynb

# Launch the interactive dashboard
streamlit run app.py
```

The workbook is included at `data/blinkit_grocery_data.xlsx`; the notebook resolves it relative to its own location. Run cells from top to bottom.

## Interactive dashboard

Launch with `streamlit run app.py`. The dashboard provides global filters for product type, outlet type, location tier, size, and fat content. The overview compares category and location totals; the product tab ranks categories and compares sales distributions; the outlet tab shows totals against average sales per record, a visibility relationship view, and an outlet detail table. Use **Reset all filters** in the sidebar to restore the full dataset. Charts support hover details, and all headline measures respond to the selected filters.

## Data and definitions

The supplied workbook has 8,523 item/outlet records and 12 columns. `Sales` is analyzed as the recorded item-level sales amount; the workbook does not include transaction dates, costs, margins, or unique transaction IDs. Findings describe this provided dataset and do not establish causality or profitability. The 1,463 missing item weights are preserved; weight-based analysis excludes missing weights.

## Analysis contents

- Data shape, types, missing values, duplicates, ranges, and category consistency
- Standardization of `LF`, `low fat`, and `reg` labels
- Overall sales, average item sales, ratings, product mix, outlet type/size/location performance
- Item visibility, weight, and rating relationship checks
- Ranked visual summaries and business recommendations

## Key findings (from the supplied workbook)

- Recorded sales total **1,201,681.49** across 8,523 rows; mean row sales are **140.99** and mean rating is **3.97/5**.
- Supermarket Type1 contributes **787,549.89 (65.5%)** of recorded sales, largely alongside its larger row count (5,577 records). Mean row sales are similar across outlet types (~139.80–141.68), so total contribution should not be mistaken for stronger per-record performance.
- Tier 3 has the highest location total (**472,133.03**) and highest count of records; mean row sales are nearly identical across tiers (~140.87–141.17).
- Fruits and Vegetables (**178,124**) and Snack Foods (**175,434**) lead item type sales.
- Item visibility has essentially no linear association with row sales in this file (Pearson r ≈ **−0.001**). This does not rule out nonlinear or confounded relationships.
- Exact duplicate rows: **0**. Item Weight is missing on **1,463 rows (17.2%)**.

Recommendations are framed as hypotheses for follow-up: prioritize replenishment checks for leading categories, compare outlets on normalized measures and operational context, and improve source data before evaluating trends, margin, or causal effects.

## Project structure

```text
├── app.py                        # Interactive Streamlit dashboard
├── docs/                         # Public static dashboard for GitHub Pages
├── .github/workflows/pages.yml   # GitHub Pages deployment
├── .streamlit/config.toml        # Dashboard theme
├── data/                         # Provided source workbook
├── notebooks/                    # Guided, reproducible analysis
├── src/                          # Reusable loading and cleaning functions
├── requirements.txt
└── README.md
```

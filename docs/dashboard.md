# Dashboard

Read-only Databricks SQL (or notebook) views over Gold and ops tables. No pipeline writes.

## What it shows

**Sales (from `workspace.gold`)**

| Tile | Query file | Table |
|------|------------|--------|
| Total orders, quantity, sales, AOV | `sql/dashboard/01_kpi_totals.sql` | `gold.sales_performance` |
| Sales trend | `sql/dashboard/02_sales_trend.sql` | `gold.kpi_daily` |
| Top customers | `sql/dashboard/03_top_customers.sql` | `gold.customer_performance` |
| Top products | `sql/dashboard/04_top_products.sql` | `gold.product_performance` |
| Category performance | `sql/dashboard/05_category_performance.sql` | rollup of `gold.product_performance` |

Sales KPIs already exclude `cancelled` orders in Gold. The dashboard does not recalculate revenue.

**Data quality (from `workspace.ops`)**

| Tile | Query file | Table |
|------|------------|--------|
| Failed rules | `sql/dashboard/06_dq_failed_rules.sql` | `ops.dq_results` |
| Quarantine counts | `sql/dashboard/07_quarantine_counts.sql` | `ops.quarantine_*` |
| Quarantine sample | `sql/dashboard/08_quarantine_sample.sql` | `ops.quarantine_*` |

Expected quality counts for the seeded generator: 18 `dq_results` rows; quarantine 4 / 5 / 9 for customers / products / orders.

## Option A — notebook (fastest)

1. Open `notebooks/04_dashboard.py` on a cluster that can read `workspace.gold` and `workspace.ops`.
2. Run all.
3. On each result cell, use the chart picker: counters for KPIs, line for trend, bar for top lists and categories, table for quarantine sample.

## Option B — Databricks SQL dashboard

1. Open **SQL Editor** against a warehouse that can query catalog `workspace`.
2. Create one saved query per file in `sql/dashboard/`. Paste the SQL as-is.
3. Create a new dashboard (Lakeview / AI/BI or SQL dashboard).
4. Add visualisations:

   - `01_kpi_totals` — four counters (`total_sales`, `total_orders`, `average_order_value`, `total_quantity`)
   - `02_sales_trend` — line, X = `order_date`, Y = `total_sales`
   - `03_top_customers` — bar, X = `customer_id` or name, Y = `total_sales`
   - `04_top_products` — bar, X = `product_name`, Y = `total_sales`
   - `05_category_performance` — bar, X = `category`, Y = `total_sales`
   - `06_dq_failed_rules` — bar or table (`rule_id`, `failed_count`)
   - `07_quarantine_counts` — bar (`entity`, `quarantined_records`)
   - `08_quarantine_sample` — table

5. Keep the layout to two bands: **Sales** on top, **Data quality** below.

Do not point dashboard queries at Bronze, Silver, or the Volume CSVs for sales numbers.

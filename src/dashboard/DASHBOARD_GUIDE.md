# Dashboard guide

Read-only views. Sales from `workspace.gold`. Quality from `workspace.ops`. No job writes data here.

Implementation: `src/dashboard/dashboard_queries.sql` and `notebooks/04_dashboard.py`. Pipeline run order: `docs/runbook.md`.

## What it shows

**Sales (from `workspace.gold`)**

| Tile | Query | Table |
|------|--------|--------|
| Total orders, quantity, sales, AOV | first SELECT in `dashboard_queries.sql` | `gold.sales_performance` |
| Sales trend | daily SELECT | `gold.kpi_daily` |
| Top customers | LIMIT 10 | `gold.customer_performance` |
| Top products | LIMIT 10 | `gold.product_performance` |
| Category performance | rollup | `gold.product_performance` |

Sales KPIs already exclude `cancelled` orders in Gold. The dashboard does not recalculate revenue.

**Data quality (from `workspace.ops`)**

| Tile | Query | Table |
|------|--------|--------|
| Failed rules | grouped `rule_id` | `ops.dq_results` |
| Quarantine counts | union of counts | `ops.quarantine_*` |
| Quarantine sample | union of rows | `ops.quarantine_*` |

Expected quality counts for the seeded generator: 18 `dq_results` rows; quarantine 4 / 5 / 9 for customers / products / orders.

## Option A — notebook (fastest)

1. Open `notebooks/04_dashboard.py` on a cluster that can read `workspace.gold` and `workspace.ops`.
2. Run all.
3. On each result cell, use the chart picker: counters for KPIs, line for trend, bar for top lists and categories, table for quarantine sample.

## Option B — Databricks SQL dashboard

1. Open **SQL Editor** against a warehouse that can query catalog `workspace`.
2. Create one saved query per SELECT block in `src/dashboard/dashboard_queries.sql`.
3. Create a new dashboard (Lakeview / AI/BI or SQL dashboard).
4. Add visualisations:

   - KPI totals — four counters (`total_sales`, `total_orders`, `average_order_value`, `total_quantity`)
   - Sales trend — line, X = `order_date`, Y = `total_sales`
   - Top customers — bar, X = `customer_id` or name, Y = `total_sales`
   - Top products — bar, X = `product_name`, Y = `total_sales`
   - Category performance — bar, X = `category`, Y = `total_sales`
   - Failed rules — bar or table (`rule_id`, `failed_count`)
   - Quarantine counts — bar (`entity`, `quarantined_records`)
   - Quarantine sample — table

5. Keep the layout to two bands: **Sales** on top, **Data quality** below.

Do not point dashboard queries at Bronze, Silver, or the Volume CSVs for sales numbers.

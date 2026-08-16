# Design Notes

## Architecture Overview

```text
Python generator → data/*.csv
        → upload unchanged
        → /Volumes/workspace/ai-poc/ai-data/{customers,products,orders}.csv
                → Bronze (PySpark)  workspace.bronze.*
                → Silver (PySpark)  workspace.silver.*
                                    workspace.ops.quarantine_*
                                    workspace.ops.dq_results
                → Gold (PySpark)    workspace.gold.*
                → Dashboard SQL     src/dashboard/ + notebooks/04_dashboard.py
```

Each layer may only read the previous durable output. `defect_log.csv` is uploaded next to the entity files but is **not** ingested into Bronze.

| Layer | Reads | Writes | Payload change? |
|-------|-------|--------|-----------------|
| Bronze | Volume CSVs | `bronze.customers/products/orders` | No. Strings + ingest columns |
| Silver | Bronze Delta | `silver.*`, `ops.quarantine_*`, `ops.dq_results` | Yes. Type and split good/bad |
| Gold | Silver Delta | `gold.*` | Yes. Business grain and KPIs |
| Dashboard | Gold + ops | Nothing | No. SELECT only |

Catalog: `workspace`. Shared config: `src/common/settings.py`.

## Data Model & Schema

Three tables. Full column notes: `data-model.md`. Documentary DDL: `database/schema.sql`.

**customers** — grain: one row per customer. PK `customer_id`. Columns: `first_name`, `last_name`, `email`, `signup_date`, `country`, `city`.

**products** — grain: one row per product. PK `product_id`. Columns: `product_name`, `category` (Electronics / Home / Fashion / Sports / Books), `unit_price`, `in_stock`.

**orders** — grain: one row per order, **one product per order**. PK `order_id`. FKs: `customer_id`, `product_id`. Columns: `order_date`, `quantity`, `unit_price`, `order_status`, `payment_method`.

Revenue: `quantity * unit_price`. Allowed statuses: pending, paid, shipped, delivered, cancelled.

## Bronze Layer Design

- Entry: `src/bronze/ingest_all.py` (wrappers: `01_ingest_customers.py`, `02_ingest_orders.py`, `03_ingest_products.py`).
- Read CSVs with `header=true`, `inferSchema=false` so dirty types land.
- Add `_ingest_file`, `_ingest_ts`, `_run_id`.
- Overwrite Delta tables. Do not drop rows. Do not read `defect_log.csv`.
- Notebook: `notebooks/01_bronze_ingest.py`. Expected counts: 10,000 / 500 / 100,000.

## Silver Layer Design

- Entry: `src/silver/create_silver_tables.py`.
- Read Bronze only. Cast clean rows to logical types.
- Apply named flags in `01_quality_completeness.py` … `05_quality_business_logic.py`.
- Any failed flag → entire original Bronze row to quarantine. Both duplicate PK rows fail.
- Write customers and products first; then flag orders’ FKs against **clean Silver**.
- `ops.dq_results`: one row per failed rule.
- Conservation assert: Bronze = Silver + quarantine. Expected: 9996+4 / 495+5 / 99991+9; `dq_results` = 18.
- Notebook: `notebooks/02_silver_transform.py`.

## Gold Layer Design

- Entry: `src/gold/create_gold_tables.py` (PySpark write path).
- Read Silver only.
- Tables: `dim_customer`, `dim_product`, `fact_orders` (`order_sales = quantity * unit_price`), `sales_performance`, `customer_performance`, `product_performance`, `kpi_daily`.
- KPI tables exclude `order_status = 'cancelled'`. `fact_orders` keeps cancelled rows; its count must equal Silver orders.
- Read-only SQL (not a second write path):
  - `01_sales_by_product.sql` → `gold.product_performance`
  - `02_revenue_by_customer.sql` → `gold.customer_performance`
  - `03_daily_weekly_trends.sql` → `gold.kpi_daily` plus a weekly rollup
  - `04_customer_segmentation.sql` — **not implemented as a table**; SELECT over `customer_performance` plus an honest note
- Notebook: `notebooks/03_gold_build.py`.

## Data Quality Validation Strategy

Quality lives in Silver. Five check families (completeness, uniqueness, type, referential, business) map to 15 `rule_id`s. Failures are quarantined, not deleted. Metrics are exact counts against the seeded generator, not a loose “>99%” gate. Details: `data-quality-strategy.md`.

## Debugging Approach

1. Read the failing job output (generator validation, Silver `ValueError`, Gold count mismatch).
2. Compare to `data/defect_log.csv` and the layer that owns the rule.
3. Change only that layer. Do not “fix” Gold by reading Bronze.

Issues that shaped the code: Volume vs FileStore, empty PK vs null, both-dup-rows, Silver dimension order before order FKs, notebook `repo_root`. Full write-up: `debugging-notes.md`. Code review of AI output: `code-review-notes.md`.

# Design Notes

## Architecture Overview

- Generator writes local CSVs → upload unchanged to `/Volumes/workspace/ai-poc/ai-data/`
- Bronze reads those CSVs into `workspace.bronze` (strings + ingest metadata)
- Silver reads Bronze only → clean `workspace.silver` + quarantine / `ops.dq_results`
- Gold reads Silver only → `workspace.gold` dims, fact, and performance tables
- Dashboard runs SELECT only against Gold and ops

`defect_log.csv` is a reference file. It is not a Bronze table.

## Data Model & Schema

- **customers:** one row per customer. PK `customer_id`. Columns: `first_name`, `last_name`, `email`, `signup_date`, `country`, `city`
- **products:** one row per product. PK `product_id`. Columns: `product_name`, `category`, `unit_price`, `in_stock`. Allowed categories: Electronics, Home, Fashion, Sports, Books
- **orders:** one row per order, one product per order. PK `order_id`. FKs: `customer_id`, `product_id`. Columns: `order_date`, `quantity`, `unit_price`, `order_status`, `payment_method`

Revenue on a clean order: `quantity * unit_price`. Full types: `data-model.md`. DDL: `database/schema.sql`.

## Bronze Layer Design

- Read Volume CSVs with `inferSchema=false`
- Add `_ingest_file`, `_ingest_ts`, `_run_id`
- Overwrite `workspace.bronze.customers|products|orders`
- Do not clean, cast, or drop rows
- Code: `src/bronze/ingest_all.py`; notebook: `notebooks/01_bronze_ingest.py`

## Silver Layer Design

- Read Bronze only; cast valid rows to logical types
- Apply 15 named rules; any failure sends the whole Bronze row to quarantine
- Duplicate PKs: both rows quarantined
- Process customers and products first; order FKs join clean Silver
- `ops.dq_results`: one row per failed rule
- Code: `src/silver/create_silver_tables.py` + `01`–`05` quality modules; notebook: `notebooks/02_silver_transform.py`

## Gold Layer Design

- Read Silver only
- Write `dim_customer`, `dim_product`, `fact_orders`, `sales_performance`, `customer_performance`, `product_performance`, `kpi_daily`
- `order_sales = quantity * unit_price`; KPI tables exclude `cancelled`
- SQL views: `src/gold/01_sales_by_product.sql`, `02_revenue_by_customer.sql`, `03_daily_weekly_trends.sql`
- Code: `src/gold/create_gold_tables.py`; notebook: `notebooks/03_gold_build.py`

## Data Quality Validation Strategy

Silver owns quality. Completeness, uniqueness, type, referential, and business checks map to 15 `rule_id`s. Failures are quarantined, not deleted. The job asserts Bronze = Silver + quarantine (9996+4 / 495+5 / 99991+9) and 18 `dq_results` rows. Details: `data-quality-strategy.md`.

## Debugging Approach

- Read the failing job output, then compare to `data/defect_log.csv`
- Fix only the layer that owns the rule
- Do not repair Gold by reading Bronze

Main issues: Volume path vs FileStore, empty PK vs duplicate window, FK against Silver not Bronze. Details: `debugging-notes.md`.

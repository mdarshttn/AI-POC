# Setup notes

How to land the CSVs and run the Databricks jobs. Detailed run order: `docs/runbook.md`.

## Workspace objects

| Setting | Value |
|---------|--------|
| Catalog | `workspace` |
| Raw files | `/Volumes/workspace/ai-poc/ai-data/` |
| Schemas | `bronze`, `silver`, `ops`, `gold` |

Configured in `src/common/settings.py`. Notebooks take the same values as widgets.

## One-time setup

1. Generate CSVs locally: `python src/data_generation/generate_sample_data.py`
2. Upload `customers.csv`, `products.csv`, `orders.csv`, and `defect_log.csv` to the Volume path above. Do not edit the files after generation.
3. Clone or pull this repo where the Databricks cluster can import `src/` (Git folder, or set the `repo_root` widget).
4. Use a Unity Catalog cluster. Use a SQL warehouse only if you build the dashboard in Databricks SQL.

## Job order

1. `notebooks/01_bronze_ingest.py` — expect 10000 / 500 / 100000
2. `notebooks/02_silver_transform.py` — expect Silver 9996 / 495 / 99991 and quarantine 4 / 5 / 9; `dq_results` = 18
3. `notebooks/03_gold_build.py` — `gold.fact_orders` count must match `silver.orders`
4. `notebooks/04_dashboard.py` or `src/dashboard/dashboard_queries.sql`

Each layer overwrites its own tables. Re-run does not append.

`database/schema.sql` documents the logical DDL. The jobs create Delta tables with `saveAsTable`; you do not need to run the SQL file first.

## Import path

Notebooks add `src/` to `sys.path` and import:

- `bronze.ingest_all.run_bronze_ingest`
- `silver.create_silver_tables.run_silver_transform`
- `gold.create_gold_tables.run_gold_build`

If import fails, set the `repo_root` widget to the cloned repo directory (the folder that contains `src/`).

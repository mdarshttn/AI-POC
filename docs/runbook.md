# Runbook

How to generate data, run the medallion jobs, and open the dashboard.

## Completed layers

| Stage | How to run | Output |
|-------|------------|--------|
| 1 Foundation | In git | `cursor-workflow/`, folder skeleton |
| 2 Generator | `python src/data_generation/generate_sample_data.py` | `data/*.csv` |
| 3 Bronze | `notebooks/01_bronze_ingest.py` | `workspace.bronze.customers\|products\|orders` |
| 4 Silver | `notebooks/02_silver_transform.py` | `workspace.silver.*`, `workspace.ops.quarantine_*`, `ops.dq_results` |
| 6 Gold | `notebooks/03_gold_build.py` | `workspace.gold.*` |
| 7 Dashboard | `notebooks/04_dashboard.py` or `src/dashboard/` | Read-only views |

Stage 5 (pytest) is not part of this POC slice.

## Raw files

Local CSVs: `data/`  
Volume (unchanged source): `/Volumes/workspace/ai-poc/ai-data/`  
Entities: `customers.csv`, `products.csv`, `orders.csv`  
`defect_log.csv` is not ingested into Bronze.

## Databricks run order

Use a Unity Catalog cluster (and a SQL warehouse if you use Option B for the dashboard).

1. Upload the four generated CSVs to `/Volumes/workspace/ai-poc/ai-data/` if they are not already there.
2. Run `notebooks/01_bronze_ingest.py`. Expect 10000 / 500 / 100000 rows.
3. Run `notebooks/02_silver_transform.py`. Expect Silver 9996 / 495 / 99991 and quarantine 4 / 5 / 9; `dq_results` = 18.
4. Run `notebooks/03_gold_build.py`. `gold.fact_orders` count must match `silver.orders`.
5. Open the dashboard (`src/dashboard/DASHBOARD_GUIDE.md`).

Re-runs overwrite the layer they belong to; they do not append.

## Catalog objects

- `workspace.bronze.*` — raw strings plus ingest metadata
- `workspace.silver.*` — typed clean rows
- `workspace.ops.quarantine_*` and `workspace.ops.dq_results` — quality
- `workspace.gold.*` — business marts used by the dashboard

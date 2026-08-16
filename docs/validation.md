# Validation

What we actually ran and what numbers we trust. Nothing here is a made-up KPI.

## Generator (local)

Command: `python src/data_generation/generate_sample_data.py`  
Seed `42`. Output under `data/`.

| File | Data rows |
|------|-----------|
| `customers.csv` | 10,000 |
| `products.csv` | 500 |
| `orders.csv` | 100,000 |
| `defect_log.csv` | 18 |

The script checks those counts, that the defect log has 18 rows, and that good orders only reference good customer/product IDs. That run completed with “Validation passed.”

`defect_log.csv` is the expected Silver failure list (null PKs, dups, bad email/category/price/qty/status/date, orphan FKs).

## Bronze

Notebook: `notebooks/01_bronze_ingest.py`  
Reads `/Volumes/workspace/ai-poc/ai-data/{customers,products,orders}.csv`. Does not read `defect_log.csv`.

In-job check: row counts vs `EXPECTED_BRONZE_COUNTS` (10000 / 500 / 100000).

Developer confirmation in this project: Bronze was run on Databricks and accepted before Silver started. Re-run uses overwrite, so counts should stay at those three numbers, including the bad rows.

Useful SQL (not a stored pytest):

```sql
SELECT COUNT(*) FROM workspace.bronze.customers;  -- 10000
SELECT COUNT(*) FROM workspace.bronze.products;   -- 500
SELECT COUNT(*) FROM workspace.bronze.orders;     -- 100000
SHOW TABLES IN workspace.bronze;                  -- no defect_log
```

## Silver

Notebook: `notebooks/02_silver_transform.py`

The transform **raises** if conservation or expected splits fail:

| Entity | Bronze | Silver | Quarantine |
|--------|--------|--------|------------|
| customers | 10,000 | 9,996 | 4 |
| products | 500 | 495 | 5 |
| orders | 100,000 | 99,991 | 9 |

`ops.dq_results` must have **18** rows (one per seeded defect record). Duplicate PK rules contribute two rows each.

Developer confirmation: Silver was run on Databricks and accepted before Gold.

## Gold

Notebook: `notebooks/03_gold_build.py`

In-job checks:

- `gold.fact_orders` count = `silver.orders` count (99,991)
- `gold.sales_performance` has exactly 1 row

Cancelled orders remain in `fact_orders` but are excluded from `sales_performance`, `customer_performance`, `product_performance`, and `kpi_daily`.

`notebooks/Validation.ipynb` (added on Databricks) compares Silver vs Gold counts for customers, products, and orders, and lists Gold table row counts. Cell outputs are not saved in the file, so treat it as the query set we used, not as exported result screenshots.

## Dashboard

`notebooks/04_dashboard.py` and `src/dashboard/dashboard_queries.sql` only SELECT from `workspace.gold` and `workspace.ops`. There is no extra metric engine. If Gold and ops counts above are correct, the tiles are reading those same tables.

## What we did not validate in code

- Exact dollar totals for `total_sales` / AOV (they depend on the random good rows; we did not freeze a gold KPI snapshot in git)
- pytest
- A Databricks SQL dashboard object ID (the queries exist; the warehouse UI dashboard is assembled from `src/dashboard/DASHBOARD_GUIDE.md`)

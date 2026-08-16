# Requirement Analysis

## Problem Statement

An e-commerce team needs a small, demonstrable analytics pipeline on Databricks. Operational CSVs for customers, products, and orders must be landed as-is, cleaned with named data-quality rules, turned into sales marts, and shown on a dashboard.

The data is synthetic so we can plant known bad rows and prove Silver catches them. This is an assessment POC, not a production platform. The useful constraint is medallion discipline: Bronze does not clean, Silver does not read CSVs, Gold does not read Bronze, and the dashboard does not recalculate revenue from raw files.

## Functional Requirements

- Generate reproducible sample CSVs: ~10,000 customers, 500 products, 100,000 orders, plus a defect log.
- Include intentional quality issues that map to named `rule_id`s.
- Land the three entity CSVs unchanged on a Unity Catalog Volume.
- Bronze: ingest CSVs as strings into Delta (`workspace.bronze`), add ingest metadata, skip `defect_log.csv`.
- Silver: type columns, apply completeness / uniqueness / type / referential / business checks, write clean rows to `workspace.silver` and failures to `workspace.ops` quarantine + `dq_results`.
- Gold: build reporting tables from Silver only — sales by product, revenue by customer, daily (and weekly) trends, plus overall KPIs. Exclude cancelled orders from KPI tables.
- Dashboard: read-only SQL over Gold (sales) and ops (quality). Visualisation wiring is a follow-up; query files already exist.
- Jobs must be rerunnable (Delta overwrite, not append).

## Non-Functional Requirements

- Stack limited to Python, PySpark, SQL, and Databricks. No Great Expectations, dbt, Asset Bundles, Airflow, or streaming.
- Batch only.
- Reproducible generator: `SEED = 42`, `AS_OF_DATE = 2026-08-16`.
- No extra Python packages for the Spark jobs beyond the Databricks runtime.
- Local tests use the standard library (`unittest`) so they run without installing Spark.
- Catalog `workspace`; schemas `bronze`, `silver`, `ops`, `gold`.
- Raw path is a Volume (`/Volumes/workspace/ai-poc/ai-data/`), not DBFS FileStore.

## Assumptions

- Three entities only. Each order references one customer and one product (no `order_items`).
- Revenue on a clean order is `quantity * unit_price`. Average order value is that grain, not basket AOV.
- Cancelled orders stay in Silver and `gold.fact_orders` but are excluded from Gold KPI tables.
- Duplicate primary keys: quarantine **both** rows so the uniqueness demo is visible.
- Order FK checks use **clean Silver** parents, not Bronze.
- Spec notes without a `rule_id` (payment_method, in_stock, names, signup_date) are not unofficial extra rules.
- Assessment “~700 quality issues” is a generic example. This repo uses **18 named, fully traceable defects** so every quarantine row matches `defect_log.csv`.

## Edge Cases

- Empty PK in CSV becomes null after Spark ingest; treat null and blank as missing (`*_PK_NULL`).
- A null PK must not also count as a duplicate (`*_PK_DUP` ignores blank keys).
- Unparseable `order_date` and dates after `AS_OF_DATE` share `ORD_DATE_INVALID`.
- Orphan order FKs (`CUST-MISSING`, `PROD-MISSING`) fail only after Silver dimensions are written.
- Re-running a layer must not double row counts (overwrite).
- Gold `fact_orders` count must equal Silver orders; if Silver was skipped after a Bronze overwrite, Gold should fail.

## Clarifications Needed

Resolved during the build (not left open):

- FileStore vs Volume — files were uploaded to `/Volumes/workspace/ai-poc/ai-data/`.
- Keep-a-winner vs quarantine both duplicate PK rows — both rows are quarantined.
- Fourth entity `order_items` — not used.

Still open for the assessor:

- Whether customer segmentation (High-Value / Repeat / One-Time / Inactive) is scored. It is **not** implemented as a Gold table.
- Whether a Databricks SQL dashboard object (warehouse UI) is required, or SQL + notebook cells are enough. Queries exist; UI assembly is the remaining dashboard step.
- Whether 18 named defects are accepted in place of a large random dirty-data dump.

# Requirement Analysis

## Problem Statement

Build a batch e-commerce analytics pipeline on Databricks. Synthetic CSVs for customers, products, and orders are landed raw, cleaned with named data-quality rules, aggregated into sales marts, and queried on a dashboard.

The dataset includes planted bad rows so Silver can be shown to catch them. Each layer may only read the previous layer: Bronze does not clean, Silver does not read CSVs, Gold does not read Bronze, and the dashboard does not recalculate revenue from raw files.

## Functional Requirements

- Generate ~10,000 customers, 500 products, 100,000 orders, plus a defect log
- Plant intentional quality issues mapped to named `rule_id`s
- Land entity CSVs unchanged on a Unity Catalog Volume
- Bronze: ingest as strings into Delta, add ingest metadata, skip `defect_log.csv`
- Silver: type columns, run completeness / uniqueness / type / referential / business checks, write clean rows and quarantine failures
- Gold: sales by product, revenue by customer, daily/weekly trends, overall KPIs; exclude cancelled orders from KPI tables
- Dashboard: read-only SQL on Gold (sales) and ops (quality)
- Jobs must be rerunnable (overwrite, not append)

## Non-Functional Requirements

- Stack: Python, PySpark, SQL, Databricks only
- Batch processing
- Reproducible generator (`SEED = 42`, `AS_OF_DATE = 2026-08-16`)
- Catalog `workspace`; schemas `bronze`, `silver`, `ops`, `gold`
- Raw path configurable in `src/common/settings.py`

## Assumptions

- Three entities only; each order has one customer and one product
- Revenue = `quantity * unit_price`
- Cancelled orders stay in Silver and `fact_orders` but are excluded from KPI tables
- Duplicate PKs: quarantine both rows
- Order FKs are checked against clean Silver parents
- Planted defects are 18 named rows (not a large random dirty dump)

## Edge Cases

- Empty PK in CSV may ingest as null; treat blank and null as missing
- Blank PKs must not also count as duplicates
- Unparseable `order_date` and dates after `AS_OF_DATE` share `ORD_DATE_INVALID`
- Re-run must not double counts
- Gold `fact_orders` count must equal Silver orders

## Clarifications Needed

Resolved during the build:

- Raw landing is a Unity Catalog Volume, not DBFS FileStore
- Duplicate PK handling is quarantine both rows (not keep a winner)
- No `order_items` table

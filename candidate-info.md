# Candidate Information

**Name:** Md Arsh  
**Role:** SE  
**Primary Technology Stack:** Python / PySpark, SQL, Databricks  
**Primary AI Tool Used:** Cursor  
**Project Option Selected:** Data Pipeline (Medallion Architecture)  
**Assessment Start Date:** 14 Aug 2026  
**Submission Date:** 16 Aug 2026

## Tools & Environment

- Databricks: Unity Catalog workspace (`workspace`), raw files on Volume `/Volumes/workspace/ai-poc/ai-data/`
- Languages: Python, PySpark, SQL
- Libraries: PySpark, Delta Lake
- AI Tool: Cursor

## Setup Summary

1. Generate CSVs: `python src/data_generation/generate_sample_data.py`
2. Local tests: `python -m unittest discover -s tests -v`
3. Upload `data/customers.csv`, `products.csv`, `orders.csv`, `defect_log.csv` to `/Volumes/workspace/ai-poc/ai-data/`
4. Run on a Unity Catalog cluster: `notebooks/01_bronze_ingest.py` → `02_silver_transform.py` → `03_gold_build.py`
5. Dashboard SQL: `notebooks/04_dashboard.py` or `src/dashboard/dashboard_queries.sql`

Expected counts: Bronze 10000 / 500 / 100000. Silver 9996+4 / 495+5 / 99991+9. `dq_results` = 18.

Full instructions: `README.md`.

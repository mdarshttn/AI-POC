# AI Prompts — Bronze Layer

## Prompt 1: Landing zone, then ingest

**PROMPT SENT:**
Design how CSVs get to Databricks (configurable path, not hardcoded in every notebook). After upload to `/Volumes/workspace/ai-poc/ai-data/`, implement Bronze only: read CSVs as strings, add `_ingest_file` / `_ingest_ts` / `_run_id`, Delta overwrite, skip `defect_log.csv`. Thin notebook. Do not clean or cast payload columns.

**AI RESPONSE SUMMARY:**
Settings module with `RAW_DATA_PREFIX`, ingest module, `notebooks/01_bronze_ingest.py` with a `repo_root` widget and `sys.path` into `src/`.

**YOUR EVALUATION:**

- **Accepted:** Volume prefix in settings; overwrite; schema-on-read strings; three entity tables only.
- **Changed:** Later split into `src/bronze/ingest_all.py` plus `01_ingest_customers.py`, `02_ingest_orders.py`, `03_ingest_products.py` for the submission folder tree. Same `ingest_entity` behavior.
- **Rejected:** Hardcoding FileStore (`/FileStore/ecommerce_poc/raw/`) after files were actually uploaded to a Volume. Rejected ingesting `defect_log.csv`.

**Validation:** Ran Bronze on Databricks. Counts 10,000 / 500 / 100,000 before starting Silver.

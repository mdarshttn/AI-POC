# AI Prompts — Bronze Layer

## Prompt 1: Landing zone design (no Spark code)

**PROMPT SENT:**
the generator is working and the local csv files are ready. now i want to move to the databricks side, but before writing the bronze code lets first decide how the local generated files will be moved into dbfs and how the bronze job will read them.

the generated files are customers.csv, products.csv, orders.csv and defect_log.csv. the raw csv files should be treated as the source data and should not be modified before bronze.

please design a simple approach for this POC where the files are uploaded to a known DBFS raw location and the bronze layer reads from there using pyspark.

i want the dbfs path to be configurable instead of hardcoding the same path in multiple notebooks or scripts.

also explain how i can manually upload the generated csv files from my windows machine to databricks for the first run, and how we could later automate that step if needed.

for now dont create the bronze ingestion code or any pyspark code. just give me the recommended folder/path structure in dbfs and explain the local-to-dbfs flow and what the next bronze step will consume

**AI RESPONSE SUMMARY:**
Configurable raw prefix in settings. Manual upload for the first run. `defect_log.csv` stored next to entity files but not ingested as a Bronze table. Early notes still used a FileStore-style path.

**YOUR EVALUATION:**

✓ **What was good:** One configurable prefix; raw files unchanged; defect log not a business table  
✗ **What needed fixing:** Actual upload was a Unity Catalog Volume, not FileStore  
△ **Missing:** Ingest code (intentionally)

**Accepted** configurable path. **Changed** later to `/Volumes/workspace/ai-poc/ai-data/` once files were uploaded.

---

## Prompt 2: Implement Bronze ingest

**PROMPT SENT:**
okay the csv files are now uploaded to databricks at /Volumes/workspace/ai-poc/ai-data/ so lets move to the bronze layer.

please implement only the bronze ingestion for customers, products and orders based on the design we agreed earlier. dont work on silver, gold, dq, dashboard or testing yet.

the bronze layer should read the raw csv files from /Volumes/workspace/ai-poc/ai-data/. keep all source columns as strings because bronze is only the raw landing layer and we dont want to clean or cast anything here.

add the ingestion metadata we discussed: _ingest_file, _ingest_ts and _run_id. the run_id should identify one bronze ingestion run so we can trace the records back to the source files.

write the results as Delta tables under the bronze schema: bronze.customers, bronze.products and bronze.orders.

the raw files must not be modified and defect_log.csv should not be loaded as a bronze business table. it will be used later as the expected defect reference for testing.

keep the pyspark logic in src/pipeline/bronze and create only a thin databricks notebook or entry point to execute it. use the existing project structure and dont introduce any new frameworks.

make the ingestion safe to rerun. if the same run is executed again it should not keep duplicating the same records.

after implementing it, tell me exactly which files you created and how i should run the bronze ingestion in databricks. also tell me what checks i should perform to confirm that bronze.customers has 10000 rows, bronze.products has 500 rows and bronze.orders has 100000 rows, including the intentionally bad records.

dont modify the generator and dont start silver yet

**AI RESPONSE SUMMARY:**
Settings + ingest module + `notebooks/01_bronze_ingest.py`. String columns, ingest metadata, Delta overwrite. Skip `defect_log.csv`.

**YOUR EVALUATION:**

✓ **ACCEPTED** — ran on Databricks; 10000 / 500 / 100000 including bad rows  
✗ **Changed later** — files moved to `src/bronze/ingest_all.py` and `01`/`02`/`03` wrappers for submission layout  
△ **Rejected** — cleansing, casting, ingesting the defect log

**FINAL DECISION:** `src/bronze/ingest_all.py` + `notebooks/01_bronze_ingest.py`

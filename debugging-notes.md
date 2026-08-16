# Debugging notes

There was no long stack-trace firefight in this build. Most issues were design mismatches caught **before** code, or path/count issues caught when a job refused to finish.

## How we debugged

1. Read the failing job output (generator `Validation failed`, Silver `ValueError`, Gold count mismatch).
2. Compare to `data/defect_log.csv` and the layer that should own the rule.
3. Change only that layer. Do not “fix” Gold by reading Bronze.

Cursor was used to explain likely causes (empty PK becoming null after CSV ingest, window functions treating null PKs as one duplicate group, FK joining Bronze instead of Silver). The developer still ran the notebook and accepted or rejected the fix.

## Issues that actually shaped the code

**Raw path is a Volume, not FileStore.**  
Early notes said `/FileStore/ecommerce_poc/raw/`. Files were uploaded to `/Volumes/workspace/ai-poc/ai-data/`. Bronze `RAW_DATA_PREFIX` was pointed at the Volume. If you still see file-not-found, the cluster cannot see that Volume or the CSV names differ.

**Empty PK vs null.**  
The generator writes an empty `customer_id`. Spark CSV often stores that as null. Silver treats null and blank as missing (`CUST_PK_NULL`). Duplicate detection **ignores** blank PKs so one null PK is not also `CUST_PK_DUP`.

**Duplicate PK “keep a winner”.**  
Keeping one Silver row would make `CUST_PK_DUP` disappear from the demo. Both rows are quarantined.

**Order of Silver.**  
If orders ran before customers/products, `ORD_FK_*` would have nothing clean to join. Customers and products are written first; orders read those Silver tables.

**Gold following Silver.**  
If `fact_orders` count ≠ `silver.orders`, Gold raises. That usually means Silver was not rerun after a Bronze overwrite, or Gold is pointed at the wrong schema.

**Notebook cannot import `bronze` / `silver` / `gold`.**  
The runner looks for `src/bronze/ingest_all.py` (and the Silver/Gold counterparts) from cwd or the `repo_root` widget. If the Git folder is not the repo root, set `repo_root`.

## What we did not see

No production incident log, no cluster OOM, no recorded Databricks error dump in git. If a run fails now, paste the error into `docs/validation.md` notes after you fix it — do not invent a stack trace here.

# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Bronze ingest
# MAGIC
# MAGIC Lands `customers`, `products`, and `orders` CSVs from the UC Volume as Delta tables.
# MAGIC Does not read `defect_log.csv`. Does not clean or cast source columns.

# COMMAND ----------

dbutils.widgets.text("raw_prefix", "/Volumes/workspace/ai-poc/ai-data")
dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("bronze_schema", "bronze")
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("repo_root", "")

# COMMAND ----------

import sys
from pathlib import Path

widget_root = dbutils.widgets.get("repo_root").strip()
candidates = []
if widget_root:
    candidates.append(Path(widget_root))
candidates.extend([Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent])

repo_root = None
for candidate in candidates:
    if (candidate / "src" / "pipeline" / "bronze" / "ingest.py").exists():
        repo_root = candidate
        break

if repo_root is None:
    raise FileNotFoundError(
        "Could not find src/pipeline/bronze/ingest.py. "
        "Set the repo_root widget to the cloned repo path."
    )

sys.path.insert(0, str(repo_root / "src"))

from pipeline.bronze.ingest import run_bronze_ingest

# COMMAND ----------

results = run_bronze_ingest(
    spark,
    raw_prefix=dbutils.widgets.get("raw_prefix").strip(),
    catalog=dbutils.widgets.get("catalog").strip() or None,
    bronze_schema=dbutils.widgets.get("bronze_schema").strip(),
    run_id=dbutils.widgets.get("run_id").strip() or None,
)

display(spark.createDataFrame(results))

# COMMAND ----------

catalog = dbutils.widgets.get("catalog").strip() or None
schema = dbutils.widgets.get("bronze_schema").strip()
if catalog:
    spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

print("customers", spark.table("customers").count())
print("products", spark.table("products").count())
print("orders", spark.table("orders").count())

# COMMAND ----------


# Databricks notebook source
# MAGIC %md
# MAGIC # Silver transform
# MAGIC
# MAGIC Reads `workspace.bronze` tables only. Writes typed Silver, quarantine, and `ops.dq_results`.
# MAGIC Does not read Volume CSVs or `defect_log.csv`.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("bronze_schema", "bronze")
dbutils.widgets.text("silver_schema", "silver")
dbutils.widgets.text("ops_schema", "ops")
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
    if (candidate / "src" / "pipeline" / "silver" / "transform.py").exists():
        repo_root = candidate
        break

if repo_root is None:
    raise FileNotFoundError(
        "Could not find src/pipeline/silver/transform.py. "
        "Set the repo_root widget to the cloned repo path."
    )

sys.path.insert(0, str(repo_root / "src"))

from pipeline.silver.transform import run_silver_transform

# COMMAND ----------

results = run_silver_transform(
    spark,
    catalog=dbutils.widgets.get("catalog").strip() or None,
    bronze_schema=dbutils.widgets.get("bronze_schema").strip(),
    silver_schema=dbutils.widgets.get("silver_schema").strip(),
    ops_schema=dbutils.widgets.get("ops_schema").strip(),
    run_id=dbutils.widgets.get("run_id").strip() or None,
)

display(spark.createDataFrame(results))

# COMMAND ----------

catalog = dbutils.widgets.get("catalog").strip() or None
if catalog:
    spark.sql(f"USE CATALOG `{catalog}`")

print("silver.customers", spark.table("silver.customers").count())
print("silver.products", spark.table("silver.products").count())
print("silver.orders", spark.table("silver.orders").count())
print("ops.quarantine_customers", spark.table("ops.quarantine_customers").count())
print("ops.quarantine_products", spark.table("ops.quarantine_products").count())
print("ops.quarantine_orders", spark.table("ops.quarantine_orders").count())
print("ops.dq_results", spark.table("ops.dq_results").count())

# COMMAND ----------

display(
    spark.table("ops.dq_results")
    .groupBy("table_name", "rule_id")
    .count()
    .orderBy("table_name", "rule_id")
)

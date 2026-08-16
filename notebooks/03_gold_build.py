# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Gold build
# MAGIC
# MAGIC Reads clean `workspace.silver` tables only. Writes business marts under `workspace.gold`.
# MAGIC Does not read Bronze, CSVs, or quarantine tables.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("silver_schema", "silver")
dbutils.widgets.text("gold_schema", "gold")
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
    if (candidate / "src" / "pipeline" / "gold" / "build.py").exists():
        repo_root = candidate
        break

if repo_root is None:
    raise FileNotFoundError(
        "Could not find src/pipeline/gold/build.py. "
        "Set the repo_root widget to the cloned repo path."
    )

sys.path.insert(0, str(repo_root / "src"))

from pipeline.gold.build import run_gold_build

# COMMAND ----------

results = run_gold_build(
    spark,
    catalog=dbutils.widgets.get("catalog").strip() or None,
    silver_schema=dbutils.widgets.get("silver_schema").strip(),
    gold_schema=dbutils.widgets.get("gold_schema").strip(),
    run_id=dbutils.widgets.get("run_id").strip() or None,
)

display(spark.createDataFrame(results))

# COMMAND ----------

catalog = dbutils.widgets.get("catalog").strip() or None
if catalog:
    spark.sql(f"USE CATALOG `{catalog}`")

display(spark.table("gold.sales_performance"))

# COMMAND ----------

display(spark.sql("SELECT * FROM gold.product_performance ORDER BY total_sales DESC LIMIT 10"))
display(spark.sql("SELECT * FROM gold.customer_performance ORDER BY total_sales DESC LIMIT 10"))

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     order_status,
# MAGIC     COUNT(*) AS orders,
# MAGIC     SUM(quantity * unit_price) AS sales
# MAGIC FROM workspace.gold.fact_orders
# MAGIC GROUP BY order_status
# MAGIC ORDER BY order_status;

# COMMAND ----------


# Databricks notebook source
# MAGIC %md
# MAGIC # E-commerce POC dashboard
# MAGIC
# MAGIC Read-only views over `workspace.gold` and `workspace.ops`.
# MAGIC No pipeline writes. Visualise cells as counters, line, or bar in the notebook UI,
# MAGIC or paste the matching SELECTs from `src/dashboard/dashboard_queries.sql` into a Databricks SQL dashboard.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sales KPIs
# MAGIC Total orders, quantity, sales, and average order value (cancelled orders excluded in Gold).

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   total_orders,
# MAGIC   total_quantity,
# MAGIC   total_sales,
# MAGIC   average_order_value
# MAGIC FROM workspace.gold.sales_performance

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sales trend

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   order_date,
# MAGIC   total_orders,
# MAGIC   total_quantity,
# MAGIC   total_sales,
# MAGIC   average_order_value
# MAGIC FROM workspace.gold.kpi_daily
# MAGIC ORDER BY order_date

# COMMAND ----------

# MAGIC %md
# MAGIC ## Top customers

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   customer_id,
# MAGIC   first_name,
# MAGIC   last_name,
# MAGIC   country,
# MAGIC   total_orders,
# MAGIC   total_quantity,
# MAGIC   total_sales,
# MAGIC   average_order_value
# MAGIC FROM workspace.gold.customer_performance
# MAGIC ORDER BY total_sales DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Top products

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   product_id,
# MAGIC   product_name,
# MAGIC   category,
# MAGIC   total_orders,
# MAGIC   total_quantity,
# MAGIC   total_sales,
# MAGIC   average_order_value
# MAGIC FROM workspace.gold.product_performance
# MAGIC ORDER BY total_sales DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Category performance

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   category,
# MAGIC   SUM(total_orders) AS total_orders,
# MAGIC   SUM(total_quantity) AS total_quantity,
# MAGIC   SUM(total_sales) AS total_sales,
# MAGIC   ROUND(SUM(total_sales) / SUM(total_orders), 2) AS average_order_value
# MAGIC FROM workspace.gold.product_performance
# MAGIC GROUP BY category
# MAGIC ORDER BY total_sales DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data quality — failed rules

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   table_name,
# MAGIC   rule_id,
# MAGIC   COUNT(*) AS failed_count
# MAGIC FROM workspace.ops.dq_results
# MAGIC GROUP BY table_name, rule_id
# MAGIC ORDER BY table_name, rule_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data quality — quarantined records

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'customers' AS entity, COUNT(*) AS quarantined_records
# MAGIC FROM workspace.ops.quarantine_customers
# MAGIC UNION ALL
# MAGIC SELECT 'products' AS entity, COUNT(*) AS quarantined_records
# MAGIC FROM workspace.ops.quarantine_products
# MAGIC UNION ALL
# MAGIC SELECT 'orders' AS entity, COUNT(*) AS quarantined_records
# MAGIC FROM workspace.ops.quarantine_orders
# MAGIC ORDER BY entity

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   'customers' AS entity,
# MAGIC   _rule_id,
# MAGIC   _failed_column,
# MAGIC   _failed_value,
# MAGIC   _row_fingerprint
# MAGIC FROM workspace.ops.quarantine_customers
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC   'products' AS entity,
# MAGIC   _rule_id,
# MAGIC   _failed_column,
# MAGIC   _failed_value,
# MAGIC   _row_fingerprint
# MAGIC FROM workspace.ops.quarantine_products
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC   'orders' AS entity,
# MAGIC   _rule_id,
# MAGIC   _failed_column,
# MAGIC   _failed_value,
# MAGIC   _row_fingerprint
# MAGIC FROM workspace.ops.quarantine_orders
# MAGIC ORDER BY entity, _rule_id

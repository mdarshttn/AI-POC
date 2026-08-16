-- E-commerce POC dashboard queries
-- Sales tiles read workspace.gold. Quality tiles read workspace.ops.
-- SELECT only. Cancelled orders are already excluded from Gold KPI tables.
-- Visualise in notebooks/04_dashboard.py or paste into Databricks SQL.

-- =============================================================================
-- Sales: KPI counters
-- Visualisation: four counters
-- =============================================================================

SELECT
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.sales_performance;

-- =============================================================================
-- Sales: daily trend
-- Visualisation: line chart, X = order_date, Y = total_sales
-- =============================================================================

SELECT
  order_date,
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.kpi_daily
ORDER BY order_date;

-- =============================================================================
-- Sales: top customers
-- Visualisation: bar chart or table
-- =============================================================================

SELECT
  customer_id,
  first_name,
  last_name,
  country,
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.customer_performance
ORDER BY total_sales DESC
LIMIT 10;

-- =============================================================================
-- Sales: top products
-- Visualisation: bar chart or table
-- =============================================================================

SELECT
  product_id,
  product_name,
  category,
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.product_performance
ORDER BY total_sales DESC
LIMIT 10;

-- =============================================================================
-- Sales: category performance
-- Visualisation: bar chart, X = category, Y = total_sales
-- =============================================================================

SELECT
  category,
  SUM(total_orders) AS total_orders,
  SUM(total_quantity) AS total_quantity,
  SUM(total_sales) AS total_sales,
  ROUND(SUM(total_sales) / SUM(total_orders), 2) AS average_order_value
FROM workspace.gold.product_performance
GROUP BY category
ORDER BY total_sales DESC;

-- =============================================================================
-- Data quality: failed rules
-- Visualisation: bar chart or table, X = rule_id, Y = failed_count
-- =============================================================================

SELECT
  table_name,
  rule_id,
  COUNT(*) AS failed_count
FROM workspace.ops.dq_results
GROUP BY table_name, rule_id
ORDER BY table_name, rule_id;

-- =============================================================================
-- Data quality: quarantine counts
-- Visualisation: bar chart or table
-- =============================================================================

SELECT 'customers' AS entity, COUNT(*) AS quarantined_records
FROM workspace.ops.quarantine_customers
UNION ALL
SELECT 'products' AS entity, COUNT(*) AS quarantined_records
FROM workspace.ops.quarantine_products
UNION ALL
SELECT 'orders' AS entity, COUNT(*) AS quarantined_records
FROM workspace.ops.quarantine_orders
ORDER BY entity;

-- =============================================================================
-- Data quality: quarantine sample
-- Visualisation: table
-- =============================================================================

SELECT
  'customers' AS entity,
  _rule_id,
  _failed_column,
  _failed_value,
  _row_fingerprint
FROM workspace.ops.quarantine_customers
UNION ALL
SELECT
  'products' AS entity,
  _rule_id,
  _failed_column,
  _failed_value,
  _row_fingerprint
FROM workspace.ops.quarantine_products
UNION ALL
SELECT
  'orders' AS entity,
  _rule_id,
  _failed_column,
  _failed_value,
  _row_fingerprint
FROM workspace.ops.quarantine_orders
ORDER BY entity, _rule_id;

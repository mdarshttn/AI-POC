-- Customer segmentation (High-Value / Repeat / One-Time / Inactive) was not
-- implemented as a Gold table in this POC. There is no gold.customer_segmentation
-- write in create_gold_tables.py.
--
-- Closest shipped mart: workspace.gold.customer_performance
-- (customers with at least one non-cancelled order). Inactive customers with
-- zero included orders are not in this table.

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
ORDER BY total_sales DESC;

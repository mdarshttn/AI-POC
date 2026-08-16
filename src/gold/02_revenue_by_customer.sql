-- Revenue by customer from the Gold mart (cancelled orders already excluded).
-- Source: workspace.gold.customer_performance
-- Built by src/gold/create_gold_tables.py — this file is SELECT only.

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

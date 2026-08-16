-- Sales by product from the Gold mart (cancelled orders already excluded).
-- Source: workspace.gold.product_performance
-- Built by src/gold/create_gold_tables.py — this file is SELECT only.

SELECT
  product_id,
  product_name,
  category,
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.product_performance
ORDER BY total_sales DESC;

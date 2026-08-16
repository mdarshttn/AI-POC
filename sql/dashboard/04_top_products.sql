-- Top products by sales
-- Source: workspace.gold.product_performance
-- Visualisation: bar chart or table

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

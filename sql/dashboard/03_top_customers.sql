-- Top customers by sales
-- Source: workspace.gold.customer_performance
-- Visualisation: bar chart or table

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

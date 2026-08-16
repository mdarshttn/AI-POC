-- Category performance rolled up from gold.product_performance
-- Visualisation: bar chart, X = category, Y = total_sales

SELECT
  category,
  SUM(total_orders) AS total_orders,
  SUM(total_quantity) AS total_quantity,
  SUM(total_sales) AS total_sales,
  ROUND(SUM(total_sales) / SUM(total_orders), 2) AS average_order_value
FROM workspace.gold.product_performance
GROUP BY category
ORDER BY total_sales DESC;

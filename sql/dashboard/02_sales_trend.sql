-- Sales trend by day
-- Source: workspace.gold.kpi_daily
-- Visualisation: line chart, X = order_date, Y = total_sales

SELECT
  order_date,
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.kpi_daily
ORDER BY order_date;

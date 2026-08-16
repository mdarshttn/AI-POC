-- KPI counters: total orders, quantity, sales, AOV
-- Source: workspace.gold.sales_performance (cancelled orders already excluded)
-- Visualisation: four counter tiles, one per column

SELECT
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.sales_performance;

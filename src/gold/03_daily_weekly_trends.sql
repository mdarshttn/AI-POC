-- Daily trend from Gold, plus a weekly rollup of the same metrics.
-- Source: workspace.gold.kpi_daily (cancelled orders already excluded).
-- Built by src/gold/create_gold_tables.py — this file is SELECT only.

SELECT
  order_date,
  total_orders,
  total_quantity,
  total_sales,
  average_order_value
FROM workspace.gold.kpi_daily
ORDER BY order_date;

-- Weekly rollup (ISO week of order_date)

SELECT
  date_trunc('WEEK', order_date) AS week_start,
  SUM(total_orders) AS total_orders,
  SUM(total_quantity) AS total_quantity,
  ROUND(SUM(total_sales), 2) AS total_sales,
  ROUND(SUM(total_sales) / SUM(total_orders), 2) AS average_order_value
FROM workspace.gold.kpi_daily
GROUP BY date_trunc('WEEK', order_date)
ORDER BY week_start;

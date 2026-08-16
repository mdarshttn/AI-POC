-- Quarantined record counts by entity
-- Source: workspace.ops.quarantine_* tables
-- Visualisation: bar chart or table

SELECT 'customers' AS entity, COUNT(*) AS quarantined_records
FROM workspace.ops.quarantine_customers
UNION ALL
SELECT 'products' AS entity, COUNT(*) AS quarantined_records
FROM workspace.ops.quarantine_products
UNION ALL
SELECT 'orders' AS entity, COUNT(*) AS quarantined_records
FROM workspace.ops.quarantine_orders
ORDER BY entity;

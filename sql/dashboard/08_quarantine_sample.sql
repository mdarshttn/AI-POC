-- Sample quarantined rows so reviewers can see the original Bronze values
-- Visualisation: table

SELECT
  'customers' AS entity,
  _rule_id,
  _failed_column,
  _failed_value,
  _row_fingerprint
FROM workspace.ops.quarantine_customers
UNION ALL
SELECT
  'products' AS entity,
  _rule_id,
  _failed_column,
  _failed_value,
  _row_fingerprint
FROM workspace.ops.quarantine_products
UNION ALL
SELECT
  'orders' AS entity,
  _rule_id,
  _failed_column,
  _failed_value,
  _row_fingerprint
FROM workspace.ops.quarantine_orders
ORDER BY entity, _rule_id;

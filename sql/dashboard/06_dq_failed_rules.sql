-- Failed DQ rules
-- Source: workspace.ops.dq_results
-- Visualisation: bar chart or table, X = rule_id, Y = failed_count

SELECT
  table_name,
  rule_id,
  COUNT(*) AS failed_count
FROM workspace.ops.dq_results
GROUP BY table_name, rule_id
ORDER BY table_name, rule_id;

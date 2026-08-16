# Code review notes

Review of AI-generated code before it was accepted. This is not a third-party PR review with line comments in GitHub.

## What I checked on every Spark job

- Reads only the allowed layer (Bronze: Volume CSVs; Silver: Bronze; Gold: Silver; dashboard: Gold + ops)
- Write mode is overwrite, not append
- No new pip packages
- No hardcoded secrets
- Named `rule_id`s only — no extra unofficial checks
- Notebooks stay thin (`sys.path` + one function call)

## Findings that changed the code

| Finding | Decision |
|---------|----------|
| Early layout used FileStore | Point ingest at `/Volumes/workspace/ai-poc/ai-data/` |
| “Keep a winner” on duplicate PK | Quarantine both rows |
| Null PK also flagged as duplicate | Uniqueness ignores blank PKs |
| Order FKs against Bronze | FK after Silver dimensions exist |
| Gold as unrun SQL files | PySpark writer plus SELECT SQL on top |
| Assessment example ~700 random issues | Keep 18 named defects + `defect_log.csv` |
| Faker / extra customer columns | Rejected; stick to spec columns |

## What passed review as-is

- String ingest in Bronze (`inferSchema=false`)
- Quarantine keeping original Bronze strings
- `dq_results` grain: one row per failed rule
- Gold `order_sales = quantity * unit_price` and cancelled excluded from KPI tables
- Conservation asserts in Silver; fact-count assert in Gold

## Residual risk

- Local unittests do not execute PySpark. A regression in a Spark expression is caught on the next Databricks run, not in `python -m unittest`.
- Dashboard SQL is reviewed as SELECT-only; the warehouse UI dashboard is not in git.

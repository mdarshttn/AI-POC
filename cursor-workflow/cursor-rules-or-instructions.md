# Cursor rules / instructions

How to change this repository. Read `project-context.md`, `spec.md`, and `task-breakdown.md` before generating code.

## Source of truth

1. The user’s current message
2. This `cursor-workflow/` folder
3. Existing code and folder layout

If chat history suggested extra tools, extra entities, or generating several stages at once, ignore that and follow this folder plus the current user request.

## Build incrementally

- Implement **only** the stage the user asked for.
- Do not add a generator, PySpark jobs, SQL marts, notebooks, or tests until that stage is requested.
- Each stage should be reviewable on its own: clear output, no leftover stubs for later stages.
- After a stage, update `task-breakdown.md` status (and `project-context.md` if a decision changed).

## Stack discipline

Allowed: Python, PySpark, SQL, Databricks, CSV in DBFS, pytest (when tests are in scope).

Do **not** add: Great Expectations, Soda, dbt, Databricks Asset Bundles, Terraform, Airflow, Kafka, streaming, extra BI tools, or new Python packages unless the user asks and the need is justified.

Do **not** add a fourth entity (`order_items` or similar). Orders already carry `customer_id` and `product_id`.

## Folder conventions

| Path | What belongs there |
|------|--------------------|
| `src/data_generation/` | Plain Python. No Spark imports. |
| `src/bronze/` | PySpark ingest from Volume CSVs |
| `src/silver/` | PySpark typing, rules, quarantine |
| `src/gold/` | PySpark business marts from Silver |
| `src/common/` | Shared path helpers, Delta writes |
| `src/dashboard/` | Databricks SQL queries for tiles |
| `notebooks/` | Thin wrappers that call `src` / run SQL files |
| `tests/` | pytest only; fixtures stay small |
| `docs/` | Extra human docs; do not fork a second spec |
| `cursor-workflow/` | Context for people and Cursor |

Keep notebooks thin. Business and quality logic belongs in `src` or `sql` so it can be tested.

## Data movement rules

- Bronze reads entity CSVs from `RAW_DATA_PREFIX` only. Do not ingest `defect_log.csv`.
- Silver reads Bronze only.
- Gold reads Silver only.
- Quality tiles may read `ops` quarantine / `dq_results`.
- Do not compute dashboard KPIs from raw CSVs or Bronze.

Raw volume prefix: `/Volumes/workspace/ai-poc/ai-data/` (override only via `src/common/settings.py` or notebook widgets).

## Quality and tests

- Quality rules are PySpark/SQL with a `rule_id` from `spec.md`.
- Write failures to quarantine and summary rows to `ops.dq_results`.
- Local tests: `python -m unittest discover -s tests -v`. Do not require a live dashboard to prove generator contracts.
- Never commit secrets, workspace tokens, or extra generated dumps under `data/sample/generated/`.

## Code style

- Follow existing naming and layout once code exists.
- Prefer small functions over one giant notebook cell.
- Pin new dependencies only when necessary; this POC should need little beyond Python and PySpark.
- No `eval`, hardcoded credentials, or disabled TLS.

## What “done” means for a stage

Match the exit check in `task-breakdown.md`. If the user asked for foundation only, stop after skeleton + these context files.

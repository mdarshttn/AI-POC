# Databricks medallion pipeline (e-commerce POC)

Batch data-engineering POC for a small e-commerce dataset. Raw files are CSVs in DBFS. The pipeline follows Bronze, Silver, and Gold. A Databricks SQL dashboard presents business results and data-quality outcomes.

This repository is in the **foundation** stage. There is no generator, pipeline, SQL, notebook, or test code yet.

## Stack

- Python — synthetic CSV generation (not started)
- PySpark on Databricks — Bronze and Silver (not started)
- SQL — Gold business layer (not started)
- Databricks SQL — dashboard (not started)
- CSV files in DBFS — raw landing zone

Do not add extra frameworks (Great Expectations, Databricks Asset Bundles, dbt, Airflow, and similar).

## Entities

- `customers`
- `products`
- `orders` (each order references one customer and one product)

## Source of truth for this chat

Work from the files in `cursor-workflow/`:

| File | Purpose |
|------|---------|
| `cursor-workflow/project-context.md` | What we know, decisions, and constraints |
| `cursor-workflow/spec.md` | Entities, layers, DBFS, quality, dashboard, tests |
| `cursor-workflow/cursor-rules-or-instructions.md` | How to implement the next increment |
| `cursor-workflow/task-breakdown.md` | Ordered stages and current status |

## Intended layout (empty until a later stage)

```text
src/generator/           Python CSV generator
src/pipeline/common/     Shared PySpark helpers
src/pipeline/bronze/     Bronze ingest
src/pipeline/silver/     Silver cleanse and quality checks
sql/gold/                Gold mart SQL
sql/dashboard/           Databricks SQL tile queries
notebooks/               Thin Databricks entrypoints
tests/                   pytest (unit, integration, fixtures)
docs/                    Human-readable notes beyond cursor-workflow
data/sample/             Tiny example CSVs (later)
```

## How we will build this

Incrementally. Finish and validate one stage before starting the next. See `cursor-workflow/task-breakdown.md`.

# Databricks medallion pipeline (e-commerce POC)

Batch e-commerce pipeline on Databricks: Python generator → Unity Catalog Volume CSVs → Bronze → Silver (with quarantine) → Gold → dashboard.

Generator, Bronze, Silver, and Gold are implemented and validated. This repo now includes dashboard SQL and docs. There is no pytest suite yet.

## Stack

- Python — synthetic CSVs with seeded defects (`src/generator/`)
- PySpark on Databricks — Bronze, Silver, Gold (`src/pipeline/`)
- SQL — dashboard tiles (`sql/dashboard/`)
- Databricks SQL / notebook — dashboard
- Raw CSVs — `/Volumes/workspace/ai-poc/ai-data/`

Do not add extra frameworks (Great Expectations, Databricks Asset Bundles, dbt, Airflow, and similar).

## Entities

- `customers`
- `products`
- `orders` (one customer and one product per order)

## Pipeline

```text
python src/generator/generate.py
        → Volume CSVs (unchanged)
            → notebooks/01_bronze_ingest.py    workspace.bronze.*
            → notebooks/02_silver_transform.py workspace.silver.* + ops.*
            → notebooks/03_gold_build.py       workspace.gold.*
            → notebooks/04_dashboard.py
              or sql/dashboard/                sales + quality tiles
```

| Layer | Tables |
|-------|--------|
| Bronze | `workspace.bronze.customers`, `products`, `orders` |
| Silver | `workspace.silver.customers`, `products`, `orders` |
| Ops | `quarantine_customers\|products\|orders`, `dq_results` |
| Gold | `dim_customer`, `dim_product`, `fact_orders`, `sales_performance`, `customer_performance`, `product_performance`, `kpi_daily` |

Expected counts (seeded generator): Bronze 10000 / 500 / 100000; Silver 9996 / 495 / 99991; quarantine 4 / 5 / 9; `dq_results` 18.

## How to run

See [docs/runbook.md](docs/runbook.md). Dashboard setup: [docs/dashboard.md](docs/dashboard.md).

## Source of truth

| File | Purpose |
|------|---------|
| `cursor-workflow/project-context.md` | Decisions and constraints |
| `cursor-workflow/spec.md` | Entities, layers, quality rules, dashboard |
| `cursor-workflow/cursor-rules-or-instructions.md` | How to change the repo |
| `cursor-workflow/task-breakdown.md` | Stages and status |

## Layout

```text
src/generator/           Python CSV generator
src/pipeline/common/     Shared paths and Delta writes
src/pipeline/bronze/     Bronze ingest
src/pipeline/silver/     Silver cleanse and quality checks
src/pipeline/gold/       Gold business marts
sql/dashboard/           Databricks SQL tile queries
notebooks/               Thin Databricks entrypoints
docs/                    Runbook and dashboard notes
cursor-workflow/         Spec and working agreement
data/sample/generated/   Local CSVs (gitignored)
tests/                   Reserved (not implemented)
```

# Databricks medallion pipeline (e-commerce POC)

Batch pipeline: synthetic CSVs → Unity Catalog Volume → Bronze → Silver (quarantine + DQ) → Gold → dashboard SQL.

I used Cursor to draft designs and code. I reviewed that output and ran the generator locally and the Spark jobs on Databricks before calling a layer done.

## Setup

### 1. Generate sample data (local Python)

```text
python src/data_generation/generate_sample_data.py
```

Writes `data/customers.csv`, `data/products.csv`, `data/orders.csv`, `data/defect_log.csv` (10,000 / 500 / 100,000 / 18 rows, seed 42).

### 2. Run local tests

```text
python -m unittest discover -s tests -v
```

No extra packages. These tests do not start Spark.

### 3. Upload CSVs to Databricks

Copy the four files unchanged to:

`/Volumes/workspace/ai-poc/ai-data/`

`defect_log.csv` is a reference file. Bronze does not ingest it.

### 4. Run the pipeline (Unity Catalog cluster)

Clone or pull this repo where the cluster can import `src/`. If imports fail, set the notebook widget `repo_root` to the repo directory.

1. `notebooks/01_bronze_ingest.py` — expect 10000 / 500 / 100000
2. `notebooks/02_silver_transform.py` — expect Silver 9996 / 495 / 99991, quarantine 4 / 5 / 9, `dq_results` = 18
3. `notebooks/03_gold_build.py` — `gold.fact_orders` count must match `silver.orders`
4. Optional SQL checks: `notebooks/Validation.ipynb`
5. Dashboard queries: `notebooks/04_dashboard.py` or `src/dashboard/dashboard_queries.sql` (warehouse UI dashboard still to assemble)

Each layer overwrites its own tables. Re-run does not append.

Catalog: `workspace`. Raw prefix and expected counts: `src/common/settings.py`. Documentary DDL: `database/schema.sql`. Longer run order: `docs/runbook.md` and `database/setup-notes.md`.

## What it does

| Layer | Entry | Writes |
|-------|--------|--------|
| Generator | `python src/data_generation/generate_sample_data.py` | `data/*.csv` |
| Bronze | `notebooks/01_bronze_ingest.py` | `workspace.bronze.customers\|products\|orders` |
| Silver | `notebooks/02_silver_transform.py` | `workspace.silver.*`, `workspace.ops.quarantine_*`, `ops.dq_results` |
| Gold | `notebooks/03_gold_build.py` | dims, `fact_orders`, sales/customer/product/daily performance |
| Dashboard | `src/dashboard/dashboard_queries.sql` | Nothing — SELECT only |

Gold KPIs exclude `cancelled`. `fact_orders` keeps cancelled rows.

## Assessment docs

| Doc | Contents |
|-----|----------|
| [candidate-info.md](candidate-info.md) | Name and tools |
| [tool-workflow.md](tool-workflow.md) | How Cursor was used |
| [requirements-analysis.md](requirements-analysis.md) | Problem, functional/non-functional, assumptions |
| [design-notes.md](design-notes.md) | Architecture through debugging |
| [data-model.md](data-model.md) | PKs, FKs, types |
| [data-quality-strategy.md](data-quality-strategy.md) | Completeness, uniqueness, referential, metrics |
| [test-strategy.md](test-strategy.md) | Local tests + in-job asserts |
| [debugging-notes.md](debugging-notes.md) | Real issues |
| [code-review-notes.md](code-review-notes.md) | Review of AI output |
| [reflection.md](reflection.md) | Learning and reusable workflow |
| [final-ai-usage-summary.md](final-ai-usage-summary.md) | Accept / reject |
| [ai-prompts/](ai-prompts/) | Prompts by activity |
| [cursor-workflow/](cursor-workflow/) | Cursor context, spec, rules, tasks |

## Not in this repo

A Gold customer-segmentation **table**, streaming, dbt, Great Expectations, Asset Bundles, `order_items`. Dashboard **SQL is in the repo**; the Databricks SQL warehouse dashboard object is the remaining UI step.

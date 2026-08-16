# Project context

Living snapshot of what we currently know. Update this file when a decision changes. Detailed contracts live in `spec.md`. Ordered work lives in `task-breakdown.md`. Implementation rules live in `cursor-rules-or-instructions.md`.

## Purpose

Build a small, demonstrable data-engineering POC for e-commerce.

The POC must show:

1. Synthetic operational data, including **intentional bad rows**
2. Landing that data as CSVs on a **Unity Catalog Volume** (`/Volumes/workspace/ai-poc/ai-data/`)
3. A **Bronze → Silver → Gold** pipeline on Databricks with PySpark and SQL
4. Data quality checks, automated tests, and validation
5. A **Databricks SQL dashboard** of business results and quality outcomes

This is a teaching / assessment POC, not a production platform. Prefer a complete thin slice over extra tooling.

## Current status

**Stage 7 — Dashboard SQL done; warehouse UI still to assemble.** Local `unittest` contract tests are in `tests/`. Repo layout matches the submission tree.

We will implement and validate one stage at a time in this chat.

## Stack (allowed)

| Layer | Technology | Role |
|-------|------------|------|
| Data generation | Python | Create reproducible CSVs, including seeded defects |
| Raw storage | CSV files on UC Volume `/Volumes/workspace/ai-poc/ai-data/` | Source of truth for ingest |
| Bronze and Silver | PySpark on Databricks | Land, type, clean, quarantine |
| Gold | PySpark | Business marts from Silver |
| Serving | Databricks SQL / notebook | Dashboard |

Delta tables are the expected table format on Databricks. That is native storage, not an extra product.

## Stack (do not add)

Do not introduce frameworks or products beyond the allowed stack unless the user explicitly asks. In particular, do **not** add:

- Great Expectations, Soda, dbt tests, or other DQ platforms
- Databricks Asset Bundles, Terraform, or other deploy frameworks
- dbt, Airflow, Prefect, Kafka, Structured Streaming
- Extra entities such as `order_items`, payments, or events
- BI tools other than Databricks SQL

Local `pytest` (and a local Spark session when we need to test PySpark) is in scope later. It is a test runner, not a pipeline framework.

## Domain

Three core entities only:

- `customers`
- `products`
- `orders`

There is no `order_items` table. Each order row references **one** `customer_id` and **one** `product_id`. That keeps joins and KPIs simple while still allowing foreign-key quality checks.

## Architecture in one paragraph

Python writes CSV files. Those files are uploaded unchanged to `/Volumes/workspace/ai-poc/ai-data/`. A PySpark Bronze step reads the entity CSVs as-is (plus ingest metadata) into Delta. A PySpark Silver step types columns, enforces quality rules, writes clean rows to Silver, and writes failing rows to quarantine with a rule id. PySpark builds Gold marts from Silver only. Databricks SQL charts Gold KPIs and ops quality counts. Local unittests assert generator contracts and file-level Gold SQL; Spark jobs assert live counts.

## Data flow

```text
Python generator
    → CSV files on UC Volume (raw)
        → Bronze Delta (raw + ingest metadata)
            → Silver Delta (typed, clean)
            → Quarantine + quality result rows
                → Gold SQL marts
                    → Databricks SQL dashboard
                      (business tiles + quality tiles)
```

Rules:

- Bronze reads the three entity CSVs from the raw volume only.
- Silver reads Bronze only.
- Gold SQL reads Silver only (quality tiles may also read quarantine / quality result tables).
- The dashboard does not re-implement Gold joins against Bronze or CSVs.

## Role of the raw volume

The Unity Catalog Volume is the **raw landing zone**, not a substitute for tables.

- Raw CSVs live at `/Volumes/workspace/ai-poc/ai-data/` (`RAW_DATA_PREFIX` in `src/common/settings.py`).
- `defect_log.csv` is stored there for later tests and is **not** a Bronze business table.
- Pipeline tables live as Delta in `workspace.bronze` (later `silver`, `gold`, `ops`).
- Generated files may be created locally first, then uploaded unchanged. Local generated dumps are not committed to git.

## Testing approach

- **Unit tests** (`python -m unittest discover -s tests`): generator defect blocks, conservation math, quality module files, Gold SQL aggregations.
- **In-job asserts** on Databricks: Silver conservation and Gold `fact_orders` count.
- **SQL notebook:** `notebooks/Validation.ipynb` after Gold.

Databricks is the runtime for the pipeline demo. Laptop tests do not start Spark.

## Dashboard goal

One Databricks SQL dashboard that a reviewer can open after a pipeline run:

1. **Business:** order volume, revenue (quantity × unit price), average order value, top products, simple customer activity.
2. **Quality:** Bronze vs Silver counts, quarantine rate, counts by rule id — so intentional bad data is visible.

Dashboard queries should be SQL against Gold (and ops quality tables), not Spark notebooks.

## Incremental working agreement

- Implement only the stage the user asked for.
- Each stage has an input, an output, and an exit check (`task-breakdown.md`).
- Do not generate later-stage code “while we are here”.
- Validate the current stage before starting the next.
- When a requirement conflicts with an earlier suggestion in chat (for example extra tools or a fourth entity), **this folder wins**.

## Open points (defaults, change if needed)

| Topic | Current default |
|-------|-----------------|
| Order grain | One product per order |
| Catalog style | `workspace.bronze` (later `silver`, `gold`, `ops`) |
| Ingest style | Batch, not streaming |
| DQ implementation | PySpark + SQL, results written to `ops` tables |
| Job packaging | Notebooks or Python files run in the workspace; no Asset Bundles |

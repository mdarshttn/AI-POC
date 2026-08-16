# Final AI usage summary

Cursor (this chat) was used as a coding assistant. It drafted designs and code. I reviewed the output, ran jobs on Databricks, and only kept what matched the brief and what I could verify.

That is the whole story: **AI suggested, I constrained, I ran, I accepted or rejected.**

## Tooling

- Cursor agent in the `databricks-medallion-pipeline` repo
- Databricks workspace for Bronze / Silver / Gold / dashboard SQL
- Local Python for `src/data_generation/generate_sample_data.py`
- Git to push notebooks and `src/` into the Databricks repo

No Great Expectations, dbt, or Asset Bundles were added, including when the model offered them early on.

## How each stage used AI

| Stage | What I asked AI to do | What I did myself |
|-------|------------------------|-------------------|
| Foundation | Break the POC into stages; write `cursor-workflow/` | Locked three entities, banned extra frameworks |
| Generator | Design then implement CSVs + defect log | Ran the generator, checked 10000/500/100000/18 |
| Bronze | Ingest design then PySpark + thin notebook | Uploaded CSVs to the Volume, ran `01_bronze_ingest`, checked counts |
| Silver | Design DQ, then implement | Confirmed quarantine splits on Databricks before Gold |
| Gold | Business tables from Silver | Ran `03_gold_build`, used `Validation.ipynb` for Silver vs Gold counts |
| Dashboard | SQL tiles + notebook, no new transforms | Pointed tiles at existing Gold/ops tables |
| Docs | Assessment pack + later repo-layout match | Checked docs against code so we do not claim pytest or segmentation |

## What I accepted from AI

- Medallion split with quarantine instead of dropping rows
- Seeded defect log as the expected Silver result
- Overwrite for reruns
- Thin Databricks notebooks that import `src/`
- Named `rule_id`s instead of a DQ product
- Gold KPIs excluding `cancelled`

## What I changed or rejected

- **No `order_items`.** Early architecture had four entities. The brief is three tables.
- **No Asset Bundles / GE / dbt.** Stack is Python, PySpark, SQL, Databricks.
- **Volume path, not FileStore.** That is where the files actually landed.
- **Quarantine both duplicate PK rows**, not “keep latest.”
- **Gold as PySpark** under `src/gold/create_gold_tables.py`, same as Bronze/Silver. SQL files under `src/gold/` are SELECT-only over those tables.
- **No pytest-on-Spark in this slice.** Local `unittest` covers generator and file contracts. Job-level asserts + SQL remain the Databricks gate.
- **No customer segmentation table.** `src/gold/04_customer_segmentation.sql` documents that gap and reads `customer_performance`.

## Prompts

The real Cursor prompts (not the unused 49-item reference pack) are in `ai-prompts/`. The same narrative is in `tool-workflow.md`.

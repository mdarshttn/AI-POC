# Reflection

## What I Built

A batch e-commerce medallion pipeline on Databricks: synthetic CSVs with 18 planted defects, Bronze landing, Silver DQ + quarantine, Gold sales marts, and read-only dashboard SQL. I ran the generator locally and Bronze / Silver / Gold on Databricks before calling each layer done.

## How I Used AI (Across the Lifecycle)

Cursor was used one stage at a time: design first when the contract was unclear, then implementation only for that stage. I cut extra tools and a fourth entity, then ran the output before asking for the next layer. Prompt history is in `ai-prompts/`.

## What AI Helped With Most

- Breaking the POC into stages with inputs and exit checks
- Boilerplate (CSV writer, Spark ingest/overwrite, thin notebooks)
- Named `rule_id`s and deterministic defect injection
- Explaining trade-offs (one product per order, overwrite vs append, quarantine both duplicate rows)

## What AI Got Wrong

- First plan added Asset Bundles, Great Expectations, and `order_items`
- Defaulted to FileStore; files actually landed on a Unity Catalog Volume
- Spec line “keep a PK winner” would have hidden the uniqueness demo
- Would clean in Bronze or compute KPIs from CSVs unless told not to

## How I Validated AI Output

- Checked each job reads the right layer and overwrites rather than appends
- Ran the generator and confirmed 10000 / 500 / 100000 / 18
- Ran Bronze, Silver, and Gold on Databricks; Silver and Gold raise on count mismatch
- Compared docs to `src/` so unimplemented items were not claimed

## What I Would Improve Next

- Wire the existing SQL into a Databricks SQL dashboard in the warehouse UI
- Save Validation notebook outputs or a `dq_results` screenshot
- Add a small local Spark test for Silver flags on a tiny fixture

## Reusable Workflow

Lock stack and entities → prompt one stage (design, then code) → accept or cut scope → run it → record expected counts → only then prompt the next stage.

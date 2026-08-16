# Reflection

## What I Built

A batch e-commerce medallion pipeline on Databricks:

- Python generator with seed 42 and 18 planted defects
- Bronze landing from a Unity Catalog Volume (raw strings)
- Silver typing + 15 named DQ rules, quarantine, `dq_results`
- Gold dims, fact, and sales / customer / product / daily metrics (cancelled excluded from KPIs)
- Read-only dashboard SQL and a display notebook (SQL warehouse dashboard UI still to assemble)
- Local `unittest` contract tests for the generator, seeded issues, and Gold SQL files

I ran the generator locally and Bronze / Silver / Gold on Databricks before calling a layer done.

## How I Used AI (Across the Lifecycle)

Cursor was used stage by stage, not as a one-shot “generate the repo” request.

1. **Requirements / architecture** — break the POC into stages; I cut extra tools and a fourth entity.
2. **Data model** — review PKs, FKs, grain; I kept three tables and the 15 named rules.
3. **Generator** — design, then code; I ran it and checked 10000 / 500 / 100000 / 18.
4. **Bronze / Silver / Gold** — design then implement; I ran each notebook on Databricks and only then asked for the next layer.
5. **Dashboard SQL** — read-only tiles; I did not let it recalculate revenue from Bronze.
6. **Docs and repo layout** — assessment templates and folder match; I rejected claims (pytest-as-if-complete, 700 random defects, FileStore, segmentation table) that the code does not support.

Prompts: `ai-prompts/`. Tool loop: `tool-workflow.md`. Cursor context files: `cursor-workflow/`.

## What AI Helped With Most

- Turning a vague “build a POC” into a stage list with inputs and exit checks
- Boilerplate: CSV writer, Spark read/write, notebook widget / `sys.path` pattern
- Naming `rule_id`s and keeping defect injection deterministic
- Explaining trade-offs (one product per order, overwrite vs append, both-dup-rows)

That saved time. It did not replace running the jobs.

## What AI Got Wrong

- First architecture pass added Asset Bundles, Great Expectations, and `order_items`
- Spec vs demo conflict: “keep a PK winner” would hide `CUST_PK_DUP`
- Defaulted to DBFS FileStore; the workspace used a Volume
- Assessment examples mention ~700 issues, faker, customer segments, and pytest; following those blindly would have produced a different (and dishonest) repo
- Happy to clean in Bronze or compute KPIs from CSVs unless told not to

## How I Validated AI Output

- Read every Spark job for: reads the right layer, overwrite not append, no extra dependencies
- Ran `generate_sample_data.py` locally and confirmed counts
- Ran Bronze, then Silver, then Gold on Databricks; Silver/Gold raise on count mismatch
- Cross-checked docs against `src/` so we do not claim segmentation, FileStore, or 700 defects
- Added local unittests for generator defects, conservation math, and Gold SQL presence

## What I Would Improve Next

1. Assemble the Databricks SQL dashboard in the warehouse UI (queries already exist).
2. Save `Validation.ipynb` outputs or a screenshot of `dq_results` grouped by `rule_id`.
3. Add a local Spark session test for Silver flags on a 20-row fixture, so DQ is not only in-notebook.
4. If the assessor scores segmentation, add it as an explicit Gold table — not as a surprise extra.

## Reusable Workflow

```text
lock stack and entities in cursor-workflow/
    → one stage prompt (design first if the contract is unclear)
    → accept / cut scope
    → implement only that stage
    → run it (local or Databricks)
    → write the expected counts down
    → only then prompt the next stage
```

Keep a short reject list (no extra frameworks, no reading the wrong layer). AI will fill gaps; the workflow is what stops those gaps becoming undeclared scope.

# Task breakdown

Ordered stages for this POC. Do not start a later stage until the current one meets its exit check and the user asks to continue.

## Status

| Stage | Name | Status |
|-------|------|--------|
| 1 | Foundation and context | **Done** |
| 2 | Python CSV generator | **Done** |
| 3 | Bronze ingest (PySpark) | **Done** |
| 4 | Silver + quality (PySpark) | **Done** |
| 5 | Tests and validation | Not started |
| 6 | Gold business layer | **Done** |
| 7 | Databricks SQL dashboard and demo notes | **Done** (this increment) |

Tests are listed as Stage 5 so the harness has a dedicated checkpoint. When Stages 2–4 are built, add tests for that module in the same increment if the user agrees; Stage 5 then tightens the suite and makes it the gate.

---

## Stage 1 — Foundation and context

**Input:** POC requirements (three entities, medallion, DBFS CSVs, Python / PySpark / SQL / Databricks, incremental build, no extra frameworks).

**Output:**

- README and `.gitignore`
- Empty folder skeleton for later code
- `cursor-workflow/` files: context, spec, rules, this breakdown

**Exit check:** A new session can learn the stack, entities, DBFS role, layer rules, testing approach, and dashboard goal without reading chat history. No pipeline, generator, notebook, SQL, or test code exists yet.

**Connects to:** Every later stage uses `spec.md` as the contract.

---

## Stage 2 — Python CSV generator

**Input:** Entity columns, allowed values, and `rule_id`s from `spec.md`.

**Output:** Python under `src/generator/` that writes local CSVs (and can be copied to DBFS). A defect log of injected bad rows. No Spark.

**Exit check:** Same seed → same files. Good rows plus at least one example of each planned defect class. Defect log lists `rule_id`s.

**Connects to:** Stage 3 consumes the CSVs in DBFS. Stage 5 uses the defect log as expected failures.

**Do not do in this stage:** PySpark jobs, Gold SQL, dashboard.

---

## Stage 3 — Bronze ingest (PySpark)

**Input:** CSVs at `/Volumes/workspace/ai-poc/ai-data/`.

**Output:** `workspace.bronze.customers`, `workspace.bronze.products`, `workspace.bronze.orders` with ingest metadata. Code under `src/pipeline/bronze/`; thin notebook `notebooks/01_bronze_ingest.py`.

**Exit check:** Row counts match CSVs. Payload stays raw (string-friendly). Re-run for the same `_run_id` does not duplicate that run. No business cleansing.

**Connects to:** Stage 4 reads Bronze only.

---

## Stage 4 — Silver + data quality (PySpark)

**Input:** Bronze tables + quality rules in `spec.md`.

**Output:** Silver clean tables, `ops` quarantine tables, `ops.dq_results`. Code under `src/pipeline/silver/`.

**Exit check:** Seeded defects land in quarantine with the correct `rule_id`. Clean orders have valid FKs to clean customers and products.

**Connects to:** Stage 6 reads Silver. Stage 7 quality tiles read `ops`.

---

## Stage 5 — Tests and validation

**Input:** Generator, Bronze/Silver functions, spec contracts, tiny fixtures.

**Output:** pytest under `tests/` (unit, a small integration path, fixtures). No new DQ product.

**Exit check:** A local pytest run fails if columns, seeded defects, or Gold grain/KPI formulas break (Gold tests may wait until Stage 6 if SQL does not exist yet).

**Connects to:** Gates Stages 2–6.

---

## Stage 6 — Gold business layer

**Input:** Clean Silver tables + KPI definitions in `spec.md`.

**Output:** PySpark under `src/pipeline/gold/` and thin notebook `notebooks/03_gold_build.py`. Tables: `gold.dim_customer`, `gold.dim_product`, `gold.fact_orders`, `gold.sales_performance`, `gold.customer_performance`, `gold.product_performance`, `gold.kpi_daily`.

**Exit check:** Grain of `fact_orders` is `order_id` and matches Silver order count. Revenue KPIs use `quantity * unit_price` and exclude `cancelled`.

**Connects to:** Stage 7.

---

## Stage 7 — Dashboard and demo notes

**Input:** Gold marts and `ops.dq_results` / quarantine counts.

**Output:** SQL tiles in `sql/dashboard/`, thin notebook `notebooks/04_dashboard.py`, `docs/dashboard.md`, and `docs/runbook.md`.

**Exit check:** A reviewer can follow the notes and see both sales KPIs and quarantine-by-rule without reading PySpark.

**Connects to:** Closes the POC.

---

## Handshake (what each stage hands off)

```text
1 spec/context  →  2 generator, 3–7 all layers
2 CSVs + defect log  →  3 Bronze, 5 tests
3 Bronze Delta  →  4 Silver
4 Silver + ops  →  6 Gold, 7 dashboard quality
5 pytest gate  →  2–6
6 Gold marts  →  7 dashboard business tiles
```

## Next requested increment

POC pipeline and dashboard are complete. Do not start a new pipeline layer. Pytest remains optional if requested later.

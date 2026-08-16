# Test Strategy

## Purpose

Prove the seeded contracts without requiring Great Expectations or a live dashboard. Spark jobs still assert counts when notebooks run on Databricks. Local tests cover what can run on a laptop with the standard library.

## Layers of testing

| Kind | Where | What it proves |
|------|--------|----------------|
| Generator unit | `tests/test_data_generation.py` | Defect blocks, `rule_id`s, good-order FKs, file counts |
| Quality contracts | `tests/test_quality_contracts.py` | 18 issues, conservation math, each check family has a module |
| Pipeline / Gold contracts | `tests/test_pipeline_contracts.py` | Bronze/Silver/Gold entrypoints exist; three Gold aggregations are present in SQL |
| In-job asserts | `create_silver_tables.py`, `create_gold_tables.py` | Live Databricks counts; job fails on drift |
| SQL notebook | `notebooks/Validation.ipynb` | Silver vs Gold table counts after a workspace run |

## How to run locally

```text
python -m unittest discover -s tests -v
```

No extra packages. These tests do **not** start Spark or Databricks.

## What is not automated here

- PySpark DataFrame flag logic on a cluster (that is the Silver notebook)
- A Databricks SQL dashboard object ID
- Frozen dollar totals for `total_sales` (they depend on RNG good rows; we did not snapshot KPI money)

## Mapping to the brief

The brief asked for data-quality tests and pipeline integration tests. Local unittests lock the **contracts** (volumes, 18 defects, Gold SQL files, conservation). Integration of Bronze → Silver → Gold still happens by running notebooks 01 → 02 → 03 on a Unity Catalog cluster, with in-job raises as the gate.

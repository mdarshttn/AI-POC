# Testing

See [test-strategy.md](../test-strategy.md) for the full plan.

## Local

```text
python -m unittest discover -s tests -v
```

Covers generator defects, conservation math, quality module files, and the three Gold aggregation SQL files.

## In-job (Databricks)

| Layer | What fails the run |
|-------|---------------------|
| Generator | Wrong CSV counts, defect log ≠ 18, good order FKs pointing at defect IDs |
| Silver | Bronze ≠ Silver + quarantine; splits ≠ 9996+4 / 495+5 / 99991+9; `dq_results` ≠ 18 |
| Gold | `fact_orders` ≠ Silver orders; `sales_performance` ≠ 1 row |

## SQL notebook

`notebooks/Validation.ipynb` compares Silver vs Gold counts. Cell outputs are not committed.

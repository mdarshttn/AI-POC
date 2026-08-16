# Data generation notes

Standalone Python generator. No Spark or Databricks imports.

## How to run

```text
python src/data_generation/generate_sample_data.py
```

Writes under `data/`:

| File | Data rows |
|------|-----------|
| `customers.csv` | 10,000 |
| `products.csv` | 500 |
| `orders.csv` | 100,000 |
| `defect_log.csv` | 18 |

`defect_log.csv` is the expected-defect list. It is **not** a Bronze table. Upload it next to the three entity CSVs on the Volume so reviewers can compare Silver `ops.dq_results`.

## Reproducibility

- `SEED = 42`
- `AS_OF_DATE = 2026-08-16`
- Good rows are generated first; a **fixed** defect block is appended. Defects are not “randomly corrupt 1% of rows.”

## Volumes including defects

| Entity | Good | Defects | File total |
|--------|------|---------|------------|
| customers | 9,996 | 4 | 10,000 |
| products | 495 | 5 | 500 |
| orders | 99,991 | 9 | 100,000 |

Good orders only reference good customer and product IDs. Reserved duplicate IDs (`CUST-DUP-01`, `PROD-DUP-01`, `ORD-DUP-01`) are not used in the good population.

## Seeded defects (matches Silver `rule_id`s)

**customers:** empty PK, two rows with `CUST-DUP-01`, invalid email `not-an-email`.  
**products:** empty PK, two rows with `PROD-DUP-01`, category `Food`, `unit_price = -10`.  
**orders:** empty PK, two rows with `ORD-DUP-01`, quantity 0, negative price, status `SHIPPPED`, missing customer FK, missing product FK, `order_date` in 2099.

The generator checks file counts, that the defect log has 18 rows, and that good order FKs stay inside the good ID sets. It exits if those checks fail.

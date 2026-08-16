# Seed data notes

Synthetic e-commerce CSVs from `src/data_generation/generate_sample_data.py`.

## Files

Local copies live under `data/`. Upload the same files unchanged to:

`/Volumes/workspace/ai-poc/ai-data/`

| File | Ingested to Bronze? | Rows |
|------|---------------------|------|
| `customers.csv` | Yes | 10,000 |
| `products.csv` | Yes | 500 |
| `orders.csv` | Yes | 100,000 |
| `defect_log.csv` | No | 18 |

## Seed

`SEED = 42`, `AS_OF_DATE = 2026-08-16`. Re-running the generator overwrites `data/*.csv` with the same counts.

## What the defects are for

Silver is supposed to quarantine the 18 planted failures (both duplicate PK rows count). `defect_log.csv` is the expected list, not a pipeline input.

Good orders only reference good customer and product IDs. Orphan FKs are only in the defect block (`CUST-MISSING`, `PROD-MISSING`).

## Grain

One order row = one customer + one product. There is no `order_items` file.

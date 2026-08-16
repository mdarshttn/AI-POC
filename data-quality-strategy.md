# Data Quality Strategy

Quality runs in **Silver only**. Bronze lands dirty strings. Gold reads clean Silver. Dashboard SQL reports `ops.dq_results` and quarantine; it does not re-check rules.

This POC does **not** use a “>99% complete” pass/fail gate. Every named failure is quarantined, and the job **raises** if conservation or expected counts drift. That is stricter than a percentage threshold for a seeded dataset.

## Quality Checks Overview

### 1. Completeness Check

- **What:** Critical primary keys are present (`customer_id`, `product_id`, `order_id`). Email blank/null is covered with the email format rule (`CUST_EMAIL_INVALID`).
- **How:** `src/silver/01_quality_completeness.py` flags null or trimmed-empty PKs. Spark CSV often stores an empty CSV field as null; both are treated as missing.
- **Threshold:** 100% of Silver rows have a PK. Bronze may contain the seeded blanks. After quarantine: customers 9,996 / 10,000 (99.96% of Bronze rows remain), products 99.0%, orders 99.991%.
- **Result:** Flag the row (`CUST_PK_NULL`, `PROD_PK_NULL`, `ORD_PK_NULL`), send it to quarantine, write a `dq_results` row.

### 2. Uniqueness Check

- **What:** Primary keys are unique. This is uniqueness of `customer_id` / `product_id` / `order_id`, not “entire row identical.”
- **How:** `src/silver/02_quality_uniqueness.py` uses a window count partitioned by PK. Blank PKs are **not** grouped as duplicates (that would double-count `*_PK_NULL`).
- **Threshold:** 100% unique in Silver. Both duplicate rows are quarantined (no surviving winner), so `CUST-DUP-01`, `PROD-DUP-01`, and `ORD-DUP-01` are absent from Silver.
- **Result:** Flag `_r_*_PK_DUP` on every row that shares a non-blank PK.

### 3. Referential Integrity

- **What:** Order foreign keys exist in parent tables.
- **How:** `src/silver/04_quality_referential_integrity.py` left-joins orders to **clean Silver** `customers` and `products` (written first). Not Bronze, not the Volume CSVs.
- **Threshold:** 100% of Silver orders have valid FKs. Two seeded orphans (`CUST-MISSING`, `PROD-MISSING`) are quarantined (`ORD_FK_CUSTOMER`, `ORD_FK_PRODUCT`).
- **Result:** Flag orphan records; they do not enter `silver.orders`.

### 4. Type / format validation

- **What:** Email looks like an address; category is in the allowed list; `order_date` parses as `yyyy-MM-dd HH:mm:ss` and is not after `AS_OF_DATE`.
- **How:** `src/silver/03_quality_type_validation.py`.
- **Result:** `CUST_EMAIL_INVALID`, `PROD_CATEGORY_INVALID`, `ORD_DATE_INVALID`.

### 5. Business logic

- **What:** Product and order prices `>= 0`; order quantity `> 0`; order status in the allowed list.
- **How:** `src/silver/05_quality_business_logic.py`.
- **Result:** `PROD_PRICE_NEGATIVE`, `ORD_QTY_INVALID`, `ORD_PRICE_NEGATIVE`, `ORD_STATUS_INVALID`.

## Quality Metrics Report

Present results as **counts and conservation**, which is what the Silver job prints and asserts:

| Entity | Bronze | Silver (passed) | Quarantine (failed) | Pass rate |
|--------|--------|-----------------|---------------------|-----------|
| customers | 10,000 | 9,996 | 4 | 99.96% |
| products | 500 | 495 | 5 | 99.00% |
| orders | 100,000 | 99,991 | 9 | 99.991% |

`ops.dq_results` must have **18** rows (one per seeded defect record; each duplicate PK contributes two rows).

How to show this to a reviewer:

```sql
SELECT table_name, rule_id, COUNT(*) AS failed_count
FROM workspace.ops.dq_results
GROUP BY table_name, rule_id
ORDER BY table_name, rule_id;

SELECT 'customers' AS entity, COUNT(*) AS quarantined_records FROM workspace.ops.quarantine_customers
UNION ALL
SELECT 'products', COUNT(*) FROM workspace.ops.quarantine_products
UNION ALL
SELECT 'orders', COUNT(*) FROM workspace.ops.quarantine_orders;
```

Local contract tests (`python -m unittest discover -s tests`) check the same expected numbers and the seeded `rule_id`s without a cluster.

## Sample Data Quality Issues

The generic assessment example mentions ~700 random issues. **This repo does not do that.** Random dirty data is hard to score and easy to miss. We planted **18 deterministic defects** (good rows + a fixed defect block, seed 42). Every issue has a `rule_id` in `data/defect_log.csv`.

| table | rule_id | record_id | bad_value | notes |
|-------|---------|-----------|-----------|--------|
| customers | CUST_PK_NULL | (empty) | empty PK | 1 row |
| customers | CUST_PK_DUP | CUST-DUP-01 | CUST-DUP-01 | 2 rows |
| customers | CUST_EMAIL_INVALID | CUST-BAD-EML | not-an-email | 1 row |
| products | PROD_PK_NULL | (empty) | empty PK | 1 row |
| products | PROD_PK_DUP | PROD-DUP-01 | PROD-DUP-01 | 2 rows |
| products | PROD_CATEGORY_INVALID | PROD-BAD-CAT | Food | 1 row |
| products | PROD_PRICE_NEGATIVE | PROD-NEG-PRC | -10.00 | 1 row |
| orders | ORD_PK_NULL | (empty) | empty PK | 1 row |
| orders | ORD_PK_DUP | ORD-DUP-01 | ORD-DUP-01 | 2 rows |
| orders | ORD_QTY_INVALID | ORD-BAD-QTY | 0 | 1 row |
| orders | ORD_PRICE_NEGATIVE | ORD-BAD-PRC | -5.00 | 1 row |
| orders | ORD_STATUS_INVALID | ORD-BAD-STS | SHIPPPED | 1 row |
| orders | ORD_FK_CUSTOMER | ORD-BAD-FCU | CUST-MISSING | 1 row |
| orders | ORD_FK_PRODUCT | ORD-BAD-FPR | PROD-MISSING | 1 row |
| orders | ORD_DATE_INVALID | ORD-BAD-DAT | 2099-12-31 23:59:59 | 1 row |

Total: **18** `defect_log` rows = **18** expected `dq_results` rows. Good orders only reference good customer and product IDs, so the two FK failures are intentional orphans, not generator accidents.

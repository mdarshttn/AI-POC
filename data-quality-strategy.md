# Data Quality Strategy

Quality runs in Silver. Bronze lands dirty strings. Gold reads clean Silver only.

## Quality Checks Overview

### 1. Completeness Check

- **What:** No missing primary keys (`customer_id`, `product_id`, `order_id`)
- **How:** Flag null or blank PKs in `src/silver/01_quality_completeness.py`
- **Threshold:** 100% of Silver rows have a PK (Bronze may contain the seeded blanks)
- **Result:** Flag `CUST_PK_NULL` / `PROD_PK_NULL` / `ORD_PK_NULL` and quarantine the row

### 2. Uniqueness Check

- **What:** No duplicate primary keys
- **How:** Window count by PK in `src/silver/02_quality_uniqueness.py`. Blank PKs are not treated as duplicates
- **Threshold:** 100% unique in Silver
- **Result:** Flag both duplicate rows (`CUST_PK_DUP`, `PROD_PK_DUP`, `ORD_PK_DUP`) and quarantine them

### 3. Referential Integrity

- **What:** Order FKs exist in parent tables
- **How:** Left join orders to clean Silver customers and products in `src/silver/04_quality_referential_integrity.py`
- **Threshold:** 100% of Silver orders have valid FKs
- **Result:** Flag orphans (`ORD_FK_CUSTOMER`, `ORD_FK_PRODUCT`) and quarantine them

Type and business checks are also implemented: email format, allowed category, parseable `order_date`, quantity > 0, prices >= 0, allowed order status (`src/silver/03_quality_type_validation.py`, `05_quality_business_logic.py`).

## Quality Metrics Report

| Entity | Bronze | Silver (passed) | Quarantine | Pass rate |
|--------|--------|-----------------|------------|-----------|
| customers | 10,000 | 9,996 | 4 | 99.96% |
| products | 500 | 495 | 5 | 99.00% |
| orders | 100,000 | 99,991 | 9 | 99.991% |

`ops.dq_results` = 18 rows. Review with:

```sql
SELECT table_name, rule_id, COUNT(*) AS failed_count
FROM workspace.ops.dq_results
GROUP BY table_name, rule_id
ORDER BY table_name, rule_id;
```

## Sample Data Quality Issues

18 intentional defects (seed 42), listed in `data/defect_log.csv`:

| table | rule_id | record_id | bad_value |
|-------|---------|-----------|-----------|
| customers | CUST_PK_NULL | (empty) | empty PK |
| customers | CUST_PK_DUP | CUST-DUP-01 | CUST-DUP-01 (2 rows) |
| customers | CUST_EMAIL_INVALID | CUST-BAD-EML | not-an-email |
| products | PROD_PK_NULL | (empty) | empty PK |
| products | PROD_PK_DUP | PROD-DUP-01 | PROD-DUP-01 (2 rows) |
| products | PROD_CATEGORY_INVALID | PROD-BAD-CAT | Food |
| products | PROD_PRICE_NEGATIVE | PROD-NEG-PRC | -10.00 |
| orders | ORD_PK_NULL | (empty) | empty PK |
| orders | ORD_PK_DUP | ORD-DUP-01 | ORD-DUP-01 (2 rows) |
| orders | ORD_QTY_INVALID | ORD-BAD-QTY | 0 |
| orders | ORD_PRICE_NEGATIVE | ORD-BAD-PRC | -5.00 |
| orders | ORD_STATUS_INVALID | ORD-BAD-STS | SHIPPPED |
| orders | ORD_FK_CUSTOMER | ORD-BAD-FCU | CUST-MISSING |
| orders | ORD_FK_PRODUCT | ORD-BAD-FPR | PROD-MISSING |
| orders | ORD_DATE_INVALID | ORD-BAD-DAT | 2099-12-31 23:59:59 |

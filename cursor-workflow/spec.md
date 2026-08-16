# Spec

Contracts for the POC. Implementation has not started. If code and this file diverge later, update this file in the same change.

## Scope

**In**

- Three entities: `customers`, `products`, `orders`
- Intentional bad data in the generated CSVs
- Bronze, Silver, Gold on Databricks
- Raw CSVs on a Unity Catalog Volume (read by Spark as files)
- Data quality checks, automated tests, validation
- Databricks SQL dashboard (business + quality)

**Out**

- Extra entities (`order_items`, payments, sessions, and similar)
- Streaming
- Extra DQ or orchestration frameworks
- Production IAM, CI platforms, or multi-environment promotion (unless asked later)

## Entities

### customers

| Column | Logical type | Notes |
|--------|--------------|--------|
| `customer_id` | string | Primary key |
| `first_name` | string | Required on clean rows |
| `last_name` | string | Required on clean rows |
| `email` | string | Unique on clean rows; must look like an email |
| `signup_date` | date | Not in the future |
| `country` | string | Required on clean rows |
| `city` | string | Optional |

### products

| Column | Logical type | Notes |
|--------|--------------|--------|
| `product_id` | string | Primary key |
| `product_name` | string | Required on clean rows |
| `category` | string | Required; allowed values listed below |
| `unit_price` | decimal | `>= 0` on clean rows |
| `in_stock` | integer | `>= 0` on clean rows |

Allowed `category` values: `Electronics`, `Home`, `Fashion`, `Sports`, `Books`.

### orders

Each row is one order for **one** customer and **one** product.

| Column | Logical type | Notes |
|--------|--------------|--------|
| `order_id` | string | Primary key |
| `customer_id` | string | FK to `customers.customer_id` |
| `product_id` | string | FK to `products.product_id` |
| `order_date` | timestamp | Not in the future |
| `quantity` | integer | `> 0` on clean rows |
| `unit_price` | decimal | Price at purchase; `>= 0` |
| `order_status` | string | Allowed values listed below |
| `payment_method` | string | Allowed values listed below |

Allowed `order_status` values: `pending`, `paid`, `shipped`, `delivered`, `cancelled`.

Allowed `payment_method` values: `card`, `upi`, `netbanking`, `cod`.

**Revenue on a clean order row:** `quantity * unit_price`. Cancelled orders should be excluded from revenue KPIs unless a later Gold spec says otherwise. Default: exclude `cancelled`.

## Files in the raw volume

Prefix: `/Volumes/workspace/ai-poc/ai-data/`  
Configured in `src/pipeline/common/settings.py` (`RAW_DATA_PREFIX`). Do not hardcode this path in notebooks.

| Entity | Path | Bronze? |
|--------|------|---------|
| customers | `/Volumes/workspace/ai-poc/ai-data/customers.csv` | Yes |
| products | `/Volumes/workspace/ai-poc/ai-data/products.csv` | Yes |
| orders | `/Volumes/workspace/ai-poc/ai-data/orders.csv` | Yes |
| defect_log | `/Volumes/workspace/ai-poc/ai-data/defect_log.csv` | No — expected-defect reference only |

CSV conventions (when generation starts): UTF-8, comma-separated, header row, optional quoted fields. Dates as `YYYY-MM-DD`. Timestamps as `YYYY-MM-DD HH:MM:SS`.

## Medallion layers

### Bronze

**Reads:** The three entity CSVs on the raw volume. Does not read `defect_log.csv`. Does not modify the files.

**Writes:** Delta tables `workspace.bronze.customers`, `workspace.bronze.products`, `workspace.bronze.orders` (shown as `bronze.customers` after `USE CATALOG workspace`). Full-table overwrite so a re-run cannot duplicate rows.

**Behavior:**

- Schema-on-read. Prefer storing payload columns as strings so ingest does not fail on dirty types.
- Add ingest metadata: `_ingest_file`, `_ingest_ts`, `_run_id`.
- Do not drop rows for business-rule failures. Unreadable files should be logged, not ignored.
- Idempotent for a given `_run_id` (re-running the same run should not duplicate that run’s rows).

### Silver

**Reads:** Bronze tables only.

**Writes:**

- Clean: `workspace.silver.customers`, `workspace.silver.products`, `workspace.silver.orders`
- Quarantine: `workspace.ops.quarantine_customers`, `workspace.ops.quarantine_products`, `workspace.ops.quarantine_orders` (original Bronze string values plus rule metadata)
- Quality: `workspace.ops.dq_results` (one row per failed rule: `run_id`, `table_name`, `rule_id`, `record_id`, `row_fingerprint`, `failed_column`, `failed_value`, `severity`, `message`)

**Behavior:**

- Read Bronze Delta tables only. Do not read Volume CSVs or `defect_log.csv`.
- Cast clean rows to logical types.
- Apply the named quality rules. Any failure sends the **entire Bronze row** to quarantine; it does not enter Silver.
- Duplicate primary keys: quarantine **both** rows. Do not keep a winner in Silver.
- Silver `orders` FK checks use clean `silver.customers` and `silver.products` only.
- Full-table overwrite of Silver, quarantine, and `dq_results` so a re-run cannot duplicate rows.
- Conservation: Bronze count = Silver count + quarantine count per entity.

### Gold

**Reads:** Silver clean tables only (plus `ops.dq_results` / quarantine for quality tiles).

**Writes (planned):**

- `gold.dim_customer`
- `gold.dim_product`
- `gold.fact_orders`
- `gold.kpi_daily` (optional helper: date, order_count, revenue, aov)

Gold is SQL. Grain of `fact_orders` is one row per `order_id`.

## Quality rules (intentional defects must hit these)

Seeded bad data in the generator must be explainable by a `rule_id`. Suggested ids:

| rule_id | Entity | Check |
|---------|--------|--------|
| `CUST_PK_NULL` | customers | `customer_id` present |
| `CUST_PK_DUP` | customers | `customer_id` unique |
| `CUST_EMAIL_INVALID` | customers | email contains `@` and a domain |
| `PROD_PK_NULL` | products | `product_id` present |
| `PROD_PK_DUP` | products | `product_id` unique |
| `PROD_CATEGORY_INVALID` | products | category in allowed list |
| `PROD_PRICE_NEGATIVE` | products | `unit_price >= 0` |
| `ORD_PK_NULL` | orders | `order_id` present |
| `ORD_PK_DUP` | orders | `order_id` unique |
| `ORD_QTY_INVALID` | orders | `quantity > 0` |
| `ORD_PRICE_NEGATIVE` | orders | `unit_price >= 0` |
| `ORD_STATUS_INVALID` | orders | status in allowed list |
| `ORD_FK_CUSTOMER` | orders | `customer_id` exists in silver customers |
| `ORD_FK_PRODUCT` | orders | `product_id` exists in silver products |
| `ORD_DATE_INVALID` | orders | parseable timestamp, not future |

Generator (later) should emit a defect log listing injected `rule_id`s so tests can expect quarantine counts.

## Dashboard

Databricks SQL, one dashboard.

**Business tiles (from Gold):**

- Order count
- Revenue (excluding `cancelled`)
- Average order value
- Top products by revenue
- Orders by status or by day

**Quality tiles (from `ops`):**

- Bronze row count vs Silver row count per entity
- Quarantine count and rate
- Failures grouped by `rule_id`

## Tests (when that stage starts)

| Kind | What it proves |
|------|----------------|
| Generator unit | Seed is reproducible; defect log matches injected rows |
| Transform unit | Given a tiny DataFrame, Bronze/Silver functions emit expected columns |
| Quality | Each seeded defect class fails its `rule_id` and does not enter Silver |
| Gold SQL | `fact_orders` grain is `order_id`; revenue formula matches spec |
| Fixtures | Tiny CSVs committed under `tests/fixtures/`; no large dumps in git |

No Great Expectations (or similar) suites.

## Success criteria for the POC

1. Raw CSVs are visible in DBFS.
2. Bronze, Silver, and Gold tables exist and follow the read/write rules above.
3. Intentional bad rows are quarantined with named rules.
4. Tests fail if those rules or grains break.
5. The dashboard shows both sales KPIs and quality results.

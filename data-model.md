# Data model

Logical types for Silver. Bronze stores the same payload columns as **strings**. Gold dims/facts are projections of clean Silver.

## customers

| | |
|---|---|
| **Grain** | One row per customer |
| **PK** | `customer_id` |
| **FK** | None |

| Column | Logical type | Role |
|--------|--------------|------|
| `customer_id` | string | Identity |
| `first_name` | string | Attribute |
| `last_name` | string | Attribute |
| `email` | string | Contact; format-checked in Silver |
| `signup_date` | date | Attribute (`yyyy-MM-dd` in CSV) |
| `country` | string | Attribute |
| `city` | string | Attribute |

## products

| | |
|---|---|
| **Grain** | One row per product |
| **PK** | `product_id` |
| **FK** | None |

| Column | Logical type | Role |
|--------|--------------|------|
| `product_id` | string | Identity |
| `product_name` | string | Attribute |
| `category` | string | Allowed: Electronics, Home, Fashion, Sports, Books |
| `unit_price` | decimal(10,2) | List price; `>= 0` on clean rows |
| `in_stock` | integer | Attribute; no named DQ rule in this POC |

## orders

| | |
|---|---|
| **Grain** | One row per order; **one product per order** |
| **PK** | `order_id` |
| **FK** | `customer_id` → silver.customers; `product_id` → silver.products |

| Column | Logical type | Role |
|--------|--------------|------|
| `order_id` | string | Identity |
| `customer_id` | string | FK |
| `product_id` | string | FK |
| `order_date` | timestamp | CSV `yyyy-MM-dd HH:mm:ss`; not after AS_OF_DATE |
| `quantity` | integer | `> 0` on clean rows |
| `unit_price` | decimal(10,2) | Price at purchase; `>= 0` |
| `order_status` | string | pending, paid, shipped, delivered, cancelled |
| `payment_method` | string | card, upi, netbanking, cod; no named DQ rule |

**Revenue on a clean order:** `quantity * unit_price`. Cancelled orders stay in Silver and `gold.fact_orders`. Gold KPI tables exclude `order_status = 'cancelled'`.

There is no `order_items` entity. AOV in this POC is average single-product order value.

## Layer mapping

| Column set | Bronze | Silver (clean) | Gold |
|------------|--------|----------------|------|
| Entity payload | strings + `_ingest_*` | typed + run ids | dims / `fact_orders` / performance tables |
| Failed rows | still in Bronze | quarantine + `ops.dq_results` | not read |

Full Unity Catalog DDL (documentary): `database/schema.sql`.

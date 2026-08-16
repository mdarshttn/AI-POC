# AI Prompts — Gold Layer

## Prompt 1: Gold marts from Silver

**PROMPT SENT:**
Gold only. Read Silver. Sales / customer / product performance with total orders, quantity, sales, AOV. Daily trend. Thin notebook. Overwrite. No dashboard or pytest yet. Do not change Bronze/Silver. Exclude cancelled from KPIs. `fact_orders` count must equal Silver orders.

**AI RESPONSE SUMMARY:**
`build.py` (now `src/gold/create_gold_tables.py`) writing `dim_customer`, `dim_product`, `fact_orders`, `sales_performance`, `customer_performance`, `product_performance`, `kpi_daily`. KPIs filter `order_status != cancelled`. Raises if fact count drifts or `sales_performance` is not 1 row.

**YOUR EVALUATION:**

- **Accepted:** Same module + notebook pattern as Bronze/Silver. Cancelled excluded from KPI tables but kept on `fact_orders`.
- **Changed:** Added read-only SQL files `01_sales_by_product.sql`, `02_revenue_by_customer.sql`, `03_daily_weekly_trends.sql` for the submission tree. They SELECT from the PySpark tables; they do not write a second Gold path.
- **Rejected:** Gold as SQL-only files with no runner. Rejected High-Value / Repeat / One-Time / Inactive segmentation as a new table (not in the locked spec). `04_customer_segmentation.sql` documents that gap.

**Validation:** Databricks run plus `notebooks/Validation.ipynb` (Silver vs Gold counts).

# AI Prompts — Gold Layer

## Prompt 1: Implement Gold

**PROMPT SENT:**
okay silver is working fine now lets move to gold

implement only the gold layer for this poc and dont change bronze or silver

gold should read only from the clean silver tables and create business level tables for sales customer and product performance

include metrics like total orders total quantity total sales and average order value

keep the logic simple and modular under src/pipeline/gold and create a thin databricks notebook to run it

make it rerunnable without duplicate records

dont start dashboard or testing yet

**AI RESPONSE SUMMARY:**
PySpark Gold build: `dim_customer`, `dim_product`, `fact_orders` (`order_sales = quantity * unit_price`), `sales_performance`, `customer_performance`, `product_performance`, `kpi_daily`. KPI tables exclude `cancelled`. Overwrite. Raises if `fact_orders` count ≠ Silver orders. Thin notebook `03_gold_build.py`.

**YOUR EVALUATION:**

✓ **What was good:** Silver-only reads, overwrite, AOV, cancelled excluded from KPIs  
✗ **What needed fixing:** none after Databricks run and Validation.ipynb counts  
△ **Missing:** dashboard (intentionally out of this prompt)

**Accepted** the PySpark writer. **Changed later** — added SELECT SQL files `01_sales_by_product.sql`, `02_revenue_by_customer.sql`, `03_daily_weekly_trends.sql` for the submission tree. **Rejected** Gold as SQL-only with no runner.

**FINAL DECISION:** `src/gold/create_gold_tables.py` + `notebooks/03_gold_build.py`

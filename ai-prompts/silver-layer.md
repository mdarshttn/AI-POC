# AI Prompts — Silver Layer

## Prompt 1: Silver design (no code)

**PROMPT SENT:**
before we start implementing silver, i want to design the silver layer properly based on the current project and the bronze layer that is already working.

please inspect the existing cursor-workflow/spec.md, project-context.md, task-breakdown.md and the current bronze implementation.

i want you to propose the silver design only, dont modify any files or write code yet.

the silver layer must read only from the bronze delta tables, never directly from the raw csv files.

for customers, products and orders explain the expected silver schema and the data type conversions from bronze strings to the logical types in our spec.

also design how each of our existing dq rules will be detected:
CUST_PK_NULL, CUST_PK_DUP, CUST_EMAIL_INVALID,
PROD_PK_NULL, PROD_PK_DUP, PROD_CATEGORY_INVALID, PROD_PRICE_NEGATIVE,
ORD_PK_NULL, ORD_PK_DUP, ORD_QTY_INVALID, ORD_PRICE_NEGATIVE, ORD_STATUS_INVALID, ORD_FK_CUSTOMER, ORD_FK_PRODUCT and ORD_DATE_INVALID.

explain how valid records will go to silver and invalid records will go to quarantine without silently dropping them.

also propose the structure of the dq_results table, including run_id, table name, rule_id, record identifier and useful failure information.

for duplicate primary keys, explain clearly how you would handle both records and how the result should appear in quarantine.

for order foreign keys, make sure the check is against the clean silver customer and product records, not just bronze.

keep the design simple and use only pyspark, sql and databricks. dont introduce great expectations, dbt or any other framework.

finally give me the silver input/output flow and the validation checks we should perform after implementation.

again, this is only a design review. dont create or modify any files yet

**AI RESPONSE SUMMARY:**
Design only. Called out keep-a-winner vs quarantine both duplicate PK rows. Recommended both rows quarantined. Customers/products first, then order FKs vs clean Silver. `dq_results` one row per failed rule. Expected split 9996+4 / 495+5 / 99991+9.

**YOUR EVALUATION:**

✓ **What was good:** Bronze-only reads, 15 named rules, conservation, FK vs Silver  
✗ **What needed fixing:** Spec “keep a winner” was rejected in favour of both-dup-rows  
△ **Missing:** Code (intentionally)

**Accepted** the design. **Rejected** Great Expectations and extra unofficial rules.

---

## Prompt 2: Implement Silver

**PROMPT SENT:**
okay bronze is working and the data is already available in workspace.bronze tables. lets move to silver now.

please implement only the silver layer based on the design we reviewed. dont start gold, dashboard, testing framework or modify the generator.

silver should read only from workspace.bronze.customers, workspace.bronze.products and workspace.bronze.orders. it should not read the csv files or defect_log directly.

implement the silver pyspark logic under src/pipeline/silver and create a thin databricks notebook/entry point to run it.

for customers and products, apply the agreed DQ rules first and write valid typed records to workspace.silver.customers and workspace.silver.products. invalid records should go to workspace.ops.quarantine_customers and workspace.ops.quarantine_products.

then process orders and validate its foreign keys against the clean silver customers and products tables. valid orders should go to workspace.silver.orders and invalid ones should go to workspace.ops.quarantine_orders.

use the exact rule ids we agreed on:
CUST_PK_NULL, CUST_PK_DUP, CUST_EMAIL_INVALID,
PROD_PK_NULL, PROD_PK_DUP, PROD_CATEGORY_INVALID, PROD_PRICE_NEGATIVE,
ORD_PK_NULL, ORD_PK_DUP, ORD_QTY_INVALID, ORD_PRICE_NEGATIVE, ORD_STATUS_INVALID,
ORD_FK_CUSTOMER, ORD_FK_PRODUCT, ORD_DATE_INVALID

for duplicate primary keys, quarantine both duplicate rows rather than keeping one of them.

keep the original bronze values in quarantine so we can see what failed. create workspace.ops.dq_results with one row for each failed rule and include the run id, table name, rule id, record id, failed column, failed value and a row fingerprint so duplicate records can still be distinguished.

bronze counts should be conserved:
customers 10000 = silver 9996 + quarantine 4
products 500 = silver 495 + quarantine 5
orders 100000 = silver 99991 + quarantine 9

use 2026-08-16 as the as_of_date for the order date validation.

silver should convert the bronze string columns to their agreed logical types. dont silently drop records and dont add new dq rules.

make the silver run rerunnable without duplicating records. use overwrite for the silver, quarantine and dq_results outputs for a run.

keep the implementation reasonably simple and modular. after creating the files, review your implementation and tell me exactly what files you created and how i should run the silver notebook in databricks.

dont run or implement anything for gold, dashboard or pytest yet

**AI RESPONSE SUMMARY:**
`rules.py` + transform + `notebooks/02_silver_transform.py`. Duplicate window ignores blank PKs. Job raises if counts drift. `dq_results` = 18 rows.

**YOUR EVALUATION:**

✓ **ACCEPTED** — Databricks run matched 9996+4 / 495+5 / 99991+9 and 18 `dq_results`  
✗ **Changed later** — rules split into `01`–`05` quality files + `create_silver_tables.py` for submission layout  
△ **Rejected** — extra rules for payment_method / in_stock / names / signup_date

Two follow-up prompts restated the same implement request (dq_results columns, overwrite, count validation). Same code path; no new rules.

**FINAL DECISION:** `src/silver/create_silver_tables.py` + quality modules + `notebooks/02_silver_transform.py`

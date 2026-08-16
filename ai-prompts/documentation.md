# AI Prompts — Documentation

## Prompt 1: Stage the work (no code)

**PROMPT SENT:**
Hi Cursor,
I’m starting a data engineering POC for an e-commerce use case and I want to build it step by step rather than generating the whole project at once.

The main stack will be Python for data generation, PySpark and Databricks for the data pipeline, SQL for the business layer and Databricks Sql for the dashboard. The raw data will be CSV files stored in DBFS.

The pipeline should follow a Bronze, Silver and Gold structure. We also need intentional bad data so that we can demonstrate data quality checks, automated testing, and validation. At the end there will be a dashboard showing results.

Before writing any code, help me break this into practical development stages. For each stage, what the input and output should be, and how the stages will connect with each other.

I also want the project to be maintainable, so consider how we should organize Python, PySpark, SQL, tests and documentation in the repository.

Don't generate code yet.

**AI RESPONSE SUMMARY:**
Seven stages with inputs, outputs, and exit checks. Early draft mentioned extra tools and a fourth entity (`order_items`).

**YOUR EVALUATION:**

✓ **What was good:** Stage-by-stage plan, medallion, defect-driven DQ  
✗ **What needed fixing:** Extra frameworks and `order_items`  
△ **Missing:** Code (intentionally)

**Accepted** staged build. **Rejected** generating the whole repo at once.

---

## Prompt 2: Foundation files

**PROMPT SENT:**
Yes, lets start with the foundation, but before creating it I want to keep the implementation aligned with the original POC requirements rather than adding extra technologies.

For now use the three core entities from the requirement: customers, products and orders. We will keep the architecture simple and use Python, PySpark, Sql and Databricks with CSV files in DBFS. Don't use extra frameworks such as Great Expectations, Asset Bundles or other tools.

Please create the initial project skeleton and a cursor-workflow folder with project-context.md, spec.md, cursor-rules-or-instructions.md and task-breakdown.md.

The context files should capture what we currently know about the project, the intended Bronze - Silver - Gold flow, the role of DBFS, the testing approach, the dashboard goal and the fact that we will build and validate the project incrementally.

For now don't create any pipeline code, data generator, notebooks, SQL queries or tests. I only want the foundation and context files so we have a clean base for the next steps.

**AI RESPONSE SUMMARY:**
README, `.gitignore`, empty folders, four `cursor-workflow/` files. Three entities locked. Extra frameworks banned.

**YOUR EVALUATION:**

✓ **ACCEPTED** — skeleton only, no pipeline code  
✗ **Changed later** — FileStore notes replaced by the Volume path after upload

---

## Prompt 3: Data model review (no files)

**PROMPT SENT:**
Before we move to the data generator, I want to review the data model we just created. Don't change any files yet.

Please review the current spec and show me the proposed structure for customers, products and orders, including the columns, data types, primary keys, foreign keys and the grain of each table.

For the orders table, explain the assumption that one order directly references one product and why that is appropriate for this POC. Also explain what limitations this creates compared with having a separate order_items table.

For each table, tell me which columns are important for the Bronze, Silver and Gold layers and which columns will be used for the required data-quality checks.

I want this as a design review only. Don't generate or modify any code or files yet. If you think any part of the current model doesn't align with the project requirements, point it out instead of silently changing it

**AI RESPONSE SUMMARY:**
Three-table model is usable. One-product-per-order is a POC simplification vs `order_items`. Flagged spec notes with no `rule_id` (payment_method, in_stock, names, signup_date).

**YOUR EVALUATION:**

✓ **ACCEPTED** — keep three tables; only named rules in Silver  
✗ **Rejected** — adding unofficial DQ rules or `order_items`

---


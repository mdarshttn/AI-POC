# AI Prompts — Data Generation

## Prompt 1: Generator design (no code)

**PROMPT SENT:**
the data model looks good and I want to move to the synthetic data generator now. before writing the Python code, I want to design exactly what the generator should produce.

we need three CSV datasets: customers, products and orders. The generator should create realistic e-commerce data and also intentionally inject the data-quality issues required by the POC so that we can later prove that the Silver layer catches them

please design the generator around these requirements:

- customers: 10,000 records
- products: 500 records
- orders: 100,000 records
- use a fixed random seed so the output is reproducible
- keep the three-table relationship valid for the normal records
- generate the required bad records deliberately rather than randomly
- keep a small defect log that tells us which generated records contain which defect

for now, don't write the Python implementation. Give me a concise design for the generation process, including how you would generate each table, how you would inject each required defect, how you would make the defect injection reproducible, and what the defect log should contain.

Don't add additional defect categories unless they are necessary for one of the required checks. I want to review the design before we implement it

**AI RESPONSE SUMMARY:**
Design only. Good rows first, then a fixed defect block. Reserved duplicate IDs so good rows cannot collide. Good orders only reference good customer and product IDs. Defect log: table, rule_id, record_id, source_row, column, bad_value. 18 log rows covering the 15 named rules (dups count twice).

**YOUR EVALUATION:**

✓ **What was good:** Deterministic defects, reserved IDs, defect log mapped to `rule_id`s  
✗ **What needed fixing:** Nothing in the design; implementation came next  
△ **Missing:** Code (intentionally — design-only prompt)

**Accepted** the design. **Rejected** random “corrupt 1% of rows.”

---

## Prompt 2: Implement the generator

**PROMPT SENT:**
okay the generator design looks good, lets implement it now.

create the python generator based on the design we just discussed. keep the generator standalone python, no pyspark or databricks code in it.

it should generate the 3 csv files under data/sample/generated/:

- customers.csv — 10,000 rows
- products.csv — 500 rows
- orders.csv — 100,000 rows
- defect_log.csv

use seed 42 and AS_OF_DATE = 2026-08-16 so the output is reproducible. please keep the good records and defect records separate in the code so its easy to understand and test.

also make sure the normal orders only reference valid customer and product ids. the intentional bad records should be the exact defect cases from the design we just reviewed, and the defect_log should capture the rule_id, record_id, source_row, column and bad_value.

please add basic validation at the end of the generator which checks the final row counts and that the defect log contains the expected number of records.

keep the code reasonably clean and modular, with separate functions for generating customers, products, orders, injecting defects and writing the csv files. don't over-engineer it.

after creating the code, run it and show me the generated file names, row counts and the defect summary. don't start working on DBFS, pyspark, bronze or any other stage yet.

**AI RESPONSE SUMMARY:**
Wrote the generator (`generate_good_*` + `inject_*_defects`). Ran it locally. Output: 10000 / 500 / 100000 / 18, “Validation passed.”

**YOUR EVALUATION:**

✓ **ACCEPTED** — counts and defect summary matched the design; no Spark in the generator  
✗ **Changed later** — output path moved to `data/` for the submission tree  
△ **Rejected** — Faker, extra columns, Spark imports

**FINAL DECISION:** `src/data_generation/generate_sample_data.py`

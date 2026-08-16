# AI Prompts — Data Generation

## Prompt 1: Generator design (no code)

**PROMPT SENT:**
Design a standalone Python generator for this POC. Volumes: 10,000 customers, 500 products, 100,000 orders, plus a defect log. Seed 42, AS_OF_DATE 2026-08-16. Deliberate defects that map to the named Silver `rule_id`s. Good orders must only reference good customer and product IDs. No Spark.

**AI RESPONSE SUMMARY:**
Proposed good rows first, then a **fixed** defect block appended at the end of each file. Reserved duplicate IDs (`CUST-DUP-01`, etc.) so the good population cannot collide. Defect log columns: table, rule_id, record_id, source_row, column, bad_value. Warned against randomly corrupting 1% of rows.

**YOUR EVALUATION:**

- **Accepted:** Good-then-defect structure, reserved IDs, 18-row log matching the 15 rules (dups count twice).
- **Changed:** Later output path became `data/` (was `data/sample/generated/`) to match the submission tree.
- **Rejected:** Faker library, random dirty-data percentage, extra columns such as `customer_segment` / `lifetime_value` from the generic assessment example.

## Prompt 2: Implement the generator

**PROMPT SENT:**
Implement the generator from that design. Standalone Python. Write `customers.csv`, `products.csv`, `orders.csv`, `defect_log.csv`. Keep good records and defect records separate in code. Add validation that counts match and that good order FKs stay inside the good ID sets.

**AI RESPONSE SUMMARY:**
Wrote `generate.py` (now `src/data_generation/generate_sample_data.py`) with `generate_good_*` and `inject_*_defects`. Local run printed 10000 / 500 / 100000 / 18 and “Validation passed.”

**YOUR EVALUATION:**

- **Accepted:** Implementation after I ran it locally and checked the defect summary.
- **Changed:** Output directory to `data/` during the repo-layout match.
- **Rejected:** Spark or Databricks imports in the generator.

**FINAL DECISION:** Use `src/data_generation/generate_sample_data.py` as the generator. Notes: `src/data_generation/DATA_GENERATION_NOTES.md`.

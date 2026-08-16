# AI Prompts — Silver Layer

## Prompt 1: Silver design (no code)

**PROMPT SENT:**
Design Silver from Bronze + the spec. Bronze only. 15 named rules. Quarantine failed rows. FK checks against clean Silver. `dq_results` one row per failure. Overwrite. Conservation counts. Do not touch the generator.

**AI RESPONSE SUMMARY:**
Called out the spec conflict: “keep a PK winner” vs a demo that needs `CUST_PK_DUP` visible. Proposed writing customers/products first, then orders with FKs vs Silver. Listed the 15 `rule_id`s.

**YOUR EVALUATION:**

- **Accepted:** Both duplicate rows quarantined; FK after dimensions; 18 expected `dq_results` rows.
- **Changed:** none at design time.
- **Rejected:** Extra unofficial rules for payment_method, in_stock, names, signup_date. Rejected Silver reading Volume CSVs.

## Prompt 2: Silver implementation

**PROMPT SENT:**
Implement the design. Do not add new rule ids. Raise if counts are not 9996+4 / 495+5 / 99991+9 and `dq_results` ≠ 18.

**AI RESPONSE SUMMARY:**
`rules.py` + transform + `notebooks/02_silver_transform.py`. Window uniqueness ignoring blank PKs. Quarantine keeps original Bronze strings.

**YOUR EVALUATION:**

- **Accepted:** After Databricks run matched the expected split.
- **Changed:** Later split flags into `01_quality_completeness.py` … `05_quality_business_logic.py` with `create_silver_tables.py` as orchestrator. Same flags and counts.
- **Rejected:** Great Expectations. Rejected “keep latest” on duplicate PKs.

**Validation:** Silver on Databricks accepted before Gold.

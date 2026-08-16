# AI Prompts — Debugging

No separate “debug this stack trace” prompt. Issues were caught in design reviews and when a job refused the expected counts. Cursor explained likely causes; I ran the notebook and kept or rejected the fix.

## Issue 1: Empty PK vs uniqueness

Came up in Silver design/implement (duplicate PK rules).

**Problem:** Generator writes an empty `customer_id`. Spark CSV often stores that as null. A window on PK would treat all nulls as one duplicate group.

**AI RESPONSE SUMMARY:** Completeness = null or blank. Uniqueness ignores blank PKs so one missing key is `CUST_PK_NULL` only.

**YOUR EVALUATION:**

✓ **ACCEPTED** — matches the single seeded null-PK row  
✗ **Rejected** — filling empty PK with a placeholder ID

---

## Issue 2: FK parent table

Came up in the Silver design prompt (FK must be against clean Silver).

**AI RESPONSE SUMMARY:** Write Silver customers/products first; join orders to those tables.

**YOUR EVALUATION:**

✓ **ACCEPTED**  
✗ **Rejected** — joining Bronze or `defect_log.csv`

---

## Issue 3: Raw path

Came up after local CSVs were uploaded.

**PROMPT SENT (from Bronze implement):** files are at `/Volumes/workspace/ai-poc/ai-data/`

**AI RESPONSE SUMMARY:** Set `RAW_DATA_PREFIX` to that Volume.

**YOUR EVALUATION:**

✓ **ACCEPTED**  
✗ **Rejected** — leaving FileStore as the live raw path

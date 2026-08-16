# AI Prompts — Debugging

Cursor was used to explain likely causes. I still ran the failing notebook and accepted or rejected the fix. No invented stack traces.

## Prompt 1: Empty PK vs duplicate window

**PROMPT SENT (summary):**
Generator writes an empty `customer_id`. After Spark CSV ingest that may be null. How should uniqueness treat it so we do not also fire `CUST_PK_DUP`?

**AI RESPONSE SUMMARY:**
Treat null and blank as completeness failures. Duplicate window should ignore blank PKs (`when(is_blank(pk), false)`).

**YOUR EVALUATION:**

- **Accepted:** Matches the seeded single null-PK row (one `CUST_PK_NULL`, not a fake dup group).
- **Rejected:** Coalescing empty PK to a placeholder ID (would hide the completeness demo).

## Prompt 2: FK parent

**PROMPT SENT (summary):**
Should order FK checks join Bronze customers/products or Silver?

**AI RESPONSE SUMMARY:**
Join clean Silver after those tables are written, otherwise a dirty parent could still “validate” an order.

**YOUR EVALUATION:**

- **Accepted:** `ORD_FK_*` vs Silver only.
- **Rejected:** Checking FKs against Bronze or against `defect_log.csv`.

## Prompt 3: Path not found

**PROMPT SENT (summary):**
Bronze cannot see the CSVs. Early notes said FileStore.

**AI RESPONSE SUMMARY:**
Point `RAW_DATA_PREFIX` at the Volume that actually holds the files.

**YOUR EVALUATION:**

- **Accepted:** `/Volumes/workspace/ai-poc/ai-data/`.
- **Rejected:** Leaving FileStore as the documented raw path.

Write-up: `debugging-notes.md`.

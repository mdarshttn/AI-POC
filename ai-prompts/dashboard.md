# AI Prompts — Dashboard

Dashboard **SQL and notebook exist**. Assembling a Databricks SQL warehouse dashboard in the UI is the remaining follow-up (skipped in this pass).

## Prompt 1: Read-only tiles from Gold and ops

**PROMPT SENT:**
Dashboard from Gold. KPIs, trend, top customers/products, category performance, plus a small DQ section from ops. No new processing. Do not change pipeline code.

**AI RESPONSE SUMMARY:**
SQL files and `notebooks/04_dashboard.py` with `%sql` cells. Category rollup in SQL rather than a new Gold table.

**YOUR EVALUATION:**

- **Accepted:** Read-only SELECTs against `workspace.gold` and `workspace.ops`.
- **Changed:** Combined queries into `src/dashboard/dashboard_queries.sql` for the submission tree.
- **Rejected:** Recalculating revenue from Bronze or CSVs.

**Still to do:** Create the Lakeview / SQL dashboard object in the warehouse UI and attach visualisations (counters, line, bars). Guide: `src/dashboard/DASHBOARD_GUIDE.md`.

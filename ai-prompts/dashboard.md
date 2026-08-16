# AI Prompts — Dashboard

## Prompt 1: Dashboard from Gold

**PROMPT SENT:**
I have pushed the changes to databricks and have verified it is working fine for now,

lets move to the dashboard stage now

the generator bronze silver and gold layers are already completed and validated so dont modify them

create the dashboard based only on the gold tables in workspace.gold

first review the existing gold tables and project structure and then create a simple dashboard setup for this poc

i want the dashboard to show total sales total orders average order value total quantity sales trend top customers top products and category performance

also add a small data quality section using the existing dq results and quarantine tables so we can show failed rules and quarantined records

keep the dashboard simple and clean and dont add any new data processing logic or modify bronze silver gold

also update the project documentation with what we have completed so far and add the dashboard related documentation

dont start any new pipeline layer after this

**AI RESPONSE SUMMARY:**
Read-only SQL tiles and `notebooks/04_dashboard.py`. Sales from `workspace.gold`. Quality from `workspace.ops`. Category rollup in SQL, not a new Gold table.

**YOUR EVALUATION:**

✓ **ACCEPTED** — SELECT only; no new transforms; pipeline code unchanged  
✗ **Changed later** — queries combined into `src/dashboard/dashboard_queries.sql`  
△ **Missing** — warehouse UI dashboard object (SQL and notebook are the artifacts in git)

**Rejected** recalculating revenue from Bronze or CSVs.

**FINAL DECISION:** `src/dashboard/dashboard_queries.sql` + `notebooks/04_dashboard.py` + `DASHBOARD_GUIDE.md`

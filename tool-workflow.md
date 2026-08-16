# Tool workflow

How Cursor was used on this POC. Same facts as `final-ai-usage-summary.md`, written for the assessment “tool workflow” artifact.

AI assisted with **code generation, explanation, debugging, and documentation**. Generated code was **reviewed, tested, and validated by me** on local Python (generator) and Databricks (Bronze, Silver, Gold) before I treated a stage as done.

## Loop I actually used

```text
write a short prompt for ONE stage
    → AI returns a design (no code) when I asked for design
    → I accept / cut scope
    → AI writes files for that stage only
    → I run it (local or Databricks)
    → I only then ask for the next stage
```

I did not one-shot “generate the whole pipeline.” Early chat was explicitly “don’t generate code yet.”

## Stage map

| Work | Cursor used for | Human gate |
|------|-----------------|------------|
| Requirements / stages | Structure, risks | Cut extra tools and extra entities |
| Architecture | Medallion + folder layout | Volume path, overwrite, no GE |
| Data model | PK/FK/grain review | Keep 3 tables; 15 rules only |
| Generator | Design + `generate_sample_data.py` | Local run, 18-row defect log |
| Bronze | Ingest module + notebook | Databricks row counts 10k/500/100k |
| Silver | Rules + transform | Databricks 9996+4 / 495+5 / 99991+9 |
| Gold | Marts + notebook | `fact_orders` = silver orders; Validation.ipynb |
| Dashboard | SQL + display notebook | Queries only hit gold/ops |
| These docs | Draft from repo + chat | Cross-check so we don’t claim pytest/segmentation |

## Accept / reject examples

| AI suggestion | Decision | Why |
|---------------|----------|-----|
| Databricks Asset Bundles | Rejected | Brief is Python/PySpark/SQL/Databricks only |
| Great Expectations | Rejected | Named Spark rules + `dq_results` are enough |
| `order_items` | Rejected | Three-entity requirement |
| Keep one row on duplicate PK | Rejected | Would hide the DQ demo |
| FileStore raw path | Changed | Files live on `/Volumes/workspace/ai-poc/ai-data/` |
| pytest as Stage 5 before Gold | Deferred then added as local `unittest` | Spark jobs stay the Databricks gate; laptop tests lock contracts |
| Customer segmentation | Not built | Not in the locked Cursor spec for this repo |

## Evidence trail

- Prompts: `ai-prompts/`
- Counts: `docs/validation.md`
- Code review: `code-review-notes.md`
- Code the model touched lives under `src/` and `notebooks/`; I ran those entrypoints, I did not paste unverified snippets into Databricks as the source of truth

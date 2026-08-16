# AI Prompts — Documentation

## Prompt 1: Assessment docs from the real repo

**PROMPT SENT:**
Write the assessment docs from the brief and the real repo. Only what is implemented. Include prompts. AI drafted code; I reviewed and ran it. Do not change pipeline code. Do not claim pytest, segmentation, or FileStore as live.

**AI RESPONSE SUMMARY:**
Requirements, architecture, validation, testing, debugging, AI workflow, prompt history, reflection, `tool-workflow.md`.

**YOUR EVALUATION:**

- **Accepted:** After checking claims against `src/` and notebooks.
- **Rejected:** Documenting faker, ~700 random issues, or a Gold segmentation table as if they existed.

## Prompt 2: Match the submission folder tree

**PROMPT SENT:**
Restructure the repo to the desired assessment layout (root markdown names, `src/bronze|silver|gold|dashboard`, `database/`, `ai-prompts/`) without inventing unimplemented features.

**AI RESPONSE SUMMARY:**
Moved generator, split Bronze/Silver files, added Gold SQL SELECTs, dashboard combo file, root docs, `database/`. Kept notebooks and `src/common/`.

**YOUR EVALUATION:**

- **Accepted:** Layout match with honest extras (`notebooks/`, `src/common/`, `defect_log.csv`).
- **Changed:** This follow-up: rewrite docs to the required headings; add local unittests; add `code-review-notes.md` and `test-strategy.md`.
- **Rejected:** Fake 700 defects or a pytest-on-Spark suite that cannot run without Databricks.

## Prompt 3: Template headings and checklist

**PROMPT SENT:**
Update `requirements-analysis.md`, `design-notes.md`, `data-quality-strategy.md`, `ai-prompts/`, `reflection.md` to the specified section headings. Check the submission checklist (skip finishing the dashboard UI). Produce a complete repo.

**AI RESPONSE SUMMARY:**
(this change) Template-aligned docs, local `unittest` suite, checklist honesty on dashboard UI and segmentation.

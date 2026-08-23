---
name: project-refactor
description: Synchronize continuity documents after the user has renamed, moved, merged, or reorganized files and directories in the current local project. Use when the user reports a structural change and asks to update project documentation or references.
---

# Project Refactor

Reconcile project documentation after a user-reported structural change. Work only inside the current local project root and preserve historical traceability.

## Gather the change boundary

Use the user's description of renamed, moved, merged, or restructured paths as the primary scope. Inspect only the affected current paths and their references in `AGENTS.md`, `README.md`, `PROGRESS.md`, `DECISIONS.md`, `knowledge/INDEX.md`, and relevant knowledge notes.

If the user provides incomplete but safely inferable old-to-new mappings, infer them from direct filesystem evidence. Do not expand to unrelated broad scans.

## Update clear references

For each clear, one-to-one low-risk mapping:

1. Update navigation, path references, commands, indexes, progress descriptions, and decision links that would otherwise mislead a future agent or reader.
2. Preserve history where the old path matters. Add `原路径 → 新路径` and the date in the relevant historical record rather than rewriting past events as if the old path never existed.
3. Keep `AGENTS.md` concise and update it only where stable routes, entry points, or project navigation changed.
4. Keep `README.md` appropriate for colleagues and potential public readers.
5. Do not alter unrelated content or create additional permanent root documents.

## Decide autonomously unless risk is material

Automatically resolve clear references, index repairs, date normalization, and duplicate path mentions. Ask the user only if there are multiple credible targets, changed file meaning, possible overwrite/loss, potentially broken external/public links, a conflict in key facts/decisions, or a risk of mixing project and cross-project knowledge.

## Check lightly

Confirm only that referenced new paths exist, old references within the affected documentation were handled, and knowledge-index links still resolve. Do not perform an unrelated repository scan.

## Finish

Return a compact list of the reported structural change, documents updated, preserved old-to-new mappings, and any unresolved serious ambiguity.

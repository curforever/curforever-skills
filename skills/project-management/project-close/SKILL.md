---
name: project-close
description: Save a complete project handoff or a lightweight automatic checkpoint in the current local project. Use when the user asks to close, hand off, save progress, switch agent/model/platform, or when an imminent context or session transition risks losing work.
---

# Project Close

Preserve current-project continuity with an explicit close or a low-cost automatic checkpoint. Work only inside the current local project root.

## Respect the project protocol

Use `AGENTS.md` as the sole editable instruction source and require `CLAUDE.md` to be its symbolic link. Update `README.md`, `PROGRESS.md`, `DECISIONS.md`, and `knowledge/` only for their defined purposes. Keep project `knowledge/` completely separate from any cross-project `knowledge-base` system.

## Collect evidence

Use current-conversation commitments, user corrections, actions taken, tool outputs, changed files, validations, and current project documents. Do not turn a guess into a recorded fact. Flag unsupported conclusions as `待验证`.

Before writing likely sensitive material, briefly state the risk and target location; proceed only if the user explicitly asks.

## Explicit close

When explicitly invoked:

1. Update `PROGRESS.md` directly with the current phase and workstream; detailed work completed; changed files; commands and results; verified outcomes; incomplete work and reasons; blockers; next actions; and important project conventions.
2. Preserve older progress as compact `- YYYY-MM-DD（周X）：摘要。` history entries in the project timezone, defaulting to `Asia/Shanghai`.
3. Add a `DECISIONS.md` entry only for a stable choice that affects future work. Include date, context, choice, rationale, alternatives, impact, source, status, review date, and review trigger.
4. Add to `knowledge/` only reusable, project-specific material that should not remain in working context. Update `knowledge/INDEX.md` in the same pass.
5. Update `AGENTS.md` only when stable background, boundaries, entry points, or navigation have changed. Keep procedural and transient content out of it.

## Automatic lightweight checkpoint

When a session is likely to end, compact, change model/platform, or otherwise lose continuity, run a best-effort checkpoint without asking first. Keep it cheap: append only a terse outline to `PROGRESS.md` containing current goal, key actions, key result, changed files, open item, and next action. Do not reread deeply, compact history, run broad validation, or write long knowledge notes.

Do not promise this catches crashes, forced interruption, or platform events that are not visible to the agent. An explicit close supersedes and expands prior lightweight checkpoints.

## Resolve autonomously by default

Make low-risk path fixes, index updates, date normalization, clear duplicate consolidation, and temporary-record compression yourself, then mention them in the final compact list.

Stop for a serious conflict only: credible sources disagree on a key fact, data definition, goal, or formal decision; an irreversible overwrite/deletion is needed; a path has multiple plausible targets; an action affects privacy, permissions, publication, or an external system; or project knowledge could be mixed with cross-project knowledge. State the conflicting locations, claims, impact, and recommended resolution.

## Finish

Lightly verify that the progress handoff fields are present, new knowledge is indexed, and no independent `CLAUDE.md` body was created. Return only a compact change list and unresolved serious risks.

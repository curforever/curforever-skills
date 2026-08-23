---
name: project-init
description: Initialize, migrate, or reconcile continuity documents for the current local project. Use when starting a project, standardizing an existing project, or when the user asks to initialize, migrate, reconcile, sync, or audit project documents.
---

# Project Init

Create a durable project handoff system without creating unnecessary documentation. Work only inside the current local project root.

## Operating model

Maintain these root artifacts:

- `AGENTS.md`: the sole editable, canonical project-agent instruction body. Keep it concise (normally under 200 lines) and limited to stable background, principles, boundaries, entry points, key paths, commands, and document navigation.
- `CLAUDE.md`: a symbolic link to `AGENTS.md`; never maintain a separate body.
- `README.md`: public-appropriate project overview, goals, outputs, and use or reproduction instructions.
- `PROGRESS.md`: current state and handoff log.
- `DECISIONS.md`: durable project decisions only.
- `knowledge/INDEX.md`: short index into project-specific, on-demand knowledge notes.

Treat `knowledge/` as project-local. Do not read from, write to, or merge it with any cross-project `knowledge-base` system.

## Choose a mode

- **Initialize** when the root is new or the user asks to set up project continuity documents.
- **Migrate** when the root already contains documents that would need moving, merging, renaming, replacing, or retirement.
- **Reconcile** when the user says “对账项目文档”, “同步项目文档”, or equivalent. Reconcile only clear, low-risk references and indexes.

## Inspect lightly

1. Establish the current project root; do not walk above it.
2. Inspect its immediate structure and the six protocol locations. Read existing project overview, instruction, progress, decision, and index files when present.
3. Use relevant current-conversation facts, confirmed requirements, completed actions, tool results, and edits as evidence. Mark unverified inferences as `待验证`; never invent facts.
4. Detect sensitive content such as credentials, cookies, private data, internal links, or raw customer data. Before writing it, briefly state the risk and intended location; write it only after the user explicitly asks.

## Migrate safely

Before a migration that changes existing documentation, show one compact proposal: affected files, proposed action, reason, and any material loss of history. Wait for explicit approval. Do not silently overwrite, delete, or retire existing documents.

After approval, or in an empty root, create all protocol artifacts. Create `CLAUDE.md` as a symbolic link to `AGENTS.md`; if links are unavailable, report that blocker and wait rather than creating duplicate bodies.

## Create useful initial content

- Put stable, every-session facts in `AGENTS.md`; move procedures and transient status elsewhere.
- Make `README.md` safe for colleagues and public readers.
- Give `PROGRESS.md` sections for current phase, current workstream, recent detailed work, verified results, changed files, commands/results, incomplete work/reasons, blockers, next actions, important project conventions, and dated historical entries.
- Record historical entries as `- YYYY-MM-DD（周X）：摘要。` using `Asia/Shanghai` unless the project specifies another timezone.
- In the current workstream record name, goal, inherited assumptions, relationship to mainline, and status.
- Give `DECISIONS.md` a decision record with date, context, choice, rationale, alternatives, impact, source, status (`已验证` / `暂定` / `待验证`), last review date, and review trigger.
- Keep `knowledge/INDEX.md` short. Each note should state source, date, status or confidence, last review date, and review trigger.

## Reconcile automatically where safe

Update clear one-to-one path references, broken index entries, dates, and low-risk duplicate records yourself. Preserve meaningful historical paths. Stop only for material ambiguity: conflicting key facts or decisions, multiple plausible path targets, irreversible loss, external/public impact, or possible pollution between project and cross-project knowledge.

## Finish

Perform only light checks: required files exist, `CLAUDE.md` resolves to `AGENTS.md`, essential sections exist, and every knowledge-index link resolves. Report only a compact list of created/changed files, low-risk repairs made, open `待验证` items, and any serious decision required.

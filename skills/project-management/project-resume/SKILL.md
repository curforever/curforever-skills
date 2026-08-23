---
name: project-resume
description: Read and brief the continuity state of the current local project without modifying it. Use when a new agent or model takes over, a new conversation resumes a project, or the user asks for a project handoff, resume, or onboarding briefing.
---

# Project Resume

Produce a reliable, read-only handoff briefing for the current local project. Do not execute the next task or modify any project artifact.

## Read the minimum useful context

1. Establish the current project root.
2. Read `AGENTS.md`, `README.md`, `PROGRESS.md`, `DECISIONS.md`, and `knowledge/INDEX.md` when present.
3. Read only knowledge notes indexed as relevant to the user's stated task or current workstream. Do not load the whole knowledge base.
4. Use current-conversation context only as supplemental evidence. Project documents and actual files remain independently checkable sources.
5. Do not access a cross-project `knowledge-base` system; it is outside the project protocol.

## Create the handoff briefing

Use exactly these headings, omitting only genuinely unavailable information:

- Current phase
- Current workstream
- Verified results
- Incomplete work / blockers
- Key decisions
- Risks requiring confirmation
- Recommended first action

Be concise. Cite project-relative files or decision dates where useful rather than restating long source text.

## Support a new workstream

If the user says they want to begin a new branch of work, propose a workstream name, goal, inherited assumptions, relationship to mainline, and initial status. Do not write it to `PROGRESS.md` until the user authorizes execution of that work.

## Detect, but do not repair, drift

Lightly sample current project files against recent `PROGRESS.md` claims and check that required documents, the `CLAUDE.md` link, and knowledge index references exist.

If actual files and progress disagree, report the difference and evidence. You may recommend treating actual files as the likely source of truth and repairing documentation with `Project Refactor` or `Project Close`, but do not repair it now.

If documents are missing, `CLAUDE.md` is not a link to `AGENTS.md`, an index is broken, or a serious document conflict exists, state impact and the lowest-cost remediation. Do not ask about ordinary formatting gaps or low-risk missing details.

## Finish

Return only the compact handoff briefing. Do not modify files, run the recommended first action, or automatically create a workstream record.

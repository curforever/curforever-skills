---
name: skill-manager
description: "Safely publish and maintain a local collection of Agent Skills in a GitHub repository. Use when the user asks to inventory skills, normalize their repository layout, remove local or personal data from the publish copy, preview changes, or explicitly push a reviewed update."
---

# Skill Manager

Manage a local skill collection as a sanitized, installable GitHub repository.

## Invocation and safety

Use this skill only when the user asks to organize, publish, synchronize, or review skills.

- Treat the source skill directory as read-only. Never edit, move, rename, or delete an existing source skill to prepare a release.
- Generate a temporary Git working copy. All normalization and redaction occur only in that copy.
- Always run a preview first. Push only when the user explicitly requests publication after reviewing the preview result.
- Never publish local project paths, user names, email addresses, credentials, tokens, real documents, or generated personal reports.
- If a possible sensitive value cannot be safely replaced using a relative path or a generic label, stop and ask the user instead of publishing it.

## Workflow

1. Confirm the source directory, GitHub repository, and branch. Inspect the repository's existing layout before changing it.
2. Inventory every direct child containing `SKILL.md`. Exclude metadata directories such as `__MACOSX`.
3. Review `references/skill-map.json`. Add a category and concise public summary for every new skill. Do not guess a category if the skill's purpose is unclear.
4. Keep user-specific replacement rules only in `.local-publishing-rules.json` beside this skill. This local-only file is deliberately excluded from releases. Start from the example in `references/local-publishing-rules.example.json`.
5. Run `scripts/sync-skills.ps1` in `Preview` mode. Resolve every validation failure before requesting a publish run.
6. Summarize added, updated, removed, and blocked files for the user. When they explicitly request publishing, rerun in `Publish` mode.
7. Verify the pushed commit, repository status, README catalog, and that no sensitive-value scanner failures remain.

## Commands

Use PowerShell and pass explicit absolute paths for local inputs:

```powershell
pwsh -File ./scripts/sync-skills.ps1 `
  -SourceRoot '<source-skills-directory>' `
  -RepoUrl 'https://github.com/<account>/<repository>.git' `
  -Mode Preview
```

After the user has reviewed the preview and explicitly asked to publish:

```powershell
pwsh -File ./scripts/sync-skills.ps1 `
  -SourceRoot '<source-skills-directory>' `
  -RepoUrl 'https://github.com/<account>/<repository>.git' `
  -Mode Publish
```

To synchronize only a previously published skill, add `-SkillNames '<skill-name>'`. With no `-SkillNames`, the initial release includes only mappings not marked `initialPublish: false`.

## Release layout

Publish skills as `skills/<category>/<skill-name>/`. Each directory must contain `SKILL.md`; optional reusable support files belong in `agents/`, `references/`, `scripts/`, or `tests/`.

The synchronization script rewrites the repository's `## Skills` catalog from the public summaries in `references/skill-map.json`. Keep summaries short, accurate, and free of private context.

## Failure handling

- An unmapped skill, invalid frontmatter, unrecognized local path, email address, credential-like assignment, or local-only configuration in the release copy is a release blocker.
- Do not bypass a blocker by disabling its check. Add a safe local replacement rule or revise only the temporary release copy.
- Authentication, non-fast-forward, and Git conflicts are external-state failures. Preserve the temporary worktree path printed by the script and report the exact next action; do not force-push.

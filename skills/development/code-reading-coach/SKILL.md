---
name: code-reading-coach
description: "Guide a learner through source code one business question at a time with plain-language business flows, IntelliJ IDEA follow-along steps, source evidence, and adaptive self-checks. Use only when the user explicitly invokes $code-reading-coach or /code-reading-coach to study a codebase, follow an HTML learning handbook, connect business behavior to source files, or maintain a code-learning knowledge document."
---

# Code Reading Coach

## Purpose

Use this skill to turn code reading into a repeatable learning loop. Start from the learner's HTML handbook and Todo list, trace the smallest useful business slice through read-only source repositories, explain the key methods, test understanding, and update the handbook after each completed learning unit.

Do not behave like a code summarizer. Teach from shallow to deep: business purpose first, then a small analogy, the real runtime flow, and finally the exact code. Default to a low-density explanation that the learner can follow in IntelliJ IDEA while reading.

## Invocation and scope

Invoke only after the user explicitly writes `$code-reading-coach`, `/code-reading-coach`, or clearly says to use this Skill. Do not apply the workflow to ordinary code questions without explicit invocation.

Use these defaults when the user does not provide replacements:

- Handbook: `./首页服务端学习手册.html`
- `whomesoa`: `./repositories/whomesoa`
- `channelsoa`: `./repositories/channelsoa`
- `channelcms`: `./repositories/channelcms`
- Reference material: `./references/参考资料` and `./references/首页性能优化`

Treat the handbook and repository paths as user-configurable. If the user provides another HTML, repository, or reference path, use the new path for that run and do not silently mix projects.

Repositories and reference material are read-only. The only normal write target in the default project is the handbook. Do not modify, format, commit, or reset a source repository.

## Learning workflow

Follow this sequence for every learning unit:

1. Read the current handbook, especially the reading route, Todo groups, completed items, evidence labels, open questions, and the last studied chapter.
2. Select the topic:
   - honor an explicit topic or code path from the user;
   - otherwise choose the next unfinished, high-leverage Todo that can be supported by current source evidence;
   - do not repeat a fully answered topic unless the user asks for review or the source changed.
3. State the business question in one sentence and define the expected learning result.
4. Read only the necessary source slice: locate the entry point, caller, callee, configuration, data model, cache, notification, and fallback branch. Expand outward only when needed to explain the current unit.
5. Explain in this order: one-sentence answer → a small everyday analogy → the real runtime flow → exact code. Use a compact flow or table only when three or more components interact.
6. Select one key method or a very small group. Show a source locator containing repository, file, method, line range, local path, and business purpose.
7. Include an **IDEA 跟读卡** for every unit. Give the project directory, file, method/line, the next cursor position, and the exact macOS IntelliJ IDEA shortcut needed to make the next move. Use `⌘O` to find a class, `⌘F12` to find a method in the open class, `⌘B` for declaration, `⌥⌘B` for implementations, `⌥F7` for callers/usages, and `⌘E` for recent files. State that shortcuts may differ if the learner changed the IDEA keymap. Do not instruct the learner to open irrelevant files.
8. Apply the default two-question core to every key method: **position** and **input/output**. Discuss failure behavior, logs/troubleshooting, and alternatives only when the learner explicitly asks, the current topic is an incident/stability topic, or omitting them would make the result misleading. Use `references/five-question-rubric.md` for the extended mode.
9. Teach in the default mode: explain first, then give a self-check with its answer immediately. Each self-check is formatted “问题 → 一句答案 → 易理解的展开解释”. If the learner says “考我”, ask first and delay the answer; if they say “直接讲答案”, retain the default direct-answer behavior.
10. Update the handbook after the learning unit: add or correct the business explanation, source locator, evidence confidence, direct-answer self-check, and next Todo. Only mark a Todo complete when the learner explicitly confirms mastery; do not infer completion from reading the explanation.
11. End with the next smallest useful learning step, not an unbounded list of classes.

Use the interaction details in `references/teaching-loop.md` when the learner asks to change pace, review, be tested, or switch projects.

## Method-reading contract

For each key method, always answer the first two questions. This is the default learning load. Use questions 3–5 only in extended mode: when explicitly requested, when teaching failures/operations, or when a missing caveat would create a false conclusion. Keep every answer tied to code and runtime evidence rather than generic software advice.

1. **Position** — Where does this method sit in the end-to-end business flow? Identify its caller, the stage it belongs to, and the downstream consumer of its result.
2. **Input and output** — Name the actual parameters, important fields, context objects, cache entries, or external responses. Explain what the method returns or mutates and who consumes it next.
3. **Failure behavior (extended)** — Trace exceptions, null/empty results, timeouts, rejected tasks, feature switches, partial results, old-cache retention, fallback responses, and whether the request continues or fails. If the code does not show the behavior, label it as unknown.
4. **Logging and troubleshooting (extended)** — Find the real `log`, UMP, metric, trace, alarm, error code, or operational switch near the path. Give a minimal check order: request sample → input → output → first disappearance or latency jump. If no useful logging evidence exists, say so and identify the missing observability.
5. **Alternative (extended)** — Discuss only when there is a credible alternative, an architectural trade-off, or a design choice worth challenging. Otherwise write: “暂无必要替代；当前代码路径没有足够证据表明这是一个需要改造的设计选择。”

## Evidence and confidence

Every non-trivial conclusion must carry both an evidence label and a confidence score:

- **代码已确认** — directly supported by current source, configuration, or a reproducible local check; normally 8–10/10.
- **结构推断** — supported by several code signals but not by an explicit historical or online statement; normally 5–7/10.
- **待线上/负责人确认** — the source is incomplete, environment-dependent, or contradicted by another signal; normally 1–4/10.

Use the score as an honest estimate, not decoration. A score of 9/10 does not mean production behavior is proven if the code only shows a disabled path or a non-production configuration. Never convert class names, old comments, repository names, or plausible architecture into facts without evidence.

When code, handbook, local reference material, and user-provided facts disagree, use this priority:

1. current source code;
2. current local reference material;
3. explicit user-confirmed online facts;
4. verified operational evidence;
5. historical material;
6. inference.

Keep conflicting versions visible as “历史结论 / 当前实现”. Add material unknowns to the handbook's “待确认事实” section, not to a speculative answer.

## Handbook update contract

Keep the existing single-page HTML, left navigation, single-column layout, collapsed deep dives, colored repository locator cards, and learning Todo interaction. Do not add an in-page form for creating Todo items; new Todo items come from the current conversation and are written by the Skill when justified.

For each completed learning unit, update only the relevant section and preserve still-valid content. The update should normally contain:

- a one-sentence key answer;
- the business flow from App behavior to runtime result;
- an IDEA follow-along card: project → file → method/line → shortcut → next file/method;
- one or more `repository → file → method → line` locator cards with absolute local links;
- default position/input-output answers, with extended questions only when applicable;
- a self-check formatted as question → concise answer → easy-to-follow explanation;
- the next learning Todo or an explicit reason no new Todo is needed.

Keep practice tasks distinct from knowledge already explained. A generic method for tracing a real `businessCode`, incident, or App UI mapping is not the same as a completed real case.

## Operational and safety rules

- Read source with fast search and focused file slices; do not load entire repositories without a reason.
- Verify that every cited file exists and that line ranges are close to the current checkout before writing a locator.
- When discussing logs, inspect the actual logging and monitoring calls. Do not invent a log path, metric name, alert, or production state.
- Distinguish configuration cache, runtime result cache, client cache, and full-page fallback cache.
- Distinguish a database write, a cache publication, a ZooKeeper notification, a local JVM refresh, a request-time filter, and client rendering. “Published” does not automatically mean “visible to this user”.
- Never claim an outer database transaction committed solely because a mapper invocation returned.
- Never mark a user Todo complete without explicit confirmation.
- If the requested conclusion requires unavailable online evidence, stop at a clearly labeled pending conclusion and give the safest local verification path.
- Before finishing, validate HTML syntax sufficiently for the edited page, confirm navigation targets, confirm source links, and report any validation limitation.

## Response shape

Use this compact order in the conversation:

1. **本次学习目标** — one business question and why it is next.
2. **先给结论** — plain-language answer, analogy, and a small flow.
3. **IDEA 跟读卡** — project, file, method/line, shortcut, and the next jump.
4. **关键代码定位与两问** — repository, file, method, line, business purpose, position, and input/output; add extended questions only when needed.
5. **自测** — question → concise answer → easy-to-follow explanation; ask before answering only in “考我” mode.
6. **手册更新** — summarize what changed and which Todo remains.
7. **下一步** — one bounded recommended step.

Do not expose hidden chain-of-thought. Provide concise, checkable reasoning, code evidence, assumptions, and uncertainty instead.

# Teaching loop

## Default mode: explain, follow in IDEA, then test

Use this mode unless the learner changes it:

1. State the business question and one-sentence answer.
2. Draw the smallest useful flow from user behavior to code result.
3. Give an IDEA follow-along card: project, file, method/line, cursor target, shortcut, and next jump.
4. Answer position and input/output with evidence and confidence. Add failure, operational, and alternative analysis only when requested or necessary.
5. Give one or two self-checks, each immediately followed by a concise answer and an easy-to-follow expansion.
6. In “考我” mode only, wait for the learner reply, then give the standard answer, missing links, and exact evidence.
7. Update the handbook and report the next Todo.

## “考我” mode

Do not reveal the standard answer before the learner attempts the questions. Present only:

- the business context;
- the relevant source locator;
- the questions and the expected scope of the answer.

After the attempt, switch back to the default feedback behavior: direct standard answer, gap analysis, evidence, and confidence.

## “直接讲答案” mode

Skip the waiting step. Give the complete explanation, IDEA follow-along card, default two-question answers, needed extended analysis, evidence, self-check answer key, and handbook update in one response.

## Review mode

When the learner asks to review, do not reread the entire project by default. Read the handbook's existing answer, source locators, and confidence labels first. Recheck the current source only where the old answer is uncertain, stale, or explicitly challenged.

## Topic selection

When no topic is provided, rank unfinished items by:

1. prerequisite value for the next chapters;
2. ability to verify from current local source;
3. relevance to the learner's stated business goal;
4. bounded size for one learning unit.

Prefer one concrete entry point, method, configuration, or failure path over a tour of many unrelated classes.

## Project switching

When the learner provides new paths, confirm the active project in the response and use only that project's handbook and repositories for the unit. Preserve the same default two-question contract, IDEA follow-along card, evidence labels, confidence scores, and HTML update rules.
